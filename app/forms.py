from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, RadioField, FieldList
from wtforms.validators import DataRequired, ValidationError, EqualTo, NumberRange
from app.models.user import *
import wtforms.widgets as widgets


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
    human_players = IntegerField('Human Players', widget=widgets.Input(input_type="number"),
                                 validators=[NumberRange(min=1, max=10)])
    computer_players = IntegerField('Computer Players', widget=widgets.Input(input_type="number"),
                                    validators=[NumberRange(max=10)])
    submit = SubmitField('Go to game details')


class PlayersNamesForm(FlaskForm):
    players = FieldList(StringField('Name', validators=[DataRequired()]), min_entries=1, max_entries=10)
    computer_ai = RadioField('Computer Players Level',
                             choices=[('Dummy', 'Dummy computers'), ('Smart', 'Smart Computers')], default='Dummy')
    throw = SubmitField('Let the first player throw!')


class ThrowForm(FlaskForm):
    dice1 = BooleanField('Dice 1', description='Dice 1:')
    dice2 = BooleanField('Dice 2', description='Dice 2:')
    dice3 = BooleanField('Dice 3', description='Dice 3:')
    dice4 = BooleanField('Dice 4', description='Dice 4:')
    dice5 = BooleanField('Dice 5', description='Dice 5:')

    throw_sel = SubmitField('Throw selected dice again', )
    throw_all = SubmitField('Throw all 5 dice')
    keep = SubmitField('Keep all the dice and select the category')
    cat_sel = SubmitField('Go to category selection')
    comp_next_step = SubmitField("Show me computer's next step")


class SelectCategoryForm(FlaskForm):
    choices = RadioField('Categories',
                         choices=[(0, ''), (1, ''), (2, ''), (3, ''), (4, ''), (5, ''), (6, ''), (7, ''), (8, ''),
                                  (9, ''), (10, ''), (11, ''), (12, '')], default=0, coerce=int)

    submit_the_box = SubmitField('Submit the category')


class ShowCategoryForm(FlaskForm):
    submit_next_player = SubmitField('Next player')
