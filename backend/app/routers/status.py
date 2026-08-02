"""Casa Biônica — GET /status/{home_id}"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Baseline
from ..schemas import HomeStatusResponse
from ..services.anomaly_detector import AnomalyDetector
from ..services.ingest_service import IngestService

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/{home_id}", response_model=HomeStatusResponse)
def home_status(home_id: str, db: Session = Depends(get_db)):
    ingest = IngestService(db)
    detector = AnomalyDetector(db)

    last_event = ingest.get_last_event(home_id)
    active_alerts = detector.get_active_alerts(home_id)

    result = db.execute(
        select(func.count()).select_from(
            select(func.distinct(Baseline.sensor_id))
            .where(Baseline.home_id == home_id).subquery()
        )
    )
    sensors_online = result.scalar() or 4

    last_bs = db.execute(
        select(Baseline.last_updated)
        .where(Baseline.home_id == home_id)
        .order_by(Baseline.last_updated.desc()).limit(1)
    ).scalar_one_or_none()

    return HomeStatusResponse(
        home_id=home_id, last_event=last_event, active_alerts=active_alerts,
        sensors_online=sensors_online, last_baseline_update=last_bs,
    )
