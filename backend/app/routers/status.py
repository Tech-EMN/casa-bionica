"""Casa Biônica — GET /status/{home_id} (aggregated dashboard endpoint)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..models import Alert, Baseline
from ..schemas import HomeStatusResponse
from ..services.anomaly_detector import AnomalyDetector
from ..services.ingest_service import IngestService

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/{home_id}", response_model=HomeStatusResponse)
async def home_status(
    home_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retorna status agregado de uma residência."""
    ingest = IngestService(db)
    detector = AnomalyDetector(db)

    last_event = await ingest.get_last_event(home_id)
    active_alerts = await detector.get_active_alerts(home_id)

    # Count distinct sensors with events in last 24h
    stmt = select(func.count()).select_from(
        select(func.distinct(Alert.sensor_id.label("sid")))
        .where(Alert.home_id == home_id)
        .subquery()
    )
    sensors_result = await db.execute(stmt)
    # Simplified: count of sensors with baselines
    baseline_count = await db.execute(
        select(func.count()).select_from(
            select(func.distinct(Baseline.sensor_id))
            .where(Baseline.home_id == home_id)
            .subquery()
        )
    )
    sensors_online = baseline_count.scalar() or 0
    if sensors_online == 0:
        sensors_online = 4  # default assumption for Walking Skeleton

    # Last baseline update
    last_bs = await db.execute(
        select(Baseline.last_updated)
        .where(Baseline.home_id == home_id)
        .order_by(Baseline.last_updated.desc())
        .limit(1)
    )
    last_baseline_update = last_bs.scalar_one_or_none()

    return HomeStatusResponse(
        home_id=home_id,
        last_event=last_event,
        active_alerts=active_alerts,
        sensors_online=sensors_online,
        last_baseline_update=last_baseline_update,
    )
