# PayPulse API 🚀

> A production-grade, asynchronous e-commerce payment backend built with FastAPI, PostgreSQL, and Stripe. Designed with strict data integrity, idempotent webhook processing, and structured JSON logging.

---

## 🛠️ Core Architecture & Tech Stack

- **Framework:** FastAPI (ASGI, asynchronous Python)
- **Database & ORM:** PostgreSQL with SQLAlchemy (`asyncpg` async driver)
- **Payment Gateway:** Stripe Checkout & Webhooks (Signature Verification)
- **Logging:** `structlog` (JSON-rendered structured logging)
- **Security & Reliability:** SlowAPI (IP-based rate limiting) & Idempotent Webhook tracking

---

## ✨ Key Features & Engineering Highlights

- **100% Asynchronous Pipeline:** Leverages non-blocking I/O (`async def`) and connection pooling to handle concurrent client requests without thread-blocking bottlenecks.
- **Idempotent Webhook Architecture:** Implements a dedicated `ProcessedWebhookEvent` tracking table to safely handle Stripe retry attempts and prevent duplicate event processing.
- **Database Lifespan Management:** Uses modern FastAPI `asynccontextmanager` lifespans to automatically sync SQLAlchemy models and manage database connection states cleanly on startup and shutdown.
- **Secure Payment Sessions:** Integrates Stripe Checkout API with secure metadata mapping (`order_id`) to tie gateway transactions back to internal database records.
- **Production Observability:** Replaces native `print()` debugging with structured JSON logs (`structlog`) for seamless integration with cloud log monitors.

---

## 📂 Project Structure

```text
paypulse-api/
├── app/
│   ├── core/
│   │   ├── config.py         # Environment and settings management
│   │   └── logger.py         # Structlog JSON configuration
│   ├── models/
│   │   └── database.py       # SQLAlchemy async models (Order, ProcessedWebhookEvent)
│   ├── routers/
│   │   ├── checkout.py       # Stripe checkout session endpoints
│   │   └── webhooks.py       # Verified Stripe webhook listeners & idempotency logic
│   ├── database.py           # Async engine and session factory
│   └── main.py               # FastAPI app, lifespan, and rate limiter setup
├── .env.example              # Environment variables template
├── requirements.txt          # Project dependencies
└── README.md