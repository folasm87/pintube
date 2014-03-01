from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField, HiddenField, validators
from wtforms.validators import Required, DataRequired

class Pinboard_Login_Form(Form):
    pin_user_id = TextField('pin_user_id', validators=[Required()])
    pin_password = PasswordField('pin_password', validators=[Required()])
    pin_remember_me = BooleanField('pin_remember_me', default=False)


class Copy_Playlist(Form):
    new_playlist_name = TextField('new_playlist_name', validators=[DataRequired()])
    original_playlist_url = HiddenField('original_playlist_url', validators=[DataRequired()])


class Add_Video(Form):
    playlist_names = HiddenField('playlist_name', validators=[DataRequired()])
    video_url = HiddenField('video_url', validators=[DataRequired()])


"""
class Youtube_Login_Form(Form):
    yt_user_id = TextField('yt_user_id', validators=[Required()])
    yt_password = TextField('yt_password', validators=[Required()])
    yt_remember_me = BooleanField('yt_remember_me', default=False)
"""
