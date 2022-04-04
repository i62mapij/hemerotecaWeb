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
import re
import requests
from logging.handlers import RotatingFileHandler

#bot that fetches publications from direct message urls, mentions, or replies 
# to the twitter user logged into the app

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

logFile = './log/hemerotecaWebTwitterBot.log'

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=10, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

logger = logging.getLogger('root')
logger.setLevel(logging.INFO)

logger.addHandler(my_handler)

def create_api():
    connect('hemeroteca')
    parametersTwitter = ParametersTwitter.objects().first()
    auth = tweepy.OAuthHandler(parametersTwitter.consumerKey, parametersTwitter.consumerSecret) 
    auth.set_access_token(parametersTwitter.accessToken, parametersTwitter.accessTokenSecret)
    api = tweepy.API(auth,wait_on_rate_limit=True)

    try:
        connectedUser=api.verify_credentials()
    except Exception as exc:
        logger.error("Error creando objeto API", exc_info=True)
        raise exc
    logger.info("Objeto API creado")

    return connectedUser,api

class ParametersTwitter(Document):
    __tablename__ = 'ParametersTwitter'
    _id = ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    consumerKey = StringField(max_length=400, required=True)
    consumerSecret = StringField(max_length=400, required=True)
    accessToken = StringField(max_length=400, required=True)
    accessTokenSecret = StringField(max_length=400, required=True)

class Counters(Document):
    __tablename__ = 'Counters'
    _id = ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    lastDMTwitterId = StringField(max_length=100)
    lastReplieTwitterId = StringField(max_length=100)
    publicationsTwitterDay =  IntField()
    lastPublicationDayTwitter = DateTimeField()
    publicationsTelegramDay =  IntField()
    lastPublicationDayTelegram = DateTimeField()

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

class BotTwitter(Document):
    __tablename__ = 'BotTwitter'
    _id = ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    maxCatchNumber = IntField()
    pid = IntField()
    
