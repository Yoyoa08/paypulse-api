from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Order, OrderStatus
from app.schemas import OrderCreate, OrderResponse
from app.services.payment import create_stripe_checkout_session

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderCreate, db: AsyncSession = Depends(get_db)):
   
    db_order = Order(
        amount=order_in.amount,
        currency=order_in.currency,
        customer_email=order_in.email,
        status=OrderStatus.PENDING
    )

    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

@router.post("/{order_id}/checkout")
async def checkout_order(order_id: UUID, db: AsyncSession = Depends(get_db)):
    print(f"--> Incoming checkout request for Order ID: {order_id}")
    
    db_order = await db.get(Order, order_id)
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )

    try:
        session_data = await create_stripe_checkout_session(
            db=db,
            order_id=db_order.id,
            amount=db_order.amount,
            currency=db_order.currency,
            customer_email=db_order.customer_email
        )
        return session_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )