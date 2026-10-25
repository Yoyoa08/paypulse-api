from pydantic import BaseModel, EmailStr
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from app.models import OrderStatus

class OrderCreate(BaseModel):
    amount: Decimal
    currency: str = "USD"
    email: EmailStr


class OrderResponse(BaseModel):
    id: UUID
    provider_reference: str | None = None
    amount: Decimal
    currency: str
    status: OrderStatus
    customer_email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

        