from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.database import get_db
from api.modules.auth import models, schemas, service
from api.core.security import create_access_token, create_refresh_token
from api.modules.auth.dependencies import get_current_user
from api.core.log import logger

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.UserResponse)
async def register(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await service.get_user_by_email(db, user_in.email)
    if existing_user:
        logger.warn(f"Registration failed: Email already exists - {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await service.create_user(db, user_in)
    logger.track(f"New user registered: {user.email} [{user.role}]")
    return user

@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warn(f"Login failed: Incorrect credentials - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role.value}) # Include role in token
    refresh_token = create_refresh_token(data={"sub": user.email})
    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(request: schemas.RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = create_access_token.jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # Check if user exists
        user = await service.get_user_by_email(db, email)
        if not user:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
        new_refresh_token = create_refresh_token(data={"sub": user.email})
        return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
    except Exception: # generic catch for jose.JWTError but need import
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
