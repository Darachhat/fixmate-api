from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.modules.auth import models, schemas
from api.core.security import get_password_hash, verify_password
from api.shared.enums import UserRole

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    # Technician registers as PENDING implicitly? Plan says "Technician registers as PENDING".
    # But UserRole is TECHNICIAN.
    # Step 5 mentions "Technician cannot be matched unless verified".
    # User model doesn't have verified status, Technician profile does.
    # So User is created, Technician profile comes later?
    # Or "Technician registers as PENDING" refers to some status?
    # The plan for Step 3 says "Technician registers as PENDING".
    # Wait, Step 5 "Technician apply".
    # Maybe Step 3 just creates the User account.
    # And default behavior for Technician role?
    # I'll stick to simple User creation here.
    
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
