from flask import Flask,g, session

from config import Config
from flask_bootstrap import Bootstrap
#TODO report that flask_SQL is imported and why
# to use SQLalchemy we had to run: pip install flask-security-too[fsqla,common]
# and for flask login we ran:  pip install flask-login
#from flask_login import LoginManager, login_required, login_user, current_user, logout_user
#from flask_sqlalchemy import SQLAlchemy
#from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from flask_session import Session

import sqlite3
import os

# create and configure app
app = Flask(__name__)
app.config['SECRET_KEY'] = '4980b19f16449c5c8385c37ec09f2a44'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

Bootstrap(app)
app.config.from_object(Config)
#sess = Session(app)
#sess.init_app(app)

#Sectret key protects against modifying cookies and cross site forgery attacks
#TODO make the secret key to an enviroment variable
# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# perform generic query, not very secure yet
def query_db(query, one=False):
    db = get_db()
    cursor = db.execute(query)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

# TODO: Add more specific queries to simplify code

# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes