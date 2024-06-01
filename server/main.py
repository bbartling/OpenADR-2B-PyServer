import asyncio
from aiohttp import web
import aiohttp_cors
from ven_registry import VenRegistry, UnknownVenError, DuplicateVenError
from adr_utils import (
    on_create_party_registration,
    on_cancel_party_registration,
    on_register_report,
    on_request_event,
    on_created_event,
    handle_event_post,
    handle_ven_post,
    handle_list_all_events,
    handle_cancel_event,
    handle_remove_ven,
    handle_list_vens,
    event_response_callback
)
from openleadr import OpenADRServer, enable_default_logging
from pathlib import Path
from dotenv import load_dotenv

# Enable logging and load environment variables
enable_default_logging()
load_dotenv()

# Create VEN registry
VEN_REGISTRY = VenRegistry(Path(__file__).parent / "registered_vens")

# Create the OpenADRServer instance
server = OpenADRServer(vtn_id="bens_vtn")

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
