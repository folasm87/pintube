import sqlalchemy
from __init__ import db
from sqlalchemy import ForeignKey
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.ext.mutable import Mutable
import json
# from sqlalchemy import relationship, backref



class JSONEncodedDict(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, state):
        self.update(state)


MutableDict.associate_with(JSONEncodedDict)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    last_updated = db.Column(db.String(120), index=True, unique=True)
    token = db.Column(db.String(360), index=True, unique=True)

    # info_id = db.Column(db.Integer, db.ForeignKey('info.id'))
    info = db.relationship('Info', backref=db.backref('users', lazy='dynamic'))  # , uselist=False)

    def __init__(self, username, last_updated, token, info):
        self.username = username
        self.last_updated = last_updated
        self.token = token
        self.info = info

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User: %r, last updated at %r>' % (self.username, self.last_updated)

class Info(db.Model):

    __tablename__ = 'info'

    id = db.Column(db.Integer, primary_key=True)
    pinboard_videos = db.Column(db.JSONEncodedDict, index=True)
    pinboard_playlists = db.Column(db.JSONEncodedDict, index=True)
    pinboard_subscriptions = db.Column(db.JSONEncodedDict, index=True)
    youtube_playlists = db.Column(db.JSONEncodedDict, index=True)
    youtube_subscriptions = db.Column(db.JSONEncodedDict, index=True)

    user_id = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, username):
        self.username = username


    def __repr__(self):
        return '<User %r>' % (self.username)
