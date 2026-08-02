"""Casa Biônica — /alerts"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Alert
from ..schemas import AlertResponse, AlertUpdate
from ..services.anomaly_detector import AnomalyDetector

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    home_id: str = Query(default=None),
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    detector = AnomalyDetector(db)
    if active_only:
        return detector.get_active_alerts(home_id or settings.home_id)
    return list(db.execute(
        select(Alert).where(Alert.home_id == (home_id or settings.home_id))
        .order_by(Alert.triggered_at.desc()).limit(50)
    ).scalars().all())


@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: UUID, update: AlertUpdate, db: Session = Depends(get_db)):
    alert = AnomalyDetector(db).update_alert_status(str(alert_id), update.status)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
