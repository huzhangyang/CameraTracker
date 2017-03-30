#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import cv2
import numpy

class CameraTracker:
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.__tracker = cv2.MultiTracker(algorithm)
        self.trackResult = []
    
    def addROI(self, frame, roi):
        self.__tracker.add(frame, roi)
        
    def reset(self):
        self.__tracker = cv2.MultiTracker(self.algorithm)
        
    def track(self, frame):
        print('x')
        result = self.__tracker.update(frame)
        print('y')
        if result[0] == False:
            print('Warning: Tracking Failed.')
            return None
        else:
            return result[1]

    def output(self, index = 0):
        with open('out.txt', 'w') as file:
            for result in self.trackResult:
                if result[0] == True:
                    px = int(result[1][0][0] + result[1][0][2] / 2)
                    py = int(result[1][0][1] + result[1][0][3] / 2)
                    file.writelines([str(px), ' ', str(py), ' '])
                else:
                    file.writelines(['-1 -1 '])