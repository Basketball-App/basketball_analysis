import os
import argparse

from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from drawers import PlayerTracksDrawer, BallTracksDrawer, TeamBallControlDrawer, PassInterceptionDrawer, CourtKeypointDrawer, TacticalViewDrawer, SpeedAndDistanceDrawer
from team_jersey_assigner import TeamJerseyAssigner
from ball_acquisition import BallAcquisitionDetector
from pass_interception_detector import PassInterceptionDetector
from court_keypoint_detector import CourtKeypointDetector
from tactical_view_converter import TacticalViewConverter 
from speed_distance import SpeedAndDistanceCalculator

from configs import STUBS_DEFAULT_PATH, PLAYER_DETECTOR_PATH, BALL_DETECTOR_PATH, COURT_KEYPOINT_DETECTOR_PATH, OUTPUT_VIDEO_PATH, COURT_IMAGE_PATH

def parse_args():
    parser = argparse.ArgumentParser(description='Thesis')
    parser.add_argument('input_video', type=str, help='Path to input video file')
    parser.add_argument('--output_video', type=str, default=OUTPUT_VIDEO_PATH, 
                        help='Path to output video file')
    parser.add_argument('--stub_path', type=str, default=STUBS_DEFAULT_PATH,
                        help='Path to stub directory')
    return parser.parse_args()

def main():
    args = parse_args()

    video_frames = read_video(args.input_video) # Read video from a file

    player_tracker = PlayerTracker(PLAYER_DETECTOR_PATH) # Initialize the player tracker with the model path
    ball_tracker = BallTracker(BALL_DETECTOR_PATH) # Initialize the ball tracker with the model path 

    court_keypoint_detector = CourtKeypointDetector(COURT_KEYPOINT_DETECTOR_PATH) # Initialize the court keypoint detector with the model path
    
    player_tracks = player_tracker.get_object_tracks(video_frames, 
                                                     read_from_stub=True, 
                                                     stub_path= os.path.join(args.stub_path, "player_track_stubs.pkl")
                                                     ) # Get object tracks from the video frames
    
    ball_tracks = ball_tracker.get_object_tracks(video_frames,  
                                                 read_from_stub=True, 
                                                 stub_path= os.path.join(args.stub_path, "ball_track_stubs.pkl")
                                                 ) # Get object tracks from the video frames
    
    court_keypoints = court_keypoint_detector.get_court_keypoints(video_frames,
                                                                  read_from_stub=True, 
                                                                  stub_path= os.path.join(args.stub_path, "court_keypoint_stubs.pkl")
                                                                  ) # Get court keypoints from the video frames
    
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks) # Remove wrong detections from the ball tracks
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks) # Interpolate ball positions in the tracks

    team_jersey_assigner = TeamJerseyAssigner() # Initialize the team jersey assigner
    player_assignment = team_jersey_assigner.get_player_teams_across_frames(video_frames, 
                                                                       player_tracks, 
                                                                       read_from_stub=True, 
                                                                       stub_path= os.path.join(args.stub_path, "player_team_assigner_stubs.pkl")
                                                                       ) # Get player teams across frames
    
    ball_acquisition_detector = BallAcquisitionDetector() # Initialize the ball acquisition detector
    ball_acquisition = ball_acquisition_detector.detect_ball_possession(player_tracks, ball_tracks) # Detect ball possession

    pass_interception_detector = PassInterceptionDetector() # Initialize the pass interception detector
    passes = pass_interception_detector.detect_passes(ball_acquisition, player_assignment) # Detect passes
    interceptions = pass_interception_detector.detect_interceptions(ball_acquisition, player_assignment) # Detect interceptions

    tactical_view_converter = TacticalViewConverter(court_image_path=COURT_IMAGE_PATH) # Initialize the tactical view converter
    court_keypoints = tactical_view_converter.validate_keypoints(court_keypoints) # Validate the court keypoints
    tactical_player_positions = tactical_view_converter.transform_players_to_tactical_view(court_keypoints, player_tracks) # Transform player positions to tactical view

    speed_distance_calculator = SpeedAndDistanceCalculator(tactical_view_converter.width,
                                                           tactical_view_converter.height,
                                                           tactical_view_converter.actual_width_in_meters,
                                                           tactical_view_converter.actual_height_in_meters) # Initialize the speed and distance calculator
    
    player_distance = speed_distance_calculator.calculate_distance(tactical_player_positions) # Calculate player distances
    player_speed = speed_distance_calculator.calculate_speed(player_distance) # Calculate player speeds
    
    player_tracks_drawer = PlayerTracksDrawer() # Initialize the player tracks drawer with the player tracker
    ball_tracks_drawer = BallTracksDrawer() # Initialize the ball tracks drawer with the ball tracker
    team_ball_control_drawer = TeamBallControlDrawer() # Initialize the team ball control drawer
    pass_interception_detector = PassInterceptionDrawer() # Initialize the pass interception detector
    court_keypoints_drawer = CourtKeypointDrawer() # Initialize the court keypoints drawer
    tactical_view_drawer = TacticalViewDrawer() # Initialize the tactical view drawer
    speed_distance_drawer = SpeedAndDistanceDrawer() # Initialize the speed and distance drawer

    output_video_frames = player_tracks_drawer.draw(video_frames, player_tracks, player_assignment, ball_acquisition) # Draw the tracks on the video frames
    output_video_frames = ball_tracks_drawer.draw(output_video_frames, ball_tracks) # Draw the tracks on the video frames
    output_video_frames = team_ball_control_drawer.draw(output_video_frames, player_assignment, ball_acquisition) # Draw the team ball control on the video frames
    output_video_frames = pass_interception_detector.draw(output_video_frames, passes, interceptions) # Draw the pass interceptions on the video frames
    output_video_frames = court_keypoints_drawer.draw(output_video_frames, court_keypoints) # Draw the court keypoints on the video frames
    output_video_frames = tactical_view_drawer.draw(output_video_frames,
                                                    tactical_view_converter.court_image_path,
                                                    tactical_view_converter.width,
                                                    tactical_view_converter.height, 
                                                    tactical_view_converter.key_points,
                                                    tactical_player_positions,
                                                    player_assignment,
                                                    ball_acquisition                                                   
                                                    )
    output_video_frames = speed_distance_drawer.draw(output_video_frames,
                                                        player_tracks, 
                                                        player_distance, 
                                                        player_speed
                                                        ) # Draw the speed and distance on the video frames
    
    save_video(output_video_frames, args.output_video) # Save the output video frames to a file

if __name__ == "__main__":
    main()