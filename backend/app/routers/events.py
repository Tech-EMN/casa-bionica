"""Casa Biônica — GET /events (PostgREST backend)."""

from datetime import datetime

from fastapi import APIRouter, Query
from httpx import HTTPError

from ..config import settings
from ..schemas import CrossingEventResponse
from ..services.ingest_service import IngestService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[CrossingEventResponse])
def list_events(
    home_id: str = Query(default=None),
    sensor_id: str | None = Query(default=None),
    from_ts: datetime | None = Query(default=None, alias="from"),
    to_ts: datetime | None = Query(default=None, alias="to"),
    limit: int = Query(default=100, le=1000),
):
    try:
        return IngestService().get_events(
            home_id=home_id or settings.home_id,
            sensor_id=sensor_id, from_ts=from_ts, to_ts=to_ts, limit=limit,
        )
    except HTTPError as e:
        return []


@router.get("/last", response_model=CrossingEventResponse | None)
def get_last_event(home_id: str = Query(default=None)):
    try:
        return IngestService().get_last_event(home_id or settings.home_id)
    except HTTPError:
        return None
