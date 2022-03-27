

from wtforms.validators import DataRequired
from wtforms import ValidationError, validators
from wtforms import StringField,SelectField,PasswordField
from flask_wtf import FlaskForm

from hemerotecaApp.auth.model.user import User

class UpdateForm(FlaskForm):

    new_username = StringField('Nombre de usuario', validators=[
        validators.DataRequired('El nombre de usuario es obligatorio'),
    ])

    rol = SelectField('Rol', choices=[('Consulta', 'Consulta'),('Admin', 'Admin'),('Superadmin', 'Superadmin')])


    