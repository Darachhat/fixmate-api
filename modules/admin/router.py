from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from modules.admin import models, schemas
from modules.auth.models import User
from core.rbac import require_role
from shared.enums import UserRole

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/logs", response_model=list[schemas.AuditLogResponse])
async def get_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    result = await db.execute(select(models.AuditLog).order_by(models.AuditLog.created_at.desc()))
    return result.scalars().all()
