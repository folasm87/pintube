from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField
from wtforms.validators import Required

class Pinboard_Login_Form(Form):
    pin_user_id = TextField('pin_user_id', validators=[Required()])
    pin_password = PasswordField('pin_password', validators=[Required()])
    pin_remember_me = BooleanField('pin_remember_me', default=False)

class Youtube_Login_Form(Form):
    yt_user_id = TextField('yt_user_id', validators=[Required()])
    yt_password = TextField('yt_password', validators=[Required()])
    yt_remember_me = BooleanField('yt_remember_me', default=False)
