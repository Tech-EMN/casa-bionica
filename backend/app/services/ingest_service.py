"""Casa Biônica — IngestService (DEEP module).

Interface: ingest(raw_event: dict) → EventID
Depth: validate → normalize timestamp → dedup → store → queue baseline update
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import CrossingEvent
from ..schemas import CrossingEventCreate


class DuplicateEventError(ValueError):
    """Evento já existe (mesmo sensor_id + event_timestamp)."""


class IngestService:
    """Recebe evento bruto do gateway, valida, deduplica e persiste."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest(self, payload: CrossingEventCreate) -> CrossingEvent:
        """Processa e armazena um evento de travessia.

        Raises:
            DuplicateEventError: se o evento já existe.
        """
        # 1. Validate (Pydantic already did this via schema)
        # 2. Normalize timestamp to UTC
        ts_utc = payload.event_timestamp
        if ts_utc.tzinfo is None:
            ts_utc = ts_utc.replace(tzinfo=timezone.utc)

        # 3. Dedup: same sensor_id + exact same timestamp = duplicate
        existing = await self.db.execute(
            select(CrossingEvent).where(
                CrossingEvent.sensor_id == payload.sensor_id,
                CrossingEvent.event_timestamp == ts_utc,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise DuplicateEventError(
                f"Duplicate: sensor={payload.sensor_id} ts={ts_utc.isoformat()}"
            )

        # 4. Store
        event = CrossingEvent(
            sensor_id=payload.sensor_id,
            home_id=payload.home_id,
            direction=payload.direction,
            distance_mm=payload.distance_mm,
            event_timestamp=ts_utc,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        # 5. Baseline update is triggered separately by the caller
        #    (keeps IngestService single-responsibility)
        return event

    async def get_events(
        self,
        home_id: str,
        sensor_id: str | None = None,
        from_ts: datetime | None = None,
        to_ts: datetime | None = None,
        limit: int = 100,
    ) -> list[CrossingEvent]:
        """Query events with optional filters."""
        stmt = select(CrossingEvent).where(CrossingEvent.home_id == home_id)
        if sensor_id:
            stmt = stmt.where(CrossingEvent.sensor_id == sensor_id)
        if from_ts:
            stmt = stmt.where(CrossingEvent.event_timestamp >= from_ts)
        if to_ts:
            stmt = stmt.where(CrossingEvent.event_timestamp <= to_ts)
        stmt = stmt.order_by(CrossingEvent.event_timestamp.desc()).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_last_event(self, home_id: str) -> CrossingEvent | None:
        """Retorna o evento mais recente de uma residência."""
        stmt = (
            select(CrossingEvent)
            .where(CrossingEvent.home_id == home_id)
            .order_by(CrossingEvent.event_timestamp.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
