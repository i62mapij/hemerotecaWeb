import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages,send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort
from datetime import datetime
from sqlalchemy.sql.expression import not_,or_
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, IntegerField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, NumberRange
from wtforms import ValidationError, validators
import json
import sys
import signal
import psutil
from pathlib import Path

import bson

import subprocess
from hemerotecaApp import app
from hemerotecaApp.configuration.model.parameters import ParametersTelegram, ParametersTwitter, ParametersTwitterForm, ParametersTelegramForm
from hemerotecaApp.configuration.model.botsAdmin import BotTelegram, BotTwitter

from flask_login import login_required
from flask_user import roles_required
import time
from os import environ
import sys
configurationController = Blueprint('configurationController',__name__)

#admin role required for use this controller
@configurationController.before_request
@login_required
@roles_required(['Admin','Superadmin']) 
def constructor():
   pass

class ParametersTwitterError(Exception):
    pass

class ParametersTelegramError(Exception):
    pass

#method to update twitter parameters
@configurationController.route('/parametersTwitter', methods=('GET', 'POST'))
def parametersTwitter():
 form = ParametersTwitterForm(meta={'csrf':False})
 errorMessage=''
 try:  
   if form.validate_on_submit():
    consumerKey = request.form['consumerKey']
    consumerSecret = request.form['consumerSecret']
    accessToken = request.form['accessToken']
    accessTokenSecret = request.form['accessTokenSecret']
    id = request.form['id']
    
    try:
     if id!='':
      parameters = ParametersTwitter(_id=bson.objectid.ObjectId(id),consumerKey=consumerKey, consumerSecret=consumerSecret, accessToken=accessToken, accessTokenSecret=accessTokenSecret)
     else:
      parameters = ParametersTwitter(consumerKey=consumerKey, consumerSecret=consumerSecret, accessToken=accessToken, accessTokenSecret=accessTokenSecret)
  
     parameters.save()

     flash("Parámetros creados con éxito")
     return redirect(url_for('configurationController.parametersTwitter'))
    except:
      errorMessage='Se produjo un error al guardar los parámetros'
      raise
   else:
    #if the parameters were already filled in, they are shown in the form
    try:
     parameters = ParametersTwitter.objects()
     if parameters.count()>0:
      form.consumerKey.default=parameters[0].consumerKey
      form.consumerSecret.default=parameters[0].consumerSecret
      form.accessToken.default=parameters[0].accessToken
      form.accessTokenSecret.default=parameters[0].accessTokenSecret
      form.id.default=parameters[0]._id
      form.process()

     if form.errors:
      flash(form.errors,'')
    except:
      errorMessage='Se produjo un error al obtener los parámetros'
      raise
 except:
      if errorMessage=='':
        errorMessage='Se produjo un error al cargar la página'

      flash(errorMessage,'danger')

 return render_template('configuration/parametersTwitter.html',form=form)

#method to update telegram parameters
@configurationController.route('/parametersTelegram', methods=('GET', 'POST'))
def parametersTelegram():
   form = ParametersTelegramForm(meta={'csrf':False})
   errorMessage=''
   
   try:
    if form.validate_on_submit():
     apiId = request.form['apiId']
     apiHash = request.form['apiHash']
     applicationName = request.form['applicationName']

     id = request.form['id']
     
     try:
      if id!='':
       parameters = ParametersTelegram(_id=bson.objectid.ObjectId(id),apiId=apiId,apiHash=apiHash,applicationName = applicationName)
      else:
       parameters = ParametersTelegram(apiId=apiId,apiHash=apiHash,applicationName = applicationName)
  
      parameters.save()

      flash("Parámetros creados con éxito")
      return redirect(url_for('configurationController.parametersTelegram'))
     except:
        errorMessage='Se produjo un error al guardar los parámetros'
        raise
    else:
     try:
      parameters = ParametersTelegram.objects()
      if parameters.count()>0:
       form.apiId.default=parameters[0].apiId
       form.apiHash.default=parameters[0].apiHash
       form.applicationName.default=parameters[0].applicationName

       form.id.default=parameters[0]._id
       form.process()

      if form.errors:
        flash(form.errors,'')
    
      
     except:
       errorMessage='Se produjo un error al obtener los parámetros'
       raise

   except Exception as ex:
    if errorMessage=='':
      errorMessage='Se produjo un error al cargar la página'

    flash(errorMessage,'danger')
    return render_template('configuration/parametersTelegram.html',form=form)
   
   return render_template('configuration/parametersTelegram.html',form=form)
  
