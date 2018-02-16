from app import db
import random
from app.models import game as models
from flask import session


class Diceroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dice1 = db.Column(db.Integer)
    dice2 = db.Column(db.Integer)
    dice3 = db.Column(db.Integer)
    dice4 = db.Column(db.Integer)
    dice5 = db.Column(db.Integer)
    player_id = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, nullable=False)

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

    def generate_all_rand_dices_and_insert_to_db(self, player_id, game_id):
        dices_list = []
        for i in range(5):
            dices_list.append(random.randint(1, 6))
        self.turn_dices_list_to_class_attributes(dices_list)
        self.player_id = player_id
        self.game_id = game_id
        models.insert_to_db(self)

    def assign_dices(self, source_diceroll):
        self.dice1 = source_diceroll.dice1
        self.dice2 = source_diceroll.dice2
        self.dice3 = source_diceroll.dice3
        self.dice4 = source_diceroll.dice4
        self.dice5 = source_diceroll.dice5

    def check_selected_get_random_numbers_and_insert(self, dices, player_id, game_id):
        if dices[0]:
            self.dice1 = random.randint(1, 6)
        if dices[1]:
            self.dice2 = random.randint(1, 6)
        if dices[2]:
            self.dice3 = random.randint(1, 6)
        if dices[3]:
            self.dice4 = random.randint(1, 6)
        if dices[4]:
            self.dice5 = random.randint(1, 6)
        self.player_id = player_id
        self.game_id = game_id
        models.insert_to_db(self)

    def throw_all_rand(self, player_id, game_id):
        self.generate_all_rand_dices_and_insert_to_db(player_id, game_id)
        return self.return_dices_as_list()

# def get_dicerolls_data():
#     dicerolls_data = {}
#     dicerolls_data['second_dice_id'] = 0 # todo: dokończyć
#     dicerolls_data['third_dice_id'] = 0
#
#     if session.get('diceroll_3_id'):
#         third_dice_obj = dicerolls_data['last_dice_obj'] = Diceroll.query.get(session['diceroll_3_id'])
#         dicerolls_data['third_dice_id'] = third_dice_obj.id
#         session.get('diceroll_2_id')
#         second_dice = Diceroll.query.get(session['diceroll_2_id'])
#         dicerolls_data['second_dice_id'] = second_dice.id
#         session.get('diceroll_1_id')
#         first_dice = Diceroll.query.get(session['diceroll_1_id'])
#         dicerolls_data['first_dice_id'] = first_dice.id
#
#     elif session.get('diceroll_2_id'):
#         second_dice = last_dice = Diceroll.query.get(session['diceroll_2_id'])
#         dicerolls_data['second_dice_id'] = second_dice.id
#         session.get('diceroll_1_id')
#         first_dice = Diceroll.query.get(session['diceroll_1_id'])
#         dicerolls_data['first_dice_id'] = first_dice.id
#
#     elif session.get('diceroll_1_id'):
#         first_dice = dicerolls_data['last_dice_obj'] = Diceroll.query.get(session['diceroll_1_id'])
#         dicerolls_data['first_dice_id'] = first_dice.id
