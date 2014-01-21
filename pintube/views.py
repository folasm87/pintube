import xml.etree.ElementTree as ET

import pinboard

import gdata
from gdata import youtube
import gdata.youtube.service
from gdata import apps
from gdata import client
from gdata import gauth

# from pinboard import open
from functools import wraps
from basicauth import encode
import urllib
import urllib2
import httplib2
import requests
import os
import sys
import re
import cPickle as pickle
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






#global has_youtube
#global has_pinboard

has_youtube= False
has_pinboard = False
authsub_token = ''
"""

# An OAuth 2 access scope that allows for full read/write access.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service():
    
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
"""

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
    p = pinboard.open(username, password)
    #print p 
    posts = p.posts(tag="youtube", count=1000)
    #print posts
    for post in posts:
        url = post[u'href']
        tags = post[u'tags']
        if re.search(video_pattern, url):
            videos.append(url)
            for tag in tags:
                tag = str(tag)
                if tag in tags_for_vids:
                    tags_for_vids[tag].append(url)
                elif tag != "youtube":
                    tags_for_vids.setdefault(tag, [url])
        elif re.search(playlist_pattern, url):
            playlists.append(url)
        elif re.search(channel_pattern, url):
            channels.append(url)
    
    print 'Videos :- [%s]' % ', '.join(map(str, videos))
    print 'Channels :- [%s]' % ', '.join(map(str, channels))
    print 'Playlists :- [%s]' % ', '.join(map(str, playlists))
    print '-*' * 50
    
    for vid_tag in tags_for_vids:
        print "%s :-> [%s]" % (vid_tag, ', '.join(map(str, tags_for_vids[vid_tag])))
        
    

    print "Get_Pintube has run again"
    return {"videos": videos, "playlists": playlists, "channels": channels, "vid_tags": tags_for_vids}


@app.route('/oauth')
def oauth():
    if not has_playlist():
        insert_playlist()
           
        
@app.route('/pinboard', methods=['GET', 'POST'])
def pinboard_login():
    form = Pinboard_Login_Form()
    global has_pinboard
    global pinboard_data
    print "Success 1"
    if form.validate_on_submit():
        session['pin_remember_me'] = form.pin_remember_me.data
        print "Success 2"
        if test_pinboard(form.pin_user_id.data, form.pin_password.data):
            pinboard_data = get_pintubes(form.pin_user_id.data, form.pin_password.data)
            print "Success 3"
            has_pinboard = True
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

