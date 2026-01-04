from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.modules.users import models, schemas
from fastapi import HTTPException, status

async def get_technician_by_user_id(db: AsyncSession, user_id: str):
    result = await db.execute(select(models.Technician).where(models.Technician.user_id == user_id))
    return result.scalars().first()

async def create_technician_profile(db: AsyncSession, user_id: str, tech_in: schemas.TechnicianCreate):
    # Check if exists
    existing = await get_technician_by_user_id(db, user_id)
    if existing:
         raise HTTPException(status_code=400, detail="Profile already exists")
    
    db_tech = models.Technician(
        user_id=user_id,
        **tech_in.model_dump()
    )
    db.add(db_tech)
    await db.commit()
    await db.refresh(db_tech)
    return db_tech

async def verify_technician(db: AsyncSession, technician_id: str):
    result = await db.execute(select(models.Technician).where(models.Technician.id == technician_id))
    tech = result.scalars().first()
    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found")
    tech.is_verified = True
    await db.commit()
    await db.refresh(tech)
    return tech
