import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# SQLALCHEMY_DATABASE_URI = "postgresql://folasm87:GoatKiller87@localhost/pintube"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_ECHO = True

CSRF_ENABLED = True
SECRET_KEY = b'KC\xed\xd9\xd1p\xd1A\xe7\xcer\xa2\x89\xb7Gv\xb9\xce\x1e\xd5\xe7\t\xabu'
