## Basketball Analysis

End-to-end basketball video analysis pipeline that detects and tracks players and the ball, infers team possession, detects passes and interceptions, estimates court keypoints, converts to a tactical top-down view, computes player speed and distance, and renders all overlays into an output video.

### Key Features
- Player detection and multi-frame tracking
- Ball detection and tracking with interpolation and cleanup
- Team jersey color assignment for team affiliation
- Ball possession detection across frames
- Pass and interception detection
- Court keypoint detection on broadcast view
- Tactical view conversion (homography) to a top-down court
- Speed and distance calculation per player in meters/second and meters
- Rich overlays drawn into an annotated output video

### Repository Layout
```
basketball_analysis/
  main.py                         # Entry point: runs the full pipeline
  configs/                        # Paths and constants
  models/                         # YOLO/torch .pt weights (only *_2.pt tracked)
  stubs/                          # Precomputed pickle stubs for demo runs
  input_videos/                   # Input videos (only video_1..video_3 tracked)
  output_videos/                  # Generated videos (ignored by Git)
  drawers/                        # Frame overlay rendering components
  trackers/                       # Player and ball trackers
  court_keypoint_detector/        # Court keypoint model wrapper
  team_jersey_assigner/           # Team color clustering/assignment
  ball_acquisition/               # Ball possession detector
  pass_interception_detector/     # Passes and interceptions
  tactical_view_converter/        # Broadcast→tactical transformation
  speed_distance/                 # Speed and distance calculator
  images/                         # Court image (e.g., basketball_court.png)
  utils/                          # Video IO and helpers
  .gitignore                      # Keeps repo size sane
  .gitattributes                  # Git LFS for large model files
```

### Requirements
This project uses PyTorch/YOLO-based models and OpenCV. A typical environment includes:
- Python 3.9+ (3.11 is fine)
- PyTorch with CUDA (optional but recommended)
- OpenCV, NumPy, SciPy, scikit-learn (color clustering), and other standard libs

If you have a `requirements.txt`, install with:
```bash
pip install -r requirements.txt
```
Otherwise, minimally:
```bash
pip install opencv-python numpy scipy scikit-learn
# plus your chosen torch/torchvision build
```

### Models
Place model weights under `models/`. By default, `configs/configs.py` points to:
- `models/player_detector_2.pt`
- `models/ball_detector_2.pt`
- `models/court_keypoints_detector_2.pt`

Only files ending with `_2.pt` are tracked in Git (others are ignored). For different filenames, update the constants in `configs/configs.py`.

### Stubs (Demo Mode)
For quick demos without running heavy inference, the pipeline reads precomputed results from `stubs/`:
- `player_track_stubs.pkl`
- `ball_track_stubs.pkl`
- `court_keypoint_stubs.pkl`
- `player_team_assigner_stubs.pkl`

You can control the stubs directory with `--stub_path`. The current `main.py` runs with `read_from_stub=True` so everything will work out-of-the-box using these files.

### Input and Output
- Put your input video into `input_videos/` (only `video_1.mp4` – `video_3.mp4` are tracked by Git).
- The rendered video is written to `output_videos/output_video.avi` by default.

### How It Works (High-Level Pipeline)
1. Read frames from the input video (`utils.read_video`).
2. Detect and track players and the ball (`trackers.PlayerTracker`, `trackers.BallTracker`).
3. Detect court keypoints (`court_keypoint_detector.CourtKeypointDetector`).
4. Assign players to teams by jersey colors (`team_jersey_assigner.TeamJerseyAssigner`).
5. Detect ball possession over time (`ball_acquisition.BallAcquisitionDetector`).
6. Detect passes and interceptions (`pass_interception_detector.PassInterceptionDetector`).
7. Validate keypoints and convert to a tactical top-down view (`tactical_view_converter.TacticalViewConverter`).
8. Compute per-player distance and speed in real-world units (`speed_distance.SpeedAndDistanceCalculator`).
9. Render overlays for tracks, possession, passes, keypoints, tactical view, and speed/distance (`drawers/*`).
10. Write the annotated video to disk (`utils.save_video`).

### Configuration
Key paths are centralized in `configs/configs.py`:
```python
STUBS_DEFAULT_PATH
PLAYER_DETECTOR_PATH
BALL_DETECTOR_PATH
COURT_KEYPOINT_DETECTOR_PATH
OUTPUT_VIDEO_PATH
COURT_IMAGE_PATH
```
Adjust these if you relocate models, stubs, images, or want a different output filename.

### Quickstart
From the `basketball_analysis` folder:
```bash
python main.py input_videos/video_1.mp4 \
  --output_video output_videos/output_video.avi \
  --stub_path stubs
```

To run without stubs, update the relevant calls in `main.py` to set `read_from_stub=False` and ensure the model paths in `configs/configs.py` point to valid `.pt` files.

### Git and Large Files
This repo is set up to avoid committing bulky artifacts:
- `models/*` is ignored except for files ending in `_2.pt` (tracked; consider Git LFS for these).
- `input_videos/*` is ignored except the first three videos.
- `output_videos/` and `training/` are ignored entirely.
- `stubs/` contents are ignored except for an empty `stubs/.gitkeep` to keep the folder.

If using Git LFS, ensure it is installed and initialized:
```bash
git lfs install
git lfs track "models/*_2.pt"
git add .gitattributes
```

### Notes
- The tactical view requires a court image at `images/basketball_court.png` (configurable).
- For best results without stubs, use broadcast footage with a steady camera.

### License
Add your preferred license here (e.g., MIT) if you plan to share this publicly.


