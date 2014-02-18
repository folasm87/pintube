# import xml.etree.ElementTree as ET
import pinboard
import urllib
import urllib2
import httplib2
import StringIO
import gzip
from xml.dom import minidom

import os
import sys
import re
# import cPickle as pickle

import micawber
import gdata
import gdata.youtube.service
from gdata.service import RequestError
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
from pintube import db
from pintube import models
from pintube import login_manager
from forms import Pinboard_Login_Form
from models import User
from models import Info
from sqlalchemy.exc import IntegrityError


# Initializing GData YouTubeService() used to generate the object so that we can communicate with the YouTube API
youtube_service = gdata.youtube.service.YouTubeService()
youtube_service.ssl = True

youtube_service.developer_key = 'AI39si5JGdicli8WGHhzGfW07rvFHMmlLJMtpB1zx3rpBhaBruxL4wkqGFPkQ0Dj2MDFObGCsR_wphhr3N9QpyTUOH9y_aeWsQ'

youtube_service.source = 'PinTube'

has_youtube = False
has_pinboard = False
embed_videos = []
pinboard_data = {}
pinboard_object_data = {}
authsub_token = ''
# pin_login = {}
# pinboard_object = {}

def GetAuthSubUrl():
    next = 'http://localhost:5000/'
    scope = 'http://gdata.youtube.com'
    secure = False
    session = True
    # youtube_service = gdata.youtube.service.YouTubeService()
    return youtube_service.GenerateAuthSubURL(next, scope, secure, session)



vid_id_pattern = r"""youtu(?:\.be|be\.com)/(?:.*v(?:/|=)|(?:.*/)?)([a-zA-Z0-9-_]+)"""
def get_video_id(vid_url):
    print "Video URL is %s" % vid_url
    return re.search(vid_id_pattern, vid_url).group(1)

playlist_id_pattern = r"""([a-zA-Z0-9_\-]{11,100})"""  # r"""([a-zA-Z0-9_\-]{18})"""
def get_playlist_id(playlist_url=None, playlist_entry=None):
    id = ''
    if playlist_url:
        print "Playlist URL is %s" % playlist_url
        id = re.search(playlist_id_pattern, playlist_url).group(0)
        print "Playlist URL %s has an id : %s" % (playlist_url, id)

    else:
        id = playlist_entry.id.text.split('/')[-1]
        print "Playlist ID for the given Playlist Entry is %s" % id
    return id  # re.search(playlist_id_pattern, playlist_url).group(0)

# subscription_id_pattern = r"""(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/ ]{11})"""
# subscription_id_pattern = r"""(\w(?:.*/)|(?:.*))"""
# subscription_id_pattern = r"""(http://www.youtube.com/user/(\w(?:.*/)|(?:.*)))"""
def get_subscription_id(sub_url):
    print "Subscription URL is %s" % sub_url
    prev = None
    for part in sub_url.split('/'):
        if prev == 'user':
            print "Subscription ID is %s" % part
            return part
        prev = part
    raise ValueError('Could not find user in url')
    print "Subscription ID is None"
    return None


def get_video_name(video_entry):
    return video_entry.media.title.text

def get_playlist_name(playlist_id=None, playlist_entry=None):
    if (playlist_id):
        # youtube_service.GetYouTubePlaylistVideoFeed(id=playlist_id)
        uri = 'https://gdata.youtube.com/feeds/api/playlists/' + playlist_id
        print "Playlist URI: %s" % uri
        return youtube_service.GetYouTubePlaylistFeed(uri).title.text
    elif(playlist_entry):
        return playlist_entry.title.text
    return None

def get_subscription_name(sub_id=None, sub_entry=None):
    if (sub_id):
        uri = "https://gdata.youtube.com/feeds/api/users/" + sub_id
        title = youtube_service.GetYouTubeSubscriptionEntry(uri).title.text
        print "Subscription URI is %s" % uri
        print "Subscription Title is %s" % title
        return title
    elif(sub_entry):
        title = sub_entry.title.text
        print "Subscription Title is %s" % title
        return title
    return None

def get_video_entry(video_entry=None, vid_id=None):
    if vid_id:
        return youtube_service.GetYouTubeVideoEntry(video_id=vid_id)
    elif video_entry:
        vid_id = video_entry.id.text
        return youtube_service.GetYouTubeVideoEntry(video_id=vid_id)
    return None

