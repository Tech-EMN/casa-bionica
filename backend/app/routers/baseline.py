"""Casa Biônica — GET /baseline/{home_id}."""

from fastapi import APIRouter, Query

from ..database import get_client
from ..services.ewma_engine import BaselineEngine

router = APIRouter(prefix="/baseline", tags=["baseline"])


@router.get("/{home_id}")
def get_baseline(
    home_id: str,
    window_days: int = Query(default=7, ge=1, le=90),
    alpha: float = Query(default=0.2, ge=0.0, le=1.0),
    threshold_sigma: float = Query(default=2.0, ge=0.0),
):
    """Calculate EWMA-smoothed baseline durations per room per weekday.

    Returns baseline data for the given home, grouped by room name and
    day of week, plus any anomalies detected in today's events.
    """
    client = get_client()
    engine = BaselineEngine(
        alpha=alpha,
        threshold_sigma=threshold_sigma,
        window_days=window_days,
    )
    return engine.calc_baseline(home_id, client)
