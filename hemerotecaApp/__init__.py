from flask import request, redirect, url_for, Flask
from flask_login import LoginManager, logout_user, current_user
from flask_user import UserManager, TokenManager
from flask_user.signals import user_registered
from flask_mongoengine import MongoEngine
from functools import wraps
import os
from flask_babel import Babel


#create flask app
app = Flask(__name__)
app.config.from_object('configuration.DevelopmentConfig')

#configure mongoengine
dbMongo = MongoEngine()
dbMongo.init_app(app)

#babel = Babel(app)

#configure flask-user and flask-login
from hemerotecaApp.auth.model.user import User
user_manager = UserManager(app, dbMongo, User)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user.login"

#mapping views with blueprint
from hemerotecaApp.catches.publicationController import publication
from hemerotecaApp.auth.userController import userBp
from hemerotecaApp.configuration.configurationController import configurationController
from hemerotecaApp.auth.auth_views import auth
from hemerotecaApp.appvue.views import appvue

from hemerotecaApp.rest_api.publication_api import publication_view

app.register_blueprint(publication)
app.register_blueprint(configurationController)
app.register_blueprint(userBp)
app.register_blueprint(appvue)

# create default user for app
userSuperadmin=User.objects(username='SuperadminFactory').first()

if not userSuperadmin:
   userSuperadmin=User(username='SuperadminFactory', password = user_manager.hash_password('SuperadminFactory'), roles=['Superadmin'])
   userSuperadmin.save()

