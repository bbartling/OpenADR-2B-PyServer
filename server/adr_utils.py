import asyncio
from functools import partial
from datetime import datetime, timezone, timedelta
import logging
from aiohttp import web
from ven_registry import VenRegistry, UnknownVenError, DuplicateVenError

# Define VEN registry variable to be set later
VEN_REGISTRY = None

# Set up logging
logger = logging.getLogger('openleadr')
logger.setLevel(logging.INFO)

def set_ven_registry(ven_registry):
    global VEN_REGISTRY
    VEN_REGISTRY = ven_registry

async def on_create_party_registration(registration_info):
    ven_name = registration_info["ven_name"]
    try:
        ven_info = VEN_REGISTRY.get_ven_info_from_name(ven_name)
        return (ven_info.ven_id, ven_info.registration_id)
    except UnknownVenError:
        logger.warning(f"An unknown VEN tried to connect: {ven_name}")
    return False

async def on_cancel_party_registration(payload):
    ven_id = payload['ven_id']
    try:
        ven_info = VEN_REGISTRY.get_ven_info_from_id(ven_id)
        VEN_REGISTRY.remove_ven(ven_info.ven_name)
        logger.info(f"VEN {ven_info.ven_name} with ID {ven_id} has been deregistered.")
    except UnknownVenError:
        logger.warning(f"Attempted to deregister unknown VEN with ID {ven_id}")
    return None

async def on_register_report(
    ven_id,
    resource_id,
    measurement,
    unit,
    scale,
    min_sampling_interval,
    max_sampling_interval,
):
    callback = partial(
        on_update_report,
        ven_id=ven_id,
        resource_id=resource_id,
        measurement=measurement,
    )
    sampling_interval = min_sampling_interval
    return callback, sampling_interval

async def on_update_report(data, ven_id, resource_id, measurement):
    logger.info("on update report")
    logger.info(data)
    for time, value in data:
        logger.info(
            f"Ven {ven_id} reported {measurement} = {value} at time {time} for resource {resource_id}"
        )

async def event_response_callback(ven_id, event_id, opt_type):
    logger.info(f"VEN {ven_id} responded to Event {event_id} with: {opt_type}")

async def on_request_event(ven_id):
    """
    Custom handler to provide events for a VEN when it requests them.
    """
    # Here, you can add logic to determine which events should be sent to the VEN
    events = VEN_REGISTRY.get_events_for_ven(ven_id)  # Assuming you have this method implemented
    return events

async def on_created_event(ven_id, event_id, opt_type):
    """
    Custom handler to process the response from a VEN when they acknowledge the receipt of an event.
    """
    logger.info(f"VEN {ven_id} responded to Event {event_id} with: {opt_type}")

async def handle_event_post(request):
    payload = await request.json()
    logger.info('Received Event Payload:', payload)
    ven_name = payload.get("venName")
    if not ven_name:
        logger.error("Error: Missing venName")
        raise web.HTTPBadRequest(text="Missing venName")
    
    signal_name = payload.get("eventName")
    signal_type = payload.get("eventType")
    start_time = payload.get("startTime")
    duration = payload.get("duration")

    if not all([signal_name, signal_type, start_time, duration]):
        logger.error("Error: Missing required event data")
        raise web.HTTPBadRequest(text="Missing required event data")

    intervals = [
        {
            "dtstart": datetime.strptime(start_time, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc),
            "duration": timedelta(minutes=int(duration)),
            "signal_payload": 1,
        }
    ]

    if signal_name not in ["SIMPLE", "ELECTRICITY_PRICE", "LOAD_DISPATCH"]:
        logger.error(f"Error: Unknown name {signal_name}")
        raise web.HTTPBadRequest(text=f"Unknown name {signal_name}")
    if signal_type not in [
        "level",
        "price",
        "priceRelative",
        "priceMultiplier",
        "setpoint",
        "delta",
        "multiplier",
    ]:
        logger.error(f"Error: Unknown type {signal_type}")
        raise web.HTTPBadRequest(text=f"Unknown type {signal_type}")

    try:
        ven = VEN_REGISTRY.get_ven_info_from_name(ven_name)
        logger.info(f'VEN found: {ven}')
    except UnknownVenError:
        logger.error(f"Error: VEN {ven_name} not found")
        raise web.HTTPNotFound(text=f"VEN {ven_name} not found")

    # Check for existing events with the same parameters
    existing_events = request.app["server"].events.get(ven.ven_id, [])
    for event in existing_events:
        existing_signal_name = event.event_signals[0].signal_name
        existing_signal_type = event.event_signals[0].signal_type
        existing_intervals = event.event_signals[0].intervals

        # Compare event details
        if (existing_signal_name == signal_name and
            existing_signal_type == signal_type and
            existing_intervals == intervals):
            logger.info(f"Duplicate event detected for VEN {ven.ven_id}. Event not added.")
            return web.json_response({"status": "error", "message": "Duplicate event detected. Event not added."}, status=400)

    # If no duplicates found, add the event
    event_id = request.app["server"].add_event(
        ven.ven_id, signal_name, signal_type, intervals, callback=event_response_callback
    )
    logger.info(f"Sent event to {ven_name}: {signal_name} ({signal_type})")
    return web.json_response({"status": "success", "message": f"Event sent to {ven_name}", "event_id": event_id})

async def handle_ven_post(request):
    payload = await request.json()
    logger.info('Received VEN Payload:', payload)
    ven_name = payload["venName"]

    try:
        VEN_REGISTRY.add_ven(ven_name)
        logger.info(f'VEN {ven_name} added successfully.')
        return web.json_response({"status": "success", "message": f"VEN {ven_name} added successfully"})
    except DuplicateVenError:
        logger.warning(f'VEN {ven_name} already registered.')
        return web.json_response({"status": "error", "message": "VEN already registered"}, status=400)

async def handle_list_all_events(request):
    events_list = []
    try:
        for ven_id, events in request.app["server"].events.items():
            for event in events:
                event_id = event.event_descriptor.event_id
                event_name = event.event_signals[0].signal_name
                event_type = event.event_signals[0].signal_type
                event_start = event.active_period['dtstart']
                event_duration = event.active_period['duration']

                try:
                    ven_info = VEN_REGISTRY.get_ven_info_from_id(ven_id)
                    ven_name = ven_info.ven_name
                except UnknownVenError:
                    ven_name = "Unknown VEN"

                # Print the specific details on a single line
                logger.info(f"EVENTS - {ven_name}, Event Start: {event_start}, Event Duration: {event_duration}, Signal Type: {event_type}")

                events_list.append({
                    "ven_id": ven_id,
                    "ven_name": ven_name,
                    "event_id": event_id,
                    "event_name": event_name,
                    "event_type": event_type,
                    "event_start": event_start.isoformat(),
                    "event_duration": event_duration.total_seconds() / 60
                })
        return web.json_response(events_list)
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise web.HTTPInternalServerError(text=str(e))

async def handle_cancel_event(request):
    payload = await request.json()
    ven_id = payload.get("ven_id")
    event_id = payload.get("event_id")

    if not ven_id or not event_id:
        raise web.HTTPBadRequest(text="Missing ven_id or event_id")

    # Cancel the event using OpenADRServer's method
    request.app["server"].cancel_event(ven_id, event_id)
    logger.info(f"Cancelled event {event_id} for VEN {ven_id}")
    return web.json_response({"status": "success", "message": f"Event {event_id} cancelled for VEN {ven_id}"})

async def handle_remove_ven(request):
    payload = await request.json()
    ven_name = payload.get("venName")

    if not ven_name:
        raise web.HTTPBadRequest(text="Missing venName")

    try:
        VEN_REGISTRY.remove_ven(ven_name)
        logger.info(f"Removed VEN {ven_name} successfully.")
        return web.json_response({"status": "success", "message": f"VEN {ven_name} removed successfully"})
    except UnknownVenError:
        logger.warning(f"VEN {ven_name} not found.")
        return web.json_response({"status": "error", "message": f"VEN {ven_name} not found"}, status=404)

async def handle_list_vens(request):
    ven_list = VEN_REGISTRY.get_all_vens()
    return web.json_response([{"ven_name": ven.ven_name, "ven_id": ven.ven_id, "registration_id": ven.registration_id} for ven in ven_list])