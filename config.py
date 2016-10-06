import os
basedir = os.path.abspath(os.path.dirname(__file__))

TEMPLATES_AUTO_RELOAD = True
WTF_CSRF_ENABLED = True
SECRET_KEY = "na-na-na-na-na-na-na-na-na-na-na-BATMAN"

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
