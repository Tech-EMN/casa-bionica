"""Casa Biônica — EWMABaselineEngine (DEEP module).

Interface: calculate(sensor_id, window_hours) → Baseline(mean, std, threshold)
Depth: query window → EWMA math → upsert baseline row
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Baseline, CrossingEvent


class EWMABaselineEngine:
    """Calcula baseline EWMA por sensor + faixa horária.

    alpha=0.2 dá mais peso a observações recentes (decai ~50% em 3 dias).
    threshold = 2σ captura ~95% do intervalo de confiança.
    """

    ALPHA = 0.2  # EWMA smoothing factor
    THRESHOLD_SIGMA = 2.0  # anomalies > mean + 2*std
    WINDOW_DAYS = 7  # Rolling window for baseline calculation

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate(self, sensor_id: str, home_id: str) -> Baseline | None:
        """Calcula ou atualiza o baseline para um sensor específico.

        Returns None se não houver dados suficientes (< 10 eventos).
        """
        now = datetime.now(timezone.utc)
        hour_bucket = now.hour
        since = now - timedelta(days=self.WINDOW_DAYS)

        # Query events for this sensor in the rolling window
        stmt = (
            select(CrossingEvent.event_timestamp)
            .where(
                CrossingEvent.sensor_id == sensor_id,
                CrossingEvent.home_id == home_id,
                CrossingEvent.event_timestamp >= since,
            )
            .order_by(CrossingEvent.event_timestamp.asc())
        )
        result = await self.db.execute(stmt)
        timestamps = [row[0] for row in result.all()]

        if len(timestamps) < 10:
            return None  # Not enough data

        # Calculate inter-event durations in seconds
        durations = []
        for i in range(1, len(timestamps)):
            delta = (timestamps[i] - timestamps[i - 1]).total_seconds()
            # Cap at 12 hours (sleep) to avoid skewing baseline
            durations.append(min(delta, 43200))

        if not durations:
            return None

        # EWMA: exponentially weighted mean and std
        ewma_mean = durations[0]
        ewma_var = 0.0
        for d in durations[1:]:
            ewma_mean = self.ALPHA * d + (1 - self.ALPHA) * ewma_mean
            diff = d - ewma_mean
            ewma_var = self.ALPHA * (diff**2) + (1 - self.ALPHA) * ewma_var

        ewma_std = ewma_var**0.5

        # Upsert baseline row
        existing = await self.db.execute(
            select(Baseline).where(
                Baseline.sensor_id == sensor_id,
                Baseline.home_id == home_id,
                Baseline.hour_bucket == hour_bucket,
            )
        )
        row = existing.scalar_one_or_none()

        if row:
            row.ewma_mean_seconds = round(ewma_mean, 2)
            row.ewma_std_seconds = round(ewma_std, 2)
            row.sample_count = len(durations)
            row.last_updated = now
        else:
            row = Baseline(
                sensor_id=sensor_id,
                home_id=home_id,
                hour_bucket=hour_bucket,
                ewma_mean_seconds=round(ewma_mean, 2),
                ewma_std_seconds=round(ewma_std, 2),
                sample_count=len(durations),
                last_updated=now,
            )
            self.db.add(row)

        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def get_baseline(
        self, sensor_id: str, home_id: str
    ) -> Baseline | None:
        """Retorna o baseline atual para um sensor."""
        now = datetime.now(timezone.utc)
        stmt = select(Baseline).where(
            Baseline.sensor_id == sensor_id,
            Baseline.home_id == home_id,
            Baseline.hour_bucket == now.hour,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
