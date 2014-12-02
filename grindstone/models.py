from datetime import datetime

import arrow
from flask import url_for
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .exceptions import ValidationError
from . import db

class Permission:
    READ_ONLY = 0x01
    MEETING_CREATOR = 0x02
    ACCOUNT_MANAGER = 0x04
    ACCOUNT_OWNER = 0x08
    METAREACT_ADMIN = 0x512


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='roles', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    """
        Represents a single user in the system.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    google_access_token = db.Column(db.String(512))

    def __init__(self, email, password):
        self.email = email
        self.password = password

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_json(self):
        json_user = {
            'url': url_for('get_user', user_id=self.id, _external=True),
            'email': self.email,
        }
        return json_user
    
    def __repr__(self):
        return '<User %r>' % self.email

class Developer(db.Model):
    """
        All the things you do and do not want to display to your adoring
        software development fans.
    """ 
    __table_name__ = 'developer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    status = db.Column(db.String(200))


class Follower(db.Model):
    """
        Represents a count of followers for one service.
    """
    __tablename__ = 'follower'
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.Integer, db.ForeignKey('service.id'))
    count = db.Column(db.Integer)
    timestamped = db.Column(db.DateTime)

    def __init__(self, service, count=0, timestamp=datetime.utcnow()):
        self.service = service.id
        self.count = count
        self.timestamped = timestamp


class DayTrack(db.Model):
    """
        A single day of tracking.
    """
    __tablename__ = 'daytrack'
    id = db.Column(db.Integer, primary_key=True)
    timestamped = db.Column(db.DateTime)
    workout = db.Column(db.Boolean, default=False)
    newsletter = db.Column(db.Boolean, default=False)
    drinks = db.Column(db.Integer, default=0)
    talk = db.Column(db.Boolean, default=False)
    
    def __init__(self, create_date):
        self.timestamped = create_date

    @property
    def permalink(self):
        return url_for('get_daytrack', id=self.id, _external=True)
    
    def to_json(self):
        json_daytrack = {
            'url': url_for('get_daytrack', id=self.id, _external=True),
            'date': arrow.get(self.timestamped).format("YYYY-MM-DD"),
            'workout': self.workout,
            'drinks': self.drinks,
        }
        return json_daytrack
    

class Writing(db.Model):
    """
        A discrete piece of writing, such as a blog post or article.
    """
    __table__name = 'writing'
    id = db.Column(db.Integer, primary_key=True)
    timestamped = db.Column(db.DateTime)
    title = db.Column(db.String(1024))
    url = db.Column(db.String(2048))


class Service(db.Model):
    """
        Represents a service that is being tracked by the user,
        for example Twitter or GitHub.
    """
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    site_url = db.Column(db.String(1024))
    followers = db.relationship('Follower', backref='followers',
                                lazy='dynamic')

    def __init__(self, name, site_url):
        self.name = name
        self.site_url = site_url

    @property
    def permalink(self):
        return url_for('get_service', id=self.id, _external=True)

    def to_json(self):
        json_service = {
            'url': self.permalink,
            'name': self.name,
            'site_url': self.site_url,
        }
        return json_service

