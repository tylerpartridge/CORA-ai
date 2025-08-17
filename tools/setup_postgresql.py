#!/usr/bin/env python3
"""
Quick PostgreSQL Setup for CORA
Handles the complete migration from SQLite to PostgreSQL
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"[PostgreSQL Setup] {message}")
    print("=" * 60)

def print_step(step_num, message):
    """Print a step message"""
    print(f"\n[Step {step_num}] {message}")

def check_postgresql():
    """Check if PostgreSQL is installed and running"""
    print_step(1, "Checking PostgreSQL installation...")
    
    try:
        # Check if psql command exists
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] PostgreSQL is installed:", result.stdout.strip())
            return True
        else:
            print("[ERROR] PostgreSQL is not installed")
            print("\nPlease install PostgreSQL:")
            print("  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib")
            print("  macOS: brew install postgresql")
            print("  Windows: Download from https://www.postgresql.org/download/windows/")
            return False
    except FileNotFoundError:
        print("[ERROR] PostgreSQL is not installed or not in PATH")
        return False

def create_database():
    """Create the CORA database and user"""
    print_step(2, "Creating PostgreSQL database and user...")
    
    sql_commands = """
CREATE DATABASE cora_db;
CREATE USER cora_user WITH PASSWORD 'cora_password';
GRANT ALL PRIVILEGES ON DATABASE cora_db TO cora_user;
\\q
"""
    
    print("\n📋 Please run these commands in PostgreSQL:")
    print("-" * 40)
    print("sudo -u postgres psql")
    print(sql_commands)
    print("-" * 40)
    
    response = input("\nHave you created the database? (y/n): ")
    return response.lower() == 'y'

def backup_sqlite():
    """Backup the SQLite database"""
    print_step(3, "Backing up SQLite database...")
    
    sqlite_path = "./cora.db"
    if not os.path.exists(sqlite_path):
        print("⚠️  No SQLite database found to backup")
        return True
    
    # Create backup
    backup_dir = "./backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/cora_sqlite_backup_{timestamp}.db"
    
    try:
        shutil.copy2(sqlite_path, backup_path)
        print(f"✅ SQLite database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to backup SQLite database: {e}")
        return False

def update_env_file():
    """Update the .env file to use PostgreSQL"""
    print_step(4, "Updating environment configuration...")
    
    env_path = ".env"
    postgresql_env_path = "./config/.env.postgresql"
    
    # Backup current .env if it exists
    if os.path.exists(env_path):
        backup_path = f".env.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(env_path, backup_path)
        print(f"✅ Current .env backed up to: {backup_path}")
    
    # Copy PostgreSQL configuration
    try:
        shutil.copy2(postgresql_env_path, env_path)
        print("✅ PostgreSQL configuration activated")
        print("\n⚠️  IMPORTANT: Edit .env file to set your actual:")
        print("   - SECRET_KEY")
        print("   - JWT_SECRET_KEY")
        print("   - API keys (OpenAI, Plaid, Stripe, etc.)")
        return True
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def run_migration():
    """Run the database migration"""
    print_step(5, "Running database migration...")
    
    print("\n🔄 Starting migration from SQLite to PostgreSQL...")
    
    try:
        # Run the migration script
        result = subprocess.run([
            sys.executable, 
            "./tools/migrate_to_postgresql.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Migration failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run migration: {e}")
        return False

def test_connection():
    """Test the PostgreSQL connection"""
    print_step(6, "Testing PostgreSQL connection...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cora_db",
            user="cora_user",
            password="cora_password"
        )
        conn.close()
        print("✅ PostgreSQL connection successful!")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print_header("PostgreSQL Setup for CORA")
    print("\nThis script will help you migrate from SQLite to PostgreSQL")
    print("to handle concurrent users without crashes.")
    
    # Step 1: Check PostgreSQL
    if not check_postgresql():
        print("\n❌ Setup cannot continue without PostgreSQL")
        return False
    
    # Step 2: Create database
    if not create_database():
        print("\n❌ Setup cannot continue without database")
        return False
    
    # Step 3: Backup SQLite
    if not backup_sqlite():
        response = input("\nContinue without backup? (y/n): ")
        if response.lower() != 'y':
            return False
    
    # Step 4: Update .env file
    if not update_env_file():
        print("\n❌ Failed to update configuration")
        return False
    
    # Step 5: Test connection
    if not test_connection():
        print("\n❌ Cannot connect to PostgreSQL")
        print("Please check your PostgreSQL service and credentials")
        return False
    
    # Step 6: Run migration
    response = input("\n🚀 Ready to migrate data. Continue? (y/n): ")
    if response.lower() == 'y':
        if run_migration():
            print_header("Migration Complete!")
            print("\n✅ CORA is now using PostgreSQL!")
            print("\nNext steps:")
            print("1. Update your .env file with production values")
            print("2. Restart CORA: python app.py")
            print("3. Test with concurrent users: python tools/test_postgresql_concurrent.py")
            return True
        else:
            print("\n❌ Migration failed. Your SQLite database is still intact.")
            return False
    else:
        print("\n⚠️  Migration cancelled. No changes were made.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)