"""Casa Biônica — FastAPI application entrypoint.

Walking Skeleton: sensor → gateway → MQTT → ingest → baseline → alerts → dashboard.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .middleware.error_handler import rfc9457_error_handler
from .middleware.trace_id import TraceIDMiddleware
from .mqtt.subscriber import mqtt_subscriber
from .routers import alerts, baseline, events, ingest, status

# ── Logging ────────────────────────────────────────────

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


# ── Lifespan ────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: launch MQTT subscriber as background task."""
    logger.info("Starting Casa Biônica backend")
    mqtt_task = asyncio.create_task(mqtt_subscriber())
    yield
    logger.info("Shutting down Casa Biônica backend")
    mqtt_task.cancel()
    try:
        await mqtt_task
    except asyncio.CancelledError:
        pass


# ── App ─────────────────────────────────────────────────

app = FastAPI(
    title="Casa Biônica",
    description="Sistema de monitoramento de idosos por sensores ToF",
    version="0.1.0-walking-skeleton",
    lifespan=lifespan,
    debug=(settings.app_env == "development"),
)

# Middleware
app.add_middleware(TraceIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(Exception, rfc9457_error_handler)

# Routers
app.include_router(ingest.router)
app.include_router(events.router)
app.include_router(baseline.router)
app.include_router(alerts.router)
app.include_router(status.router)


# ── Root ────────────────────────────────────────────────


@app.get("/")
async def root():
    return {
        "name": "Casa Biônica",
        "version": "0.1.0-walking-skeleton",
        "status": "running",
        "home_id": settings.home_id,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
