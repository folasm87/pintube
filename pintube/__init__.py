#!flask/bin/python

import os, sys
from flask import Flask, g
import flask_sijax
# from flask_sijax import Sijax
# from flask.ext.admin import Admin, BaseView, expose
# from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
import psycopg2
# from flask.ext.restless import APIManager

import config
from micawber.providers import bootstrap_basic
from micawber.contrib.mcflask import add_oembed_filters

"""
class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('panel.html')
"""



app = Flask(__name__, static_folder='./static',
                template_folder='./templates')

app.config.from_object(config)


db = SQLAlchemy(app)

# sijax = Sijax(app)
# flask_sijax.Sijax(app)
# admin = Admin(app)
# admin.add_view(MyView(name='Hello'))
# admin.add_view(ModelView(User, db.session))

login_manager = LoginManager()
login_manager.init_app(app)
# app.config.from_object(settings)

oembed_providers = bootstrap_basic()
add_oembed_filters(app, oembed_providers)


import views, models

