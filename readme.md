[![Cover](https://github.com/KrishOnGH/shitpost.video/blob/c1dc325a6ea0cab1fc3207c9f55e8b4deb3c7f03/image.png)](https://www.loom.com/share/e66411b5f1084862be3291763d19c8c1?sid=373bb510-6b08-4f6c-b38e-cdfb9aaca0bc)

(Above Video is a Loom Link, Click on it)

# shitpost.video

shitpost.video is a tool for creating and posting Reddit TikTok-style videos for the AITA (Am I The Asshole) and Ask Reddit subreddits. It consists of two main components:

1. Web client for generating specific types of videos with custom posts, subtitles, and background footage.
2. YouTube autopost server for 24/7 video creation, review, and posting.

## Setup

1. Rename `.env.text` in the `common resources` directory to `.env` and add your real credentials.
2. Download Image Magik and FFMPEG and replace the Image Magik exe link in "common resources/generate_video.py"
3. If using the autopost server, replace `ytClientSecrets.json` with your actual Google API client secrets.

## Running the Web Client

1. In one terminal session:
   ```
   cd "web client"
   npm run build_web
   ```

2. In another terminal session:
   ```
   cd "web client/backend"
   python main.py
   ```

## Running the YouTube Autopost Server

```
cd "youtube autopost server"
python main.py
```

## Customization

To modify the subtitle, subreddit, background footage, or their usage frequency, edit `preferences.json` in the `youtube autopost server` directory.

## License

This project is licensed under the MIT License. Contributions are welcome.
