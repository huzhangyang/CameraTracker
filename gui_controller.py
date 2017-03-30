#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QPoint, QRect, QSize, Qt
import cv2
import sys
import time

class MyImage(QLabel):
    def __init__(self):
        super().__init__()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
       
    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
            
    def mouseReleaseEvent(self, event):   
        if event.button() == Qt.LeftButton:
            pass

class MyWindow(QWidget):
    def __init__(self, controller, windowName):
        super().__init__()
        self.controller = controller
        self.resize(960, 720)
        self.move(300, 100)
        self.setWindowTitle(windowName)
        
        self.playButton = QPushButton('Play')
        self.addButton = QPushButton('AddToTracker')
        self.clearButton = QPushButton('ClearTracker')
        self.trackButton = QPushButton('Track')
        self.frameBar = QScrollBar(Qt.Horizontal)
        self.frameText = QLabel('Frame:0')
        self.image = MyImage()
        
        buttons = QHBoxLayout()
        buttons.addWidget(self.playButton)
        buttons.addWidget(self.addButton)
        buttons.addWidget(self.clearButton)
        buttons.addWidget(self.trackButton)
        
        frames = QHBoxLayout()
        frames.addWidget(self.frameText)
        frames.addWidget(self.frameBar)
        
        vbox = QVBoxLayout()
        vbox.addLayout(frames)
        vbox.addStretch(1)
        vbox.addLayout(buttons)    
        vbox.addStretch(1)
        vbox.addWidget(self.image)    
        vbox.addStretch(6)
        
        self.setLayout(vbox)      
        self.show()
        
        self.playButton.clicked.connect(self.onPlayButton)
        self.addButton.clicked.connect(self.onAddButton)
        self.clearButton.clicked.connect(self.onClearButton)
        self.trackButton.clicked.connect(self.onTrackButton)
        self.frameBar.valueChanged.connect(self.onFrameBar)

    def onPlayButton(self):
        if not self.controller.isPlaying:
            self.play()
        else:
            self.pause()
            
    def onAddButton(self):
        if self.image.rubberBand.isHidden():
            return
        
        self.image.rubberBand.hide()
        self.controller.addROI(self.image.rubberBand.geometry())

    def onTrackButton(self):
        if len(self.controller.rois) == 0:
            print('Nothing to track.')
            return
        
        self.trackButton.setText('Pause')
        self.controller.isPlaying = True
        while self.controller.isPlaying:
            ret = self.controller.video.advance()
            if ret:
                self.frameBar.setValue(self.controller.video.getPosition())
                self.controller.showCurrentFrame()
                self.controller.app.processEvents()
                self.controller.updateTracker()
            else:
                break     
        self.trackButton.setText('Track')
        
    def onClearButton(self):
        self.controller.tracker.reset()
        for roi in self.controller.rois:
            roi.hide()
        self.controller.rois.clear()
    
    def onFrameBar(self, value):
        self.frameText.setText('Frame:' + str(value))
        if not self.controller.isPlaying:
            self.controller.video.setPosition(value)
            self.controller.showCurrentFrame()
            
    def play(self):
        self.playButton.setText('Pause')
        self.controller.isPlaying = True
        while self.controller.isPlaying:
            ret = self.controller.video.advance()
            if ret:
                self.frameBar.setValue(self.controller.video.getPosition())
                self.controller.showCurrentFrame()
                self.controller.app.processEvents()
                time.sleep(1.0 / self.controller.video.fps)
            else:
                self.pause();
                break
    
    def pause(self):
        self.playButton.setText('Play')
        self.controller.isPlaying = False
        

class GUIController:
    def __init__(self, windowName):
        self.app = QApplication(sys.argv)
        self.window = MyWindow(self, windowName)
        self.isPlaying = False
        self.rois = []
   
    def readFile(self):
        fileName, filetype = QFileDialog.getOpenFileName(self.window, "Select a video file", "C:/", "All Files (*)")
        return fileName
    
    def initUI(self, video, tracker):
        self.video = video
        self.tracker = tracker
        self.window.frameBar.setRange(0, video.totalFrame)
        self.showCurrentFrame()
        
    def showCurrentFrame(self):
        frame = cv2.cvtColor(self.video.currentFrame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.window.image.setPixmap(QPixmap.fromImage(image))
        
    def addROI(self, geometry):
        self.tracker.addROI(self.video.currentFrame, geometry.getCoords())
        print(roi, ' was add to tracker.')
        #duplicate for display
        copy = QRubberBand(QRubberBand.Rectangle, self.window.image)
        copy.setGeometry(geometry)
        copy.show()
        self.rois.append(copy)  
        
    def updateTracker(self):
        result = tracker.track(self.controller.video.currentFrame)
        if result == None:
            self.isPlaying = False
        
        print('y')
        
        for i in len(result):
            self.rois[i].setGeometry(QRect(result[i]))           
        print('Z')
        
    def cleanup(self):
        self.app.exec_()
        
        


    
