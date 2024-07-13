from moviepy.editor import VideoFileClip
import os
import random
import cv2
import datetime

relative_video_path = './minecraftvideo.mp4'

script_dir = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(script_dir, relative_video_path)
data = cv2.VideoCapture(video_path)

frames = data.get(cv2.CAP_PROP_FRAME_COUNT) 
fps = data.get(cv2.CAP_PROP_FPS)
seconds = round(frames / fps) 
video_time = datetime.timedelta(seconds=seconds) 

start = random.randint(10, seconds-300)
end = start + 30
clip1 = VideoFileClip("minecraftvideo.mp4").subclip(start, end)

output_path = os.path.join(script_dir, 'clippedvideo.mp4')
clip1.write_videofile(output_path, codec="libx264")