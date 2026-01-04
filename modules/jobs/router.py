from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.database import get_db
from api.modules.jobs import models, schemas, service
from api.modules.auth.models import User
from api.core.rbac import require_role
from api.shared.enums import UserRole
from api.core.log import logger

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=schemas.JobResponse)
async def create_job(
    job_in: schemas.JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CUSTOMER))
):
    job = await service.create_job(db, current_user.id, job_in)
    logger.track(f"Job created: {job.id} by Customer {current_user.email}")
    return job

@router.get("/{job_id}", response_model=schemas.JobResponse)
async def get_job_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CUSTOMER, UserRole.TECHNICIAN, UserRole.ADMIN))
):
    job = await service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Ownership checks omitted for brevity (handled in service or here)
    return job

@router.post("/{job_id}/accept", response_model=schemas.JobResponse)
async def accept_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TECHNICIAN))
):
    # Logic to find offer... (simplified from previous step)
    tech = current_user.technician_profile[0]
    from sqlalchemy import select
    from api.modules.jobs.models import JobOffer
    from api.shared.enums import JobOfferStatus

    result = await db.execute(select(JobOffer).where(
        JobOffer.job_id == job_id,
        JobOffer.technician_id == tech.id,
        JobOffer.status == JobOfferStatus.PENDING
    ))
    offer = result.scalars().first()
    if not offer:
        logger.warn(f"Job accept failed: No active offer - Job {job_id}, Tech {tech.id}")
        raise HTTPException(status_code=400, detail="No active offer found")
    
    job = await service.accept_job_offer(db, offer.id, tech.id)
    logger.info(f"Job accepted: {job.id} by Tech {tech.id}")
    return job

@router.post("/{job_id}/start", response_model=schemas.JobResponse)
async def start_job_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TECHNICIAN))
):
    tech = current_user.technician_profile[0]
    job = await service.start_job(db, job_id, tech.id)
    logger.info(f"Job started: {job_id}")
    return job

@router.post("/{job_id}/complete", response_model=schemas.JobResponse)
async def complete_job_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TECHNICIAN))
):
    tech = current_user.technician_profile[0]
    job = await service.complete_job(db, job_id, tech.id)
    logger.track(f"Job completed: {job_id} by Tech {tech.id}")
    return job

@router.post("/{job_id}/cancel", response_model=schemas.JobResponse)
async def cancel_job_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CUSTOMER, UserRole.TECHNICIAN, UserRole.ADMIN))
):
    tech_id = current_user.technician_profile[0].id if current_user.role == UserRole.TECHNICIAN and current_user.technician_profile else None
    uid = tech_id if current_user.role == UserRole.TECHNICIAN else current_user.id
    
    job = await service.cancel_job(db, job_id, uid, current_user.role)
    logger.warn(f"Job cancelled: {job_id} by {current_user.email} [{current_user.role}]")
    return job
