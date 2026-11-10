import stripe
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Order, OrderStatus, ProcessedWebhookEvent
from app.config import settings 

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # Use settings instead of raw os.getenv
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        print(f"--> Webhook Error (Invalid payload): {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print(f"--> Webhook Error (Invalid signature): {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_id = event["id"]
    print(f"--> Received Stripe Event Type: {event['type']} (ID: {event_id})")

    # --- Idempotency Check ---
    event_result = await db.execute(select(ProcessedWebhookEvent).filter(ProcessedWebhookEvent.event_id == event_id))
    if event_result.scalars().first():
        print(f"--> INFO: Event {event_id} already processed. Returning 200 OK.")
        return {"status": "success"}

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
                print(f"--> SUCCESS: Order {order_id} marked as COMPLETED!")
            else:
                print(f"--> WARNING: Order ID {order_id} found in webhook, but NOT in database!")
        else:
            print("--> WARNING: No order_id found in session metadata!")

    # Record the event as processed so retries return 200 OK cleanly
    db.add(ProcessedWebhookEvent(event_id=event_id))
    await db.commit()

    return {"status": "success"}