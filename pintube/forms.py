from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField, validators
from wtforms.validators import Required

class Pinboard_Login_Form(Form):
    pin_user_id = TextField('pin_user_id', validators=[Required()])
    pin_password = PasswordField('pin_password', validators=[Required()])
    pin_remember_me = BooleanField('pin_remember_me', default=False)
