"""Casa Biônica — IngestService v2 (schema: devices, events, passages)."""

from datetime import datetime, timezone
from uuid import uuid4

from ..database import get_client


class IngestService:
    def __init__(self):
        self.client = get_client()

    # ── Device lookup ──────────────────────────────────
    def _resolve_device(self, sensor_id: str) -> dict | None:
        """Resolve sensor_id → {id, home_id, passage_name, passage_type}."""
        resp = self.client.get(
            "/devices",
            params={
                "sensor_id": f"eq.{sensor_id}",
                "select": "id,home_id,passage_id,passages(name,passage_type)",
                "limit": "1",
            },
        )
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            return None
        r = rows[0]
        passage = r.get("passages", {}) or {}
        return {
            "device_id": r["id"],
            "home_id": r["home_id"],
            "passage_name": passage.get("name", "unknown"),
            "passage_type": passage.get("passage_type", "room"),
        }

    # ── Ingest ─────────────────────────────────────────
    def ingest(self, payload) -> dict:
        ts = payload.event_timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        # Resolve device
        device = self._resolve_device(payload.sensor_id)
        if device is None:
            *** ValueError(f"Device not found: {payload.sensor_id}")

        data = {
            "id": str(uuid4()),
            "device_id": device["device_id"],
            "direction": payload.direction,
            "distance_mm": payload.distance_mm,
            "event_timestamp": ts.isoformat(),
        }
        resp = self.client.post(
            "/events",
            json=data,
            params={"select": "id,device_id,direction,distance_mm,event_timestamp,created_at"},
        )
        resp.raise_for_status()
        result = resp.json()
        row = result[0] if isinstance(result, list) else result
        row["sensor_id"] = payload.sensor_id
        row["home_id"] = device["home_id"]
        row["passage_name"] = device["passage_name"]
        row["passage_type"] = device["passage_type"]
        return row

    # ── Query ──────────────────────────────────────────
    def get_events(self, home_id, sensor_id=None, from_ts=None, to_ts=None, limit=100):
        # Join devices to filter by home_id
        # PostgREST: /events?select=*,devices!inner(home_id)&devices.home_id=eq.X
        params = {
            "select": "id,device_id,direction,distance_mm,event_timestamp,created_at,"
                      "devices!inner(sensor_id,home_id,passages(name,passage_type))",
            "devices.home_id": f"eq.{home_id}",
            "order": "event_timestamp.desc",
            "limit": str(limit),
        }
        if sensor_id:
            params["devices.sensor_id"] = f"eq.{sensor_id}"
        if from_ts:
            params["event_timestamp"] = f"gte.{from_ts.isoformat()}"
        resp = self.client.get("/events", params=params)
        resp.raise_for_status()
        rows = resp.json()
        # Flatten nested structure
        result = []
        for r in rows:
            device = r.get("devices", {}) or {}
            passage = device.get("passages", {}) or {}
            result.append({
                "id": r["id"],
                "device_id": r["device_id"],
                "direction": r["direction"],
                "distance_mm": r["distance_mm"],
                "event_timestamp": r["event_timestamp"],
                "created_at": r["created_at"],
                "sensor_id": device.get("sensor_id", "?"),
                "home_id": device.get("home_id", "?"),
                "passage_name": passage.get("name", "?"),
                "passage_type": passage.get("passage_type", "?"),
            })
        return result

    def get_last_event(self, home_id):
        events = self.get_events(home_id, limit=1)
        return events[0] if events else None

    # ── Presence (Q10=C) ───────────────────────────────
    def get_presence(self, home_id: str) -> dict:
        """Determina se idoso está em casa baseado no último evento de entrada."""
        # Último evento de qualquer device de entrada
        resp = self.client.get(
            "/events",
            params={
                "select": "id,device_id,direction,event_timestamp,"
                          "devices!inner(sensor_id,home_id,passages!inner(passage_type))",
                "devices.home_id": f"eq.{home_id}",
                "devices.passages.passage_type": "eq.entrance",
                "order": "event_timestamp.desc",
                "limit": "1",
            },
        )
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            return {"home_id": home_id, "presence": "unknown", "last_entrance_event": None}

        last = rows[0]
        return {
            "home_id": home_id,
            "presence": "home" if last["direction"] == "entry" else "away",
            "last_entrance_event": {
                "direction": last["direction"],
                "timestamp": last["event_timestamp"],
            },
        }
