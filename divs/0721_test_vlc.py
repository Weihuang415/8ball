import os
import random
import subprocess
import glob
# .mp4 videos in the "vids" folder
cachedVids = sorted(glob.glob('*.mp4'))
index = len(cachedVids)
print(str(index) + " : " + str(cachedVids))

player = None
playing = False
pickedVid = ''

def playVideo():
    global cachedVids
    global pickedVid
    global playing
    global player

    if cachedVids:
        pickedVid = random.choice(cachedVids)
        print('played ' + pickedVid)

        playing = True
        # Use subprocess to execute the cvlc command with --fullscreen
        cvlc_cmd = f"cvlc {os.path.abspath(pickedVid)} --fullscreen"
        subprocess.Popen(cvlc_cmd, shell=True)

    else:
        print("No videos available.")


playVideo()