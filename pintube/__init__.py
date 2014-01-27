from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from pintube import settings
from micawber.providers import bootstrap_basic
from micawber.contrib.mcflask import add_oembed_filters

app = Flask(__name__, static_folder='./static',
                template_folder='./templates')
login_manager = LoginManager()
login_manager.init_app(app)
app.config.from_object(settings)

oembed_providers = bootstrap_basic()
add_oembed_filters(app, oembed_providers)

import views
