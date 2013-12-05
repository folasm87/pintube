import xml.etree.ElementTree as ET
#import pinboard
from pinboard import open
from functools import wraps
from basicauth import encode
import urllib2
import httplib2
import os
import sys
import re



from pintube import app
from rauth.service import OAuth1Service, OAuth1Session
from flask_oauth import OAuth
#from flask.ext.rauth import RauthOAuth2
from flask import Flask
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


from forms import LoginForm
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

#CLIENT_ID = '830901840095-ro3r226k4lkfpbgvliinc372hs9ma0p2.apps.googleusercontent.com'


#CLIENT_SECRET = 'Qypg1VjBLlUS4JhLCFicG8fh'

CLIENT_SECRETS_FILE = "client_secret_830901840095-ro3r226k4lkfpbgvliinc372hs9ma0p2.apps.googleusercontent.com.json"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console
https://code.google.com/apis/console#access

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))



# An OAuth 2 access scope that allows for full read/write access.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


has_youtube = False
has_pinboard = False

def get_authenticated_service(is_authenticated=False):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    message=MISSING_CLIENT_SECRETS_MESSAGE,
    scope=YOUTUBE_READ_WRITE_SCOPE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
       credentials = run(flow, storage)

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))
    
    is_authenticated = True


def has_playlist():
    pass

def insert_playlist():
    playlists_insert_response = youtube.playlists().insert(
        part="snippet,status",
        body=dict(
          snippet=dict(
            title="PinTube Playlist",
            description="A private playlist created from the saved videos from your Pinboard account."
          ),
          status=dict(
            privacyStatus="private"
          )
        )
    ).execute()

    print "New playlist id: %s" % playlists_insert_response["id"]

video_pattern = '\bwatch\b'
playlist_pattern = '\bplaylist\b'
channel_pattern = '\buser\b'

pinboard_data = {}

def test_pinboard(user, passw):
    
    user = '' + user
    passw = '' + passw
    #p = pinboard(open(username=user, password=passw, token=None))
   
    
    try:
        #p = pinboard
        #p.open(username=user, password=passw, token=None)
        p = open()
        encoded_string = encode(user, passw)
        #p(username=user, password=passw)
        p(encoded_string)
        #p = pinboard(open(username=user, password=passw, token=None))
    except urllib2.HTTPError, error:
        print error
        return False
    
    return True 
    

def get_pintubes(username, password):
    videos = []
    playlists = []
    channels = []
    pintubes = {}
    p = pinboard.open(username, password)
    posts = p.posts(tag="youtube", count = 400)
    for post in posts:
        url = post[u'href']
        if re.search(video_patten, url):
            videos.append(url)
        elif re.search(playlist_pattern, url):
            playlists.append(url)
        elif re.search(channel_pattern, url):
            channels.append(url)
              
    return {"videos": videos, "playlists": playlists, "channels": channels}


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard)

@app.route('/oauth')
def oauth():
    if not has_playlist():
        insert_playlist()
        
    
@app.route('/oauth2callback/')
@app.route('/oauth2callback')
def oauth2callback():
    return get_authenticated_service(has_youtube)
    #return pintube.authorize(callback=url_for('oauth_authorized',
        #next=request.args.get('next') or request.referrer or None))
        
@app.route('/pinboard', methods = ['GET', 'POST'])
def pinboard():
    form = LoginForm()
    print "Success 1"
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        print "Success 2"
        if test_pinboard(form.user_id.data, form.password.data):
            pinboard_data = get_pintubes(form.user_id.data, form.password.data)
            print "Success 3"
            return redirect(url_for('index'))
        else:
            print "Failure 1"
            return redirect(url_for('pinboard'))
        #flash('Login requested for Pinboard with UserID="' + form.user_id.data + '", remember_me=' + str(form.remember_me.data))
        #return redirect('/index')
    return render_template('pinboard.html', title = 'Sign In', form = form)