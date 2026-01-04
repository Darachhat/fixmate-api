from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.modules.disputes import models, schemas
from api.modules.jobs import models as job_models
from api.shared.enums import DisputeStatus
from fastapi import HTTPException
from datetime import datetime

async def create_dispute(db: AsyncSession, user_id: str, dispute_in: schemas.DisputeCreate):
    # Check if job exists
    job = await db.scalar(select(job_models.Job).where(job_models.Job.id == dispute_in.job_id))
    if not job:
         raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if user involved
    if job.customer_id != user_id and job.technician_id != user_id:
         raise HTTPException(status_code=403, detail="Not involved in this job")
         
    dispute = models.Dispute(
        job_id=job.id,
        created_by_id=user_id,
        reason=dispute_in.reason,
        status=DisputeStatus.OPEN
    )
    db.add(dispute)
    await db.commit()
    await db.refresh(dispute)
    return dispute

async def resolve_dispute(db: AsyncSession, dispute_id: str, resolve_in: schemas.DisputeResolve, admin_id: str):
    dispute = await db.scalar(select(models.Dispute).where(models.Dispute.id == dispute_id))
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
        
    dispute.status = resolve_in.outcome
    dispute.resolution_notes = resolve_in.notes
    dispute.resolved_at = datetime.utcnow()
    
    # Log admin action (todo)
    
    await db.commit()
    await db.refresh(dispute)
    return dispute
