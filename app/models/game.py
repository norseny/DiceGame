from app import db
from sqlalchemy import func
from flask_login import current_user
from datetime import datetime
from app.models.diceroll import *


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(64))
    computer_player = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return '<Player {}>'.format(self.player_name)

    def insert_part_result(self, game_id, cat_name, cat_result, diceroll_1_id, diceroll_2_id, diceroll_3_id):
        turn = Turn(
            player_id=self.id,
            game_id=game_id,
            diceroll1_id=diceroll_1_id,
            diceroll2_id=diceroll_2_id,
            diceroll3_id=diceroll_3_id,
            category=cat_name,
            part_result=cat_result
        )
        insert_to_db(turn)

    def generate_dict_of_part_results(self, game_id):
        return dict(Turn.query.with_entities(Turn.category, Turn.part_result).filter_by(game_id=game_id,
                                                                                        player_id=self.id).all())

    def get_no_of_turns(self, game_id):
        return Turn.query.filter_by(game_id=game_id, player_id=self.id).count()

    def insert_player_to_db(self, game_id, user=False):
        if user:
            self.user_id = current_user.id
        existing_player = Player.query.filter_by(player_name=self.player_name).first()
        if existing_player is None:
            insert_to_db(self)
            id_to_db = self.id
            insert_to_db(self)
        else:
            id_to_db = existing_player.id
        game_result = Gameresult(game_id=game_id, player_id=id_to_db)
        insert_to_db(game_result)

    def remove_unassigned_dicerolls(self, game_id):

        player_dicerolls = Diceroll.query.filter_by(game_id=game_id, player_id=self.id).all()
        player_turn_dicerolls = Turn.query.filter_by(game_id=game_id, player_id=self.id).add_columns(
            Turn.diceroll1_id, Turn.diceroll2_id, Turn.diceroll3_id).all()

        player_turn_dicerolls_ids = []
        for el in player_turn_dicerolls:
            player_turn_dicerolls_ids.append(el.diceroll1_id)
            player_turn_dicerolls_ids.append(el.diceroll2_id)
            player_turn_dicerolls_ids.append(el.diceroll3_id)

        for diceroll in player_dicerolls:
            if diceroll.id not in player_turn_dicerolls_ids:
                diceroll_to_remove = Diceroll.query.get(diceroll.id)
                db.session.delete(diceroll_to_remove)
                db.session.commit()

    def find_unassigned_dicerolls(self, game_id):
        found_dicerolls = []

        player_dicerolls = Diceroll.query.filter_by(game_id=game_id, player_id=self.id).all()
        player_turn_dicerolls = Turn.query.filter_by(game_id=game_id, player_id=self.id).add_columns(
            Turn.diceroll1_id, Turn.diceroll2_id, Turn.diceroll3_id).all()

        player_turn_dicerolls_ids = []
        for el in player_turn_dicerolls:
            player_turn_dicerolls_ids.append(el.diceroll1_id)
            player_turn_dicerolls_ids.append(el.diceroll2_id)
            player_turn_dicerolls_ids.append(el.diceroll3_id)

        for index, diceroll in enumerate(player_dicerolls):
            if diceroll.id not in player_turn_dicerolls_ids:
                found_dicerolls.append(Diceroll.query.get(diceroll.id))

        return found_dicerolls
                # db.session.delete(diceroll_to_remove)
                # db.session.commit()



class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    date = db.Column(db.DateTime, default=datetime.now())

    def __init__(self):
        insert_to_db(self)
        self.name = current_user.username + "'s game " + 'id ' + str(self.id) #todo: poprawic na wprowadzanie nazwy gry
        db.session.commit()

    def __repr__(self):
        return '<Game {}>'.format(self.name)

    def get_list_of_all_players_ids(self):
        game_player_relation = Gameresult.query.filter_by(game_id=self.id).all()
        return [a.player_id for a in game_player_relation]

    def get_list_of_human_players_ids(self):
        players_ids_all = self.get_list_of_all_players_ids()
        players_ids_humans = []
        for x in players_ids_all:  # TODO zamienic na list comprehension
            player = Player.query.get(int(x))
            if not player.computer_player:
                players_ids_humans.append(player.id)
        return players_ids_humans


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

    def update_results(self, game_id):  # todo: dodatkowe punkty za cośtam
        game = Game.query.get(game_id)
        players_ids = game.get_list_of_all_players_ids()
        for player_id in players_ids:
            query = Turn.query.filter_by(game_id=game_id, player_id=player_id)
            total_for_player = query.with_entities(func.sum(Turn.part_result)).scalar()
            gameresult = Gameresult.query.filter_by(game_id=game_id, player_id=player_id).scalar()
            gameresult.result = total_for_player
            db.session.commit()


def insert_to_db(self):
    db.session.add(self)
    db.session.commit()
