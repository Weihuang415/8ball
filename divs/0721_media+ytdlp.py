import os
import random
import threading
import glob
import yt_dlp
import subprocess
import vlc
from googleapiclient.discovery import build

DEVELOPER_KEY = 'AIzaSyBnuZGMVjskvqzxNXe2Mp1Ru8ABHl6qcwo'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Playlist ID for the playlist
playlist_id = 'PLuJfaMIfNlKPuCMMQSQpjBCxHP_yh6vA8'
prefix = ['IMG ', 'IMG_', 'IMG-', 'DSC ']
postfix = [' MOV', '.MOV', ' .MOV']

player = None
playing = False
pickedVid = ''

# .mp4 videos in the "vids" folder
cachedVids = sorted(glob.glob('*.mp4'))
index = len(cachedVids)
print(str(index) + " : " + str(cachedVids))

# Download from the playlist
def downloadVid(playlist_id):
    global index
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    playlist_items = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=20  # Maximum number of videos to retrieve from the playlist
    ).execute()

    video_ids = []
    for item in playlist_items['items']:
        video_ids.append(item['contentDetails']['videoId'])

    random_video_id = random.choice(video_ids)
    url = "http://www.youtube.com/watch?v=" + random_video_id
    print(url)

    ydl_opts = {
        'format': 'best[ext=mp4]',
        'logger': MyLogger(),
        'nocheckcertificate': True,
        'progress_hooks': [my_hook],
        'outtmpl': 'yt_' + str(index-2).zfill(2) + '.mp4'
    }
    index += 1

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    
def playVideo():
    global cachedVids
    global pickedVid
    global playing
    global player
    
    if cachedVids:
        pickedVid = random.choice(cachedVids)
        print('played ' + pickedVid)

        downloadOnly()
        
        # 1 vlc, create instance
        # playing = True
        # instance = vlc.Instance()
        # player = instance.media_player_new()
        # media = instance.media_new_path(os.path.abspath(pickedVid)) #fullscreen / omx
        # player.set_media(media)
        # player.play()
        # player.set_fullscreen(True)

        #2 cvlc, subprocess to execute the cvlc command with --fullscreen
        #hold
        cvlc_cmd = f"cvlc {os.path.abspath(pickedVid)} --fullscreen --aspect-ratio=1.33"
        subprocess.Popen(cvlc_cmd, shell=True)
        
        # #3 mpv,
        # mpv_cmd = f"mpv {os.path.abspath(pickedVid)} --fullscreen"
        # subprocess.Popen(mpv_cmd, shell=True)

        
    else:
        print("No videos available.")


def playNext():
    global playing
    global pickedVid
    global index

    if cachedVids:
        playing = True
        
        downloadOnly()
        
        index += 1
        if index >= len(cachedVids):
            index = 0  # Back to the first video if index exceeds the list length

        pickedVid = cachedVids[index]
        print('Playing ' + pickedVid)

        # playing = True
        # instance = vlc.Instance()
        # media = instance.media_new_path(os.path.abspath(pickedVid))
        # player.set_media(media)
        # player.play()
        # player.set_fullscreen(True)
        cvlc_cmd = f"cvlc {os.path.abspath(pickedVid)} --fullscreen --aspect-ratio=1.33"
        subprocess.Popen(cvlc_cmd, shell=True)
        
        
    else:
        print("No videos available.")

def stop():
    global playing
    global player

    print("stopping")
    player.stop()
    playing = False     


def downloadOnly():
    dlThread = Downloader("dl")
    dlThread.start()

class Downloader(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("Starting " + self.name)
        downloadVid(playlist_id)
        print("Exiting " + self.name)

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'finished':
        global cachedVids
        cachedVids = sorted(glob.glob('*.mp4'))
        print('Done downloading, now converting ...')
        print("vids: " + str(cachedVids))
            

#Play the video it when running the py.
playVideo()

# Loop
while True:
    key = input("Press 'N' to play the next video or 'X' to exit: ")
    if key == 'n':
        playNext()
    elif key == 'x':
        break
    else:
        stop()

