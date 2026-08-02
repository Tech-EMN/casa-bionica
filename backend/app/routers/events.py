"""Casa Biônica — GET /events"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
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
    db: Session = Depends(get_db),
):
    ingest = IngestService(db)
    return ingest.get_events(
        home_id=home_id or settings.home_id,
        sensor_id=sensor_id, from_ts=from_ts, to_ts=to_ts, limit=limit,
    )


@router.get("/last", response_model=CrossingEventResponse | None)
def get_last_event(home_id: str = Query(default=None), db: Session = Depends(get_db)):
    return IngestService(db).get_last_event(home_id or settings.home_id)
