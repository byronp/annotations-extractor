import os
import shutil
import tempfile
import sqlite3
from datetime import datetime


HOME = os.getenv('HOME', '')


def connect(db):
    # Connects to a SQLite database.
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    return con, cur


def close(con):
    # Closes a database connection.
    con.close()


def get_highlights(cur_annotations, cur_books):
    query = ('SELECT Z_PK as id, ZANNOTATIONSELECTEDTEXT as text, '
             'ZANNOTATIONASSETID as book_id, ZANNOTATIONSTYLE as style, '
             'datetime(ZANNOTATIONMODIFICATIONDATE + 978307200, "unixepoch", "localtime") as last_modified '
             'FROM ZAEANNOTATION '
             'WHERE ZANNOTATIONSELECTEDTEXT IS NOT NULL '
             'ORDER BY last_modified ASC')
    cur_annotations.execute(query)
    annotations = cur_annotations.fetchall()
    highlights = {}
    for annotation in annotations:
        book = get_book(cur_books, annotation['book_id'])
        highlights[annotation['id']] = {
            'book_id': annotation['book_id'],
            'title': book['title'],
            'author': book['author'],
            'text': annotation['text'],
            'last_modified': annotation['last_modified'],
            'style': annotation['style']
        }
    return highlights


def get_highlights_2(cur):
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


def dump_db():
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

    # Create an output database
    output_db_name = 'annotations.sqlite'
    output_db = os.path.join(HOME, 'Desktop', output_db_name)
    con_o = sqlite3.connect(output_db)
    cur_o = con_o.cursor()
    query = ('CREATE TABLE highlights ('
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
    highlights = get_highlights_2(cur_a)
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
    path = 'Library/Containers/com.apple.iBooksX/Data/Documents'
    annotations_db_name = 'AEAnnotation_v10312011_1727_local.sqlite'
    books_db_name = 'BKLibrary-1-091020131601.sqlite'
    annotations_db = os.path.join(HOME, path, 'AEAnnotation', annotations_db_name)
    books_db = os.path.join(HOME, path, 'BKLibrary', books_db_name)
    temp_dir = tempfile.gettempdir()
    temp_annotations_db = os.path.join(temp_dir, 'temp_annotations_database.sqlite')
    temp_books_db = os.path.join(temp_dir, 'temp_books_database.sqlite')
    shutil.copyfile(annotations_db, temp_annotations_db) # Achtung!
    shutil.copyfile(books_db, temp_books_db) # Achtung!
    con_annotations, cur_annotations = connect(temp_annotations_db)
    con_books, cur_books = connect(temp_books_db)
    # Print highlights with metadata
    style = {0:'Underline', 1:'Green', 2:'Blue', 3:'Yellow', 4:'Pink', 5:'Purple'}
    highlights = get_highlights(cur_annotations, cur_books)
    for id in highlights: 
        highlight = highlights[id] 
        print('> {}\n'.format(highlight['text'])) 
        print('{}, _{}_'.format(highlight['author'], highlight['title'])) 
        print('Highlight last modified on {}'.format(highlight['last_modified'])) 
        if highlight['style'] == 0: 
            print('Underlined')  
        else: 
            print('Highlighted in {}'.format(style[highlight['style']].lower())) 
        print('\n---\n')
    close(con_annotations)
    close(con_books)


if __name__ == '__main__':
    main()