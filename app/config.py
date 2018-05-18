class Config(object):
    DB_CONFIG = {
        'host': 'db',
        'port': '5432',
        'database': 'postgres',     # paste db name here
        'user': 'postgres',         # paste user name here
        'password': 'password',     # paste password here
    }
    SQLALCHEMY_DATABASE_URI = "postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s" % DB_CONFIG
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "dev"   # place secret key
    SECRET_KEY = "dev"         # place secret key
