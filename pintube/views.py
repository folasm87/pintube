"""
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


import gdata
import gdata.youtube.service
from gdata.service import RequestError
from gdata import youtube
from gdata import apps
from gdata import client
from gdata import gauth

"""

import gdata
import micawber
from pinclass import Pintube
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

"""
# Initializing GData, YouTubeService() used to generate the object so that we can communicate with the YouTube API
youtube_service = gdata.youtube.service.YouTubeService()
youtube_service.ssl = True
youtube_service.developer_key = 'AI39si5JGdicli8WGHhzGfW07rvFHMmlLJMtpB1zx3rpBhaBruxL4wkqGFPkQ0Dj2MDFObGCsR_wphhr3N9QpyTUOH9y_aeWsQ'
youtube_service.source = 'PinTube'
"""
has_youtube = False
has_pinboard = False
authsub_token = ''
pintube_object = Pintube()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/pinboard', methods=['GET', 'POST'])
def pinboard_login():
    form = Pinboard_Login_Form()
    global has_pinboard
    global pintube_object
    # global pinboard_data
    global pinboard_object_data

    if form.validate_on_submit():
        session['pin_remember_me'] = form.pin_remember_me.data
        # pinboard_object_data = get_pinboard(form.pin_user_id.data, form.pin_password.data)
        # usern = form.pin_user_id.data
        # passw = form.pin_password.data
        # pintube_object = Pintube(usern)
        p = pintube_object.get_pinboard(form.pin_user_id.data, form.pin_password.data)
        # pintube_object.pinboard_object_data = p
        if p["Pass"]:
            # pinboard_data = get_pintubes(p)
            pintube_object.get_pintubes()
            has_pinboard = True
            return redirect(url_for('index'))
        else:
            return redirect(url_for('pinboard_login'))

    return render_template('pinboard_login.html', title='Sign In to Pinboard', form=form)

@app.route('/youtube', methods=['GET', 'POST'])
def youtube_login():
    print "Beginning Youtube Login Process"
    authSubUrl = pintube_object.GetAuthSubUrl()
    return redirect(authSubUrl)

@app.route('/')
@app.route('/index')
def index():
    global has_youtube
    global authsub_token

    if "token" in request.args:
        print "Got Back Token!"
        authsub_token = request.args.get("token")
        # authsub_token = str(authsub_token)
        # print "Current Page is %s" % request.url
        # temp_token = gdata.service.ExtractToken(request.url)
        # temp_token = temp_token[0]
        # temp_token = str(temp_token)
        # print "Extract Token returns %s" % temp_token
        print "Token is %s" % authsub_token
        pintube_object.SetAuthSubToken(authsub_token)
        pintube_object.UpgradeToSessionToken()
        # pintube_object.youtube_service.SetAuthSubToken(authsub_token)
        # pintube_object.youtube_service.UpgradeToSessionToken()
        # pintube_object.youtube_service.upgrade_to_session_token(authsub_token)
        has_youtube = True
        print "Successfully upgraded token!"

    if has_youtube and has_pinboard:
        providers = micawber.bootstrap_basic()

        """
        your_playlists = {}
        playlist_feed = get_user_playlist_feed()
        # url_pattern = r(http(s?)://www.youtube.com/watch+\Wv\W[a-zA-Z0-9-_]+)


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
        """
        user = pintube_object.user  # User.query.filter_by(username=pinboard_object_data["username"]).first_or_404()
        videos = user.info.pinboard_videos
        playlists = user.info.pinboard_playlists
        subscriptions = user.info.pinboard_subscriptions
        print "Testing User Here: %s" % user
        return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard, videos=videos, playlists=playlists, subscriptions=subscriptions)
    return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard)
