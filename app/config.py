class Config(object):
    DB_CONFIG = {
        'host': 'localhost',
        'port': '5432',
        'database': '',     # paste db name here
        'user': '',         # paste user name here
        'password': '',     # paste password here
    }
    SQLALCHEMY_DATABASE_URI = "postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s" % DB_CONFIG
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = ""   # place secret key
    SECRET_KEY = ""         # place secret key
