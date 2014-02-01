import xml.etree.ElementTree as ET
import pinboard
import urllib
import urllib2
import httplib2

import os
import sys
import re
# import cPickle as pickle

import micawber
import gdata
import gdata.youtube.service
from gdata import youtube
from gdata import apps
from gdata import client
from gdata import gauth

from flask import Flask
from flask import Markup
from flask import request
from flask import session
from flask import g
from flask import redirect
from flask import url_for
from flask import abort
from flask import render_template
from flask import flash
from flask import session
from flask import Response
from flask import jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required

from pintube import app
from __init__ import db
# from __init__ import models
from __init__ import login_manager
from forms import Pinboard_Login_Form
from models import User
from models import Info


# Initializing GData YouTubeService() used to generate the object so that we can communicate with the YouTube API
youtube_service = gdata.youtube.service.YouTubeService()
youtube_service.ssl = True

youtube_service.developer_key = 'AI39si5JGdicli8WGHhzGfW07rvFHMmlLJMtpB1zx3rpBhaBruxL4wkqGFPkQ0Dj2MDFObGCsR_wphhr3N9QpyTUOH9y_aeWsQ'

youtube_service.source = 'PinTube'

has_youtube = False
has_pinboard = False
embed_videos = []
authsub_token = ''
pin_login = {}
pinboard_object = ""

def GetAuthSubUrl():
    next = 'http://localhost:5000/'
    scope = 'http://gdata.youtube.com'
    secure = False
    session = True
    # youtube_service = gdata.youtube.service.YouTubeService()
    return youtube_service.GenerateAuthSubURL(next, scope, secure, session)



vid_id_pattern = r"""youtu(?:\.be|be\.com)/(?:.*v(?:/|=)|(?:.*/)?)([a-zA-Z0-9-_]+)"""
def get_video_id(vid_url):
    return re.search(vid_id_pattern, vid_url).group(1)

playlist_id_pattern = r"""([a-zA-Z0-9_\-]{18})"""
def get_playlist_id(playlist_url):
    return re.search(playlist_id_pattern, playlist_url).group(0)

subscription_id_pattern = r"""(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/ ]{11})"""
def get_subscription_id(subscription_url):
    print "Subscription URL is %s" % subscription_url
    result = re.search(subscription_id_pattern, subscription_url)
    if result is not None:
        return result.group(0)
    return None

def get_video_name(video_entry):
    return video_entry.media.title.text

def get_playlist_name(playlist_id=None, playlist_entry=None):
    if (playlist_id):
        youtube_service.GetYouTubePlaylistVideoFeed(uri=playlist_uri)
    elif(playlist_entry):
        return playlist_entry.title.text
    return None

def get_video_entry(video_entry=None, video_id=None):
    if video_id:
        return youtube_service.GetYouTubeVideoEntry(video_id)
    elif video_entry:
        vid_id = video_entry.id.text
        return youtube_service.GetYouTubeVideoEntry(vid_id)
    return None

def get_playlist_entry(service, playlist_entry=None, playlist_id=None):
    if playlist_id:
        result = service.GetYouTubePlaylistEntry(playlist_id)
        return result
    elif playlist_entry:
        plist_id = playlist_entry.id.text
        return service.GetYouTubePlaylistEntry(plist_id)

    return None

def get_subscription_entry(sub_entry=None, sub_id=None):
    if sub_id:
        return youtube_service.GetYouTubeSubscriptionEntry(sub_id)
    elif sub_entry:
        s_id = sub_entry.id.text
        return youtube_service.GetYouTubeSubscriptionEntry(s_id)

    return None

def get_user_playlist_feed():
    return youtube_service.GetYouTubePlaylistFeed(username='default')

def get_playlist_video_feed(playlist_id):
    return youtube_service.GetYouTubePlaylistVideoFeed(playlist_id=playlist_id)

