import os
basedir = os.path.abspath(os.path.dirname(__file__))

LOG_FILE = 'projet-imp-log.txt'
CSRF_ENABLED = True
SECRET_KEY = 'bacon'
SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db_imperium.db')
