"""empty message

Revision ID: 50c96a4aaba0
Revises: 2c3770e31104
Create Date: 2014-03-18 19:59:16.951202

"""

# revision identifiers, used by Alembic.
revision = '50c96a4aaba0'
down_revision = '2c3770e31104'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_info_pinboard_playlists', table_name='info')
    op.drop_index('ix_info_pinboard_subscriptions', table_name='info')
    op.drop_index('ix_info_pinboard_videos', table_name='info')
    op.drop_index('ix_info_youtube_playlists', table_name='info')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_info_youtube_playlists', 'info', ['youtube_playlists'], unique=False)
    op.create_index('ix_info_pinboard_videos', 'info', ['pinboard_videos'], unique=False)
    op.create_index('ix_info_pinboard_subscriptions', 'info', ['pinboard_subscriptions'], unique=False)
    op.create_index('ix_info_pinboard_playlists', 'info', ['pinboard_playlists'], unique=False)
    ### end Alembic commands ###
