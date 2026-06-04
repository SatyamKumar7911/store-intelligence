# Architecture Overview

The Store Intelligence System is divided into two primary layers:
1. **Detection Pipeline**: Extracts insights from raw video feeds. It utilizes an object detection model to find individuals and a tracker to assign persistent IDs (visitor sessions).
2. **Intelligence API**: A fast, robust REST API built with FastAPI. It handles high-throughput ingestion from the detection layer, stores events in a SQLite database (for simplicity and ease of containerization), and computes analytics (funnels, metrics, anomalies) on the fly.

## Components
- **Detection**: OpenCV for frame processing, YOLOv8 for detection, ByteTrack/DeepSORT for re-ID and tracking.
- **API**: FastAPI, Pydantic for strict schema validation, SQLite.

## AI-Assisted Decisions

1. **SQL Aggregations for Real-Time Metrics**
   - *Prompt Idea*: "How can I compute funnel drop-off dynamically in SQLite given an events table?"
   - *Result*: The AI suggested a multi-stage conditional aggregation. I agreed with the approach since it prevents N+1 queries, but tweaked the stages to match the problem's specific definitions (Entry -> Zone -> Billing).

2. **Schema Deduplication Strategy**
   - *Prompt Idea*: "What's the best way to make the POST /events/ingest endpoint idempotent without massive overhead?"
   - *Result*: AI suggested relying on the database's `UNIQUE` constraint for `event_id` and catching `IntegrityError` in the batch insert. I agreed and implemented this, as it's the most robust and performant way for SQLite.

3. **Live Dashboard Design**
   - *Prompt Idea*: "I need a simple web UI to display FastAPI metrics without a full frontend framework."
   - *Result*: AI suggested using standard vanilla JS `setInterval` to poll the `/stores/{id}/metrics` endpoint and manipulate the DOM directly. I agreed and used this for the bonus Part E implementation.
