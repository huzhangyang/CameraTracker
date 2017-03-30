#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import cv2
import numpy

class VideoController:
    def __init__(self, filename):
        self.__cap = cv2.VideoCapture(filename)
        self.totalFrame = 0
        self.fps = 0
        self.currentFrame = None
        
        if self.__cap.isOpened():
            self.totalFrame = int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
            self.fps = self.__cap.get(cv2.CAP_PROP_FPS)
            self.setPosition(0)
        else:
            print('Error: Video file open failed.')
            
    def isOpened(self):
        return self.__cap.isOpened()
    
    def getPosition(self):
        return int(self.__cap.get(cv2.CAP_PROP_POS_FRAMES))
    
    def setPosition(self, pos):
        self.__cap.set(cv2.CAP_PROP_POS_FRAMES, pos);
        ret, self.currentFrame = self.__cap.retrieve()
        return ret
            
    def advance(self):
        ret, self.currentFrame = self.__cap.read()
        return ret 
    
    def close(self):
        self.__cap.release()
    
    
