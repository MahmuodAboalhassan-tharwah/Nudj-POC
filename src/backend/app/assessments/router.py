from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db
from src.backend.app.auth.dependencies import get_current_user
from src.backend.app.auth.models import User
from src.backend.app.assessments.schemas import (
    AssessmentCreate, AssessmentResponse, AssessmentUpdate,
    AssessmentDomainResponse, AssessmentElementUpdate, AssessmentElementResponseSchema
)
from src.backend.app.assessments.service import AssessmentService
from src.backend.app.assessments.evidence_service import EvidenceService
from src.backend.app.assessments.models import AssessmentStatus

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    data: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    # Optional: check permissions (e.g. only CLIENT_ADMIN or ANALYST)
    return await service.create_assessment(data, current_user.id)

@router.get("/", response_model=List[AssessmentResponse])
async def list_assessments(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    # Filter by user's organization if they are CLIENT_ADMIN/ASSESSOR
    # If ANALYST, maybe list all or specific org
    org_id = current_user.organization_id # Assuming user has this
    if not org_id:
         # Fallback or error if user has no org (e.g. Super Admin w/o org context?)
         # For now return empty or handle based on role.
         return []
    return await service.list_assessments(org_id, skip, limit)

@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    assessment = await service.get_assessment(assessment_id)
    # Check access: organization must match OR user must be delegated
    if not await service.check_access(current_user.id, current_user.role, assessment_id):
         raise HTTPException(status_code=403, detail="Not authorized to view this assessment")
    return assessment

@router.patch("/{assessment_id}", response_model=AssessmentResponse)
async def update_assessment(
    assessment_id: UUID,
    data: AssessmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    # Check permissions
    # ...
    return await service.update_assessment(assessment_id, data)

@router.post("/{assessment_id}/domains/{domain_id}/assign", response_model=AssessmentDomainResponse)
async def assign_domain(
    assessment_id: UUID,
    domain_id: UUID,
    assignee_id: UUID, # Should probably be in body
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    return await service.update_domain_assignee(assessment_id, domain_id, assignee_id)

@router.post("/responses/{response_id}", response_model=AssessmentElementResponseSchema)
async def submit_response(
    response_id: UUID,
    data: AssessmentElementUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    # The service now handles access checks during update
    try:
        return await service.update_element_response(response_id, data, current_user.id, current_user.role)
    except AssessmentNotFound:
        raise HTTPException(status_code=403, detail="Permission denied to edit this response")

@router.post("/responses/{response_id}/evidence", status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    response_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = EvidenceService(db)
    return await service.upload_evidence(response_id, file, current_user.id)
