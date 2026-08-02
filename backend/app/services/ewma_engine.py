"""Casa Biônica — EWMABaselineEngine (DEEP module, sync).

Interface: calculate(sensor_id, window_hours) → Baseline
Depth: query window → EWMA math → upsert baseline row
alpha=0.2, threshold=2σ, window=7 days
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Baseline, CrossingEvent


class EWMABaselineEngine:
    ALPHA = 0.2
    THRESHOLD_SIGMA = 2.0
    WINDOW_DAYS = 7

    def __init__(self, db: Session):
        self.db = db

    def calculate(self, sensor_id: str, home_id: str) -> Baseline | None:
        now = datetime.now(timezone.utc)
        hour_bucket = now.hour
        since = now - timedelta(days=self.WINDOW_DAYS)

        rows = self.db.execute(
            select(CrossingEvent.event_timestamp)
            .where(
                CrossingEvent.sensor_id == sensor_id,
                CrossingEvent.home_id == home_id,
                CrossingEvent.event_timestamp >= since,
            )
            .order_by(CrossingEvent.event_timestamp.asc())
        ).all()

        timestamps = [r[0] for r in rows]
        if len(timestamps) < 10:
            return None

        durations = [min((timestamps[i] - timestamps[i-1]).total_seconds(), 43200)
                     for i in range(1, len(timestamps))]
        if not durations:
            return None

        ewma_mean = durations[0]
        ewma_var = 0.0
        for d in durations[1:]:
            ewma_mean = self.ALPHA * d + (1 - self.ALPHA) * ewma_mean
            diff = d - ewma_mean
            ewma_var = self.ALPHA * (diff**2) + (1 - self.ALPHA) * ewma_var

        ewma_std = ewma_var**0.5

        row = self.db.execute(
            select(Baseline).where(
                Baseline.sensor_id == sensor_id,
                Baseline.home_id == home_id,
                Baseline.hour_bucket == hour_bucket,
            )
        ).scalar_one_or_none()

        if row:
            row.ewma_mean_seconds = round(ewma_mean, 2)
            row.ewma_std_seconds = round(ewma_std, 2)
            row.sample_count = len(durations)
            row.last_updated = now
        else:
            row = Baseline(
                sensor_id=sensor_id, home_id=home_id, hour_bucket=hour_bucket,
                ewma_mean_seconds=round(ewma_mean, 2),
                ewma_std_seconds=round(ewma_std, 2),
                sample_count=len(durations), last_updated=now,
            )
            self.db.add(row)

        self.db.commit()
        self.db.refresh(row)
        return row

    def get_baseline(self, sensor_id: str, home_id: str) -> Baseline | None:
        now = datetime.now(timezone.utc)
        return self.db.execute(
            select(Baseline).where(
                Baseline.sensor_id == sensor_id,
                Baseline.home_id == home_id,
                Baseline.hour_bucket == now.hour,
            )
        ).scalar_one_or_none()
