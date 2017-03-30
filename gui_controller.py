#Camera Tracker for CM50246 Visual Effect Coursework
#Zhangyang Hu 24/03/2017

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap
import cv2
import sys
import time

class MyWindow(QWidget):
    def __init__(self, controller, windowName):
        super().__init__()
        self.controller = controller
        self.resize(960, 720)
        self.move(300, 100)
        self.setWindowTitle(windowName)
        
        self.playButton = QPushButton('Play')
        self.trackButton = QPushButton('Track')
        self.frameBar = QScrollBar(0x1)
        self.frameText = QLabel('Frame:0')
        self.image = QLabel('Video')
        
        buttons = QHBoxLayout()
        buttons.addWidget(self.playButton)
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
        self.frameBar.valueChanged.connect(self.onFrameBar)

    def onPlayButton(self):
        if not self.controller.isPlaying:
            self.play()
        else:
            self.pause()        
    
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
   
    def readFile(self):
        fileName, filetype = QFileDialog.getOpenFileName(self.window, "Select a video file", "C:/", "All Files (*)")
        return fileName
    
    def initUI(self, video):
        self.video = video
        self.window.frameBar.setRange(0, video.totalFrame)
        self.showCurrentFrame()
        
    def showCurrentFrame(self):
        frame = cv2.cvtColor(self.video.currentFrame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.window.image.setPixmap(QPixmap.fromImage(image))

    def cleanup(self):
        self.app.exec_()
        
        


    
