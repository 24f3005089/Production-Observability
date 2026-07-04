from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

import time
import uuid
import json
from collections import deque

EMAIL = "24f3005089@ds.study.iitm.ac.in"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

# Prometheus counter
REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP requests"
)

# Keep last 1000 logs
logs = deque(maxlen=1000)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    REQUEST_COUNTER.inc()

    request_id = str(uuid.uuid4())

    response = await call_next(request)

    logs.append({
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id,
    })

    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/work")
def work(n: int = Query(...)):
    # simulate K units of work
    for _ in range(n):
        pass

    return {
        "email": EMAIL,
        "done": n,
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME,
    }


@app.get("/logs/tail")
def tail(limit: int = Query(10)):
    return list(logs)[-limit:]