#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/secure_backup.py
🎯 PURPOSE: Automated secure backup system with encryption, scheduling, and recovery
🔗 IMPORTS: sqlite3, cryptography, zipfile, json, datetime, schedule, threading, time
📤 EXPORTS: create_secure_backup, restore_secure_backup, list_backups, AutomatedBackupScheduler
"""

import sqlite3
import zipfile
import json
import os
import shutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging
import schedule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureBackup:
    def __init__(self, backup_dir: str = "backups", encryption_key: str = None):
        """Initialize secure backup system"""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Generate or use encryption key
        if encryption_key:
            self.encryption_key = self._derive_key(encryption_key)
        else:
            # Use environment variable or generate new key
            env_key = os.getenv("BACKUP_ENCRYPTION_KEY")
            if env_key:
                self.encryption_key = self._derive_key(env_key)
            else:
                # No env key set; operate without logging sensitive material
                # Prefer a non-persistent ephemeral key without exposing value
                new_key = Fernet.generate_key()
                logger.info("Backup encryption key loaded from env or not set; using ephemeral in-memory key")
                self.encryption_key = new_key
        
        self.cipher = Fernet(self.encryption_key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        salt = b'cora_backup_salt'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using Fernet"""
        return self.cipher.encrypt(data)
    
    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using Fernet"""
        return self.cipher.decrypt(encrypted_data)
    
    def create_secure_backup(self, include_logs: bool = True) -> str:
        """Create a secure encrypted backup of the system"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"cora_backup_{timestamp}.zip.enc"
            backup_path = self.backup_dir / backup_filename
            
            # Create temporary directory for backup contents
            temp_dir = Path("temp_backup")
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # Backup database
                self._backup_database(temp_dir)
                
                # Backup configuration files
                self._backup_config_files(temp_dir)
                
                # Backup logs if requested
                if include_logs:
                    self._backup_logs(temp_dir)
                
                # Create metadata
                metadata = {
                    "backup_timestamp": timestamp,
                    "backup_version": "1.0",
                    "includes_logs": include_logs,
                    "created_by": "CORA Secure Backup System",
                    "encryption_method": "Fernet (AES-128-CBC)",
                    "files": []
                }
                
                # List all files in temp directory
                for file_path in temp_dir.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(temp_dir)
                        metadata["files"].append(str(relative_path))
                
                # Save metadata
                with open(temp_dir / "backup_metadata.json", "w") as f:
                    json.dump(metadata, f, indent=2)
                
                # Create encrypted zip file
                self._create_encrypted_zip(temp_dir, backup_path)
                
                logger.info(f"Secure backup created: {backup_path}")
                return str(backup_path)
                
            finally:
                # Clean up temporary directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            logger.error(f"Failed to create secure backup: {str(e)}")
            raise
    
    def _backup_database(self, temp_dir: Path):
        """Backup SQLite database"""
        db_path = Path("data/cora.db")
        if db_path.exists():
            # Create a copy of the database
            backup_db = temp_dir / "database" / "cora.db"
            backup_db.parent.mkdir(exist_ok=True)
            shutil.copy2(db_path, backup_db)
            
            # Also create SQL dump
            dump_path = temp_dir / "database" / "cora_dump.sql"
            self._create_sql_dump(db_path, dump_path)
            
            logger.info("Database backed up successfully")
        else:
            logger.warning("Database file not found, skipping database backup")
    
    def _create_sql_dump(self, db_path: Path, dump_path: Path):
        """Create SQL dump of database"""
        try:
            conn = sqlite3.connect(db_path)
            with open(dump_path, 'w') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            conn.close()
        except Exception as e:
            logger.error(f"Failed to create SQL dump: {str(e)}")
    
    def _backup_config_files(self, temp_dir: Path):
        """Backup configuration files"""
        config_dir = temp_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Backup environment template
        env_template = Path("config/env.production.template")
        if env_template.exists():
            shutil.copy2(env_template, config_dir / "env.production.template")
        
        # Backup other config files
        config_files = [
            "requirements.txt",
            "runtime.txt",
            "Procfile"
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                shutil.copy2(config_file, config_dir / config_file)
        
        logger.info("Configuration files backed up")
    
    def _backup_logs(self, temp_dir: Path):
        """Backup log files"""
        logs_dir = temp_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Backup audit logs
        audit_log = Path("logs/audit.log")
        if audit_log.exists():
            shutil.copy2(audit_log, logs_dir / "audit.log")
        
        # Backup other log files
        log_patterns = ["*.log", "*.txt"]
        for pattern in log_patterns:
            for log_file in Path("logs").glob(pattern):
                if log_file.is_file():
                    shutil.copy2(log_file, logs_dir / log_file.name)
        
        logger.info("Log files backed up")
    
    def _create_encrypted_zip(self, source_dir: Path, output_path: Path):
        """Create encrypted zip file"""
        # Create temporary zip file
        temp_zip = Path("temp_backup.zip")
        
        try:
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in source_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(source_dir)
                        zipf.write(file_path, arcname)
            
            # Encrypt the zip file
            with open(temp_zip, 'rb') as f:
                zip_data = f.read()
            
            encrypted_data = self._encrypt_data(zip_data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
                
        finally:
            # Clean up temporary zip
            if temp_zip.exists():
                temp_zip.unlink()
    
    def restore_secure_backup(self, backup_path: str, restore_dir: str = "restore") -> bool:
        """Restore from secure encrypted backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            restore_path = Path(restore_dir)
            restore_path.mkdir(exist_ok=True)
            
            # Decrypt and extract backup
            with open(backup_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._decrypt_data(encrypted_data)
            
            # Create temporary zip file
            temp_zip = restore_path / "temp_backup.zip"
            with open(temp_zip, 'wb') as f:
                f.write(decrypted_data)
            
            # Extract zip file
            with zipfile.ZipFile(temp_zip, 'r') as zipf:
                zipf.extractall(restore_path)
            
            # Clean up temporary zip
            temp_zip.unlink()
            
            logger.info(f"Backup restored to: {restore_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {str(e)}")
            return False
    
    def list_backups(self) -> list:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.enc"):
            try:
                # Try to get file info
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                logger.warning(f"Could not read backup info for {backup_file}: {str(e)}")
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def cleanup_old_backups(self, days_to_keep: int = 30):
        """Remove backups older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_count = 0
        
        for backup_file in self.backup_dir.glob("*.enc"):
            try:
                if datetime.fromtimestamp(backup_file.stat().st_ctime) < cutoff_date:
                    backup_file.unlink()
                    removed_count += 1
                    logger.info(f"Removed old backup: {backup_file.name}")
            except Exception as e:
                logger.error(f"Failed to remove old backup {backup_file}: {str(e)}")
        
        logger.info(f"Cleanup complete: removed {removed_count} old backups")

class AutomatedBackupScheduler:
    """Automated backup scheduler with monitoring and recovery capabilities"""
    
    def __init__(self, backup_system: SecureBackup, schedule_config: dict = None):
        """Initialize automated backup scheduler"""
        self.backup_system = backup_system
        self.scheduler_thread = None
        self.is_running = False
        self.last_backup_status = {"success": False, "timestamp": None, "error": None}
        
        # Default schedule: daily at 2 AM
        self.schedule_config = schedule_config or {
            "daily_backup": "02:00",
            "weekly_backup": "sunday 03:00",
            "monthly_backup": "1 04:00",  # 1st of month at 4 AM
            "cleanup_old_backups": "05:00"  # Daily cleanup at 5 AM
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup backup scheduler logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        backup_logger = logging.getLogger("backup_scheduler")
        backup_logger.setLevel(logging.INFO)
        
        # File handler for backup logs
        file_handler = logging.FileHandler(log_dir / "backup_scheduler.log")
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        backup_logger.addHandler(file_handler)
        backup_logger.addHandler(console_handler)
        
        self.logger = backup_logger
    
    def setup_schedule(self):
        """Setup automated backup schedule"""
        try:
            # Daily backup
            schedule.every().day.at(self.schedule_config["daily_backup"]).do(
                self._run_daily_backup
            )
            
            # Weekly backup (with logs)
            schedule.every().sunday.at(self.schedule_config["weekly_backup"].split()[1]).do(
                self._run_weekly_backup
            )
            
            # Monthly backup (full system) - using day of month instead of .month
            day_of_month = int(self.schedule_config["monthly_backup"].split()[0])
            time_of_day = self.schedule_config["monthly_backup"].split()[1]
            schedule.every().day.at(time_of_day).do(
                self._run_monthly_backup_if_day_matches, day_of_month
            )
            
            # Daily cleanup
            schedule.every().day.at(self.schedule_config["cleanup_old_backups"]).do(
                self._run_cleanup
            )
            
            self.logger.info("Backup schedule configured successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup backup schedule: {str(e)}")
            raise
    
    def _run_daily_backup(self):
        """Run daily backup (database + config)"""
        try:
            self.logger.info("Starting daily backup...")
            backup_path = self.backup_system.create_secure_backup(include_logs=False)
            self.last_backup_status = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "backup_path": backup_path,
                "type": "daily"
            }
            self.logger.info(f"Daily backup completed: {backup_path}")
            
        except Exception as e:
            self.last_backup_status = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "type": "daily"
            }
            self.logger.error(f"Daily backup failed: {str(e)}")
    
    def _run_weekly_backup(self):
        """Run weekly backup (database + config + logs)"""
        try:
            self.logger.info("Starting weekly backup...")
            backup_path = self.backup_system.create_secure_backup(include_logs=True)
            self.last_backup_status = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "backup_path": backup_path,
                "type": "weekly"
            }
            self.logger.info(f"Weekly backup completed: {backup_path}")
            
        except Exception as e:
            self.last_backup_status = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "type": "weekly"
            }
            self.logger.error(f"Weekly backup failed: {str(e)}")
    
    def _run_monthly_backup_if_day_matches(self, day_of_month):
        """Run monthly backup only if it's the correct day of month"""
        current_day = datetime.now().day
        if current_day == day_of_month:
            self._run_monthly_backup()
    
    def _run_monthly_backup(self):
        """Run monthly backup (full system backup)"""
        try:
            self.logger.info("Starting monthly backup...")
            backup_path = self.backup_system.create_secure_backup(include_logs=True)
            self.last_backup_status = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "backup_path": backup_path,
                "type": "monthly"
            }
            self.logger.info(f"Monthly backup completed: {backup_path}")
            
        except Exception as e:
            self.last_backup_status = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "type": "monthly"
            }
            self.logger.error(f"Monthly backup failed: {str(e)}")
    
    def _run_cleanup(self):
        """Run cleanup of old backups"""
        try:
            self.logger.info("Starting backup cleanup...")
            self.backup_system.cleanup_old_backups(days_to_keep=30)
            self.logger.info("Backup cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {str(e)}")
    
    def start_scheduler(self):
        """Start the automated backup scheduler"""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.setup_schedule()
        self.is_running = True
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Automated backup scheduler started")
    
    def stop_scheduler(self):
        """Stop the automated backup scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.logger.info("Automated backup scheduler stopped")
    
    def get_status(self) -> dict:
        """Get current scheduler status"""
        return {
            "is_running": self.is_running,
            "last_backup": self.last_backup_status,
            "next_run": self._get_next_runs(),
            "schedule_config": self.schedule_config
        }
    
    def _get_next_runs(self) -> dict:
        """Get next scheduled run times"""
        try:
            return {
                "daily_backup": schedule.next_run(),
                "weekly_backup": schedule.next_run(),
                "monthly_backup": schedule.next_run(),
                "cleanup": schedule.next_run()
            }
        except:
            return {"error": "Could not determine next runs"}

class BackupRecoverySystem:
    """Automated backup recovery and verification system"""
    
    def __init__(self, backup_system: SecureBackup):
        """Initialize recovery system"""
        self.backup_system = backup_system
        self.logger = logging.getLogger(__name__)
    
    def verify_backup_integrity(self, backup_path: str) -> dict:
        """Verify backup file integrity"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return {"valid": False, "error": "Backup file not found"}
            
            # Check file size
            file_size = backup_file.stat().st_size
            if file_size == 0:
                return {"valid": False, "error": "Backup file is empty"}
            
            # Try to decrypt and extract metadata
            try:
                with open(backup_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.backup_system._decrypt_data(encrypted_data)
                
                # Create temporary file to check zip integrity
                temp_zip = Path("temp_verify.zip")
                with open(temp_zip, 'wb') as f:
                    f.write(decrypted_data)
                
                # Check zip file integrity
                with zipfile.ZipFile(temp_zip, 'r') as zipf:
                    # Test zip file
                    zipf.testzip()
                    
                    # Check for metadata file
                    if "backup_metadata.json" not in zipf.namelist():
                        return {"valid": False, "error": "Missing backup metadata"}
                    
                    # Read metadata
                    metadata = json.loads(zipf.read("backup_metadata.json"))
                
                # Clean up
                temp_zip.unlink()
                
                return {
                    "valid": True,
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "metadata": metadata,
                    "backup_timestamp": metadata.get("backup_timestamp"),
                    "includes_logs": metadata.get("includes_logs", False)
                }
                
            except Exception as e:
                return {"valid": False, "error": f"Backup corruption detected: {str(e)}"}
                
        except Exception as e:
            return {"valid": False, "error": f"Verification failed: {str(e)}"}
    
    def test_recovery(self, backup_path: str, test_dir: str = "test_recovery") -> dict:
        """Test backup recovery without affecting production"""
        try:
            self.logger.info(f"Testing recovery from: {backup_path}")
            
            # Verify backup first
            verification = self.verify_backup_integrity(backup_path)
            if not verification["valid"]:
                return {"success": False, "error": verification["error"]}
            
            # Test restore to temporary directory
            success = self.backup_system.restore_secure_backup(backup_path, test_dir)
            
            if success:
                # Verify restored files
                restored_files = list(Path(test_dir).rglob("*"))
                file_count = len([f for f in restored_files if f.is_file()])
                
                return {
                    "success": True,
                    "test_dir": test_dir,
                    "file_count": file_count,
                    "verification": verification
                }
            else:
                return {"success": False, "error": "Restore operation failed"}
                
        except Exception as e:
            return {"success": False, "error": f"Recovery test failed: {str(e)}"}
    
    def emergency_recovery(self, backup_path: str, target_dir: str = "emergency_restore") -> dict:
        """Emergency recovery procedure"""
        try:
            self.logger.warning(f"Starting emergency recovery from: {backup_path}")
            
            # Verify backup integrity
            verification = self.verify_backup_integrity(backup_path)
            if not verification["valid"]:
                return {"success": False, "error": verification["error"]}
            
            # Create recovery log
            recovery_log = Path("logs/emergency_recovery.log")
            recovery_log.parent.mkdir(exist_ok=True)
            
            with open(recovery_log, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - Emergency recovery started\n")
                f.write(f"Backup: {backup_path}\n")
                f.write(f"Target: {target_dir}\n")
            
            # Perform recovery
            success = self.backup_system.restore_secure_backup(backup_path, target_dir)
            
            if success:
                with open(recovery_log, 'a') as f:
                    f.write(f"{datetime.now().isoformat()} - Emergency recovery completed successfully\n")
                
                return {
                    "success": True,
                    "target_dir": target_dir,
                    "verification": verification,
                    "recovery_log": str(recovery_log)
                }
            else:
                with open(recovery_log, 'a') as f:
                    f.write(f"{datetime.now().isoformat()} - Emergency recovery failed\n")
                
                return {"success": False, "error": "Recovery operation failed"}
                
        except Exception as e:
            return {"success": False, "error": f"Emergency recovery failed: {str(e)}"}

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORA Automated Secure Backup System")
    parser.add_argument("action", choices=["create", "restore", "list", "cleanup", "start-scheduler", "stop-scheduler", "status", "verify", "test-recovery", "emergency-recovery"])
    parser.add_argument("--backup-file", help="Backup file for restore/verify/test")
    parser.add_argument("--days", type=int, default=30, help="Days to keep for cleanup")
    parser.add_argument("--no-logs", action="store_true", help="Exclude logs from backup")
    parser.add_argument("--target-dir", help="Target directory for recovery")
    
    args = parser.parse_args()
    
    backup_system = SecureBackup()
    
    if args.action == "create":
        backup_path = backup_system.create_secure_backup(include_logs=not args.no_logs)
        print(f"Backup created: {backup_path}")
    
    elif args.action == "restore":
        if not args.backup_file:
            print("Error: --backup-file required for restore")
            return
        success = backup_system.restore_secure_backup(args.backup_file, args.target_dir or "restore")
        if success:
            print("Backup restored successfully")
        else:
            print("Backup restore failed")
    
    elif args.action == "list":
        backups = backup_system.list_backups()
        if backups:
            print("Available backups:")
            for backup in backups:
                print(f"  {backup['filename']} ({backup['size_mb']}MB) - {backup['created']}")
        else:
            print("No backups found")
    
    elif args.action == "cleanup":
        backup_system.cleanup_old_backups(args.days)
        print(f"Cleanup completed (kept backups newer than {args.days} days)")
    
    elif args.action == "start-scheduler":
        scheduler = AutomatedBackupScheduler(backup_system)
        scheduler.start_scheduler()
        print("Automated backup scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop_scheduler()
            print("\nScheduler stopped.")
    
    elif args.action == "stop-scheduler":
        print("Scheduler stop command sent. Check logs for status.")
    
    elif args.action == "status":
        scheduler = AutomatedBackupScheduler(backup_system)
        status = scheduler.get_status()
        print("Backup Scheduler Status:")
        print(f"  Running: {status['is_running']}")
        print(f"  Last Backup: {status['last_backup']}")
        print(f"  Schedule Config: {status['schedule_config']}")
    
    elif args.action == "verify":
        if not args.backup_file:
            print("Error: --backup-file required for verify")
            return
        recovery_system = BackupRecoverySystem(backup_system)
        result = recovery_system.verify_backup_integrity(args.backup_file)
        if result["valid"]:
            print(f"Backup verified successfully:")
            print(f"  Size: {result['file_size_mb']}MB")
            print(f"  Timestamp: {result['backup_timestamp']}")
            print(f"  Includes Logs: {result['includes_logs']}")
        else:
            print(f"Backup verification failed: {result['error']}")
    
    elif args.action == "test-recovery":
        if not args.backup_file:
            print("Error: --backup-file required for test-recovery")
            return
        recovery_system = BackupRecoverySystem(backup_system)
        result = recovery_system.test_recovery(args.backup_file, args.target_dir or "test_recovery")
        if result["success"]:
            print(f"Recovery test successful:")
            print(f"  Test Directory: {result['test_dir']}")
            print(f"  Files Restored: {result['file_count']}")
        else:
            print(f"Recovery test failed: {result['error']}")
    
    elif args.action == "emergency-recovery":
        if not args.backup_file:
            print("Error: --backup-file required for emergency-recovery")
            return
        recovery_system = BackupRecoverySystem(backup_system)
        result = recovery_system.emergency_recovery(args.backup_file, args.target_dir or "emergency_restore")
        if result["success"]:
            print(f"Emergency recovery completed:")
            print(f"  Target Directory: {result['target_dir']}")
            print(f"  Recovery Log: {result['recovery_log']}")
        else:
            print(f"Emergency recovery failed: {result['error']}")

if __name__ == "__main__":
    main() 