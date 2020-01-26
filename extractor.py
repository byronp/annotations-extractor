import os
import shutil
import tempfile
import sqlite3
from datetime import datetime


HOME = os.getenv('HOME', '')
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def connect(db):
    # Connects to a SQLite database.
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    return con, cur


def get_highlights(cur):
    query = ('SELECT Z_PK as id, ZANNOTATIONSELECTEDTEXT as text, '
             'ZANNOTATIONASSETID as book_id, ZANNOTATIONSTYLE as style, '
             'ZANNOTATIONCREATIONDATE as created, '
             'ZANNOTATIONMODIFICATIONDATE as last_modified '
             'FROM ZAEANNOTATION '
             'WHERE ZANNOTATIONSELECTEDTEXT IS NOT NULL '
             'ORDER BY last_modified ASC')
    cur.execute(query)
    highlights = cur.fetchall()
    return highlights


def get_notes(cur_annotations):
    pass


def get_book(cur, id):
    query = ('SELECT ZTITLE as title, ZAUTHOR as author '
             'FROM ZBKLIBRARYASSET '
             'WHERE ZASSETID={}').format(id)
    cur.execute(query)
    return cur.fetchone()


def initialize():
    temp_dir = tempfile.gettempdir()
    path = 'Library/Containers/com.apple.iBooksX/Data/Documents'

    # Connect to the annotations database
    a_db_name = 'AEAnnotation_v10312011_1727_local.sqlite'
    a_db = os.path.join(HOME, path, 'AEAnnotation', a_db_name)
    a_db_temp = os.path.join(temp_dir, 'a_db_temp.sqlite')
    shutil.copyfile(a_db, a_db_temp) # Achtung!
    con_a, cur_a = connect(a_db_temp)

    # Connect to the library database
    b_db_name = 'BKLibrary-1-091020131601.sqlite'
    b_db = os.path.join(HOME, path, 'BKLibrary', b_db_name)
    b_db_temp= os.path.join(temp_dir, 'b_db_temp.sqlite')
    shutil.copyfile(b_db, b_db_temp) # Achtung!
    con_b, cur_b = connect(b_db_temp)

    # Create an output database (delete existing one)
    output_db_name = 'annotations.sqlite'
    output_db = os.path.join(PROJECT_ROOT, 'data', output_db_name)
    print(output_db)
    if os.path.isfile(output_db):
        os.remove(output_db)
    con_o = sqlite3.connect(output_db)
    cur_o = con_o.cursor()
    query = ('CREATE TABLE IF NOT EXISTS highlights ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'book_id VARCHAR, '
            'title VARCHAR, '
            'author VARCHAR, '
            'text VARCHAR, '
            'created TIMESTAMP, '
            'last_modified TIMESTAMP, '
            'style INTEGER)')
    cur_o.execute(query)

    # Insert data into the output database
    highlights = get_highlights(cur_a)
    for highlight in highlights:
        book = get_book(cur_b, highlight['book_id'])
        query = ('INSERT INTO highlights '
                 '(book_id, title, author, text, created, last_modified, style) '
                 'VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
                    highlight['book_id'],
                    book['title'],
                    book['author'],
                    highlight['text'],
                    highlight['created'],
                    highlight['last_modified'],
                    highlight['style']))
        cur_o.execute(query)
    con_o.commit()
    con_o.close()
    

def main():
    initialize()
    annotations_db_name = 'annotations.sqlite'
    annotations_db = os.path.join(PROJECT_ROOT, 'data', annotations_db_name)
    con, cur = connect(annotations_db)
    # Print all highlights with metadata
    query = ('SELECT title, author, text, style, '
             'datetime(created + 978307200, "unixepoch", "localtime") as created, '
             'datetime(last_modified + 978307200, "unixepoch", "localtime") as last_modified '
             'FROM highlights '
             'ORDER BY created')
    cur.execute(query)
    highlights = cur.fetchall()
    style = {0:'Underline', 1:'Green', 2:'Blue', 3:'Yellow', 4:'Pink', 5:'Purple'}
    for highlight in highlights: 
        print('> {}\n'.format(highlight['text'])) 
        print('{}, _{}_.'.format(highlight['author'], highlight['title']))
        print('\nMetadata:')
        print('* Created: {}'.format(highlight['created'])) 
        print('* Last modified: {}'.format(highlight['last_modified'])) 
        if highlight['style'] == 0: 
            print('* Style: Underlined')  
        else: 
            print('* Style: {} highlight'.format(style[highlight['style']]))
        print('\n---\n')
    con.close()


if __name__ == '__main__':
    main()