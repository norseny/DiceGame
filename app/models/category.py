import random
from app.models.game import *

class Category:
    category_details = [
        {'label':'Aces', 'desc1':'Any combination','desc2':'The sum of dice with the number 1', 'result':0},
        {'label':'Twos', 'desc1':'Any combination','desc2':'The sum of dice with the number 2'},
        {'label':'Threes','desc1': 'Any combination', 'desc2': 'The sum of dice with the number 3'},
        {'label': 'Fours', 'desc1': 'Any combination', 'desc2': 'The sum of dice with the number 4'},
        {'label': 'Fives', 'desc1': 'Any combination', 'desc2': 'The sum of dice with the number 5'},
        {'label': 'Sixes', 'desc1': 'Any combination', 'desc2': 'The sum of dice with the number 6'},
        {'label': 'Three of a kind', 'desc1': 'At least three dice the same', 'desc2': 'Sum of all dice'},
        {'label': 'Four of a kind', 'desc1': 'At least four dice the same', 'desc2': 'Sum of all dice'},
        {'label': 'Full house', 'desc1': 'Three of one number and two of another', 'desc2': '25'},
        {'label': 'Small straight', 'desc1': 'Four sequential dice (1-2-3-4, 2-3-4-5, or 3-4-5-6)', 'desc2': '30'},
        {'label': 'Large straight', 'desc1': 'Five sequential dice (1-2-3-4-5 or 2-3-4-5-6)', 'desc2': '40'},
        {'label': 'Yahtzee', 'desc1': 'All five dice the same', 'desc2': '50'},
        {'label': 'Chance', 'desc1': 'Any combination', 'desc2': 'Sum of all dice'},
    ]

    def __init__(self):
        self.result = 0

    def aces_count(self, diceroll):
        self.upper_table_sum(1, diceroll)

    def twos_count(self, diceroll):
        self.upper_table_sum(2, diceroll)

    def threes_count(self, diceroll):
        self.upper_table_sum(3, diceroll)

    def fours_count(self, diceroll):
        self.upper_table_sum(4, diceroll)

    def fives_count(self, diceroll):
        self.upper_table_sum(5, diceroll)

    def sixes_count(self, diceroll):
        self.upper_table_sum(6, diceroll)

    def three_of_a_kind_count(self, diceroll):
        if len(set(diceroll)) <= 3:
            for dice in diceroll:
                if diceroll.count(dice) == 3:
                    self.result = sum(diceroll)
        else:
            self.result = 0

    def four_of_a_kind_count(self, diceroll):
        if len(set(diceroll)) <= 2:
            for dice in diceroll:
                if diceroll.count(dice) == 4:
                    self.result = sum(diceroll)
        else:
            self.result = 0

    def full_house_count(self, diceroll):
        if len(set(diceroll)) == 2:
            self.result = 25
        else:
            self.result = 0

    def small_straight_count(self, diceroll):
        diceroll_set = set(diceroll)
        list_of_sets = []
        list_of_sets.append(set(range(1,5)))
        list_of_sets.append(set(range(2,6)))
        list_of_sets.append(set(range(3,7)))
        for my_set in list_of_sets:
            if self.check_if_subset(diceroll_set, my_set):
                self.result = 30
                return None
            else:
                self.result = 0

    def large_straight_count(self, diceroll):
        diceroll_set = set(diceroll)
        list_of_sets = []
        list_of_sets.append(set(range(1, 6)))
        list_of_sets.append(set(range(2, 7)))
        for my_set in list_of_sets:
            if self.check_if_subset(diceroll_set, my_set):
                self.result = 40
                return None
            else:
                self.result = 0

    def yahtzee_count(self, diceroll):
        if len(set(diceroll)) == 1:
            self.result = 50
        else:
            self.result = 0

    def chance_count(self, diceroll):
        self.result = sum(diceroll)

    def upper_table_sum(self, number, diceroll):
        self.result = 0
        for thrown_number in diceroll:
            if thrown_number == number:
                self.result += number

    def check_if_subset(self, diceroll_set, my_set):
        return my_set.issubset(diceroll_set)
