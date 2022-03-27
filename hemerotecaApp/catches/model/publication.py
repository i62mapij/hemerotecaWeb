from flask.globals import current_app
from hemerotecaApp import app,dbMongo

from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form
from flask_admin.contrib.mongoengine import ModelView
from wtforms import StringField, DateTimeField
from wtforms.validators import InputRequired, EqualTo
import bson
from PIL import Image
from datetime import datetime

class Notes(dbMongo.Document):
    __tablename__ = 'Notes'
    _id = dbMongo.ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    text = dbMongo.StringField(max_length=1500, required=True)
    date = dbMongo.DateTimeField(default=datetime.now, required=True)

class Publications(dbMongo.Document):
    __tablename__ = 'Publications'
    _id = dbMongo.ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    title = dbMongo.StringField(max_length=500, required=True)
    summary = dbMongo.StringField(max_length=4000)
    text = dbMongo.StringField(max_length=15000, required=True)
    url = dbMongo.StringField(max_length=1000)
    screen_name = dbMongo.StringField(max_length=100)
    notes = dbMongo.ListField(dbMongo.ReferenceField(Notes))
    channel = dbMongo.StringField(max_length=200)
    image = dbMongo.ImageField()
    type = dbMongo.StringField(max_length=50)
    date = dbMongo.DateTimeField(default=datetime.now, required=True)
    webDate = dbMongo.DateTimeField(default=datetime.now, required=True)
    imagePath = ''

