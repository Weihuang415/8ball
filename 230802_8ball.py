import requests
import os
import random
import threading
import glob
import yt_dlp
import multiprocessing
from base64 import b64encode

from mpu6050 import mpu6050
from time import sleep
from googleapiclient.discovery import build

sensor = mpu6050(0x68)

DEVELOPER_KEY = 'AIzaSyBnuZGMVjskvqzxNXe2Mp1Ru8ABHl6qcwo'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Playlist ID for the playlist
playlist_id = 'PLuJfaMIfNlKPj1UZpGlYjCop8S_0DyEB_'
prefix = ['IMG ', 'IMG_', 'IMG-', 'DSC ']
postfix = [' MOV', '.MOV', ' .MOV']

player = None
playing = False
pickedVid = ''
dlThread = None
screenUp = False
canFlip =False

# .mp4 videos in the "vids" folder
cachedVids = sorted(glob.glob('yt_*.mp4'))
index = len(cachedVids)
print("mp4 in vids Folder", str(index) + " : " + str(cachedVids))


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

    # random_video_id = random.choice(video_ids)
    # url = "http://www.youtube.com/watch?v=" + random_video_id
    # print(url)
    
    # if index >= len(video_ids):
    #     index = 0
    
    choose_video_id = video_ids[index % len(video_ids)]
    url = "http://www.youtube.com/watch?v=" + choose_video_id
    print("Downloading video with ID:", choose_video_id)
    print("index:", index)
    print("[video_ids]", video_ids)


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
    
    #update folder vid
    new_video = 'yt_' + str(index - 1).zfill(2) + '.mp4'
    updateCachedVids(new_video)

def updateCachedVids(new_video):
    global cachedVids

    cachedVids.append(new_video)

    # If the list length exceeds 5, remove the oldest video
    if len(cachedVids) > 6:
        oldest_video = cachedVids.pop(0)
        # Delete the oldest video file from disk
        if os.path.exists(oldest_video):
            os.remove(oldest_video)
    
def downloadOnly():
    dlThread = Downloader("dl")
    dlThread.start() 
    print("downloadOnly")

def play_video_process(pickedVid):    
    if os.path.exists(pickedVid):
        cvlc_cmd = f"cvlc {os.path.abspath(pickedVid)} --fullscreen --repeat --extraintf=http --http-host=127.0.0.1 --http-port=8080 --http-password=asdf"
        os.system(cvlc_cmd)
        print("Video_process", pickedVid)

    else:
        print(f"Video file {pickedVid} does not exist.")

def playVideo():
    global cachedVids
    global pickedVid
    global playing
    global player

    if cachedVids:
        pickedVid = random.choice(cachedVids)
        # pickedVid = cachedVids[0]
        print('played ' + pickedVid)
        
        # Create a new process for video playing
        video_process = multiprocessing.Process(target=play_video_process, args=(pickedVid,))
        video_process.start()

    else:
        print("No videos available.")
        
def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

def playNext():
    global playing
    global pickedVid
    global index    
    
    if cachedVids:
        playing = True
        
        #PLAYING
        pickedVid = cachedVids[-2]
        print('Playing ' + pickedVid)
        print("Looping, index:", index)
        
        # # Send HTTP request to VLC to play the next video
        
        play_url = f'http://127.0.0.1:8080/requests/status.json' 
        headers = { 'Authorization' : basic_auth("", "asdf") }
        params={'command': 'in_play', 'input':os.path.abspath(pickedVid)}
        response = requests.get(play_url, headers=headers, params=params)
        
        #### after ? is params
        
        if response.status_code == 200:
            print(f'VLC is now playing this video: {pickedVid}')
        else:
            print(f'Failed to play the next video. Status code: {response.status_code}')

    else:
        print("No videos available.")

def sensorDetect():
    global gyro_data
    global screenUp
    gyro_data = sensor.get_gyro_data()
    
    if (gyro_data['y'] <= -70 or  gyro_data['y'] >= 70) or (gyro_data['z'] <= -70 or gyro_data['z'] >= 70):
        screenUp = False
        # print('Flip=True')
    else:
        screenUp = True
        # print('Flip=False')
        
def stop():
    global playing
    global player

    print("stopping")
    player.stop()
    playing = False     

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
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'finished':
        global cachedVids
        cachedVids = sorted(glob.glob('*.mp4'))
        print('Done downloading, now converting ...')
        print("vids: " + str(cachedVids))
    
    

if __name__ == '__main__':
    playVideo()
    downloadOnly()
    
    while True:
        sensorDetect()

        if screenUp == False:  # It's down
            canFlip = True
            print('/////Down/////')   
             
        else:                  # It's up
            print('up')
            if canFlip == True:
                playNext()
                downloadOnly()
                canFlip = False # Set it to False after playing the video
                
        sleep(0.8)


