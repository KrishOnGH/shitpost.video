# shitpost.video

shitpost.video is a tool for creating and posting Reddit TikTok-style videos for the AITA (Am I The Asshole) and Ask Reddit subreddits. It consists of two main components:

1. Web client for generating specific types of videos with custom posts, subtitles, and background footage.
2. YouTube autopost server for 24/7 video creation, review, and posting.

## Setup

1. Rename `.env.text` in the `common resources` directory to `.env` and add your real credentials.
2. If using the autopost server, replace `ytClientSecrets.json` with your actual Google API client secrets.

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