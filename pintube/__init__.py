#!flask/bin/python

import os, sys
from flask import Flask, g
import flask_sijax
from flask.ext.rq import RQ
# from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
import psycopg2

import config
from micawber.providers import bootstrap_basic
from micawber.contrib.mcflask import add_oembed_filters

app = Flask(__name__, static_folder='./static',
                template_folder='./templates')


app.debug = True
app.config.from_object(config)

db = SQLAlchemy(app)

RQ(app)

# login_manager = LoginManager()
# login_manager.init_app(app)

oembed_providers = bootstrap_basic()
add_oembed_filters(app, oembed_providers)

import views, models
