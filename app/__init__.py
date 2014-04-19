from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy

import inspect


app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

if not inspect.stack()[-1][1].startswith('db_create'): #  files for creating db
    from imperium import Imperium
    app.control = Imperium()
    app.control.loadModules()


    from app import views