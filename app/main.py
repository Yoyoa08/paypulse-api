from dotenv import load_dotenv
load_dotenv()  

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
import app.models  
from app.routers import orders, webhooks  

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="PayPulse API", lifespan=lifespan)

app.include_router(orders.router)
app.include_router(webhooks.router)

@app.get("/")
async def root():
    return {"message": "PayPulse API is live!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "paypulse-api"}

#uvicorn app.main:app --reload

