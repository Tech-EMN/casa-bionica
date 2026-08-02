"""Casa Biônica — FastAPI app (PostgREST backend v0.2.0)."""

import logging

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .middleware.error_handler import rfc9457_error_handler
from .middleware.trace_id import TraceIDMiddleware
from .routers.events import router as events_router
from .routers.ingest import router as ingest_router
from .routers.status import alerts_router, baseline_router, status_router

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
    description="Sistema de monitoramento de idosos — PostgREST backend v0.2",
    version="0.2.0-postgrest",
    debug=(settings.app_env == "development"),
)

app.add_middleware(TraceIDMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(Exception, rfc9457_error_handler)

app.include_router(ingest_router)
app.include_router(events_router)
app.include_router(baseline_router)
app.include_router(alerts_router)
app.include_router(status_router)


@app.get("/")
def root():
    return {"name": "Casa Biônica", "version": "0.2.0-postgrest",
            "status": "running", "home_id": settings.home_id, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
