#!flask/bin/python

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

import config
from micawber.providers import bootstrap_basic
from micawber.contrib.mcflask import add_oembed_filters

app = Flask(__name__, static_folder='./static',
                template_folder='./templates')

app.config.from_object(config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
# app.config.from_object(settings)

oembed_providers = bootstrap_basic()
add_oembed_filters(app, oembed_providers)

import views, models
