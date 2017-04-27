#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

import numpy

#marker: n-th frame, m-th track, pointX, pointY   
class Marker:
    def __init__(self, frame, track, x, y):
        self.frame = frame
        self.track = track
        self.x = x
        self.y = y
        
    def getMaxFrame(markers):
        maxFrame = 0
        for m in markers:
            maxFrame = max(m.frame, maxFrame)
        return maxFrame
    
    def getMaxTrack(markers):
        maxTrack = 0
        for m in markers:
            maxTrack = max(m.track, maxTrack)
        return maxTrack
    
    def getTwoFrameInMarkers(markers):
        f1, f2 = -1, -1
        f1 = markers[0].frame
        for m in markers:
            if m.frame != f1:
                f2 = m.frame
                break
        return f1, f2           
    
    def markersInBothFramess(markers, frame1, frame2):
        ret = []
        for m in markers:
            if m.frame == frame1 or m.frame == frame2:
                ret.append(m)
        return ret
    
    def markersForTrack(markers, track):
        ret = []
        for m in markers:
            if m.track == track:
                ret.append(m)
        return ret
    
    def markersForFrame(markers, frame):
        ret = []
        for m in markers:
            if m.frame == frame:
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
    
class Camera:
    def __init__(self, frame, R, T):
        self.frame = frame
        self.R = R
        self.T = T
        
class TrackPoint:
    def __init__(self, track, pos):
        self.track = track
        self.pos = pos
    
class Reconstruction:
    def __init__(self, maxFrame, maxTrack):
        self.cameras = [] # the location and rotation of the camera viewing at an image
        self.points = [] # the 3D location of a track
        for i in range(maxFrame + 1):
            self.cameras.append(Camera(-1, numpy.zeros([3, 3]), numpy.zeros(3)))
        for i in range(maxTrack + 1):
            self.points.append(TrackPoint(-1, numpy.zeros(3)))
        
    def setCamera(self, frame, R, T):
        self.cameras[frame] = Camera(frame, R, T)
    
    def setPoint(self, track, pos):
        self.points[track] = TrackPoint(track, pos)
        
    def pointForTrack(self, track):
        point = self.points[track]
        if point.track != -1:
            return point
        return None
    
    def cameraForFrame(self, frame):
        camera = self.cameras[frame]
        if camera.frame != -1:
            return camera
        return None
