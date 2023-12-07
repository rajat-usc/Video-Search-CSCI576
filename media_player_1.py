import sys
from PyQt5.QtCore import Qt, QUrl, QSizeF
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QApplication,
                             QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
                             QSlider, QLabel)
import sys
from consecutive_matching import get_video_clip
from text_matching.QueryTextMatcher import QueryTextMatcher
from frame_matching.QueryFrameMatcher import QueryFrameMatcher
import os

class VideoPlayer(QMainWindow):
    def __init__(self, filename=None, startTime=0, startFrame=0):
        super().__init__()
        self.setWindowTitle("CSCI-576 Project")
        self.startTime = startTime * 1000 # COnvert to milliseconds
        self.startFrame = startFrame

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.videoItem = QGraphicsVideoItem()
        self.mediaPlayer.setVideoOutput(self.videoItem)

        self.scene = QGraphicsScene(self)
        self.scene.addItem(self.videoItem)
        self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setFixedSize(352, 288)  #Dimensions of video

        self.playButton = QPushButton("PLAY")
        self.playButton.clicked.connect(self.playVideo)
        self.playButton.setFixedWidth(100)

        self.pauseButton = QPushButton("PAUSE")
        self.pauseButton.clicked.connect(self.pauseVideo)
        self.pauseButton.setFixedWidth(100)

        self.resetButton = QPushButton("RESET")
        self.resetButton.clicked.connect(self.resetVideo)
        self.resetButton.setFixedWidth(100)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.startFrameLabel = QLabel(f"Start Frame: {self.startFrame}")
        self.startFrameLabel.setAlignment(Qt.AlignCenter)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(self.playButton)
        buttonsLayout.addWidget(self.pauseButton)
        buttonsLayout.addWidget(self.resetButton)
        
        buttonsWidget = QWidget()
        buttonsWidget.setLayout(buttonsLayout)
        # buttonsWidget.setFixedWidth(650)

        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        controlLayout = QVBoxLayout()
        controlLayout.addWidget(self.graphicsView)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(buttonsWidget) 
        controlLayout.addWidget(self.startFrameLabel)

        centralWidget = QWidget(self)
        centralWidget.setLayout(controlLayout)
        self.setCentralWidget(centralWidget)

        if filename is not None:
            self.loadVideo(filename)

    def loadVideo(self, filename):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
        self.mediaPlayer.setPosition(self.startTime)
        self.mediaPlayer.play()

    def playVideo(self):
        self.mediaPlayer.play()

    def pauseVideo(self):
        self.mediaPlayer.pause()

    def resetVideo(self):
        print(self.startTime)
        self.mediaPlayer.setPosition(self.startTime)

    def mediaStateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playButton.setEnabled(False)
            self.pauseButton.setEnabled(True)
        else:
            self.playButton.setEnabled(True)
            self.pauseButton.setEnabled(False)

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def resizeEvent(self, event):
        super(VideoPlayer, self).resizeEvent(event)
        sizeF = QSizeF(self.graphicsView.size())
        self.videoItem.setSize(sizeF)
