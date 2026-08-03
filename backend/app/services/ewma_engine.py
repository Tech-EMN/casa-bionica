"""Casa Biônica — EWMA Baseline Engine.

Calculates duration baselines per room per weekday using
Exponentially Weighted Moving Average (EWMA) smoothing.
"""

import statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone

WEEKDAY_MAP = {
    0: "mon", 1: "tue", 2: "wed", 3: "thu",
    4: "fri", 5: "sat", 6: "sun",
}


class BaselineEngine:
    """EWMA baseline calculator for room occupancy durations.

    Queries events from PostgREST, pairs entry/exit events per sensor,
    computes mean/std duration per room per weekday, and applies
    EWMA smoothing.

    Attributes:
        alpha: EWMA smoothing factor (0–1). Higher = more weight to recent data.
        threshold_sigma: Number of standard deviations for anomaly detection.
        window_days: Lookback window in days for baseline calculation.
    """

    def __init__(self, alpha: float = 0.2, threshold_sigma: float = 2.0, window_days: int = 7):
        self.alpha = alpha
        self.threshold_sigma = threshold_sigma
        self.window_days = window_days

    # ── Duration calculation ──────────────────────────────────

    def _query_events(self, home_id: str, client, since: datetime) -> list[dict]:
        """Fetch events for the given home_id in the window [since, now].

        Uses direct home_id column on events; falls back to device-resolution
        if the REST endpoint returns 400 (no home_id column in the view).
        """
        resp = client.get("/events", params={
            "home_id": f"eq.{home_id}",
            "event_timestamp": f"gte.{since.isoformat()}",
            "order": "event_timestamp.asc",
            "limit": "5000",
        })
        if resp.status_code == 400:
            return self._query_events_via_devices(home_id, client, since)
        resp.raise_for_status()
        return resp.json()

    def _query_events_via_devices(self, home_id: str, client, since: datetime) -> list[dict]:
        """Fallback: resolve devices for home, then query events by device_id."""
        dev_resp = client.get("/devices", params={
            "select": "id,sensor_id,passages(name,passage_type)",
            "home_id_text": f"eq.{home_id}",
        })
        dev_resp.raise_for_status()
        devices = dev_resp.json()
        if not devices:
            return []

        device_map = {}
        for d in devices:
            passage = d.get("passages") or {}
            device_map[d["id"]] = {
                "sensor_id": d["sensor_id"],
                "passage_name": passage.get("name", "unknown"),
                "passage_type": passage.get("passage_type", "room"),
            }

        device_ids = list(device_map.keys())
        resp = client.get("/events", params={
            "select": "id,device_id,direction,distance_mm,event_timestamp,created_at",
            "device_id": f"in.({','.join(device_ids)})",
            "event_timestamp": f"gte.{since.isoformat()}",
            "order": "event_timestamp.asc",
            "limit": "5000",
        })
        resp.raise_for_status()
        rows = resp.json()

        # Enrich rows with sensor_id, home_id, passage_name, passage_type
        for r in rows:
            dev = device_map.get(r["device_id"], {})
            r["sensor_id"] = dev.get("sensor_id", "?")
            r["home_id"] = home_id
            r["passage_name"] = dev.get("passage_name", "?")
            r["passage_type"] = dev.get("passage_type", "?")
        return rows

    @staticmethod
    def _parse_timestamp(ts_str: str) -> datetime:
        """Parse ISO-format timestamp string to timezone-aware datetime."""
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)

    def _compute_durations(self, events: list[dict]) -> list[tuple[str, str, float]]:
        """Pair entry→exit events per sensor_id and return durations.

        Returns:
            List of (passage_name, weekday, duration_minutes) tuples.
        """
        sensors: dict[str, list[dict]] = defaultdict(list)
        for e in events:
            sid = e.get("sensor_id") or e.get("device_id", "?")
            sensors[sid].append(e)

        durations: list[tuple[str, str, float]] = []
        for _sid, sensor_events in sensors.items():
            entry_ts: datetime | None = None
            passage_name = "unknown"
            for e in sensor_events:
                passage_name = e.get("passage_name", "unknown")
                direction = e.get("direction", "")
                if direction == "entry":
                    try:
                        entry_ts = self._parse_timestamp(e["event_timestamp"])
                    except (KeyError, ValueError):
                        continue
                elif direction == "exit" and entry_ts is not None:
                    try:
                        exit_ts = self._parse_timestamp(e["event_timestamp"])
                        duration_min = (exit_ts - entry_ts).total_seconds() / 60.0
                        weekday = WEEKDAY_MAP[entry_ts.weekday()]
                        durations.append((passage_name, weekday, duration_min))
                    except (KeyError, ValueError):
                        pass
                    finally:
                        entry_ts = None
        return durations

    # ── Baseline calculation ──────────────────────────────────

    def calc_baseline(self, home_id: str, client) -> dict:
        """Calculate EWMA-smoothed baseline durations per room per weekday.

        Args:
            home_id: The home identifier (text, e.g. "home-001").
            client: An httpx.Client pointed at the Supabase REST API root.

        Returns:
            dict with keys home_id, window_days, rooms, anomalies_today.
        """
        now = datetime.now(timezone.utc)
        since = now - timedelta(days=self.window_days)

        events = self._query_events(home_id, client, since)
        if not events:
            return {
                "home_id": home_id,
                "window_days": self.window_days,
                "rooms": {},
                "anomalies_today": [],
            }

        durations = self._compute_durations(events)
        if not durations:
            return {
                "home_id": home_id,
                "window_days": self.window_days,
                "rooms": {},
                "anomalies_today": [],
            }

        # Group by (passage_name, weekday)
        grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
        for pname, wday, dur in durations:
            grouped[(pname, wday)].append(dur)

        # Compute mean, std, and EWMA baseline per group
        rooms: dict[str, dict[str, dict]] = defaultdict(dict)
        for (pname, wday), durs in grouped.items():
            mean_min = statistics.mean(durs)
            std_min = statistics.stdev(durs) if len(durs) > 1 else 0.0
            # EWMA smoothing: iteratively smooth across ordered samples
            baseline_min = durs[0]
            for d in durs[1:]:
                baseline_min = self.alpha * d + (1 - self.alpha) * baseline_min
            deviation = round(std_min / mean_min, 2) if mean_min > 0 else 0.0
            rooms[pname][wday] = {
                "real_min": round(mean_min, 1),
                "baseline_min": round(baseline_min, 1),
                "deviation": deviation,
            }

        # Detect anomalies for today
        anomalies_today = self._detect_today_anomalies(
            home_id, client, rooms, now,
        )

        return {
            "home_id": home_id,
            "window_days": self.window_days,
            "rooms": {k: dict(v) for k, v in rooms.items()},
            "anomalies_today": anomalies_today,
        }

    # ── Anomaly detection ─────────────────────────────────────

    def detect_anomaly(
        self,
        current_duration_min: float,
        baseline_mean: float,
        baseline_std: float,
    ) -> bool:
        """Check if a duration is anomalously high.

        Anomaly if current > baseline_mean + threshold_sigma * baseline_std.

        Args:
            current_duration_min: The current observed duration in minutes.
            baseline_mean: The EWMA-smoothed baseline mean for this room/weekday.
            baseline_std: The baseline standard deviation for this room/weekday.

        Returns:
            True if the duration is anomalously high.
        """
        threshold = baseline_mean + self.threshold_sigma * baseline_std
        return current_duration_min > threshold

    def _detect_today_anomalies(
        self, home_id: str, client, rooms: dict, now: datetime,
    ) -> list[dict]:
        """Detect anomalies in today's events against the computed baseline."""
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_weekday = WEEKDAY_MAP[now.weekday()]

        events_today = self._query_events(home_id, client, today_start)
        if not events_today:
            return []

        today_durations = self._compute_durations(events_today)
        if not today_durations:
            return []

        # Group today's durations by passage_name
        today_by_room: dict[str, list[float]] = defaultdict(list)
        for pname, _wday, dur in today_durations:
            today_by_room[pname].append(dur)

        anomalies = []
        for pname, durs in today_by_room.items():
            weekday_baseline = rooms.get(pname, {}).get(today_weekday)
            if not weekday_baseline:
                continue
            baseline_mean = weekday_baseline["baseline_min"]
            baseline_std = baseline_mean * weekday_baseline.get("deviation", 0)
            for dur in durs:
                if self.detect_anomaly(dur, baseline_mean, baseline_std):
                    anomalies.append({
                        "passage_name": pname,
                        "weekday": today_weekday,
                        "duration_min": round(dur, 1),
                        "baseline_min": baseline_mean,
                        "threshold": round(
                            baseline_mean + self.threshold_sigma * baseline_std, 1,
                        ),
                    })
        return anomalies
