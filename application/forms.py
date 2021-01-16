from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from flask import Markup
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from application.models import User

class InlineButtonWidget(object):
    html = """
    <button %s type="submit">%s</button>
    """

    def __init__(self, label, input_type='submit'):
        self.input_type = input_type
        self.label = label

    def __call__(self, **kwargs):
        param = []
        for key in kwargs:
            param.append(key + "=\"" + kwargs[key] + "\"")
        return Markup(self.html % (" ".join(param), self.label))


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)], render_kw={'placeholder': 'Name'})
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')], render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        try:
            user = User.query.filter_by(username=username.data)[0]
        except:
            return
        raise ValidationError("That username is taken. Please choose a different one.")

    def validate_email(self, email):
        try:
            user = User.query.filter_by(email=email.data)[0]
        except:
            return
        raise ValidationError("That email is taken. Please choose a different one.")


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Password'})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class NewDiaryEntryForm(FlaskForm):
    title = StringField('Title:', validators=[DataRequired()])
    text = TextAreaField('Content:', validators=[DataRequired()])
    picture = FileField('Upload a picture to go with your diary entry:', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Submit') # change label?
    
    
class NewGoalForm(FlaskForm):
    goal = StringField('Goal Summary:', validators=[DataRequired()])
    start_date = DateField('Start Date:')
    end_date = DateField('End Date:')
    steps = TextAreaField('Action Steps')
    reflection = TextAreaField('After Action Review:')
    submit = SubmitField('Create Goal')
    