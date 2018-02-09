from app import db


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