from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.reviews import models, schemas, service
from modules.auth.models import User
from core.rbac import require_role
from shared.enums import UserRole

from core.log import logger

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=schemas.ReviewResponse)
async def create_review_endpoint(
    review_in: schemas.ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CUSTOMER))
):
    review = await service.create_review(db, current_user.id, review_in)
    logger.track(f"Review created for Job {review.job_id} by {current_user.email}")
    return review
