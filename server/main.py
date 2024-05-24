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
    """
    Inspect the registration info and return a ven_id and registration_id.
    """
    ven_name = registration_info["ven_name"]
    try:
        ven_info = VEN_REGISTRY.get_ven_info_from_name(ven_name)
        return (ven_info.ven_id, ven_info.registration_id)
    except UnknownVenError:
        print(f"An unknown VEN tried to connect: {ven_name}")
    return False

async def on_register_report(
    ven_id,
    resource_id,
    measurement,
    unit,
    scale,
    min_sampling_interval,
    max_sampling_interval,
):
    """
    Inspect a report offering from the VEN and return a callback and sampling interval for receiving the reports.
    """
    callback = partial(
        on_update_report,
        ven_id=ven_id,
        resource_id=resource_id,
        measurement=measurement,
    )
    sampling_interval = min_sampling_interval
    return callback, sampling_interval

async def on_update_report(data, ven_id, resource_id, measurement):
    """
    Callback that receives report data from the VEN and handles it.
    """
    print("on update report")
    print(data)
    for time, value in data:
        print(
            f"Ven {ven_id} reported {measurement} = {value} at time {time} for resource {resource_id}"
        )

async def event_response_callback(ven_id, event_id, opt_type):
    """
    Callback that receives the response from a VEN to an Event.
    """
    print(f"VEN {ven_id} responded to Event {event_id} with: {opt_type}")

async def handle_event_post(request):
    """
    Handler for a POST request to `/api/event`
    """
    # Parse request payload
    payload = await request.json()
    print('Received Event Payload:', payload)  # Debugging print
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
            "duration": timedelta(minutes=int(duration)),  # Ensure duration is an integer
            "signal_payload": 1,
        }
    ]

    # Verify payload
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
    # TODO: verify intervals

    # Send this event to the VEN
    try:
        ven = VEN_REGISTRY.get_ven_info_from_name(ven_name)
        print(f'VEN found: {ven}')  # Debugging print
    except UnknownVenError:
        print(f"Error: VEN {ven_name} not found")
        raise web.HTTPNotFound(text=f"VEN {ven_name} not found")

    request.app["server"].add_event(
        ven.ven_id, signal_name, signal_type, intervals
    )

    print(f"Sent event to {ven_name}: {signal_name} ({signal_type})")
    return web.json_response({"status": "success", "message": f"Event sent to {ven_name}"})

async def handle_ven_post(request):
    """
    Handler for a POST request to `/api/ven`
    """
    # Parse request payload
    payload = await request.json()
    print('Received VEN Payload:', payload)  # Debugging print
    ven_name = payload["venName"]

    try:
        VEN_REGISTRY.add_ven(ven_name)
        print(f'VEN {ven_name} added successfully.')  # Debugging print
        return web.json_response({"status": "success", "ven_name": ven_name})
    except DuplicateVenError:
        print(f'VEN {ven_name} already registered.')  # Debugging print
        return web.json_response({"status": "error", "message": "VEN already registered"}, status=400)

# Create the server object
server = OpenADRServer(
    vtn_id="bens_vtn",
    # cert="server_certificate.crt",
    # key="server_private_key.pem",
    # passphrase=os.getenv("SERVER_KEY_PASSPHRASE"),
    # ven_lookup=lambda ven_id: VEN_REGISTRY.get_ven_info_from_id(ven_id)._asdict(),
)

# Add the handler for client (VEN) registrations
server.add_handler("on_create_party_registration", on_create_party_registration)

# Add the handler for report registrations from the VEN
server.add_handler("on_register_report", on_register_report)

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

# Add all resources to `CorsConfig`.
resource = cors.add(server.app.router.add_resource("/api/ven"))
cors.add(resource.add_route("POST", handle_ven_post))

resource = cors.add(server.app.router.add_resource("/api/event"))
cors.add(resource.add_route("POST", handle_event_post))

# Run the server on the asyncio event loop
loop = asyncio.new_event_loop()
loop.create_task(server.run())
loop.run_forever()
