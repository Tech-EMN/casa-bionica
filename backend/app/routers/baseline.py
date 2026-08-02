"""Casa Biônica — GET /baseline, POST /baseline/recalculate"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..schemas import BaselineResponse
from ..services.ewma_engine import EWMABaselineEngine

router = APIRouter(prefix="/baseline", tags=["baseline"])


@router.get("", response_model=BaselineResponse)
def get_baseline(
    sensor_id: str = Query(...),
    home_id: str = Query(default=None),
    db: Session = Depends(get_db),
):
    baseline = EWMABaselineEngine(db).get_baseline(sensor_id, home_id or settings.home_id)
    if baseline is None:
        raise HTTPException(status_code=404, detail="Not enough data")
    return baseline


@router.post("/recalculate", response_model=BaselineResponse)
def recalculate(
    sensor_id: str = Query(...),
    home_id: str = Query(default=None),
    db: Session = Depends(get_db),
):
    baseline = EWMABaselineEngine(db).calculate(sensor_id, home_id or settings.home_id)
    if baseline is None:
        raise HTTPException(status_code=422, detail="Not enough data (<10 events)")
    return baseline
