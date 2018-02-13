from app.models.category import *
from app.models.diceroll import *


class HumanPlayer(Player):
    pass

class ComputerPlayer(Player):

    def dummy(self):
        return True

    def check_ai_and_return_object(self):
        if 'Dummy' in self.player_name:
            curr_pl = ComputerPlayerDummy.query.get(int(self.id))
        elif 'Smart' in self.player_name:
            curr_pl = ComputerPlayerSmart.query.get(int(self.id))
        return curr_pl

    def create_cplayers(self, game_id, cp_no, computer_ai_type):
        for comp in range(1, int(cp_no)+1):
            computer_player = ComputerPlayer(player_name=str(computer_ai_type)+' Computer Player '+str(comp), computer_player=True)
            computer_player.insert_player_to_db(game_id)
            c =6


class ComputerPlayerDummy(ComputerPlayer):

    def randomly_select_dices(self, diceroll):
        ticked_boxes = self.random_selection_of_dices()
        sel_dices = [False for x in range(1, 6)]
        for i in ticked_boxes:
            sel_dices[i] = True
        diceroll.check_selected_get_random_numbers_and_insert(sel_dices)
        return [x+1 for x in ticked_boxes]

    def random_selection_of_dices(self):
        how_many_to_select = random.randint(1, 4)
        return random.sample(range(1, 5), how_many_to_select)

class ComputerPlayerSmart(ComputerPlayer):
    pass