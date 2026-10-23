from fastapi import FastAPI
from app.database import engine, Base
from app.models import Order  # Imports the model so SQLAlchemy registers it

app = FastAPI(title="PayPulse API")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # This creates your tables in PostgreSQL automatically
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "PayPulse API is live!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "paypulse-api"}