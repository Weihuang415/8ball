import threading
import random
import glob
import os
import yt_dlp
import requests
import multiprocessing
from pytube import YouTube
from base64 import b64encode
from cachetools import cached, TTLCache, LRUCache
from datetime import datetime, timedelta
from time import sleep
from googleapiclient.discovery import build

prefix = ['IMG ', 'IMG_', 'IMG-', 'DSC ']
postfix = [' MOV', '.MOV', ' .MOV']

DEVELOPER_KEY = 'AIzaSyBXA6zoGT0nXM2CEqkr95Y-oxXxcQMHvRg' 
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

dlThread = None
pickedVid = ''
cachedVids = sorted(glob.glob('*.mp4'))
Played = True
playing = False
screenUp = False
canFlip =False

i = 0

### CACHE (search yt)
def cache_key(*args, **kwargs):
    cache_key = 'cacheKey'
    return cache_key

cache = TTLCache(maxsize=64, ttl=60)
@cached(cache, key=cache_key, info=True)
def youtube_search():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search_response = youtube.search().list(
        q=random.choice(prefix) + str(random.randint(999, 9999)) + random.choice(postfix),
        part='snippet',
        type="video",
        videoDefinition="standard",
        videoDimension="2d",
        videoDuration="short",
        maxResults=10
    ).execute()

    videos = []

    for search_result in search_response.get('items', []):
        videos.append(search_result['id']['videoId'])
        #print(videos)
    return videos

# SearchResult List / create a object
SearchResult = youtube_search()

# The cache contains a single cached item which is a list.
#print('CacheInfo:', youtube_search.cache_info())
print('cache:', cache)

#we don't need to see the cache 
#cached_value = cache.get(cache_key())
print('First Video:', SearchResult[0]) # from -~5


def Clear_cache():
    youtube_search.cache.clear()
# print('After clearing cache:', cache)


### DOWNLOAD
def downloadVid():
    video_id = SearchResult[i] #youtube_search()
    if video_id:
        url = "https://www.youtube.com/watch?v=" + video_id
        print(url)
        print("i", i)

        ydl_opts = {
            'format': 'mp4[height<720]',
            'logger': MyLogger(),
            'nocheckcertificate': True,
            'progress_hooks': [my_hook],
            'outtmpl': 'yt_' + str(i) + '_' + video_id + '.mp4'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    else:
        print("No suitable videos found.")

  

def downloadOnly():
    dlThread = Downloader("dl")
    dlThread.start()
    
class Downloader(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        print("Starting " + self.name)
        downloadVid()
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
        #print("vids: " + str(cachedVids))


# VLC player opens (multiprocess)
def VLC_open():
    global playing
    if cachedVids:
        # Create a new process for video playing
        video_process = multiprocessing.Process(target=play_video_process, args=(pickedVid,))
        video_process.start()
        playing = True
    else:
        print("No videos available.")

def play_video_process(pickedVid):  
    vlc_cmd = f'"C:/Program Files (x86)/VideoLAN/VLC/vlc.exe" --repeat --extraintf=http --http-host=127.0.0.1 --http-port=8080 --http-password=asdf {os.path.abspath(pickedVid)}'
    os.system(vlc_cmd)
    print("Video_process", pickedVid)

#http setting stuff
def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


def playNext():
    global playing
    global pickedVid
    global played    
    
    if cachedVids:
        playing = True
        
        # Play default video once
        defaultVid = 'Default\Default.mp4'
        play_url = f'http://127.0.0.1:8080/requests/status.json'
        headers = {'Authorization': basic_auth("", "asdf")}
        params = {'command': 'in_play', 'input': os.path.abspath(defaultVid)}
        response = requests.get(play_url, headers=headers, params=params)
        if response.status_code == 200:
            print(f'VLC is now playing the default video: {defaultVid}')
        else:
            print(f'Failed to play the default video. Status code: {response.status_code}')

        sleep(1)  # delay between default video and picked video

        # Play the next video (pickedVid) Always play the first one
        pickedVid = cachedVids[0] 
        played = True
        
        params = {'command': 'in_play', 'input': os.path.abspath(pickedVid)}
        response = requests.get(play_url, headers=headers, params=params)
        if response.status_code == 200:
            print(f'VLC is now playing the picked video: {pickedVid}')
        else:
            print(f'Failed to play the picked video. Status code: {response.status_code}')
    else:
        print("No videos available.")

def delete_video():
    if played:
        print(f"{cachedVids[0]} Removing the played video.")
        try:
            os.remove(cachedVids[0])
            print(f"Existing video {cachedVids[0]} removed.")
        except OSError as e:
            print(f"Error removing video {cachedVids[0]}: {e}")

# downloadOnly()

if __name__ == '__main__':
    VLC_open()
    youtube_search()
    downloadOnly()
    
    while True:
        playNext()
        key = input("Press 'N' to play the next video or 'X' to exit: ")
        if key == 'n':
            i += 1
            print("index", i)
            downloadOnly()
            playNext()
            delete_video()
        else:
            break
        


