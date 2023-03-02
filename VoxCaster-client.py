from Base64_Assets import *
from socket import socket
from QAudioPlayer import QAudioPlayer
import os
import sqlite3 as sql
from PyQt6.QtCore import Qt, QByteArray
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

SERVERSIDE_MUSIC_FOLER_PATH = r'C:\\Users\\malekith\\Desktop\\VoxCasterPublicae_Desktop\\Half Life - Black Mesa\\'
DB_FILE_PATH = r'C:\\Users\\malekith\\Desktop\\VoxCasterPublicae_Desktop\\VoxCaster.db'

# ADRESS = '82.64.66.109'
# PORT = 2270

# # Create a TCP/IP socket
# sock = socket()

# # Connect the socket to the port where the server is listening
# sock.connect((ADRESS, PORT))
# print(f'connected to {ADRESS} port {PORT}')

# try:
#     # Send data
#     message = b'This is the message.  It will be repeated.'
#     print(f'sending {message}')
#     sock.sendall(message)

#     # Look for the response
#     amount_received = 0
#     amount_expected = len(message)

#     while amount_received < amount_expected:
#         data = sock.recv(16)
#         amount_received += len(data)
#         print(f'received {data}')

# finally:
#     print('closing socket')
#     sock.close()


# Create a sqlite file from a path
def create_db_from_path(db_file, path):
    connection = None
    try:
        connection = sql.connect(db_file)
        curser = connection.cursor()
        curser.execute('DROP TABLE IF EXISTS tracks')
        curser.execute('CREATE TABLE tracks (filepath TEXT, filename TEXT)')
        for root, dirnames, filenames in os.walk(path):
            curser.executemany('INSERT INTO tracks (filepath, filename) VALUES (?, ?)', ([(os.path.join(root, filename), filename) for filename in filenames]))
            connection.commit()
    except sql.Error as error_code:
        print(error_code)
    finally:
        if connection:
            connection.close()

# Read an sqlite file' specific table row by row
def read_db(db_file, table_name):
    try:
        connection = sql.connect(db_file)
        curser = connection.cursor()
        for row in curser.execute(f"SELECT * FROM {table_name}"):
            yield row[0]
    except sql.Error as error_code:
        print(error_code)
    finally:
        if connection:
            curser.close()
               
def get_path_from_filename(db_file, filename):
    try:
        connection = sql.connect(db_file)
        curser = connection.cursor()
        for row in curser.execute(f'SELECT filepath FROM tracks WHERE filename = "{filename}"'):
            return row[0]
    except sql.Error as error_code:
        print(error_code)
    finally:
        if connection:
            curser.close()


def iconFromBase64(base64):
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray.fromBase64(base64))
    icon = QIcon(pixmap)
    return icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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
        self.audio_player_container.setLayout(self.audio_player_layout)
        # ---------------- #
        self.audio_player_layout.addWidget(self.audio_player)
        # ---------------- #
        self.left_pannel_layout.addWidget(self.audio_player_container)

        # Audio Controls #
        self.audio_controls = QWidget()
        self.audio_controls_layout = QHBoxLayout()
        self.audio_controls.setLayout(self.audio_controls_layout)
        # ---------------- #
        self.audio_controls_button_next = QPushButton('Next')
        self.audio_controls_button_add_time = QPushButton('+')
        self.audio_controls_button_subtract_time = QPushButton('-')
        self.audio_controls_speed = QDoubleSpinBox()
        self.audio_controls_autoplay = QCheckBox('Autoplay')
        self.audio_controls_loop = QCheckBox('Loop')
        self.audio_controls_random = QCheckBox('Random')
        # ---------------- #
        self.audio_controls_layout.addWidget(self.audio_controls_button_next)
        self.audio_controls_layout.addWidget(
            self.audio_controls_button_add_time)
        self.audio_controls_layout.addWidget(
            self.audio_controls_button_subtract_time)
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
        self.curently_playing_label = QLabel('')
        # ---------------- #
        self.curently_playing_layout.addWidget(self.curently_playing_label)
        # ---------------- #
        self.left_pannel_layout.addWidget(self.curently_playing)

        # File navigation pannel
        self.file_pannel = QScrollArea()
        self.file_pannel_layout = QVBoxLayout()
        self.file_pannel.setLayout(self.file_pannel_layout)
        # ---------------- #
        self.file_pannel_tree = QTreeWidget()
        # ---------------- #
        self.file_pannel.setWidget(self.file_pannel_tree)
        # ---------------- #
        self.file_pannel.setWidgetResizable(True)
        self.file_pannel.setSizeAdjustPolicy(self.file_pannel.SizeAdjustPolicy.AdjustToContents)
        self.populate_file_tree()
        self.file_pannel_tree.itemClicked.connect(self.on_Item_Clicked)
        # ---------------- #
        self.left_pannel_layout.addWidget(self.file_pannel)

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
        self.file_pannel_tree.setHeaderLabels(['Filepath'])
        # TODO
        root = QTreeWidgetItem(self.file_pannel_tree, ['/var/www/webapp_mal/vox_caster.fr/Music_folder/'])
        root.setExpanded(True)
        parents_dictionary = {root.text(0): root}
        # We use the dictionary to keep tracks of the folder nodes
        for filepath in read_db(DB_FILE_PATH, 'tracks'):
            # TODO not WIndows
            current_parrent = root.text(0)
            for directory in os.path.dirname(filepath).split('/'):
                if (directory not in parents_dictionary):
                    if (directory != ""):
                        widget = QTreeWidgetItem(
                            parents_dictionary[current_parrent], [directory])
                        widget.setExpanded(True)
                        parents_dictionary[directory] = widget
                        current_parrent = directory
                else:
                    current_parrent = directory
                    continue
            widget = QTreeWidgetItem(parents_dictionary[current_parrent], [os.path.basename(filepath)])
            widget.setIcon(0, iconFromBase64(BASE64_ICON))


    def on_Item_Clicked(self, item, column):
        # To be sure that the folder nodes are non-clickable
        if item.childCount() == 0:
            # get the real path from the db
            audio_path = get_path_from_filename(DB_FILE_PATH, item.text(column))
            self.Play(audio_path)
        

    def Play(self, audio_path):
        # TODO online
        path = audio_path
        self.audio_player.setSource(path)


if __name__ == '__main__':
    # TODO : online
    # create_db_from_path(DB_FILE_PATH, SERVERSIDE_MUSIC_FOLER_PATH)

    app = QApplication([])
    app.setStyle('Windows')
    window = MainWindow()
    window.showMaximized()
    app.exec()
