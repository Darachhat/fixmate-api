from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.database import get_db
from api.modules.users import models, schemas, service
from api.modules.auth.models import User
from api.core.rbac import require_role
from api.shared.enums import UserRole
from api.modules.auth.dependencies import get_current_user
from api.core.log import logger
import shutil
import os

router = APIRouter(prefix="/technicians", tags=["Technicians"])

@router.post("/apply", response_model=schemas.TechnicianResponse)
async def apply_as_technician(
    tech_in: schemas.TechnicianCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TECHNICIAN))
):
    tech = await service.create_technician_profile(db, current_user.id, tech_in)
    logger.track(f"Technician profile created: {current_user.email}")
    return tech

@router.get("/me", response_model=schemas.TechnicianResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TECHNICIAN))
):
    tech = await service.get_technician_by_user_id(db, current_user.id)
    if not tech:
        raise HTTPException(status_code=404, detail="Profile not found")
    return tech

@router.put("/{technician_id}/approve", response_model=schemas.TechnicianResponse)
async def approve_technician(
    technician_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    tech = await service.verify_technician(db, technician_id)
    logger.track(f"Technician {technician_id} approved by ADMIN {current_user.email}")
    return tech

@router.post("/documents", response_model=schemas.TechnicianDocumentResponse)
async def upload_document(
    document_type: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TECHNICIAN))
):
    tech = await service.get_technician_by_user_id(db, current_user.id)
    if not tech:
        raise HTTPException(status_code=404, detail="Technician profile not found")
    
    # Save file
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_location = f"{upload_dir}/{tech.id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Save DB record
    doc = models.TechnicianDocument(
        technician_id=tech.id,
        file_url=file_location,
        document_type=document_type
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc
