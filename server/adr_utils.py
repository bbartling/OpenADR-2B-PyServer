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
        # Update the registry with the last report value, units, and time
        ven_info = VEN_REGISTRY.get_ven_info_from_id(ven_id)
        VEN_REGISTRY.update_ven_report(ven_info.ven_name, value, measurement, time.isoformat())

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
    ven_ids = payload.get("ven_ids", [])
    signal_name = payload.get("signalName")
    signal_type = payload.get("signalType")
    start_time = payload.get("startTime")
    duration = payload.get("duration")

    if not all([ven_ids, signal_name, signal_type, start_time, duration]):
        logger.error("Error: Missing required event data")
        raise web.HTTPBadRequest(text="Missing required event data")

    signal_payload = None
    if signal_name == "SIMPLE":
        signal_payload = payload.get("level", 1)
    elif signal_name == "ELECTRICITY_PRICE":
        signal_payload = payload.get("price")
        if signal_payload is None:
            raise web.HTTPBadRequest(text="Missing price for ELECTRICITY_PRICE event")
    elif signal_name == "LOAD_DISPATCH":
        signal_payload = payload.get("setpoint")
        if signal_payload is None:
            raise web.HTTPBadRequest(text="Missing setpoint for LOAD_DISPATCH event")
    else:
        raise web.HTTPBadRequest(text=f"Unknown signal name {signal_name}")

    intervals = [
        {
            "dtstart": datetime.strptime(start_time, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc),
            "duration": timedelta(minutes=int(duration)),
            "signal_payload": signal_payload,
        }
    ]

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

    responses = []
    for ven_id in ven_ids:
        try:
            ven = VEN_REGISTRY.get_ven_info_from_id(ven_id)
            logger.info(f'VEN found: {ven}')
        except UnknownVenError:
            logger.error(f"Error: VEN {ven_id} not found")
            responses.append({"status": "error", "message": f"VEN {ven_id} not found"})
            continue

        # Check for existing events with the same parameters
        existing_events = request.app["server"].events.get(ven_id, [])
        is_duplicate = False
        for event in existing_events:
            existing_signal_name = event.event_signals[0].signal_name
            existing_signal_type = event.event_signals[0].signal_type
            existing_intervals = event.event_signals[0].intervals

            if (existing_signal_name == signal_name and
                existing_signal_type == signal_type and
                existing_intervals == intervals):
                logger.info(f"Duplicate event detected for VEN {ven_id}. Event not added.")
                responses.append({"status": "error", "message": f"Duplicate event detected for VEN {ven_id}"})
                is_duplicate = True
                break
        
        if is_duplicate:
            continue

        # If no duplicates found, add the event
        event_id = request.app["server"].add_event(
            ven_id, signal_name, signal_type, intervals, callback=event_response_callback
        )
        logger.info(f"Sent event to {ven.ven_name}: {signal_name} ({signal_type})")
        responses.append({"status": "success", "message": f"Event sent to {ven.ven_name}", "event_id": event_id})

    return web.json_response(responses)


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
                signal_name = event.event_signals[0].signal_name
                signal_type = event.event_signals[0].signal_type
                event_start = event.active_period['dtstart']
                event_duration = event.active_period['duration']

                try:
                    ven_info = VEN_REGISTRY.get_ven_info_from_id(ven_id)
                    ven_name = ven_info.ven_name
                except UnknownVenError:
                    ven_name = "Unknown VEN"

                # Print the specific details on a single line
                logger.info(f"EVENTS - {ven_name}, Event Start: {event_start}, Event Duration: {event_duration}, Signal Type: {signal_type}")

                events_list.append({
                    "ven_id": ven_id,
                    "ven_name": ven_name,
                    "event_id": event_id,
                    "signal_name": signal_name,
                    "signal_type": signal_type,
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

    # Retrieve ven_name
    try:
        ven_info = VEN_REGISTRY.get_ven_info_from_id(ven_id)
        ven_name = ven_info.ven_name
    except UnknownVenError:
        raise web.HTTPNotFound(text=f"VEN with id {ven_id} not found")

    # Retrieve event_name
    event_name = None
    existing_events = request.app["server"].events.get(ven_id, [])
    for event in existing_events:
        if event.event_descriptor.event_id == event_id:
            event_name = event.event_signals[0].signal_name
            break

    if not event_name:
        raise web.HTTPNotFound(text=f"Event with id {event_id} not found for VEN {ven_id}")

    # Cancel the event using OpenADRServer's method
    request.app["server"].cancel_event(ven_id, event_id)
    logger.info(f"Cancelled event {event_id} for VEN {ven_id}")
    return web.json_response({"status": "success", "message": f"Event '{event_name}' cancelled for VEN '{ven_name}'"})


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
    ven_list = VEN_REGISTRY.get_all_vens_with_quality()
    return web.json_response([
        {
            "ven_name": ven["ven_name"],
            "ven_id": ven["ven_id"],
            "registration_id": ven["registration_id"],
            "last_report": ven["last_report"],
            "last_report_units": ven["last_report_units"],
            "last_report_time": ven["last_report_time"],
            "connection_quality": ven["connection_quality"]
        }
        for ven in ven_list
    ])
