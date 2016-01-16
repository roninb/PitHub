from flask import Flask             # framework, used to run app
from flask import render_template   # renders html templates in said dir
from flask import session           # handles sessioning between pages
from flask import request           # for dealing with post
from flask import redirect          # used after logging out
from flask import g                 # used to identify database type (?)
#import db                           # database functionality
import sqlite3                      # database functionality
from datetime import datetime       # used to measure your goals

app = Flask(__name__)

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

@app.route("/", methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        for q in query_db('select * from user where username=?', (request.form['username'],)):
            error = "Username not found"
            if request.form['password'] == q['password']:
                session['username'] = q['username']
                session['github_username'] = q['gusername']
                for p in query_db('select * from pit where uid=?', (str(q['userid']),)):
                    session['pitname'] = p['name']
                    session['health'] = p['health']
                # we can add pit_id to the session and template so that pet can be linked via a dynamic /pit/<pit_id> url
                session['logged_in']=True
                return render_template("dash.html", name=session['username'], pitname=str(session['pitname']), health=session['health'])
            else:
                error = 'Invalid Password'
    return render_template('home.html', error=error)

@app.route("/logout/", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect("/")

@app.route("/pet/")
def pet():
    if not session.get('logged_in'):
        return render_template("home.html", error='Must login before accessing pet page!')
    return "Hello, %s. %s is awake to play!" % (session['username'], session['pitname'])

@app.route('/signup/', methods=['GET','POST'])
def signup():
    error = None
    if request.method == 'POST':
        for q in query_db('select * from user'):
            if request.form['username'] == q['username']:
                error = 'This username has been taken.'
            if request.form['password'] != request.form['password2']:
                error = 'Both passwords must be the same'
        if not error:
            session['logged_in']=True
            add_query('insert into user values(NULL,?,?,NULL)', (request.form['username'], request.form['password']))
            ident = query_db('select userid from user where username=?', (str(request.form['username']),))
            add_query('insert into pit values(NULL,?,0,?,?)', (str(request.form['pitname']), datetime.now(), str(ident)))
            session['username'] = request.form['username']
            session['pitname'] = request.form['pitname']
            session['health'] = 0
            return render_template("dash.html", name=session['username'], pitname=session['pitname'], health=session['health'])
    return render_template("signup.html", error=error)

if __name__ == "__main__":
    app.secret_key = 'knighthacks'
    app.config['SESSION_TYPE'] = 'memcache'
    app.run(debug=True)
