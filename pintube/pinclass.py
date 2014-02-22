import os
import re
import sys
import gzip
import urllib
import urllib2
import httplib2
import StringIO
from xml.dom import minidom

import pinboard

import gdata
import gdata.youtube.service
from gdata.service import RequestError
from gdata import youtube
from gdata import apps
from gdata import client
from gdata import gauth


from flask import Markup
from pintube import db
from pintube import models
from models import User
from models import Info
from sqlalchemy.exc import IntegrityError


class Pintube(object):

    pinboard_data = {}
    pinboard_object_data = {}
    # youtube_service = None
    user = None


    def __init__(self):  # , username):
        # Initializing GData YouTubeService object so that we can communicate with the YouTube API
        self.youtube_service = gdata.youtube.service.YouTubeService()
        self.youtube_service.ssl = True
        self.youtube_service.developer_key = 'AI39si5JGdicli8WGHhzGfW07rvFHMmlLJMtpB1zx3rpBhaBruxL4wkqGFPkQ0Dj2MDFObGCsR_wphhr3N9QpyTUOH9y_aeWsQ'
        self.youtube_service.source = 'PinTube'
        # self.user = User.query.filter(User.username == username).first()

    # ##@classmethod
    def GetAuthSubUrl(self):
        next = 'http://localhost:5000/'
        scope = 'http://gdata.youtube.com'
        secure = False
        session = True
        return self.youtube_service.GenerateAuthSubURL(next, scope, secure, session)


    def SetAuthSubToken(self, token):
        return self.youtube_service.SetAuthSubToken(token=token)

    def UpgradeToSessionToken(self, token=None):
        print "Current token is %s" % self.youtube_service.current_token
        # return self.youtube_service.upgrade_to_session_token(self.youtube_service.GetAuthSubToken())
        return self.youtube_service.UpgradeToSessionToken()

    vid_id_pattern = r"""youtu(?:\.be|be\.com)/(?:.*v(?:/|=)|(?:.*/)?)([a-zA-Z0-9-_]+)"""
    def get_video_id(self, vid_url):
        print "Video URL is %s" % vid_url
        return re.search(self.vid_id_pattern, vid_url).group(1)

    playlist_id_pattern = r"""([a-zA-Z0-9_\-]{11,100})"""  # r"""([a-zA-Z0-9_\-]{18})"""
    def get_playlist_id(self, playlist_url=None, playlist_entry=None):
        id = ''
        if playlist_url:
            print "Playlist URL is %s" % playlist_url
            id = re.search(self.playlist_id_pattern, playlist_url).group(0)
            print "Playlist URL %s has an id : %s" % (playlist_url, id)

        else:
            id = playlist_entry.id.text.split('/')[-1]
            print "Playlist ID for the given Playlist Entry is %s" % id
        return id  # re.search(playlist_id_pattern, playlist_url).group(0)

    def get_subscription_id(self, sub_url):
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


    def get_video_name(self, video_entry):
        return video_entry.media.title.text

    # #@classmethod
    def get_playlist_name(self, playlist_id=None, playlist_entry=None):
        if (playlist_id):
            uri = 'https://gdata.youtube.com/feeds/api/playlists/' + playlist_id
            print "Playlist URI: %s" % uri
            return self.youtube_service.GetYouTubePlaylistFeed(uri).title.text
        elif(playlist_entry):
            return playlist_entry.title.text
        return None

    # #@classmethod
    def get_subscription_name(self, sub_id=None, sub_entry=None):
        if (sub_id):
            uri = "https://gdata.youtube.com/feeds/api/users/" + sub_id
            title = self.youtube_service.GetYouTubeSubscriptionEntry(uri).title.text
            print "Subscription URI is %s" % uri
            print "Subscription Title is %s" % title
            return title
        elif(sub_entry):
            title = sub_entry.title.text
            print "Subscription Title is %s" % title
            return title
        return None

    # @classmethod
    def get_video_entry(self, video_entry=None, vid_id=None):
        if vid_id:
            return self.youtube_service.GetYouTubeVideoEntry(video_id=vid_id)
        elif video_entry:
            vid_id = video_entry.id.text
            return self.youtube_service.GetYouTubeVideoEntry(video_id=vid_id)
        return None

    # @classmethod
    def get_playlist_entry(self, playlist_entry=None, playlist_id=None):
        """
        if playlist_id:
            print "Playlist ID is %s" % playlist_id
            # playlist_id = playlist_id.replace('PL', '')
            uri = "https://gdata.youtube.com/feeds/api/playlists/{0}".format(playlist_id)
            result = service.GetYouTubePlaylistEntry(uri)
            return result
        """

        if playlist_entry:
            plist_id = get_playlist_id(playlist_entry=playlist_entry)
            plist_uri = "https://gdata.youtube.com/feeds/api/playlists/" + plist_id
            return self.youtube_service.GetYouTubePlaylistEntry(plist_uri)

        return None

    # @classmethod
    def get_subscription_entry(self, sub_entry=None, sub_id=None):
        if sub_id:
            return self.youtube_service.GetYouTubeSubscriptionEntry(sub_id)
        elif sub_entry:
            s_id = sub_entry.id.text
            return self.youtube_service.GetYouTubeSubscriptionEntry(s_id)

        return None

    # @classmethod
    def get_user_playlist_feed(self):
        return self.youtube_service.GetYouTubePlaylistFeed(username='default')

    # @classmethod
    def get_playlist_video_feed(self, playlist_id):
        return self.youtube_service.GetYouTubePlaylistVideoFeed(playlist_id=playlist_id)

    # @classmethod
    def get_subscription_feed(self):
        return self.youtube_service.GetYouTubeSubscriptionFeed(username='default')

    def get_video_pic(self, video_id):
        return """<img src="http://img.youtube.com/vi/{0}/hqdefault.jpg"></img>""".format(video_id)

    # @classmethod
    def add_video_to_playlist(self, video_id, playlist_id, position):
        url = 'https://gdata.youtube.com/feeds/api/playlists/%s?v=2' % playlist_id

        headers = {'Content-Type' : 'application/atom+xml',
                   'Authorization' : 'Bearer %s' % authsub_token,
                   'GData-Version' : '2',
                   'X-GData-Key' : '%s' % self.youtube_service.developer_key}

        xml = """<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://gdata.youtube.com/schemas/2007"><id>{0}</id><yt:position>{1}</yt:position></entry>""".format(video_id, position)

        params = {'key': self.youtube_service.developer_key}

        return self.youtube_service.Post(xml, url, headers, url_params=params)

    # #@classmethod
    def create_playlist(self, playlist_title, playlist_desc):
        return self.youtube_service.AddPlaylist(playlist_title, playlist_desc)

    def is_vid_in_playlist(video_id, playlist_id):
        pass

    def does_playlist_exist(playlist_id):
        pass

    def get_embed_playlist(self, playlist_id):
        to_embed = Markup("""<iframe id="ytplayer" type="text/html" width="640" height="360"
                                src="https://www.youtube.com/embed/?listType=playlist&list={0}&theme=light"
                                frameborder="0" allowfullscreen></iframe>""".format(playlist_id))
        return to_embed


    def get_embed_subscription(self, sub_id):
        to_embed = Markup("""<div class="g-ytsubscribe" data-channel="{0}" data-layout="full" data-count="default"></div>""".format(sub_id))
        return to_embed


    # Code from Python-Pinboard. Used to directly get to last_updated information
    USER_AGENT = "Python-Pinboard/1.0 +http://morgancraft.com/service_layer/python-pinboard/"
    def get_last_update(self, username, password):
        # global USER_AGENT

        url = "https://api.pinboard.in/v1/posts/update"
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password("API", "https://api.pinboard.in/", username, password)
        opener = urllib2.build_opener(auth_handler)
        opener.addheaders = [("User-agent", self.USER_AGENT), ('Accept-encoding', 'gzip')]
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

    def get_pinboard(self, usern, passw):
        usern = '' + usern
        passw = '' + passw

        try:
            p = pinboard.open(username=usern, password=passw)
            print "Get Pinboard returns " + str(p)
        except urllib2.HTTPError, error:
            print error
            return {"Pass": False}

        self.pinboard_object_data = {"Pass": True, "pinboard_object": p, "username": usern, "password": passw}
        return self.pinboard_object_data  # {"Pass": True, "pinboard_object": p, "username": usern, "password": passw}

    video_pattern = '(watch+\Wv\W)'
    playlist_pattern = '(playlist+\Wlist=)'
    channel_pattern = '(user/)'

    # #@classmethod
    def get_pintubes(self):
        pinboard_object = self.pinboard_object_data
        last_update = self.get_last_update(pinboard_object["username"], pinboard_object["password"])
        # videos = []
        # playlists = []
        # channels = []
        # tags_for_vids = {}
        # pintubes = {}
        db_videos = {}
        db_playlists = {}
        db_subscriptions = {}
        # check_update = User.query.filter(User.last_updated == last_update).first()
        # self.user = User.query.filter(User.username == pinboard_object["username"]).first()

        if (self.user is None):
            posts = pinboard_object["pinboard_object"].posts(tag="youtube", count=1000)

            for post in posts:
                url = post[u'href']
                tags = post[u'tags']
                if re.search(self.video_pattern, url):
                    video_id = self.get_video_id(url)
                    print "Video ID is %s" % video_id
                    try:
                        video_entry = self.get_video_entry(vid_id=video_id)

                    except RequestError, error:
                        print error
                        print "Video Error!"
                        continue

                    video_name = self.get_video_name(video_entry)
                    print "Video Name is %s" % video_name
                    if url is None:
                        print "Video URL is NONE"

                    temp_tags = []
                    for tag in tags:
                        tag = str(tag)
                        temp_tags.append(tag)

                    video_details = {"url":url, "tags":temp_tags}

                    db_videos.setdefault(video_name, video_details)
                    # videos.append(url)
                    """
                    for tag in tags:
                        tag = str(tag)
                        if tag in tags_for_vids:
                            tags_for_vids[tag].append(url)
                        elif tag != "youtube":
                            tags_for_vids.setdefault(tag, [url])
                    """

                elif re.search(self.playlist_pattern, url):
                    playlist_id = self.get_playlist_id(playlist_url=url)
                    print "Playlist ID: %s" % playlist_id

                    try:
                        playlist_name = self.get_playlist_name(playlist_id)
                    except RequestError, error:
                        print error
                        print "Playlist Error!"
                        continue
                    playlist_details = {"url":url, "embed":self.get_embed_playlist(playlist_id)}
                    db_playlists.setdefault(playlist_name, playlist_details)
                    # playlists.append(url)
                elif re.search(self.channel_pattern, url):
                    subscription_id = self.get_subscription_id(url)
                    try:
                        subscription_name = self.get_subscription_name(sub_id=subscription_id)
                    except RequestError, error:
                        print error
                        print "Subscription Error!"
                        continue
                    subscription_details = {"url":url, "embed":self.get_embed_subscription(subscription_id)}
                    db_subscriptions.setdefault(subscription_name, subscription_details)
                    # channels.append(url)



            info = Info(pinboard_videos=db_videos, pinboard_playlists=db_playlists, pinboard_subscriptions=db_subscriptions)
            self.user = User(username=pinboard_object["username"], last_updated=last_update, info=info)

            try:
                db.session.add(self.user)
                db.session.commit()
            except IntegrityError, error:
                print error
                print "You've already added a row with the same user_name before"

            # return user.info


        else:
            check_update = str(self.user.last_updated)
            print "Current User was lasted updated at %s while official time of last update is %s" % (str(check_update), last_update)

            if ((check_update is None) or (str(check_update.last_updated) != last_update)):

                # user = User.query.filter_by(username=pinboard_object["username"]).first()
                self.user.last_updated = last_update
                # user.info = info

                try:
                    db.session.add(self.user)
                    db.session.commit()
                except IntegrityError, error:
                    print error
                    print "You've already added a row with the same user_name before"

                # return {"videos": db_videos, "playlists": db_playlists, "channels": db_subscriptions}


        return self.user.info  # {"videos": videos, "playlists": playlists, "channels": channels}  # , "vid_tags": tags_for_vids}
