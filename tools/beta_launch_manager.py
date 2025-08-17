#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/beta_launch_manager.py
🎯 PURPOSE: Beta launch manager for user onboarding and tracking
🔗 IMPORTS: SQLAlchemy, email service, templates
📤 EXPORTS: BetaLaunchManager class
"""

import os
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.database import get_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# Use production database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cora_user:cora_password@localhost:5432/cora_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from models.user import User
from models.feedback import Feedback
from services.email_service import send_welcome_email

class BetaLaunchManager:
    """Manages beta user onboarding and tracking"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.beta_users_file = Path("data/beta_users.json")
        self.onboarding_log_file = Path("logs/beta_onboarding.log")
        
        # Ensure directories exist
        self.onboarding_log_file.parent.mkdir(exist_ok=True)
    
    def add_beta_user(self, email: str, name: str, company: str = None, notes: str = None) -> Dict:
        """Add a new beta user to the program"""
        
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            return {
                "success": False,
                "message": f"User {email} already exists in the system",
                "user_id": existing_user.id
            }
        
        # Create new user
        new_user = User(
            email=email,
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow()
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # Save beta user info
        beta_user_info = {
            "email": email,
            "name": name,
            "company": company,
            "notes": notes,
            "added_at": datetime.utcnow().isoformat(),
            "status": "pending_onboarding"
        }
        
        self._save_beta_user_info(beta_user_info)
        
        # Log the addition
        self._log_onboarding_event("user_added", email, f"Added beta user: {name} ({email})")
        
        return {
            "success": True,
            "message": f"Beta user {email} added successfully",
            "user_id": new_user.id
        }
    
    def send_welcome_emails(self, user_emails: List[str] = None) -> Dict:
        """Send welcome emails to beta users"""
        
        if user_emails is None:
            # Get all pending beta users
            beta_users = self._load_beta_users()
            user_emails = [user["email"] for user in beta_users if user["status"] == "pending_onboarding"]
        
        results = []
        for email in user_emails:
            try:
                # Get user info
                user = self.db.query(User).filter(User.email == email).first()
                if not user:
                    results.append({
                        "email": email,
                        "success": False,
                        "message": "User not found in database"
                    })
                    continue
                
                # Get beta user info
                beta_user_info = self._get_beta_user_info(email)
                user_name = beta_user_info.get("name", email.split("@")[0]) if beta_user_info else email.split("@")[0]
                
                # Send welcome email
                success = send_welcome_email(email, user_name)
                
                if success:
                    # Update status
                    self._update_beta_user_status(email, "welcome_sent")
                    self._log_onboarding_event("welcome_sent", email, f"Welcome email sent to {user_name}")
                    
                    results.append({
                        "email": email,
                        "success": True,
                        "message": "Welcome email sent successfully"
                    })
                else:
                    results.append({
                        "email": email,
                        "success": False,
                        "message": "Failed to send welcome email"
                    })
                    
            except Exception as e:
                results.append({
                    "email": email,
                    "success": False,
                    "message": f"Error: {str(e)}"
                })
        
        return {
            "total_users": len(user_emails),
            "successful": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "results": results
        }
    
    def get_beta_stats(self) -> Dict:
        """Get beta program statistics"""
        
        # User statistics
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        admin_users = self.db.query(User).filter(User.is_admin == True).count()
        
        # Feedback statistics
        total_feedback = self.db.query(Feedback).count()
        feedback_by_category = {}
        categories = self.db.query(Feedback.category).distinct().all()
        for category in categories:
            count = self.db.query(Feedback).filter(Feedback.category == category[0]).count()
            feedback_by_category[category[0]] = count
        
        # Recent activity
        recent_users = self.db.query(User).filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        recent_feedback = self.db.query(Feedback).filter(
            Feedback.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Beta user status
        beta_users = self._load_beta_users()
        pending_onboarding = len([u for u in beta_users if u["status"] == "pending_onboarding"])
        welcome_sent = len([u for u in beta_users if u["status"] == "welcome_sent"])
        active_beta = len([u for u in beta_users if u["status"] == "active"])
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "admin": admin_users,
                "recent_7_days": recent_users
            },
            "feedback": {
                "total": total_feedback,
                "by_category": feedback_by_category,
                "recent_7_days": recent_feedback
            },
            "beta_program": {
                "total_beta_users": len(beta_users),
                "pending_onboarding": pending_onboarding,
                "welcome_sent": welcome_sent,
                "active": active_beta
            }
        }
    
    def generate_beta_report(self, output_file: str = None) -> str:
        """Generate a comprehensive beta program report"""
        
        if output_file is None:
            output_file = f"reports/beta_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Ensure reports directory exists
        Path(output_file).parent.mkdir(exist_ok=True)
        
        # Get beta users
        beta_users = self._load_beta_users()
        
        # Get user activity data
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'email', 'name', 'company', 'status', 'added_at', 
                'last_login', 'total_expenses', 'total_feedback',
                'last_activity'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for beta_user in beta_users:
                email = beta_user["email"]
                user = self.db.query(User).filter(User.email == email).first()
                
                if user:
                    # Get user activity data
                    total_expenses = self.db.query(func.count()).select_from(user.expenses).scalar() or 0
                    total_feedback = self.db.query(Feedback).filter(Feedback.user_email == email).count()
                    
                    row = {
                        'email': email,
                        'name': beta_user.get('name', ''),
                        'company': beta_user.get('company', ''),
                        'status': beta_user.get('status', ''),
                        'added_at': beta_user.get('added_at', ''),
                        'last_login': user.last_login.isoformat() if user.last_login else '',
                        'total_expenses': total_expenses,
                        'total_feedback': total_feedback,
                        'last_activity': user.updated_at.isoformat() if user.updated_at else ''
                    }
                    writer.writerow(row)
        
        return output_file
    
    def _save_beta_user_info(self, user_info: Dict):
        """Save beta user information to JSON file"""
        
        beta_users = self._load_beta_users()
        
        # Update existing or add new
        existing = False
        for i, user in enumerate(beta_users):
            if user["email"] == user_info["email"]:
                beta_users[i] = user_info
                existing = True
                break
        
        if not existing:
            beta_users.append(user_info)
        
        # Save to file
        with open(self.beta_users_file, 'w') as f:
            json.dump(beta_users, f, indent=2)
    
    def _load_beta_users(self) -> List[Dict]:
        """Load beta users from JSON file"""
        
        if not self.beta_users_file.exists():
            return []
        
        with open(self.beta_users_file, 'r') as f:
            return json.load(f)
    
    def _get_beta_user_info(self, email: str) -> Optional[Dict]:
        """Get beta user information by email"""
        
        beta_users = self._load_beta_users()
        for user in beta_users:
            if user["email"] == email:
                return user
        return None
    
    def _update_beta_user_status(self, email: str, status: str):
        """Update beta user status"""
        
        beta_users = self._load_beta_users()
        for user in beta_users:
            if user["email"] == email:
                user["status"] = status
                user["updated_at"] = datetime.utcnow().isoformat()
                break
        
        # Save updated data
        with open(self.beta_users_file, 'w') as f:
            json.dump(beta_users, f, indent=2)
    
    def _log_onboarding_event(self, event_type: str, email: str, message: str):
        """Log onboarding events"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "email": email,
            "message": message
        }
        
        with open(self.onboarding_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

def main():
    """Main function for beta launch management"""
    
    manager = BetaLaunchManager()
    
    print("🚀 CORA Beta Launch Manager")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Add beta user")
        print("2. Send welcome emails")
        print("3. View beta statistics")
        print("4. Generate beta report")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            email = input("Enter user email: ").strip()
            name = input("Enter user name: ").strip()
            company = input("Enter company (optional): ").strip() or None
            notes = input("Enter notes (optional): ").strip() or None
            
            result = manager.add_beta_user(email, name, company, notes)
            print(f"\nResult: {result['message']}")
        
        elif choice == "2":
            print("\nSending welcome emails...")
            result = manager.send_welcome_emails()
            print(f"\nResults:")
            print(f"Total users: {result['total_users']}")
            print(f"Successful: {result['successful']}")
            print(f"Failed: {result['failed']}")
            
            for r in result['results']:
                status = "✅" if r['success'] else "❌"
                print(f"{status} {r['email']}: {r['message']}")
        
        elif choice == "3":
            stats = manager.get_beta_stats()
            print("\n📊 Beta Program Statistics:")
            print(f"Total Users: {stats['users']['total']}")
            print(f"Active Users: {stats['users']['active']}")
            print(f"Recent Users (7 days): {stats['users']['recent_7_days']}")
            print(f"Total Feedback: {stats['feedback']['total']}")
            print(f"Beta Users: {stats['beta_program']['total_beta_users']}")
            print(f"Pending Onboarding: {stats['beta_program']['pending_onboarding']}")
            print(f"Welcome Sent: {stats['beta_program']['welcome_sent']}")
            print(f"Active Beta: {stats['beta_program']['active']}")
        
        elif choice == "4":
            output_file = manager.generate_beta_report()
            print(f"\n📄 Beta report generated: {output_file}")
        
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 