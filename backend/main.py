from moviepy.editor import VideoFileClip, CompositeVideoClip
from pydub import AudioSegment
import os
import random
import cv2
import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
posttext = input("What is the post? ")

# Audio generation function
def generateAudio(posttext):
    # Generate and store audio from post
    temp_audio_path = os.path.join(script_dir, 'temp_post_audio.mp3')
    tts = gTTS(posttext)
    tts.save(temp_audio_path)
    
    audio = AudioSegment.from_file(temp_audio_path, format="mp3")
    audio_duration = len(audio) / 1000.0

    return audio, audio_duration

# Video generation function
def generateBackgroundVideo():
    # Get minecraft gameplay
    relative_video_path = './minecraftvideo.mp4'
    video_path = os.path.join(script_dir, relative_video_path)

    # Get duration of gameplay video
    data = cv2.VideoCapture(video_path)
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv2.CAP_PROP_FPS)

    seconds = round(frames / fps)
    video_time = datetime.timedelta(seconds=seconds)

    # Clip random section of video
    start = random.randint(10, seconds - 300)
    end = start + audio_duration + 3

    clippedVideo = VideoFileClip(video_path).subclip(start, end)

    # Resize video to mobile dimensions
    original_width, original_height = clippedVideo.size

    new_width = (original_height / 1920) * 1080
    new_height = original_height

    x1 = (original_width - new_width) // 2
    x2 = x1 + new_width
    y1 = 0
    y2 = original_height

    backgroundVideo = clippedVideo.crop(x1=x1, x2=x2, y1=y1, y2=y2)
    return backgroundVideo

# Run audio generation function
audio, audio_duration = generateAudio(posttext)

# Run video generation function
backgroundVideo = generateBackgroundVideo()

# Stitch and save final video
final_video = backgroundVideo.set_audio(audio)

video_path = os.path.join(script_dir, 'video.mp4')
final_video.write_videofile(video_path, codec="libx264")
