from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, RadioField, FieldList
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models.game import *
from app.models.user import *


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
    name = StringField('Name')
    human_players = IntegerField('Human Players')
    computer_players = IntegerField('Computer Players') #TODO: mozna zostawic puste, ale jesli wypelnione, nie moze przekraczac 10
    submit = SubmitField('Go to game details')

    def validate_name(self, name):
        game = Game.query.filter_by(name=name.data).first()
        if game is not None:
            raise ValidationError('Please use different name.')


class PlayersNamesForm(FlaskForm):
    players = FieldList(StringField('Name'), min_entries=1, max_entries=10)

    computer_ai = RadioField('Computer Players Level', choices=[('Dummy', 'Dummy computers'), ('Smart', 'Smart Computers')], default='Dummy')
    throw = SubmitField('Let the first player throw!')

class ThrowForm(FlaskForm):
    dice1 = BooleanField('Dice 1',description='Dice 1:') # todo ,default=False) = nie działa, zrobić domyslnie niezaznaczone w kazdej turze
    dice2 = BooleanField('Dice 2',description='Dice 2:') # todo description niepotrzebne, jest przeciez label
    dice3 = BooleanField('Dice 3',description='Dice 3:')
    dice4 = BooleanField('Dice 4',description='Dice 4:')
    dice5 = BooleanField('Dice 5',description='Dice 5:')

    throw_sel = SubmitField('Throw selected dices again',)
    throw_all = SubmitField('Throw all 5 dices')
    keep = SubmitField('Keep all the dices and select the category')
    cat_sel = SubmitField('Go to category selection')
    comp_next_step = SubmitField("Show me computer's next step")


class SelectCategoryForm(FlaskForm):
    aces = BooleanField('Aces')
    twos = BooleanField('Twos')
    threes = BooleanField('Threes')
    fours = BooleanField('Fours')
    fives = BooleanField('Fives')
    sixes = BooleanField('Sixes')
    three_of_a_kind = BooleanField('Three of a kind')
    four_of_a_kind = BooleanField('Four of a kind')
    full_house = BooleanField('Full house')
    small_straight = BooleanField('Small straight')
    large_straight = BooleanField('Large straight')
    yahtzee = BooleanField('Yahtzee')
    chance = BooleanField('Chance')

    submit_the_box = SubmitField('Submit the category')
    submit_next_player = SubmitField('Next player')

