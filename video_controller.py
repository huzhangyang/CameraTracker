#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import cv2
import numpy

class VideoController:
    def __init__(self, filename, windowName):
        self.__cap = cv2.VideoCapture(filename)
        self.totalFrame = 0
        self.fps = 0
        self.isPlaying = False
        self.currentFrame = None
        self.windowName = windowName
        
        if self.__cap.isOpened():
            self.totalFrame = int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.__cap.get(cv2.CAP_PROP_FPS)
        else:
            print('Error: Video file open failed.')
            
    def isOpened(self):
        return self.__cap.isOpened()
    
    def getPosition(self):
        return int(self.__cap.get(cv2.CAP_PROP_POS_FRAMES))
    
    def setPosition(self, pos):
        self.__cap.set(cv2.CAP_PROP_POS_FRAMES, pos);
        ret, self.currentFrame = self.__cap.read()
        if ret == True:
            cv2.imshow(self.windowName, self.currentFrame)
        return ret
    
    def play(self):
        self.isPlaying = True
        while(self.isPlaying):
            ret, self.currentFrame = self.__cap.read()
            if ret == True:
                cv2.setTrackbarPos('Frame', self.windowName, self.getPosition())
                cv2.imshow(self.windowName, self.currentFrame)
                cv2.waitKey(int(1000 / self.fps))
            
    def advance(self):
        ret, self.currentFrame = self.__cap.read()
        return ret
            
    def pause(self):
        self.isPlaying = False
        
    
    def close(self):
        self.__cap.release()
    
    
