import os
import modules.VLC as VLC
from modules.Base64_Assets import *
from modules.VoxCaster_db import *
from modules.QJumpSlider import QJumpSlider
from PyQt6.QtGui import QFont
from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QKeySequence,
    QShortcut)
from PyQt6.QtCore import (
    Qt, 
    QSize, 
    QTimer,
    pyqtSignal,
    QByteArray
)
from PyQt6.QtWidgets import (
    QPushButton, 
    QHBoxLayout, 
    QStyle,
    QLabel,
    QStatusBar,
    QVBoxLayout,
    QWidget
)

def iconFromBase64(base64):
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray.fromBase64(base64))
    icon = QIcon(pixmap)
    return icon


class QAudioPlayer(QWidget):
    
    mediaPlayerEndReached = pyqtSignal(bool)
    spacebarPressed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(QAudioPlayer, self).__init__(parent)
        
        self.vlc_instance = VLC.Instance("prefer-insecure")
        self.vlc_mediaPlayer = self.vlc_instance.media_player_new()
        self.vlc_event_listener  = self.vlc_mediaPlayer.event_manager()
        self.media = None
        self.media_filepath = ''
        
        self.vlc_event_listener  = self.vlc_mediaPlayer.event_manager()
        self.vlc_event_listener.event_attach(VLC.EventType.MediaPlayerEndReached, self.event_handler)
        
        # keyboard shortcuts
        self.spacebarEvent = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.spacebarEvent.activated.connect(self.spacebar_event)
     
        btnSize = QSize(16, 16)
        
        self.statusBar = QStatusBar()
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)
        
        self.currentPlaybackTimeLabel = QLabel('--:--')
        self.currentPlaybackTimeLabel.setFont(QFont("Noto Sans", 7))
         
        self.positionSlider = QJumpSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setMaximum(1000)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.pressed.connect(self.setPosition)
        
        self.durationLabel = QLabel('--:--')
        self.durationLabel.setFont(QFont("Noto Sans", 7))
        
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.currentPlaybackTimeLabel)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.durationLabel)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setFixedWidth(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        
        self.stopButton = QPushButton()
        self.stopButton.setEnabled(False)
        self.stopButton.setFixedHeight(24)
        self.stopButton.setFixedWidth(24)
        self.stopButton.setIconSize(btnSize)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stopButton.clicked.connect(self.stop)
        
        self.volumeSlider = QJumpSlider(Qt.Orientation.Horizontal)
        self.volumeSlider.setMaximum(200)
        self.volumeSlider.setValue(50)
        self.volumeSlider.setFixedWidth(150)
        self.volumeSlider.valueChanged.connect(self.setVolume)
        
        self.volume_icon = QLabel()
        self.volume_icon.setPixmap(iconFromBase64(BASE64_ICON_SOUND).pixmap(QSize(12, 12)))
        
        self.volumeStatusBar = QLabel()
        self.volumeStatusBar.setText('50%')
        self.volumeStatusBar.setFixedHeight(24)
        self.volumeStatusBar.setFixedWidth(28)
        
        volumeLayout = QHBoxLayout()
        volumeLayout.addWidget(self.volume_icon)
        volumeLayout.addWidget(self.volumeStatusBar)
        volumeLayout.addWidget(self.volumeSlider)
        volumeLayout.insertStretch(0, 1)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.playButton)
        buttonLayout.addWidget(self.stopButton)
        
        bottomLayout = QHBoxLayout()
        bottomLayout.addLayout(buttonLayout)
        bottomLayout.addLayout(volumeLayout)
        
        layout = QVBoxLayout()
        layout.addWidget(self.statusBar)
        layout.addLayout(controlLayout)
        layout.addLayout(bottomLayout)
        
        self.setLayout(layout)
        
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateUI)
    
    
    def setSource(self, filePath):
        if filePath != '':
            self.stop()
            self.media_filepath = filePath
            self.media = self.vlc_instance.media_new(filePath.replace(' ', '%20'))
            self.vlc_mediaPlayer.set_media(self.media)
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.statusBar.showMessage(''.join(os.path.basename(filePath)).split('.')[0])
            self.play()
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
            
                      
    def updateDuration(self):
        milliseconds = self.media.get_duration()
        seconds = milliseconds // 1000
        hours = seconds // 3600
        seconds = seconds % 3600
        minutes = seconds // 60
        seconds = seconds % 60
        if hours > 0.:
            self.durationLabel.setText('%02d:%02d:%02d' % (hours, minutes, seconds))
        else:
            self.durationLabel.setText('%02d:%02d' % (minutes, seconds))
     
     
    # jump 10 seconds forward 
    def jump_forward(self):
        if self.media:
            current_time = self.vlc_mediaPlayer.get_time()
            if current_time + 10000 < self.media.get_duration():
                self.vlc_mediaPlayer.set_time(current_time + 10000)
                self.updateUI()
            else: 
                duration = self.media.get_duration()
                self.vlc_mediaPlayer.set_time(duration - 2000)
                self.updateUI()
            
    
    # jump 10 seconds backward 
    def jump_backward(self):
        if self.media:
            current_time = self.vlc_mediaPlayer.get_time()
            if current_time - 10000 > 0:
                self.vlc_mediaPlayer.set_time(current_time - 10000)
                self.updateUI()
            else: 
                self.vlc_mediaPlayer.set_time(0)
                self.updateUI()
     
     
    # in case it wasn't set properly at lauch      
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


    def isPlaying(self):
        return self.vlc_mediaPlayer.is_playing()
        
               
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
        self.volumeStatusBar.setText(f'{Volume}%')
        if not Volume:
            self.volume_icon.setPixmap(iconFromBase64(BASE64_ICON_MUTE).pixmap(QSize(12, 12)))
        else:
            self.volume_icon.setPixmap(iconFromBase64(BASE64_ICON_SOUND).pixmap(QSize(12, 12)))

    def setRate(self, rate):
        self.vlc_mediaPlayer.set_rate(rate)
        

    def setPosition(self, position):
        # setting the position to where the slider was dragged
        self.vlc_mediaPlayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)
        
        
    def event_handler(self, event):
        if event.type == VLC.EventType.MediaPlayerEndReached:
            self.mediaPlayerEndReached.emit(True)
            
            
    def spacebar_event(self):
        self.spacebarPressed.emit(self.media_filepath)
        

    def updateUI(self):
        # setting the slider to the desired position
        self.positionSlider.setValue(self.vlc_mediaPlayer.get_position() * 1000)
        self.updateTime()
        if self.durationLabel.text() in {'--:--', '00:00', '00:00:00'}:
            self.updateDuration()

        if not self.vlc_mediaPlayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                self.stop()


    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.vlc_mediaPlayer.errorString())
