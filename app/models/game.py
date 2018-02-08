from app import db
import random


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(64))
    game_results = db.relationship('Gameresult', backref='player', lazy='dynamic')
    game_turn = db.relationship('Turn', backref='player', lazy='dynamic')

    def __repr__(self):
        return '<Player {}>'.format(self.player_name)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    game_results = db.relationship('Gameresult', backref='game', lazy='dynamic')
    game_round = db.relationship('Turn', backref='game', lazy='dynamic')

    def __init__(self, name, cp_no=0):
        self.name = name
        insert_to_db(self)
        self.create_cplayers(cp_no)

    def __repr__(self):
        return '<Game {}>'.format(self.name)

    def create_cplayers(self, cp_no):
        for comp in range(1, int(cp_no)+1):
            player = Player(player_name='Computer Player '+str(comp))
            existing_player = Player.query.filter_by(player_name=player.player_name).first()
            if existing_player is None:
                insert_to_db(player)
                id_to_db = player.id
            else:
                id_to_db = existing_player.id
            game_result = Gameresult(game_id=self.id, player_id=id_to_db)
            insert_to_db(game_result)


class Diceroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dice1 = db.Column(db.Integer)
    dice2 = db.Column(db.Integer)
    dice3 = db.Column(db.Integer)
    dice4 = db.Column(db.Integer)
    dice5 = db.Column(db.Integer)
    diceroll1 = db.relationship('Turn', backref='diceroll1', lazy='dynamic', foreign_keys='Turn.diceroll1_id')
    diceroll2 = db.relationship('Turn', backref='diceroll2', lazy='dynamic', foreign_keys='Turn.diceroll2_id')
    diceroll3 = db.relationship('Turn', backref='diceroll3', lazy='dynamic', foreign_keys='Turn.diceroll3_id')

    def return_dices_as_list(self):
        dices_list = []
        dices_list.append(self.dice1)
        dices_list.append(self.dice2)
        dices_list.append(self.dice3)
        dices_list.append(self.dice4)
        dices_list.append(self.dice5)
        return dices_list

    def turn_dices_list_to_class_attributes(self, dices_list):
        if len(dices_list) == 5:
            self.dice1 = dices_list[0]
            self.dice2 = dices_list[1]
            self.dice3 = dices_list[2]
            self.dice4 = dices_list[3]
            self.dice5 = dices_list[4]

    def generate_all_rand_dices(self):
        dices_list = []
        for i in range(5):
            dices_list.append(random.randint(1, 6))
        self.turn_dices_list_to_class_attributes(dices_list)


class Turn(db.Model):
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
        return '<Gameresult {} {} {}>'.format(self.game_id, self.player_id, self.result)


def insert_to_db(self):
    db.session.add(self)
    db.session.commit()
