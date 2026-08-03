"""Casa Biônica — POST /ingest v2."""

from fastapi import APIRouter, HTTPException
from httpx import HTTPError

from ..schemas import EventCreate, EventResponse
from ..services.ingest_service import IngestService

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=EventResponse, status_code=201)
def ingest_event(payload: EventCreate):
    try:
        return IngestService().ingest(payload)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Supabase error: {e}")
