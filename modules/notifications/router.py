from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from core.database import get_db
from modules.notifications import models, schemas
from modules.auth.models import User
from modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

async def create_notification(db: AsyncSession, user_id: str, message: str, payload: dict = None):
    # This function is internal, called by other services
    notification = models.Notification(
        user_id=user_id,
        message=message,
        payload=payload
    )
    db.add(notification)
    # Commit handled by caller usually or here?
    # Better here if async task.
    await db.commit()
    await db.refresh(notification)
    return notification

@router.get("/", response_model=List[schemas.NotificationResponse])
async def list_messages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Notification)
        .where(models.Notification.user_id == current_user.id)
        .order_by(models.Notification.created_at.desc())
    )
    return result.scalars().all()
