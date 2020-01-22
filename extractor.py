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


def get_highlights(cur_notes, cur_books):
    query = 'SELECT * FROM ZAEANNOTATION WHERE ZANNOTATIONSELECTEDTEXT IS NOT NULL'
    cur_notes.execute(query)
    notes = cur_notes.fetchall()
    highlights = {}
    for note in notes:
        query = 'SELECT * FROM ZBKLIBRARYASSET WHERE ZASSETID={}'.format(
            note['ZANNOTATIONASSETID']
        )
        cur_books.execute(query)
        book = cur_books.fetchone()
        highlights[note['Z_PK']] = {
            'book_id': note['ZANNOTATIONASSETID'],
            'title': book['ZTITLE'],
            'author': book['ZAUTHOR'],
            'text': note['ZANNOTATIONSELECTEDTEXT']
        }
    return highlights


def get_highlights(cur_notes, cur_books, book_id):
    query = 'SELECT * FROM ZAEANNOTATION WHERE \
        ZANNOTATIONSELECTEDTEXT IS NOT NULL AND \
        ZANNOTATIONASSETID={}'.format(book_id)
    cur_notes.execute(query)
    notes = cur_notes.fetchall()
    highlights = {}
    for note in notes:
        highlights[note['Z_PK']] = {
            'book_id': note['ZANNOTATIONASSETID'],
            'text': note['ZANNOTATIONSELECTEDTEXT']
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
    notes_db_name = 'AEAnnotation_v10312011_1727_local.sqlite'
    books_db_name = 'BKLibrary-1-091020131601.sqlite'
    notes_db = os.path.join(HOME, path, 'AEAnnotation', notes_db_name)
    books_db = os.path.join(HOME, path, 'BKLibrary', books_db_name)
    temp_dir = tempfile.gettempdir()
    temp_notes_db = os.path.join(temp_dir, 'temp_notes_database.sqlite')
    temp_books_db = os.path.join(temp_dir, 'temp_books_database.sqlite')
    shutil.copyfile(notes_db, temp_notes_db) # Achtung!
    shutil.copyfile(books_db, temp_books_db) # Achtung!
    con_notes, cur_notes = connect(temp_notes_db)
    con_books, cur_books = connect(temp_books_db)
    # Print highlights grouped by book
    books = get_books(cur_books)
    book_ids = [k for k, v in books.items()]
    for book_id in book_ids:
        highlights = get_highlights(cur_notes, cur_books, book_id)
        if highlights != {}:
            print('# {}\n'.format(books[book_id]['title']))
            for highlight in [v['text'] for k, v in highlights.items()]:
                print('{}\n\n---\n\n'.format(highlight))
    close(con_notes)
    close(con_books)


if __name__ == '__main__':
    main()