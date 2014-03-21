import os
import sys
import json
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
"""
from __init__ import app
from __init__ import db
from __init__ import login_manager
import models
"""
from forms import Pinboard_Login_Form
from models import User
from models import Info
from sqlalchemy.exc import IntegrityError

from jinja2 import Environment, FileSystemLoader
import flask_sijax
import sijax

sys.path.append(os.path.join('.', os.path.dirname(__file__), '../'))
app.config['SIJAX_STATIC_PATH'] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'

flask_sijax.Sijax(app)


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
    global pinboard_object_data

    if form.validate_on_submit():
        session['pin_remember_me'] = form.pin_remember_me.data
        p = pintube_object.get_pinboard(form.pin_user_id.data, form.pin_password.data)
        if p["Pass"]:
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

@flask_sijax.route(app, "/")
@flask_sijax.route(app, "/index")
def index():
    global has_youtube
    global authsub_token

    def copy_playlist(obj_response, original_playlist_url, new_playlist_name):
        print "Playlist URL is %s" % original_playlist_url
        print "Playlist Name is %s" % new_playlist_name
        pintube_object.copy_playlist_to(original_playlist_url, new_playlist_name)
        print "Copied Playlist"
        obj_response.alert('Copied Playlist')

    def add_video_to_playlists(obj_response, video_url, p_name, last_one):
        print "Video URL is %s" % video_url
        print "Playlist Name is %s" % p_name
        pintube_object.add_video_to_possible_playlists(video_url, playlist_name=p_name)
        print "Added Video to Playlist {0}".format(p_name)
        if last_one == "True":
            obj_response.alert('Added Video to Playlist(s)')

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('say_hi', say_hi)
        g.sijax.register_callback('copy_playlist', copy_playlist)
        g.sijax.register_callback('add_video', add_video_to_playlists)
        return g.sijax.process_request()

    if ("token" in request.args) and (not has_youtube):
        print "Got Back Token!"
        authsub_token = request.args.get("token")
        print "Token is %s" % authsub_token
        pintube_object.authsub_token = authsub_token
        pintube_object.SetAuthSubToken(authsub_token)
        pintube_object.UpgradeToSessionToken()
        has_youtube = True
        print "Successfully upgraded token!"
        if has_pinboard:
            pintube_object.get_pintubes()

    if has_youtube and has_pinboard:
        providers = micawber.bootstrap_basic()
        videos = pintube_object.db_videos
        playlists = pintube_object.db_playlists
        subscriptions = pintube_object.db_subscriptions
        youtube_data = pintube_object.youtube_data
        return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard, videos=videos, playlists=playlists, subscriptions=subscriptions, youtube_data=youtube_data)  # pintube_object=pintube_object, cp_form=cp_form, add_form=add_form)
    return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard)
