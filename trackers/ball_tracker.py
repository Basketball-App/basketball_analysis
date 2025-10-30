from ultralytics import YOLO
import sys
import numpy as np
import supervision as sv
import pandas as pd
sys.path.append("../")
from utils import save_stub, read_stub

class BallTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_frames(self, frames): 
        batch_size = 20
        detections = []

        for i in range(0, len(frames), batch_size):
            batch_frames = frames[i:i + batch_size]
            batch_detections = self.model.predict(batch_frames, conf=0.5)
            detections+= batch_detections
        return detections
    
    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):

        tracks = read_stub(read_from_stub, stub_path) # Read tracks from a stub if specified
        if tracks is not None:
            if len(tracks) == len(frames): # Check if the number of tracks matches the number of frames
                return tracks
            
        detections = self.detect_frames(frames) # Detect objects in the frames
        tracks = []

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v: k for k, v in cls_names.items()}

            detection_supervision = sv.Detections.from_ultralytics(detection)
            tracks.append({})

            chosen_bbox = None # Initialize chosen bounding box
            max_confidence = 0 # Initialize maximum confidence

            for frame_detection in detection_supervision:
                bbox = frame_detection[0].tolist() # Get bounding box coordinates
                cls_id = frame_detection[3] # Get class ID
                confidence = frame_detection[2] # Get confidence score

                if cls_id == cls_names_inv['Ball']: # Check if the detected object is a ball
                    if max_confidence < confidence: # Check if the current detection has a higher confidence
                        chosen_bbox = bbox # Store the bounding box of the chosen detection
                        max_confidence = confidence # Update maximum confidence

            if chosen_bbox is not None:
                tracks[frame_num][1] = {"bbox": chosen_bbox} # Store the bounding box coordinates of the chosen detection
            
        save_stub(stub_path, tracks) # Save tracks to a stub if specified
        return tracks

    def remove_wrong_detections(self, ball_positions):
        max_distance = 25
        last_frame_detected = -1

        for i in range(len(ball_positions)):
            current_bbox = ball_positions[i].get(1, {}).get("bbox", [])

            if len(current_bbox) == 0:
                continue

            if last_frame_detected == -1:
                last_frame_detected = i
                continue

            last_correct_bbox = ball_positions[last_frame_detected].get(1, {}).get("bbox", [])
            frame_gap = i - last_frame_detected
            adjusted_max_distance = max_distance * frame_gap

            if np.linalg.norm(np.array(last_correct_bbox[:2]) - np.array(current_bbox[:2])) > adjusted_max_distance:
                ball_positions[i] = {}
            else:
                last_frame_detected = i

        return ball_positions
            
    def interpolate_ball_positions(self, ball_positions):
        ball_positions= [x.get(1, {}).get("bbox", []) for x in ball_positions]

        df_ball_positions = pd.DataFrame(ball_positions, columns=["x1", "y1", "x2", "y2"])

        df_ball_positions = df_ball_positions.interpolate()
        df_ball_positions = df_ball_positions.bfill()

        ball_positions = [{1:{"bbox": x}} for x in df_ball_positions.to_numpy().tolist()]

        return ball_positions