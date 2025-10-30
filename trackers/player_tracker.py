from ultralytics import YOLO
import supervision as sv
import sys
sys.path.append("../")
from utils import save_stub, read_stub

class PlayerTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()

    def detect_frames(self, frames): 
        batch_size = 20
        detections = []

        for i in range(0, len(frames), batch_size):
            batch_frames = frames[i:i + batch_size]
            batch_detections = self.model.predict(batch_frames, conf=0.5, verbose=False)
            detections+= batch_detections
        return detections
    
    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):

        tracks = read_stub(read_from_stub, stub_path) # Read tracks from a stub if specified
        if tracks is not None:
            if len(tracks) == len(frames): # Check if the number of tracks matches the number of frames
                return tracks

        detections = self.detect_frames(frames)
        tracks = []

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v: k for k, v in cls_names.items()} # Invert the dictionary to get class names from IDs

            detection_supervision = sv.Detections.from_ultralytics(detection) # Convert to supervision format

            detection_with_tracks = self.tracker.update_with_detections(detection_supervision) # Update tracker with detections

            tracks.append({}) # Initialize empty dictionary for each frame

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist() # Get bounding box coordinates
                cls_id = frame_detection[3] 
                track_id = frame_detection[4]

                if cls_id == cls_names_inv["Player"]: # Check if the detected object is a player
                    tracks[frame_num][track_id] = {"bbox": bbox} # Store bounding box coordinates

        save_stub(stub_path, tracks) # Save tracks to a stub if specified
        return tracks