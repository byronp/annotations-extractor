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
    query = 'SELECT\
        Z_PK as id,\
        ZANNOTATIONSELECTEDTEXT as text,\
        ZANNOTATIONASSETID as book_id,\
        ZANNOTATIONSTYLE as style,\
        datetime(ZANNOTATIONMODIFICATIONDATE+978307200, "unixepoch") as last_modified\
        FROM\
        ZAEANNOTATION\
        WHERE\
        ZANNOTATIONSELECTEDTEXT IS NOT NULL'
    cur_annotations.execute(query)
    annotations = cur_annotations.fetchall()
    highlights = {}
    for annotation in annotations:
        query = 'SELECT * FROM ZBKLIBRARYASSET WHERE ZASSETID={}'.format(
            annotation['book_id']
        )
        cur_books.execute(query)
        book = cur_books.fetchone()
        highlights[annotation['id']] = {
            'book_id': annotation['book_id'],
            'title': book['ZTITLE'],
            'author': book['ZAUTHOR'],
            'text': annotation['text'],
            'last_modified': annotation['last_modified'],
            'style': annotation['style']
        }
    return highlights


def get_highlights(cur_annotations, cur_books, book_id):
    query = 'SELECT\
        Z_PK as id,\
        ZANNOTATIONSELECTEDTEXT as text,\
        ZANNOTATIONASSETID as book_id,\
        ZANNOTATIONSTYLE as style,\
        datetime(ZANNOTATIONMODIFICATIONDATE+978307200, "unixepoch") as last_modified\
        FROM\
        ZAEANNOTATION\
        WHERE\
        ZANNOTATIONSELECTEDTEXT IS NOT NULL\
        AND\
        ZANNOTATIONASSETID={}'.format(book_id)
    cur_annotations.execute(query)
    annotations = cur_annotations.fetchall()
    highlights = {}
    for annotation in annotations:
        highlights[annotation['id']] = {
            'book_id': annotation['book_id'],
            'text': annotation['text'],
            'last_modified': annotation['last_modified'],
            'style': annotation['style']
        }
    return highlights


def get_book(cur, id):
    query = 'SELECT * FROM ZBKLIBRARYASSET WHERE ZASSETID={}'.format(id)
    cur.execute(query)
    row = cur.fetchone()
    return {
        'title': row['ZTITLE'],
        'author': row['ZAUTHOR'],
    }


def get_books(cur):
    query = 'SELECT * FROM ZBKLIBRARYASSET'
    cur.execute(query)
    rows = cur.fetchall()
    books = {}
    for row in rows:
        books[row['ZASSETID']] = {
            'title': row['ZTITLE'],
            'author': row['ZAUTHOR'],
        }
    return books


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
    books = get_books(cur_books)
    book_ids = [k for k, v in books.items()]
    for book_id in book_ids:
        highlights = get_highlights(cur_annotations, cur_books, book_id)
        if highlights != {}:
            for k in highlights.keys():
                print('> {}\
                \n\n{}, _{}_\
                \n\nLast modified: {}\
                \n\nHighlight color: {}\
                \n\n---\n'.format(
                    highlights[k]['text'],
                    books[book_id]['author'],
                    books[book_id]['title'],
                    highlights[k]['last_modified'],
                    style[highlights[k]['style']]
                ))
    close(con_annotations)
    close(con_books)


if __name__ == '__main__':
    main()