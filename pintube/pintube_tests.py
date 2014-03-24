import os
# import pintube
import unittest
from unittest.mock import MagicMock
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





if __name__ == '__main__':
    unittest.main()