#method to check the bot state
def testBot(parameters):
    retorno = 'B'
    if parameters and parameters[0].pid:
       try:
        os.kill(parameters[0].pid, 0)
        proc = psutil.Process(parameters[0].pid)
        if proc.status() == psutil.STATUS_ZOMBIE:
         retorno='B'
        else:
         retorno='A'
       except OSError:
        retorno='B'
    else:
       retorno = 'B'    

    return retorno


#method to start the twitter bot
def runBotTwitterProcess(parameters): 

   parametersTwitter = ParametersTwitter.objects()
   if parametersTwitter.count()==0:
    raise ParametersTwitterError('Es necesario introducir los parámetros de conexión a Twitter de la aplicación')
   
   my_env = os.environ.copy()
   process = subprocess.Popen([sys.executable,'../bots/twitterBot.py'], env = my_env, shell = False, stdout = subprocess.PIPE, stderr = subprocess.PIPE,cwd='/root/hemerotecaWeb/hemerotecaApp/bots/')
   
   if process.pid:
      if parameters:
       parameters = BotTwitter(_id=bson.objectid.ObjectId(parameters[0]._id),pid=process.pid, maxCatchNumber=parameters[0].maxCatchNumber)
      else:
       raise ParametersTelegramError('Es necesario introducir el canal de Telegram') 

      parameters.save()
      
      return 'A'
   else:
      return 'B' 

#method to stop the twitter bot
def stopBotTwitterProcess(parameters):
   if parameters[0].pid!=0:
    os.kill(parameters[0].pid, signal.SIGTERM) 
   return 'B'

      
#method to manage the twitter bot
@configurationController.route('/configureBotTwitter', methods=('GET', 'POST'))
def configureBotTwitter():
   errorMessage=''
   try:
    form = ConfigureBotForm(meta={'csrf':False})
   
    formid = request.args.get('formid', 1, type=int)

    if formid==1 and form.validate_on_submit():
     maxCatchNumber = request.form['maxCatchNumber']
     id = request.form['id']
    
     try:
      if id!='':
       parameters = BotTwitter.objects().first()
       parameters = BotTwitter(_id=bson.objectid.ObjectId(id),maxCatchNumber=maxCatchNumber, pid=parameters.pid)
      else:
       parameters = BotTwitter(maxCatchNumber=maxCatchNumber)
  
      parameters.save()

      flash("Parámetros creados con éxito")
      return redirect(url_for('configurationController.configureBotTwitter'))
     except:
        errorMessage='Error al guardar los datos de configuración del proceso'
        raise
    else:
     try:
      parameters = BotTwitter.objects()
      if parameters.count()>0:
       form.maxCatchNumber.default=parameters[0].maxCatchNumber
       form.id.default=parameters[0]._id
       form.process()
     
      if formid==2:
       botState=testBot(parameters)
       if botState=='A':
        botState=stopBotTwitterProcess(parameters)  
       else:
        botState=runBotTwitterProcess(parameters)
      else:
        botState=testBot(parameters)

      if form.errors:
        flash(form.errors,'')
     except ParametersTwitterError as errPar:
       errorMessage=str(errPar)
       raise errPar
     except:
       errorMessage='Error al obtener datos de configuración del proceso'
       raise
   except:
      if errorMessage=='':
         errorMessage='Error al cargar la página'
      flash(errorMessage,'danger')
   
   files=getLogFilesList()
   return render_template('bots/botTwitter.html',form=form, botState=botState, files=files)

