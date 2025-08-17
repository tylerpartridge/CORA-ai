#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/pdf_export.py
🎯 PURPOSE: PDF export API endpoints for profit intelligence reports
🔗 IMPORTS: FastAPI, PDF exporter, authentication
📤 EXPORTS: PDF export router
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import os
from datetime import datetime

from models import get_db, User
from dependencies.auth import get_current_user
from utils.pdf_exporter import pdf_exporter
from services.profit_leak_detector import ProfitLeakDetector
from utils.error_constants import (
    ErrorMessages, 
    STATUS_NOT_FOUND, 
    STATUS_FORBIDDEN, 
    STATUS_SERVER_ERROR,
    STATUS_BAD_REQUEST,
    ERROR_ACCESS_DENIED
)

router = APIRouter(
    prefix="/api/pdf-export",
    tags=["PDF Export"],
    responses={404: {"description": "Not found"}}
)

def calculate_intelligence_score(db: Session, user_id: int) -> int:
    """Calculate basic intelligence score based on user data"""
    # Simple calculation for now - can be enhanced later
    base_score = 70
    
    # Add points for having expenses tracked
    from models import Expense
    expense_count = db.query(Expense).filter(Expense.user_id == user_id).count()
    if expense_count > 0:
        base_score += min(10, expense_count // 10)  # Up to 10 points
    
    # Add points for having jobs
    from models import Job
    job_count = db.query(Job).filter(Job.user_id == user_id).count()
    if job_count > 0:
        base_score += min(10, job_count * 2)  # Up to 10 points
    
    return min(100, base_score)  # Cap at 100

@router.post("/profit-intelligence/full-report")
async def generate_full_profit_intelligence_report(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate comprehensive profit intelligence PDF report
    Includes all 5 sections: forecasting, vendors, jobs, pricing, benchmarks
    """
    try:
        # Get profit intelligence data
        detector = ProfitLeakDetector(db, current_user.id)
        
        # DEMO DATA: Using sample data for PDF generation
        data = {
            "is_demo_data": True,  # IMPORTANT: This is demonstration data
            "intelligenceScore": calculate_intelligence_score(db, current_user.id),  # Real calculation
            "letterGrade": "B+",  # (DEMO)
            "monthlySavingsPotential": 15420,
            "costTrend": -12.5,
            "vendorCount": 23,
            "forecast": {
                "months": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                "actual": [45000, 52000, 48000, 55000, 58000, 62000],
                "predicted": [None, None, None, 61000, 65000, 68000]
            },
            "vendors": [
                {"name": "ABC Construction", "performance": 92, "cost": 45000, "trend": 5.2},
                {"name": "XYZ Materials", "performance": 88, "cost": 32000, "trend": -2.1},
                {"name": "Best Tools Co", "performance": 85, "cost": 28000, "trend": 1.8},
                {"name": "Quality Lumber", "performance": 82, "cost": 22000, "trend": -1.5},
                {"name": "Pro Electric", "performance": 79, "cost": 18000, "trend": 3.2}
            ],
            "jobs": [
                {"name": "Kitchen Remodel - Smith", "risk": "high", "potential": 25000, "completion": 65},
                {"name": "Bathroom Addition - Johnson", "risk": "low", "potential": 18000, "completion": 85},
                {"name": "Deck Construction - Davis", "risk": "medium", "potential": 12000, "completion": 45}
            ],
            "pricing": {
                "marketAverage": 118,
                "yourAverage": 125,
                "recommendations": [
                    {"service": "Kitchen Remodel", "currentPrice": 125, "suggestedPrice": 135, "confidence": 85},
                    {"service": "Bathroom Remodel", "currentPrice": 95, "suggestedPrice": 102, "confidence": 78},
                    {"service": "Deck Construction", "currentPrice": 45, "suggestedPrice": 48, "confidence": 92}
                ]
            },
            "benchmarks": {
                "profitMargin": {"your": 18.5, "industry": 15.2},
                "completionRate": {"your": 94, "industry": 87},
                "satisfaction": {"your": 4.2, "industry": 3.8},
                "efficiency": {"your": 78, "industry": 72}
            }
        }
        
        # Generate PDF report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"profit_intelligence_full_report_{current_user.id}_{timestamp}.pdf"
        output_path = f"reports/{filename}"
        
        pdf_path = pdf_exporter.generate_profit_intelligence_report(data, output_path)
        
        return {
            "status": "success",
            "message": "Full profit intelligence report generated successfully",
            "filename": filename,
            "download_url": f"/api/pdf-export/download/{filename}",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.post("/profit-intelligence/section/{section_name}")
async def generate_section_report(
    section_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate PDF report for a specific profit intelligence section
    Valid sections: forecasting, vendors, jobs, pricing, benchmarks
    """
    valid_sections = ["forecasting", "vendors", "jobs", "pricing", "benchmarks"]
    
    if section_name not in valid_sections:
        raise HTTPException(status_code=400, detail=f"Invalid section. Must be one of: {valid_sections}")
    
    try:
        # Get section-specific data
        detector = ProfitLeakDetector(db, current_user.id)
        
        # Mock data for now - will be replaced with real data
        data = {
            "intelligenceScore": 87,
            "letterGrade": "B+",
            "forecast": {
                "months": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                "actual": [45000, 52000, 48000, 55000, 58000, 62000],
                "predicted": [None, None, None, 61000, 65000, 68000]
            },
            "vendors": [
                {"name": "ABC Construction", "performance": 92, "cost": 45000, "trend": 5.2},
                {"name": "XYZ Materials", "performance": 88, "cost": 32000, "trend": -2.1},
                {"name": "Best Tools Co", "performance": 85, "cost": 28000, "trend": 1.8},
                {"name": "Quality Lumber", "performance": 82, "cost": 22000, "trend": -1.5},
                {"name": "Pro Electric", "performance": 79, "cost": 18000, "trend": 3.2}
            ],
            "jobs": [
                {"name": "Kitchen Remodel - Smith", "risk": "high", "potential": 25000, "completion": 65},
                {"name": "Bathroom Addition - Johnson", "risk": "low", "potential": 18000, "completion": 85},
                {"name": "Deck Construction - Davis", "risk": "medium", "potential": 12000, "completion": 45}
            ],
            "pricing": {
                "marketAverage": 118,
                "yourAverage": 125,
                "recommendations": [
                    {"service": "Kitchen Remodel", "currentPrice": 125, "suggestedPrice": 135, "confidence": 85},
                    {"service": "Bathroom Remodel", "currentPrice": 95, "suggestedPrice": 102, "confidence": 78},
                    {"service": "Deck Construction", "currentPrice": 45, "suggestedPrice": 48, "confidence": 92}
                ]
            },
            "benchmarks": {
                "profitMargin": {"your": 18.5, "industry": 15.2},
                "completionRate": {"your": 94, "industry": 87},
                "satisfaction": {"your": 4.2, "industry": 3.8},
                "efficiency": {"your": 78, "industry": 72}
            }
        }
        
        # Generate section-specific PDF report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{section_name}_report_{current_user.id}_{timestamp}.pdf"
        output_path = f"reports/{filename}"
        
        pdf_path = pdf_exporter.generate_section_report(section_name, data, output_path)
        
        return {
            "status": "success",
            "message": f"{section_name.title()} report generated successfully",
            "filename": filename,
            "download_url": f"/api/pdf-export/download/{filename}",
            "section": section_name,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate {section_name} report: {str(e)}")

@router.get("/download/{filename}")
async def download_pdf_report(
    filename: str,
    current_user: User = Depends(get_current_user)
) -> FileResponse:
    """
    Download a generated PDF report
    """
    try:
        file_path = f"reports/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=STATUS_NOT_FOUND, detail=ErrorMessages.not_found("report file"))
        
        # Basic security check - ensure user can only download their own reports
        if str(current_user.id) not in filename:
            raise HTTPException(status_code=STATUS_FORBIDDEN, detail=ERROR_ACCESS_DENIED)
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")

@router.get("/reports/list")
async def list_user_reports(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List all PDF reports generated by the user
    """
    try:
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            return {
                "status": "success",
                "reports": [],
                "count": 0
            }
        
        user_reports = []
        for filename in os.listdir(reports_dir):
            if filename.endswith('.pdf') and str(current_user.id) in filename:
                file_path = os.path.join(reports_dir, filename)
                file_stats = os.stat(file_path)
                
                user_reports.append({
                    "filename": filename,
                    "size_bytes": file_stats.st_size,
                    "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "download_url": f"/api/pdf-export/download/{filename}"
                })
        
        # Sort by creation date (newest first)
        user_reports.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "status": "success",
            "reports": user_reports,
            "count": len(user_reports)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")

@router.delete("/reports/{filename}")
async def delete_report(
    filename: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a user's PDF report
    """
    try:
        file_path = f"reports/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=STATUS_NOT_FOUND, detail=ErrorMessages.not_found("report file"))
        
        # Security check - ensure user can only delete their own reports
        if str(current_user.id) not in filename:
            raise HTTPException(status_code=STATUS_FORBIDDEN, detail=ERROR_ACCESS_DENIED)
        
        os.remove(file_path)
        
        return {
            "status": "success",
            "message": f"Report {filename} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

@router.get("/health")
async def pdf_export_health() -> Dict[str, str]:
    """
    Health check for PDF export service
    """
    return {
        "status": "healthy",
        "service": "PDF Export",
        "version": "1.0.0"
    } 