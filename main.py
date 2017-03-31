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