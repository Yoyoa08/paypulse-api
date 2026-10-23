from fastapi import APIRouter

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/stripe")
async def stripe_webhook():
    return {"status": "received"}