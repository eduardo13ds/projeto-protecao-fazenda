from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
# Importe seu modelo de usuário para validar se o usuário já existe
# from app.models import Usuario

class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    password2 = PasswordField(
        'Repita a Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    # def validate_username(self, username):
    #     user = # Lógica para buscar usuário no DB
    #     if user:
    #         raise ValidationError('Este nome de usuário já está em uso.')

    # def validate_email(self, email):
    #     user = # Lógica para buscar usuário no DB por email
    #     if user:
    #         raise ValidationError('Este email já está em uso.')