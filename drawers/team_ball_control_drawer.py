import cv2 
import numpy as np

class TeamBallControlDrawer:
    def __init__(self):
        pass

    def get_team_ball_control(self,player_assignment,ball_acquisition):
        team_ball_control = []
        for player_assignment_frame,ball_acquisition_frame in zip(player_assignment,ball_acquisition):
            if ball_acquisition_frame == -1:
                team_ball_control.append(-1)
                continue
            if ball_acquisition_frame not in player_assignment_frame:
                team_ball_control.append(-1)
                continue
            if player_assignment_frame[ball_acquisition_frame] == 1:
                team_ball_control.append(1)
            else:
                team_ball_control.append(2)

        team_ball_control= np.array(team_ball_control) 
        return team_ball_control

    def draw(self,video_frames,player_assignment,ball_acquisition):        
        team_ball_control = self.get_team_ball_control(player_assignment,ball_acquisition)

        output_video_frames= []

        for frame_num, frame in enumerate(video_frames):
            frame_drawn = self.draw_frame(frame,frame_num,team_ball_control)
            output_video_frames.append(frame_drawn)
        return output_video_frames
    
    def draw_frame(self, frame, frame_num, team_ball_control):

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        padding = 10  # Padding interno dentro del rectángulo
        line_spacing = 10  # Espacio entre líneas

        # Calcular control de balón
        team_ball_control_till_frame = team_ball_control[:frame_num + 1]
        team_1_frames = np.sum(team_ball_control_till_frame == 1)
        team_2_frames = np.sum(team_ball_control_till_frame == 2)
        total_frames = len(team_ball_control_till_frame)

        team_1_pct = 100 * team_1_frames / total_frames if total_frames > 0 else 0
        team_2_pct = 100 * team_2_frames / total_frames if total_frames > 0 else 0

        # Textos a dibujar
        text1 = f"Team 1 Ball Control: {team_1_pct:.2f}%"
        text2 = f"Team 2 Ball Control: {team_2_pct:.2f}%"

        # Obtener tamaños de texto
        (w1, h1), _ = cv2.getTextSize(text1, font, font_scale, font_thickness)
        (w2, h2), _ = cv2.getTextSize(text2, font, font_scale, font_thickness)

        text_width = max(w1, w2)
        text_height = h1 + h2 + line_spacing

        # Posicionar en la esquina inferior derecha con margen
        frame_h, frame_w = frame.shape[:2]
        margin = 20

        x1 = frame_w - text_width - 2 * padding - margin
        y1 = frame_h - text_height - 2 * padding - margin
        x2 = frame_w - margin
        y2 = frame_h - margin

        # Dibujar rectángulo gris translúcido
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (178, 186, 187), -1)
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Posición del texto dentro del rectángulo
        text_x = x1 + padding
        text_y1 = y1 + padding + h1
        text_y2 = text_y1 + h2 + line_spacing

        # Dibujar texto
        cv2.putText(frame, text1, (text_x, text_y1), font, font_scale, (255, 240, 250), font_thickness)
        cv2.putText(frame, text2, (text_x, text_y2), font, font_scale, (123, 20, 162), font_thickness)

        return frame