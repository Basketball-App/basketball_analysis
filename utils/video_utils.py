import cv2
import os

def read_video(video_path):
    cap = cv2.VideoCapture(video_path) # Open the video file
    frames = [] # List to store frames

    while True:
        ret,frame = cap.read() # Read a frames one at a time
        if not ret:
            break # If no frame is returned, break the loop
        frames.append(frame) 

    return frames

def save_video(frames, output_path):
    if not os.path.exists(os.path.dirname(output_path)): # Check if the directory exists
        os.mkdir(os.path.dirname(output_path)) # Create the directory if it doesn't exist

    fourcc = cv2.VideoWriter_fourcc(*'XVID') # create a VideoWriter object with XVID codec
    output_video = cv2.VideoWriter(output_path, fourcc, 30.0, (frames[0].shape[1], frames[0].shape[0])) 

    for frame in frames: # Write each frame to the video file
        output_video.write(frame)
    output_video.release() # Release the VideoWriter object