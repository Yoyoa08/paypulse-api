import os
import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Order, OrderStatus

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    
    payload = await request.body()

    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Missing stripe-signature header"
        )

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=STRIPE_WEBHOOK_SECRET
        )

    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id")

        result = await db.execute(select(Order).where(Order.provider_reference == session_id))

        db_order = result.scalar_one_or_none()

        if db_order and db_order.status != OrderStatus.COMPLETED:
            db_order.status = OrderStatus.COMPLETED
            await db.commit()
            await db.refresh(db_order)

    return {"status": "success"}