import os
import VLC
from urllib.parse import quote
from QJumpSlider import QJumpSlider
from PyQt6.QtGui import QFont
from PyQt6.QtCore import (
    Qt, 
    QSize, 
    QTimer,
)
from PyQt6.QtWidgets import (
    QPushButton, 
    QHBoxLayout, 
    QStyle,
    QSlider,
    QLabel,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class QAudioPlayer(QWidget):
    def __init__(self, parent=None):
        super(QAudioPlayer, self).__init__(parent)
        
        self.vlc_instance = VLC.Instance("prefer-insecure")
        self.vlc_mediaPlayer = self.vlc_instance.media_player_new()

        btnSize = QSize(16, 16)

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
        
        self.currentPlaybackTimeLabel = QLabel('--:--')
        self.currentPlaybackTimeLabel.setFont(QFont("Noto Sans", 7))
        
        self.durationLabel = QLabel('--:--')
        self.durationLabel.setFont(QFont("Noto Sans", 7))

        self.positionSlider = QJumpSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setMaximum(1000)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.pressed.connect(self.setPosition)
        
        self.volumeSlider = QJumpSlider(Qt.Orientation.Horizontal)
        self.volumeSlider.setMaximum(200)
        self.volumeSlider.setValue(50)
        self.volumeSlider.valueChanged.connect(self.setVolume)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.currentPlaybackTimeLabel)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.durationLabel)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.playButton)
        buttonLayout.addWidget(self.stopButton)
        buttonLayout.addWidget(self.volumeSlider, 25)
        
        layout = QVBoxLayout()
        layout.addWidget(self.statusBar)
        layout.addLayout(controlLayout)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateUI)
    
    
    def setSource(self, filePath):
        if filePath != '':
            self.stop()
            print(filePath)
            print(filePath.replace(' ', '%20'))
            self.media = self.vlc_instance.media_new(filePath.replace(' ', '%20'))
            self.vlc_mediaPlayer.set_media(self.media)
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.statusBar.showMessage(''.join(os.path.basename(filePath)).split('.')[0])
            
            self.media.parse_with_options(1)
            while True:
                if self.media.is_parsed():
                    # TODO c'est moche
                    break
            
            self.setDuration()
                
            
            
    def getDuration(self):
        if self.media.is_parsed():
            return self.media.get_duration()
        else:
            return 0
        
        
    def setDuration(self):
        if self.media.is_parsed():
            milliseconds = self.media.get_duration()
            seconds = milliseconds // 1000
            hours = seconds // 3600
            seconds = seconds % 3600
            minutes = seconds // 60
            seconds = seconds % 60
            if hours > 0.:
                self.durationLabel.setText('%02d:%02d:%02d' % (hours, minutes, seconds))
                self.currentPlaybackTimeLabel.setText('00:00:00')
            else:
                self.durationLabel.setText('%02d:%02d' % (minutes, seconds))
                self.currentPlaybackTimeLabel.setText('00:00')
        else:
            self.durationLabel.setText('--:--')
            self.currentPlaybackTimeLabel.setText('--:--')
     
            
    def updateTime(self):
        if (milliseconds := self.vlc_mediaPlayer.get_time()) > 0:
            seconds = milliseconds // 1000
            hours = seconds // 3600
            seconds = seconds % 3600
            minutes = seconds // 60
            seconds = seconds % 60
            if len(self.durationLabel.text()) > 5:
                self.currentPlaybackTimeLabel.setText('%02d:%02d:%02d' % (hours, minutes, seconds))
            else:
                self.currentPlaybackTimeLabel.setText('%02d:%02d' % (minutes, seconds))

            
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
        self.vlc_mediaPlayer.stop()
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)) 
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))  
        self.positionSlider.setValue(self.positionSlider.minimum())
        if len(self.durationLabel.text()) > 5:
            self.currentPlaybackTimeLabel.setText('00:00:00')
        else:
            self.currentPlaybackTimeLabel.setText('00:00')


    def setVolume(self, Volume):
        self.vlc_mediaPlayer.audio_set_volume(Volume)
        

    def setPosition(self, position):
        # setting the position to where the slider was dragged
        self.vlc_mediaPlayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)
        

    def updateUI(self):
        # setting the slider to the desired position
        self.positionSlider.setValue(self.vlc_mediaPlayer.get_position() * 1000)
        self.updateTime()

        if not self.vlc_mediaPlayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                self.stop()


    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.vlc_mediaPlayer.errorString())
