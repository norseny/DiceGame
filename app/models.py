from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    game_results = db.relationship('Gameresult', backref='user', lazy='dynamic')
    game_round = db.relationship('Round', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    game_results = db.relationship('Gameresult', backref='game', lazy='dynamic')
    game_round = db.relationship('Round', backref='game', lazy='dynamic')

    def __repr__(self):
        return '<Game {}>'.format(self.name)


class Diceroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dice1 = db.Column(db.Integer)
    dice2 = db.Column(db.Integer)
    dice3 = db.Column(db.Integer)
    dice4 = db.Column(db.Integer)
    dice5 = db.Column(db.Integer)
    diceroll1 = db.relationship('Round',backref='diceroll1', lazy='dynamic', foreign_keys = 'Round.diceroll1_id')
    diceroll2 = db.relationship('Round',backref='diceroll2', lazy='dynamic', foreign_keys = 'Round.diceroll2_id')
    diceroll3 = db.relationship('Round',backref='diceroll3', lazy='dynamic', foreign_keys = 'Round.diceroll3_id')


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    diceroll1_id = db.Column(db.Integer, db.ForeignKey('diceroll.id'))
    diceroll2_id = db.Column(db.Integer, db.ForeignKey('diceroll.id'))
    diceroll3_id = db.Column(db.Integer, db.ForeignKey('diceroll.id'))
    category = db.Column(db.String(64))
    part_result = db.Column(db.Integer)


class Gameresult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    result = db.Column(db.Integer)

    def __repr__(self):
        return '<Gameresult {} {} {}>'.format(self.game_id, self.user_id, self.result)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))