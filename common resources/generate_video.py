from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings
from faster_whisper import WhisperModel
import pandas as pd
import pyttsx3
import random
import time
import wave
import cv2
import csv
import os

IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_PATH})

# Get post, background footage choice, and directory location for temporary storage
script_dir = os.path.dirname(os.path.abspath(__file__))

# Generate SRT file
def generateSRT(input_audio, username):
    def transcribe(audio):
        model = WhisperModel("base")
        segments, info = model.transcribe(audio, vad_filter=False, vad_parameters=dict(min_silence_duration_ms=100))
        language = info[0]
        segments = list(segments)
        return language, segments

    def formattedtime(seconds):
        final_time = time.strftime("%H:%M:%S", time.gmtime(float(seconds)))
        milliseconds = seconds.split('.')[1].ljust(3, '0')
        return f"{final_time},{milliseconds}"

    def writetocsv(segments, output_folder):
        output = f"{output_folder}/output.csv"
        cols = ["start", "end", "text"]
        data = []
        for segment in segments:
            start = formattedtime(format(segment.start, ".3f"))
            end = formattedtime(format(segment.end, ".3f"))
            data.append([start, end, segment.text])
        df = pd.DataFrame(data, columns=cols)
        df.to_csv(output, index=False)
        return output

    def split_text(text, max_words_per_line=2):
        words = text.split()
        lines = [' '.join(words[i:i + max_words_per_line]) for i in range(0, len(words), max_words_per_line)]
        return lines

    def calculate_time_per_character(start, end, text):
        start_seconds = sum(float(x) * 60 ** i for i, x in enumerate(reversed(start.replace(',', '.').split(':'))))
        end_seconds = sum(float(x) * 60 ** i for i, x in enumerate(reversed(end.replace(',', '.').split(':'))))
        total_duration = end_seconds - start_seconds
        total_characters = len(text)
        return total_duration / total_characters

    def split_time(start, time_per_character, text_lines):
        start_seconds = sum(float(x) * 60 ** i for i, x in enumerate(reversed(start.replace(',', '.').split(':'))))
        times = [start_seconds]

        for line in text_lines:
            duration = len(line) * time_per_character
            times.append(times[-1] + duration)
        
        formatted_times = [formattedtime(format(t, ".3f")) for t in times]
        return [(formatted_times[i], formatted_times[i + 1]) for i in range(len(formatted_times) - 1)]

    def generatesrt(csv_file, output_folder):
        rows = []
        count = 0
        with open(csv_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                lines = split_text(row['text'])
                time_per_character = calculate_time_per_character(row['start'], row['end'], row['text'])
                timings = split_time(row['start'], time_per_character, lines)
                
                for line, (start, end) in zip(lines, timings):
                    count += 1
                    txt = f"{count}\n{start} --> {end}\n{line.strip()}\n\n"
                    rows.append(txt)
        
        srt_output = f"{output_folder}/output.srt"
        with open(srt_output, "w") as srt_file:
            for row in rows:
                srt_file.write(row)
        return srt_output

    output_folder = f"temporary{username}/subtitles"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Step 1: Transcribe Audio
    language, segments = transcribe(audio=input_audio)
    
    # Step 2: Write to CSV
    csv_file = writetocsv(segments, output_folder)
    
    # Step 3: Generate SRT from CSV
    generatesrt(csv_file, output_folder)
    
    return f"{output_folder}/output.srt"

# Audio generation function
def generateAudio(posttext, username, temp_dir):
    # Generate and temporarily save audio
    temp_audio_filename = os.path.join(temp_dir, "temp_audio.mp3")
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', int(rate)*.9)
    rate = engine.getProperty('rate')
    engine.setProperty('volume', int(engine.getProperty('volume'))*0.75)

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    engine.save_to_file(posttext, temp_audio_filename)
    engine.runAndWait()

    # Get audio duration
    with wave.open(temp_audio_filename, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        audio_duration = frames / float(rate)
    
    # Generate subtitle data
    subtitle_file = generateSRT(temp_audio_filename, username)

    return temp_audio_filename, audio_duration, subtitle_file

# Video generation function
def generateBackgroundVideo(duration, footage_type):
    # Get video
    relative_video_path = f'backgroundfootage/{footage_type}{random.randint(1, 5)}.mp4'
    video_path = os.path.join(script_dir, relative_video_path)

    # Get duration of video
    data = cv2.VideoCapture(video_path)
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv2.CAP_PROP_FPS)
    seconds = round(frames / fps)

    # Clip random section of video
    start = random.randint(1, seconds - round(duration) - 2)
    end = start + duration + 2

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
def addSubtitles(background_video, subtitle_file, color):
    def make_textclip(txt):
        stroke = 'black'
        if color == 'purple':
            stroke == 'white'

        # Create a TextClip with word wrapping and center alignment
        txt_clip = TextClip(txt, fontsize=86, font='Arial', color=color, stroke_color=stroke, stroke_width=3,
                            size=background_video.size, method='caption', align='center')
        return txt_clip

    subtitles_clip = SubtitlesClip(subtitle_file, make_textclip)

    # Center the subtitles both vertically and horizontally
    final_clip = CompositeVideoClip([background_video, subtitles_clip.set_position(('center', 'center'))])
    
    return final_clip