import os
import json
import time
import schedule
import googleapiclient.errors
import google_auth_oauthlib.flow
import googleapiclient.discovery
from datetime import datetime, timedelta
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
script_dir = os.path.dirname(os.path.abspath(__file__))
video_reserve_path = os.path.join(script_dir, 'video reserve')
metadata_file = os.path.join(video_reserve_path, 'metadata.json')
preferences_file = os.path.join(script_dir, 'preferences.json')
CLIENT_SECRETS_FILE = "ytClientSecrets.json"

if os.path.exists(preferences_file):
    with open(preferences_file, 'r') as file:
        preferences = json.load(file)

else:
    preferences = {"subtitleColor": "white", "backgroundFootagePercentages": {"GTA": 50, "Minecraft": 0, "Satisfying": 50, "Subway Surfers": 0}, "subredditPercentages": {"AITA": 100, "AskReddit": 0}, "postsPerDay (max 10)": 3, "maxReserveVideos (100 reccomended for storage reasons)": 100, "needsManualCheck": True}

posts_per_day = max(1, min(preferences.get('postsPerDay (max 10)', 3), 10))

def upload(video_path, title, description):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    client_secrets_path = os.path.join("..", "common resources", CLIENT_SECRETS_FILE)

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_path, SCOPES)
    flow.run_local_server(port=8080)
    credentials = flow.credentials

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                },
                "status": {
                    "privacyStatus": "public"
                }
            },
            media_body=MediaFileUpload(video_path)
        )

        response = request.execute()
        return response['id']

    except googleapiclient.errors.HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None

def uploadReserveVideo():
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as file:
            metadata = json.load(file)

    if preferences['needsManualCheck']:
        approvedVideos = metadata['approved videos']
    else:
        approvedVideos = metadata['all videos']

    if not approvedVideos:
        print("No videos available for upload.")
        return

    v = approvedVideos[0]

    video = os.path.join(video_reserve_path, f'video{v}')
    title = metadata['data of videos'][f'video{v}']['title']
    upload(video, title, title)
    os.remove(video)

    metadata['all videos'].remove(f'video{v}')
    
    if v in metadata['approved videos']:
        metadata['approved videos'].remove(f'video{v}')
    
    del metadata['data of videos'][f'video{v}']
    
    with open(metadata_file, 'w') as file:
        json.dump(metadata, file, indent=4)

def schedule_uploads():
    now = datetime.utcnow()
    interval = 24 / posts_per_day

    for i in range(posts_per_day):
        upload_time = now + timedelta(hours=i * interval)
        upload_time_str = upload_time.strftime("%H:%M")
        schedule.every().day.at(upload_time_str).do(uploadReserveVideo)
        print(f"Scheduled upload at {upload_time_str} UTC")

    while True:
        schedule.run_pending()
        time.sleep(60)