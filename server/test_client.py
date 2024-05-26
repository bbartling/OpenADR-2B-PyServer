import sys
import asyncio
from datetime import timedelta
from openleadr import OpenADRClient, enable_default_logging

enable_default_logging()

async def collect_report_value():
    # This callback is called when you need to collect a value for your Report
    return 1.23

async def handle_event(event):
    # This callback receives an Event dict.
    # You should include code here that sends control signals to your resources.
    print("----- EVENT -----")
    print(event)
    print("-----------------")
    return "optIn"

async def handle_update_event(event):
    # This callback receives an Event dict for updated events.
    # You should include code here that sends control signals to your resources.
    print("----- UPDATED EVENT hit -----")
    print(event)
    print("-------------------------")
    return "optIn"  # or "optOut" based on your logic

vtn_url = "http://localhost:8080/OpenADR2/Simple/2.0b"
print(f"Connecting to: {vtn_url}")

# Create the client object
ven_name = "asdf"
client = OpenADRClient(ven_name, vtn_url)

# Add the report capability to the client
client.add_report(callback=collect_report_value,
                  resource_id="device001",
                  measurement="voltage",
                  sampling_rate=timedelta(seconds=20))

# Add event handling capability to the client
client.add_handler("on_event", handle_event)

# Add updated event handling capability to the client
client.add_handler("on_update_event", handle_update_event)

# Run the client in the Python AsyncIO Event Loop
loop = asyncio.get_event_loop()
loop.create_task(client.run())
loop.run_forever()
