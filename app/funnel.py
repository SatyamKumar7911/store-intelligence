from .database import get_db

def get_funnel(store_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Funnel Definition: Entry -> Zone Visit -> Billing Queue -> Purchase (Mocked via POS join or similar)
        
        # 1. Entries
        cursor.execute('''
            SELECT COUNT(DISTINCT visitor_id) FROM events 
            WHERE store_id = ? AND event_type = 'ENTRY' AND is_staff = 0
        ''', (store_id,))
        entries = cursor.fetchone()[0] or 0
        
        # 2. Zone Visits
        cursor.execute('''
            SELECT COUNT(DISTINCT visitor_id) FROM events 
            WHERE store_id = ? AND event_type IN ('ZONE_ENTER', 'ZONE_DWELL') AND is_staff = 0
        ''', (store_id,))
        zone_visits = cursor.fetchone()[0] or 0
        
        # 3. Billing Queue
        cursor.execute('''
            SELECT COUNT(DISTINCT visitor_id) FROM events 
            WHERE store_id = ? AND event_type = 'BILLING_QUEUE_JOIN' AND is_staff = 0
        ''', (store_id,))
        billing = cursor.fetchone()[0] or 0
        
        # Drop-offs
        entry_to_zone_drop = ((entries - zone_visits) / entries * 100) if entries > 0 else 0
        zone_to_billing_drop = ((zone_visits - billing) / zone_visits * 100) if zone_visits > 0 else 0
        
        return {
            "stages": [
                {"stage": "Entry", "count": entries, "drop_off_pct": 0},
                {"stage": "Zone Visit", "count": zone_visits, "drop_off_pct": round(max(0, entry_to_zone_drop), 2)},
                {"stage": "Billing Queue", "count": billing, "drop_off_pct": round(max(0, zone_to_billing_drop), 2)}
            ]
        }
