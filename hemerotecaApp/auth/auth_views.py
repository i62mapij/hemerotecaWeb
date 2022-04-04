from flask import Blueprint

from hemerotecaApp.auth.model.user import User
from hemerotecaApp import dbMongo
from hemerotecaApp import login_manager
import bson

auth = Blueprint('auth',__name__)

#necessary method for flask-login
@login_manager.user_loader
def load_user(user_id):
    user=User.objects(_id=bson.objectid.ObjectId(user_id)).first()
    return user



