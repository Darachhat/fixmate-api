from fastapi import FastAPI
from api.core.config import settings
from api.modules.auth.router import router as auth_router
from api.modules.users.router import router as users_router
from api.modules.services.router import router as services_router
from api.modules.jobs.router import router as jobs_router
from api.modules.reviews.router import router as reviews_router
from api.modules.disputes.router import router as disputes_router
from api.modules.notifications.router import router as notifications_router
from api.modules.admin.router import router as admin_router
from api.core.database import engine, Base
from contextlib import asynccontextmanager

from api.workers.matching import run_matching_worker
import asyncio
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start background worker
    worker_task = asyncio.create_task(run_matching_worker())
    
    yield
    
    # Cleanup
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

from api.core.log import logger
from fastapi import Request

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(services_router, prefix=settings.API_PREFIX)
app.include_router(jobs_router, prefix=settings.API_PREFIX)
app.include_router(reviews_router, prefix=settings.API_PREFIX)
app.include_router(disputes_router, prefix=settings.API_PREFIX)
app.include_router(notifications_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"message": "Welcome to FixMate API"}
