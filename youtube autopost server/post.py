import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "ytClientSecrets.json"

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
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None