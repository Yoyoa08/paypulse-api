import os
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Order

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


async def create_stripe_checkout_session(
    db: AsyncSession,
    order_id,
    amount: float,
    currency: str,
    customer_email: str
):
    """
    Creates a Stripe Checkout Session for the given order.
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            metadata={
                "order_id": str(order_id)
            },
            line_items=[
                {
                    "price_data": {
                        "currency": currency.lower(),
                        "product_data": {
                            "name": f"PayPulse Order #{order_id}",
                        },
                        
                        "unit_amount": int(float(amount) * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            customer_email=customer_email,
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
        )

        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }

    except stripe.error.StripeError as e:
        raise ValueError(f"Stripe API Error: {e.user_message}")