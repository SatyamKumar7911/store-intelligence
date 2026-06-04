import requests
import json
import logging

API_URL = "http://localhost:8000/events/ingest"

def emit_events(events: list):
    if not events:
        return
    try:
        response = requests.post(API_URL, json=events, timeout=5)
        if response.status_code not in [200, 207]:
            logging.error(f"Failed to emit events: {response.text}")
    except Exception as e:
        logging.error(f"Error connecting to API: {e}")
