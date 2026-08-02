"""Casa Biônica — GET /baseline, POST /baseline/recalculate."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..schemas import BaselineResponse
from ..services.ewma_engine import EWMABaselineEngine

router = APIRouter(prefix="/baseline", tags=["baseline"])


@router.get("", response_model=BaselineResponse | None)
async def get_baseline(
    sensor_id: str = Query(...),
    home_id: str = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Retorna o baseline atual de um sensor."""
    ewma = EWMABaselineEngine(db)
    baseline = await ewma.get_baseline(sensor_id, home_id or settings.home_id)
    if baseline is None:
        raise HTTPException(status_code=404, detail="Baseline not found (not enough data)")
    return baseline


@router.post("/recalculate", response_model=BaselineResponse)
async def recalculate_baseline(
    sensor_id: str = Query(...),
    home_id: str = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Força recálculo do baseline de um sensor."""
    ewma = EWMABaselineEngine(db)
    baseline = await ewma.calculate(sensor_id, home_id or settings.home_id)
    if baseline is None:
        raise HTTPException(
            status_code=422,
            detail="Not enough data (< 10 events in rolling window)",
        )
    return baseline
