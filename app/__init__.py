from flask import Flask
from config import Config
from flask_admin import Admin, AdminIndexView
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(Config)
admin = Admin(app, index_view=AdminIndexView())
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
migrate = Migrate(app, db)

from app import routes, models