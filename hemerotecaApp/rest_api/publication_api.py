from flask.helpers import url_for
from flask.views import MethodView
from flask import request
from hemerotecaApp.rest_api.helper.request import sendResJson
from hemerotecaApp import app
import sys, os
from hemerotecaApp.urlsMapper import urlToObject 
from flask_httpauth import HTTPTokenAuth
from hemerotecaApp.auth.model.user import User
from hemerotecaApp.catches.model.publication import Publications,Notes
from hemerotecaApp import user_manager
from flask_login import  current_user
import bson
from urllib.request import urlopen
from hemerotecaApp.configuration.model.parameters import ParametersTwitter
import tweepy 
import re
import json
import tempfile
import mimetypes
import base64
from base64 import b64encode
import requests
import validators
from mongoengine.queryset.visitor import Q
from datetime import datetime
import traceback

#token protected APIs
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    if  not User.verify_auth_token(token):
        return False
    
    return True

#class to update publications
class SavePublication():
    def savePublication(self, id,title,summary,text,url,notes,screen_name,channel, image, webDate, publication,type):
        if id!='':
                 publication = Publications(_id=bson.objectid.ObjectId(id),title = title, summary = summary, text = text, url = url, screen_name = screen_name, notes = publication.notes, channel = channel, image = image, type=type,webDate=webDate)
        else:
                 notesList = []
                 if notes!='':
                  notesObj=Notes(text=notes)
                  notesList.append(notesObj)
                  notesObj.save()
		
                 user=current_user._id  
                 publication = Publications(title = title, summary = summary, text = text, url = url, screen_name = screen_name, notes = notesList, channel = channel, image = image, type=type,webDate=webDate,user=user)
                
        publication.save()
        return publication

#api that manages the operations with publications
class PublicationApi(MethodView):
    
    #obtain de publications list
    @auth.login_required
    def get(self, type=None, page=1):
            res = []
            resJson = []
            try:
             res=Publications.objects(type=type).order_by('-_id').paginate(page,25)

             for result in res.items:
              
              resJson.append(transformPublicationJson(result))

             resJson.append(createObjectPaginationJson(res.pages, page))
            
             return sendResJson(resJson,None,200)
            except Exception as e:
             print(type)
             return sendResJson(None,'Se ha producido un error al obtener las publicaciones#'+ traceback.format_exc(),240)

    #get list of posts with filter
    @auth.login_required
    def post(self, type=None, page=1):
        res = []
        resJson = []
        try:
            #filters
            if type==None or type=='':
             if request.form['text']!='':
              qText=Q(text__contains=request.form['text'])
             else:
              qText=Q()

             if request.form['title']!='':
              qTitle=Q(title__contains=request.form['title'])
             else:
              qTitle=Q()
            
             if request.form['type']!='':
              qType=Q(type=request.form['type'])
             else:
              qType=Q()
            
             if request.form['tag']!='':
              qNotesId=Q(text__contains=request.form['tag'])
              idsNotes=Notes.objects(qNotesId).scalar('_id')
              qTag=Q(notes__in=idsNotes)
             else:
              qTag=Q()
             
            
             if request.form['fromDate']!='':
              fromDate = request.form['fromDate'].split('-')
              qFromDate=Q(date__gte=datetime(int(fromDate[0]),int(fromDate[1]),int(fromDate[2]),23,59))
             else:
              qFromDate=Q()

             if request.form['toDate']!='':
              toDate = request.form['toDate'].split('-')
              qToDate=Q(date__lte=datetime(int(toDate[0]),int(toDate[1]),int(toDate[2]),23,59))
             else:
              qToDate=Q()

             if request.form['fromWebDate']!='':
              fromWebDate = request.form['fromWebDate'].split('-')
              qFromWebDate=Q(webDate__gte=datetime(int(fromWebDate[0]),int(fromWebDate[1]),int(fromWebDate[2])))
             else:
              qFromWebDate=Q()

             if request.form['toWebDate']!='':
              toWebDate = request.form['toWebDate'].split('-')
              qToWebDate=Q(webDate__lte=datetime(int(toWebDate[0]),int(toWebDate[1]),int(toWebDate[2],23,59)))
             else:
              qToWebDate=Q()

            if type==None or type=='':
             if request.form['hasImage']=='Y':
              qHasImage=Q(image__exists=True)
             else:
              qHasImage=Q()

             res=Publications.objects(qText & qTitle & qType & qTag & qFromDate & qToDate & qFromWebDate & qToWebDate & qHasImage).order_by('-_id').paginate(page,25)
            else:
             res=Publications.objects(type=type).order_by('-_id').paginate(page,25)

            for result in res.items:
             resJson.append(transformPublicationJson(result))

            resJson.append(createObjectPaginationJson(res.pages, page))
            
            return sendResJson(resJson,None,200)
        except Exception as e:
            return sendResJson(None,'Se ha producido un error al obtener las publicaciones#'+ traceback.format_exc(),250)   
    
    #add a publication
    @auth.login_required
    def put(self):
        errorMessage=''
        try:
            title=request.form['title']
            summary=request.form['summary']
            text=request.form['text']
            url=request.form['url']
            screen_name=request.form['screen_name']
            notes=request.form['notes']
            date=request.form['date']
            webDate=request.form['webDate']

            id=request.form['id']
            channel=''
            publication = Publications.objects(url=url).first()
            if publication and id=='':
                errorMessage='La publicación ya está registrada en el sistema'
                raise Exception

            type=request.form['type']
            try:
             webDate=datetime.strptime(webDate, '%d/%m/%Y')
            except Exception as exc:
             webDate=None
		  
            savePublicationObj=SavePublication()

            if request.form['image']!='':
                if validators.url(request.form['image']):
                 file_like =  requests.get(request.form['image']).content
                else:
                 file_like = base64.b64decode(request.form['image'].split(',')[1])
                bytes_image = bytearray(file_like)
                            
                with tempfile.TemporaryFile() as f:
                    f.write(bytes_image)
                    f.flush()
                    f.seek(0)
                    image=f
                    publication=savePublicationObj.savePublication(id,title,summary,text,url,notes,screen_name,channel, image, webDate,publication,type)
            else:
              publication=savePublicationObj.savePublication(id,title,summary,text,url,notes,screen_name,channel, None, webDate,publication,type)
          
            return sendResJson(transformPublicationJson(publication),None,200)
        except Exception as e:
            if errorMessage=='':
             errorMessage='Se ha producido un error al guardar la publicación#'+ traceback.format_exc()

            return sendResJson(None,errorMessage,230)

    #delete publication
    @auth.login_required
    def delete(self):
        try:
         id=request.form['id']
         publications=Publications.objects(_id=bson.objectid.ObjectId(id))
         if publications.count()>0:

          if publications[0].notes:
           for note in publications[0].notes:
            note.delete()
          publications[0].delete()
          return sendResJson(None,None,200)
        except Exception as e:
          return sendResJson(None,"Se ha producido un error al eliminar la publicación#"+ traceback.format_exc(),220)

