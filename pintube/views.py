import xml.etree.ElementTree as ET
import pinboard
import gdata.youtube
import gdata.youtube.service
import gdata.apps
import gdata.client
import gdata.gauth

# from pinboard import open
from functools import wraps
from basicauth import encode
import urllib2
import httplib2
import os
import sys
import re
#import forms
import cgi, cgitb


from pintube import app
from rauth.service import OAuth1Service, OAuth1Session
from flask_oauth import OAuth
# from flask.ext.rauth import RauthOAuth2
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


from forms import Youtube_Login_Form, Pinboard_Login_Form 
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run


# Initializing GData YouTubeService() used to generate the object so that we can communicate with the YouTube API
youtube_service = gdata.youtube.service.YouTubeService()
youtube_service.ssl = True

youtube_service.developer_key = 'AI39si5JGdicli8WGHhzGfW07rvFHMmlLJMtpB1zx3rpBhaBruxL4wkqGFPkQ0Dj2MDFObGCsR_wphhr3N9QpyTUOH9y_aeWsQ'

youtube_service.source = 'PinTube'
# youtube_service.client_id = '830901840095-ro3r226k4lkfpbgvliinc372hs9ma0p2.apps.googleusercontent.com'

# Keep in mind that providing a Client ID isn't necessary anymore for API requests



def GetAuthSubUrl():
    next = 'http://localhost:5000/'
    scope = 'http://gdata.youtube.com'
    secure = False
    session = True
    # youtube_service = gdata.youtube.service.YouTubeService()    
    return youtube_service.GenerateAuthSubURL(next, scope, secure, session)


"""
authSubUrl = GetAuthSubUrl()
print 'URL is: %s' % authSubUrl
parameters = cgi.FieldStorage()
#authsub_token = parameters['auth_sub_scopes' ]
authsub_token = parameters[[]'token']
youtube_service.SetAuthSubToken(authsub_token)
youtube_service.UpgradeToSessionToken()

"""
# CLIENT_ID = '830901840095-ro3r226k4lkfpbgvliinc372hs9ma0p2.apps.googleusercontent.com'


# CLIENT_SECRET = 'Qypg1VjBLlUS4JhLCFicG8fh'


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
                                   'client_secret.json'))



# An OAuth 2 access scope that allows for full read/write access.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


has_youtube = False
has_pinboard = False

def get_authenticated_service():
    """
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
    """
    
    SCOPE = 'https://gdata.youtube.com/feeds/api'
    
    flow = flow_from_clientsecrets('client_secret.json',
                               scope=SCOPE,
                               redirect_uri='http://localhost:5000/oauth2callback')
    
    #auth_uri = flow.step1_get_authorize_url()
    #storage = Storage('plus.dat')
    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()
    
    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)
    
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))
     
    # Munge the data in the credentials into a gdata OAuth2Token
    # This is based on information in this blog post:
    # https://groups.google.com/forum/m/#!msg/google-apps-developer-blog/1pGRCivuSUI/3EAIioKp0-wJ
     
    auth2token = gdata.gauth.OAuth2Token(client_id=credentials.client_id,
      client_secret=credentials.client_secret,
      scope=SCOPE,
      access_token=credentials.access_token,
      refresh_token=credentials.refresh_token,
      user_agent='PinTube')
    
    client = gdata.youtube.client.YouTubeClient(source='PinTube',
                                                auth_token=auth2token)
    
    auth2token.authorize(client)
    

def has_playlist(username):
    url = "http://gdata.youtube.com/feeds/api/users/"
    playlist_url = url + username + "/playlists"
    # retrieve Youtube playlist
    video_feed = youtube_service.GetYouTubePlaylistVideoFeed(playlist_url)
    print "\nPlaylists for " + str.format(playlist) + ":\n"
    # display each playlist to screen
    for p in video_feed.entry:
        if (p.title.text == "PinTube Playlist"):
            return True
        
    return False

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

