"""Casa Biônica — FastAPI app v2.1."""

import structlog
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .middleware.error_handler import rfc9457_error_handler
from .middleware.trace_id import TraceIDMiddleware
from .routers.events import presence_router, router as events_router
from .routers.ingest import router as ingest_router
from .routers.status import router as status_router
from .routers.baseline import router as baseline_router
from .routers.admin import router as admin_router

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

app = FastAPI(
    title="Casa Biônica",
    description="Monitoramento de idosos por sensores ToF — Schema v2",
    version="2.1.0",
    debug=(settings.app_env == "development"),
)

app.add_middleware(TraceIDMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(Exception, rfc9457_error_handler)

app.include_router(ingest_router)
app.include_router(events_router)
app.include_router(presence_router)
app.include_router(status_router)
app.include_router(baseline_router)
app.include_router(admin_router)

# Static files — dashboard v2
static_dir = Path(__file__).parent.parent / "static" / "v2"
if static_dir.exists():
    app.mount("/v2", StaticFiles(directory=str(static_dir), html=True), name="dashboard-v2")


@app.get("/")
def root():
    return {"name": "Casa Biônica", "version": "2.1.0",
            "status": "running", "home_id": settings.home_id, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