#method that transforms a publication to json        
def transformPublicationJson(publication):
    image=''
    if publication.image:
     image='data:image/'+publication.image.format+';base64,'+b64encode(publication.image.read()).decode("utf-8") 
        
    return {
                'id': str(publication._id),
                'title': publication.title,
                'date':publication.date.strftime("%d/%m/%Y"),
                'url':publication.url,
                'webDate':publication.webDate.strftime("%d/%m/%Y"),
                'notes':'',
                'type': publication.type,
                'text': publication.text,
                'screen_name': publication.screen_name,
                'channel': publication.channel,
                'summary':publication.summary,
                'image': image
           }
#method that transforms a note to json
def transformNoteJson(note):

    return {
                'id': str(note._id),
                'text': note.text,
                'date':note.date.strftime("%d/%m/%Y")
           }

#api that manages the notes
class NotesApi(MethodView):
    @auth.login_required
    def get(self, idPublication):
            res = []
            resJson = []
            try:
             res=Publications.objects(_id=bson.objectid.ObjectId(idPublication)).first().notes
             for result in res:
              resJson.append(transformNoteJson(result))
         
             return sendResJson(resJson,None,200)
            except Exception as e:
             return sendResJson(None,'Se ha producido un error al obtener las notas de la publicación#'+ traceback.format_exc(),240)
    
    def delete(self, idNote, idPublication):
        try:
         
         publication=Publications.objects(_id=bson.objectid.ObjectId(idPublication)).first()
         notes=publication.notes
         newNotes=[]
         for noteAux in notes:
            if str(noteAux._id)!=idNote:
             newNotes.append(noteAux)
          
         publication.update(notes=newNotes)
         note=Notes.objects(_id=bson.objectid.ObjectId(idNote)).first()
         note.delete()

         return sendResJson(None,None,200)
        except Exception as e:
          return sendResJson(None,"Se ha producido un error al eliminar la nota#"+ traceback.format_exc(),220)
         
    def put(self):
        errorMessage=''
        try:
            text=request.form['text']
            idPublication=request.form['idPublication']
        
            publication = Publications.objects(_id=bson.objectid.ObjectId(idPublication)).first()
            note=Notes(text=text)
            note.save()
            notes=publication.notes
            notes.append(note)
            publication.update(notes=notes)
              
            return sendResJson(None,None,200)
        except Exception as e:
            if errorMessage=='':
             errorMessage='Se ha producido un error al guardar la nota#'+ traceback.format_exc()

            return sendResJson(None,errorMessage,230)

#api that handles publications capture
class CatchPublicationApi(MethodView):
    #method that obtains the elements of a publication from the url
    @auth.login_required
    def post(self, type=None, page=1):
        try:
            type=request.form['type']
            res=[]
            classUrlToObject=urlToObject.UrlToObject()
            screen_name=''
            if 'screen_name' in request.form:
             screen_name=request.form['screen_name']
            
            publication = classUrlToObject.getDataFromWebPage(request.form['url'],screen_name,type)
            res.append(publication)       
            return sendResJson(res,None,200)
        except urlToObject.ForbidedError as forEx:
            return sendResJson(None,str(forEx),403)
        except Exception as e:
            return sendResJson(None,"Se produjo un error al obtener contenido de la página web#"+ traceback.format_exc(),210)

