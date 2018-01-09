from app import db


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    game_results = db.relationship('Gameresult', backref='player', lazy='dynamic')
    game_round = db.relationship('Round', backref='player', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)


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
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    diceroll1_id = db.Column(db.Integer, db.ForeignKey('diceroll.id'))
    diceroll2_id = db.Column(db.Integer, db.ForeignKey('diceroll.id'))
    diceroll3_id = db.Column(db.Integer, db.ForeignKey('diceroll.id'))
    category = db.Column(db.String(64))
    part_result = db.Column(db.Integer)


class Gameresult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    result = db.Column(db.Integer)

    def __repr__(self):
        return '<Gameresult {} {}>'.format(self.game_id, self.player_id)
