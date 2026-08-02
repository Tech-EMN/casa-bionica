"""Casa Biônica — IngestService via Supabase PostgREST."""

from datetime import datetime, timezone
from uuid import uuid4

from ..database import get_client, get_headers


class IngestService:
    def __init__(self):
        self.client = get_client()

    def ingest(self, payload) -> dict:
        ts = payload.event_timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        data = {
            "id": str(uuid4()),
            "sensor_id": payload.sensor_id,
            "home_id": payload.home_id,
            "direction": payload.direction,
            "distance_mm": payload.distance_mm,
            "event_timestamp": ts.isoformat(),
        }
        resp = self.client.post("/crossing_events", json=data)
        resp.raise_for_status()
        result = resp.json()
        return result[0] if isinstance(result, list) else result

    def get_events(self, home_id, sensor_id=None, from_ts=None, to_ts=None, limit=100):
        params = {
            "home_id": f"eq.{home_id}",
            "order": "event_timestamp.desc",
            "limit": str(limit),
        }
        if sensor_id:
            params["sensor_id"] = f"eq.{sensor_id}"
        if from_ts:
            params["event_timestamp"] = f"gte.{from_ts.isoformat()}"
        if to_ts:
            params["event_timestamp"] = params.get("event_timestamp", "") + f",lte.{to_ts.isoformat()}"
        resp = self.client.get("/crossing_events", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_last_event(self, home_id):
        params = {"home_id": f"eq.{home_id}", "order": "event_timestamp.desc", "limit": "1"}
        resp = self.client.get("/crossing_events", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data[0] if data else None