def get_subscription_feed():
    return youtube_service.GetYouTubeSubscriptionFeed(username='default')

def get_video_pic(video_id):
    return """<img src="http://img.youtube.com/vi/{0}/hqdefault.jpg"></img>""".format(video_id)


def add_video_to_playlist(video_id, playlist_id, position):
    url = 'https://gdata.youtube.com/feeds/api/playlists/%s?v=2' % playlist_id

    headers = {'Content-Type' : 'application/atom+xml',
               'Authorization' : 'Bearer %s' % authsub_token,
               'GData-Version' : '2',
               'X-GData-Key' : '%s' % youtube_service.developer_key}

    xml = """<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://gdata.youtube.com/schemas/2007"><id>{0}</id><yt:position>{1}</yt:position></entry>""".format(video_id, position)

    params = {'key': youtube_service.developer_key}

    return youtube_service.Post(xml, url, headers, url_params=params)

def create_playlist(playlist_title, playlist_desc):
    return youtube_service.AddPlaylist(playlist_title, playlist_desc)

def add_subscription(subscription_id):
    pass

def is_vid_in_playlist(video_id, playlist_id):
    pass

def does_playlist_exist(playlist_id):
    pass



def test_pinboard(user, passw):
    user = '' + user
    passw = '' + passw

    try:
        p = pinboard.open(username=user, password=passw)
    except urllib2.HTTPError, error:
        print error
        return False
    return True

video_pattern = '(watch+\Wv\W)'
playlist_pattern = '(playlist+\Wlist=)'
channel_pattern = '(user/)'
pinboard_data = {}

def get_pintubes(username, password):
    videos = []
    playlists = []
    channels = []
    tags_for_vids = {}
    pintubes = {}
    pinboard_object = pinboard.open(username, password)
    db_videos = {}
    db_playlists = {}
    db_subscriptions = {}
    checker = str(pinboard_object['last_updated'])
    last_updated = User.query.filter(User.last_updated == checker)
    # last_updated = User.query.filter_by(User.last_updated == checker).scalar
    print "Last Updated is: %s" % last_updated.scalar()

    if last_updated.scalar() is None:
        posts = pinboard_object.posts(tag="youtube", count=1000)

        for post in posts:
            url = post[u'href']
            tags = post[u'tags']
            if re.search(video_pattern, url):
                db_videos.setdefault(get_video_name(get_video_entry(video_id=get_video_id(url))), url)
                videos.append(url)
                for tag in tags:
                    tag = str(tag)
                    if tag in tags_for_vids:
                        tags_for_vids[tag].append(url)
                    elif tag != "youtube":
                        tags_for_vids.setdefault(tag, [url])
            elif re.search(playlist_pattern, url):
                temp = get_playlist_id(url)
                temp2 = get_playlist_entry(youtube_service, playlist_id=temp)
                temp3 = get_playlist_name(playlist_entry=temp2)
                db_playlists.setdefault(temp3, url)
                playlists.append(url)
            elif re.search(channel_pattern, url):
                g.url = url
                db_subscriptions.setdefault(get_subscription_id(g.url), url)
                channels.append(url)


        user = User(username=username, last_updated=checker)
        info = Info(pinboard_videos=db_videos, pinboard_playlists=playlists, pinboard_subscriptions=channels, users=user)
        db.session.add(user)
        db.session.commit()

    else:
        print "Not updated since last accessed"

    return {"videos": videos, "playlists": playlists, "channels": channels, "vid_tags": tags_for_vids}



@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/pinboard', methods=['GET', 'POST'])
def pinboard_login():
    form = Pinboard_Login_Form()
    global has_pinboard
    global pinboard_data
    global pin_login

    if form.validate_on_submit():
        session['pin_remember_me'] = form.pin_remember_me.data

        if test_pinboard(form.pin_user_id.data, form.pin_password.data):
            pinboard_data = get_pintubes(form.pin_user_id.data, form.pin_password.data)
            pin_login.setdefault("username", form.pin_user_id)
            pin_login.setdefault("password", form.pin_password)

            has_pinboard = True
            return redirect(url_for('index'))
        else:

            return redirect(url_for('pinboard_login'))

    return render_template('pinboard_login.html', title='Sign In to Pinboard', form=form)

