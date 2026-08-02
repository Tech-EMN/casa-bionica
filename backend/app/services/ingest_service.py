"""Casa Biônica — IngestService (DEEP module, sync).

Interface: ingest(raw_event: dict) → EventID
Depth: validate → normalize → dedup → store → baseline update
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import CrossingEvent
from ..schemas import CrossingEventCreate


class DuplicateEventError(ValueError):
    """Evento já existe (mesmo sensor_id + event_timestamp)."""


class IngestService:
    """Recebe evento bruto do gateway, valida, deduplica e persiste."""

    def __init__(self, db: Session):
        self.db = db

    def ingest(self, payload: CrossingEventCreate) -> CrossingEvent:
        ts_utc = payload.event_timestamp
        if ts_utc.tzinfo is None:
            ts_utc = ts_utc.replace(tzinfo=timezone.utc)

        existing = self.db.execute(
            select(CrossingEvent).where(
                CrossingEvent.sensor_id == payload.sensor_id,
                CrossingEvent.event_timestamp == ts_utc,
            )
        ).scalar_one_or_none()

        if existing is not None:
            raise DuplicateEventError(
                f"Duplicate: sensor={payload.sensor_id} ts={ts_utc.isoformat()}"
            )

        event = CrossingEvent(
            sensor_id=payload.sensor_id,
            home_id=payload.home_id,
            direction=payload.direction,
            distance_mm=payload.distance_mm,
            event_timestamp=ts_utc,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_events(
        self,
        home_id: str,
        sensor_id: str | None = None,
        from_ts: datetime | None = None,
        to_ts: datetime | None = None,
        limit: int = 100,
    ) -> list[CrossingEvent]:
        stmt = select(CrossingEvent).where(CrossingEvent.home_id == home_id)
        if sensor_id:
            stmt = stmt.where(CrossingEvent.sensor_id == sensor_id)
        if from_ts:
            stmt = stmt.where(CrossingEvent.event_timestamp >= from_ts)
        if to_ts:
            stmt = stmt.where(CrossingEvent.event_timestamp <= to_ts)
        stmt = stmt.order_by(CrossingEvent.event_timestamp.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_last_event(self, home_id: str) -> CrossingEvent | None:
        return self.db.execute(
            select(CrossingEvent)
            .where(CrossingEvent.home_id == home_id)
            .order_by(CrossingEvent.event_timestamp.desc())
            .limit(1)
        ).scalar_one_or_none()
