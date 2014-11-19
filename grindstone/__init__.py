from celery import Celery
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.socketio import SocketIO
import redis

from config import REDIS_SERVER, REDIS_PORT, REDIS_DB
from utils import make_celery

app = Flask(__name__)
app.config.from_object('grindstone.config')

redis_db = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=REDIS_DB)

socketio = SocketIO(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'sign_in'
login_manager.init_app(app)

celery = make_celery(app)

from . import views, admin, tasks, api #, websockets
