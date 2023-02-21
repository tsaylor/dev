import functools
import json
import random
import time
import uuid
from asyncio import create_task, gather
from asyncio import sleep as aiosleep
from asyncio import wait

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles


def get_and_process(get_data, process_data, data):
    task = create_task(get_data(data))
    task.add_done_callback(functools.partial(process_data, data))
    return task


async def service_call_simulator(data):
    simulated_duration = random.randint(0, data["request"]["dur_ms"])
    await aiosleep(simulated_duration / 1000)
    return {f"service call took {simulated_duration} milliseconds": True}


def service_call_data_processor(data, service_call_fut):
    new_data = service_call_fut.result()
    data.update(new_data)
    return True


async def store_complete_aggregation(id, aggregated_data, done, pending):
    await gather(*pending, return_exceptions=True)
    # TODO handle exceptions
    with open(f"{id}.json", "w") as f:
        json.dump(aggregated_data, f, indent=4)
    print(f"Stored http://localhost:8000/retrieve/{id}.json")


async def aggregate_service_calls(request):
    start_time = time.monotonic()
    request_id = str(uuid.uuid4())
    dur_ms = int(request.query_params.get("dur_ms", 10000))
    count = int(request.query_params.get("count", 10))
    timeout_sec = int(request.query_params.get("timeout_sec", 5))
    aggregated_data = {
        "request": {
            "id": request_id,
            "dur_ms": dur_ms,
            "count": count,
            "timeout_sec": timeout_sec,
        }
    }
    service_calls = [
        get_and_process(
            service_call_simulator, service_call_data_processor, aggregated_data
        )
        for i in range(count)
    ]
    (done, pending) = await wait(service_calls, timeout=timeout_sec)
    task = BackgroundTask(
        store_complete_aggregation, request_id, aggregated_data, done, pending
    )
    aggregated_data["number of timeouts"] = len(pending)
    aggregated_data["response generation time"] = time.monotonic() - start_time
    return JSONResponse(aggregated_data, background=task)


def startup():
    print("Open http://localhost:8000 in your browser")


routes = [
    Route("/", aggregate_service_calls),
    Mount("/retrieve", app=StaticFiles(directory="."), name="retrieve"),
]

app = Starlette(debug=True, routes=routes, on_startup=[startup])
