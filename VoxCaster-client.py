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
    QWidget
)

SPECIFIC_ROOT = 'https://vox-caster.fr/Music_folder/'

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
            return False
        elif not other_is_folder and is_folder:
            return True
        else:
            return data < other_data


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.playing_item = None
        self.playing_playlist = []
        self.playlist_order_changed = False
        self.breadcrumb_nodes = []
        self.curently_selected_node = None

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
        self.audio_player.spacebarPressed.connect(self.spacebar_event)
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
        self.currently_playing_scrollArea = QScrollArea()
        self.currently_playing_scrollArea_widget = QWidget()
        self.curently_playing_layout = QHBoxLayout()
        self.currently_playing_GoupBox_layout = QHBoxLayout()
        # ---------------- #
        self.curently_playing.setLayout(self.currently_playing_GoupBox_layout)
        self.currently_playing_GoupBox_layout.addWidget(self.currently_playing_scrollArea)
        self.currently_playing_scrollArea.setWidget(self.currently_playing_scrollArea_widget)
        self.currently_playing_scrollArea_widget.setLayout(self.curently_playing_layout)
        # ---------------- #
        self.curently_playing_label_root = QPushButton()
        self.curently_playing_label_root.setIcon(iconFromBase64(BASE64_ICON_AQUILA))
        self.curently_playing_label_root.setIconSize(QSize(32,32))
        self.curently_playing_label_root.clicked.connect(self.collapse_all_nodes)
        # ---------------- #
        self.curently_playing.setFixedHeight(70)
        self.curently_playing.setContentsMargins(0, 10, 0, 0)
        self.currently_playing_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.currently_playing_scrollArea.setWidgetResizable(True)
        self.currently_playing_scrollArea.verticalScrollBar().setDisabled(True)
        self.currently_playing_scrollArea.setStyleSheet("border: 0;"
                                                        "QScrollBar::horizontal {height: 3px;}")
        self.curently_playing_layout.setContentsMargins(0, 0, 0, 0)
        self.curently_playing_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.curently_playing_layout.addWidget(self.curently_playing_label_root)
        # ---------------- #
        self.left_pannel_layout.addWidget(self.curently_playing)

        # File navigation pannel
        self.file_pannel_tree = QTreeWidget()
        # ---------------- #
        self.populate_file_tree()
        self.file_pannel_tree.setSortingEnabled(True)
        self.file_pannel_tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.file_pannel_tree.header().setSortIndicatorShown(False)
        self.file_pannel_tree.header().setSectionsClickable(False)
        #TODO
        self.file_pannel_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.file_pannel_tree.itemClicked.connect(self.on_Item_Clicked)
        # ---------------- #
        self.left_pannel_layout.addWidget(self.file_pannel_tree)
    
        # File infos pannel
        self.file_infos_tabs = QTabWidget()
        self.file_info_tab = QScrollArea()
        self.file_art_tab = QWidget()
        self.file_infos_layout = QVBoxLayout()
        self.file_art_layout = QVBoxLayout()
        self.file_info_tab.setLayout(self.file_infos_layout)
        self.file_art_tab.setLayout(self.file_art_layout)
        # ---------------- #
        self.file_infos_label = QLabel('')
        self.file_info_tab.setWidget(self.file_infos_label)
        # ---------------- #
        self.file_infos_tabs.addTab(self.file_art_tab, 'Art')
        self.file_infos_tabs.addTab(self.file_info_tab, 'File infos')
        # ---------------- #
        self.right_pannel_layout.addWidget(self.file_infos_tabs)

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
            if len(directories := os.path.dirname(filepath.replace(SPECIFIC_ROOT, '')).split('/')):
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


    def on_Item_Clicked(self, item, column):
        # if file: play
        self.curently_selected_node = item
        if item.childCount() == 0:
            if self.playing_item is not None:
                self.playing_item.setIcon(0, iconFromBase64(BASE64_ICON_FILE))
            item.setIcon(0, iconFromBase64(BASE64_ICON_FILE_PLAYING)) 
            self.playing_item = item
            audio_path = get_path_from_filename(DB_FILE_PATH, item.text(column))
            self.Play(audio_path)
            self.set_playing_playlist(item)
            self.depopulate_layout(self.curently_playing_layout)
            self.populate_breadcrumbs(item)
        # if folder expand / collapse
        if item.childCount() > 0:
            if item.isExpanded():
                item.setExpanded(False)
                for child_index in range(item.childCount()):
                    item.child(child_index).setExpanded(False)
            else:
                item.setExpanded(True)
            # to keep the breadcrumbs pointing on the currently playing item
            if not self.audio_player.isPlaying():
                self.depopulate_layout(self.curently_playing_layout)
                self.populate_breadcrumbs(item)
        
    
    def depopulate_layout(self, layout):
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)
    
    
    def populate_breadcrumbs(self, node):
        self.curently_playing_layout.addWidget(self.curently_playing_label_root)
        current_node = node
        self.breadcrumb_nodes = [current_node]
        reverse_breadcrumbs = [current_node.text(0)]
        while current_node.parent():
            current_node = current_node.parent()
            if current_node.text(0) not in reverse_breadcrumbs:
                reverse_breadcrumbs.append(current_node.text(0))
                self.breadcrumb_nodes.append(current_node)
        reverse_breadcrumbs.reverse()
        for element in reverse_breadcrumbs:
            if element:
                element_label = QPushButton()
                element_label.setText(element)
                element_label.clicked.connect(self.breadcrumbs_clicked)
                element_label.setStyleSheet("border:0;")
                arrow_label = QLabel()
                arrow_label.setPixmap(iconFromBase64(BASE64_ICON_TRIANGLE).pixmap(QSize(7, 7)))
                self.curently_playing_layout.addWidget(arrow_label)
                self.curently_playing_layout.addWidget(element_label)
        self.currently_playing_scrollArea.verticalScrollBar().setEnabled(False)
        
    
    def collapse_all_nodes(self):
        self.file_pannel_tree.collapseAll()
    

    def Play(self, audio_path):
        self.audio_player.setSource(audio_path)
        
    
    def Play_next(self):
        # check if the options have changed 
        if self.playlist_order_changed:
            self.playlist_order_changed = False
            self.set_playing_playlist(self.playing_item)
        # if playlist exists
        if playlist_lenght := len(self.playing_playlist):
            current_node_index = self.playing_playlist.index(self.playing_item)
            if self.playing_item is not None:
                self.playing_item.setIcon(0, iconFromBase64(BASE64_ICON_FILE))
            # if the playing item is the penultimate
            if current_node_index < (playlist_lenght - 1):
                self.playing_item = self.playing_playlist[current_node_index + 1]
            # if the playing item is the last
            if current_node_index == (playlist_lenght - 1):
                # if we loop
                if self.audio_controls_loop.isChecked():
                    self.playing_item = self.playing_playlist[0]
                # if we don't loop, do nothing
                else : 
                    return
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
            
            
    def spacebar_event(self, curently_playing_filepath):
        items_selected = self.file_pannel_tree.selectedItems()
        for item in items_selected:
            audio_path = get_path_from_filename(DB_FILE_PATH, item.text(0))
            if curently_playing_filepath == audio_path:
                self.audio_player.play()
            else:
                self.on_Item_Clicked(item, 0)
                
                
    def breadcrumbs_clicked(self):
        for node in self.breadcrumb_nodes:
            if node.text(0) == self.sender().text():
                node.setExpanded(True)
                parent = node.parent()
                while parent:
                    parent.setExpanded(True)
                    parent = parent.parent()
                for child_index in range(node.childCount()):
                    node.child(child_index).setExpanded(False)
                self.curently_selected_node.setSelected(False)
                self.curently_selected_node = node
                node.setSelected(True)
                self.file_pannel_tree.scrollToItem(node)
                
    

if __name__ == '__main__':
    # TODO : online
    # create_db_from_path(DB_FILE_PATH, SERVERSIDE_MUSIC_FOLER_PATH)
    app = QApplication([])
    # app.setStyle('Windows')
    window = MainWindow()
    # window.showMaximized()
    window.show()
    app.exec()
    
