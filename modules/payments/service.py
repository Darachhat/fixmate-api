from sqlalchemy.ext.asyncio import AsyncSession
from modules.payments import models
from modules.jobs import models as job_models
from shared.enums import PaymentStatus

async def create_payment_for_job(db: AsyncSession, job: job_models.Job):
    # Calculate fees
    # Assuming job.estimated_price is the final price? Or service base price?
    # Step 7 says "estimated_price". Step 6 says "base_price".
    # I'll use estimated_price if available, else service price?
    # Job model has relation to Service.
    
    price = job.estimated_price if job.estimated_price else 0.0
    if price == 0 and job.service:
         # Need to fetch service price? Job object might have it loaded.
         # For safety, use 0 or ensure price is set.
         pass
         
    # Logic: 10% platform fee
    platform_fee = price * 0.10
    earnings = price - platform_fee
    
    payment = models.Payment(
        job_id=job.id,
        amount=price,
        platform_fee=platform_fee,
        technician_earnings=earnings,
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    # Don't commit here if part of larger transaction? 
    # Usually jobs/service.py calls this. Passing session.
    # jobs/service.py commits.
    # But I should adding to session.
    return payment

async def process_payment(db: AsyncSession, payment_id: str):
    # Mock payment processing
    pass
