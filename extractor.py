import os
import shutil
import tempfile
import sqlite3

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


def get_annotations(cur):
    query = 'SELECT * \
        FROM ZAEANNOTATION \
        WHERE ZANNOTATIONREPRESENTATIVETEXT IS NOT NULL \
        ORDER BY ZANNOTATIONCREATIONDATE DESC'
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        print(row['ZANNOTATIONREPRESENTATIVETEXT'])
        metadata = {
            'id': row['Z_PK'],
            'book_id': row['ZANNOTATIONASSETID'],
            'created': row['ZANNOTATIONCREATIONDATE']
        }
        print('\nMetadata: {}'.format(metadata))
        print('\n---\n')


def main():
    path = 'Library/Containers/com.apple.iBooksX/Data/Documents/AEAnnotation'
    db = os.path.join(HOME, path, 'AEAnnotation_v10312011_1727_local.sqlite')
    temp_dir = tempfile.gettempdir()
    temp_db = os.path.join(temp_dir, 'temp_database.sqlite')
    shutil.copyfile(db, temp_db) # Achtung!
    con, cur = connect(temp_db)
    get_annotations(cur)
    close(con)


if __name__ == '__main__':
    main()