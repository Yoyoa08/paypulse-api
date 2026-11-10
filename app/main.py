from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import engine, Base
import app.models  
from app.routers import orders, webhooks  
from app.logger import logger


limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_startup", message="Initializing database connection & syncing tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("app_startup_complete", message="Database tables ready.")
    yield

app = FastAPI(title="PayPulse API", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(orders.router)
app.include_router(webhooks.router)

@app.get("/")
async def root():
    logger.info("root_endpoint_accessed")
    return {"message": "PayPulse API is live!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "paypulse-api"}