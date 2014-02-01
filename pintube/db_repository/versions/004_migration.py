from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
info = Table('info', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('pinboard_videos', String),
    Column('pinboard_playlists', String),
    Column('pinboard_subscriptions', String),
    Column('youtube_playlists', String),
    Column('youtube_subscriptions', String),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['info'].columns['youtube_playlists'].drop()
    pre_meta.tables['info'].columns['youtube_subscriptions'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['info'].columns['youtube_playlists'].create()
    pre_meta.tables['info'].columns['youtube_subscriptions'].create()
