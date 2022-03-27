from flask.globals import current_app
from hemerotecaApp import app,dbMongo

from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form
from flask_admin.contrib.mongoengine import ModelView
from wtforms import StringField, HiddenField
from wtforms.validators import InputRequired, EqualTo
import bson

class BotTelegram(dbMongo.Document):
    __tablename__ = 'BotTelegram'
    _id = dbMongo.ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    maxCatchNumber = dbMongo.IntField()
    channel = dbMongo.StringField(max_length=300, required=True)
    pid = dbMongo.IntField()
    
class BotTwitter(dbMongo.Document):
    __tablename__ = 'BotTwitter'
    _id = dbMongo.ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    maxCatchNumber = dbMongo.IntField()
    pid = dbMongo.IntField()
    