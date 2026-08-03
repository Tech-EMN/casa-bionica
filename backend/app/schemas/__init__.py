"""Casa Biônica — Pydantic schemas v2."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Ingest (payload do ESP32) ──────────────────────────
class EventCreate(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=64)
    home_id: str = Field(..., min_length=1, max_length=64)
    direction: str = Field(..., pattern="^(entry|exit)$")
    distance_mm: int = Field(..., ge=0, le=4000)
    event_timestamp: datetime


# ── Event Response ─────────────────────────────────────
class EventResponse(BaseModel):
    id: str
    device_id: str | None = None
    sensor_id: str | None = None
    home_id: str | None = None
    direction: str
    distance_mm: int
    passage_name: str | None = None
    passage_type: str | None = None
    event_timestamp: str
    created_at: str | None = None

    model_config = {"from_attributes": True}


# ── Status ─────────────────────────────────────────────
class DeviceStatus(BaseModel):
    sensor_id: str
    passage_name: str
    passage_type: str
    status: str


class HomeStatusResponse(BaseModel):
    home_id: str
    home_name: str
    elderly_name: str
    devices: list[DeviceStatus] = []
    last_event: EventResponse | None = None
    active_alerts: int = 0
    presence: str = "unknown"
    emergency_contacts: list[dict] = []


# ── Presence ───────────────────────────────────────────
class PresenceResponse(BaseModel):
    home_id: str
    presence: str  # "home" | "away" | "unknown"
    last_entrance_event: dict | None = None
