import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_email = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    provider_reference = Column(String, nullable=True, unique=True, index=True)
    
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )