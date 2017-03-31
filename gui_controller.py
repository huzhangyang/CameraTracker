#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap, QDoubleValidator
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
        self.setWindowTitle(windowName)
        
        self.playButton = QPushButton('Play')
        self.addButton = QPushButton('AddToTracker')
        self.clearButton = QPushButton('ClearTracker')
        self.trackButton = QPushButton('Track')
        self.solveButton = QPushButton('Solve')

        self.focalLengthText = QLabel('Focal Length')
        self.focalLengthEdit = QLineEdit('900')
        self.centerXText = QLabel('Optical Center X')
        self.centerXEdit = QLineEdit('960')
        self.centerYText = QLabel('Optical Center Y')
        self.centerYEdit = QLineEdit('540')
        self.frameText = QLabel('Frame:0')
        self.frameBar = QScrollBar(Qt.Horizontal)
        self.image = MyImage()
        
        buttons = QHBoxLayout()
        buttons.addWidget(self.playButton)
        buttons.addWidget(self.addButton)
        buttons.addWidget(self.clearButton)
        buttons.addWidget(self.trackButton)
        buttons.addWidget(self.solveButton)
        
        frames = QHBoxLayout()
        frames.addWidget(self.focalLengthText)
        frames.addWidget(self.focalLengthEdit)
        frames.addWidget(self.centerXText)
        frames.addWidget(self.centerXEdit)
        frames.addWidget(self.centerYText)
        frames.addWidget(self.centerYEdit)
        frames.addWidget(self.frameText)
        frames.addWidget(self.frameBar)
        frames.addStretch(10)
        
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
        self.solveButton.clicked.connect(self.onSolveButton)
        self.frameBar.valueChanged.connect(self.onFrameBar)
        
        validator = QDoubleValidator()
        self.focalLengthEdit.setValidator(validator)
        self.centerXEdit.setValidator(validator)
        self.centerYEdit.setValidator(validator)

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
        if len(self.controller.rois) < 5:
            print('Error: Not enough points to track.')
            return
        
        self.trackButton.setText('Pause')
        if not self.controller.isPlaying: 
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
            self.controller.tracker.output()
        else:
            self.controller.isPlaying = False
            
    def onSolveButton(self):
        fl = float(self.focalLengthEdit.text())
        cx = float(self.centerXEdit.text())
        cy = float(self.centerYEdit.text())
        filename = self.controller.readFile('Select a track file:')
        self.controller.tracker.solve(fl, cx, cy, filename)
        
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
   
    def readFile(self, title):
        fileName, filetype = QFileDialog.getOpenFileName(self.window, title, "C:/", "All Files (*)")
        return fileName
    
    def initUI(self, video, tracker):
        self.video = video
        self.tracker = tracker
        self.window.frameBar.setRange(0, video.totalFrame)
        self.window.frameBar.setFixedWidth(video.getSize()[0] / 2)
        self.showCurrentFrame()
        
    def showCurrentFrame(self):
        frame = cv2.cvtColor(self.video.currentFrame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.window.image.setPixmap(QPixmap.fromImage(image))
        
    def addROI(self, geometry):
        roi = geometry.getRect()
        self.tracker.addROI(self.video.currentFrame, roi)
        #duplicate for display
        copy = QRubberBand(QRubberBand.Rectangle, self.window.image)
        copy.setGeometry(geometry)
        copy.show()
        self.rois.append(copy)  
        
    def updateTracker(self):
        result = self.tracker.track(self.video.currentFrame)
        if result is None:
            self.isPlaying = False
        
        for i in range(len(result)):
            rect = QRect(result[i][0], result[i][1], result[i][2], result[i][3])
            self.rois[i].setGeometry(rect)
        
    def cleanup(self):
        self.app.exec_()
        
        


    
