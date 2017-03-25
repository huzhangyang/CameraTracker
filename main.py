#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import cv2
import numpy
from video_controller import VideoController
from camera_tracker import CameraTracker

def OnTrackBarChange(pos):
    global frameCount
    frameCount = pos
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

frameCount = 0
playing = 0

print('Welcome to Camera Tracker. Please Input the name of file to inspect.')
#filename = input()
filename = "c:/source.mp4" # use test file

video = VideoController(filename, WINDOW_NAME)
tracker = CameraTracker(WINDOW_NAME)

if video.isOpened():
    cv2.namedWindow(WINDOW_NAME)
    cv2.createTrackbar('Frame', WINDOW_NAME, frameCount, video.totalFrame, OnTrackBarChange)
    cv2.createTrackbar('Playing', WINDOW_NAME, playing, 1, OnPlayingChange)
    video.setPosition(0)
    tracker.selectROI(video.currentFrame)
    playing = 1
    while(video.advance()):
        p1, p2 = tracker.track(video.currentFrame)
        if p1 is not None and p2 is not None:
            cv2.rectangle(video.currentFrame, p1, p2, (0, 0, 255), 2, 1)
        
        cv2.setTrackbarPos('Frame', WINDOW_NAME, video.getPosition())
        cv2.imshow(WINDOW_NAME, video.currentFrame)
        cv2.waitKey(1)
    tracker.output()
    #cv2.destroyAllWindows()
    #video.close()


