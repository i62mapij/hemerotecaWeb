#from hemerotecaApp import app
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort
from datetime import datetime
from sqlalchemy.sql.expression import not_,or_
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, IntegerField
from wtforms.fields import DateField
from wtforms.validators import InputRequired, NumberRange
import json
from hemerotecaApp.catches.model.publication import Publications

from flask_login import login_required
from flask_user import roles_required

from hemerotecaApp import app


publication = Blueprint('publication',__name__)

import time

#all roles allowed
@publication.before_request
@login_required
@roles_required(['Consulta','Admin','Superadmin']) 
def constructor():
   pass


@publication.route('/index')
def index(page=1):
   return render_template('catches/webCatch.html')

@publication.route('/webCatch')
def webCatch(page=1):
   return render_template('catches/webCatch.html')

@publication.route('/twitterCatch')
def twitterCatch(page=1):
   return render_template('catches/twitterCatch.html')

@publication.route('/telegramCatch')
def telegramCatch(page=1):
   return render_template('catches/telegramCatch.html')

#class for search form
class SearchesForm(FlaskForm):
    type = SelectField('Tipo', choices=[('', ''),('Telegram', 'Telegram'),('web', 'Web'), ('Twitter', 'Twitter')])
    tag = StringField('Contenido en notas')
    title = StringField('Contenido en titulo')
    text = StringField('Contenido en texto')
    fromDate = DateField('Fecha de captura desde', format='%m/%d/%Y')
    toDate = DateField('hasta', format='%m/%d/%Y')
    hasImage = BooleanField('Tiene imagen')
    automatic =  SelectField('Tipo de captura', choices=[('', ''),('M', 'Manual'),('A', 'Automática')])
    fromWebDate = DateField('Fecha de publicación desde', format='%m/%d/%Y')
    toWebDate = DateField('hasta', format='%m/%d/%Y')
    
#method to display search screen	
@publication.route('/searches')
def searches():
   form = SearchesForm(meta={'csrf':False})
   return render_template('searches/searches.html',form=form)

#method to display publicacion listing screen
@publication.route('/search', methods=('GET', 'POST'))
def search(): 
   firstpage = 'S'
   hasImage = 'N'
   if request.method == 'POST':
      firstpage='N'
      if 'hasImage' in request.form:
       hasImage='Y'

      publicationsearch= {'type': request.form['type'],
                  'tag': request.form['tag'],
                  'title':request.form['title'],
                  'text':request.form['text'],
                  'fromDate': request.form['fromDate'],
                  'toDate':request.form['toDate'],
                  'fromWebDate': request.form['fromWebDate'],
                  'toWebDate':request.form['toWebDate'],
                  'hasImage': hasImage,
                  'automatic': request.form['automatic']
            }
   else:
       publicationsearch= {'type': '','tag': '',
                  'title':'',
                  'text':'',''
                  'fromDate': '',
                  'toDate':'',
                  'fromWebDate': '',
                  'toWebDate':'',
                  'hasImage': '',
                  'automatic': ''
            }

   return render_template('searches/publicationsList.html',publicationsearch=json.dumps(publicationsearch),firstpage=firstpage)


#method to show statistics screen
@publication.route('/dataPanel')
def dataPanel():
   now = datetime.now() 

   publicationsWeb=Publications.objects(type='web')
   publicationsTwitter=Publications.objects(type='Twitter')
   publicationsTelegram=Publications.objects(type='Telegram')

   statisticalData= {'web': publicationsWeb.count(),
                  'twitter':publicationsTwitter.count(),
                  'telegram': publicationsTelegram.count()
   }

   return render_template('statistics/dataPanel.html',time=now.strftime("%d/%m/%Y a las %H:%M:%S"), statisticalData=statisticalData)