#get the list of log files
def getLogFilesList():
 files=[]
 for child in Path('./hemerotecaApp/bots/log').iterdir():
    if child.is_file():
     if 'Twitter' in child.name:
      files.append(child.name)
 return files

#method to run de telegram bot
def runBotTelegramProcess(parameters):

   parametersTelegram = ParametersTelegram.objects()
   if parametersTelegram.count()==0:
    raise ParametersTelegramError('Es necesario introducir los parámetros de conexión a Telegram de la aplicación')
   
   my_env = os.environ.copy()
   process = subprocess.Popen([sys.executable,'../bots/telegramBot.py'], env = my_env, shell = False, stdout = subprocess.PIPE, stderr = subprocess.PIPE,cwd='/root/hemerotecaWeb/hemerotecaApp/bots/')
   
   if process.pid:
      if parameters:
       parameters = BotTelegram(_id=bson.objectid.ObjectId(parameters[0]._id),pid=process.pid, channel = parameters[0].channel, maxCatchNumber=parameters[0].maxCatchNumber)
      else:
       raise ParametersTelegramError('Es necesario introducir el canal de Telegram')    

      parameters.save()
      
      return 'A'
   else:
      return 'B' 

#method to stop telegram bot
def stopBotTelegramProcess(parameters):
   if parameters[0].pid!=0:
       try:
         p=psutil.Process(parameters[0].pid)
         p.terminate()
         
       except:
         print('error al parar')
   
   return 'B'


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename): 
    return send_from_directory('./bots/log', filename)
    
#method to manage the telegram bot
@configurationController.route('/configureBotTelegram', methods=('GET', 'POST'))
def configureBotTelegram():
   errorMessage=''
   try:
    form = ConfigureBotForm(meta={'csrf':False})
   
    formid = request.args.get('formid', 1, type=int)

    if formid==1 and form.validate_on_submit():
     channel = request.form['channel']
     maxCatchNumber = request.form['maxCatchNumber']
     if channel=='':
      flash('El canal es obligatorio','danger')
      return redirect(url_for('configurationController.configureBotTelegram'))
     
     try:
      id = request.form['id']
    
      if id!='':
       parameters = BotTelegram.objects().first()
       parameters = BotTelegram(_id=bson.objectid.ObjectId(id),maxCatchNumber=maxCatchNumber,channel=channel, pid=parameters.pid)
      else:
       parameters = BotTelegram(maxCatchNumber=maxCatchNumber,channel=channel)
  
      parameters.save()

      flash("Parámetros creados con éxito")
      return redirect(url_for('configurationController.configureBotTelegram'))
     except:
      errorMessage='Error al guardar parámetros del proceso'  
      raise
    else:
     try:
      parameters = BotTelegram.objects()
      if parameters.count()>0:
       form.maxCatchNumber.default=parameters[0].maxCatchNumber
       form.channel.default=parameters[0].channel

       form.id.default=parameters[0]._id
       form.process()

      if formid==2:
        botState=testBot(parameters)
        if botState=='A':
         botState=stopBotTelegramProcess(parameters)  
        else:
         botState=runBotTelegramProcess(parameters)
      else:
        botState=testBot(parameters)
     except ParametersTelegramError as errPar:
       errorMessage=str(errPar)
       raise errPar
     except:
      errorMessage='Error al obtener parámetros del proceso'  
      raise
   except:
      if errorMessage=='':
         errorMessage='Error al cargar la página'
      flash(errorMessage,'danger')
   
   files=getLogFilesList()
   
   return render_template('bots/botTelegram.html',form=form, botState=botState, files=files)

#class for bot configuration forms
class ConfigureBotForm(FlaskForm):
    channel = StringField('Canal de captura')
    maxCatchNumber = IntegerField('Límite de capturas por día') 
    id=HiddenField("id")


