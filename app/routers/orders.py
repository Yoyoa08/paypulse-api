import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Order
from app.schemas import OrderCreate, OrderResponse
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderResponse])
async def list_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    return orders

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):

    reference = f"PAY-{uuid.uuid4().hex[:10].upper()}"
    
    new_order = Order(
        reference=reference,
        amount=payload.amount,
        currency=payload.currency,
        email=payload.email,
        status="pending"
    )
    
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    
    return new_order