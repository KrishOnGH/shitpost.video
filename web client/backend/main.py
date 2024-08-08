# Import common resources
import sys
import os

# Handle the directory name with a space
common_resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../common resources'))

# Temporarily add the directory to sys.path
sys.path.insert(0, common_resources_path)

try:
    from generate_video import createTempFolder, generateAudio, generateBackgroundVideo, addSubtitles
    from fetch import fetch_aita_post, fetch_askreddit_post, fetch_from_link

finally:
    sys.path.pop(0)

from flask import Flask, request, send_file, jsonify
from flask_socketio import SocketIO
from unidecode import unidecode
from flask_cors import CORS
import subprocess
import zipfile
import random
import shutil
import time
import io

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get post, background footage choice, and directory location for temporary storage
script_dir = os.path.dirname(os.path.abspath(__file__))

# Main script execution
script_start_time = time.time()

# Save video function
def save(video, audio, username, i):
    output_video = os.path.join(script_dir, f'video{username}{i}.mp4')

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

def emit_progress(username, parts, step):
    socketio.emit('progress', {'username': username, 'parts': parts, 'step': step})

@app.route('/generate-link', methods=['POST'])
def generate_link():
    data = request.get_json()
    username = data.get('username')

    try:
        subreddit = random.randint(1, 2)
        if subreddit == 1:
            data = fetch_aita_post(username)
            return { 'url': data['url'] }
        elif subreddit == 2:
            data = fetch_askreddit_post(username)
            return { 'url': data['url'] }
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.get_json()
    link = data.get('link')
    footage_type = data.get('footage_type')
    subtitle_color = data.get('subtitle_color')
    username = data.get('username')
    result = fetch_from_link(link)

    temp_dir = createTempFolder(username)

    try:
        if result:
            if 'top_comment' in result:
                posttext = result['content'] + ', ' + result['top_comment']['content']
            else:
                posttext = result['title'] + ', ' + result['content']
            cut = 1030
            parts, start = [], 0
            while start < len(posttext):
                end = start + cut
                end = max(posttext.rfind('.', start, end), posttext.rfind('!', start, end), posttext.rfind('?', start, end))
                if end == -1 or end <= start:
                    end = min(start + cut, len(posttext))
                part = posttext[start:end+1].strip()
                if part:
                    parts.append(part)
                start = end + 1
                
        else:
            return jsonify({"error": "Link not sufficient"}), 500

        for i, posttext in enumerate(parts):        
            emit_progress(username, f'Part {i+1}/{len(parts)}', 1)
            # Generate audio and subtitles in SRT format
            start = time.time()
            audio_filename, audio_duration, subtitle_file = generateAudio(posttext, temp_dir)
            print(f"{username} has completed step 1 in {str(time.time()-start)}s")
            emit_progress(username, f'Part {i+1}/{len(parts)}', 2)

            # Generate background video
            start = time.time()
            background_video = generateBackgroundVideo(audio_duration, footage_type)
            print(f"{username} has completed step 2 in {str(time.time()-start)}s")
            emit_progress(username, f'Part {i+1}/{len(parts)}', 3)

            # Add subtitles to background video
            start = time.time()
            subtitled_video = addSubtitles(background_video, subtitle_file, subtitle_color)
            print(f"{username} has completed step 3 in {str(time.time()-start)}s")
            emit_progress(username, f'Part {i+1}/{len(parts)}', 4)

            # Write final video
            start = time.time()
            final_video_path = os.path.join(temp_dir, f'converting{i+1}.mp4')
            final_video = subtitled_video
            final_video.write_videofile(final_video_path, codec='libx264', audio_codec='aac', temp_audiofile=os.path.join(temp_dir, 'temp-audio.m4a'), remove_temp=True, logger=None)

            # Save the combined video with audio
            save(final_video_path, audio_filename, username, i+1)
            print(f"{username} has completed step 4 in {str(time.time()-start)}s")
            emit_progress(username, f'Part {i+1}/{len(parts)}', 5)

        video_files = [os.path.join(script_dir, f'video{username}{i+1}.mp4') for i in range(len(parts))]

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for i, video_file in enumerate(video_files):
                if os.path.exists(video_file):
                    zip_file.write(video_file, f'video{i+1}.mp4')
                else:
                    return jsonify({"error": f"File {video_file} not found"}), 404

        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name='videos.zip', mimetype='application/zip')
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    app.run(debug=True)