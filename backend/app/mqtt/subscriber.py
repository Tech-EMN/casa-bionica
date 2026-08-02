"""Casa Biônica — MQTT subscriber (aiomqtt).

Listens on casa_bionica/events/# → IngestService.ingest() → EWMA update → Anomaly check.
"""

import asyncio
import json
import logging

import aiomqtt

from ..config import settings
from ..database import async_session
from ..schemas import CrossingEventCreate
from ..services.anomaly_detector import AnomalyDetector
from ..services.ewma_engine import EWMABaselineEngine
from ..services.ingest_service import DuplicateEventError, IngestService

logger = logging.getLogger(__name__)


async def mqtt_subscriber():
    """Main MQTT subscriber loop. Reconnects on failure."""
    while True:
        try:
            async with aiomqtt.Client(
                hostname=settings.mqtt_broker_host,
                port=settings.mqtt_broker_port,
            ) as client:
                topic = f"{settings.mqtt_topic_prefix}/events/#"
                await client.subscribe(topic)
                logger.info(f"MQTT subscribed to {topic}")

                async for message in client.messages:
                    try:
                        await handle_event(message.payload)
                    except Exception:
                        logger.exception("Error handling MQTT event")
        except aiomqtt.MqttError:
            logger.warning("MQTT disconnected. Reconnecting in 5s...")
            await asyncio.sleep(5)


async def handle_event(payload: bytes):
    """Process a single MQTT event: ingest → baseline → anomaly check."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON payload: {payload[:200]}")
        return

    try:
        event = CrossingEventCreate(**data)
    except Exception as e:
        logger.warning(f"Invalid event schema: {e}")
        return

    async with async_session() as db:
        ingest = IngestService(db)

        try:
            stored = await ingest.ingest(event)
            logger.info(
                f"Ingested: sensor={stored.sensor_id} dir={stored.direction} "
                f"distance={stored.distance_mm}mm"
            )
        except DuplicateEventError:
            logger.debug(f"Duplicate event, skipping: {event.sensor_id}")
            return
        except Exception:
            logger.exception("Ingest failed")
            return

        # Update baseline (fire-and-forget — failure doesn't block ingest)
        try:
            ewma = EWMABaselineEngine(db)
            await ewma.calculate(event.sensor_id, event.home_id)
        except Exception:
            logger.exception("Baseline update failed (non-blocking)")

        # Check for anomaly
        try:
            now = stored.created_at
            last_event = await ingest.get_last_event(event.home_id)
            if last_event and last_event.sensor_id == event.sensor_id:
                duration = (now - last_event.event_timestamp).total_seconds()
            else:
                duration = (now - stored.event_timestamp).total_seconds()

            if duration > 0:
                detector = AnomalyDetector(db)
                alert = await detector.check(
                    stored.sensor_id,
                    stored.home_id,
                    duration,
                )
                if alert:
                    logger.warning(f"ANOMALY: {alert.message}")
        except Exception:
            logger.exception("Anomaly check failed (non-blocking)")
