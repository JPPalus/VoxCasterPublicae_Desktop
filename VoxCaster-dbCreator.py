import sqlite3 as sql
import os

SERVERSIDE_MUSIC_FOLER_PATH = r'/var/www/webapp_mal/vox_caster.fr_/Music_folder'
DB_FILE_PATH = r'/var/www/webapp_mal/vox_caster.fr_/VoxCaster.db'

# Create a sqlite file from a path
def create_db_from_path(db_file, path):
    connection = None
    try:
        connection = sql.connect(db_file)
        curser = connection.cursor()
        curser.execute('DROP TABLE IF EXISTS tracks')
        curser.execute('CREATE TABLE tracks (filepath TEXT, filename TEXT)')
        for root, dirnames, filenames in os.walk(path):
            curser.executemany('INSERT INTO tracks (filepath, filename) VALUES (?, ?)', ([(os.path.join('/var/www/webapp_mal/vox_caster.fr_/', filename), filename) for filename in filenames]))
            connection.commit()
    except sql.Error as error_code:
        print(error_code)
    finally:
        if connection:
            connection.close()
            
            
def url_from_path(path):
    return path.replace('/var/www/webapp_mal/vox_caster.fr_/', 'https://vox-caster.fr/')
            
if __name__ == '__main__':
    create_db_from_path(DB_FILE_PATH, SERVERSIDE_MUSIC_FOLER_PATH)