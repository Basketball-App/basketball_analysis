import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STUBS_DEFAULT_PATH = os.path.join(BASE_DIR, "..", "stubs")
PLAYER_DETECTOR_PATH = os.path.join(BASE_DIR, "..", "models", "player_detector_2.pt")
BALL_DETECTOR_PATH = os.path.join(BASE_DIR, "..", "models", "ball_detector_2.pt")
COURT_KEYPOINT_DETECTOR_PATH = os.path.join(BASE_DIR, "..", "models", "court_keypoints_detector_2.pt")
OUTPUT_VIDEO_PATH = os.path.join(BASE_DIR, "..", "output_videos", "output_video.avi")
COURT_IMAGE_PATH = os.path.join(BASE_DIR, "..", "images", "basketball_court.png")