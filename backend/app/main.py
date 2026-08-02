"""Casa Biônica — FastAPI app (sync)."""

import logging

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .middleware.error_handler import rfc9457_error_handler
from .middleware.trace_id import TraceIDMiddleware
from .routers import alerts, baseline, events, ingest, status

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Casa Biônica",
    description="Sistema de monitoramento de idosos por sensores ToF",
    version="0.1.1-psycopg2",
    debug=(settings.app_env == "development"),
)

app.add_middleware(TraceIDMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(Exception, rfc9457_error_handler)

app.include_router(ingest.router)
app.include_router(events.router)
app.include_router(baseline.router)
app.include_router(alerts.router)
app.include_router(status.router)


@app.get("/")
def root():
    return {"name": "Casa Biônica", "version": "0.1.1-psycopg2",
            "status": "running", "home_id": settings.home_id, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
