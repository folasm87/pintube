from flask import Flask
from flask.ext.login import LoginManager
from pintube import settings

app = Flask(__name__, static_folder='./static',
                template_folder='./templates')
login_manager = LoginManager()
login_manager.init_app(app)
app.config.from_object(settings)

import views