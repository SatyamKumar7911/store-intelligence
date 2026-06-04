from .database import get_db

def get_metrics(store_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Today's unique visitors (exclude staff)
        cursor.execute('''
            SELECT COUNT(DISTINCT visitor_id) 
            FROM events 
            WHERE store_id = ? AND is_staff = 0 AND date(timestamp) = date('now')
        ''', (store_id,))
        unique_visitors = cursor.fetchone()[0] or 0
        
        # We assume POS data ingestion for conversion rate, 
        # but lacking that in real-time, we mock or calculate from billing events.
        cursor.execute('''
            SELECT COUNT(DISTINCT visitor_id)
            FROM events
            WHERE store_id = ? AND is_staff = 0 AND date(timestamp) = date('now')
            AND event_type = 'BILLING_QUEUE_JOIN'
        ''', (store_id,))
        buyers = cursor.fetchone()[0] or 0
        conversion_rate = (buyers / unique_visitors) * 100 if unique_visitors > 0 else 0
        
        # Avg dwell per zone
        cursor.execute('''
            SELECT zone_id, AVG(dwell_ms) as avg_dwell
            FROM events
            WHERE store_id = ? AND event_type = 'ZONE_DWELL' AND is_staff = 0
            GROUP BY zone_id
        ''', (store_id,))
        dwell_data = {row['zone_id']: row['avg_dwell'] for row in cursor.fetchall()}
        
        # Queue depth (latest event)
        cursor.execute('''
            SELECT json_extract(metadata, '$.queue_depth') as queue_depth
            FROM events
            WHERE store_id = ? AND event_type = 'BILLING_QUEUE_JOIN'
            ORDER BY timestamp DESC LIMIT 1
        ''', (store_id,))
        queue_row = cursor.fetchone()
        queue_depth = queue_row[0] if queue_row and queue_row[0] is not None else 0
        
        # Abandonment rate
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN event_type = 'BILLING_QUEUE_ABANDON' THEN 1 ELSE 0 END) * 100.0 /
                COUNT(DISTINCT visitor_id)
            FROM events
            WHERE store_id = ? AND event_type IN ('BILLING_QUEUE_JOIN', 'BILLING_QUEUE_ABANDON')
        ''', (store_id,))
        abandon_row = cursor.fetchone()
        abandonment_rate = abandon_row[0] if abandon_row and abandon_row[0] is not None else 0
        
        return {
            "unique_visitors": unique_visitors,
            "conversion_rate": round(conversion_rate, 2),
            "avg_dwell_per_zone": dwell_data,
            "queue_depth": queue_depth,
            "abandonment_rate": round(abandonment_rate, 2)
        }

def get_heatmap(store_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Fetch zone visit frequency and avg dwell
        cursor.execute('''
            SELECT zone_id, COUNT(DISTINCT visitor_id) as visits, AVG(dwell_ms) as avg_dwell
            FROM events
            WHERE store_id = ? AND zone_id IS NOT NULL AND is_staff = 0
            GROUP BY zone_id
        ''')
        zones = cursor.fetchall()
        
        cursor.execute('''
            SELECT COUNT(DISTINCT visitor_id) FROM events WHERE store_id = ?
        ''', (store_id,))
        session_count = cursor.fetchone()[0] or 0
        
        heatmap_data = {}
        for row in zones:
            visits = row['visits']
            # Normalised 0-100 logic: visits relative to total sessions
            intensity = (visits / session_count * 100) if session_count > 0 else 0
            heatmap_data[row['zone_id']] = {
                "intensity": min(100, round(intensity, 2)),
                "visits": visits,
                "avg_dwell_ms": row['avg_dwell'] or 0
            }
        
        return {
            "heatmap": heatmap_data,
            "data_confidence": session_count >= 20
        }
