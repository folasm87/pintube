from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required

class LoginForm(Form):
    user_id = TextField('user_id', validators = [Required()])
    password = TextField('password', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)