from .utils import draw_triangle

class BallTracksDrawer:
    def __init__(self):
        self.ball_pointer_color = (255, 0, 0)

    def draw(self, video_frames, ball_tracks):
        output_video_frames = []

        for frame_num, frame in enumerate(video_frames):
            output_frames = frame.copy()

            ball_dict = ball_tracks[frame_num]

            for _,track in ball_dict.items():
                bbox = track["bbox"]

                if bbox is None:
                    continue

                output_frames = draw_triangle(frame, bbox, self.ball_pointer_color)

            output_video_frames.append(output_frames)

        return output_video_frames

