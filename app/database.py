from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG,
    pool_size=5,          # Keeps 5 active connections ready
    max_overflow=10,      # Allows up to 10 extra connections during traffic spikes
    pool_timeout=30,      # Seconds to wait before giving up on a connection
    pool_pre_ping=True    # Automatically detects and drops broken/stale DB connections
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session