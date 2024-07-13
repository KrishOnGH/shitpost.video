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

start = random.randint(10, seconds - 300)
end = start + 30
clippedVideo = VideoFileClip(video_path).subclip(start, end)

original_width, original_height = clippedVideo.size
new_width = (original_height/1920) * 1080
new_height = original_height
x1 = (original_width - new_width) // 2
x2 = x1 + new_width
y1 = 0
y2 = original_height

backgroundVideo = clippedVideo.crop(x1=x1, x2=x2, y1=y1, y2=y2)
output_path = os.path.join(script_dir, 'clipped_video.mp4')
backgroundVideo.write_videofile(output_path, codec="libx264")