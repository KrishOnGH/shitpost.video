from generate import generate
from check import app as runCheckApp
from post import upload
import threading
import json
import os

generate_thread = threading.Thread(target=generate)
generate_thread.start()

script_dir = os.path.dirname(os.path.abspath(__file__))
video_reserve_path = os.path.join(script_dir, 'video reserve')
metadata_file = os.path.join(video_reserve_path, 'metadata.json')   
preferences_file = os.path.join(script_dir, 'preferences.json')

if os.path.exists(preferences_file):
    with open (preferences_file, 'r') as file:
        preferences = json.load(file)
else:
    preferences = {"subtitleColor": "white", "backgroundFootagePercentages": {"GTA": 50, "Minecraft": 0, "Satisfying": 50, "Subway Surfers": 0}, "subredditPercentages": {"AITA": 100, "AskReddit": 0}, "postsPerDay (max 10)": 3, "maxReserveVideos (100 reccomended for storage reasons)": 100, "needsManualCheck": True}

if (preferences['needsManualCheck']):
    flask_thread = threading.Thread(target=runCheckApp.run(debug=True))
    flask_thread.start()

if os.path.exists(metadata_file):
    with open(metadata_file, 'r') as file:
        metadata = json.load(file)
else:
    metadata = {"all videos": [], "approved videos": [], "data of videos": {}}

if (preferences['needsManualCheck']):
    approvedVideos = metadata["approved videos"] 
else:
    approvedVideos = metadata["all videos"] 

for v in approvedVideos:
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as file:
            metadata = json.load(file)

    video = os.path.join(video_reserve_path, f'video{v}')
    title = metadata['data of videos'][f'video{v}']['title']
    upload(video, title, title)
    os.remove(video)

    metadata['all videos'].remove(f'video{v}')
    
    metadata['approved videos'].remove(f'video{v}')
    
    del metadata['data of videos'][f'video{v}']
    
    with open(metadata_file, 'w') as file:
        json.dump(metadata, file, indent=4)