"""Casa Biônica — GET /status/{home_id} v2."""

from fastapi import APIRouter

from ..database import get_client
from ..schemas import DeviceStatus, HomeStatusResponse
from ..services.ingest_service import IngestService

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/{home_id}", response_model=HomeStatusResponse)
def home_status(home_id: str):
    client = get_client()

    # Home info — query by home_id (text field, not UUID)
    resp = client.get("/homes", params={"home_id": f"eq.{home_id}", "limit": "1"})
    resp.raise_for_status()
    homes = resp.json()
    if not homes:
        return HomeStatusResponse(home_id=home_id, home_name="unknown", elderly_name="unknown")

    home = homes[0]

    # Devices — use home_id_text (text field, not UUID)
    resp = client.get(
        "/devices",
        params={
            "home_id_text": f"eq.{home_id}",
            "select": "sensor_id,status,passages(name,passage_type)",
        },
    )
    resp.raise_for_status()
    devices = [
        DeviceStatus(
            sensor_id=d["sensor_id"],
            passage_name=d.get("passages", {}).get("name", "?"),
            passage_type=d.get("passages", {}).get("passage_type", "?"),
            status=d["status"],
        )
        for d in resp.json()
    ]

    # Last event
    ingest = IngestService()
    last_event = ingest.get_last_event(home_id)

    # Presence
    presence = ingest.get_presence(home_id)

    # Alerts
    resp = client.get(
        "/alerts",
        params={
            "home_id_text": f"eq.{home_id}",
            "status": "in.(pending,notified)",
            "limit": "50",
        },
    )
    resp.raise_for_status()
    active_alerts = len(resp.json())

    # Emergency contacts
    resp = client.get(
        "/emergency_contacts",
        params={"home_id_text": f"eq.{home_id}", "order": "priority.asc"},
    )
    resp.raise_for_status()
    contacts = resp.json()

    return HomeStatusResponse(
        home_id=home_id,
        home_name=home["name"],
        elderly_name=home.get("elderly_name", ""),
        devices=devices,
        last_event=last_event,
        active_alerts=active_alerts,
        presence=presence["presence"],
        emergency_contacts=contacts,
    )
