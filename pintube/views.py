"""Handles the display of different views in the application"""
import os
import sys
# import json
# import gdata
import micawber
from pintube.pinclass import Pintube
# from flask import Flask
# from flask import Markup
from flask import request
from flask import session
from flask import g
from flask import redirect
from flask import url_for
# from flask import abort
from flask import render_template
# from flask import flash
# from flask import session
# from flask import Response
# from flask import jsonify
# from flask.ext.login import login_user,
# logout_user, current_user, login_required

from pintube import app
# from pintube import db
# from pintube import models
# from pintube import login_manager
"""
from __init__ import app
from __init__ import db
from __init__ import login_manager
import models
"""
from pintube.forms import Pinboard_Login_Form
# from pintube.models import User
# from pintube.models import Info
# from sqlalchemy.exc import IntegrityError

# from jinja2 import Environment, FileSystemLoader
import flask_sijax
# import sijax

SIJAX_PATH = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
sys.path.append(os.path.join('.', os.path.dirname(__file__), '../'))
app.config['SIJAX_STATIC_PATH'] = SIJAX_PATH
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'

flask_sijax.Sijax(app)


HAS_YOUTUBE = False
HAS_PINBOARD = False
AUTHSUB_TOKEN = ''
PINTUBE_OBJECT = Pintube()

"""
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
"""


@app.route('/about')
def about():
    global HAS_YOUTUBE
    global HAS_PINBOARD
    return render_template('about.html', HAS_YOUTUBE=HAS_YOUTUBE,
                           HAS_PINBOARD=HAS_PINBOARD)


@app.route('/contact')
def contact():
    global HAS_YOUTUBE
    global HAS_PINBOARD
    return render_template('contact.html', HAS_YOUTUBE=HAS_YOUTUBE,
                           HAS_PINBOARD=HAS_PINBOARD)

@app.route('/logout')
def logout():
    global HAS_YOUTUBE
    global HAS_PINBOARD
    global AUTHSUB_TOKEN
    global PINTUBE_OBJECT

    HAS_YOUTUBE = False
    HAS_PINBOARD = False
    AUTHSUB_TOKEN = ''
    PINTUBE_OBJECT = Pintube()

    return render_template('index.html', HAS_YOUTUBE=HAS_YOUTUBE,
                           HAS_PINBOARD=HAS_PINBOARD)

@app.route('/pinboard', methods=['GET', 'POST'])
def pinboard_login():
    """
    View to Pinboard Login
    """
    global HAS_PINBOARD
    global HAS_YOUTUBE
    global PINTUBE_OBJECT
    form = Pinboard_Login_Form()

    # global pinboard_object_data

    if form.validate_on_submit():
        session['pin_remember_me'] = form.pin_remember_me.data
        user_id = form.pin_user_id.data
        password = form.pin_password.data
        pinboard_pass = PINTUBE_OBJECT.get_pinboard(user_id, password)
        if pinboard_pass["Pass"]:
            PINTUBE_OBJECT.get_pintubes()
            HAS_PINBOARD = True
            return redirect(url_for('index'))
        else:
            return redirect(url_for('pinboard_login'))

    return render_template('pinboard_login.html',
                           title='Sign In to Pinboard', form=form,
                           HAS_YOUTUBE=HAS_YOUTUBE,
                           HAS_PINBOARD=HAS_PINBOARD)

@app.route('/youtube', methods=['GET', 'POST'])
def youtube_login():
    """
    View to Youtube Login
    """
    print "Beginning Youtube Login Process"
    authsub_url = PINTUBE_OBJECT.GetAuthSubUrl()
    return redirect(authsub_url)

@flask_sijax.route(app, "/")
@flask_sijax.route(app, "/index")
def index():
    """
    Displays the index and main page of the application
    """
    global HAS_YOUTUBE
    global AUTHSUB_TOKEN

    def copy_playlist(obj_response, original_playlist_url, new_playlist_name):
        """Sijax function used to expose the
        copy_playlist functionality to the front end
        """
        print "Playlist URL is %s" % original_playlist_url
        print "Playlist Name is %s" % new_playlist_name
        PINTUBE_OBJECT.copy_playlist_to(original_playlist_url,
                                        new_playlist_name)
        print "Copied Playlist"
        obj_response.alert('Copied to new playlist with name '
                           + new_playlist_name)


    def add_video_to_playlists(obj_response, video_url, p_name, last_one):
        """Sijax function used to expose the
        add_video functionality to the front end
        """
        print "Video URL is %s" % video_url
        print "Playlist Name is %s" % p_name
        PINTUBE_OBJECT.add_video_to_possible_playlists(video_url,
                                                        playlist_name=p_name)
        print "Added Video to Playlist {0}".format(p_name)
        if last_one == "True":
            obj_response.alert('Added Video to Playlist(s)')

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('copy_playlist', copy_playlist)
        g.sijax.register_callback('add_video', add_video_to_playlists)
        return g.sijax.process_request()

    if ("token" in request.args) and (not HAS_YOUTUBE):
        print "Got Back Token!"
        AUTHSUB_TOKEN = request.args.get("token")
        print "Token is %s" % AUTHSUB_TOKEN
        PINTUBE_OBJECT.AUTHSUB_TOKEN = AUTHSUB_TOKEN
        PINTUBE_OBJECT.SetAuthSubToken(AUTHSUB_TOKEN)
        PINTUBE_OBJECT.UpgradeToSessionToken()
        HAS_YOUTUBE = True
        print "Successfully upgraded token!"
        if HAS_PINBOARD:
            PINTUBE_OBJECT.get_pintubes()

    if HAS_YOUTUBE and HAS_PINBOARD:
        providers = micawber.bootstrap_basic()
        videos = PINTUBE_OBJECT.db_videos
        playlists = PINTUBE_OBJECT.db_playlists
        subscriptions = PINTUBE_OBJECT.db_subscriptions
        youtube_data = PINTUBE_OBJECT.youtube_data
        return render_template('index.html', HAS_YOUTUBE=HAS_YOUTUBE,
                                HAS_PINBOARD=HAS_PINBOARD, videos=videos,
                                playlists=playlists,
                                subscriptions=subscriptions,
                                youtube_data=youtube_data)
    return render_template('index.html', HAS_YOUTUBE=HAS_YOUTUBE,
                           HAS_PINBOARD=HAS_PINBOARD)
