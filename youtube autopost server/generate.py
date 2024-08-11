# Import common resources
import sys
import os

# Handle the directory name with a space
common_resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../common resources'))

# Temporarily add the directory to sys.path
sys.path.insert(0, common_resources_path)

try:
    from generate_video import createTempFolder, generateAudio, generateBackgroundVideo, addSubtitles
    from fetch import fetch_aita_post, fetch_askreddit_post, fetch_from_link

finally:
    sys.path.pop(0)

import subprocess
import random
import shutil
import random
import time
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
video_reserve_path = os.path.join(script_dir, 'video reserve')
metadata_file = os.path.join(video_reserve_path, 'metadata.json')

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preferences.json'), 'r') as file:
    preferences = json.load(file)

# Save video function
def save(video, audio, video_id, i):
    output_video = f"video reserve/video{video_id}part{i}.mp4"

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

def generate_link(username, subreddit):
    try:
        if subreddit == 'AITA':
            data = fetch_aita_post(username)
            return { 'url': data['url'] }
        elif subreddit == 'AskReddit':
            data = fetch_askreddit_post(username)
            return { 'url': data['url'] }

    except Exception as e:
        print(f"An error occurred:: {e}")
        return None

def generateVideo(username, footage_type, subtitle_color, link):
    result = fetch_from_link(link['url'])
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
            return "Link not sufficient"

        for i, posttext in enumerate(parts):
            # Generate audio and subtitles in SRT format
            start = time.time()
            audio_filename, audio_duration, subtitle_file = generateAudio(posttext, temp_dir)
            print(f"{username} has completed step 1 in {str(time.time()-start)}s")

            # Generate background video
            start = time.time()
            background_video = generateBackgroundVideo(audio_duration, footage_type)
            print(f"{username} has completed step 2 in {str(time.time()-start)}s")

            # Add subtitles to background video
            start = time.time()
            subtitled_video = addSubtitles(background_video, subtitle_file, subtitle_color)
            print(f"{username} has completed step 3 in {str(time.time()-start)}s")

            # Write final video
            start = time.time()
            video_id = result['id']
            final_video = subtitled_video
            final_video_path = os.path.join(temp_dir, f'converting{video_id}part{i+1}.mp4')
            final_video.write_videofile(final_video_path, codec='libx264', audio_codec='aac', temp_audiofile=os.path.join(temp_dir, 'temp-audio.m4a'), remove_temp=True, logger=None)

            # Save the combined video with audio
            save(final_video_path, audio_filename, video_id, i+1)
            print(f"{username} has completed step 4 in {str(time.time()-start)}s")

            metadata_file = os.path.join(video_reserve_path, 'metadata.json')   
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as file:
                    metadata = json.load(file)

            metadata['all videos'].append(f'{video_id}part{i+1}')
            metadata['data of videos'][f'video{video_id}part{i+1}'] = {'title': result['title']}

            with open(metadata_file, 'w') as file:
                json.dump(metadata, file, indent=4)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def generate():
    while True:
        reservedVideos = len([f for f in os.listdir(video_reserve_path) if f.lower().endswith('.mp4')])

        if reservedVideos < preferences['maxReserveVideos (100 reccomended for storage reasons)']:
            subreddit = random.choices(list(preferences['subredditPercentages'].keys()), 
                                    weights=list(preferences['subredditPercentages'].values()), 
                                    k=1)[0]
            backgroundFootage = random.choices(list(preferences['backgroundFootagePercentages'].keys()), 
                                        weights=list(preferences['backgroundFootagePercentages'].values()), 
                                        k=1)[0]

            subtitleColor = preferences['subtitleColor']
            link = generate_link("Auto Post Server", subreddit)
            generateVideo("Auto Post Server", backgroundFootage, subtitleColor, link)

        time.sleep(10)