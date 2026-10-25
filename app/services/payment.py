import stripe
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Order, OrderStatus
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

async def create_stripe_checkout_session(
    db: AsyncSession, 
    order_id: str, 
    amount: Decimal, 
    currency: str, 
    customer_email: str
) -> dict:
   
    try:
        unit_amount_cents = int(amount * 100)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": currency.lower(),
                    "product_data": {
                        "name": f"PayPulse Order #{order_id}",
                    },
                    "unit_amount": unit_amount_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            customer_email=customer_email,
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
        )

        db_order = await db.get(Order, order_id)
        if db_order:
            db_order.provider_reference = checkout_session.id
            db_order.status = OrderStatus.PENDING
            await db.commit()
            await db.refresh(db_order)

        return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}

    except stripe.error.StripeError as e:
        raise ValueError(f"Stripe API Error: {str(e)}")