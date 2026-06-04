import urllib.request
import json
import time
import uuid
from datetime import datetime, timezone

API_URL = "http://localhost:8000/events/ingest"

def post_event(event):
    req = urllib.request.Request(API_URL, method="POST")
    req.add_header('Content-Type', 'application/json')
    data = json.dumps([event]).encode('utf-8')
    try:
        response = urllib.request.urlopen(req, data=data)
        print(f"Sent {event['event_type']} - Status: {response.status}")
    except Exception as e:
        print("Error sending event:", e)

def generate_event(event_type, visitor_id, metadata):
    return {
        "event_id": str(uuid.uuid4()),
        "store_id": "STORE_BLR_002",
        "camera_id": "CAM_ENTRY_01",
        "visitor_id": visitor_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "zone_id": "SKINCARE" if "ZONE" in event_type else None,
        "dwell_ms": 5000 if event_type == "ZONE_DWELL" else 0,
        "is_staff": False,
        "confidence": 0.95,
        "metadata": metadata
    }

print("Starting live traffic simulation for dashboard...")
visitor_count = 0
while True:
    visitor_count += 1
    vid = f"VIS_LIVE_{visitor_count}"
    
    # Simulate a visitor entering
    post_event(generate_event("ENTRY", vid, {"session_seq": 1}))
    time.sleep(2)
    
    # Simulate browsing
    post_event(generate_event("ZONE_ENTER", vid, {"session_seq": 2}))
    time.sleep(3)
    
    # Some visitors buy, some abandon
    if visitor_count % 3 != 0:
        post_event(generate_event("BILLING_QUEUE_JOIN", vid, {"session_seq": 3, "queue_depth": visitor_count % 5}))
        time.sleep(2)
        # Convert (no abandon event)
    else:
        # Abandoned
        post_event(generate_event("BILLING_QUEUE_ABANDON", vid, {"session_seq": 3}))
        time.sleep(1)
        
    post_event(generate_event("EXIT", vid, {"session_seq": 4}))
    
    time.sleep(2)
