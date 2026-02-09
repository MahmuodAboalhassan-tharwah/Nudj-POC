from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from io import BytesIO

from src.backend.app.auth.dependencies import get_current_user
from src.backend.app.auth.models import User
from src.backend.database import get_db
from src.backend.app.reports.service import ReportingService
# Correct import assuming generator.py is in the same package
from src.backend.app.reports.generator import PDFGenerator
import os

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/assessments/{assessment_id}/pdf")
async def download_assessment_report(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ReportingService(db)
    
    # Check if assessment exists and belongs to user's organization (unless Super Admin)
    assessment_data = await service.get_assessment_metadata(assessment_id)
    if not assessment_data:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    if current_user.role != "super_admin" and str(assessment_data.organization_id) != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    try:
        report_data = await service.get_assessment_report_data(assessment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
    # Generate PDF
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    generator = PDFGenerator(template_dir)
    pdf_bytes = generator.generate_report(report_data)
    
    # Return as stream
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=assessment_report_{assessment_id}.pdf"}
    )
