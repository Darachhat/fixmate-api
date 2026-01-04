from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin import models

async def log_admin_action(db: AsyncSession, user_id: str, action: str, details: str = ""):
    log = models.AuditLog(user_id=user_id, action=action, details=details)
    db.add(log)
    await db.commit()
