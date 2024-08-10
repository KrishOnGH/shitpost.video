from generate import generate
from check import app as runCheckApp
from post import schedule_uploads as uploadSchedule
import threading
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
video_reserve_path = os.path.join(script_dir, 'video reserve') 
preferences_file = os.path.join(script_dir, 'preferences.json')

if os.path.exists(preferences_file):
    with open (preferences_file, 'r') as file:
        preferences = json.load(file)
else:
    preferences = {"subtitleColor": "white", "backgroundFootagePercentages": {"GTA": 50, "Minecraft": 0, "Satisfying": 50, "Subway Surfers": 0}, "subredditPercentages": {"AITA": 100, "AskReddit": 0}, "postsPerDay (max 10)": 3, "maxReserveVideos (100 reccomended for storage reasons)": 100, "needsManualCheck": True}

if (preferences['needsManualCheck']):
    flask_thread = threading.Thread(target=runCheckApp.run(debug=True))
    flask_thread.start()

generate_thread = threading.Thread(target=generate)
generate_thread.start()

upload_thread = threading.Thread(target=uploadSchedule)
upload_thread.start()