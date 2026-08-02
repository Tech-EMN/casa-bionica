"""Casa Biônica — POST /ingest (recebe evento diretamente, bypass MQTT).

Usado para teste rápido e para o dashboard enviar eventos manualmente.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas import CrossingEventCreate, CrossingEventResponse
from ..services.anomaly_detector import AnomalyDetector
from ..services.ewma_engine import EWMABaselineEngine
from ..services.ingest_service import DuplicateEventError, IngestService

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=CrossingEventResponse, status_code=201)
async def ingest_event(
    payload: CrossingEventCreate,
    db: AsyncSession = Depends(get_db),
):
    """Recebe um evento de travessia do gateway.

    Pipeline: validate → dedup → store → baseline update → anomaly check.
    """
    ingest = IngestService(db)

    try:
        stored = await ingest.ingest(payload)
    except DuplicateEventError:
        raise HTTPException(status_code=409, detail="Duplicate event")

    # Baseline update (fire-and-forget)
    try:
        ewma = EWMABaselineEngine(db)
        await ewma.calculate(payload.sensor_id, payload.home_id)
    except Exception:
        pass  # Non-blocking

    # Anomaly check
    try:
        detector = AnomalyDetector(db)
        await detector.check(
            payload.sensor_id,
            payload.home_id,
            current_duration_seconds=0,  # Will be calculated from last event
        )
    except Exception:
        pass  # Non-blocking

    return stored
