import os
import re
import sys
import gzip
import urllib
import urllib2
import httplib2
import StringIO
import pprint
from xml.dom import minidom

import pinboard

import atom
import gdata
import gdata.media as Media
import gdata.youtube.service
from gdata.service import RequestError
from gdata import youtube
from gdata import apps
from gdata import client
from gdata import gauth


from flask import Markup
from flask.ext.restless import APIManager

from pintube import db
from pintube import app
from pintube import models
"""
from __init__ import db
from __init__ import app
import models
"""
from models import User
from models import Info
from sqlalchemy.exc import IntegrityError


reload(sys)
sys.setdefaultencoding('utf-8')


db.create_all()
api_manager = APIManager(app, flask_sqlalchemy_db=db)
api_manager.create_api(User, methods=['GET', 'POST', 'DELETE', 'PUT'])
api_manager.create_api(Info, methods=['GET', 'POST', 'DELETE', 'PUT'])


class Pintube(object):

    pinboard_data = {}
    pinboard_object_data = {}
    youtube_service = None
    user = None
    youtube_data = {}
    authsub_token = ''
    db_videos = {}
    db_playlists = {}
    db_subscriptions = {}
    user_playlist_feed = None


    def __init__(self):
        # Initializing GData YouTubeService object so that we can communicate with the YouTube API
        self.youtube_service = gdata.youtube.service.YouTubeService()
        self.youtube_service.ssl = True
        self.youtube_service.developer_key = 'AI39si5JGdicli8WGHhzGfW07rvFHMmlLJMtpB1zx3rpBhaBruxL4wkqGFPkQ0Dj2MDFObGCsR_wphhr3N9QpyTUOH9y_aeWsQ'
        self.youtube_service.source = 'PinTube'
        # self.youtube_data = self.get_youtube_data()
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

    video_url_pattern = r"""(http(s?)://www.youtube.com/watch+\Wv\W[a-zA-Z0-9-_]+)"""
    def get_youtube_data(self):
        print "Starting GetYoutubeData Function"

        pinboard_object = self.pinboard_object_data

        current_user = User.query.filter(User.username == pinboard_object["username"]).first()

        # if (current_user is None):
        if ((current_user is None) or (current_user.info is None) or (current_user.info.youtube_playlists is None)):
            print "Youtube Playlists doesn't exist within the current user's info"

            playlists = {}
            p_feed = None
            # last_update = self.get_last_update(pinboard_object["username"], pinboard_object["password"])
            if (self.user_playlist_feed is not None):
                p_feed = self.user_playlist_feed
            else:
                self.user_playlist_feed = self.get_user_playlist_feed()
                p_feed = self.user_playlist_feed
            """
            # youtube_playlists = {}
            #if (self.user is not None):
                # check_update = str(self.user.last_updated)
                # youtube_playlists = self.user.info.youtube_playlists
        
        
               print "GetYoutubeData: Current User was lasted updated at %s while official time of last update is %s" % (check_update, last_update)
        
                if ((check_update != last_update) or (youtube_playlists is None)):
        
                    if (youtube_playlists is None):
                        print "self.user.info.youtube_playlists is None"
                    elif (check_update != last_update):
                        print "self.user.last_updated does not match self.get_last_update()"
        """

            for p_entry in p_feed.entry:
                p_id = p_entry.id.text.split('/')[-1]
                p_title = p_entry.title.text
                v_feed = self.get_playlist_video_feed(p_id)
                videos = {}
                number_of_vids = {}
                i = 0
                print ""
                print "_"*30
                print "Your Youtube Account has a playlist [%s] with id [%s] ->" % (p_title, p_id)


                for v_entry in v_feed.entry:
                    v_title = v_entry.title.text
                    v_uri = v_entry.id.text  # .split('/')[-1]
                    # print "Video Title = [%s],  URI = [%s]" % (v_title, v_uri)
                    try:
                        video_entry = self.get_video_entry(video_uri=v_uri)
                    except RequestError, error:
                            print error
                            print "Video Entry Error!"
                            continue

                    # video_entry = self.youtube_service.GetYouTubeVideoEntry(v_uri)
                    i += 1
                    video_data = {}

                    if (video_entry.media.player is not None):
                        media_url = video_entry.media.player.url
                        # print "Media URL is %s" % media_url
                        media_url = re.search(self.video_url_pattern, media_url).group(0)
                        video_data = {"video_url": media_url, "video_uri": v_uri}
                    else:
                        video_data = {"video_url": None, "video_uri": v_uri}

                    videos.setdefault(v_title, video_data)

                    # print "It has a video [%s] at url [%s] with uri [%s]" % (v_title, video_data["video_url"], video_data["video_uri"])

                print "Playlist [%s] has [%s] videos" % (p_title, i)
                print ""
                print "_"*30
                    # number_of_vids = {"number":i}
                playlist = {"number_of_vids": i, "videos": videos}
                playlists.setdefault(p_title, playlist)

                # print "Playlist [%s] has [%s] videos" % (p_title, i)
            print ""
            print "_"*30
            print "Your have {0} Playlists in your Youtube Account".format(len(playlists))
            self.youtube_data = playlists
            # print "In GetYoutubeData() 'playlists' :=> "
            # pprint.pprint(playlists)
            # current_user.info.youtube_playlists = playlists
            # db.session.commit()
            return playlists

        return current_user.info.youtube_playlists

        """
        # else:
        print "self.user.info.youtube_playlists is present and last_update matches"
        self.youtube_data = self.user.info.youtube_playlists
        print "In GetYoutubeData() 'youtube_playlists' :=> "
        pprint.pprint(youtube_playlists)

        print "Your have {0} Playlists in your Youtube Account".format(len(self.user.info.youtube_playlists))
        print "GetYoutubeData() 'youtube_playlists' returned"
        return self.user.info.youtube_playlists

       
        print "Your have {0} Playlists in your Youtube Account".format(len(playlists))
        self.youtube_data = playlists
                print "In GetYoutubeData() 'playlists' :=> "
                # pprint.pprint(playlists)
                current_user.info.youtube_playlists = playlists
                db.session.commit()
        print "GetYoutubeData() 'playlists' returned"
        return self.user.info.youtube_playlists  # youtube_playlists
        """


    def add_video_to_possible_playlists(self, video_url, playlist_name):
        vid_id = self.get_video_id(video_url)
        user_playlist_feed = None
        if (self.user_playlist_feed is None):
            self.user_playlist_feed = self.get_user_playlist_feed()
            # user_playlist_feed = self.get_user_playlist_feed()
        p_exist = self.does_playlist_exist(user_playlist_feed=self.user_playlist_feed, playlist_name=playlist_name)  # user_playlist_name)
        if (p_exist["exist"]):
            try:
                self.add_video_to_playlist(vid_id, p_exist["id"], 1)
            except RequestError, error:
                print error
                print "Adding Video to the Already Existing Playlist Did Not Work"
        else:
            new_playlist = self.create_playlist(playlist_title=playlist_name, playlist_desc="A Pintube Playlist")
            new_playlist_id = self.get_playlist_id(playlist_entry=new_playlist)
            new_playlist_uri = "https://gdata.youtube.com/feeds/api/playlists/" + new_playlist_id
            # new_playlist_entry = self.get_playlist_entry(playlist_entry=new_playlist_uri)
            # new_playlist_id = self.get_playlist_id(playlist_entry=new_playlist_entry)

            try:
                self.add_vid_to_playlist(video_id=vid_id, playlist_uri=new_playlist_uri)
                # self.add_video_to_playlist(vid_id, new_playlist_id, 1)
            except RequestError, error:
                print error
                print "Adding Video to A New Playlist Did Not Work"





    def copy_playlist_to(self, original_playlist_url, new_playlist_name):
        new_playlist = self.create_playlist(new_playlist_name, "A PinTube Playlist")
        new_playlist_id = self.get_playlist_id(playlist_entry=new_playlist)
        new_playlist_user_uri = new_playlist.id.text
        new_playlist_uri = "https://gdata.youtube.com/feeds/api/playlists/" + new_playlist_id
        original_playlist_id = self.get_playlist_id(playlist_url=original_playlist_url)
        original_playlist_video_feed = self.get_playlist_video_feed(original_playlist_id)

        for video_entry in original_playlist_video_feed.entry:
            vid_entry = self.get_video_entry(video_uri=video_entry.id.text)
            vid_id = vid_entry.id.text  # .split('/')[-1]

            video_entry = self.youtube_service.GetYouTubeVideoEntry(vid_id)  # youtube_service.GetYouTubeVideoEntry(video_id)
            video_url = ""
            if video_entry.media.player is not None:
                video_url = video_entry.media.player.url
                video_url = re.search(self.video_url_pattern, video_url).group(0)  # re.search(url_pattern, media_url).group(0)

            video_id = self.get_video_id(video_url)
            print "CP Video Entry ID is %s" % vid_id
            print "CP New Playlist ID is %s" % new_playlist_id


            try:
                self.add_vid_to_playlist(video_id=video_id, playlist_uri=new_playlist_uri)
                # add_video = self.add_video_to_playlist(vid_id, new_playlist_id, 1)  # new_playlist_id, 1)
            except RequestError, error:
                    print error
                    print "CP Adding Video To Playlist Error!"
                    continue








    """
    def add_video_to_playlist(self, video_id, playlist_uri):
        return self.youtube_service.AddPlaylistVideoEntryToPlaylist(playlist_uri=playlist_uri, video_id=video_id)
    """






    vid_id_pattern = r"""youtu(?:\.be|be\.com)/(?:.*v(?:/|=)|(?:.*/)?)([a-zA-Z0-9-_]+)"""
    def get_video_id(self, vid_url):
        # print "Video URL is %s" % vid_url
        return re.search(self.vid_id_pattern, vid_url).group(1)

    playlist_id_pattern = r"""([a-zA-Z0-9_\-]{11,100})"""  # r"""([a-zA-Z0-9_\-]{18})"""
    def get_playlist_id(self, playlist_url=None, playlist_entry=None):
        id = ''
        if playlist_url:
            # print "Playlist URL is %s" % playlist_url
            id = re.search(self.playlist_id_pattern, playlist_url).group(0)
            print "Playlist URL %s has an id : %s" % (playlist_url, id)

        elif playlist_entry:
            id = playlist_entry.id.text
            print "Pre-Split Playlist ID is %s" % id
            id = playlist_entry.id.text.split('/')[-1]
            print "Post-Split Playlist ID for the given Playlist Entry is %s" % id
        return id  # re.search(playlist_id_pattern, playlist_url).group(0)

    def get_subscription_id(self, sub_url):
        # print "Subscription URL is %s" % sub_url
        prev = None
        for part in sub_url.split('/'):
            if prev == 'user':
                # print "Subscription ID is %s" % part
                return part
            prev = part
        raise ValueError('Could not find user in url')
        # print "Subscription ID is None"
        return None


    def get_video_name(self, video_entry):
        return video_entry.media.title.text

    # #@classmethod
    def get_playlist_name(self, playlist_id=None, playlist_entry=None):
        if (playlist_id):
            uri = 'https://gdata.youtube.com/feeds/api/playlists/' + playlist_id
            # print "Playlist URI: %s" % uri
            return self.youtube_service.GetYouTubePlaylistFeed(uri).title.text
        elif(playlist_entry):
            return playlist_entry.title.text
        return None

    # #@classmethod
    def get_subscription_name(self, sub_id=None, sub_entry=None):
        if (sub_id):
            uri = "https://gdata.youtube.com/feeds/api/users/" + sub_id
            title = self.youtube_service.GetYouTubeSubscriptionEntry(uri).title.text
            # print "Subscription URI is %s" % uri
            # #print "Subscription Title is %s" % title
            return title
        elif(sub_entry):
            title = sub_entry.title.text
            # print "Subscription Title is %s" % title
            return title
        return None

    # @classmethod
    def get_video_entry(self, video_entry=None, video_id=None, video_uri=None):
        if video_id:
            return self.youtube_service.GetYouTubeVideoEntry(video_id=video_id)
        elif video_uri:
            return self.youtube_service.GetYouTubeVideoEntry(uri=video_uri)
        elif video_entry:
            video_id = video_entry.id.text
            return self.youtube_service.GetYouTubeVideoEntry(video_id=video_id)
        return None

    # @classmethod
    def get_playlist_entry(self, playlist_entry=None, playlist_id=None):
        """
        if playlist_id:
            #print "Playlist ID is %s" % playlist_id
            # playlist_id = playlist_id.replace('PL', '')
            uri = "https://gdata.youtube.com/feeds/api/playlists/{0}".format(playlist_id)
            result = service.GetYouTubePlaylistEntry(uri)
            return result
        """

        if playlist_entry:
            plist_id = self.get_playlist_id(playlist_entry=playlist_entry)
            plist_uri = "https://gdata.youtube.com/feeds/api/playlists/" + plist_id
            print "Playlist URI is %s" % plist_uri
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
    def add_vid_to_playlist(self, video_id, playlist_uri):
        media = Media.Group()  # not added by default, but required to prevent 400
        print "The ID of the video to be added to the playlist => %s" % video_id
        print "The URI of the playlist => %s" % playlist_uri
        playlist_video_entry = gdata.youtube.YouTubePlaylistVideoEntry(atom_id=atom.Id(text=video_id), media=media)
        self.youtube_service.Post(playlist_video_entry, playlist_uri, converter=gdata.youtube.YouTubePlaylistVideoEntryFromString)
        # yt_service.Post(playlist_video_entry, playlist_uri, converter=gdata.youtube.YouTubePlaylistVideoEntryFromString)


    def add_video_to_playlist(self, video_id, playlist_id, position):
        url = 'https://gdata.youtube.com/feeds/api/playlists/{0}?v=2'.format(playlist_id)

        print "authsub_token for adding video is %s" % self.authsub_token
        print "X-GData-Key OR Youtube Developer key is => %s" % self.youtube_service.developer_key

        headers = {'Content-Type' : 'application/atom+xml',
                   'Authorization' : 'Bearer %s' % self.authsub_token,
                   'GData-Version' : '2',
                   'X-GData-Key' : 'key=%s' % self.youtube_service.developer_key}

        xml = """<?xml version="1.0" encoding="UTF-8"?>
                <entry xmlns="http://www.w3.org/2005/Atom" 
                    xmlns:yt="http://gdata.youtube.com/schemas/2007">
                <id>{0}</id>
                <yt:position>{1}</yt:position>
                </entry>""".format(video_id, position)

        params = {'key': self.youtube_service.developer_key}

        return self.youtube_service.Post(data=xml, uri=url, extra_headers=headers)  # , url_params=params)

    # #@classmethod
    def create_playlist(self, playlist_title, playlist_desc):
        return self.youtube_service.AddPlaylist(playlist_title, playlist_desc)

    def is_vid_in_playlist(video_id, playlist_id):
        pass

    def does_playlist_exist(self, user_playlist_feed, playlist_id=None, playlist_name=None):
        for entry in user_playlist_feed.entry:
            id = entry.id.text.split('/')[-1]
            if playlist_name:
                if entry.title.text == playlist_name:
                    return {"exist":True, "id":id }
            elif playlist_id:
                if id == playlist_id:
                    {"exist":True, "id":id }
        return {"exist":False}

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
            # #print "XML is: %s" % xml
        except urllib2.URLError, e:
            raise e

        return xml

    def get_pinboard(self, usern, passw):
        usern = '' + usern
        passw = '' + passw

        try:
            p = pinboard.open(username=usern, password=passw)
            # print "Get Pinboard returns " + str(p)
        except urllib2.HTTPError, error:
            print error
            return {"Pass": False}

        self.pinboard_object_data = {"Pass": True, "pinboard_object": p, "username": usern, "password": passw}
        return self.pinboard_object_data  # {"Pass": True, "pinboard_object": p, "username": usern, "password": passw}

    video_pattern = '(watch+\Wv\W)'
    playlist_pattern = '(playlist+\Wlist=)'
    channel_pattern = '(user/)'

    def get_pinboard_data(self):
        pinboard_object = self.pinboard_object_data
        posts = pinboard_object["pinboard_object"].posts(tag="youtube", count=1000)

        for post in posts:
            url = post[u'href']
            tags = post[u'tags']
            if re.search(self.video_pattern, url):
                video_id = self.get_video_id(url)
                # print "Video ID is %s" % video_id
                try:
                    video_entry = self.get_video_entry(video_id=video_id)

                except RequestError, error:
                    print error
                    print "Video Error!"
                    continue

                video_name = self.get_video_name(video_entry)
                # print "Video Name is %s" % video_name
                if url is None:
                    print "Video URL is NONE"

                temp_tags = []
                for tag in tags:
                    tag = str(tag)
                    temp_tags.append(tag)

                video_details = {"url":url, "id":video_id, "tags":temp_tags}

                self.db_videos.setdefault(video_name, video_details)
                # self.db_videos = db_videos



            elif re.search(self.playlist_pattern, url):
                playlist_id = self.get_playlist_id(playlist_url=url)
                # print "Playlist ID: %s" % playlist_id

                try:
                    playlist_name = self.get_playlist_name(playlist_id)
                except RequestError, error:
                    print error
                    print "Playlist Error!"
                    continue
                playlist_details = {"url":url, "id": playlist_id, "embed":self.get_embed_playlist(playlist_id)}
                self.db_playlists.setdefault(playlist_name, playlist_details)
                # self.db_playlists = db_playlists
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
                self.db_subscriptions.setdefault(subscription_name, subscription_details)
                # self.db_subscriptions = db_subscriptions

    """
    def commit_user(self, user):
        self.user = User.query.filter(User.username == pinboard_object["username"]).first()
        check_update = str(user.last_updated)
        if (self.authsub_token):
            yt_playlists = self.get_youtube_data()

        if (self.user is None):
            info = Info(pinboard_videos=self.db_videos, pinboard_playlists=self.db_playlists, pinboard_subscriptions=self.db_subscriptions, youtube_playlists=yt_playlists)
            self.user = User(username=pinboard_object["username"], last_updated=last_update, info=info)

        else:
           
        pass

    """

    def get_pintubes(self):
        if (self.pinboard_object_data is not None):
            if (self.pinboard_object_data["Pass"]):
                print "starting Get_Pintubes()"
                pinboard_object = self.pinboard_object_data
                user = User.query.filter(User.username == pinboard_object["username"]).first()
                last_update = self.get_last_update(pinboard_object["username"], pinboard_object["password"])


                # check_update = User.query.filter(User.last_updated == last_update).first()


                if (self.authsub_token):
                    yt_playlists = self.get_youtube_data()

                    if (user is None):
                        print "user is None"
                        self.get_pinboard_data()

                        # yt_playlists = self.get_youtube_data()
                        info = Info(pinboard_videos=self.db_videos, pinboard_playlists=self.db_playlists, pinboard_subscriptions=self.db_subscriptions, youtube_playlists=yt_playlists)
                        user = User(username=pinboard_object["username"], last_updated=last_update, info=info)
                        try:

                            # db.session.add(user)
                            # print "Added User to Session"
                            print "Adding User to Session currently causes the following Error"
                            print "OperationalError: (OperationalError) index row requires 21016 bytes, maximum size is 8191"
                            print "Will return to fix once I've handled the other problems first"

                            db.session.commit()
                            print "Committed Session/User Added"
                        except IntegrityError, error:
                            print error
                            print "You've already added a row with the same user_name before"

                    else:
                        print "user is present"
                        check_update = str(user.last_updated)
                        print "Current User was lasted updated at %s while official time of last update is %s" % (str(check_update), last_update)
                        # yt_playlists = self.get_youtube_data()
                        # check_update = str(user.last_updated)
                        user.info.youtube_playlists = yt_playlists
                        if ((check_update is None) or (check_update != last_update)):
                            if (check_update is None):
                                print "user.last_updated is None"
                            else:
                                print "user.last_updated doesn't match time of last update"
                            # user = User.query.filter_by(username=pinboard_object["username"]).first()
                            user.last_updated = last_update
                            # user.info = info

                        try:

                            db.session.commit()
                            print "Committed Session/User Present"
                        except IntegrityError, error:
                            print error
                            print "You've already added a row with the same user_name before"


                    """
                        try:
                            # db.session.add(self.user)
                            db.session.commit()
                        except IntegrityError, error:
                            print error
                            print "You've already added a row with the same user_name before"
                    """

                self.user = user
                # self.commit_user(user)
                # return self.user.info
