import yt_dlp
import os
import random
import threading
import glob
from googleapiclient.discovery import build

DEVELOPER_KEY = 'AIzaSyBnuZGMVjskvqzxNXe2Mp1Ru8ABHl6qcwo'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Playlist ID for the playlist
playlist_id = 'PLuJfaMIfNlKPj1UZpGlYjCop8S_0DyEB_'

prefix = ['IMG ', 'IMG_', 'IMG-', 'DSC ']
postfix = [' MOV', '.MOV', ' .MOV']


# .mp4 videos in the "vids" folder
cachedVids = sorted(glob.glob('*.mp4'))
index = len(cachedVids)
print(str(index) + " : " + str(cachedVids))

#URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

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
        'outtmpl': 'yt_' + str(index).zfill(2) + '.mp4'
    
    }
    index += 1

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        

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
        print(msg)
        pass

    def warning(self, msg):
        print(msg)
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'finished':
        global cachedVids
        cachedVids = sorted(glob.glob('*.mp4'))
        print('Done downloading, now converting ...')
        print("vids: " + str(cachedVids))

        
downloadOnly()