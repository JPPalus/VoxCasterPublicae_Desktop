import sqlite3 as sql
import os

SERVERSIDE_MUSIC_FOLER_PATH = r'/var/www/webapp_mal/vox_caster.fr_/Music_folder'
DB_FILE_PATH = r'/var/www/webapp_mal/vox_caster.fr_/VoxCaster.db'

ALLOWED_PATTERNS = ['mp3','MP3', 'wav', 'flac', 'ogg', 'mid', 'm3u', 'wma', 'tta']

# Create a sqlite file from a path
def create_db_from_path(db_file, path):
    connection = None
    try:
        connection = sql.connect(db_file)
        curser = connection.cursor()
        curser.execute('DROP TABLE IF EXISTS tracks')
        curser.execute('CREATE TABLE tracks (filepath TEXT, filename TEXT)')
        filecount = 0
        data = []
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if os.path.basename(filename).split('.')[-1] in ALLOWED_PATTERNS:
                    filecount += 1    
                    data.append((os.path.join(url_from_path(root), filename), filename))
                    # print(os.path.join(url_from_path(root), filename), filename)
                    ###----------------###
                    print(f'file n°{filecount} : {filename}')
                    ###----------------###
        curser.executemany('INSERT INTO tracks (filepath, filename) VALUES (?, ?)', (data))
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