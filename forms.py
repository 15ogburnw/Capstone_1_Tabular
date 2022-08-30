from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField
from wtforms.validators import InputRequired, Email, Length


class NewUserForm(FlaskForm):

    first_name = StringField('First Name', validators=[InputRequired(
        message='This field is required!'), Length(max=20)])
    last_name = StringField('Last Name (Optional)',
                            validators=[Length(max=30)])
    username = StringField('Username', validators=[InputRequired(
        message='This field is required!'), Length(max=30)])
    email = StringField('E-mail', validators=[InputRequired(
        message='This field is required!'), Email(message='Please enter a valid email address!')])
    password = PasswordField('Password', validators=[InputRequired(
        'This field is required!'), Length(min=6, max=30)])


class EditUserForm(FlaskForm):

    first_name = StringField('First Name', validators=[InputRequired(
        message='This field is required!'), Length(max=20)])
    last_name = StringField('Last Name (Optional)',
                            validators=[Length(max=30)])
    username = StringField('Username', validators=[InputRequired(
        message='This field is required!'), Length(max=30)])
    email = StringField('E-mail', validators=[InputRequired(
        message='This field is required!'), Email(message='Please enter a valid email address!')])

    profile_pic = FileField('Profile Picture')

    cover_pic = FileField('Cover Photo')

    instrument_id = SelectField('Instrument', coerce=int)

    bio = TextAreaField('About Me', validators=[Length(max=200)])


class UserLoginForm(FlaskForm):

    username = StringField('Username', validators=[InputRequired(
        message='This field is required!'), Length(max=30)])

    password = PasswordField('Password', validators=[InputRequired(
        'This field is required!'), Length(min=6, max=30)])
