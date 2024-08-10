from flask import Flask, render_template_string, jsonify, request, send_from_directory
import json
import os

app = Flask(__name__)

VIDEO_DIR = 'video reserve'  # Directory where videos are stored
METADATA_FILE = os.path.join(VIDEO_DIR, 'metadata.json')  # Metadata file in the video reserve directory

def get_metadata():
    with open(METADATA_FILE, 'r') as file:
        return json.load(file)

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as file:
        json.dump(metadata, file, indent=4)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Swipe</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                overflow: hidden;
            }
            .video-container {
                position: relative;
                width: 80vw;
                max-width: 600px;
            }
            video {
                width: 100%;
                height: auto;
                display: block;
            }
            .message {
                font-size: 24px;
                color: #333;
                text-align: center;
            }
            .instructions {
                position: absolute;
                top: 50%;
                width: 100%;
                display: flex;
                justify-content: space-between;
                font-size: 24px;
                color: #333;
                transform: translateY(-50%);
            }
        </style>
    </head>
    <body>
        <div class="video-container">
            <video id="video" controls></video>
            <div class="instructions">
                <div id="reject" class="instruction">L - Reject</div>
                <div id="approve" class="instruction">R - Approve</div>
            </div>
        </div>
        <div id="message" class="message"></div>

        <script>
            async function loadVideo() {
                const response = await fetch('/video');
                const data = await response.json();

                if (data.video) {
                    document.getElementById('video').src = data.video;
                    document.getElementById('message').textContent = '';
                    document.getElementById('video').style.display = 'block';
                } else {
                    document.getElementById('message').textContent = data.message;
                    document.getElementById('video').style.display = 'none';
                }
            }

            function sendSwipeAction(action) {
                fetch('/' + action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ video: document.getElementById('video').src.split('/').pop().replace('video', '').replace('.mp4', '') })
                }).then(response => response.json()).then(() => loadVideo());
            }

            document.addEventListener('keydown', function(e) {
                if (e.key === 'r' || e.key === 'R') {
                    sendSwipeAction('approve');
                } else if (e.key === 'l' || e.key === 'L') {
                    sendSwipeAction('reject');
                }
            });

            // Load the first video when the page loads
            loadVideo();
        </script>
    </body>
    </html>
    ''')

@app.route('/video')
def get_video():
    metadata = get_metadata()
    all_videos = metadata.get('all videos', [])
    approved_videos = set(metadata.get('approved videos', []))

    available_videos = [v for v in all_videos if v not in approved_videos]

    if available_videos:
        next_video = available_videos[0]
        video_path = os.path.join(VIDEO_DIR, f'video{next_video}.mp4')
        return jsonify({'video': f'/video/{next_video}'})
    else:
        return jsonify({'message': 'No more videos available'})

@app.route('/video/<video_id>')
def serve_video(video_id):
    return send_from_directory(VIDEO_DIR, f'video{video_id}.mp4')

@app.route('/approve', methods=['POST'])
def approve_video():
    video_id = request.json.get('video')
    if video_id:
        metadata = get_metadata()
        approved_videos = set(metadata.get('approved videos', []))
        approved_videos.add(int(video_id))
        metadata['approved videos'] = list(approved_videos)
        save_metadata(metadata)
        return jsonify({'status': 'approved'})
    return jsonify({'status': 'error'})

@app.route('/reject', methods=['POST'])
def reject_video():
    # For simplicity, we'll just reload the video after rejection
    return jsonify({'status': 'rejected'})

if __name__ == '__main__':
    app.run(debug=True)
