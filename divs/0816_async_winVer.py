import asyncio
import random
import glob
import os
import yt_dlp
import requests
import multiprocessing
from base64 import b64encode
from time import sleep, time
import time
from googleapiclient.discovery import build

prefix = ['IMG ', 'IMG_', 'IMG-', 'DSC ']
postfix = [' MOV', '.MOV', ' .MOV']

DEVELOPER_KEY = 'AIzaSyCGp2bkWFADc2zcHr_VPMl6W8CVbbs1IJc' 
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

pickedVid = ''
cachedVids = sorted(glob.glob('VideoDL/*.mp4'))
print("cachedVids:", cachedVids)
output_dir = 'VideoDL'  

Played = True
playing = False
screenUp = False
canFlip =False

searchResult = []
i_search = 0

def youtube_search():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    videos = []
    
    while len(videos) < 5:
        try:
            search_response = youtube.search().list(
                q=random.choice(prefix) + str(random.randint(999, 9999)) + random.choice(postfix),
                part='snippet',
                type="video",
                videoDefinition="standard",
                videoDimension="2d",
                videoDuration="short",
                maxResults=5
            ).execute()
            
            for search_result in search_response.get('items', []):
                videos.append(search_result['id']['videoId'])
        
        except Exception as e:
            print(e)        
    print('videos:', videos)
    return videos


### DOWNLOAD
async def downloadVid():
    global searchResult
    print(searchResult)
    
    video_id = searchResult[i_search] #youtube_search()
    if video_id:
        url = "https://www.youtube.com/watch?v=" + video_id
        print(url)
        print("i", i_search)

        ydl_opts = {
            'format': 'mp4[height<720]',
            'logger': MyLogger(),
            'nocheckcertificate': True,
            'progress_hooks': [my_hook],
            # 'outtmpl': + str(int(time.time()))[-4:] + '_'+ video_id + '.mp4'
            'outtmpl': os.path.join(output_dir, 'yt_' + str(int(time.time()))[-4:] + '_'+ str(video_id)[4:] + '.mp4')
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            global cachedVids
            cachedVids = sorted(glob.glob('VideoDL/*.mp4'))

    else:
        print("No suitable videos found.")
    

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
    print("Video_process:", pickedVid)

#http setting
def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

#Play a Video
async def playNext():
    global playing
    global played    
    global pickedVid
    
    if cachedVids:
        playing = True
        #Playthe First one
        pickedVid = cachedVids[0] 
        play_url = f'http://127.0.0.1:8080/requests/status.json'
        headers = {'Authorization': basic_auth("", "asdf")}     
           
        params = {'command': 'in_play', 'input': os.path.abspath(pickedVid)}
        response = requests.get(play_url, headers=headers, params=params)
        if response.status_code == 200:
            print(f'VLC is now playing the picked video: {pickedVid}')
        else:
            print(f'Failed to play the picked video. Status code: {response.status_code}')

        played = True

    else:
        print("No videos available.")


#Stop the Video
def stopPlaying():
    global played
    global playing
    global pickedVid
    
    if playing:
        
        play_url = f'http://127.0.0.1:8080/requests/status.json'
        headers = {'Authorization': basic_auth("", "asdf")}
        
        #Stop Video
        params = {'command': 'pl_stop', 'input': os.path.abspath(pickedVid)}
        response = requests.get(play_url, headers=headers, params=params)
        if response.status_code == 200:
            print(f'VLC stoped the picked video: {pickedVid}')
        else:
            print(f'Failed to stop the picked video. Status code: {response.status_code}')
            
        # Play default video
        defaultVid = 'VideoDefault\Default2.mp4'    
        params = {'command': 'in_play', 'input': os.path.abspath(defaultVid)}
        response = requests.get(play_url, headers=headers, params=params)
        if response.status_code == 200:
            print(f'VLC is now playing the default video: {defaultVid}')
        else:
            print(f'Failed to play the default video. Status code: {response.status_code}')

        sleep(1)  # delay between default video and picked video

        played = True
        
    else:
        print("No videos playing.")

def delete_video():
    if played:
        print(f"{cachedVids[0]} --- Removing the played video.")
        try:
            os.remove(cachedVids[0])  #remove the file in VideoDL folder
            print(f"{cachedVids[0]} --- Removed.")
            
            cachedVids.pop(0)   #remove from the list
            print(f"{cachedVids[0]} --- first video in cachedVids.")
            
        except OSError as e:
            print(f"Error removing video {cachedVids[0]}: {e}")


async def Tasks():
    await asyncio.gather(playNext(), downloadVid())


if __name__ == '__main__':
        
    VLC_open()

    searchResult = youtube_search()
    print('SearchResult:', searchResult)    
    
    while True:
        key = input("Press 'N' to play or 'X' to exit: ")
    
        if key == 'n': #flip up
            
            #Async 
            asyncio.run(Tasks())
            
            i_search += 1
            print("index:", i_search)
            
            #search again if it runs out of list
            if i_search >= 5:
                SearchResult = youtube_search() 
                i_search = 0
                
        elif key == 'd': #flip down
            stopPlaying()
            delete_video()
                       
        else:
            break
        
        
'''
if __name__ == '__main__':
    playVideo()
    downloadOnly()
    while True:
        #sensorDetect()

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
        
'''
