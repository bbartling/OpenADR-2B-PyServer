import asyncio
import os
from datetime import datetime, timezone, timedelta
from functools import partial
from pathlib import Path

import aiohttp_cors
from aiohttp import web
from dotenv import load_dotenv
from openleadr import OpenADRServer, enable_default_logging

from ven_registry import VenRegistry, UnknownVenError, DuplicateVenError

enable_default_logging()
load_dotenv()

VEN_REGISTRY = VenRegistry(
    Path(__file__).parent / "registered_vens"
)

async def on_create_party_registration(registration_info):
    ven_name = registration_info["ven_name"]
    try:
        ven_info = VEN_REGISTRY.get_ven_info_from_name(ven_name)
        return (ven_info.ven_id, ven_info.registration_id)
    except UnknownVenError:
        print(f"An unknown VEN tried to connect: {ven_name}")
    return False

async def on_cancel_party_registration(payload):
    ven_id = payload['ven_id']
    try:
        ven_info = VEN_REGISTRY.get_ven_info_from_id(ven_id)
        VEN_REGISTRY.remove_ven(ven_info.ven_name)
        print(f"VEN {ven_info.ven_name} with ID {ven_id} has been deregistered.")
    except UnknownVenError:
        print(f"Attempted to deregister unknown VEN with ID {ven_id}")
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
    print("on update report")
    print(data)
    for time, value in data:
        print(
            f"Ven {ven_id} reported {measurement} = {value} at time {time} for resource {resource_id}"
        )

async def event_response_callback(ven_id, event_id, opt_type):
    print(f"VEN {ven_id} responded to Event {event_id} with: {opt_type}")

async def event_delivery_callback(ven_id, event_id):
    print(f"Event {event_id} delivered to VEN {ven_id}")

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
    print(f"VEN {ven_id} responded to Event {event_id} with: {opt_type}")

async def handle_event_post(request):
    payload = await request.json()
    print('Received Event Payload:', payload)
    ven_name = payload.get("venName")
    if not ven_name:
        print("Error: Missing venName")
        raise web.HTTPBadRequest(text="Missing venName")
    
    signal_name = payload.get("eventName")
    signal_type = payload.get("eventType")
    start_time = payload.get("startTime")
    duration = payload.get("duration")

    if not all([signal_name, signal_type, start_time, duration]):
        print("Error: Missing required event data")
        raise web.HTTPBadRequest(text="Missing required event data")

    intervals = [
        {
            "dtstart": datetime.strptime(start_time, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc),
            "duration": timedelta(minutes=int(duration)),
            "signal_payload": 1,
        }
    ]

    if signal_name not in ["SIMPLE", "ELECTRICITY_PRICE", "LOAD_DISPATCH"]:
        print(f"Error: Unknown name {signal_name}")
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
        print(f"Error: Unknown type {signal_type}")
        raise web.HTTPBadRequest(text=f"Unknown type {signal_type}")

    try:
        ven = VEN_REGISTRY.get_ven_info_from_name(ven_name)
        print(f'VEN found: {ven}')
    except UnknownVenError:
        print(f"Error: VEN {ven_name} not found")
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
            print(f"Duplicate event detected for VEN {ven.ven_id}. Event not added.")
            return web.json_response({"status": "error", "message": "Duplicate event detected. Event not added."}, status=400)

    # If no duplicates found, add the event
    event_id = request.app["server"].add_event(
        ven.ven_id, signal_name, signal_type, intervals, callback=event_response_callback, delivery_callback=event_delivery_callback
    )

    print(f"Sent event to {ven_name}: {signal_name} ({signal_type})")
    return web.json_response({"status": "success", "message": f"Event sent to {ven_name}", "event_id": event_id})


async def handle_ven_post(request):
    payload = await request.json()
    print('Received VEN Payload:', payload)
    ven_name = payload["venName"]

    try:
        VEN_REGISTRY.add_ven(ven_name)
        print(f'VEN {ven_name} added successfully.')
        return web.json_response({"status": "success", "message": f"VEN {ven_name} added successfully"})
    except DuplicateVenError:
        print(f'VEN {ven_name} already registered.')
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
                print(f"EVENTS - {ven_name}, Event Start: {event_start}, Event Duration: {event_duration}, Signal Type: {event_type}")

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
        print(f"Error listing events: {e}")
        raise web.HTTPInternalServerError(text=str(e))

async def handle_cancel_event(request):
    payload = await request.json()
    ven_id = payload.get("ven_id")
    event_id = payload.get("event_id")

    if not ven_id or not event_id:
        raise web.HTTPBadRequest(text="Missing ven_id or event_id")

    # Cancel the event using OpenADRServer's method
    request.app["server"].cancel_event(ven_id, event_id)
    print(f"Cancelled event {event_id} for VEN {ven_id}")
    return web.json_response({"status": "success", "message": f"Event {event_id} cancelled for VEN {ven_id}"})

async def handle_remove_ven(request):
    payload = await request.json()
    ven_name = payload.get("venName")

    if not ven_name:
        raise web.HTTPBadRequest(text="Missing venName")

    try:
        VEN_REGISTRY.remove_ven(ven_name)
        print(f"Removed VEN {ven_name} successfully.")
        return web.json_response({"status": "success", "message": f"VEN {ven_name} removed successfully"})
    except UnknownVenError:
        print(f"VEN {ven_name} not found.")
        return web.json_response({"status": "error", "message": f"VEN {ven_name} not found"}, status=404)

async def handle_list_vens(request):
    ven_list = VEN_REGISTRY.get_all_vens()
    return web.json_response([{"ven_name": ven.ven_name, "ven_id": ven.ven_id, "registration_id": ven.registration_id} for ven in ven_list])

# Create the OpenADRServer instance
server = OpenADRServer(
    vtn_id="bens_vtn",
)

# Add the handlers for VEN registrations and reports
server.add_handler("on_create_party_registration", on_create_party_registration)
server.add_handler("on_cancel_party_registration", on_cancel_party_registration)
server.add_handler("on_register_report", on_register_report)
server.add_handler("on_request_event", on_request_event)
server.add_handler("on_created_event", on_created_event)

# Set up CORS and routes for handling VEN and event operations
cors = aiohttp_cors.setup(
    server.app,
    defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    },
)

# Add routes to the server
resource = cors.add(server.app.router.add_resource("/api/ven"))
cors.add(resource.add_route("POST", handle_ven_post))

resource = cors.add(server.app.router.add_resource("/api/event"))
cors.add(resource.add_route("POST", handle_event_post))

resource = cors.add(server.app.router.add_resource("/api/all_events"))
cors.add(resource.add_route("GET", handle_list_all_events))

resource = cors.add(server.app.router.add_resource("/api/cancel_event"))
cors.add(resource.add_route("POST", handle_cancel_event))

resource = cors.add(server.app.router.add_resource("/api/remove_ven"))
cors.add(resource.add_route("POST", handle_remove_ven))

resource = cors.add(server.app.router.add_resource("/api/list_vens"))
cors.add(resource.add_route("GET", handle_list_vens))

# Run the server
loop = asyncio.new_event_loop()
loop.create_task(server.run())
loop.run_forever()
