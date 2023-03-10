import os
import sys
import sqlite3 as sql


if sys.platform == 'darwin':
    pass
if os.name == 'nt':
    SERVERSIDE_MUSIC_FOLER_PATH = r'C:\\Users\\malekith\\Desktop\\VoxCasterPublicae_Desktop\\Half Life - Black Mesa\\'
    DB_FILE_PATH = r'C:\\Users\\malekith\\Desktop\\VoxCasterPublicae_Desktop\\VoxCaster.db'
    
    

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
def read_db(db_file, table_name, column):
    try:
        connection = sql.connect(db_file)
        curser = connection.cursor()
        for row in curser.execute(f"SELECT {column} FROM {table_name}"):
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
            
            
def get_metadatas_from_filename(db_file, filename):
    try:
        connection = sql.connect(db_file)
        curser = connection.cursor()
        for row in curser.execute(f'SELECT metadatas FROM tracks WHERE filename = "{filename}"'):
            return row[0]
    except sql.Error as error_code:
        print(error_code)
    finally:
        if connection:
            curser.close()
            
            
def get_cover_art_from_filename(db_file, filename):
    try:
        connection = sql.connect(db_file)
        curser = connection.cursor()
        for row in curser.execute(f'SELECT cover_art FROM tracks WHERE filename = "{filename}"'):
            return row[0]
    except sql.Error as error_code:
        print(error_code)
    finally:
        if connection:
            curser.close()