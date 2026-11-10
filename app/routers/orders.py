from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models import Order, OrderStatus
from app.schemas import OrderCreate, OrderResponse
from app.services.payment import create_stripe_checkout_session
from app.logger import logger

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_order(request: Request, order_in: OrderCreate, db: AsyncSession = Depends(get_db)):
    logger.info("creating_order_request", email=order_in.email, amount=order_in.amount)
    
    db_order = Order(
        amount=order_in.amount,
        currency=order_in.currency,
        customer_email=order_in.email,
        status=OrderStatus.PENDING
    )

    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    
    logger.info("order_created_successfully", order_id=str(db_order.id))
    return db_order

@router.post("/{order_id}/checkout")
@limiter.limit("5/minute")
async def checkout_order(request: Request, order_id: UUID, db: AsyncSession = Depends(get_db)):
    logger.info("incoming_checkout_request", order_id=str(order_id))
    
    db_order = await db.get(Order, order_id)
     
    if not db_order:
        logger.warning("order_not_found_for_checkout", order_id=str(order_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    try:
        session_data = await create_stripe_checkout_session(
            db=db,
            order_id=db_order.id,
            amount=db_order.amount,
            currency=db_order.currency,
            customer_email=db_order.customer_email
        )
        logger.info("checkout_session_created", order_id=str(order_id))
        return session_data

    except ValueError as e:
        logger.error("checkout_failed", error=str(e), order_id=str(order_id))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))