"""Casa Biônica — Admin PATCH endpoint (temporary, for data fixes)."""

from fastapi import APIRouter, HTTPException

from ..database import get_client

router = APIRouter(prefix="/admin", tags=["admin"])


@router.patch("/homes/{home_id}")
def update_home(home_id: str, payload: dict):
    """Update home fields (elderly_name, etc)."""
    client = get_client()
    resp = client.patch(
        "/homes",
        params={"home_id": f"eq.{home_id}"},
        json=payload,
    )
    if resp.status_code >= 400:
        raise HTTPException(resp.status_code, detail=resp.text)
    return resp.json()


@router.patch("/emergency-contacts/{home_id}")
def update_contacts(home_id: str, payload: dict):
    """Update emergency contact fields (phone, etc)."""
    client = get_client()
    resp = client.patch(
        "/emergency_contacts",
        params={"home_id_text": f"eq.{home_id}"},
        json=payload,
    )
    if resp.status_code >= 400:
        raise HTTPException(resp.status_code, detail=resp.text)
    return resp.json()
