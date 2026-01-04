from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.config import settings
from api.core.database import get_db
from api.modules.auth import models, schemas
from api.core.exceptions import CredentialsException, NotFoundException, PermissionDeniedException # PermissionDeniedException for rbac later
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise CredentialsException()
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise CredentialsException()
    
    result = await db.execute(select(models.User).where(models.User.email == token_data.email))
    user = result.scalars().first()
    
    if user is None:
        raise CredentialsException()
    return user
