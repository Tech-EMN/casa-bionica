"""Casa Biônica — SQLAlchemy ORM models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def utcnow():
    return datetime.now(timezone.utc)


class CrossingEvent(Base):
    """Evento de travessia detectado por um sensor."""

    __tablename__ = "crossing_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sensor_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    home_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # "entry" | "exit"
    distance_mm: Mapped[int] = mapped_column(Integer, nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return (
            f"<CrossingEvent sensor={self.sensor_id} dir={self.direction} "
            f"ts={self.event_timestamp.isoformat()}>"
        )


class Baseline(Base):
    """Baseline EWMA por sensor_id + faixa horária."""

    __tablename__ = "baselines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sensor_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    home_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    hour_bucket: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-23
    ewma_mean_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    ewma_std_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=utcnow
    )

    __table_args__ = (
        # One baseline row per sensor per hour bucket per home
        {"comment": "EWMA baseline: one row per sensor + hour bucket"},
    )


class Alert(Base):
    """Alerta de anomalia de rotina."""

    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    home_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    sensor_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="pending", nullable=False
    )  # pending | notified | acknowledged | resolved
    current_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_mean_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True, nullable=False
    )
    resolved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
