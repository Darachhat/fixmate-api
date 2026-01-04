from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from modules.disputes import models, schemas, service
from modules.auth.models import User
from core.rbac import require_role
from shared.enums import UserRole
from core.log import logger

router = APIRouter(prefix="/disputes", tags=["Disputes"])

@router.post("/", response_model=schemas.DisputeResponse)
async def create_dispute_endpoint(
    dispute_in: schemas.DisputeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CUSTOMER, UserRole.TECHNICIAN))
):
    dispute = await service.create_dispute(db, current_user.id, dispute_in)
    logger.warn(f"Dispute opened for Job {dispute.job_id} by {current_user.email}")
    return dispute

@router.put("/{dispute_id}/resolve", response_model=schemas.DisputeResponse)
async def resolve_dispute_endpoint(
    dispute_id: str,
    resolve_in: schemas.DisputeResolve,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    dispute = await service.resolve_dispute(db, dispute_id, resolve_in, current_user.id)
    logger.track(f"Dispute {dispute_id} resolved as {resolve_in.outcome} by ADMIN {current_user.email}")
    return dispute
