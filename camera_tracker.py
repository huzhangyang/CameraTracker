#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import cv2
import numpy
from scipy import optimize

#marker: n-th frame, m-th track, pointX, pointY   
class marker:
    def __init__(self, frame, track, x, y):
        self.frame = frame
        self.track = track
        self.x = x
        self.y = y
        

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
                
    def solve(self, focalLength, centerX, centerY, imageSize, filename):
        with open(filename) as file:
            content = file.readlines()
            if len(content) < 50:
                print('Error: Not Enough Tracking Data.')
                return
            
            numOfTracks = len(content[0].split(' ')) - 1 # strip \n
            markers = []
            for i in range(len(content)):
                tracks = content[i].split(' ')
                for j in range(numOfTracks):
                    split = tracks[j].split(',')
                    if len(split) == 2:
                        markers.append(marker(i, j, int(split[0]), int(split[1])))

        K = numpy.mat([[focalLength, 0, centerX], [0, focalLength, centerY], [0, 0, 1]])

        Rs, Ts, points3D = self.reconstruct(K, imageSize, markers)
    
     
    def reconstruct(self, K, imageSize, markers):
        
        def normalizeMarkersCostFunction(parameters):
            x = parameters[0]
            y = parameters[1]
            
            r2 = x*x + y*y
            r4 = r2*r2
            r6 = r4*r2
            r_coeff = 1 + k1*r2 + k2*r4 + k3*r6
            xx = K[0, 0]*x*r_coeff + K[0, 2]
            yy = K[1, 1]*y*r_coeff + K[1, 2]
            
            return xx - m.x, yy - m.y
        
        k1, k2, k3 = 0, 0, 0 # polynomial radial distortion
        #Normalize markers
        normalizedMarkers = []
        for m in markers:
            initParams = numpy.zeros(2)
            initParams[0] = (m.x - K[0, 2]) / K[0, 0]
            initParams[1] = (m.y - K[1, 2]) / K[1, 1]
            result = optimize.root(normalizeMarkersCostFunction, initParams, method='lm')
            #print(initParams[0], initParams[1], m.x, m.y, result.x[0], result.x[1])
            normalizedMarkers.append(marker(m.frame, m.track, result.x[0], result.x[1]))
        #select two keyframes
        keyframes = self.selectKeyFrames(normalizedMarkers, K)
        #TODO
        return None, None, None
    
    def selectKeyFrames(self, markers, K):
        
        def getMaxFrame(markers):
            maxFrame = 0
            for m in markers:
                maxFrame = max(m.frame, maxFrame)
            return maxFrame
        
        def markersInBothFramess(markers, frame1, frame2):
            ret = []
            for m in markers:
                if m.frame == frame1 or m.frame == frame2:
                    ret.append(m)
            return ret
        
        def markersForTracksInBothFrames(markers, frame1, frame2):
            tracks1 = []
            tracks2 = []
            for m in markers:
                if m.frame == frame1:
                    tracks1.append(m.track)
                elif m.frame == frame2:
                    tracks2.append(m.track)
            
            intersection = [val for val in tracks1 if val in tracks2]
            ret = []
            for m in markers:
                if m.frame == frame1 or m.frame == frame2:
                    if m.track in intersection:
                        ret.append(m)
                        
            return ret
        
        def intrinsicsNormalizationMatrix(K):
            T = numpy.identity(3)
            S = numpy.identity(3)
            T[0, 2] = -K[0, 2]
            T[1, 2] = -K[1, 2]
            S[0, 0] /= K[0, 0]
            S[1, 1] /= K[1, 1]
            return S * T
        
        def coordinatesForMarkersInFrame(markers, frame):
            coords = []
            for m in markers:
                if m.frame == frame:
                    coords.append([m.x, m.y])
                    
            coordinates = numpy.zeros([2, len(coords)])
            for i in range(len(coords)):
                coordinates[0, i] = coords[i][0]
                coordinates[1, i] = coords[i][1]
            return coordinates

        keyFrames = []
        maxFrame = getMaxFrame(markers)
        nextKeyframe = 1
        numKeyframe = 0
        N = intrinsicsNormalizationMatrix(K)
        
        Sc_best = numpy.finfo(numpy.float).max
        success_intersects_factor_best = 0
        
        while nextKeyframe != -1:#found keyframe
            currentKeyframe = nextKeyframe
            Sc_best_candidate = numpy.finfo(numpy.float).max
            numKeyframe += 1
            nextKeyframe = -1
            
            for candidate in range(currentKeyframe + 1, maxFrame + 1):
                allMarkers = markersInBothFramess(markers, currentKeyframe, candidate)
                trackedMarkers = markersForTracksInBothFrames(markers, currentKeyframe, candidate)
                # Correspondences in normalized space
                x1 = coordinatesForMarkersInFrame(trackedMarkers, currentKeyframe)
                x2 = coordinatesForMarkersInFrame(trackedMarkers, candidate)
                
                print(x1.shape, x2.shape)
                
                if x1.shape[1] < 8 or x2.shape[1] < 8:
                    continue
                
                # STEP 1: Correspondence ratio constraint
                
        return keyFrames
    
