from Base64_Assets import *
from VoxCaster_db import *
from QAudioPlayer import QAudioPlayer
import random
import os
from PyQt6.QtCore import (
    Qt, 
    QByteArray,
    QSize)
from PyQt6.QtGui import (
    QMovie,
    QIcon,
    QPixmap)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QCheckBox,
    QDoubleSpinBox,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QLabel,
    QGroupBox,
    QScrollArea,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

def iconFromBase64(base64):
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray.fromBase64(base64))
    icon = QIcon(pixmap)
    return icon


class QFileSystemTreeWidgetItem(QTreeWidgetItem):
      
    def __lt__(self, other):
        other_is_folder = True if other.childCount() else False
        other_data = other.text(0)
        is_folder = True if self.childCount() else False
        data = self.text(0)
        
        if other_is_folder and not is_folder:
            return True
        elif not other_is_folder and is_folder:
            return False
        else:
            # yes that's done on purpose !
            return data > other_data


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.playing_item = None
        self.playing_playlist = []
        self.playlist_order_changed = False

        # Main window #
        self.window_layout = QHBoxLayout()
        self.container = QWidget()
        self.container.setLayout(self.window_layout)
        # ---------------- #
        self.setWindowTitle("Vox Xaster Publicae")
        # ---------------- #
        self.setCentralWidget(self.container)

        # Right & left pannel #
        self.left_pannel = QWidget()
        self.right_pannel = QWidget()
        self.left_pannel_layout = QVBoxLayout()
        self.right_pannel_layout = QVBoxLayout()
        # ---------------- #
        self.left_pannel.setLayout(self.left_pannel_layout)
        self.right_pannel.setLayout(self.right_pannel_layout)
        # ---------------- #
        self.window_layout.addWidget(self.left_pannel, 50)
        self.window_layout.addWidget(self.right_pannel, 50)

        # Audio player #
        self.audio_player_container = QGroupBox()
        self.audio_player = QAudioPlayer()
        self.audio_player_layout = QHBoxLayout()
        # ---------------- #
        self.audio_player.mediaPlayerEndReached.connect(self.Play_next_auto)
        # ---------------- #
        self.audio_player_container.setLayout(self.audio_player_layout)
        self.audio_player_layout.addWidget(self.audio_player)
        # ---------------- #
        self.left_pannel_layout.addWidget(self.audio_player_container)

        # Audio Controls #
        self.audio_controls = QWidget()
        self.audio_controls_layout = QHBoxLayout()
        self.audio_controls.setLayout(self.audio_controls_layout)
        # ---------------- #
        self.audio_controls_button_next = QPushButton('Next')
        self.audio_controls_button_subtract_time = QPushButton('<<')
        self.audio_controls_button_add_time = QPushButton('>>')
        self.audio_controls_speed = QDoubleSpinBox()
        self.audio_controls_autoplay = QCheckBox('Autoplay')
        self.audio_controls_singleloop = QCheckBox('Single loop')
        self.audio_controls_loop = QCheckBox('Loop')
        self.audio_controls_random = QCheckBox('Random')
        # ---------------- #
        self.audio_controls_speed.setRange(0.3, 4.0)
        self.audio_controls_speed.setSingleStep(0.1)
        self.audio_controls_speed.setValue(1.0)
        # ---------------- #
        self.audio_controls_button_next.clicked.connect(self.Play_next)
        self.audio_controls_speed.valueChanged.connect(self.set_rate)
        self.audio_controls_button_subtract_time.clicked.connect(self.subtract_time)
        self.audio_controls_button_add_time.clicked.connect(self.add_time)
        self.audio_controls_singleloop.clicked.connect(self.playlist_order_has_changed)
        self.audio_controls_loop.clicked.connect(self.playlist_order_has_changed)
        self.audio_controls_autoplay.clicked.connect(self.playlist_order_has_changed)
        self.audio_controls_random.clicked.connect(self.playlist_order_has_changed)
        # ---------------- #
        self.audio_controls_layout.addWidget(self.audio_controls_button_next)
        self.audio_controls_layout.addWidget(self.audio_controls_button_subtract_time)
        self.audio_controls_layout.addWidget(self.audio_controls_button_add_time)
        self.audio_controls_layout.addWidget(self.audio_controls_speed)
        self.audio_controls_layout.addWidget(self.audio_controls_loop)
        self.audio_controls_layout.addWidget(self.audio_controls_autoplay)
        self.audio_controls_layout.addWidget(self.audio_controls_random)
        # ---------------- #
        self.left_pannel_layout.addWidget(self.audio_controls)

        # Curently playing breadcrumbs
        self.curently_playing = QGroupBox('Curently playing')
        self.curently_playing_layout = QHBoxLayout()
        self.curently_playing.setLayout(self.curently_playing_layout)
        # ---------------- #
        self.curently_playing_label_root = QLabel()
        # ---------------- #
        self.curently_playing_label_root.setPixmap(iconFromBase64(BASE64_ICON_AQUILA).pixmap(QSize(32, 32)))
        # ---------------- #
        self.curently_playing_layout.addWidget(self.curently_playing_label_root)
        # ---------------- #
        self.left_pannel_layout.addWidget(self.curently_playing)

        # File navigation pannel
        self.file_pannel_tree = QTreeWidget()
        # ---------------- #
        self.populate_file_tree()
        self.file_pannel_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.file_pannel_tree.setSortingEnabled(False)
        self.file_pannel_tree.itemClicked.connect(self.on_Item_Clicked)
        # ---------------- #
        self.left_pannel_layout.addWidget(self.file_pannel_tree)
    
        # File infos pannel
        self.file_infos = QGroupBox('File infos')
        self.file_infos_layout = QVBoxLayout()
        self.file_infos.setLayout(self.file_infos_layout)
        # ---------------- #
        self.file_info_scrollarea = QScrollArea()
        self.file_infos_label = QLabel('')
        # ---------------- #
        self.file_info_scrollarea.setWidget(self.file_infos_label)
        self.file_infos_layout.addWidget(self.file_info_scrollarea)
        # ---------------- #
        self.right_pannel_layout.addWidget(self.file_infos)

        # Art
        self.art = QGroupBox('Art')
        self.art_layout = QVBoxLayout()
        self.art.setLayout(self.art_layout)
        # ---------------- #
        self.art_label = QLabel('')
        self.art_movie = QMovie()
        # ---------------- #
        self.art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # ---------------- #
        self.art_label.setMovie(self.art_movie)
        self.art_layout.addWidget(self.art_label)
        self.art_label.setMovie(self.art_movie)
        # ---------------- #
        self.right_pannel_layout.addWidget(self.art)

        # DSP tab
        self.dsp_tabs = QTabWidget()
        self.dsp_tab_1 = QWidget()
        self.dsp_tab_2 = QWidget()
        self.dsp_tab_3 = QWidget()
        self.dsp_layout_1 = QVBoxLayout()
        self.dsp_layout_2 = QVBoxLayout()
        self.dsp_layout_3 = QVBoxLayout()
        self.dsp_tab_1.setLayout(self.dsp_layout_1)
        self.dsp_tab_2.setLayout(self.dsp_layout_2)
        self.dsp_tab_3.setLayout(self.dsp_layout_3)
        # ---------------- #
        self.dsp_tabs.addTab(self.dsp_tab_1, 'DSP 1')
        self.dsp_tabs.addTab(self.dsp_tab_2, 'DSP 2')
        self.dsp_tabs.addTab(self.dsp_tab_3, 'DSP 3')
        # ---------------- #
        self.right_pannel_layout.addWidget(self.dsp_tabs)


    def populate_file_tree(self):
        self.file_pannel_tree.setHeaderLabels(['Files'])
        # For each file in the database
        for filepath in read_db(DB_FILE_PATH, 'tracks'):
            # if node is a folder
            parent = None
            if len(directories := os.path.dirname(filepath.replace('https://vox-caster.fr/Music_folder/', '')).split('/')):
                # for each element of the path that is a directory
                for directory in directories:
                    # If we are at the root of the tree
                    if parent is None:
                        # if a node with that name already exists continue
                        if len(items := self.file_pannel_tree.findItems(directory, Qt.MatchFlag.MatchExactly, 0)):
                            parent = items[0]
                            continue
                        # If not create a new node that the root of the tree
                        else:
                            widget = QFileSystemTreeWidgetItem()
                            widget.setText(0, directory)
                            widget.setIcon(0, iconFromBase64(BASE64_ICON_FOLDER))
                            self.file_pannel_tree.addTopLevelItem(widget)
                            parent = widget
                    # if node is not a root but still a directory
                    if parent is not None:
                        # if the current parent has children 
                        if child_count := parent.childCount():
                            children = [parent.child(child_index) for child_index in range(child_count)]
                            children_labels = [child.text(0) for child in children]
                            # if directory is one of them he becomes the new parent
                            if directory in children_labels:
                                parent = children[children_labels.index(directory)]
                            # if directory is not one of them, create a new node and it becomes the parent
                            else:
                                widget = QFileSystemTreeWidgetItem(parent, [directory])
                                widget.setIcon(0, iconFromBase64(BASE64_ICON_FOLDER))
                                parent = widget
                        # if the current parent is not in the root nor have children :
                        if parent.text(0) != directory:
                            widget = QFileSystemTreeWidgetItem(parent, [directory])
                            widget.setIcon(0, iconFromBase64(BASE64_ICON_FOLDER))
                            parent = widget   
            # if node is a file
            widget = QFileSystemTreeWidgetItem(parent, [os.path.basename(filepath)])
            widget.setIcon(0, iconFromBase64(BASE64_ICON_FILE))
        # self.file_pannel_tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)


    def on_Item_Clicked(self, item, column):
        # if file: play
        if item.childCount() == 0:
            if self.playing_item is not None:
                self.playing_item.setIcon(0, iconFromBase64(BASE64_ICON_FILE))
            item.setIcon(0, iconFromBase64(BASE64_ICON_FILE_PLAYING)) 
            self.playing_item = item
            audio_path = get_path_from_filename(DB_FILE_PATH, item.text(column))
            self.Play(audio_path)
            self.set_playing_playlist(item)
        # if folder expand / colapse
        if item.childCount() > 0:
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        

    def Play(self, audio_path):
        self.audio_player.setSource(audio_path)
        
    
    def Play_next(self):
        # check if the options have changed 
        if self.playlist_order_changed:
            self.playlist_order_changed = False
            self.set_playing_playlist(self.playing_item)
        if playlist_lenght := len(self.playing_playlist):
            current_node_index = self.playing_playlist.index(self.playing_item)
            if self.playing_item is not None:
                self.playing_item.setIcon(0, iconFromBase64(BASE64_ICON_FILE))
            # if the playing item is the penultimate
            if current_node_index < (playlist_lenght - 1):
                self.playing_item = self.playing_playlist[current_node_index + 1]
            # if the playing item is the last
            if self.audio_controls_loop.isChecked():
                if current_node_index == (playlist_lenght - 1):
                    if self.audio_controls_loop.isChecked():
                        self.playing_item = self.playing_playlist[0]
            self.playing_item.setIcon(0, iconFromBase64(BASE64_ICON_FILE_PLAYING))
            audio_path = get_path_from_filename(DB_FILE_PATH, self.playing_item.text(0))
            self.audio_player.setSource(audio_path)
            
            
    # connected to the event "mediaPlayerEndReached"
    def Play_next_auto(self):
        if self.audio_controls_autoplay.isChecked():
            self.Play_next()
           
            
    def set_rate(self):
        rate = self.audio_controls_speed.value()
        self.audio_player.setRate(rate)
           
           
    def add_time(self):
        self.audio_player.jump_forward()
           
            
    def subtract_time(self):
        self.audio_player.jump_backward()
        
    
    def playlist_order_has_changed(self):
        self.playlist_order_changed = True
        
        
    def set_playing_playlist(self, node):
        parent = node.parent()
        self.playing_playlist = []
        if child_count := parent.childCount():
            for child_index in range(child_count):
                if not parent.child(child_index).childCount():
                    self.playing_playlist.append(parent.child(child_index))
        if self.audio_controls_random.isChecked():
            print("random")
            print(self.playing_playlist)
            random.shuffle(self.playing_playlist)
            print(self.playing_playlist)
    

if __name__ == '__main__':
    # TODO : online
    # create_db_from_path(DB_FILE_PATH, SERVERSIDE_MUSIC_FOLER_PATH)
    app = QApplication([])
    app.setStyle('Windows')
    window = MainWindow()
    # window.showMaximized()
    window.show()
    app.exec()
    
