from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config import Config
from app.utils import datetimeformat

# app init
app = Flask(__name__)
app.config.from_object(Config)

# custom jinja2 filters
app.jinja_env.filters["datetimeformat"] = datetimeformat

# database init
db = SQLAlchemy(app)

from app import models

# migrate init
migrate = Migrate(app, db)

from app import routes

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix="/api")
