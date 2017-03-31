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
                
    def solve(self, focalLength, centerX, centerY, filename):
        with open(filename) as file:
            content = file.readlines()
            if len(content) < 50:
                print('Error: Not Enough Tracking Data.')
                return
            
            numOfTracks = len(content[0].split(' ')) - 1 # strip \n
            points2D = numpy.zeros([numOfTracks, len(content), 2])
            for i in range(len(content)):
                tracks = content[i].split(' ')
                for j in range(numOfTracks):
                    split = tracks[j].split(',')
                    if len(split) != 2:
                        continue 

                    points2D[j, i, 0] = int(split[0])
                    points2D[j, i, 1] = int(split[1])
                
        K = numpy.mat([[focalLength, 0, centerX], [0, focalLength, centerY], [0, 0, 1]])

        Rs, Ts, points3D = self.reconstruct(K, points2D)
        
    def reconstruct(self, K, points2D):
        #TODO
        return None, None, None