#class that handles fetching tweets from Twitter         
class TwitterApi(MethodView):
    @auth.login_required
    def get(self, screen_name=None):
        res = [] 
        errorMessage=''

        try:
            parametersTwitter = ParametersTwitter.objects().first()

            if not parametersTwitter:
              errorMessage='Se ha producido un error al obtener los tuits. No se encontraron los parámetros de conexión con Twitter'
              raise Exception

            if not parametersTwitter.consumerKey or not parametersTwitter.consumerSecret or not parametersTwitter.accessToken or not parametersTwitter.accessTokenSecret:
              errorMessage='Alguno de los parámetros de conexión con Twitter no existe en el sistema'
              raise Exception
 
            auth = tweepy.OAuthHandler(parametersTwitter.consumerKey, parametersTwitter.consumerSecret) 
        
            try:
             auth.set_access_token(parametersTwitter.accessToken, parametersTwitter.accessTokenSecret)
             api = tweepy.API(auth)
            except:
             errorMessage='Error al autenticarse en Twitter. Revise los parámetros de conexión introducidos en el sistema'
             raise Exception
            tweets=[]

            try:
             tweets = api.user_timeline(screen_name=screen_name, 
                           count=20,
                           include_rts = False,
                           tweet_mode = 'extended'
                           )
            except tweepy.errors.NotFound as ex:
                 errorMessage='El usuario introducido no existe en Twitter'
                 raise ex
            except Exception as exGen:  
                 raise exGen

            for tweet in tweets:  
              imageUrl=getImageFromTweet(tweet)
              if imageUrl!=None:
               
               response = requests.get(imageUrl)
               content_type = response.headers['content-type']
               extension = mimetypes.guess_extension(content_type)            
               imageBase64= 'data:image/'+extension+';base64,'+b64encode(urlopen(imageUrl).read()).decode("utf-8") 
              else:
               imageBase64=None   
              
              url=getURLFromTweet(tweet)
              if url: 
               text = re.sub(r"http\S+", url, tweet.full_text, flags=re.MULTILINE)
              else:
               if 'https://' in  tweet.full_text:
                text = re.sub(r"http\S+", '', tweet.full_text, flags=re.MULTILINE)
               else:
                text = tweet.full_text
              res.append(createTuitJson(tweet.id, text, tweet.created_at.strftime("%d/%m/%Y"),imageBase64,url=url, screen_name=screen_name))
          
            return sendResJson(res,None,200)
        except Exception as e:
            if errorMessage=='':
             errorMessage='Se ha producido un error al obtener los tuits#'+ traceback.format_exc()

            return sendResJson(None,errorMessage,260)

#method that gets the images from a Tweet object
def getImageFromTweet(status):
        if 'media' in status.entities:
            for image in  status.entities['media']:
                link = image['media_url']
                return link             

#method that gets the urls of a tweet object
def getURLFromTweet(tweet):
        for url in tweet.entities['urls']:
          return url['expanded_url']
           
#api for obtaining token
class TokenApi(MethodView):
    def get(self, id=None):
        try:
         token=User.generate_auth_token(User)

         res = {'token':token}
        except Exception as ex:
         return sendResJson(None,'',210)

        return sendResJson(res,None,200)
#method to create the pagination object into json
def createObjectPaginationJson(pages, current):
    return {
                'pages': pages,
                'current': current
           }
#method to create the tweet object into json
def createTuitJson(id, text, date, image,url,screen_name):
    return {
                'id': id,
                'text': text,
                'date':date,
                'image':image,
                'url':url,
                'screen_name':screen_name
           }           
#API mapping
publication_view = PublicationApi.as_view('publication_view')
app.add_url_rule('/api/publications/<string:type>/<int:page>',
view_func=publication_view,
methods=['GET'])

app.add_url_rule('/api/publications/<int:page>',
view_func=publication_view,
methods=['POST'])

app.add_url_rule('/api/publication/<int:id>',
view_func=publication_view,
methods=['GET'])

app.add_url_rule('/api/publication/',
view_func=publication_view,
methods=['PUT','DELETE'])

token_view = TokenApi.as_view('token_view')
app.add_url_rule('/api/getToken',
view_func=token_view,
methods=['GET'])

notes_view = NotesApi.as_view('notes_view')
app.add_url_rule('/api/notes/<string:idPublication>',
view_func=notes_view,
methods=['GET'])

app.add_url_rule('/api/notes/<string:idNote>/<string:idPublication>',
view_func=notes_view,
methods=['DELETE'])

app.add_url_rule('/api/notes/',
view_func=notes_view,
methods=['PUT'])

twitter_view = TwitterApi.as_view('tuits_view')
app.add_url_rule('/api/tuits/<string:screen_name>',
view_func=twitter_view,
methods=['GET'])

catchpublication_view = CatchPublicationApi.as_view('catchpublication_view')
app.add_url_rule('/api/catchPublication',
view_func=catchpublication_view,
methods=['POST'])

