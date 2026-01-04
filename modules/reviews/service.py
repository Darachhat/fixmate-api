from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from modules.reviews import models, schemas
from modules.jobs import models as job_models
from modules.users import models as user_models
from shared.enums import JobStatus
from fastapi import HTTPException

async def create_review(db: AsyncSession, user_id: str, review_in: schemas.ReviewCreate):
    # Check if job exists
    result = await db.execute(select(job_models.Job).where(job_models.Job.id == review_in.job_id))
    job = result.scalars().first()
    
    if not job:
         raise HTTPException(status_code=404, detail="Job not found")
         
    if job.customer_id != user_id:
         raise HTTPException(status_code=403, detail="Not authorized to review this job")
         
    if job.status != JobStatus.COMPLETED:
         raise HTTPException(status_code=400, detail="Job must be completed to review")
         
    # Check existing review
    result = await db.execute(select(models.Review).where(models.Review.job_id == review_in.job_id))
    if result.scalars().first():
         raise HTTPException(status_code=400, detail="Review already exists")
         
    review = models.Review(
        job_id=job.id,
        reviewer_id=user_id,
        technician_id=job.technician_id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    db.add(review)
    
    # Update technician stats (Step 11 requirement)
    # Inefficient to query all reviews every time. Incremental update is better.
    # Or simplified:
    tech = await db.scalar(select(user_models.Technician).where(user_models.Technician.id == job.technician_id))
    if tech:
        new_total = tech.total_reviews + 1
        # tech.average_rating = ((tech.average_rating * tech.total_reviews) + review.rating) / new_total
        # Handle 0 case
        current_total_score = tech.average_rating * tech.total_reviews
        tech.average_rating = (current_total_score + review.rating) / new_total
        tech.total_reviews = new_total
        db.add(tech)

    await db.commit()
    await db.refresh(review)
    return review
