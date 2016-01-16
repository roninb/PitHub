from flask import Flask             # framework, used to run app
from flask import render_template   # renders html templates in said dir
from flask import session           # handles sessioning between pages
from flask import request           # for dealing with post
from flask import redirect          # used after logging out
from flask import g                 # used to identify database type (?)
#import db                           # database functionality
import os                           # connect to cloud9 hosting server
import sqlite3                      # database functionality
import json                         # used to easily deal with github data
from datetime import datetime       # used to measure your goals
from datetime import timedelta      # used to measure limit what we collect

app = Flask(__name__)

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

# connecting to github through api
def get_commits(github_username, github_repo):
    current_datetime = datetime.now()
    two_weeks_ago = timedelta(weeks=2)
    since = current_datetime - two_weeks_ago
    github_username = str(github_username[0])
    github_repo = str(github_repo[0])
    print github_username + github_repo
    githuburl = 'https://api.github.com/repos/%s/%s/commits?since=%s' % (github_username, github_repo, since.isoformat())
    r = requests.get(githuburl)
    j = r.json()

    add_query('update pit set commits=? where uid=?', (len(j), str(session['userid'])))

# view methods

@app.route("/", methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        for q in query_db('select * from user where username=?', (request.form['username'],)):
            error = "Username not found"
            if request.form['password'] == q['password']:
                session['username'] = q['username']
                session['userid'] = q['userid']
                session['github_username'] = q['gusername']
                for p in query_db('select * from pit where uid=?', (str(q['userid']),)):
                    session['pitname'] = p['name']
                    session['health'] = p['health']
                # we can add pit_id to the session and template so that pet can be linked via a dynamic /pit/<pit_id> url
                session['logged_in']=True
                return render_template("dash.html", name=session['username'], pitname=session['pitname'], health=session['health'])
            else:
                error = 'Invalid Password'
    return render_template('home.html', error=error)

@app.route("/logout/", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect("/")

@app.route("/dash/")
def dash():
    return render_template("dash.html", name=session['username'], pitname=session['pitname'])

@app.route("/pet/", methods=['GET', 'POST'])
def pet():
    if not session.get('logged_in'):
        return render_template("home.html", error='Must login before accessing pet page!')
    return "Hello, %s. %s is awake to play!" % (session['username'], session['pitname'])

@app.route("/feed/")
def feed():
    try:
        repos = query_db('select * from repo where uid=?', session['userid'])
        for repo in repos:
            gu = session['github_username']
            rn = repo['name']
            get_commits(gu,rn)

    except sqlite3.error, e:
        error = "You must have at least one repo added under settings before trying to feed your pet!"
        render_template("/home.html", error=error)

@app.route("/settings/", methods=['GET', 'POST'])
def settings(): 
    if not session.get('logged_in'):
        return render_template("home.html", error="Must login before accessing settings page!")
    error=None
    if request.method == "POST":
        if request.form['gusername']:
            add_query('update user set gusername=? where userid=?', (request.form['gusername'], str(session['userid']),))
        if request.form['newrepo']:
            if request.form['commits']:
                add_query('insert into repo values(NULL,?,?,?)', (request.form['newrepo'], request.form['commits'], str(session['userid']),))
            else:
                add_query('insert into repo values(NULL,?,0,?)', (request.form['newrepo'], str(session['userid']),))
        if request.form['repos'] and request.form['commits'] and not request.form['newrepo']:
            add_query('update repo set commits=? where uid=?', (request.form['commits'], str(session['userid']),))
        if request.form['password']:
            add_query('update user set password=? where userid=?', (request.form['password'], str(session['userid']),))
        if request.form['pitname']:
            add_query('update pit set name=? where uid=?', (request.form['pitname'], str(session['userid']),))
    repos = query_db('select * from repo where uid=?', (str(session['userid']),))
    if len(repos) == 1:
        oldrepos = ["empty", "placeholder"]
        oldrepos[1] = repos[0]
        temprepos = repos
        repos = oldrepos
    return render_template("/settings.html", error=error, repos=repos)

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
            ident = query_db('select userid from user where username=?', (str(request.form['username']),))[0][0]
            print int(ident)
            add_query('insert into pit values(NULL,?,0,?,?)', (str(request.form['pitname']), datetime.now(), str(ident)))
            session['username'] = request.form['username']
            session['userid'] = str(ident)
            session['pitname'] = request.form['pitname']
            session['health'] = 0
            return render_template("dash.html", name=session['username'], pitname=session['pitname'], health=session['health'])
    return render_template("signup.html", error=error)

if __name__ == "__main__":
    app.secret_key = 'knighthacks'
    app.config['SESSION_TYPE'] = 'memcache'
    app.run(debug=True, host=os.getenv('IP','0.0.0.0'), port=int(os.getenv('PORT', '8080')))
