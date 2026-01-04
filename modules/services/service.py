from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.modules.services import models, schemas
from fastapi import HTTPException

async def get_services(db: AsyncSession, active_only: bool = True):
    query = select(models.Service)
    if active_only:
        query = query.where(models.Service.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()

async def get_service(db: AsyncSession, service_id: str):
    result = await db.execute(select(models.Service).where(models.Service.id == service_id))
    return result.scalars().first()

async def create_service(db: AsyncSession, service_in: schemas.ServiceCreate):
    db_service = models.Service(**service_in.model_dump())
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service

async def update_service(db: AsyncSession, service_id: str, service_in: schemas.ServiceUpdate):
    db_service = await get_service(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    update_data = service_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_service, key, value)
    
    await db.commit()
    await db.refresh(db_service)
    return db_service

async def delete_service(db: AsyncSession, service_id: str):
    db_service = await get_service(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db_service.is_active = False # Soft delete
    await db.commit()
    await db.refresh(db_service)
    return db_service
