#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import cv2
import numpy
from scipy import optimize
from reconstruction import Reconstruction, Marker, Camera, TrackPoint
  
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
                        markers.append(Marker(i, j, int(split[0]), int(split[1])))

        K = numpy.mat([[focalLength, 0, centerX], [0, focalLength, centerY], [0, 0, 1]])

        Rs, Ts, points3D = self.reconstruct(K, imageSize, markers)
        #print(Rs, Ts, points3D)
    
############################## Key Algorithms #################################
     
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
            normalizedMarkers.append(Marker(m.frame, m.track, result.x[0], result.x[1]))
        #select two keyframes
        #keyframes = self.selectKeyFrames(normalizedMarkers, K)
        kf1, kf2 = 0, Marker.getMaxFrame(normalizedMarkers)
        #Actual reconstruction
        keyframeMarkers = Marker.markersForTracksInBothFrames(markers, kf1, kf2)
        if len(keyframeMarkers) < 8:
            print('Error: Not Enough Keyframe Markers.')
            return None, None, None
        
        maxFrame = Marker.getMaxFrame(markers)
        maxTrack = Marker.getMaxTrack(markers)
        reconstruction = Reconstruction(maxFrame, maxTrack) 
        
        self.reconstructTwoFrames(keyframeMarkers, reconstruction)
        #TODO: EuclideanBundle(normalized_tracks)
        self.completeReconstruction(normalizedMarkers, reconstruction)        
        #TODO: EuclideanBundleCommonIntrinsics
        self.scaleToUnity(reconstruction)
        #TODO: EuclideanReprojectionError        
        return reconstruction.extract() # K is refined but not returned here
    
    def selectKeyFrames(self, markers, K):

        def intrinsicsNormalizationMatrix(K):
            T = numpy.identity(3)
            S = numpy.identity(3)
            T[0, 2] = -K[0, 2]
            T[1, 2] = -K[1, 2]
            S[0, 0] /= K[0, 0]
            S[1, 1] /= K[1, 1]
            return S * T

        def estimateHomography2DFromCorrespondences(x1, x2):
            # TODO: IMPLEMENTION
            pass
        
        def estimateFundamentalFromCorrespondences(x1, x2):
            # TODO: IMPLEMENTION
            pass

        keyFrames = []
        maxFrame = Marker.getMaxFrame(markers)
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
            print('Processing Frame:', currentKeyframe)
            
            for candidate in range(currentKeyframe + 1, maxFrame + 1):
                allMarkers = Marker.markersInBothFramess(markers, currentKeyframe, candidate)
                trackedMarkers = Marker.markersForTracksInBothFrames(markers, currentKeyframe, candidate)
                # Correspondences in normalized space
                x1 = Marker.coordinatesForMarkersInFrame(trackedMarkers, currentKeyframe)
                x2 = Marker.coordinatesForMarkersInFrame(trackedMarkers, candidate)

                if x1.shape[1] < 8 or x2.shape[1] < 8:
                    continue
                
                # STEP 1: Correspondence ratio constraint
                rc = len(allMarkers) / len(trackedMarkers)
                if rc < 0.8 or rc > 1.0:
                    continue# Limit correspondence ratio
                
                H = estimateHomography2DFromCorrespondences(x1, x2)
                H = N.I * H * N;
                F = estimateFundamentalFromCorrespondences(x1, x2)
                F = N.I * F * N;
                # STEP2:
                # TODO: IMPLEMENTION
                
        return keyFrames
    
    def reconstructTwoFrames(self, markers, reconstruction):
        def preconditionerFromPoints(points):
            mean = numpy.mean(points, axis = 0)
            variance = numpy.var(points, axis = 0)
            xfactor = numpy.sqrt(2 / variance[0])
            yfactor = numpy.sqrt(2 / variance[1])
            #handle small value
            if variance[0] < 1e-8:
                xfactor = mean[0] = 1
            if variance[1] < 1e-8:
                yfactor = mean[1] = 1
                
            T = numpy.mat([[xfactor, 0, -xfactor * mean[0]], [0, yfactor, -yfactor * mean[1]],[0, 0, 1]])
            return T
        
        def applyTransformationToPoints(points, T):
            P = numpy.concatenate((points, numpy.ones([1, points.shape[1]])))
            P = T * P
            transformedPoints = P[:2] / P[2]#HomogeneousToEuclidean
            return transformedPoints
        
        def eightPointSolver(x1, x2):
            A = numpy.zeros([x1.shape[1], 9])
            for i in range(x1.shape[1]):
                A[i, 0] = x2[0, i] * x1[0, i]
                A[i, 1] = x2[0, i] * x1[1, i]
                A[i, 2] = x2[0, i]
                A[i, 3] = x2[1, i] * x1[0, i]
                A[i, 4] = x2[1, i] * x1[1, i]
                A[i, 5] = x2[1, i]
                A[i, 6] = x1[0, i]
                A[i, 7] = x1[1, i]
                A[i, 8] = 1
                
            U, S, V = numpy.linalg.svd(A)
            F = V[:,-1].reshape(3, 3)
            return F
        
        def enforceFundamentalRank2Constraint(F):
            U, S, V = numpy.linalg.svd(F)
            S[2] = 0
            F = U * numpy.diag(S) * V
            return F
            
        def normalizedEightPointSolver(x1, x2):
            #Normalize
            T1 = preconditionerFromPoints(x1)
            T2 = preconditionerFromPoints(x2)
            x1_normalized = applyTransformationToPoints(x1, T1)
            x2_normalized = applyTransformationToPoints(x2, T2)
            #estimate fundamental matrix
            F = eightPointSolver(x1_normalized, x2_normalized)
            F = enforceFundamentalRank2Constraint(F)
            #denormalize the fundamental matrix
            F = T2.T * F * T1
            return F
        
        def fundamentalToEssential(F):
            U, S, V = numpy.linalg.svd(F)
            s = (S[0] + S[1]) / 2
            E = U * numpy.diag(numpy.array([s, s, 0])) * V
            return E
        
        def triangulateDLT(P1, x1, P2, x2):
            design = numpy.zeros([4, 4])
            for i in range(4):
                design[0, i] = x1[0] * P1[2, i] - P1[0, i]
                design[1, i] = x1[1] * P1[2, i] - P1[1, i]
                design[2, i] = x2[0] * P2[2, i] - P2[0, i]
                design[3, i] = x2[1] * P2[2, i] - P2[1, i]
                
            U, S, V = numpy.linalg.svd(design)
            X = V[:,-1]
            X = X[:3] / X[3]#HomogeneousToEuclidean
            return numpy.mat(X).T
        
        def motionFromEssentialAndCorrespondence(E, x1, x2):
            U, S, V = numpy.linalg.svd(E)
            
            if numpy.linalg.det(U) < 0:
                U[:,-1] *= -1
                
            if numpy.linalg.det(V) < 0:
                V[-1] *= -1
                
            W = numpy.mat([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
            UWV = U * W * V
            UWTV = U * W.T * V
            
            Rs = [UWV, UWV, UWTV, UWTV]
            Ts = [U[:, -1], -U[:, -1], U[:, -1], -U[:, -1]]
            R1 = numpy.eye(3, 3)
            T1 = numpy.zeros(3)
            P1 = numpy.eye(3, 4)
            for i in range(4):
                P2 = numpy.concatenate((Rs[i], Ts[i]), axis = 1)
                X = triangulateDLT(P1, x1, P2, x2)
                d1 = (R1 * X)[2] + T1[2]
                d2 = (Rs[i] * X)[2] + Ts[i][2]
                if d1 > 0 and d2 > 0:
                    return Rs[i], Ts[i]
            
            print("Error: Motion From Essential Failed.")
            return None, None

        f1, f2 = Marker.getTwoFrameInMarkers(markers)
        x1 = Marker.coordinatesForMarkersInFrame(markers, f1)
        x2 = Marker.coordinatesForMarkersInFrame(markers, f2)
        F = normalizedEightPointSolver(x1, x2)
        #print(F)
        E = fundamentalToEssential(F)
        #print(E)
        R, T = motionFromEssentialAndCorrespondence(E, x1[:, 0], x2[:, 0])
        #print(R, T)
        reconstruction.setCamera(f1, numpy.identity(3), numpy.zeros(3))
        reconstruction.setCamera(f2, R, numpy.asarray(T).ravel())
    
    def completeReconstruction(self, markers, reconstruction):
        def intersect(reconstructedMarkers, reconstruction):
            # TODO: IMPLEMENTION
            return False
        
        def resect(reconstructedMarkers, reconstruction, finalPass):
            # TODO: IMPLEMENTION
            return False
        
        maxFrame = Marker.getMaxFrame(markers)
        maxTrack = Marker.getMaxTrack(markers)
        numResects = -1
        numIntersects = -1
        while numResects != 0 or numIntersects != 0:
            #Do all possible intersections
            numIntersects = 0
            for track in range(maxTrack):
                if reconstruction.pointForTrack(track) is not None:
                    continue

                allMarkers = Marker.markersForTrack(markers, track)
                reconstructedMarkers = []
                for i in range(len(allMarkers)):
                    if reconstruction.cameraForFrame(allMarkers[i].frame):
                        reconstructedMarkers.append(allMarkers[i])
                        
                if len(reconstructedMarkers) >= 2:
                    if intersect(reconstructedMarkers, reconstruction):
                        numIntersects += 1
                        
            #if numIntersects > 0:
                #bundle(markers, reconstruction)
                
            #Do all possible resections
            numResects = 0
            for frame in range(maxFrame):
                if reconstruction.cameraForFrame(frame) is not None:
                    continue
                
                allMarkers = Marker.markersForFrame(markers, frame)
                reconstructedMarkers = []
                for i in range(len(allMarkers)):
                    if reconstruction.pointForTrack(allMarkers[i].track):
                        reconstructedMarkers.append(allMarkers[i])
                        
                if len(reconstructedMarkers) >= 5:
                    if resect(reconstructedMarkers, reconstruction, False):
                        numIntersects += 1
                        
            #if numResects > 0:
                #bundle(markers, reconstruction)
            
            #One last pass
            numResects = 0
            for frame in range(maxFrame):
                if reconstruction.cameraForFrame(frame) is not None:
                    continue
                
                allMarkers = Marker.markersForFrame(markers, frame)
                reconstructedMarkers = []
                for i in range(len(allMarkers)):
                    if reconstruction.pointForTrack(allMarkers[i].track):
                        reconstructedMarkers.append(allMarkers[i])
                        
                if len(reconstructedMarkers) >= 5:
                    if resect(reconstructedMarkers, reconstruction, True):
                        numIntersects += 1
                        
            #if numResects > 0:
                #bundle(markers, reconstruction)
                
    def scaleToUnity(self, reconstruction):
        allCameras = reconstruction.getCameras()
        allPoints = reconstruction.getPoints()
        # Calculate center of the mass of all cameras
        massCenter = numpy.zeros(3)
        for camera in allCameras:
            massCenter += camera.T
        massCenter /= len(allCameras)
        # Find the most distant camera from the mass center
        maxDistance = 0
        for camera in allCameras:
            dis = numpy.linalg.norm(camera.T - massCenter)
            maxDistance = max(maxDistance, dis)
        
        if maxDistance < 1e-8:# too close
            return
        
        scale = 1 / numpy.sqrt(maxDistance)
        
        # Rescale cameras positions
        for camera in allCameras:
            camera.T *= scale
            
        # Rescale points positions
        for point in allPoints:       
            point.pos *= scale    
                        
                
