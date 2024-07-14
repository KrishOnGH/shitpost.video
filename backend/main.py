from moviepy.editor import VideoFileClip, AudioFileClip
import unidecode
import pyttsx3
import ffmpeg
import shutil
import random
import wave
import time
import cv2
import os

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

    # Temporarily save audio to file
    temp_audio_filename = "temporary/temp_audio.wav"
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
    srt_filename = "temporary/subtitles.srt"
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
def addSubtitles(input_video_path, srt_file):
    output_video_path = os.path.join(script_dir, 'temporary/video_with_subtitles.mp4')
    
    ffmpeg_path = r"C:\ffmpeg\ffmpeg.exe"
    
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(f"FFmpeg not found at {ffmpeg_path}. Please install FFmpeg or update the path.")

    try:
        # Input video
        input_video = ffmpeg.input(input_video_path)
        
        # Styling
        video_with_subs = input_video.filter(
            'subtitles', srt_file, 
            force_style='Fontname=Arial,Fontsize=16,PrimaryColour=&HFFFFFF&,SecondaryColour=&ffffff&,OutlineColour=&H000000&,BackColour=&H000000&,Alignment=10'
        )
        
        # Output video
        output = ffmpeg.output(video_with_subs, output_video_path, vcodec='libx264')
        output = output.overwrite_output()
        ffmpeg.run(output, cmd=ffmpeg_path, capture_stdout=True, capture_stderr=True)
        
    except ffmpeg.Error as e:
        print(f"FFmpeg error occurred: {e.stderr.decode()}")
        raise

    return output_video_path

# Generate audio
script_start_time = time.time()
start_time = time.time()
audio_filename, audio_duration, srt_file = generateAudio(posttext)
print("Audio and subtitle file created. Time taken: " + str(time.time() - start_time) + "s")

# Generate video and save temporarily
start_time = time.time()
backgroundVideo = generateBackgroundVideo(audio_duration)
temp_bg_video_path = os.path.join(script_dir, 'temporary/temp_bg_video.mp4')
backgroundVideo.write_videofile(temp_bg_video_path, codec="libx264", logger=None)
print("Video file created. Time taken: " + str(time.time() - start_time) + "s")

# Add subtitles to background video
start_time = time.time()
subtitled_video_path = addSubtitles(temp_bg_video_path, srt_file)
print("Subtitles added. Time taken: " + str(time.time() - start_time) + "s")

# Stitch audio into subtitled video
start_time = time.time()
final_video = VideoFileClip(subtitled_video_path)
audio = AudioFileClip(audio_filename)
final_video = final_video.set_audio(audio)
print("Audio added. Time taken: " + str(time.time() - start_time) + "s")

# Save the final video
start_time = time.time()
final_video_path = os.path.join(script_dir, 'video.mp4')
final_video.write_videofile(final_video_path, codec="libx264", logger=None)
print("Final video compiled. Time taken: " + str(time.time() - start_time) + "s" + " Total time taken: " + str(time.time() - script_start_time) + "s")

# Clean up temporary files
shutil.rmtree(os.path.join(script_dir, 'temporary'))