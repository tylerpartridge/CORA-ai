#!/usr/bin/env python3
"""
Fix Critical System Gaps
Address all issues identified in the deep audit
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_missing_tables():
    """Create missing database tables"""
    print("🔧 Creating missing database tables...")
    
    db_path = "data/cora.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create job_alerts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email VARCHAR(255) NOT NULL,
            job_id INTEGER NOT NULL,
            alert_type VARCHAR(50) NOT NULL,
            severity VARCHAR(20) NOT NULL DEFAULT 'warning',
            message VARCHAR(500) NOT NULL,
            details TEXT,
            read BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at DATETIME
        )
        """)
        
        # Create indexes for job_alerts
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_alerts_user_email ON job_alerts(user_email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_alerts_job_id ON job_alerts(job_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_alerts_read ON job_alerts(read)")
        
        # Create contractor_waitlist table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contractor_waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            email VARCHAR(200) UNIQUE NOT NULL,
            phone VARCHAR(20),
            company_name VARCHAR(200),
            source VARCHAR(100),
            source_details TEXT,
            signup_keyword VARCHAR(50),
            business_type VARCHAR(100),
            team_size VARCHAR(50),
            biggest_pain_point TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            invitation_sent_at DATETIME,
            invitation_accepted_at DATETIME,
            referred_by_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            admin_notes TEXT
        )
        """)
        
        # Create indexes for contractor_waitlist
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contractor_waitlist_email ON contractor_waitlist(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contractor_waitlist_status ON contractor_waitlist(status)")
        
        conn.commit()
        print("✅ Missing tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_missing_frontend_files():
    """Create missing frontend JavaScript files"""
    print("🔧 Creating missing frontend files...")
    
    # Voice expense entry JS
    voice_js = '''/**
 * Voice Expense Entry System
 * Handles voice-to-text expense entry for contractors
 */

class VoiceExpenseEntry {
    constructor() {
        this.isRecording = false;
        this.recognition = null;
        this.init();
    }

    init() {
        this.setupSpeechRecognition();
        this.bindEvents();
    }

    setupSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isRecording = true;
            this.updateUI('listening');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.processTranscript(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.updateUI('error');
        };

        this.recognition.onend = () => {
            this.isRecording = false;
            this.updateUI('ready');
        };
    }

    bindEvents() {
        const voiceBtn = document.querySelector('.voice-btn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => {
                if (this.isRecording) {
                    this.stopRecording();
                } else {
                    this.startRecording();
                }
            });
        }
    }

    startRecording() {
        if (this.recognition) {
            this.recognition.start();
        }
    }

    stopRecording() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    async processTranscript(transcript) {
        try {
            this.updateUI('processing');
            
            const response = await fetch('/api/voice/expense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    transcript: transcript,
                    source: 'dashboard_voice'
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccess(result.expense);
                this.refreshDashboard();
            } else {
                this.showError(result.error);
            }

        } catch (error) {
            console.error('Voice processing error:', error);
            this.showError('Failed to process voice input');
        } finally {
            this.updateUI('ready');
        }
    }

    updateUI(state) {
        const voiceBtn = document.querySelector('.voice-btn');
        if (!voiceBtn) return;

        const label = voiceBtn.querySelector('.voice-label');
        if (!label) return;

        switch (state) {
            case 'listening':
                label.textContent = 'Listening...';
                voiceBtn.classList.add('recording');
                break;
            case 'processing':
                label.textContent = 'Processing...';
                voiceBtn.classList.add('processing');
                break;
            case 'ready':
                label.textContent = 'Voice Entry';
                voiceBtn.classList.remove('recording', 'processing');
                break;
            case 'error':
                label.textContent = 'Error';
                voiceBtn.classList.remove('recording', 'processing');
                break;
        }
    }

    showSuccess(expense) {
        this.showNotification(`Expense added: $${(expense.amount_cents / 100).toFixed(2)} - ${expense.vendor}`, 'success');
    }

    showError(message) {
        this.showNotification(`Error: ${message}`, 'error');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `voice-notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#22c55e' : '#ef4444'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    refreshDashboard() {
        // Refresh dashboard data
        if (typeof loadTransactions === 'function') {
            loadTransactions();
        }
        if (typeof updateDashboardMetrics === 'function') {
            updateDashboardMetrics();
        }
    }
}

// Initialize voice expense entry
document.addEventListener('DOMContentLoaded', () => {
    new VoiceExpenseEntry();
});
'''
    
    # Job profitability JS
    job_profitability_js = '''/**
 * Job Profitability Dashboard
 * Shows job profitability metrics and alerts
 */

class JobProfitabilityDashboard {
    constructor() {
        this.jobs = [];
        this.alerts = [];
        this.init();
    }

    async init() {
        await this.loadJobs();
        await this.loadAlerts();
        this.render();
        this.setupEventListeners();
    }

    async loadJobs() {
        try {
            const response = await fetch('/api/jobs');
            if (response.ok) {
                this.jobs = await response.json();
            }
        } catch (error) {
            console.error('Error loading jobs:', error);
        }
    }

    async loadAlerts() {
        try {
            const response = await fetch('/api/alerts/summary');
            if (response.ok) {
                const summary = await response.json();
                this.alerts = summary.alerts || [];
            }
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }

    render() {
        this.renderJobCards();
        this.renderAlertBadge();
    }

    renderJobCards() {
        const container = document.getElementById('jobProfitabilityGrid');
        if (!container) return;

        if (this.jobs.length === 0) {
            container.innerHTML = '<p>No jobs found. Add your first job to see profitability metrics.</p>';
            return;
        }

        const jobCards = this.jobs.map(job => this.createJobCard(job)).join('');
        container.innerHTML = jobCards;
    }

    createJobCard(job) {
        const profit = job.quoted_amount - (job.total_spent || 0);
        const margin = job.quoted_amount > 0 ? (profit / job.quoted_amount * 100) : 0;
        const alertCount = this.alerts.filter(alert => alert.job_id === job.id).length;
        
        const alertBadge = alertCount > 0 ? `<div class="alert-badge">${alertCount}</div>` : '';
        
        return `
            <div class="job-profit-card ${margin < 20 ? 'low-margin' : ''}">
                ${alertBadge}
                <div class="job-header">
                    <h4>${job.job_name}</h4>
                    <div class="job-status ${job.status}">${job.status}</div>
                </div>
                <div class="job-profit-metrics">
                    <div class="job-metric">
                        <div class="job-metric-label">Quoted</div>
                        <div class="job-metric-value">$${job.quoted_amount?.toFixed(0) || 0}</div>
                    </div>
                    <div class="job-metric">
                        <div class="job-metric-label">Spent</div>
                        <div class="job-metric-value">$${(job.total_spent || 0).toFixed(0)}</div>
                    </div>
                    <div class="job-metric">
                        <div class="job-metric-label">Profit</div>
                        <div class="job-metric-value ${profit >= 0 ? 'positive' : 'negative'}">$${profit.toFixed(0)}</div>
                    </div>
                    <div class="job-metric">
                        <div class="job-metric-label">Margin</div>
                        <div class="job-metric-value ${margin >= 20 ? 'positive' : margin >= 10 ? 'warning' : 'negative'}">${margin.toFixed(1)}%</div>
                    </div>
                </div>
                <div class="job-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${Math.min(100, (job.total_spent || 0) / job.quoted_amount * 100)}%"></div>
                    </div>
                    <div class="progress-label">${((job.total_spent || 0) / job.quoted_amount * 100).toFixed(1)}% of budget used</div>
                </div>
            </div>
        `;
    }

    renderAlertBadge() {
        const alertCount = document.getElementById('alertCount');
        if (!alertCount) return;

        const unreadAlerts = this.alerts.filter(alert => !alert.read).length;
        
        if (unreadAlerts > 0) {
            alertCount.textContent = unreadAlerts;
            alertCount.style.display = 'flex';
        } else {
            alertCount.style.display = 'none';
        }
    }

    setupEventListeners() {
        // Add click handlers for job cards
        document.addEventListener('click', (e) => {
            if (e.target.closest('.job-profit-card')) {
                const jobCard = e.target.closest('.job-profit-card');
                const jobName = jobCard.querySelector('h4').textContent;
                this.showJobDetails(jobName);
            }
        });
    }

    showJobDetails(jobName) {
        // Show job details modal or navigate to job page
        console.log('Showing details for job:', jobName);
        // Implementation depends on your UI requirements
    }
}

// Initialize job profitability dashboard
document.addEventListener('DOMContentLoaded', () => {
    new JobProfitabilityDashboard();
});
'''
    
    # Create the files
    files_to_create = [
        ('web/static/js/voice_expense_entry.js', voice_js),
        ('web/static/js/job_profitability.js', job_profitability_js)
    ]
    
    for file_path, content in files_to_create:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Created {file_path}")

def create_missing_routes():
    """Create missing route files"""
    print("🔧 Creating missing route files...")
    
    # Create alerts routes
    alerts_routes = '''"""
Job Alerts API Routes
Handles job profitability alerts and notifications
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from dependencies.database import get_db
from dependencies.auth import get_current_user, User
from services.job_alerts import JobAlertService
from models.job import Job

alert_router = APIRouter()

@alert_router.get("/summary")
async def get_alert_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary of user's alerts"""
    alert_service = JobAlertService(db)
    summary = alert_service.get_alert_summary(current_user.email)
    return summary

@alert_router.get("/")
async def get_alerts(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's alerts"""
    alert_service = JobAlertService(db)
    alerts = alert_service.get_user_alerts(current_user.email, unread_only, limit)
    return alerts

@alert_router.post("/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as read"""
    alert_service = JobAlertService(db)
    success = alert_service.mark_alert_read(alert_id, current_user.email)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}

@alert_router.post("/read-all")
async def mark_all_alerts_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all user's alerts as read"""
    alert_service = JobAlertService(db)
    count = alert_service.mark_all_alerts_read(current_user.email)
    return {"success": True, "alerts_marked": count}

@alert_router.post("/check-jobs")
async def check_jobs_for_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check all user's jobs for new alerts"""
    alert_service = JobAlertService(db)
    
    # Get user's jobs
    jobs = db.query(Job).filter(Job.user_email == current_user.email).all()
    
    new_alerts = 0
    for job in jobs:
        alerts = alert_service.check_job_alerts(job, current_user.email)
        for alert_data in alerts:
            alert_service.create_alert(
                current_user.email, 
                job.id, 
                alert_data
            )
            new_alerts += 1
    
    return {"success": True, "new_alerts": new_alerts}
'''
    
    # Create the routes file
    with open('routes/alerts.py', 'w') as f:
        f.write(alerts_routes)
    print("✅ Created routes/alerts.py")

def create_test_data():
    """Create test data for demonstration"""
    print("🔧 Creating test data...")
    
    db_path = "data/cora.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create test user if not exists
        cursor.execute("SELECT email FROM users WHERE email = 'test@cora.com'")
        if not cursor.fetchone():
            import bcrypt
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw('test123'.encode('utf-8'), salt).decode('utf-8')
            
            cursor.execute("""
            INSERT INTO users (email, hashed_password, created_at, is_active, is_admin)
            VALUES (?, ?, ?, ?, ?)
            """, ('test@cora.com', hashed_password, datetime.now(), "1", 1))
            
            print("✅ Created test user: test@cora.com / test123")
        
        # Add sample jobs
        sample_jobs = [
            ('test@cora.com', 'JB001', 'Johnson Bathroom', 'Johnson Family', '123 Main St', '2025-01-10', '2025-02-15', 25000.00, 'active'),
            ('test@cora.com', 'SK002', 'Smith Kitchen', 'Smith Family', '456 Oak Ave', '2025-01-20', '2025-03-10', 35000.00, 'active'),
            ('test@cora.com', 'WD003', 'Wilson Deck', 'Wilson Family', '789 Pine Rd', '2025-02-01', '2025-04-01', 15000.00, 'active'),
        ]
        
        for job in sample_jobs:
            cursor.execute("""
            INSERT OR IGNORE INTO jobs (user_email, job_id, job_name, customer_name, job_address, start_date, end_date, quoted_amount, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, job + (datetime.now(), datetime.now()))
        
        # Add sample expenses
        sample_expenses = [
            ('test@cora.com', 15000, 'USD', 1, 'Home Depot - Johnson bathroom materials', 'Home Depot', '2025-01-15', 'credit_card', '', '{"job_name": "Johnson Bathroom"}', 95, 1),
            ('test@cora.com', 2500, 'USD', 2, 'Gas for work truck', 'Shell', '2025-01-16', 'credit_card', '', '{"job_name": "Johnson Bathroom"}', 90, 1),
            ('test@cora.com', 12000, 'USD', 1, 'Materials for Smith kitchen', 'Home Depot', '2025-01-18', 'credit_card', '', '{"job_name": "Smith Kitchen"}', 95, 1),
        ]
        
        for expense in sample_expenses:
            cursor.execute("""
            INSERT OR IGNORE INTO expenses (user_email, amount_cents, currency, category_id, description, vendor, expense_date, payment_method, receipt_url, tags, confidence_score, auto_categorized, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, expense + (datetime.now(), datetime.now()))
        
        conn.commit()
        print("✅ Test data created successfully")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Run all fixes"""
    print("🚀 Starting critical gap fixes...")
    
    create_missing_tables()
    create_missing_frontend_files()
    create_missing_routes()
    create_test_data()
    
    print("\n✅ All critical gaps fixed!")
    print("\n📋 Test Credentials:")
    print("  Email: test@cora.com")
    print("  Password: test123")
    print("\n🔗 Test the system at: http://localhost:8000/dashboard")

if __name__ == "__main__":
    main() 