def get_playlist_entry(service, playlist_entry=None, playlist_id=None):
    """
    if playlist_id:
        print "Playlist ID is %s" % playlist_id
        # playlist_id = playlist_id.replace('PL', '')
        uri = "https://gdata.youtube.com/feeds/api/playlists/{0}".format(playlist_id)
        result = service.GetYouTubePlaylistEntry(uri)
        return result
    """

    if playlist_entry:
        # plist_id = playlist_entry.id.text
        plist_id = get_playlist_id(playlist_entry=playlist_entry)
        plist_uri = "https://gdata.youtube.com/feeds/api/playlists/" + plist_id
        return service.GetYouTubePlaylistEntry(plist_uri)

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

def get_embed_playlist(playlist_id):
    to_embed = Markup("""<iframe id="ytplayer" type="text/html" width="640" height="360"
                            src="https://www.youtube.com/embed/?listType=playlist&list={0}&theme=light"
                            frameborder="0" allowfullscreen></iframe>""".format(playlist_id))
    return to_embed


def get_embed_subscription(sub_id):
    to_embed = Markup("""<div class="g-ytsubscribe" data-channel="{0}" data-layout="full" data-count="default"></div>""".format(sub_id))
    return to_embed


# Code from Python-Pinboard. Used to directly get to last_updated information
USER_AGENT = "Python-Pinboard/1.0 +http://morgancraft.com/service_layer/python-pinboard/"
def get_last_update(username, password):
    url = "https://api.pinboard.in/v1/posts/update"
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password("API", "https://api.pinboard.in/", username, password)
    opener = urllib2.build_opener(auth_handler)
    opener.addheaders = [("User-agent", USER_AGENT), ('Accept-encoding', 'gzip')]
    urllib2.install_opener(opener)
    xml = ''
    try:
        # # for pinboard a gzip request is made
        raw_xml = urllib2.urlopen(url)
        compresseddata = raw_xml.read()
        # # bing unpackaging gzipped stream buffer
        compressedstream = StringIO.StringIO(compresseddata)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        xml = gzipper.read()
        xml = minidom.parseString(xml)
        xml = xml.firstChild.getAttribute("time")
        # print "XML is: %s" % xml
    except urllib2.URLError, e:
        raise e

    return xml

def get_pinboard(user, passw):
    user = '' + user
    passw = '' + passw

    try:
        p = pinboard.open(username=user, password=passw)
        print "Get Pinboard returns " + str(p)
    except urllib2.HTTPError, error:
        print error
        return {"Pass": False}
    return {"Pass": True, "pinboard_object": p, "username": user, "password": passw}

video_pattern = '(watch+\Wv\W)'
playlist_pattern = '(playlist+\Wlist=)'
channel_pattern = '(user/)'

