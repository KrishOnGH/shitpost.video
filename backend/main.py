
from generate_video import generateAudio, generateBackgroundVideo, addSubtitles
from flask import Flask, request, jsonify
from moviepy.editor import AudioFileClip
from unidecode import unidecode
from flask_cors import CORS
import subprocess
import tempfile
import shutil
import time
import uuid
import os

app = Flask(__name__)
CORS(app)

# Get post, background footage choice, and directory location for temporary storage
script_dir = os.path.dirname(os.path.abspath(__file__))

# Main script execution
script_start_time = time.time()

# Save video function
def save(video, audio):
    output_video = "video.mp4"

    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-nostats",
        "-loglevel", "panic",
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

@app.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.get_json()
    posttext = data.get('post')
    footage_type = data.get('footage_type')
    posttext = unidecode(posttext)

    temp_dir = tempfile.mkdtemp(prefix="tmp_video_", suffix=f"_{uuid.uuid4()}")

    # Create folder for temporary files
    if not os.path.exists(os.path.join(script_dir, 'temporary')):
        os.makedirs(os.path.join(script_dir, 'temporary'))

    try:
        # Generate audio and subtitles in SRT format
        audio_filename, audio_duration, subtitle_file = generateAudio(posttext)

        # Generate background video
        background_video = generateBackgroundVideo(audio_duration, footage_type)

        # Add subtitles to background video
        subtitled_video = addSubtitles(background_video, subtitle_file)

        # Load audio and add to video
        audio = AudioFileClip(audio_filename)
        final_video = subtitled_video
        final_video.set_audio(audio)
        audio.close()

        # Write final video
        final_video_path = os.path.join(script_dir, 'temporary', 'converting.mp4')
        final_video.write_videofile(final_video_path, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, logger=None)

        # Save the combined video with audio
        save(final_video_path, audio_filename)
        
        return jsonify({'path': final_video_path})

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        shutil.rmtree('temporary', ignore_errors=True)

if __name__ == '__main__':
    app.run(debug=True)