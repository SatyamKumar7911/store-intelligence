from .database import get_db
import datetime

def get_anomalies(store_id: str):
    anomalies = []
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Queue Spike
        cursor.execute('''
            SELECT json_extract(metadata, '$.queue_depth') as queue_depth
            FROM events
            WHERE store_id = ? AND event_type = 'BILLING_QUEUE_JOIN'
            ORDER BY timestamp DESC LIMIT 1
        ''', (store_id,))
        row = cursor.fetchone()
        queue_depth = row[0] if row and row[0] is not None else 0
        
        if queue_depth > 10:
            anomalies.append({
                "type": "BILLING_QUEUE_SPIKE",
                "severity": "CRITICAL",
                "description": f"Queue depth is {queue_depth}, which is unusually high.",
                "suggested_action": "Open a new billing counter immediately."
            })
        elif queue_depth > 5:
            anomalies.append({
                "type": "BILLING_QUEUE_SPIKE",
                "severity": "WARN",
                "description": f"Queue depth is {queue_depth}.",
                "suggested_action": "Monitor billing counters."
            })
            
        # 2. Dead Zone (No visits in 30 mins)
        # Mock logic checking last event timestamp per zone
        cursor.execute('''
            SELECT zone_id, MAX(timestamp) as last_seen
            FROM events
            WHERE store_id = ? AND zone_id IS NOT NULL
            GROUP BY zone_id
        ''', (store_id,))
        
        now = datetime.datetime.utcnow()
        for r in cursor.fetchall():
            zone = r['zone_id']
            last_seen_str = r['last_seen']
            # ISO format parsing
            if last_seen_str:
                # Basic iso parsing
                try:
                    last_seen = datetime.datetime.fromisoformat(last_seen_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    if (now - last_seen).total_seconds() > 1800:
                        anomalies.append({
                            "type": "DEAD_ZONE",
                            "severity": "INFO",
                            "description": f"Zone {zone} has had no visits in over 30 minutes.",
                            "suggested_action": "Check camera feed or store layout for blockage."
                        })
                except Exception:
                    pass
                    
    return {"anomalies": anomalies}
