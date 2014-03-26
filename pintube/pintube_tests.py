import os
# import pintube
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from mock import Mock
from mock import MagicMock
from mock import patch

import tempfile

from pinclass import Pintube

from __init__ import app, db
from models import User
from requests import get
from flask.ext.testing import TestCase

"""
class PintubeTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = get('http://api.postgression.com').text
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    
    def setUp(self):
        self.db_fd, pintube.app.config['DATABASE'] = tempfile.mkstemp()
        pintube.app.config['TESTING'] = True
        self.app = pintube.app.test_client()
        pintube.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(pintube.app.config['DATABASE'])
"""


class PintubeTest(unittest.TestCase):
    def create_app(self):
        """Configure our app to use a postgression database."""
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        # app.config['LIVESERVER_PORT'] = 8943
        app.config['SQLALCHEMY_DATABASE_URI'] = get('http://api.postgression.com').text
        self.pintube = Pintube()


        # mock = MagicMock()

    def setUp(self):
        """Prepare the database tables."""
        db.create_all()

    def tearDown(self):
        """Rip out the database tables to have a 'clean slate' for the next test case."""
        db.session.remove()
        db.drop_all()

    def test_user_saves_properly(self):
        """Save our model to a postgression database, then ensure things are OK."""
        user = User(username='john')
        db.session.add(user)
        db.session.commit()
        self.assertEqual(user.id, 1)


    """
        Testing Class Methods. We Test:
            * Does it receive the correct input
            * Does it return the right output
    """
    def test_get_authsub_url(self):
        self.pintube.get_authsub_url = MagickMock()
        """
        https://accounts.google.com/AuthSubRequest?scope=http%3A%2F%2Fgdata.youtube.com&session=1&secure=0
        &hd=default&next=http%3A%2F%2Flocalhost%3A5000%2F%3Fauth_sub_scopes%3Dhttp%253A%252F%252Fgdata.youtube.com
        """

    def test_set_authsub_token(self):
        self.pintube.set_authsub_token = MagickMock()

    def test_upgrade_to_session_token(self):
        self.pintube.upgrade_to_session_token = MagickMock()

    def test_get_youtube_data(self):
        self.pintube.get_youtube_data = MagickMock()

    def test_add_video_to_possible_playlists(self):
        self.pintube.add_video_to_possible_playlists = MagickMock()

    def test_copy_playlist_to(self):
        self.pintube.copy_playlist_to = MagickMock()

    def test_get_list_of_feed_video_id(self):
        self.pintube.get_list_of_feed_video_id = MagickMock()

    def test_get_video_id(self):
        self.pintube.get_video_id = MagickMock()

    def test_get_playlist_id(self):
        self.pintube.get_playlist_id = MagickMock()

    def test_get_subscription_id(self):
        self.pintube.get_subscription_id = MagickMock()

    def test_get_video_name(self):
        self.pintube.get_video_name = MagickMock()

    def test_get_playlist_name(self):
        self.pintube.get_playlist_name = MagickMock()

    def test_get_subscription_name(self):
        self.pintube.get_subscription_name = MagickMock()

    def test_get_video_entry(self):
        self.pintube.get_video_entry = MagickMock()

    def test_get_playlist_entry(self):
        self.pintube.get_playlist_entry = MagickMock()

    def test_get_subscription_entry(self):
        self.pintube.get_subscription_entry = MagickMock()

    def test_get_user_playlist_feed(self):
        self.pintube.get_user_playlist_feed = MagickMock()

    def test_get_playlist_video_feed(self):
        self.pintube.get_playlist_video_feed = MagickMock()

    def test_get_subscription_feed(self):
        self.pintube.get_subscription_feed = MagickMock()

    def test_add_vid_to_playlist(self):
        self.pintube.add_vid_to_playlist = MagickMock()

    def test_add_video_to_playlist(self):
        self.pintube.add_video_to_playlist = MagickMock()

    def test_create_playlist(self):
        self.pintube.create_playlist = MagickMock()

    def test_does_playlist_exist(self):
        self.pintube.does_playlist_exist = MagickMock()

    def test_get_embed_playlist(self):
        self.pintube.get_embed_playlist = MagickMock()

    def test_get_embed_subscription(self):
        self.pintube.get_embed_subscription = MagickMock()

    def test_get_last_update(self):
        self.pintube.get_last_update = MagickMock()

    def test_get_pinboard(self):
        self.pintube.get_pinboard = MagickMock()

    def test_get_pinboard_data(self):
        self.pintube.get_pinboard_data = MagickMock()

    def test_get_pintubes(self):
        self.pintube.get_pintubes = MagickMock()






if __name__ == '__main__':
    unittest.main()
