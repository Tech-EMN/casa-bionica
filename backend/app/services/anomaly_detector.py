"""Casa Biônica — AnomalyDetector (DEEP module).

Interface: check(sensor_id, current_duration) → Alert | None
Depth: load baseline → compare threshold → cooldown check → create alert
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Alert, Baseline, CrossingEvent
from .ewma_engine import EWMABaselineEngine


class AnomalyDetector:
    """Detecta anomalias de rotina comparando duração atual com baseline."""

    COOLDOWN_SECONDS = 1800  # 30 min — don't re-alert same sensor

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ewma = EWMABaselineEngine(db)

    async def check(
        self,
        sensor_id: str,
        home_id: str,
        current_duration_seconds: float,
    ) -> Alert | None:
        """Verifica se um sensor está em anomalia.

        Args:
            sensor_id: ID do sensor
            home_id: ID da residência
            current_duration_seconds: Tempo desde o último evento neste sensor

        Returns:
            Alert se anomalia detectada, None caso contrário.
        """
        # 1. Load or calculate baseline
        baseline = await self.ewma.get_baseline(sensor_id, home_id)
        if baseline is None:
            baseline = await self.ewma.calculate(sensor_id, home_id)
        if baseline is None:
            return None  # Not enough data for baseline

        # 2. Calculate threshold
        threshold = baseline.ewma_mean_seconds + (
            EWMABaselineEngine.THRESHOLD_SIGMA * baseline.ewma_std_seconds
        )

        # 3. Check if current duration exceeds threshold
        if current_duration_seconds <= threshold:
            return None

        # 4. Check cooldown: don't re-alert if same sensor was alerted < 30 min ago
        cooldown_since = datetime.now(timezone.utc).timestamp() - self.COOLDOWN_SECONDS
        recent_alert = await self.db.execute(
            select(Alert)
            .where(
                Alert.sensor_id == sensor_id,
                Alert.home_id == home_id,
                Alert.triggered_at.timestamp() >= cooldown_since,
            )
            .limit(1)
        )
        if recent_alert.scalar_one_or_none() is not None:
            return None

        # 5. Create alert
        message = (
            f"Sensor {sensor_id} em anomalia: "
            f"{current_duration_seconds:.0f}s no ambiente "
            f"(baseline: {baseline.ewma_mean_seconds:.0f}s ± "
            f"{baseline.ewma_std_seconds:.0f}s, threshold: {threshold:.0f}s)"
        )

        alert = Alert(
            home_id=home_id,
            sensor_id=sensor_id,
            current_duration_seconds=round(current_duration_seconds, 2),
            threshold_seconds=round(threshold, 2),
            baseline_mean_seconds=baseline.ewma_mean_seconds,
            message=message,
            triggered_at=datetime.now(timezone.utc),
        )
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        return alert

    async def get_active_alerts(self, home_id: str) -> list[Alert]:
        """Retorna alertas ativos (pending ou notified)."""
        stmt = (
            select(Alert)
            .where(
                Alert.home_id == home_id,
                Alert.status.in_(["pending", "notified"]),
            )
            .order_by(Alert.triggered_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_alert_status(self, alert_id: str, status: str) -> Alert | None:
        """Atualiza status de um alerta (acknowledged/resolved)."""
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self.db.execute(stmt)
        alert = result.scalar_one_or_none()
        if alert is None:
            return None

        alert.status = status
        if status == "resolved":
            alert.resolved_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert
