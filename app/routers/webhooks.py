import os
import stripe
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Order, OrderStatus

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    print(f"--> Received Stripe Event Type: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        session_dict = session.to_dict() if hasattr(session, "to_dict") else session
        metadata = session_dict.get("metadata", {})
        
        if hasattr(metadata, "get"):
            order_id = metadata.get("order_id")
        elif isinstance(metadata, dict):
            order_id = metadata.get("order_id")
        else:
            order_id = getattr(metadata, "order_id", None)

        print(f"--> Extracted Order ID from Metadata: {order_id}")

        if order_id:
            result = await db.execute(select(Order).filter(Order.id == order_id))
            db_order = result.scalars().first()

            if db_order:
                db_order.status = OrderStatus.COMPLETED
                db_order.provider_reference = getattr(session, "id", None)
                await db.commit()
                print(f"--> SUCCESS: Order {order_id} marked as COMPLETED!")
            else:
                print(f"--> WARNING: Order ID {order_id} found in webhook, but NOT in database!")
        else:
            print("--> WARNING: No order_id found in session metadata!")

    return {"status": "success"}