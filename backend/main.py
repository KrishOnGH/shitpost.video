from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings
import subprocess
import unidecode
import pyttsx3
import random
import shutil
import wave
import time
import cv2
import os

IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_PATH})

# Get post, background footage choice, and directory location for temporary storage
script_dir = os.path.dirname(os.path.abspath(__file__))
footage_type = 'minecraft'
posttext = input("What is the post? ")
posttext = unidecode.unidecode(posttext)

# Create folder for temporary files
if not os.path.exists(os.path.join(script_dir, 'temporary')):
    os.makedirs(os.path.join(script_dir, 'temporary'))

# Audio generation function
def generateAudio(posttext):
    # Init
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', int(rate * 0.75))
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    # Save audio to file temporarily
    temp_audio_filename = os.path.join(os.path.join(script_dir, 'temporary'), "temp_audio.mp3")
    engine.save_to_file(posttext, temp_audio_filename)
    engine.runAndWait()

    # Get audio duration
    with wave.open(temp_audio_filename, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        audio_duration = frames / float(rate)

    # Generate subtitle data
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

    max_length = 10
    lines = split_text(posttext, max_length)
    subtitle_data = []
    duration_per_line = audio_duration / len(lines)
    
    for i, line in enumerate(lines):
        start_time = i * duration_per_line
        end_time = (i + 1) * duration_per_line
        subtitle_data.append(((start_time, end_time), line))

    subtitle_file = os.path.join(os.path.join(script_dir, 'temporary'), "subtitles.srt")
    with open(subtitle_file, 'w', encoding='utf-8') as f:
        for i, ((start, end), text) in enumerate(subtitle_data):
            f.write(f"{i + 1}\n")
            f.write(f"{time.strftime('%H:%M:%S', time.gmtime(start))},{int((start % 1) * 1000)} --> {time.strftime('%H:%M:%S', time.gmtime(end))},{int((end % 1) * 1000)}\n")
            f.write(f"{text}\n\n")

    return temp_audio_filename, audio_duration, subtitle_file

# Video generation function
def generateBackgroundVideo(duration):
    # Get video
    relative_video_path = f'backgroundfootage/{footage_type}.mp4'
    video_path = os.path.join(script_dir, relative_video_path)

    # Get duration of video
    data = cv2.VideoCapture(video_path)
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv2.CAP_PROP_FPS)
    seconds = round(frames / fps)

    # Clip random section of video
    if footage_type == "subway surfers":
        start = random.randint(30, seconds - 360)
    else:
        start = random.randint(30, seconds - 180)
    end = start + duration + 3

    clippedVideo = VideoFileClip(video_path).subclip(start, end)

    # Resize video to mobile dimensions
    original_width, original_height = clippedVideo.size
    new_width = (original_height / 1920) * 1080

    x1 = (original_width - new_width) // 2
    x2 = x1 + new_width
    y1 = 0
    y2 = original_height

    backgroundVideo = clippedVideo.crop(x1=x1, x2=x2, y1=y1, y2=y2)
    return backgroundVideo

# Add subtitles
def addSubtitles(background_video, subtitle_file):
    def make_textclip(txt):
        # Create a TextClip with word wrapping and center alignment
        txt_clip = TextClip(txt, fontsize=128, font='Arial', color='white', stroke_color='black', stroke_width=5,
                            size=background_video.size, method='caption', align='center')
        return txt_clip

    subtitles_clip = SubtitlesClip(subtitle_file, make_textclip)

    # Center the subtitles both vertically and horizontally
    final_clip = CompositeVideoClip([background_video, subtitles_clip.set_position(('center', 'center'))])
    
    return final_clip

# Save video
def save(video, audio):
    output_video = "video.mp4"

    ffmpeg_command = [
        "ffmpeg",
        "-i", video,
        "-i", audio,
        "-vf", "scale=trunc(iw/2)*2:ih,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "160k",
        "-movflags", "+faststart",
        "-strict", "experimental",
        "-map", "0:v:0",
        "-map", "1:a:0",
        output_video
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

# Main script execution
script_start_time = time.time()

try:
    # Generate audio and subtitles in SRT format
    start_time = time.time()
    audio_filename, audio_duration, subtitle_file = generateAudio(posttext)
    print("Audio and subtitle data created. Time taken: {:.2f}s".format(time.time() - start_time))

    # Generate background video
    start_time = time.time()
    background_video = generateBackgroundVideo(audio_duration)
    print("Video file created. Time taken: {:.2f}s".format(time.time() - start_time))

    # Add subtitles to background video
    start_time = time.time()
    subtitled_video = addSubtitles(background_video, subtitle_file)
    print("Subtitles added. Time taken: {:.2f}s".format(time.time() - start_time))

    # Load audio and add to video
    start_time = time.time()
    audio = AudioFileClip(audio_filename)
    final_video = subtitled_video
    final_video.set_audio(audio)
    audio.close()
    print("Audio added. Time taken: {:.2f}s".format(time.time() - start_time))

    # Write final video
    start_time = time.time()
    final_video.write_videofile('temporary/converting.mp4', logger=None)
    save(os.path.join(script_dir, 'temporary/converting.mp4'), audio_filename)
    print("Final video compiled. Time taken: {:.2f}s".format(time.time() - start_time))

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Clean up temporary files
    shutil.rmtree(os.path.join(script_dir, 'temporary'), ignore_errors=True)

print("Total time taken: {:.2f}s".format(time.time() - script_start_time))