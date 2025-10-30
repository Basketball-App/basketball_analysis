import cv2
import numpy as np

class PassInterceptionDrawer:
    def __init__(self):
        pass

    def get_stats(self, passes, interceptions):
        team1_passes = []
        team2_passes = []
        team1_interceptions = []
        team2_interceptions = []

        for frame_num, (pass_frame, interception_frame) in enumerate(zip(passes, interceptions)):
            if pass_frame == 1:
                team1_passes.append(frame_num)
            elif pass_frame == 2:
                team2_passes.append(frame_num)
                
            if interception_frame == 1:
                team1_interceptions.append(frame_num)
            elif interception_frame == 2:
                team2_interceptions.append(frame_num)
                
        return len(team1_passes), len(team2_passes), len(team1_interceptions), len(team2_interceptions)

    def draw(self, video_frames, passes, interceptions):
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            if frame_num == 0:
                continue
            
            frame_drawn = self.draw_frame(frame, frame_num, passes, interceptions)
            output_video_frames.append(frame_drawn)
        return output_video_frames
    
    def draw_frame(self, frame, frame_num, passes, interceptions):
        font_scale = 0.7
        font_thickness = 2
        font = cv2.FONT_HERSHEY_SIMPLEX
        padding = 10
        line_spacing = 10
        margin = 20

        # Get stats until current frame
        passes_till_frame = passes[:frame_num + 1]
        interceptions_till_frame = interceptions[:frame_num + 1]

        team1_passes, team2_passes, team1_interceptions, team2_interceptions = self.get_stats(
            passes_till_frame,
            interceptions_till_frame
        )

        line1 = f"Team 1 - Passes: {team1_passes} | Interceptions: {team1_interceptions}"
        line2 = f"Team 2 - Passes: {team2_passes} | Interceptions: {team2_interceptions}"

        # Measure text size
        (w1, h1), _ = cv2.getTextSize(line1, font, font_scale, font_thickness)
        (w2, h2), _ = cv2.getTextSize(line2, font, font_scale, font_thickness)
        text_width = max(w1, w2)
        text_height = h1 + h2 + line_spacing

        # Position aligned with Ball Control (bottom left)
        frame_h, frame_w = frame.shape[:2]
        x1 = margin
        y1 = frame_h - text_height - 2 * padding - margin
        x2 = x1 + text_width + 2 * padding
        y2 = frame_h - margin

        # Draw translucent white rectangle
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (178, 186, 187), -1)
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Text positions
        text_x = x1 + padding
        text_y1 = y1 + padding + h1
        text_y2 = text_y1 + h2 + line_spacing

        cv2.putText(frame, line1, (text_x, text_y1), font, font_scale, (255, 240, 250), font_thickness)
        cv2.putText(frame, line2, (text_x, text_y2), font, font_scale, (123, 20, 162), font_thickness)

        return frame
