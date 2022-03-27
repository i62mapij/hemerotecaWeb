#from hemerotecaApp import app
from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from werkzeug.exceptions import abort

from flask_login import login_required
from flask_user import roles_required
from flask_user.forms import ChangeUsernameForm

from hemerotecaApp import app, dbMongo
from hemerotecaApp.auth.model.user import User, RegisterForm
from hemerotecaApp.auth.model.userModel import UpdateForm
from hemerotecaApp import user_manager
import bson
from collections import namedtuple

from mongoengine import errors

userBp = Blueprint('useradmin',__name__)

@userBp.before_request
@login_required
@roles_required(['Superadmin']) 
def constructor():
   pass


@userBp.route('/dashboard/user')
@userBp.route('/dashboard/user/<int:page>')
def index(page=1):
   
   users = User.objects().paginate(page=page, per_page=10)
   return render_template('dashboard/user/index.html', users=users)


@userBp.route('/dashboard/user/create', methods=('GET', 'POST'))
def create():
   form = RegisterForm() 
   errorMessage=''
   if form.validate_on_submit():
      #crear usuario
      try:
       username = request.form['username']
       password = user_manager.hash_password(request.form['password'])
       email = request.form['email']
       rol = request.form['rol']
       roles=[]
       roles.append(rol)

       # crear usuario
       user = User(username=username, password=password, email=email, roles=roles)

       user.save()
       flash("Usuario creado con éxito")
       return redirect(url_for('useradmin.create'))
      except errors.NotUniqueError as exDup:
          errorMessage='El nombre de usuario ya existe'
      except Exception as ex:
          errorMessage=str(ex)
      
      if errorMessage!='':
       flash(errorMessage,'danger')

   if form.errors:
      flash(form.errors,'danger')
   
   return render_template('dashboard/user/create.html',form=form)

@userBp.route('/dashboard/user/update-username/<string:id>', methods=('GET', 'POST'))
def update(id):
   errorMessage=''
   user =  User.objects(_id=bson.objectid.ObjectId(id))

   form = UpdateForm() #meta={'csrf':False}

   if request.method == 'GET':
      form.new_username.data = user[0].username
      form.rol.data = user[0].roles[0]

   if form.validate_on_submit():
      try:
       roles=[]
       roles.append(request.form['rol'])
       user[0].update(username=request.form['new_username'],roles=roles)
       flash("Usuario actualizado con éxito")
       return redirect(url_for('useradmin.update',id=user[0]._id))
      except Exception as ex:
          errorMessage=str(ex)
   
   if errorMessage!='':
      flash(errorMessage,'danger')

   if form.errors:
      flash(form.errors,'danger')

   return render_template('dashboard/user/update.html',form=form,user=user)

@userBp.route('/dashboard/user/delete/<string:id>', methods=('GET', 'POST'))
def delete(id):
   user =  User.objects(_id=bson.objectid.ObjectId(id)) 

   user[0].delete()
   flash("Usuario eliminado con éxito")

   return redirect(url_for('useradmin.index'))