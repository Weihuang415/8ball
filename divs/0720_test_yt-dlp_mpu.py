import os
import random
import threading
import glob
import yt_dlp
import vlc
from googleapiclient.discovery import build

from mpu6050.mpu6050 import mpu6050
from time import sleep

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
        'outtmpl': 'yt_' + str(index).zfill(2) + '.mp4'
    }
    index += 1

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def downloadOnly():
    dlThread = Downloader("dl")
    dlThread.start()

def playNext():
    global playing
    global pickedVid
    global index

    if cachedVids:
        playing = True
        
        index += 1
        if index >= len(cachedVids):
            index = 0  # Back to the first video if index exceeds the list length

        pickedVid = cachedVids[index]
        print('Playing ' + pickedVid)

        playing = True
        instance = vlc.Instance()
        media = instance.media_new_path(os.path.abspath(pickedVid))
        player.set_media(media)
        player.play()
        
    else:
        print("No videos available.")


def stop():
    global playing
    global player

    print("stopping")
    player.stop()
    playing = False

def removeVid():
    global cachedVids
    global pickedVid
    
    player.stop()
    player.release()
    os.remove(pickedVid)
    cachedVids = sorted(glob.glob('*.mp4'))
    print(cachedVids)


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
            
            
# Accelerometer
def sensorDetect():
    global Flip
    if gyro_data['y'] <= -180 or  gyro_data['y'] >= 180:
        Flip = True
        print("Flip")
    else:
        Flip = False
        print("N")

def updateSensorData():
    global accel_data
    global gyro_data
    global temp
    global Flip

    accel_data = sensor.get_accel_data()
    gyro_data = sensor.get_gyro_data()
    temp = sensor.get_temp()
    Flip = False

# Start the ball game (default value)
#playVideo()
updateSensorData()
downloadOnly()

# Loop
while True:
    updateSensorData()
    sensorDetect()
    sleep(0.8)

