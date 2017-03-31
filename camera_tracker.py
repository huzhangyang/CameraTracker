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
        self.trackResult = []
        
    def track(self, frame):
        result = self.__tracker.update(frame)
        self.trackResult.append(result)
        if result[0] == False:
            print('Warning: Tracking Failed.')
            return None
        else:
            return result[1]

    def output(self):
        with open('out.txt', 'w') as file:
            
            for result in self.trackResult:
                if result[0] == False:
                    break
                
                for singleResult in result[1]:
                    px = int(singleResult[0] + singleResult[2] / 2)
                    py = int(singleResult[1] + singleResult[3] / 2)
                    file.writelines([str(px), ',', str(py), ' '])
                file.write('\n')
                
    def solve(self, focalLength, centerX, centerY):
        if len(self.trackResult) < 50:
            print('Error: Not Enough Tracking Data.')
            return
        
        # TODO
        print('Solve! ', focalLength, ',', centerX, ',', centerY)