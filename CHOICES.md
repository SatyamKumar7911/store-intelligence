# Implementation Choices

## 1. Detection Model
- **Options Considered**: YOLOv8, MediaPipe, RT-DETR.
- **AI Suggestion**: YOLOv8 nano/small for balancing speed and accuracy on standard CPU/GPU infrastructure.
- **My Choice & Rationale**: YOLOv8. It provides an excellent trade-off between inference speed and bounding-box accuracy. It handles partial occlusions decently well, which is common in retail (e.g. billing queues). Using a pre-trained model on the COCO dataset (class 0: person) requires no further training to get a functional prototype.

## 2. Event Schema Design
- **Options Considered**: A normalized relational schema (visitors table + events table) vs a flat event-sourced schema.
- **AI Suggestion**: Suggested a flat schema for ease of ingestion, appending a JSON payload for variable metadata.
- **My Choice & Rationale**: I went with the flat event-sourced schema as suggested. It strictly adheres to the required output schema, provides the flexibility to query aggregations dynamically, and reduces write contention since the pipeline just append rows. Metadata is stored as JSON in the database, offering schema flexibility without migrations.

## 3. API Architecture
- **Options Considered**: PostgreSQL vs SQLite.
- **AI Suggestion**: Suggested SQLite for easy containerization in a take-home challenge, while noting PostgreSQL is better for real-world scaling.
- **My Choice & Rationale**: SQLite. The challenge emphasizes "docker compose up starts everything" with no manual steps. SQLite avoids managing a separate database container, initialization scripts, and connection pooler overhead. It easily handles the throughput of 40 stores if WAL mode is enabled and batch inserts are used.
