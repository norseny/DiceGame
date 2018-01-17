from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import *


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use different username.')


class NewGameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Start')

    def validate_name(self, name):
        game = Game.query.filter_by(name=name.data).first()
        if game is not None:
            raise ValidationError('Please use different name.')


class ThrowForm(FlaskForm):
    dice1 = BooleanField('Dice 1',description='Dice 1:') # todo ,default=False) = nie działa, zrobić domyslnie niezaznaczone w kazdej turze
    dice2 = BooleanField('Dice 2',description='Dice 2:')
    dice3 = BooleanField('Dice 3',description='Dice 3:')
    dice4 = BooleanField('Dice 4',description='Dice 4:')
    dice5 = BooleanField('Dice 5',description='Dice 5:')

    throw_sel = SubmitField('Throw selected dices again',)
    throw_all = SubmitField('Throw all 5 dices')
    keep = SubmitField('Keep all the dices and select the category')
    cat_sel = SubmitField('Go to category selection')




