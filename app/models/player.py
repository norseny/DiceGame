from app.models.category import *
from app.models.diceroll import *
from app.models.game import *
import string


class HumanPlayer(Player):
    pass

class ComputerPlayer(Player):

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

    def count_points(self, diceroll):
            cat = Category()
            methods = [a for a in dir(cat) if not a.startswith('__') and callable(getattr(cat, a)) if 'count' in a]
            results ={'best':[0, 'methodname']}
            for method in methods:
                getattr(cat, method)(diceroll)
                results[method] = cat.result
                if cat.result > results['best'][0]:
                    results['best'] = [cat.result, method]
            return results


class ComputerPlayerDummy(ComputerPlayer):

    def randomly_select_dices(self, diceroll, game_id):
        ticked_boxes = self.random_selection_of_dices()
        sel_dices = [False for x in range(1, 6)]
        for i in ticked_boxes:
            sel_dices[i] = True
        diceroll.check_selected_get_random_numbers_and_insert(sel_dices, self.id, game_id)
        return [x+1 for x in ticked_boxes]

    def random_selection_of_dices(self):
        how_many_to_select = random.randint(1, 4)
        return random.sample(range(1, 5), how_many_to_select)

    def choose_rand_cat_and_count_result(self, last_diceroll, game_id):
        cat = Category()
        picked_category = {}

        results_dict = self.count_points(last_diceroll)
        zero_results_dict = {}
        del results_dict['best']

        for key, value in results_dict.items():
            if value == 0:
                zero_results_dict[key] = value

        for key in zero_results_dict.keys():
            del results_dict[key]

        method_name = ''

        if results_dict:
            keys = list(results_dict.keys())
            random.shuffle(keys)
            shuffled_results = [(key, results_dict[key]) for key in keys]

            for el in shuffled_results:
                el_name = el[0].capitalize().replace('_', ' ').replace('count', '').rstrip(string.whitespace)
                if not Turn.query.filter_by(game_id=game_id, player_id=self.id, category=el_name).count():
                    method_name = el[0]
                    break

        if method_name == '':
            cat_already_chosen = True
            while cat_already_chosen:
                rand_met_name = random.choice(list(zero_results_dict.keys()))
                rand_cat_name = rand_met_name.capitalize().replace('_', ' ').replace('count', '').rstrip(string.whitespace)
                if not Turn.query.filter_by(game_id=game_id, player_id=self.id, category=rand_cat_name).count():
                    cat_already_chosen = False
                    method_name = rand_met_name
                del zero_results_dict[rand_met_name]


        getattr(cat, method_name)(last_diceroll)
        picked_category['result'] = cat.result
        cat_name = method_name.capitalize().replace('_', ' ').replace('count', '').rstrip(string.whitespace)
        picked_category['name'] = cat_name

        return picked_category

class ComputerPlayerSmart(ComputerPlayer):

    def choose_cat_and_count_result(self, diceroll, game_id):
        results_dict = self.count_points(diceroll)
        picked_category = {}
        best_category_name = results_dict['best'][1].capitalize().replace('_', ' ').replace('count', '')
        best_category_name = best_category_name.rstrip(string.whitespace)
        if not Turn.query.filter_by(game_id=game_id, player_id=self.id, category=best_category_name).count():
            picked_category['name'] = best_category_name.rstrip(string.whitespace)
            picked_category['result'] = results_dict['best'][0]
            return picked_category
        else:
            del results_dict['best']
            sorted_results = sorted(results_dict.items(), key=lambda x: x[1], reverse=True)
            for category in sorted_results:
                category_name = category[0].capitalize().replace('_', ' ').replace('count', '')
                category_name = category_name.rstrip(string.whitespace)
                if not Turn.query.filter_by(game_id=game_id, player_id=self.id, category=category_name).count():
                    picked_category['name'] = category_name.rstrip(string.whitespace)
                    picked_category['result'] = category[1]
                    return picked_category

    # def count_points(self, diceroll):
    #         cat = Category()
    #         methods = [a for a in dir(cat) if not a.startswith('__') and callable(getattr(cat, a)) if 'count' in a]
    #         results ={'best':[0, 'methodname']}
    #         for method in methods:
    #             getattr(cat, method)(diceroll)
    #             results[method] = cat.result
    #             if cat.result > results['best'][0]:
    #                 results['best'] = [cat.result, method]
    #         return results