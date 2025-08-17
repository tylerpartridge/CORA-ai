#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/backup_manager.py
🎯 PURPOSE: Backup management and monitoring interface with API integration
🔗 IMPORTS: secure_backup, logging, json, fastapi, threading
📤 EXPORTS: BackupManager, backup_api_router
"""

import logging
import json
import threading
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from .secure_backup import SecureBackup, AutomatedBackupScheduler, BackupRecoverySystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupManager:
    """Centralized backup management system"""
    
    def __init__(self):
        """Initialize backup manager"""
        self.backup_system = SecureBackup()
        self.scheduler = AutomatedBackupScheduler(self.backup_system)
        self.recovery_system = BackupRecoverySystem(self.backup_system)
        self.scheduler_thread = None
        self.is_running = False
        
        # Setup status tracking
        self.status = {
            "scheduler_running": False,
            "last_backup": None,
            "backup_count": 0,
            "last_error": None,
            "next_scheduled": None
        }
        
        # Load backup statistics
        self._load_backup_stats()
    
    def _load_backup_stats(self):
        """Load backup statistics"""
        try:
            backups = self.backup_system.list_backups()
            self.status["backup_count"] = len(backups)
            if backups:
                self.status["last_backup"] = backups[0]
        except Exception as e:
            logger.error(f"Failed to load backup stats: {str(e)}")
    
    def start_automated_backup(self):
        """Start automated backup scheduler"""
        try:
            if not self.is_running:
                self.scheduler.start_scheduler()
                self.is_running = True
                self.status["scheduler_running"] = True
                logger.info("Automated backup scheduler started")
                return {"success": True, "message": "Automated backup scheduler started"}
            else:
                return {"success": False, "message": "Scheduler already running"}
        except Exception as e:
            logger.error(f"Failed to start backup scheduler: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def stop_automated_backup(self):
        """Stop automated backup scheduler"""
        try:
            if self.is_running:
                self.scheduler.stop_scheduler()
                self.is_running = False
                self.status["scheduler_running"] = False
                logger.info("Automated backup scheduler stopped")
                return {"success": True, "message": "Automated backup scheduler stopped"}
            else:
                return {"success": False, "message": "Scheduler not running"}
        except Exception as e:
            logger.error(f"Failed to stop backup scheduler: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_manual_backup(self, include_logs: bool = True):
        """Create manual backup"""
        try:
            backup_path = self.backup_system.create_secure_backup(include_logs=include_logs)
            self._load_backup_stats()
            logger.info(f"Manual backup created: {backup_path}")
            return {
                "success": True,
                "backup_path": backup_path,
                "includes_logs": include_logs,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to create manual backup: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_backup_status(self):
        """Get comprehensive backup status"""
        try:
            scheduler_status = self.scheduler.get_status()
            backups = self.backup_system.list_backups()
            
            return {
                "scheduler": scheduler_status,
                "backups": backups,
                "total_backups": len(backups),
                "manager_status": self.status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get backup status: {str(e)}")
            return {"error": str(e)}
    
    def verify_backup(self, backup_filename: str):
        """Verify backup integrity"""
        try:
            backup_path = Path("backups") / backup_filename
            if not backup_path.exists():
                return {"success": False, "error": "Backup file not found"}
            
            result = self.recovery_system.verify_backup_integrity(str(backup_path))
            return {"success": True, "verification": result}
        except Exception as e:
            logger.error(f"Failed to verify backup: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_recovery(self, backup_filename: str):
        """Test backup recovery"""
        try:
            backup_path = Path("backups") / backup_filename
            if not backup_path.exists():
                return {"success": False, "error": "Backup file not found"}
            
            result = self.recovery_system.test_recovery(str(backup_path))
            return {"success": True, "test_result": result}
        except Exception as e:
            logger.error(f"Failed to test recovery: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def cleanup_old_backups(self, days_to_keep: int = 30):
        """Clean up old backups"""
        try:
            self.backup_system.cleanup_old_backups(days_to_keep)
            self._load_backup_stats()
            return {"success": True, "message": f"Cleaned up backups older than {days_to_keep} days"}
        except Exception as e:
            logger.error(f"Failed to cleanup backups: {str(e)}")
            return {"success": False, "error": str(e)}

# Global backup manager instance
backup_manager = BackupManager()

# FastAPI router for backup API endpoints
backup_api_router = APIRouter(prefix="/api/backup", tags=["backup"])

@backup_api_router.get("/status")
async def get_backup_status():
    """Get backup system status"""
    try:
        status = backup_manager.get_backup_status()
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@backup_api_router.post("/start")
async def start_automated_backup():
    """Start automated backup scheduler"""
    try:
        result = backup_manager.start_automated_backup()
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=result.get("error", result["message"]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@backup_api_router.post("/stop")
async def stop_automated_backup():
    """Stop automated backup scheduler"""
    try:
        result = backup_manager.stop_automated_backup()
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=result.get("error", result["message"]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@backup_api_router.post("/create")
async def create_backup(include_logs: bool = True):
    """Create manual backup"""
    try:
        result = backup_manager.create_manual_backup(include_logs)
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@backup_api_router.get("/list")
async def list_backups():
    """List all available backups"""
    try:
        backups = backup_manager.backup_system.list_backups()
        return JSONResponse(content={"backups": backups, "count": len(backups)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@backup_api_router.post("/verify/{backup_filename}")
async def verify_backup(backup_filename: str):
    """Verify backup integrity"""
    try:
        result = backup_manager.verify_backup(backup_filename)
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@backup_api_router.post("/test-recovery/{backup_filename}")
async def test_recovery(backup_filename: str):
    """Test backup recovery"""
    try:
        result = backup_manager.test_recovery(backup_filename)
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@backup_api_router.post("/cleanup")
async def cleanup_backups(days_to_keep: int = 30):
    """Clean up old backups"""
    try:
        result = backup_manager.cleanup_old_backups(days_to_keep)
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@backup_api_router.post("/emergency-recovery/{backup_filename}")
async def emergency_recovery(backup_filename: str, target_dir: str = "emergency_restore"):
    """Emergency recovery procedure"""
    try:
        backup_path = Path("backups") / backup_filename
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        result = backup_manager.recovery_system.emergency_recovery(str(backup_path), target_dir)
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task to start scheduler on application startup
def start_backup_scheduler_on_startup():
    """Start backup scheduler when application starts"""
    try:
        logger.info("Starting backup scheduler on application startup...")
        backup_manager.start_automated_backup()
    except Exception as e:
        logger.error(f"Failed to start backup scheduler on startup: {str(e)}")

# Export the startup function
__all__ = ["backup_manager", "backup_api_router", "start_backup_scheduler_on_startup"] 