
from generate_video import generateAudio, generateBackgroundVideo, addSubtitles
from flask import Flask, request, send_file
from flask_socketio import SocketIO
from unidecode import unidecode
from flask_cors import CORS
import subprocess
import shutil
import time
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get post, background footage choice, and directory location for temporary storage
script_dir = os.path.dirname(os.path.abspath(__file__))

# Main script execution
script_start_time = time.time()

# Save video function
def save(video, audio, username):
    output_video = f"video{username}.mp4"

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

def emit_progress(username, step):
    socketio.emit('progress', {'username': username, 'step': step})

@app.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.get_json()
    posttext = data.get('post')
    footage_type = data.get('footage_type')
    username = data.get('username')
    posttext = unidecode(posttext)

    if not os.path.exists(os.path.join(script_dir, f'temporary{username}')):
        os.makedirs(os.path.join(script_dir, f'temporary{username}'))

    try:
        # Generate audio and subtitles in SRT format
        start = time.time()
        audio_filename, audio_duration, subtitle_file = generateAudio(posttext, username)
        print(f"{username} has completed step 1 in {str(time.time()-start)}s")
        emit_progress(username, 2)

        # Generate background video
        start = time.time()
        background_video = generateBackgroundVideo(audio_duration, footage_type)
        print(f"{username} has completed step 2 in {str(time.time()-start)}s")
        emit_progress(username, 3)

        # Add subtitles to background video
        start = time.time()
        subtitled_video = addSubtitles(background_video, subtitle_file)
        print(f"{username} has completed step 3 in {str(time.time()-start)}s")
        emit_progress(username, 4)

        # Write final video
        start = time.time()
        final_video = subtitled_video
        final_video_path = os.path.join(script_dir, f'temporary{username}', 'converting.mp4')
        final_video.write_videofile(final_video_path, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, logger=None)

        # Save the combined video with audio
        save(final_video_path, audio_filename, username)
        print(f"{username} has completed step 4 in {str(time.time()-start)}s")
        emit_progress(username, 5)
        
        return send_file(os.path.join(script_dir, f'video{username}.mp4'), as_attachment=True, download_name='video.mp4')

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        shutil.rmtree(f'temporary{username}', ignore_errors=True)

if __name__ == '__main__':
    app.run(debug=True)