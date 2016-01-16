from pithub import app  # context
from flask import g     # used to identify database type (?)
import sqlite3
# database methods

def connect_db():
    # connects to database
    rv = sqlite3.connect('pithub.db')
    rv.row_factory = sqlite3.Row
    return rv


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def query_db(query, args=None, one=False):
    if args:
        cursor = get_db().execute(query, args)
    else:
        cursor = get_db().execute(query)
    rv = cursor.fetchall()
    cursor.close()
    return (rv[0] if rv else None) if one else rv


def add_query(query, args=None):
    db = get_db()
    if args:
        db.execute(query, args)
    else:
        db.execute(query)
    db.commit()
