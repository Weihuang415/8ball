import os
import random
import threading
import glob
import yt_dlp
import multiprocessing

from mpu6050 import mpu6050
from time import sleep
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
dlThread = None
screenUp = False
canFlip =False

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
    
def downloadOnly():
    dlThread = Downloader("dl")
    dlThread.start() 
    
    
# def play_video_process(pickedVid):
#     cvlc_cmd = f"cvlc {os.path.abspath(pickedVid)} --fullscreen --aspect-ratio=1.777" ###win
#     os.system(cvlc_cmd)


def play_video_process(pickedVid):
    cvlc_cmd = f'"C:/Program Files (x86)/VideoLAN/VLC/vlc.exe" -I dummy --dummy-quiet {os.path.abspath(pickedVid)}'
    os.system(cvlc_cmd)

def playVideo():
    global cachedVids
    global pickedVid
    global playing
    global player

    if cachedVids:
        pickedVid = random.choice(cachedVids)
        print('played ' + pickedVid)

        downloadOnly()
        print('downloadonly')
        
        # Create a new process for video playing
        video_process = multiprocessing.Process(target=play_video_process, args=(pickedVid,))
        video_process.start()

    else:
        print("No videos available.")
        
        
def playNext():
    global playing
    global pickedVid
    global index

    if cachedVids:
        playing = True

        # index += 1
        # if index >= len(cachedVids):
        #     index = 0  # Back to the first video if index exceeds the list length
        pickedVid = cachedVids[index-1]
        print('Playing ' + pickedVid)

        video_process = multiprocessing.Process(target=play_video_process, args=(pickedVid,))
        video_process.start()

    else:
        print("No videos available.")

    
def sensorDetect():
    global gyro_data
    global screenUp
    gyro_data = sensor.get_gyro_data()

    if (gyro_data['y'] <= -180 or  gyro_data['y'] >= 180) or (gyro_data['x'] <= -180 or gyro_data['x'] >= 180):
        screenUp = False
        print('Flip=True')
    else:
        screenUp = True
        print('Flip=False')
        
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
        
#Play the video 
playVideo()
    
    
# while True:
#     sensorDetect()
#     if screenUp == False:  # It's down
#         canFlip = True     
#     else:                  # It's up
#         if canFlip == True:
#             playVideo()
#             canFlip = False # Set it to False after playing the video
#     sleep(0.8)
