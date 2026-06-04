from deep_sort_realtime.deepsort_tracker import DeepSort

class PersonTracker:
    def __init__(self):
        self.tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0)
        
    def update(self, detections, frame):
        # detections: list of ([left, top, w, h], confidence, class)
        tracks = self.tracker.update_tracks(detections, frame=frame)
        active_tracks = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            ltrb = track.to_ltrb()
            active_tracks.append((track_id, ltrb))
        return active_tracks
