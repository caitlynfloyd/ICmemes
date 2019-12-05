from click import Group
from flask import request
from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, DateTimeField, \
    SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class NewMemeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    caption = StringField('Caption', validators=[DataRequired()])
    location = SelectField('Location', coerce=int, validators=[DataRequired()])
    categories = SelectMultipleField("Categories", coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')


class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])
    submit = SubmitField('Submit')


images = UploadSet('images', IMAGES)


class UploadForm(FlaskForm):
    upload = FileField('image', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!')
    ])


class MemeSearchForm(FlaskForm):
    choices = [('Park', 'Park'), ('PT', 'PT'), ('Circles', 'Circles'),('Dining', 'Dining')]
    select = SelectField('Search for memes: ', choices=choices)
    search = StringField('')


class SearchForm(FlaskForm):
    search = StringField('Search: ', validators=[DataRequired()])
    submit = SubmitField('Submit')
