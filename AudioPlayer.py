import os
import VLC
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtCore import (
    Qt, 
    QSize, 
    QTimer
)
from PyQt6.QtWidgets import (
    QPushButton, 
    QHBoxLayout, 
    QStyle,
    QSlider,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class AudioPlayer(QWidget):

    def __init__(self, parent=None):
        super(AudioPlayer, self).__init__(parent)
        
        self.vlc_instance = VLC.Instance()
        self.vlc_mediaPlayer = self.vlc_instance.media_player_new()

        # self.mediaPlayer = QMediaPlayer()
        # self.audio_output = QAudioOutput()

        btnSize = QSize(16, 16)
        # videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        
        self.stopButton = QPushButton()
        self.stopButton.setEnabled(False)
        self.stopButton.setFixedHeight(24)
        self.stopButton.setIconSize(btnSize)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stopButton.clicked.connect(self.stop)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setMaximum(1000)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        
        self.volumeSlider = QSlider(Qt.Orientation.Horizontal)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(self.vlc_mediaPlayer.audio_get_volume())
        self.volumeSlider.setToolTip("Volume")
        
        

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.positionSlider)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.playButton)
        buttonLayout.addWidget(self.stopButton)
        buttonLayout.addWidget(self.volumeSlider, 25)
        
        layout = QVBoxLayout()
        layout.addLayout(controlLayout)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)
        
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateUI)
    
    def setSource(self, filePath):
        if filePath != '':
            self.media = self.vlc_instance.media_new(filePath)
            self.vlc_mediaPlayer.set_media(self.media)
            
            
            
            # self.mediaPlayer.setSource(QUrl.fromLocalFile(filePath))
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.statusBar.showMessage(''.join(os.path.basename(filePath)).split('.')[0])
            # self.play()

    def play(self):
        if self.vlc_mediaPlayer.is_playing():
            self.vlc_mediaPlayer.pause()
            self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.isPaused = True
        else:
            self.vlc_mediaPlayer.play()
            self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.timer.start()
            self.isPaused = False
            
    def stop(self):
        """Stop player
        """
        self.vlc_mediaPlayer.stop()
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)) 
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))      

    def setVolume(self, Volume):
        """Set the volume
        """
        self.vlc_mediaPlayer.audio_set_volume(Volume)

    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.vlc_mediaPlayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionSlider.setValue(self.vlc_mediaPlayer.get_position() * 1000)

        if not self.vlc_mediaPlayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.stop()

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.vlc_mediaPlayer.errorString())
