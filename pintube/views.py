import xml.etree.ElementTree as ET
import httplib2
import os
import sys
import re
import pinboard

from pintube import app
from rauth.service import OAuth1Service, OAuth1Session
from flask_oauth import OAuth
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


def get_pinboard(username, password):
    return pinboard.open(username, password)
    


"""

oauth = OAuth()


youtube = oauth.remote_app(
    base_url = ''
)


goodreads = oauth.remote_app('goodreads',
    base_url = 'http://www.goodreads.com/',
    request_token_url='http://www.goodreads.com/oauth/request_token',
    access_token_url='http://www.goodreads.com/oauth/access_token',
    authorize_url='http://www.goodreads.com/oauth/authorize',
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)



goodreads = OAuth1Service(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    name='goodreads',
    request_token_url='http://www.goodreads.com/oauth/request_token',
    authorize_url='http://www.goodreads.com/oauth/authorize',
    access_token_url='http://www.goodreads.com/oauth/access_token',
    base_url='http://www.goodreads.com/'
    )
    


@app.route('/oauth-authorized')
@goodreads.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['goodreads_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['goodreads_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(next_url)

"""

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