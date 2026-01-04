from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from api.core.database import get_db
from api.modules.services import models, schemas, service
from api.modules.auth.models import User
from api.core.rbac import require_role
from api.shared.enums import UserRole
from api.core.log import logger

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("/", response_model=List[schemas.ServiceResponse])
async def list_services(db: AsyncSession = Depends(get_db)):
    return await service.get_services(db, active_only=True)

@router.post("/", response_model=schemas.ServiceResponse)
async def create_service_endpoint(
    service_in: schemas.ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    srv = await service.create_service(db, service_in)
    logger.track(f"Service created: {srv.name} [{srv.id}] by ADMIN {current_user.email}")
    return srv

@router.put("/{service_id}", response_model=schemas.ServiceResponse)
async def update_service_endpoint(
    service_id: str,
    service_in: schemas.ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    srv = await service.update_service(db, service_id, service_in)
    logger.info(f"Service updated: {srv.name} [{srv.id}]")
    return srv

@router.delete("/{service_id}", response_model=schemas.ServiceResponse)
async def delete_service_endpoint(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    srv = await service.delete_service(db, service_id)
    logger.warn(f"Service deleted (soft): {srv.name} [{srv.id}] by ADMIN {current_user.email}")
    return srv