@app.route('/')
@app.route('/index')
def index():
    #parameters = cgi.FieldStorage()
    #authsub_token = parameters.getvalue('token')#["token"]
    #print "Token is: %s"%(authsub_token)
    global has_youtube
    global authsub_token
    if "token" in request.args:
        authsub_token = request.args.get("token")
        print "Token is: %s"%(authsub_token)
        youtube_service.SetAuthSubToken(authsub_token)
        youtube_service.UpgradeToSessionToken()
        print "Youtube Session Authorized"
        has_youtube = True
        
        print "has_youtube is %s and has_pinboard is %s" % (has_youtube, has_pinboard)
    
    if has_youtube and has_pinboard:
        your_playlists = {} 
        playlist_feed = youtube_service.GetYouTubePlaylistFeed(username='default')
        
        
        fo = open('playlist_feed.p', 'wb')
        pickle.dump(playlist_feed, fo)
        fo.close()
        
        #Copies the playlist Names, URIs and Videos to a dictionary
        print "Beginning Playlist process"
        for playlist_entry in playlist_feed.entry:
           
            playlist_entry_title = playlist_entry.title.text
            playlist_entry_uri = playlist_entry.id.text.split('/')[-1]
            #playlist_content = playlist_entry.content
            playlist_id = playlist_entry.id.text
            playlist_entry_id = playlist_entry.id.text.split('/')[-1]
            playlist_entry_video_feed = youtube_service.GetYouTubePlaylistVideoFeed(playlist_id=playlist_entry_id)
            """
            
            requestURL = "https://gdata.youtube.com/feeds/api/users/default/playlists?v=2&token=%s" % authsub_token
            root = ET.parse(urllib.urlopen(requestURL)).getroot()
            print "=" * 100
            print "This is the XML"
            print root
            print '\n'
            print "=" * 100
            
            
            tree = ET.parse('playlist_content')
            root = tree.getroot()
            print root[2][0].text
            print root[2][1].text
            """
            
            #if playlist_entry_title not in pinboard_data["playlists"]:
            print "Part 1"
            #print "Playlist Content: %s" % playlist_content
            print "Playlist Entry Id : %s" % playlist_entry_id
            #print "%s: %s" % (playlist_entry_title, playlist_entry_uri)
            #print "playlist_entry_video_feed: %s" % playlist_entry_video_feed
            your_playlists.setdefault(playlist_entry_title, [playlist_entry_id, []])
            
            for playlist_video_entry in playlist_entry_video_feed.entry:
                print "Part 2"
                video_title = playlist_video_entry.title.text
                #your_playlists[playlist_entry_title].append(playlist_video_entry.title.text)
                your_playlists[playlist_entry_title][1].append(playlist_video_entry.title.text)
                
            #if playlist_entry.title.text in pinboard_data['playlists']:
        
        #Checks to see if videos are in playlists that correspond to their tags on Pinboard
        print "Pinboard_Data is %s" % pinboard_data
        print "Pinboard_Data Vid_Tags are %s" % pinboard_data["vid_tags"]
        for tag in pinboard_data["vid_tags"].keys():
        #for tag in pinboard_data["vid_tags"]["tags_for_vids"].keys():
            print "Part 3"
            #Adding playlist according to tag if not already present
            if tag not in your_playlists:
                print "Part 4"
                new_public_playlistentry = youtube_service.AddPlaylist(tag, 'A Pintube Playlist')
                
                if isinstance(new_public_playlistentry, gdata.youtube.YouTubePlaylistEntry):
                  print 'New playlist %s added!' % tag
            #If playlist already present check to see if you should update
            else:
                
                print "Your already have a playlist named %s" % tag
                for vid in pinboard_data["vid_tags"][tag]:
                    """
                    A video is missing from an already created playlist
                    
                    In order to 
                    
                    https://stackoverflow.com/questions/3652046/c-sharp-regex-to-get-video-id-from-youtube-and-vimeo-by-url
                    
                    https://developers.google.com/youtube/1.0/developers_guide_python#AddVideoToPlaylist
                    """
                    vid = str(vid)
                    if vid not in your_playlists[tag][1]:
                        print "Part 5"
                        vid_id_pattern = r"""youtu(?:\.be|be\.com)/(?:.*v(?:/|=)|(?:.*/)?)([a-zA-Z0-9-_]+)"""
                        vid_id = re.search(vid_id_pattern, vid).group(1)
                        entry = youtube_service.GetYouTubeVideoEntry(video_id=vid_id)
                        
                        playlist_id = your_playlists[tag][0].replace('PL', '')
                        
                        
                        print "Video: %s is not in Playlist %s" % (vid, your_playlists[tag])
                        print "Playlist id is %s, Video id is %s" % (playlist_id, vid_id)
                        
                        url = 'https://gdata.youtube.com/feeds/api/playlists/%s?v=2' % playlist_id
                        
                        print "URL is %s" % url
                        
                        headers = {'Content-Type' : 'application/atom+xml',
                                   'Authorization' : 'Bearer %s' % authsub_token,
                                   'GData-Version' : '2',
                                   'X-GData-Key' : '%s' % youtube_service.developer_key}
                        
                        xml = """<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://gdata.youtube.com/schemas/2007"><id>%s</id><yt:position>1</yt:position></entry>""" % (vid_id)
                        
                        params = {'key': youtube_service.developer_key}
                        
                        print "XML is %s" % xml
                        
                        post = youtube_service.Post(xml, url, headers, url_params=params)
                        
                        #data = urllib.urlencode(values)
                        #req = urllib2.Request(url, data)
                        #response = urllib2.urlopen(req)
                        #the_page = response.read()
                        
                        #playlist_video_entry = youtube_service.AddPlaylistVideoEntryToPlaylist(
                           # playlist_uri, vid_id)
                        
                        r = requests.post(url, data=xml, headers=headers)
                        
                        r
                        
                        #if isinstance(playlist_video_entry, gdata.youtube.YouTubePlaylistVideoEntry):
                            #print 'Video: %s added to Playlist: %s ' % (entry.title.text, tag)
                
            
    
    
    
            
        
    
    """
    if "token" not in parameters:
        print "Token not here"
    else:
        authsub_token = parameters["token"]
        print "Token is: %s"%(authsub_token)
    """
    return render_template('index.html', has_youtube=has_youtube, has_pinboard=has_pinboard)
