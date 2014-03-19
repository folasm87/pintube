import sqlalchemy
# from pintube import db
from __init__ import db
from __init__ import app
from sqlalchemy import ForeignKey
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.ext.mutable import Mutable
from flask.ext.restless import APIManager
import json
# from sqlalchemy import relationship, backref

from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView



class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


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


# MutableDict.associate_with(JSONEncodedDict)

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    sqlite_autoincrement = True
    username = db.Column(db.String(80), index=True, unique=True)
    last_updated = db.Column(db.String(120), index=True, unique=True)
    # token = db.Column(db.String(360), index=True, unique=True)

    # info_id = db.Column(db.Integer, db.ForeignKey('info.id'))
    info = db.relationship('Info', backref=db.backref('user'), uselist=False)  # , uselist=False) lazy='dynamic'


    def __init__(self, username, last_updated, info):
        self.username = username
        self.last_updated = last_updated
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
        return '<User( %s, %s, %s)>' % (self.username, self.last_updated, self.info)

class Info(db.Model):

    __tablename__ = 'info'

    id = db.Column(db.Integer, primary_key=True)
    pinboard_videos = db.Column(MutableDict.as_mutable(JSONEncodedDict))
    pinboard_playlists = db.Column(MutableDict.as_mutable(JSONEncodedDict))
    pinboard_subscriptions = db.Column(MutableDict.as_mutable(JSONEncodedDict))
    # youtube_videos = db.Column(MutableDict.as_mutable(JSONEncodedDict), index=True)
    youtube_playlists = db.Column(MutableDict.as_mutable(JSONEncodedDict))
    user_id = db.Column(db.Integer, ForeignKey('user.id'))


    def __init__(self, pinboard_videos, pinboard_playlists, pinboard_subscriptions, youtube_playlists):
        self.pinboard_videos = pinboard_videos
        self.pinboard_playlists = pinboard_playlists
        self.pinboard_subscriptions = pinboard_subscriptions
        self.youtube_playlists = youtube_playlists



    def __repr__(self):
        return '<Info(%s, %s, %s)>' % (self.pinboard_videos, self.pinboard_playlists, self.pinboard_subscriptions)


admin = Admin(app)
admin.add_view(MyView(name='Hello'))
admin.add_view(ModelView(User, db.session))
"""
db.create_all()

api_manager = APIManager(app, flask_sqlalchemy_db=db)
api_manager.create_api(User, methods=['GET', 'POST', 'DELETE', 'PUT'])
api_manager.create_api(Info, methods=['GET', 'POST', 'DELETE', 'PUT'])
"""
