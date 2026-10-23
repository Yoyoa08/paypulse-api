from pydantic import BaseModel, EmailStr
from decimal import Decimal
from datetime import datetime

# What the client sends to create an order
class OrderCreate(BaseModel):
    amount: Decimal
    currency: str = "USD"
    email: EmailStr

# What the API returns back to the client
class OrderResponse(BaseModel):
    id: int
    reference: str
    amount: Decimal
    currency: str
    status: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True