import tweepy
import json
from mongoengine import *
import bson
import tempfile
import sys
sys.path.insert(0,"..")
from urlsMapper import urlToObject 
from PIL import Image
from datetime import datetime
import base64
from base64 import b64encode
import os.path
import logging
import time
import requests
import configparser
import json
import re
from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (PeerChannel)
from urlsMapper import urlToObject 
from logging.handlers import RotatingFileHandler

class ParametersTelegram(Document):
    __tablename__ = 'ParametersTelegram'
    _id = ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    apiId = StringField(max_length=150, required=True)
    apiHash = StringField(max_length=300, required=True)
    applicationName = StringField(max_length=300, required=True)

class Notes(Document):
    __tablename__ = 'Notes'
    _id = ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    text = StringField(max_length=1500, required=True)
    date = DateTimeField(default=datetime.now, required=True)

class Publications(Document):
    __tablename__ = 'Publications'
    _id = ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    title = StringField(max_length=500, required=True)
    summary = StringField(max_length=4000)
    text = StringField(max_length=15000, required=True)
    url = StringField(max_length=1000)
    screen_name = StringField(max_length=100)
    notes = ListField(ReferenceField(Notes))
    channel = StringField(max_length=200)
    image = ImageField()
    type = StringField(max_length=50)
    date = DateTimeField(default=datetime.now, required=True)
    webDate = DateTimeField(default=datetime.now, required=True)

class BotTelegram(Document):
    __tablename__ = 'BotTelegram'
    _id = ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    maxCatchNumber = IntField()
    channel = StringField(max_length=300, required=True)
    pid = IntField()

class Counters(Document):
    __tablename__ = 'Counters'
    _id = ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    lastDMTwitterId = StringField(max_length=100)
    lastReplieTwitterId = StringField(max_length=100)
    publicationsTwitterDay =  IntField()
    lastPublicationDayTwitter = DateTimeField()
    publicationsTelegramDay =  IntField()
    lastPublicationDayTelegram = DateTimeField()


connect('hemeroteca')
parametersTelegram = ParametersTelegram.objects().first()
logging.basicConfig(filename='./log/hemerotecaWebTelegramBot.log', level=logging.DEBUG)
api_id = parametersTelegram.apiId
api_hash = parametersTelegram.apiHash
applicationName = parametersTelegram.applicationName
optionsTelegram = BotTelegram.objects().first()

channel = 'https://t.me/'+optionsTelegram.channel
   
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

logFile = './log/hemerotecaWebTelegramBot.log'

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=10, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

logger = logging.getLogger('root')
logger.setLevel(logging.INFO)

logger.addHandler(my_handler)

client = TelegramClient(applicationName, api_id, api_hash)
user_input_channel = channel

def catchWebPage(webPage):
       try:
        logger.info(f"Inicia captura de publicación  ")  
        url=webPage.url
        classUrlToObject=urlToObject.UrlToObject()
        objectPage=classUrlToObject.getDataFromWebPage(url,'','Telegram')
        bytes_image = bytearray(requests.get(objectPage["image"]).content)
        type=extension = os.path.splitext(objectPage["image"])[1]

        publication = Publications.objects(url=url).first()

        if not publication and objectPage["text"]!='':
         logger.info(f"Almacena publicación de la url "+url)
         webDate=objectPage["webDate"] 
         
         try:
          webDate=datetime.strptime(webDate, '%d/%m/%Y')
         except Exception as exc:
          webDate=None

         with tempfile.TemporaryFile() as f:
                f.write(bytes_image)
                f.flush()
                f.seek(0)
                image=f
                publication = Publications(title = objectPage["title"], summary = objectPage["summary"], text = objectPage["text"], url = objectPage["url"], screen_name = '', notes = [], channel = channel, image = image, type='Telegram', webDate = webDate)
                publication.save()

         logger.info(f"Actualiza contadores "+url)  
         countersBot=Counters.objects().first()
         if countersBot:
          if countersBot.publicationsTelegramDay:
           countersBot.publicationsTelegramDay=countersBot.publicationsTelegramDay+1
          else:
           countersBot.publicationsTelegramDay=1  
          countersBot.lastPublicationDayTelegram=datetime.now
          countersBot=countersBot.save()
         else:
          countersBot=Counters(publicationsTelegramDay=1,lastPublicationDayTelegram=datetime.now)
          countersBot=countersBot.save() 
        else:
          logger.info(f"No almacena publicación de la url "+url)  
       except Exception as ex:
          print(ex)
          logger.error("Error al insertar publicación de url "+url, exc_info=True)


@client.on(events.NewMessage(chats=user_input_channel))
async def newMessageListener(event):
    try:
     logger.info(f"Entra mensaje ")
     newMessage=event.message.message
    
     if event.message.media.webpage:
      logger.info(f"Mensaje con contenido web  ")  
      countersBot=Counters.objects().first()
    
      if countersBot:
       if countersBot.lastPublicationDayTelegram and countersBot.lastPublicationDayTelegram.strftime("%d/%m/%Y")!=datetime.now().strftime("%d/%m/%Y"):
         countersBot.publicationsTelegramDay=0
         countersBot.lastPublicationDayTelegram=datetime.now
         countersBot=countersBot.save()

      if not countersBot or not (countersBot.publicationsTelegramDay and 
                                 optionsTelegram.maxCatchNumber and 
                                 countersBot.lastPublicationDayTelegram and 
                                 countersBot.publicationsTelegramDay>=optionsTelegram.maxCatchNumber 
                                 and countersBot.lastPublicationDayTelegram.strftime("%d/%m/%Y")==datetime.now().strftime("%d/%m/%Y")):
        catchWebPage(event.message.media.webpage)
      else:
        logger.info(f"Excedido límite de publicaciones diarias  ")  

    except:
      logger.error(f"Error obteniendo información del evento ", exc_info=True)

with client:
    print('inicio')
    client.run_until_disconnected()


 
