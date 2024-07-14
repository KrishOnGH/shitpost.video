from moviepy.editor import VideoFileClip, AudioFileClip
import pyttsx3
import wave
import os
import random
import cv2

script_dir = os.path.dirname(os.path.abspath(__file__))
posttext = input("What is the post? ")

# Audio generation function
def generateAudio(posttext):
    # Init
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', int(rate * 0.75))

    # Temporarily save audio to file
    temp_audio_filename = "temp_audio.wav"
    engine.save_to_file(posttext, temp_audio_filename)
    engine.runAndWait()
    
    # Get audio duration
    with wave.open(temp_audio_filename, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        audio_duration = frames / float(rate)

    # Generate SRT file
    def format_time(seconds):
        millis = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"
    def split_text(text, max_length):
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 > max_length:
                lines.append(current_line.strip())
                current_line = word
            else:
                current_line += " " + word
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    # Split words into lines
    lines = split_text(posttext, 30)
    num_lines = len(lines)
    duration_per_line = audio_duration / num_lines

    # Save SRT file
    srt_filename = "subtitles.srt"
    with open(srt_filename, 'w') as srt_file:
        for i, line in enumerate(lines):
            start_time = i * duration_per_line
            end_time = start_time + duration_per_line
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
            srt_file.write(f"{line}\n\n")

    # Return audio file path, audio duration, and SRT file path
    return temp_audio_filename, audio_duration, srt_filename

# Video generation function
def generateBackgroundVideo(duration):
    # Get Minecraft gameplay
    relative_video_path = './minecraftvideo.mp4'
    video_path = os.path.join(script_dir, relative_video_path)

    # Get duration of gameplay video
    data = cv2.VideoCapture(video_path)
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv2.CAP_PROP_FPS)
    seconds = round(frames / fps)

    # Clip random section of video
    start = random.randint(10, seconds - 300)
    end = start + duration + 3

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

# Stitch audio and video
audio_filename, audio_duration, srt_file = generateAudio(posttext)
backgroundVideo = generateBackgroundVideo(audio_duration)
audio = AudioFileClip(audio_filename)
video = backgroundVideo.set_audio(audio)

# Save
video_path = os.path.join(script_dir, 'video.mp4')
video.write_videofile(video_path, codec="libx264")

# Remove temporary files
os.remove(audio_filename)
os.remove(srt_file)