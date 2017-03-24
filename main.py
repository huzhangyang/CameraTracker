#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import cv2
import numpy
from video_controller import VideoController

def OnTrackBarChange(pos):
    global currentFrame
    currentFrame = pos
    if playing == 0:
        video.setPosition(pos)

def OnPlayingChange(pos):
    global playing
    playing = pos
    if pos == 1:
        video.play()
    else:
        video.pause()
    
#Main Entrance
WINDOW_NAME = 'Camera Tracking'

currentFrame = 0
playing = 0

print('Welcome to Camera Tracker. Please Input the name of file to inspect.')
#filename = input()
filename = "c:/source.mp4" # use test file

video = VideoController(filename, WINDOW_NAME)

if video.isOpened():
    cv2.namedWindow(WINDOW_NAME)
    cv2.createTrackbar('Frame', WINDOW_NAME, currentFrame, video.totalFrame, OnTrackBarChange)
    cv2.createTrackbar('Playing', WINDOW_NAME, playing, 1, OnPlayingChange)
    video.setPosition(0)
    #cv2.destroyAllWindows()
    #video.close()


