"""Casa Biônica — POST /ingest"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import CrossingEventCreate, CrossingEventResponse
from ..services.ingest_service import DuplicateEventError, IngestService

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=CrossingEventResponse, status_code=201)
def ingest_event(payload: CrossingEventCreate, db: Session = Depends(get_db)):
    ingest = IngestService(db)
    try:
        return ingest.ingest(payload)
    except DuplicateEventError:
        raise HTTPException(status_code=409, detail="Duplicate event")
