"""Casa Biônica — POST /ingest (PostgREST backend)."""

from fastapi import APIRouter, HTTPException
from httpx import HTTPError

from ..schemas import CrossingEventCreate, CrossingEventResponse
from ..services.ingest_service import IngestService

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=CrossingEventResponse, status_code=201)
def ingest_event(payload: CrossingEventCreate):
    try:
        result = IngestService().ingest(payload)
        return result
    except HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Supabase error: {e}")
