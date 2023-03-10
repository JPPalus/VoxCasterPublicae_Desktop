import sqlite3 as sql
import os
import subprocess

SERVERSIDE_MUSIC_FOLER_PATH = r'/var/www/webapp_mal/vox_caster.fr_/Music_folder'
DB_FILE_PATH = r'/var/www/webapp_mal/vox_caster.fr_/VoxCaster.db'

ALLOWED_PATTERNS = ['mp3','MP3', 'wav', 'flac', 'ogg', 'mid', 'm3u', 'wma', 'tta']
AUDIOFILES_PATTERNS = ['mp3','MP3', 'wav', 'flac', 'ogg', 'm3u', 'wma', 'tta']

# Create a sqlite file from a path
def create_db_from_path(db_file, path):
    connection = None
    try:
        connection = sql.connect(db_file)
        curser = connection.cursor()
        curser.execute('DROP TABLE IF EXISTS tracks')
        curser.execute('CREATE TABLE tracks (filepath TEXT, filename TEXT, metadatas BLOB, cover_art BLOB)')
        filecount = 0
        data = []
        cover_art = ''
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if os.path.basename(filename).split('.')[-1] in ALLOWED_PATTERNS:
                    filecount += 1
                    metadatas = ''
                    if os.path.basename(filename).split('.')[-1] in AUDIOFILES_PATTERNS:
                        filepath = root + '/' + filename
                        try:
                            metadatas = subprocess.check_output(['ffprobe', '-hide_banner', filepath], text = True, stderr=subprocess.STDOUT)
                        except:
                            metadatas = ''
                        try:
                            cover_art_process = subprocess.run(['ffmpeg', '-hide_banner', '-i', filepath, '-an', '-c:v', 'copy', '-f', 'image2pipe', 'pipe:1'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                            cover_art = cover_art_process.stdout
                        except:
                            cover_art = b''
                    data.append((os.path.join(url_from_path(root), filename), filename, metadatas, cover_art))
                    ###----------------
                    print(f'file n°{filecount} : {filename}')
                    ###----------------###
        curser.executemany('INSERT INTO tracks (filepath, filename, metadatas, cover_art) VALUES (?, ?, ?, ?)', (data))
        connection.commit()
        
    except sql.Error as error_code:
        print(error_code)
    finally:
        if connection:
            print('Database created... Closing connection...')
            connection.close()
           
            
            
def url_from_path(path):
    return path.replace('/var/www/webapp_mal/vox_caster.fr_/', 'https://vox-caster.fr/')
            
            
if __name__ == '__main__':
    create_db_from_path(DB_FILE_PATH, SERVERSIDE_MUSIC_FOLER_PATH)