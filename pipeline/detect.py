import cv2
import argparse
import uuid
import datetime
from ultralytics import YOLO
from .tracker import PersonTracker
from .emit import emit_events

def main(video_path):
    model = YOLO("yolov8n.pt")
    tracker = PersonTracker()
    cap = cv2.VideoCapture(video_path)
    
    STORE_ID = "STORE_BLR_002"
    CAMERA_ID = "CAM_ENTRY_01"
    
    frame_count = 0
    event_buffer = []
    active_visitors = set()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # Process every 5th frame to maintain speed
        if frame_count % 5 != 0:
            continue
            
        results = model(frame, classes=[0], verbose=False)
        
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                w = x2 - x1
                h = y2 - y1
                detections.append(([x1, y1, w, h], conf, 0))
                
        tracks = tracker.update(detections, frame)
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        for track_id, (x1, y1, x2, y2) in tracks:
            visitor_id = f"VIS_{track_id}"
            
            # Simplified logic for ENTRY detection
            if visitor_id not in active_visitors:
                active_visitors.add(visitor_id)
                event = {
                    "event_id": str(uuid.uuid4()),
                    "store_id": STORE_ID,
                    "camera_id": CAMERA_ID,
                    "visitor_id": visitor_id,
                    "event_type": "ENTRY",
                    "timestamp": timestamp,
                    "zone_id": None,
                    "dwell_ms": 0,
                    "is_staff": False,
                    "confidence": 0.9,
                    "metadata": {"session_seq": 1}
                }
                event_buffer.append(event)
                
            # Simulate zone dwell every 150 frames
            if frame_count % 150 == 0:
                event = {
                    "event_id": str(uuid.uuid4()),
                    "store_id": STORE_ID,
                    "camera_id": CAMERA_ID,
                    "visitor_id": visitor_id,
                    "event_type": "ZONE_DWELL",
                    "timestamp": timestamp,
                    "zone_id": "SKINCARE",
                    "dwell_ms": 5000,
                    "is_staff": False,
                    "confidence": 0.85,
                    "metadata": {"session_seq": 2, "sku_zone": "MOISTURISER"}
                }
                event_buffer.append(event)
                
        if len(event_buffer) >= 10:
            emit_events(event_buffer)
            event_buffer = []
            
    if event_buffer:
        emit_events(event_buffer)
        
    cap.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    args = parser.parse_args()
    main(args.video)
