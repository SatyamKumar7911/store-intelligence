from .models import StoreEvent
from .database import get_db
import sqlite3
import json

def ingest_events(events: list[StoreEvent]):
    success_count = 0
    errors = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        for event in events:
            try:
                cursor.execute('''
                    INSERT INTO events (
                        event_id, store_id, camera_id, visitor_id, event_type, 
                        timestamp, zone_id, dwell_ms, is_staff, confidence, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id, event.store_id, event.camera_id, event.visitor_id,
                    event.event_type, event.timestamp.isoformat(), event.zone_id,
                    event.dwell_ms, event.is_staff, event.confidence, 
                    event.metadata.model_dump_json() if event.metadata else None
                ))
                success_count += 1
            except sqlite3.IntegrityError:
                # Idempotency: ignore duplicate event_id
                success_count += 1
            except Exception as e:
                errors.append({"event_id": event.event_id, "error": str(e)})
        conn.commit()
    
    return {"inserted": success_count, "errors": errors}
