import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "/tmp/store_intelligence.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                store_id TEXT,
                camera_id TEXT,
                visitor_id TEXT,
                event_type TEXT,
                timestamp TEXT,
                zone_id TEXT,
                dwell_ms INTEGER,
                is_staff BOOLEAN,
                confidence REAL,
                metadata TEXT
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_store_visitor_time 
            ON events(store_id, visitor_id, timestamp)
        ''')
        
        # Auto-seed the database if it is empty so the dashboard is instantly visual
        cursor.execute("SELECT COUNT(*) FROM events")
        if cursor.fetchone()[0] == 0:
            import datetime
            import json
            today_str = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            seed_events = []
            
            # Seed 10 visitors to display realistic metrics
            for i in range(1, 11):
                visitor_id = f"VIS_SEED_{i:03d}"
                
                # ENTRY
                seed_events.append((
                    f"seed-entry-{i}",
                    "STORE_BLR_002",
                    "CAM_ENTRY_01",
                    visitor_id,
                    "ENTRY",
                    today_str,
                    None,
                    0,
                    False,
                    0.99,
                    json.dumps({"session_seq": 1})
                ))
                
                # ZONE_ENTER & ZONE_DWELL (Skincare or Fragrance)
                zone = "SKINCARE" if i % 2 == 0 else "FRAGRANCE"
                seed_events.append((
                    f"seed-zone-enter-{i}",
                    "STORE_BLR_002",
                    "CAM_FLOOR_01",
                    visitor_id,
                    "ZONE_ENTER",
                    today_str,
                    zone,
                    0,
                    False,
                    0.95,
                    json.dumps({"session_seq": 2})
                ))
                seed_events.append((
                    f"seed-zone-dwell-{i}",
                    "STORE_BLR_002",
                    "CAM_FLOOR_01",
                    visitor_id,
                    "ZONE_DWELL",
                    today_str,
                    zone,
                    15000 + (i * 1000),
                    False,
                    0.95,
                    json.dumps({"session_seq": 3})
                ))
                
                # Conversions: 3 visitors join billing queue (30% Conversion)
                if i in [1, 2, 3]:
                    seed_events.append((
                        f"seed-billing-join-{i}",
                        "STORE_BLR_002",
                        "CAM_BILLING_01",
                        visitor_id,
                        "BILLING_QUEUE_JOIN",
                        today_str,
                        "BILLING_ZONE",
                        0,
                        False,
                        0.98,
                        json.dumps({"session_seq": 4, "queue_depth": i})
                    ))
                
                # Abandonment: 1 visitor abandons billing (33.3% Abandonment Rate)
                if i == 3:
                    seed_events.append((
                        f"seed-billing-abandon-{i}",
                        "STORE_BLR_002",
                        "CAM_BILLING_01",
                        visitor_id,
                        "BILLING_QUEUE_ABANDON",
                        today_str,
                        "BILLING_ZONE",
                        0,
                        False,
                        0.98,
                        json.dumps({"session_seq": 5})
                    ))
                
                # EXIT
                seed_events.append((
                    f"seed-exit-{i}",
                    "STORE_BLR_002",
                    "CAM_ENTRY_01",
                    visitor_id,
                    "EXIT",
                    today_str,
                    None,
                    0,
                    False,
                    0.99,
                    json.dumps({"session_seq": 6 if i in [1, 2, 3] else 4})
                ))
                
            cursor.executemany('''
                INSERT INTO events (event_id, store_id, camera_id, visitor_id, event_type, timestamp, zone_id, dwell_ms, is_staff, confidence, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', seed_events)
            
        conn.commit()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