@app.route('/youtube', methods=['GET', 'POST'])
def youtube_login():
    authSubUrl = GetAuthSubUrl()
    return redirect(authSubUrl)

@app.route('/')
@app.route('/index')
def index():
    global has_youtube
    global authsub_token
    global embed_videos
    embed_playlists = []
    if "token" in request.args:
        authsub_token = request.args.get("token")
        youtube_service.SetAuthSubToken(authsub_token)
        youtube_service.UpgradeToSessionToken()
        has_youtube = True

    if has_youtube and has_pinboard:
        your_playlists = {}
        playlist_feed = get_user_playlist_feed()
        url_pattern = r"""(http(s?)://www.youtube.com/watch+\Wv\W[a-zA-Z0-9-_]+)"""

        """
        fo = open('playlist_feed.p', 'wb')
        pickle.dump(playlist_feed, fo)
        fo.close()
        """
        providers = micawber.bootstrap_basic()


        for video in pinboard_data["videos"]:
            # video_id = re.search(vid_id_pattern, video).group(1)
            # embed_url = """<iframe id="ytplayer" type="text/html" width="640" height="360" src="https://www.youtube.com/embed/{0}?theme=light" frameborder="0" allowfullscreen></iframe>""".format(video_id)
            # print "Embedded URL is: %s" % embed_url
            embed_videos.append(video)


        for playlist in pinboard_data["playlists"]:
            playlist_id = get_playlist_id(playlist)
            to_embed = Markup("""<iframe id="ytplayer" type="text/html" width="640" height="360"
                            src="https://www.youtube.com/embed/?listType=playlist&list={}&theme=light"
                            frameborder="0" allowfullscreen></iframe>""".format(playlist_id))
            embed_playlists.append(to_embed)

        # Copies the playlist Names, URIs and Videos to a dictionary
        for playlist_entry in playlist_feed.entry:
            playlist_entry_title = playlist_entry.title.text
            playlist_entry_id = playlist_entry.id.text.split('/')[-1]
            playlist_entry_video_feed = get_playlist_video_feed(playlist_entry_id)  # youtube_service.GetYouTubePlaylistVideoFeed(playlist_id=playlist_entry_id)
            your_playlists.setdefault(playlist_entry_title, [playlist_entry_id, {}])

            for playlist_video_entry in playlist_entry_video_feed.entry:
                video_title = playlist_video_entry.title.text
                video_id = playlist_video_entry.id.text
                video_entry = youtube_service.GetYouTubeVideoEntry(video_id)

                if video_entry.media.player is not None:
                    media_url = video_entry.media.player.url
                    media_url = re.search(url_pattern, media_url).group(0)
                    your_playlists[playlist_entry_title][1].setdefault(video_title, media_url)
                else:
                    your_playlists[playlist_entry_title][1].setdefault(video_title, video_id)


        for tag in pinboard_data["vid_tags"].keys():
            if tag not in your_playlists.keys():
                new_public_playlistentry = youtube_service.AddPlaylist(tag, 'A Pintube Playlist')

            else:
                for vid in pinboard_data["vid_tags"][tag]:
                    vid = str(vid)
                    vid = re.search(url_pattern, vid).group(0)
                    vids = your_playlists[tag][1]

                    if vid not in vids.values():  # Insufficient to check for already present video
                        vid_id = get_video_id(vid)
                        playlist_id = your_playlists[tag][0].replace('PL', '')
                        post = add_video_to_playlist(vid_id, playlist_id, 1)


    return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard, embed_videos=embed_videos, embed_playlists=embed_playlists)
