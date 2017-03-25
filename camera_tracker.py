#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import cv2
import numpy

class CameraTracker:
    def __init__(self, windowName):
        self.__tracker = cv2.MultiTracker("MIL")
        self.windowName = windowName
        self.trackResult = []
        self.roi = None
    
    def selectROI(self, frame):
        self.roi = cv2.selectROI(self.windowName, frame, False, False)
        self.__tracker.add(frame, self.roi)
        
    def track(self, frame):
        if self.roi == None:
            print('Error: Region of Interest not selected.')
            return None, None
        
        result = self.__tracker.update(frame)
        self.trackResult.append(result)
        if result[0] == True:
            p1 = (int(result[1][0][0]), int(result[1][0][1]))
            p2 = (int(result[1][0][0] + result[1][0][2]), int(result[1][0][1] + result[1][0][3]))
            return p1, p2
        else:
            print('Warning: Tracking Failed.')
            return None, None
        
    def output(self, index = 0):
        return self.trackResult