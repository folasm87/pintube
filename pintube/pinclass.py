"""
Gets the user data from pinboard and youtube.
If pinboard has not been updated recently and data is already
in the database then it will just call the user data from the database.
"""

import re
import sys
import gzip
import urllib2
import StringIO
from xml.dom import minidom

import pinboard

import atom
import gdata
import gdata.media as Media
import gdata.youtube.service
from gdata.service import RequestError

from flask import Markup
# from flask.ext.restless import APIManager

from flask.ext.rq import job
from pintube import db
from pintube import app

"""
from __init__ import db
from __init__ import app

"""
from pintube.models import User
from pintube.models import Info
from sqlalchemy.exc import IntegrityError


reload(sys)
sys.setdefaultencoding('utf-8')

"""
db.create_all()
API_MANAGER = APIManager(app, flask_sqlalchemy_db=db)
API_MANAGER.create_api(User, methods=['GET', 'POST', 'DELETE', 'PUT'])
API_MANAGER.create_api(Info, methods=['GET', 'POST', 'DELETE', 'PUT'])
"""

class Pintube(object):
    """
    Class that handles the retrieval of user data from pinboard and youtube.
    """

    # my_pintube = Pintube()
    # my_pintube.youtube_service.GenerateAuthSubURL
    # = Mock(return_value='http://fffff')


    def __init__(self):
        """Initializing the Pintube object by initializing
        the GData YouTubeService object
        so that we can communicate with the YouTube API
        """
        self.youtube_service = gdata.youtube.service.YouTubeService()
        self.youtube_service.ssl = True
        self.youtube_service.developer_key = 'AI39si5JGdicli8WGHhzGfW07rvFHMmlLJMtpB1zx3rpBhaBruxL4wkqGFPkQ0Dj2MDFObGCsR_wphhr3N9QpyTUOH9y_aeWsQ'
        self.youtube_service.source = 'PinTube'
        self.authsub_token = ''
        self.youtube_data = {}
        self.db_videos = {}
        self.db_playlists = {}
        self.db_subscriptions = {}
        self.user_playlist_feed = None
        self.pinboard_object_data = {}


    def get_authsub_url(self):
        """
        Returns the AuthSub URL
        """
        next = 'http://0.0.0.0:5000'  #  'http://flask-pintube.herokuapp.com/'   'http://0.0.0.0:5000'  'http://localhost:5000/'
        scope = 'http://gdata.youtube.com'
        secure = False
        session = True
        return self.youtube_service.GenerateAuthSubURL(next, \
                                                       scope, secure, session)


    def set_authsub_token(self, token):
        """
        Sets the authsub token
        """
        self.authsub_token = token
        return self.youtube_service.SetAuthSubToken(token=token)

    def upgrade_to_session_token(self):
        """
        Upgrades the session token
        """
        print "Current token is %s" % self.youtube_service.current_token
        return self.youtube_service.UpgradeToSessionToken()

    video_url_pattern = r"""(http(s?)://www.youtube.com/watch+\Wv\W[a-zA-Z0-9-_]+)"""
    def get_youtube_data(self):
        """
        Retrieve's the user's youtube data
        """
        print "Starting GetYoutubeData Function"

        pinboard_object = self.pinboard_object_data

        current_user = User.query.filter(User.username == pinboard_object["username"]).first()




        if ((current_user is None) or (current_user.info is None)
            or (current_user.info.youtube_playlists is None)):
            print "Youtube Playlists doesn't exist \
             within the current user's info"

            playlists = {}
            p_feed = None

            if self.user_playlist_feed is not None:
                p_feed = self.user_playlist_feed
            else:
                self.user_playlist_feed = self.get_user_playlist_feed()
                p_feed = self.user_playlist_feed

            for p_entry in p_feed.entry:
                p_id = p_entry.id.text.split('/')[-1]
                p_title = p_entry.title.text
                v_feed = self.get_playlist_video_feed(p_id)
                videos = {}
                i = 0
                print ""
                print "_"*30
                print "Your Youtube Account has a playlist \
                [%s] with id [%s] ->" % (p_title, p_id)


                for v_entry in v_feed.entry:
                    v_title = v_entry.title.text
                    v_uri = v_entry.id.text

                    try:
                        video_entry = self.get_video_entry(video_uri=v_uri)
                    except RequestError, error:
                        print error
                        print "Video Entry Error!"
                        continue


                    i += 1
                    video_data = {}

                    if video_entry.media.player is not None:
                        media_url = video_entry.media.player.url
                        media_url = re.search(self.video_url_pattern, media_url).group(0)
                        video_data = {"video_url": media_url, "video_uri": v_uri}
                    else:
                        video_data = {"video_url": None, "video_uri": v_uri}

                    videos.setdefault(v_title, video_data)

                print "Playlist [%s] has [%s] videos" % (p_title, i)
                print ""
                print "_"*30

                playlist = {"number_of_vids": i, "videos": videos}
                playlists.setdefault(p_title, playlist)

            print ""
            print "_"*30
            print "Your have {0} Playlists in your Youtube Account".format(len(playlists))
            return playlists

        return current_user.info.youtube_playlists


    def add_video_to_possible_playlists(self, video_url, playlist_name):
        """
        Adds a video to a playlist. Checks to see if playlist already exists
        """
        vid_id = self.get_video_id(video_url)
        if self.user_playlist_feed is None:
            self.user_playlist_feed = self.get_user_playlist_feed()

        p_exist = self.does_playlist_exist(user_playlist_feed=self.user_playlist_feed, playlist_name=playlist_name)  # user_playlist_name)
        if p_exist["exist"]:
            try:
                self.add_video_to_playlist(vid_id, p_exist["id"], 1)
            except RequestError, error:
                print error
                print "Adding Video to the Already Existing Playlist Did Not Work"
        else:
            new_playlist = self.create_playlist(playlist_title=playlist_name, playlist_desc="A Pintube Playlist")
            new_playlist_id = self.get_playlist_id(playlist_entry=new_playlist)
            new_playlist_uri = "https://gdata.youtube.com/feeds/api/playlists/" + new_playlist_id


            try:
                self.add_vid_to_playlist(video_id=vid_id, playlist_uri=new_playlist_uri)
            except RequestError, error:
                print error
                print "Adding Video to A New Playlist Did Not Work"





    def copy_playlist_to(self, original_playlist_url, new_playlist_name):
        """
        Copies a playlist. Checks if the supplied name is already used by the user for a current playlist.
        If it is then it will cycle through the videos in the original playlist and add missing videos.
        """
        new_playlist = None
        new_playlist_id = ""
        new_playlist_uri = ""
        original_playlist_id = self.get_playlist_id(playlist_url=original_playlist_url)
        original_playlist_video_feed = self.get_playlist_video_feed(original_playlist_id)

        if self.user_playlist_feed is None:
            self.user_playlist_feed = self.get_user_playlist_feed()

        p_exist = self.does_playlist_exist(user_playlist_feed=self.user_playlist_feed, playlist_name=new_playlist_name)
        new_playlist_video_feed = None
        new_feed_list_id = []
        original_feed_list_id = self.get_list_of_feed_video_id(original_playlist_video_feed)
        if p_exist["exist"]:
            new_playlist_video_feed = self.get_playlist_video_feed(p_exist["id"])
            new_feed_list_id = self.get_list_of_feed_video_id(new_playlist_video_feed)

        else:
            new_playlist = self.create_playlist(new_playlist_name, "A PinTube Playlist")
            new_playlist_id = self.get_playlist_id(playlist_entry=new_playlist)
            new_playlist_uri = "https://gdata.youtube.com/feeds/api/playlists/" + new_playlist_id


        for feed_id in original_feed_list_id:
            if p_exist["exist"]:
                if feed_id not in new_feed_list_id:
                    try:
                        self.add_video_to_playlist(feed_id, p_exist["id"], 1)
                    except RequestError, error:
                        print error
                        print "Adding Video to the Already Existing Playlist Did Not Work"


            else:
                try:
                    self.add_vid_to_playlist(video_id=feed_id, playlist_uri=new_playlist_uri)
                except RequestError, error:
                    print error
                    print "CP Adding Video To Playlist Error!"
                    continue



    def get_list_of_feed_video_id(self, video_feed):
        """
        Returns a list of video id's from a video feed
        """
        list_of_id = []
        for video_entry in video_feed.entry:
            print "This is the Entry ID Text => " + video_entry.id.text
            try:
                vid_entry = self.get_video_entry(video_uri=video_entry.id.text)
                vid_id = vid_entry.id.text

                video_entry = self.youtube_service.GetYouTubeVideoEntry(vid_id)
                video_url = ""
                if video_entry.media.player is not None:
                    video_url = video_entry.media.player.url
                    video_url = re.search(self.video_url_pattern, video_url).group(0)

                video_id = self.get_video_id(video_url)
                list_of_id.append(video_id)
            except RequestError, error:
                print error
                print "Error for the Entry ID Text => " + video_entry.id.text

        return list_of_id



    vid_id_pattern = r"""youtu(?:\.be|be\.com)/(?:.*v(?:/|=)|(?:.*/)?)([a-zA-Z0-9-_]+)"""
    def get_video_id(self, vid_url):
        """
        Returns a video ID
        """
        return re.search(self.vid_id_pattern, vid_url).group(1)

    playlist_id_pattern = r"""([a-zA-Z0-9_\-]{11,100})"""
    def get_playlist_id(self, playlist_url=None, playlist_entry=None):
        """
        Returns a playlist ID
        """
        playlist_id = ''
        if playlist_url:
            playlist_id = re.search(self.playlist_id_pattern, playlist_url).group(0)
            print "Playlist URL %s has an id : %s" % (playlist_url, playlist_id)

        elif playlist_entry:
            playlist_id = playlist_entry.id.text
            print "Pre-Split Playlist ID is %s" % playlist_id
            playlist_id = playlist_entry.id.text.split('/')[-1]
            print "Post-Split Playlist ID for the given Playlist Entry is %s" % playlist_id
        return playlist_id

    def get_subscription_id(self, sub_url):
        """
        Returns a subscription ID
        """
        prev = None
        for part in sub_url.split('/'):
            if prev == 'user':
                return part
            prev = part
        raise ValueError('Could not find user in url')
        return None


    def get_video_name(self, video_entry):
        """
        Returns a video name
        """
        return video_entry.media.title.text


    def get_playlist_name(self, playlist_id=None, playlist_entry=None):
        """
        Returns a playlist name
        """
        if playlist_id:
            uri = 'https://gdata.youtube.com/feeds/api/playlists/' + playlist_id
            print "Playlist URI is " + uri
            playlist_feed = self.youtube_service.GetYouTubePlaylistFeed(uri)  # .title.text
            print "Playlist Name is " + playlist_feed.title.text
            return playlist_feed.title.text  # name
        elif playlist_entry:
            name = playlist_entry.title.text
            print "Playlist Name is " + name
            return name
        return None


    def get_subscription_name(self, sub_id=None, sub_entry=None):
        """
        Returns a subscription name
        """
        if sub_id:
            uri = "https://gdata.youtube.com/feeds/api/users/" + sub_id
            print "Subscription URI is " + uri
            title = self.youtube_service.GetYouTubeSubscriptionEntry(uri).title.text
            print "Subscription Name is " + title
            return title
        elif sub_entry:
            title = sub_entry.title.text
            print "Subscription Name is " + title
            return title
        return None


    def get_video_entry(self, video_entry=None, video_id=None, video_uri=None):
        """
        Returns a video entry
        """
        if video_id:
            return self.youtube_service.GetYouTubeVideoEntry(video_id=video_id)
        elif video_uri:
            return self.youtube_service.GetYouTubeVideoEntry(uri=video_uri)
        elif video_entry:
            video_id = video_entry.id.text
            return self.youtube_service.GetYouTubeVideoEntry(video_id=video_id)
        return None


    def get_playlist_entry(self, playlist_entry=None):
        """
        Returns a playlist entry
        """
        if playlist_entry:
            plist_id = self.get_playlist_id(playlist_entry=playlist_entry)
            plist_uri = "https://gdata.youtube.com/feeds/api/playlists/" + plist_id
            print "Playlist URI is %s" % plist_uri
            return self.youtube_service.GetYouTubePlaylistEntry(plist_uri)

        return None


    def get_subscription_entry(self, sub_entry=None, sub_id=None):
        """
        Returns a subscription entry
        """
        if sub_id:
            return self.youtube_service.GetYouTubeSubscriptionEntry(sub_id)
        elif sub_entry:
            s_id = sub_entry.id.text
            return self.youtube_service.GetYouTubeSubscriptionEntry(s_id)

        return None


    def get_user_playlist_feed(self):
        """
        Returns a user's playlist feed
        """
        return self.youtube_service.GetYouTubePlaylistFeed(username='default')


    def get_playlist_video_feed(self, playlist_id):
        """
        Returns a user's video feed
        """
        return self.youtube_service.GetYouTubePlaylistVideoFeed(playlist_id=playlist_id)


    def get_subscription_feed(self):
        """
        Returns a user's subscription feed
        """
        return self.youtube_service.GetYouTubeSubscriptionFeed(username='default')

    def get_video_pic(self, video_id):
        """
        Returns the picture of a video
        """
        return """<img src="http://img.youtube.com/vi/{0}/hqdefault.jpg"></img>""".format(video_id)


    def add_vid_to_playlist(self, video_id, playlist_uri):
        """
        Adds a video to a playlist
        """
        media = Media.Group()  # not added by default, but required to prevent 400
        print "The ID of the video to be added to the playlist => %s" % video_id
        print "The URI of the playlist => %s" % playlist_uri
        playlist_video_entry = gdata.youtube.YouTubePlaylistVideoEntry(atom_id=atom.Id(text=video_id), media=media)
        self.youtube_service.Post(playlist_video_entry, playlist_uri, converter=gdata.youtube.YouTubePlaylistVideoEntryFromString)



    def add_video_to_playlist(self, video_id, playlist_id, position):
        """
        Alternate way to add a video to playlist
        """
        url = 'https://gdata.youtube.com/feeds/api/playlists/{0}?v=2'.format(playlist_id)

        print "AUTHSUB_TOKEN for adding video is %s" % self.authsub_token
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

        return self.youtube_service.Post(data=xml, uri=url, extra_headers=headers, url_params=params)


    def create_playlist(self, playlist_title, playlist_desc):
        """
        Create a playlist
        """
        return self.youtube_service.AddPlaylist(playlist_title, playlist_desc)

    def is_vid_in_playlist(self, video_id, playlist_id):
        """
        Is video in the playlist
        """
        pass

    def does_playlist_exist(self, user_playlist_feed, playlist_id=None, playlist_name=None):
        """
        Does the the playlist exist (Y/N)?
        """
        for entry in user_playlist_feed.entry:
            entry_id = entry.id.text.split('/')[-1]
            if playlist_name:
                if entry.title.text == playlist_name:
                    return {"exist":True, "id":entry_id}
            elif playlist_id:
                if entry_id == playlist_id:
                    return {"exist":True, "id":entry_id}
        return {"exist":False}

    def get_embed_playlist(self, playlist_id):
        """
        Returns playlist in embeddable code
        """
        to_embed = Markup("""<iframe id="ytplayer" type="text/html" width="640" height="360"
                                src="https://www.youtube.com/embed/?listType=playlist&list={0}&theme=light"
                                frameborder="0" allowfullscreen></iframe>""".format(playlist_id))
        return to_embed


    def get_embed_subscription(self, sub_id):
        """
        Returns embeddable subscriptions
        """
        to_embed = Markup("""<div class="g-ytsubscribe" data-channel="{0}" data-layout="full" data-count="default"></div>""".format(sub_id))
        return to_embed


    # Code from Python-Pinboard. Used to directly get to last_updated information
    USER_AGENT = "Python-Pinboard/1.0 +http://morgancraft.com/service_layer/python-pinboard/"
    def get_last_update(self, username, password):
        """
        Return the time of last update for pinboard
        """
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
        except urllib2.URLError, error:
            raise error

        return xml

    @job
    def get_pinboard(self, usern, passw):
        """
        Sign in to the pinboard service
        """
        usern = '' + usern
        passw = '' + passw

        try:
            pinboard_data = pinboard.open(username=usern, password=passw)
        except urllib2.HTTPError, error:
            print error
            return {"Pass": False}

        self.pinboard_object_data = {"Pass": True, "pinboard_object": pinboard_data, "username": usern, "password": passw}
        return self.pinboard_object_data

    video_pattern = r'(watch+\Wv\W)'
    playlist_pattern = r'(playlist+\Wlist=)'
    channel_pattern = r'(user/)'

    def get_pinboard_data(self):
        """
        Retrieves the pinboard data
        """
        pinboard_object = self.pinboard_object_data
        posts = pinboard_object["pinboard_object"].posts(tag="youtube", count=1000)
        db_videos = {}
        db_playlists = {}
        db_subscriptions = {}

        for post in posts:
            url = post[u'href']
            tags = post[u'tags']
            if re.search(self.video_pattern, url):
                video_id = self.get_video_id(url)
                try:
                    video_entry = self.get_video_entry(video_id=video_id)

                except RequestError, error:
                    print error
                    print "Video Error!"
                    continue

                video_name = self.get_video_name(video_entry)
                if url is None:
                    print "Video URL is NONE"

                temp_tags = []
                for tag in tags:
                    tag = str(tag)
                    temp_tags.append(tag)

                video_details = {"url":url, "id":video_id, "tags":temp_tags}
                db_videos.setdefault(video_name, video_details)
                self.db_videos = db_videos

            elif re.search(self.playlist_pattern, url):
                playlist_id = self.get_playlist_id(playlist_url=url)

                try:
                    playlist_name = self.get_playlist_name(playlist_id)
                except RequestError, error:
                    print error
                    print "Playlist Error!"
                    continue
                playlist_details = {"url":url, "id": playlist_id, "embed":self.get_embed_playlist(playlist_id)}
                db_playlists.setdefault(playlist_name, playlist_details)
                self.db_playlists = db_playlists

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
                self.db_subscriptions = db_subscriptions

    @job
    def get_pintubes(self):
        """
        Retrieves the pinboard and youtube data
        """
        if self.pinboard_object_data is not None:
            if self.pinboard_object_data["Pass"]:
                print "starting Get_Pintubes()"
                pinboard_object = self.pinboard_object_data
                user = User.query.filter(User.username == pinboard_object["username"]).first()
                last_update = self.get_last_update(pinboard_object["username"], pinboard_object["password"])

                if self.authsub_token:
                    yt_playlists = self.get_youtube_data()
                    self.youtube_data = yt_playlists

                    if user is None:
                        print "user is None"

                        self.get_pinboard_data()

                        info = Info(pinboard_videos=self.db_videos, pinboard_playlists=self.db_playlists, pinboard_subscriptions=self.db_subscriptions, youtube_playlists=yt_playlists)
                        user = User(username=pinboard_object["username"], last_updated=last_update, info=info)
                        try:

                            db.session.add(user)
                            print "Added User to Session"
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
                        if check_update != last_update:
                            print "Time of last update has changed"
                            self.get_pinboard_data()
                            user.last_updated = last_update
                        else:
                            self.db_videos = user.info.pinboard_videos
                            self.db_playlists = user.info.pinboard_playlists
                            self.db_subscriptions = user.info.pinboard_subscriptions

                        print "Current User was lasted updated at %s while official time of last update is %s" % (str(check_update), last_update)
                        user.info.youtube_playlists = yt_playlists
                        """
                        if ((check_update is None) or (check_update != last_update)):
                            if (check_update is None):
                                print "user.last_updated is None"
                            else:
                                print "user.last_updated doesn't match time of last update"
                            user.last_updated = last_update
                        """
                        try:
                            db.session.commit()
                            print "Committed Session/User Present"
                        except IntegrityError, error:
                            print error
                            print "You've already added a row with the same user_name before"


