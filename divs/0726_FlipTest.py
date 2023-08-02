import os
import random
from mpu6050 import mpu6050

from time import sleep

sensor = mpu6050(0x68)

screenUp = False
canFlip =False
downloadComplete = True

def downloadOnly():
    print('downloadOnly')
    #sleep(3)
    downloadComplete = True
    
    
def playVideo():
    print("playVideo")
        
def playNext():
    print('playNext')

    
def sensorDetect():
    global gyro_data
    global screenUp
    gyro_data = sensor.get_gyro_data()
    
    # print("x: {:.2f}".format(gyro_data['x']))
    # print("y: {:.2f}".format(gyro_data['y']))
    # print("z: {:.2f}".format(gyro_data['z']))
    
    if (gyro_data['y'] <= -100 or  gyro_data['y'] >= 100) or (gyro_data['z'] <= -100 or gyro_data['z'] >= 100):
        screenUp = False
        #print('/////Down/////')
    else:
        screenUp = True
        #print('up')
     
if __name__ == '__main__':

    #Play the video 
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
                canFlip = False 
                downloadComplete = False
                
        sleep(0.8)
