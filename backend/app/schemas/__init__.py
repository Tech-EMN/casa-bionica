"""Casa Biônica — Pydantic schemas (request/response)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── CrossingEvent ──────────────────────────────────────

class CrossingEventCreate(BaseModel):
    """Payload recebido do gateway via MQTT."""
    sensor_id: str = Field(..., min_length=1, max_length=64, examples=["sensor-quarto-01"])
    home_id: str = Field(..., min_length=1, max_length=64, examples=["home-001"])
    direction: str = Field(..., pattern="^(entry|exit)$", examples=["entry"])
    distance_mm: int = Field(..., ge=0, le=4000, examples=[1187])
    event_timestamp: datetime = Field(..., examples=["2026-08-02T14:00:00Z"])


class CrossingEventResponse(BaseModel):
    id: UUID
    sensor_id: str
    home_id: str
    direction: str
    distance_mm: int
    event_timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Baseline ───────────────────────────────────────────

class BaselineResponse(BaseModel):
    id: UUID
    sensor_id: str
    home_id: str
    hour_bucket: int
    ewma_mean_seconds: float
    ewma_std_seconds: float
    sample_count: int
    last_updated: datetime

    model_config = {"from_attributes": True}


# ── Alert ──────────────────────────────────────────────

class AlertResponse(BaseModel):
    id: UUID
    home_id: str
    sensor_id: str
    status: str
    current_duration_seconds: float
    threshold_seconds: float
    baseline_mean_seconds: float
    message: str | None
    triggered_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    status: str = Field(..., pattern="^(acknowledged|resolved)$")


# ── Status (aggregated) ────────────────────────────────

class HomeStatusResponse(BaseModel):
    home_id: str
    last_event: CrossingEventResponse | None
    active_alerts: list[AlertResponse]
    sensors_online: int
    last_baseline_update: datetime | None
