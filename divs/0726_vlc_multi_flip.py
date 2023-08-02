import os
import random
import threading
import glob
import yt_dlp
import multiprocessing

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
    print("Naming, index:", index)
    print("Video_ID:", video_ids)


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
def downloadOnly():
    dlThread = Downloader("dl")
    dlThread.start() 
    print("downloadOnly")
    
    
def play_video_process(pickedVid):
    # cvlc_cmd = f"cvlc {os.path.abspath(pickedVid)} --fullscreen --aspect-ratio=1.777 --repeat" 
    # os.system(cvlc_cmd)
    print("Video_process", "pickedVid:", pickedVid)



def playVideo():
    global cachedVids
    global pickedVid
    global playing
    global player

    if cachedVids:
        pickedVid = random.choice(cachedVids)
        print('played ' + pickedVid)
        
        # Create a new process for video playing
        video_process = multiprocessing.Process(target=play_video_process, args=(pickedVid,))
        video_process.start()

    else:
        print("No videos available.")
        
        
def playNext():
    global playing
    global pickedVid
    global index
    # index = len(cachedVids)-1
    print("First, index:", index)
    
    if cachedVids:
        playing = True
        # index += 1
        # if index >= len(cachedVids):
        #     index = 0  # Back to the first video if index exceeds the list length
        pickedVid = cachedVids[index-1]
        print('Playing ' + pickedVid, 'indexNum:' + str(index))
        print("Looping, index:", index)

        #how to pass the pickedVid to the play_video_process 
        video_process = multiprocessing.Process(target=play_video_process, args=(pickedVid,))
        video_process.start()

    else:
        print("No videos available.")

    
def sensorDetect():
    global gyro_data
    global screenUp
    gyro_data = sensor.get_gyro_data()
    
    # print("x: {:.2f}".format(gyro_data['x']))
    # print("y: {:.2f}".format(gyro_data['y']))
    # print("z: {:.2f}".format(gyro_data['z']))
    
    if (gyro_data['y'] <= -100 or  gyro_data['y'] >= 100) or (gyro_data['z'] <= -100 or gyro_data['z'] >= 100):
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