import os
import shutil
from uuid import UUID, uuid4
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.app.assessments.models import Evidence
from src.backend.config import settings

UPLOAD_DIR = "uploads/evidence"

class EvidenceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    async def upload_evidence(self, response_id: UUID, file: UploadFile, user_id: UUID) -> Evidence:
        # Generate safe filename
        ext = os.path.splitext(file.filename)[1]
        safe_filename = f"{uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file (Blocking I/O in async? Ideally use aiofiles or threadpool, but for small files/POC shutil is OK or sync open)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Create record
        evidence = Evidence(
            response_id=response_id,
            file_name=file.filename,
            file_url=file_path, # In production, S3 URL
            mime_type=file.content_type,
            uploaded_by=user_id
        )
        self.session.add(evidence)
        await self.session.commit()
        await self.session.refresh(evidence)
        return evidence
    
    async def delete_evidence(self, evidence_id: UUID) -> bool:
        pass # Todo: Implement if needed
