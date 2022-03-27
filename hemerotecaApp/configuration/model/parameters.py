from flask.globals import current_app
from hemerotecaApp import app,dbMongo

from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form
from flask_admin.contrib.mongoengine import ModelView
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import InputRequired, EqualTo,Length
import bson

class ParametersTwitter(dbMongo.Document):
    __tablename__ = 'ParametersTwitter'
    _id = dbMongo.ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    consumerKey = dbMongo.StringField(max_length=400, required=True)
    consumerSecret = dbMongo.StringField(max_length=400, required=True)
    accessToken = dbMongo.StringField(max_length=400, required=True)
    accessTokenSecret = dbMongo.StringField(max_length=400, required=True)

class ParametersTelegram(dbMongo.Document):
    __tablename__ = 'ParametersTelegram'
    _id = dbMongo.ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    apiId = dbMongo.StringField(max_length=150, required=True)
    apiHash = dbMongo.StringField(max_length=300, required=True)
    applicationName = dbMongo.StringField(max_length=300, required=True)
    
class ParametersTwitterForm(FlaskForm):
    consumerKey = StringField('Consumer key',validators=[InputRequired(message='Introduzca el dato consumer key'),Length(max=400,message='La longitud máxima es de 400 caracteres')])
    consumerSecret = StringField('Consumer secret',validators=[InputRequired(message='Introduzca el dato consumer secret'),Length(max=400,message='La longitud máxima es de 400 caracteres')])
    accessToken = StringField('Access token',validators=[InputRequired(message='Introduzca el dato access token'),Length(max=400,message='La longitud máxima es de 400 caracteres')])
    accessTokenSecret = StringField('Access token secret',validators=[InputRequired(message='Introduzca el dato access token secret'),Length(max=400,message='La longitud máxima es de 400 caracteres')])
    id=HiddenField("id")

class ParametersTelegramForm(FlaskForm):
    applicationName = StringField('Nombre de la aplicación',validators=[InputRequired(message='Introduzca el dato access token secret'),Length(max=150,message='La longitud máxima es de 150 caracteres')])
    apiId = StringField('API Id',validators=[InputRequired(message='Introduzca el dato access token secret'),Length(max=300,message='La longitud máxima es de 300 caracteres')])
    apiHash = StringField('API Hash',validators=[InputRequired(message='Introduzca el dato access token secret'),Length(max=300,message='La longitud máxima es de 300 caracteres')])
    id=HiddenField("id")

