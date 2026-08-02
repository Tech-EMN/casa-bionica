"""Casa Biônica — Status/alerts/baseline routers (PostgREST backend)."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from ..config import settings
from ..schemas import AlertResponse, AlertUpdate, BaselineResponse, HomeStatusResponse
from ..services.ingest_service import IngestService

# ── Baseline (stub — PostgREST query) ──
baseline_router = APIRouter(prefix="/baseline", tags=["baseline"])


@baseline_router.get("", response_model=BaselineResponse | None)
def get_baseline(sensor_id: str = Query(...), home_id: str = Query(default=None)):
    # Stub — baseline calculation requires SQLAlchemy for now
    raise HTTPException(status_code=501, detail="Baseline engine pending PostgREST migration")


@baseline_router.post("/recalculate")
def recalculate(sensor_id: str = Query(...), home_id: str = Query(default=None)):
    raise HTTPException(status_code=501, detail="Baseline engine pending PostgREST migration")


# ── Alerts (stub — PostgREST query) ──
alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])


@alerts_router.get("", response_model=list[AlertResponse])
def list_alerts(home_id: str = Query(default=None), active_only: bool = Query(default=True)):
    # Stub
    return []


@alerts_router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: UUID, update: AlertUpdate):
    raise HTTPException(status_code=501, detail="Alert engine pending PostgREST migration")


# ── Status ──
status_router = APIRouter(prefix="/status", tags=["status"])


@status_router.get("/{home_id}", response_model=HomeStatusResponse)
def home_status(home_id: str):
    try:
        ingest = IngestService()
        last = ingest.get_last_event(home_id)
        return HomeStatusResponse(
            home_id=home_id,
            last_event=last,
            active_alerts=[],
            sensors_online=4,
            last_baseline_update=None,
        )
    except Exception:
        return HomeStatusResponse(
            home_id=home_id, last_event=None, active_alerts=[],
            sensors_online=0, last_baseline_update=None,
        )
