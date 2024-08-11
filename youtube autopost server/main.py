from post import schedule_uploads as uploadSchedule
from check import app as runCheckApp
from generate import generate
import threading
import time
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
video_reserve_path = os.path.join(script_dir, 'video reserve') 
preferences_file = os.path.join(script_dir, 'preferences.json')

def load_preferences():
    if os.path.exists(preferences_file):
        with open(preferences_file, 'r') as file:
            return json.load(file)
    else:
        return {
            "subtitleColor": "white",
            "backgroundFootagePercentages": {"GTA": 50, "Minecraft": 0, "Satisfying": 50, "Subway Surfers": 0},
            "subredditPercentages": {"AITA": 100, "AskReddit": 0},
            "postsPerDay (max 10)": 3,
            "maxReserveVideos (100 reccomended for storage reasons)": 100,
            "needsManualCheck": True
        }

def run_generate(stop_event):
    while not stop_event.is_set():
        try:
            generate()
        except Exception as e:
            print(f"An error occurred in generate: {e}")
            time.sleep(10)

def run_flask_app():
    runCheckApp.run(port=6050, debug=False, use_reloader=False)

if __name__ == "__main__":
    preferences = load_preferences()
    stop_event = threading.Event()

    generate_thread = threading.Thread(target=run_generate, args=(stop_event,))
    generate_thread.start()

    if preferences['needsManualCheck']:
        flask_thread = threading.Thread(target=run_flask_app)
        flask_thread.start()

    upload_thread = threading.Thread(target=uploadSchedule)
    upload_thread.start()

    # Keep Alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        stop_event.set()
    finally:
        generate_thread.join()
        if preferences['needsManualCheck']:
            flask_thread.join()
        print("All threads have been shut down.")