from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.modules.jobs import models, schemas
from api.shared.enums import JobStatus, JobOfferStatus
from fastapi import HTTPException
from datetime import datetime

async def get_job(db: AsyncSession, job_id: str):
    result = await db.execute(select(models.Job).where(models.Job.id == job_id))
    return result.scalars().first()

async def create_job(db: AsyncSession, user_id: str, job_in: schemas.JobCreate):
    db_job = models.Job(
        customer_id=user_id,
        **job_in.model_dump(),
        status=JobStatus.REQUESTED
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job

async def transition_job_status(db: AsyncSession, job_id: str, new_status: JobStatus):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # State Machine Logic
    valid_transitions = {
        JobStatus.REQUESTED: [JobStatus.MATCHING, JobStatus.CANCELLED],
        JobStatus.MATCHING: [JobStatus.ASSIGNED, JobStatus.REQUESTED, JobStatus.CANCELLED], # REQUESTED allowed if no match? Or Cancelled.
        JobStatus.ASSIGNED: [JobStatus.IN_PROGRESS, JobStatus.CANCELLED],
        JobStatus.IN_PROGRESS: [JobStatus.COMPLETED, JobStatus.CANCELLED], # Can cancel in progress? Maybe with penalty.
        JobStatus.COMPLETED: [], # Terminal
        JobStatus.CANCELLED: [], # Terminal
    }
    
    if new_status not in valid_transitions.get(job.status, []):
         raise HTTPException(
             status_code=400, 
             detail=f"Invalid state transition from {job.status} to {new_status}"
         )
    
    job.status = new_status
    await db.commit()
    await db.refresh(job)
    return job

async def accept_job_offer(db: AsyncSession, offer_id: str, technician_id: str):
    stmt = select(models.JobOffer).where(
        models.JobOffer.id == offer_id,
        models.JobOffer.technician_id == technician_id, # Ensure ownership
        models.JobOffer.status == JobOfferStatus.PENDING
    )
    result = await db.execute(stmt)
    offer = result.scalars().first()
    
    if not offer:
        raise HTTPException(status_code=400, detail="Offer not available or expired")
    
    # Check expiry explicitly if DB doesn't handle timezones perfectly or lag
    if offer.expires_at.replace(tzinfo=None) < datetime.utcnow():
         offer.status = JobOfferStatus.EXPIRED
         db.add(offer)
         await db.commit()
         raise HTTPException(status_code=400, detail="Offer expired")

    # Update Offer
    offer.status = JobOfferStatus.ACCEPTED
    
    # Update Job
    job = await get_job(db, offer.job_id)
    if not job:
         raise HTTPException(status_code=404, detail="Job not found")
    
    # Ensure job is still MATCHING?
    if job.status != JobStatus.MATCHING:
         raise HTTPException(status_code=400, detail="Job no longer active")

    job.status = JobStatus.ASSIGNED
    job.technician_id = technician_id
    
    db.add(offer)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def start_job(db: AsyncSession, job_id: str, technician_id: str):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.technician_id != technician_id:
        raise HTTPException(status_code=403, detail="Not assigned to this job")
        
    if job.status != JobStatus.ASSIGNED:
        raise HTTPException(status_code=400, detail="Job must be ASSIGNED to start")
        
    job.status = JobStatus.IN_PROGRESS
    await db.commit()
    await db.refresh(job)
    return job

async def complete_job(db: AsyncSession, job_id: str, technician_id: str):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.technician_id != technician_id:
        raise HTTPException(status_code=403, detail="Not assigned to this job")
        
    if job.status != JobStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Job must be IN_PROGRESS to complete")
        
    job.status = JobStatus.COMPLETED
    # Trigger payment calculation
    from api.modules.payments import service as payment_service
    await payment_service.create_payment_for_job(db, job)
    
    await db.commit()
    await db.refresh(job)
    return job

async def cancel_job(db: AsyncSession, job_id: str, user_id: str, role: str):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Auth checks
    if role == "CUSTOMER" and job.customer_id != user_id:
         raise HTTPException(status_code=403, detail="Not authorized")
    if role == "TECHNICIAN" and job.technician_id != user_id: # and not None?
         # If not assigned, technician cannot cancel? 
         # Step 9 says "Cancellation rules enforced".
         # Usually only assigned tech or customer can cancel.
         raise HTTPException(status_code=403, detail="Not authorized")
         
    if job.status in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Job already finished")
        
    job.status = JobStatus.CANCELLED
    await db.commit()
    await db.refresh(job)
    return job
