import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from api.core.database import SessionLocal
from api.modules.jobs import models as job_models
from api.modules.users import models as user_models
from api.shared.enums import JobStatus, JobOfferStatus
from datetime import datetime, timedelta

async def run_matching_worker():
    while True:
        try:
            async with SessionLocal() as db:
                await process_matching(db)
        except Exception as e:
            print(f"Matching worker error: {e}")
        await asyncio.sleep(10) # Run every 10 seconds

async def process_matching(db: AsyncSession):
    # 1. Move REQUESTED to MATCHING
    stmt = select(job_models.Job).where(job_models.Job.status == JobStatus.REQUESTED)
    result = await db.execute(stmt)
    requested_jobs = result.scalars().all()
    
    for job in requested_jobs:
        job.status = JobStatus.MATCHING
        db.add(job)
    await db.commit()

    # 2. Process MATCHING jobs
    stmt = select(job_models.Job).where(job_models.Job.status == JobStatus.MATCHING)
    result = await db.execute(stmt)
    matching_jobs = result.scalars().all()

    for job in matching_jobs:
        # Check active offer
        stmt = select(job_models.JobOffer).where(
            job_models.JobOffer.job_id == job.id,
            job_models.JobOffer.status == JobOfferStatus.PENDING,
            job_models.JobOffer.expires_at > func.now()
        )
        result = await db.execute(stmt)
        active_offer = result.scalars().first()
        
        if active_offer:
            continue
        
        # Check if any expired offer exists and mark them?
        # Database query above already filters expires_at > now. 
        # But we should update status of expired ones to EXPIRED for record keeping?
        stmt = select(job_models.JobOffer).where(
            job_models.JobOffer.job_id == job.id,
            job_models.JobOffer.status == JobOfferStatus.PENDING,
            job_models.JobOffer.expires_at <= func.now()
        )
        result = await db.execute(stmt)
        expired_offers = result.scalars().all()
        for offer in expired_offers:
            offer.status = JobOfferStatus.EXPIRED
            db.add(offer)
        await db.commit()

        # Find next technician
        # Exclude those who rejected or expired
        stmt = select(job_models.JobOffer.technician_id).where(
            job_models.JobOffer.job_id == job.id
        )
        result = await db.execute(stmt)
        excluded_tech_ids = result.scalars().all()
        
        # Simple Logic: verified techs not in excluded, order by rating?
        query = select(user_models.Technician).where(
            user_models.Technician.is_verified == True
        )
        if excluded_tech_ids:
            query = query.where(user_models.Technician.id.not_in(excluded_tech_ids))
        
        # Order by rating descending
        query = query.order_by(user_models.Technician.average_rating.desc())
        
        result = await db.execute(query)
        next_tech = result.scalars().first()
        
        if next_tech:
            # Create Offer
            offer = job_models.JobOffer(
                job_id=job.id,
                technician_id=next_tech.id,
                status=JobOfferStatus.PENDING,
                expires_at=datetime.utcnow() + timedelta(minutes=5) # 5 min timeout
            )
            db.add(offer)
            await db.commit()
            print(f"Offer created for Job {job.id} to Tech {next_tech.id}")
        else:
            # No tech found. Log or notify?
            pass
