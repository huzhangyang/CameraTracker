#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import cv2
import numpy
from gui_controller import GUIController
from video_controller import VideoController
from camera_tracker import CameraTracker

#Main Entrance
gui = GUIController('Camera Tracking')

filename = gui.readFile()
if filename == '' or filename == None:
    exit()
    
video = VideoController(filename)
if not video.isOpened():
    exit()

tracker = CameraTracker('MIL')
gui.initUI(video, tracker)

gui.cleanup()
'''
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
#video.close()
'''
