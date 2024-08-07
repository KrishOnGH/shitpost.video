# Import common resources
import sys
import os

# Handle the directory name with a space
common_resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../common resources'))

# Temporarily add the directory to sys.path
sys.path.insert(0, common_resources_path)

try:
    from generate_video import generateAudio, generateBackgroundVideo, addSubtitles
    from fetch import fetch_aita_post, fetch_askreddit_post, fetch_from_link

finally:
    sys.path.pop(0)

import subprocess
import zipfile
import random
import shutil
import time
import io

while True:
    print("placeholder for generating video to reserve")
    time.sleep(1)