"""Casa Biônica — AnomalyDetector (DEEP module, sync)."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Alert, Baseline
from .ewma_engine import EWMABaselineEngine


class AnomalyDetector:
    COOLDOWN_SECONDS = 1800

    def __init__(self, db: Session):
        self.db = db
        self.ewma = EWMABaselineEngine(db)

    def check(self, sensor_id: str, home_id: str, current_duration_seconds: float) -> Alert | None:
        baseline = self.ewma.get_baseline(sensor_id, home_id)
        if baseline is None:
            baseline = self.ewma.calculate(sensor_id, home_id)
        if baseline is None:
            return None

        threshold = baseline.ewma_mean_seconds + (EWMABaselineEngine.THRESHOLD_SIGMA * baseline.ewma_std_seconds)
        if current_duration_seconds <= threshold:
            return None

        cooldown_since = datetime.now(timezone.utc).timestamp() - self.COOLDOWN_SECONDS
        recent = self.db.execute(
            select(Alert).where(
                Alert.sensor_id == sensor_id,
                Alert.home_id == home_id,
                Alert.triggered_at >= datetime.fromtimestamp(cooldown_since, tz=timezone.utc),
            ).limit(1)
        ).scalar_one_or_none()
        if recent is not None:
            return None

        message = (
            f"Sensor {sensor_id} em anomalia: {current_duration_seconds:.0f}s "
            f"(baseline: {baseline.ewma_mean_seconds:.0f}s, threshold: {threshold:.0f}s)"
        )
        alert = Alert(
            home_id=home_id, sensor_id=sensor_id,
            current_duration_seconds=round(current_duration_seconds, 2),
            threshold_seconds=round(threshold, 2),
            baseline_mean_seconds=baseline.ewma_mean_seconds,
            message=message, triggered_at=datetime.now(timezone.utc),
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_active_alerts(self, home_id: str) -> list[Alert]:
        return list(self.db.execute(
            select(Alert).where(Alert.home_id == home_id, Alert.status.in_(["pending", "notified"]))
            .order_by(Alert.triggered_at.desc())
        ).scalars().all())

    def update_alert_status(self, alert_id: str, status: str) -> Alert | None:
        alert = self.db.execute(select(Alert).where(Alert.id == alert_id)).scalar_one_or_none()
        if alert is None:
            return None
        alert.status = status
        if status == "resolved":
            alert.resolved_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(alert)
        return alert
