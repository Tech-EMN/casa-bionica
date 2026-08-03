"""Casa Biônica — IngestService v2 (schema: devices, events, passages)."""

from datetime import datetime, timezone
from uuid import uuid4

from ..database import get_client


class IngestService:
    def __init__(self):
        self.client = get_client()

    # ── Device lookup ──────────────────────────────────
    def _resolve_device(self, sensor_id: str) -> dict | None:
        resp = self.client.get(
            "/devices",
            params={
                "sensor_id": f"eq.{sensor_id}",
                "select": "id,home_id,home_id_text,passages(name,passage_type)",
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
            "home_id": r.get("home_id_text", r.get("home_id", "")),
            "passage_name": passage.get("name", "unknown"),
            "passage_type": passage.get("passage_type", "room"),
        }

    # ── Ingest ─────────────────────────────────────────
    def ingest(self, payload) -> dict:
        ts = payload.event_timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        device = self._resolve_device(payload.sensor_id)
        if device is None:
            raise ValueError(f"Device not found: {payload.sensor_id}")

        data = {
            "id": str(uuid4()),
            "device_id": device["device_id"],
            "direction": payload.direction,
            "distance_mm": payload.distance_mm,
            "event_timestamp": ts.isoformat(),
        }
        resp = self.client.post("/events", json=data,
            params={"select": "id,device_id,direction,distance_mm,event_timestamp,created_at"})
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
        # Step 1: Get device IDs for this home
        resp = self.client.get("/devices", params={
            "select": "id,sensor_id", "home_id_text": f"eq.{home_id}"})
        resp.raise_for_status()
        devices = resp.json()
        if not devices:
            return []
        device_map = {d["id"]: d["sensor_id"] for d in devices}
        device_ids = list(device_map.keys())
        if sensor_id:
            matching = [did for did, sid in device_map.items() if sid == sensor_id]
            if not matching:
                return []
            device_ids = matching

        # Step 2: Query events
        params = {
            "select": "id,device_id,direction,distance_mm,event_timestamp,created_at",
            "device_id": f"in.({','.join(device_ids)})",
            "order": "event_timestamp.desc",
            "limit": str(limit),
        }
        if from_ts:
            params["event_timestamp"] = f"gte.{from_ts.isoformat()}"
        resp = self.client.get("/events", params=params)
        resp.raise_for_status()
        rows = resp.json()

        # Step 3: Get passage names
        resp = self.client.get("/devices", params={
            "id": f"in.({','.join(device_ids)})",
            "select": "id,passages(name,passage_type)"})
        resp.raise_for_status()
        device_passages = {d["id"]: (d.get("passages") or {}) for d in resp.json()}

        result = []
        for r in rows:
            did = r["device_id"]
            passage = device_passages.get(did, {})
            result.append({
                "id": r["id"], "device_id": did,
                "direction": r["direction"], "distance_mm": r["distance_mm"],
                "event_timestamp": r["event_timestamp"], "created_at": r["created_at"],
                "sensor_id": device_map.get(did, "?"), "home_id": home_id,
                "passage_name": passage.get("name", "?"),
                "passage_type": passage.get("passage_type", "?"),
            })
        return result

    def get_last_event(self, home_id):
        events = self.get_events(home_id, limit=1)
        return events[0] if events else None

    # ── Presence (Q10=C) ───────────────────────────────
    def get_presence(self, home_id: str) -> dict:
        resp = self.client.get("/devices", params={
            "select": "id,sensor_id,passages!inner(passage_type)",
            "home_id_text": f"eq.{home_id}",
            "passages.passage_type": "eq.entrance"})
        resp.raise_for_status()
        entrance_devices = resp.json()
        if not entrance_devices:
            return {"home_id": home_id, "presence": "unknown", "last_entrance_event": None}

        device_ids = [d["id"] for d in entrance_devices]
        resp = self.client.get("/events", params={
            "select": "id,device_id,direction,event_timestamp",
            "device_id": f"in.({','.join(device_ids)})",
            "order": "event_timestamp.desc", "limit": "1"})
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
