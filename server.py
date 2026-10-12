
import time
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from anyio import to_thread
from pydantic import BaseModel

class ThreadPoolConfig(BaseModel):
    max_tokens: int


start_time = time.perf_counter()

def log(request_id, event, timestamp, thread_id=None):
    elapsed = timestamp - start_time
    print(
        f"Request {request_id} | {event:<10} | "
        f"Time: {elapsed:.3f}s | Thread: {thread_id}",
        flush=True
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    limiter = to_thread.current_default_thread_limiter()
    print("Initial thread pool limit:", limiter.total_tokens)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/configure")
async def configure_threadpool(config: ThreadPoolConfig):
    limiter = to_thread.current_default_thread_limiter()
    limiter.total_tokens = config.max_tokens

    return {"max_tokens": limiter.total_tokens}


# @app.get("/threadpool")
# async def get_threadpool():
#     limiter = to_thread.current_default_thread_limiter()

#     return {
#         "max_tokens": limiter.total_tokens,
#         "borrowed_tokens": limiter.borrowed_tokens
#     }



def process_request(request_id, arrival_time):
    thread_id = threading.get_ident()

    assigned_time = time.perf_counter()
    log(request_id, "ASSIGNED", assigned_time, thread_id)

    time.sleep(2)

    completed_time = time.perf_counter()
    log(request_id, "COMPLETED", completed_time, thread_id)

    return {
        "request_id": request_id,
        "thread_id": thread_id,
        "waiting_time": round(assigned_time - arrival_time, 3),
        "execution_time": round(completed_time - assigned_time, 3),
        "total_time": round(completed_time - arrival_time, 3)
    }


@app.get("/test")
async def test_endpoint(request_id: int):
    arrival_time = time.perf_counter()
    log(request_id, "ARRIVED", arrival_time)

    return await to_thread.run_sync(
        process_request, request_id, arrival_time
    )
