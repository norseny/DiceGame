from app.models.game import *
from app.models.category import *
from app.models.diceroll import *


class HumanPlayer(Player):

    def __init__(self, id):
        self.id = id


class ComputerPlayer(Player):

    def __init__(self, id):
        self.id = id

    def dummy(self):
        return True

    def check_ai_and_return_object(self):
        if 'Dummy' in self.player_name:
            curr_pl = ComputerPlayerDummy.query.get(int(self.id))
        elif 'Smart' in self.player_name:
            curr_pl = ComputerPlayerSmart.query.get(int(self.id))
        return curr_pl


class ComputerPlayerDummy(ComputerPlayer):

    def randomly_select_dices(self, diceroll):
        ticked_boxes = self.random_selection_of_dices()
        sel_dices = [False for x in range(1, 6)]
        for i in ticked_boxes:
            sel_dices[i] = True
        diceroll.check_selected_get_random_numbers_and_insert(sel_dices)
        return [x+1 for x in ticked_boxes]

    def random_selection_of_dices(self):
        how_many_to_select = random.randint(0, 5)
        return random.sample(range(0, 5), how_many_to_select)

class ComputerPlayerSmart(ComputerPlayer):
    pass