def get_pintubes(pinboard_object):

    # global pinboard_object
    last_update = get_last_update(pinboard_object["username"], pinboard_object["password"])
    videos = []
    playlists = []
    channels = []
    tags_for_vids = {}
    pintubes = {}
    db_videos = {}
    db_playlists = {}
    db_subscriptions = {}
    check_update = User.query.filter(User.last_updated == last_update).first()
    if ((check_update is None) or (str(check_update.last_updated) != last_update)):
        posts = pinboard_object["pinboard_object"].posts(tag="youtube", count=1000)

        for post in posts:
            url = post[u'href']
            tags = post[u'tags']
            if re.search(video_pattern, url):
                video_id = get_video_id(url)
                print "Video ID is %s" % video_id
                try:
                    video_entry = get_video_entry(vid_id=video_id)

                except RequestError, error:
                    print error
                    print "Video Error!"
                    continue

                video_name = get_video_name(video_entry)
                print "Video Name is %s" % video_name
                if url is None:
                    print "Video URL is NONE"

                temp_tags = []
                for tag in tags:
                    tag = str(tag)
                    temp_tags.append(tag)

                video_details = {"url":url, "tags":temp_tags}

                db_videos.setdefault(video_name, video_details)
                videos.append(url)
                """
                for tag in tags:
                    tag = str(tag)
                    if tag in tags_for_vids:
                        tags_for_vids[tag].append(url)
                    elif tag != "youtube":
                        tags_for_vids.setdefault(tag, [url])
                """
            elif re.search(playlist_pattern, url):
                playlist_id = get_playlist_id(playlist_url=url)
                print "Playlist ID: %s" % playlist_id

                try:
                    playlist_name = get_playlist_name(playlist_id)
                except RequestError, error:
                    print error
                    print "Playlist Error!"
                    continue
                playlist_details = {"url":url, "embed":get_embed_playlist(playlist_id)}
                db_playlists.setdefault(playlist_name, playlist_details)
                playlists.append(url)

            elif re.search(channel_pattern, url):
                subscription_id = get_subscription_id(url)
                try:
                    subscription_name = get_subscription_name(sub_id=subscription_id)
                except RequestError, error:
                    print error
                    print "Subscription Error!"
                    continue
                subscription_details = {"url":url, "embed":get_embed_subscription(subscription_id)}
                db_subscriptions.setdefault(subscription_name, subscription_details)
                channels.append(url)

        """
        users = models.User.query.all()
        infoz = models.Info.query.all()

        for u in users:
                db.session.delete(u)

        for i in infoz:
            db.session.delete(i)

        
        if (len(users) > 0 and len(infoz) > 0):
            for u in users:
                db.session.delete(u)

            for i in infoz:
                db.session.delete(i)
        """

        # db.create_all()
        info = Info(pinboard_videos=db_videos, pinboard_playlists=db_playlists, pinboard_subscriptions=db_subscriptions)
        # user = User(username=pinboard_object["username"], last_updated=last_update, info=info)
        user = User.query.filter_by(username=pinboard_object["username"]).first()
        user.last_updated = last_update
        user.info = info

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError, error:
            print error
            print "You've already added a row with the same user_name before"

        return {"videos": db_videos, "playlists": db_playlists, "channels": db_subscriptions}

        """
    elif(check_update.last_updated is None):
        print "Pinboard was last updated at %s" % str(checker)
        check_update.last_updated = checker
        db.session.add(check_update)
        db.session.commit()
        
    else:
        print "Not updated since last accessed"
        # check_update.last_updated = last_update  # pinboard_object['last_updated']
        # db.session.add(check_update)
        # db.session.commit()
        current_user = User.query.filter_by(username=pinboard_object["username"]).first()
        # print current_user
        current_info = current_user.info
        # print current_info
        return {"videos": current_info.pinboard_videos.values(), "playlists": current_info.pinboard_playlists.values(), "channels": current_info.pinboard_subscriptions.values()}
        """

    return {"videos": videos, "playlists": playlists, "channels": channels}  # , "vid_tags": tags_for_vids}



@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/pinboard', methods=['GET', 'POST'])
def pinboard_login():
    form = Pinboard_Login_Form()
    global has_pinboard
    global pinboard_data
    global pinboard_object_data

    if form.validate_on_submit():
        session['pin_remember_me'] = form.pin_remember_me.data
        pinboard_object_data = get_pinboard(form.pin_user_id.data, form.pin_password.data)
        if pinboard_object_data["Pass"]:
            pinboard_data = get_pintubes(pinboard_object_data)
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

        """
        for video in pinboard_data["videos"]:
            # video_id = re.search(vid_id_pattern, video).group(1)
            # embed_url = <iframe id="ytplayer" type="text/html" width="640" height="360" src="https://www.youtube.com/embed/{0}?theme=light" frameborder="0" allowfullscreen></iframe>.format(video_id)
            # print "Embedded URL is: %s" % embed_url
            embed_videos.append(video)


        for playlist in pinboard_data["playlists"]:
            playlist_id = get_playlist_id(playlist)
            to_embed = Markup(<iframe id="ytplayer" type="text/html" width="640" height="360"
                            src="https://www.youtube.com/embed/?listType=playlist&list={0}&theme=light"
                            frameborder="0" allowfullscreen></iframe>.format(playlist_id))
            embed_playlists.append(to_embed)
            
        """

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

        """
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

        """
        user = User.query.filter_by(username=pinboard_object_data["username"]).first_or_404()
        videos = user.info.pinboard_videos
        playlists = user.info.pinboard_playlists
        subscriptions = user.info.pinboard_subscriptions
        print "Testing User Here: %s" % user
        return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard, videos=videos, playlists=playlists, subscriptions=subscriptions)
    return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard)
