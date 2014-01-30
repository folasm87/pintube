import sqlalchemy
from __init__ import db
from sqlalchemy import ForeignKey
# from sqlalchemy import relationship, backref


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    last_updated = db.Column(db.String(120), index=True, unique=True)
    token = db.Column(db.String(360), index=True, unique=True)

    info_id = db.Column(db.Integer, db.ForeignKey('info.id'))
    info = db.relationship('Info', backref=db.backref('users', lazy='dynamic'))  # , uselist=False)

    def __init__(self, username, last_updated, token, info):
        self.username = username
        self.last_updated = last_updated
        self.token = token
        self.info = info

    def __repr__(self):
        return '<User: %r, last updated at %r>' % (self.username, self.last_updated)

class Info(db.Model):

    __tablename__ = 'info'

    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.String(60), ForeignKey('users.id'))
    pinboard_videos = db.Column(db.String(300), index=True)  # , unique=True)
    pinboard_playlists = db.Column(db.String(300), index=True)  # , unique=True)
    pinboard_subscriptions = db.Column(db.String(300), index=True)  # , unique=True)
    youtube_playlists = db.Column(db.String(300), index=True)  # , unique=True)
    youtube_subscriptions = db.Column(db.String(300), index=True)  # , unique=True)

    # user = relationship("User", backref=backref('addresses', order_by=id))

    def __init__(self, username):
        self.username = username


    def __repr__(self):
        return '<User %r>' % (self.username)