def test_pinboard(user, passw):
    
    user = '' + user
    passw = '' + passw
    # p = pinboard(open(username=user, password=passw, token=None))
   
    
    try:
        # p = pinboard
        # p.open(username=user, password=passw, token=None)
        p = pinboard.open(username=user, password=passw)
        
        # p = open()
        # encoded_string = encode(user, passw)
        # p(username=user, password=passw)
        # p(encoded_string)
        # #p = pinboard(open(username=user, password=passw, token=None))
    except urllib2.HTTPError, error:
        print error
        return False
    
    return True 
    
video_pattern = '\bwatch\b'
playlist_pattern = '\bplaylist\b'
channel_pattern = '\buser\b'
pinboard_data = {}

def get_pintubes(username, password):
    videos = []
    playlists = []
    channels = []
    pintubes = {}
    p = pinboard.open(username, password)
    posts = p.posts(tag="youtube", count=400)
    for post in posts:
        url = post[u'href']
        if re.search(video_pattern, url):
            videos.append(url)
        elif re.search(playlist_pattern, url):
            playlists.append(url)
        elif re.search(channel_pattern, url):
            channels.append(url)
              
    return {"videos": videos, "playlists": playlists, "channels": channels}

def test_youtube(username, password):
    
    yt_service.email = 'jo@gmail.com'
    yt_service.password = 'mypassword'
    yt_service.ProgrammaticLogin()

@app.route('/oauth')
def oauth():
    if not has_playlist():
        insert_playlist()
        
"""  
@app.route('/oauth2callback/')
@app.route('/oauth2callback')
def oauth2callback():
    return get_authenticated_service()
    # return pintube.authorize(callback=url_for('oauth_authorized',
        # next=request.args.get('next') or request.referrer or None))
"""        
        
@app.route('/pinboard', methods=['GET', 'POST'])
def pinboard_login():
    form = Pinboard_Login_Form()
    print "Success 1"
    if form.validate_on_submit():
        session['pin_remember_me'] = form.pin_remember_me.data
        print "Success 2"
        if test_pinboard(form.pin_user_id.data, form.pin_password.data):
            pinboard_data = get_pintubes(form.pin_user_id.data, form.pin_password.data)
            print "Success 3"
            return redirect(url_for('index'))
        else:
            print "Failure 1"
            return redirect(url_for('pinboard'))
        # flash('Login requested for Pinboard with UserID="' + form.user_id.data + '", remember_me=' + str(form.remember_me.data))
        # return redirect('/index')
    return render_template('pinboard_login.html', title='Sign In to Pinboard', form=form)

@app.route('/youtube', methods=['GET', 'POST'])
def youtube_login():
    authSubUrl = GetAuthSubUrl()
    print 'URL is: %s' % authSubUrl
    return redirect(authSubUrl)
    '''
    form = Youtube_Login_Form()
    print "YT 1"
    if form.validate_on_submit():
        session['yt_remember_me'] = form.yt_remember_me.data
        print "YT 2"
        
        print "YT Success | Mission Accomplished!"
        
        
        if test_pinboard(form.yt_user_id.data, form.yt_password.data):
        pinboard_data = get_pintubes(form.yt_user_id.data, form.yt_password.data)
        print "YT 3"
        
        if request.method == 'GET':
            token = request.args.get('token')
            print token 
        
        return redirect(url_for('index'))
        
    else:
        print "Fail YT 1"
        return redirect(url_for('index'))
        # flash('Login requested for Pinboard with UserID="' + form.user_id.data + '", remember_me=' + str(form.remember_me.data))
        # return redirect('/index')
    '''
    #return render_template('youtube_login.html', title='Sign In', form=form)

@app.route('/')
@app.route('/index')
def index():
    parameters = cgi.FieldStorage()
    authsub_token = parameters.getvalue('token')#["token"]
    print "Token is: %s"%(authsub_token)
    print "Token 123"
    """
    if "token" not in parameters:
        print "Token not here"
    else:
        authsub_token = parameters["token"]
        print "Token is: %s"%(authsub_token)
    """
    return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard)
