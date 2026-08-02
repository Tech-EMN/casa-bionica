"""Casa Biônica — GET /alerts, PATCH /alerts/{id}."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..schemas import AlertResponse, AlertUpdate
from ..services.anomaly_detector import AnomalyDetector

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    home_id: str = Query(default=None),
    active_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
):
    """Lista alertas. Por padrão, apenas ativos."""
    detector = AnomalyDetector(db)
    if active_only:
        return await detector.get_active_alerts(home_id or settings.home_id)

    # All alerts (simplified — in production, add pagination)
    from sqlalchemy import select
    from ..models import Alert

    stmt = (
        select(Alert)
        .where(Alert.home_id == (home_id or settings.home_id))
        .order_by(Alert.triggered_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    update: AlertUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Atualiza status de um alerta (acknowledged/resolved)."""
    detector = AnomalyDetector(db)
    alert = await detector.update_alert_status(str(alert_id), update.status)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
