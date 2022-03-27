from flask.globals import current_app
from hemerotecaApp import app,dbMongo

from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form
from flask_admin.contrib.mongoengine import ModelView
from wtforms import StringField, PasswordField, HiddenField, SelectField
from wtforms.validators import InputRequired, EqualTo

from flask_login import  current_user
from flask_user import UserMixin, TokenManager
from flask_user.forms import ChangePasswordForm

from werkzeug.security import check_password_hash,generate_password_hash

from flask_admin.contrib.sqla import ModelView
import bson

token_manager=TokenManager(app)

class User(dbMongo.Document,UserMixin):
    __tablename__ = 'users'
    username = dbMongo.StringField(max_length=120, required=True,unique=True)
    password = dbMongo.StringField(max_length=300, required=True)
    roles = dbMongo.ListField(dbMongo.StringField(), default=['Consulta'])
    active = dbMongo.BooleanField(default=True)
    _id = dbMongo.ObjectIdField(required=True, default=bson.objectid.ObjectId, primary_key=True)
    email = dbMongo.StringField(max_length=150)
  
    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self._id)

    def __repr__(self):
        return '<User %r>' % (self.name)

    def check_password(self, password):
        return check_password_hash(self.pwhash,password)
 
    def generate_auth_token(self):
       
       if not current_user.is_anonymous:
        token = token_manager.generate_token(current_user._id, current_user.password)
        return token
       return None
    
    def verify_auth_token(token):
        token_is_valid = False
        data_items = token_manager.verify_token(token, 60000)
        
        if data_items:
          user_id = data_items[0]
          password_ends_with = data_items[1]
         
          
          user = User.objects.get(_id=bson.objectid.ObjectId(user_id))
          return user


class AdminModalView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self,name,**kwargs):
        return "<h1>Usuario no autenticado</h1>"

class UserModelView(AdminModalView):

    can_edit = True
    #create_modal = True
    edit_modal = True

    can_export = True
    export_max_rows = 1

    column_searchable_list = ['username','rol']
    column_filters = ['rol','username']

    column_exclude_list = ['pwhash']

    form_args = {
        'username': {
            'label': 'Usuario',
            'validators': [InputRequired()]
        },
        'pwhash': {
            'label': 'Contraseña',
            'validators': [InputRequired()]
        }
    }

    def on_model_change(self, form, model, is_created):
        print(is_created)
        model.pwhash = generate_password_hash(model.pwhash)

    def edit_form(self, obj=None):
        form = super(UserModelView, self).edit_form(obj)
        #form.pwhash.data = ""
        del form.pwhash

        return form


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[InputRequired()])
    password = PasswordField('Contraseña', validators=[InputRequired()])
    next = HiddenField('next')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[InputRequired()])
    password = PasswordField('Contraseña', validators=[InputRequired(),EqualTo('retype_password')])
    retype_password  = PasswordField('Repetir Contraseña')
    email  = StringField('Email')
    rol  =  SelectField('Rol', choices=[('Consulta', 'Consulta'),('Admin', 'Admin'),('Superadmin', 'Superadmin')])


class CustomChangePasswordForm(ChangePasswordForm):
    old_password = PasswordField('Nueva password', [InputRequired(), EqualTo('new_password', message='La password debe coincidir')])
    new_password  = PasswordField('Repita la password')
    

