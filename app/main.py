from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import time
import os

from .models import StoreEvent
from .ingestion import ingest_events
from .database import init_db
from .metrics import get_metrics, get_heatmap
from .funnel import get_funnel
from .anomalies import get_anomalies

app = FastAPI(title="Store Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.middleware("http")
async def add_structured_logs(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        latency = int((time.time() - start_time) * 1000)
        store_id = request.path_params.get("id", "NA")
        print(f"trace_id=NA store_id={store_id} endpoint={request.url.path} latency_ms={latency} status_code={response.status_code}")
        return response
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        store_id = request.path_params.get("id", "NA")
        print(f"trace_id=NA store_id={store_id} endpoint={request.url.path} latency_ms={latency} status_code=503 error='{str(e)}'")
        return JSONResponse(status_code=503, content={"error": "Service unavailable or internal error"})

@app.get("/")
def root():
    return RedirectResponse(url="/dashboard/index.html")

@app.post("/events/ingest")
def ingest(events: List[StoreEvent]):
    result = ingest_events(events)
    print(f"event_count={len(events)}")
    if result["errors"]:
        return JSONResponse(status_code=207, content=result)
    return {"message": "success", **result}

@app.get("/stores/{id}/metrics")
def metrics(id: str):
    return get_metrics(id)

@app.get("/stores/{id}/funnel")
def funnel(id: str):
    return get_funnel(id)

@app.get("/stores/{id}/heatmap")
def heatmap(id: str):
    return get_heatmap(id)

@app.get("/stores/{id}/anomalies")
def anomalies(id: str):
    return get_anomalies(id)

@app.get("/health")
def health():
    return {"status": "healthy"}

# Serve static dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="dashboard")