class TwitterBot():
 urlsArray=[]
 urlsAccount=[]
 connectedUser,api=create_api()
 meScreenName=connectedUser.screen_name
 counters = None
 parametersTwitterBot=None

 def getUrlsFromReplies(self):
     logger.info("Obtención de publicaciones en réplicas") 
     try:
      if self.counters and self.counters.lastReplieTwitterId:
       since_id=self.counters.lastReplieTwitterId
      else:
       since_id=None
      
      lastReplieTwitterId="0"
      logger.info("Llama a Twitter para obtener réplicas al usuario "+self.meScreenName) 
      for tweet in tweepy.Cursor(self.api.home_timeline, screen_name=self.meScreenName, since_id=since_id,tweet_mode="extended").items():
       
       if lastReplieTwitterId=="0":
        lastReplieTwitterId=str(tweet.id)
                           
       if tweet.in_reply_to_screen_name==self.meScreenName or (tweet.full_text and self.meScreenName in tweet.full_text):
      
        for url in tweet.entities['urls']:
          if 'twitter' not in url['expanded_url']:
           logger.info(f"Guarda url de tweet "+url['expanded_url'])
           self.urlsArray.append(url['expanded_url'])
           self.urlsAccount.append(tweet.user.screen_name)
      
      if lastReplieTwitterId!="0":
       logger.info("Actualiza contadores") 
       if self.counters:  
             self.counters.lastReplieTwitterId=lastReplieTwitterId
             self.counters=self.counters.save()
       else:
             self.counters=Counters(lastReplieTwitterId=lastReplieTwitterId)
             self.counters=self.counters.save()

     except:
          logger.error("Error al obtener urls de tweets", exc_info=True)

 def insertPublicationFromURL(self,url,urlAccount):
       try:
        logger.info(f"Procesa url "+url)
        classUrlToObject=urlToObject.UrlToObject()
        objectPage=classUrlToObject.getDataFromWebPage(url,urlAccount,'Twitter')
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
                publication = Publications(title = objectPage["title"], summary = objectPage["summary"], text = objectPage["text"], url = url, screen_name = urlAccount, channel = '', image = image, type='Twitter', webDate = webDate)
                publication.save()
        
         if self.counters:
          if self.counters.publicationsTwitterDay:
           self.counters.publicationsTwitterDay=self.counters.publicationsTwitterDay+1
          else:
           self.counters.publicationsTwitterDay=1 
          self.counters.lastPublicationDayTwitter=datetime.now
          self.counters=self.counters.save()
         else:
          self.counters=Counters(publicationsTwitterDay=1,lastPublicationDayTwitter=datetime.now)
          self.counters=self.counters.save()

        else:
          logger.info(f"No almacena publicación de la url "+url)  
       except Exception as ex:
          logger.error("Error al insertar publicación de url "+url, exc_info=True)

 def getUrlsFromDirectMessages(self):
     try:
      logger.info("Obteniendo mensajes directos") 
      directsMessages = tweepy.Cursor(self.api.get_direct_messages, count=50).items()
      meUserObject = self.api.get_user(screen_name=self.meScreenName)
      lastDMTwitterId="0"
      
      for message in directsMessages:
       logger.info("Procesa mensaje directo") 
       if lastDMTwitterId=="0":
        lastDMTwitterId=str(message.id)
      
       if self.counters and self.counters.lastDMTwitterId and str(message.id)<=self.counters.lastDMTwitterId:
           logger.info("Mensaje ya procesado") 
           break

       idUser = message.message_create['sender_id']
       userObject = self.api.get_user(user_id=idUser)
       if idUser!=userObject.id:
        logger.info("Va a obtener urls del mensaje") 
        for url in message.message_create['message_data']["entities"]["urls"]:
  
            logger.info(f"Guarda url de DM "+url['expanded_url'])
            self.urlsArray.append(url['expanded_url'])
            self.urlsAccount.append(userObject.screen_name)
       
      
      if lastDMTwitterId!="0":
       logger.info("Actualiza contadores") 
       if self.counters:
        self.counters.lastDMTwitterId=lastDMTwitterId
        self.counters=self.counters.save() 
       else:
        self.counters=Counters(lastDMTwitterId=lastDMTwitterId)
        self.counters=self.counters.save()
             
     except:
          logger.error("Error al obtener urls de mensajes directos", exc_info=True)

 def process(self):
      try:
        if self.counters and  self.counters.lastPublicationDayTwitter and self.counters.lastPublicationDayTwitter.strftime("%d/%m/%Y")!=datetime.now().strftime("%d/%m/%Y"):
            logger.info("Actualiza contador y fecha") 
            self.counters.lastPublicationDayTwitter = datetime.now()
            self.counters.publicationsTwitterDay = 0    
            self.counters.save()

        if self.counters and self.counters.publicationsTwitterDay and self.parametersTwitterBot and self.parametersTwitterBot.maxCatchNumber and self.counters.publicationsTwitterDay>=self.parametersTwitterBot.maxCatchNumber and self.counters.lastPublicationDayTwitter.strftime("%d/%m/%Y")==datetime.now().strftime("%d/%m/%Y"):
            logger.info("Límite de publicaciones en el día alcanzado") 
            return

        logger.info("Inicio lectura de envíos en Twitter") 
        self.getUrlsFromReplies()
        self.getUrlsFromDirectMessages()

        for url, urlAccount in zip(self.urlsArray,self.urlsAccount):
            logger.info("Va a insertar publicación") 
            self.insertPublicationFromURL(url,urlAccount)
      except:
          logger.error("Error generarl en proceso", exc_info=True)

      return True 

def main():
 while True:
  logger.info("Inicio proceso de búsqueda")
  twitterBot=TwitterBot()
  twitterBot.counters = Counters.objects().first()
  logger.info("Lectura de parámetros")
  twitterBot.parametersTwitterBot=BotTwitter.objects().first()
  twitterBot.urlsArray=[]
  twitterBot.urlsAccount=[]

  twitterBot.process() 
  logger.info("Espera de 2 minutos")   
  time.sleep(120)

if __name__ == '__main__':
    main()

