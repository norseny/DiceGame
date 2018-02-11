import random

class Category:
    names = ['aces',
             'twos',
             'threes',
             'fours',
             'fives',
             'sixes',
             'three_of_a_kind',
             'four_of_a_kind',
             'full_house',
             'small_straight',
             'large_straight',
             'yahtzee',
             'chance'
             ]

    def __init__(self):
        self.result = 0

    # method_list = [method_name for method_name in dir(self) if callable(getattr(self, method_name))]

    def aces_count(self, diceroll):
        self.upper_table_count(1, diceroll)

    def twos_count(self, diceroll):
        self.upper_table_count(2, diceroll)

    def threes_count(self, diceroll):
        self.upper_table_count(3, diceroll)

    def fours_count(self, diceroll):
        self.upper_table_count(4, diceroll)

    def fives_count(self, diceroll):
        self.upper_table_count(5, diceroll)

    def sixes_count(self, diceroll):
        self.upper_table_count(6, diceroll)

    def three_of_a_kind_count(self, diceroll):
        if len(set(diceroll)) <= 3:
            self.result = sum(diceroll)

    def four_of_a_kind_count(self, diceroll):
        if len(set(diceroll)) <= 2: # todo: poprawic
            self.result = sum(diceroll)

    def full_house_count(self, diceroll):
        if len(set(diceroll)) == 2:
            self.result = 25

    def small_straight_count(self, diceroll):
        if self.is_sublist(list(range(1, 5)), diceroll) or self.is_sublist(list(range(2, 6)), diceroll) or self.is_sublist(list(range(3, 7)), diceroll):
            self.result = 30

    def large_straight_count(self, diceroll):
        if self.is_sublist(list(range(1, 6)), diceroll) or self.is_sublist(list(range(2, 7)), diceroll):
            self.result = 40

    def yahtzee_count(self, diceroll):
        if len(set(diceroll)) == 1:
            self.result = 50

    def chance_count(self, diceroll):
        self.result = sum(diceroll)

    def upper_table_count(self, number, diceroll):
        for thrown_number in diceroll:
            if thrown_number == number:
                self.result += number

    def is_sublist(self, lst1, lst2):   #todo: poprawic
        ls1 = [element for element in lst1 if element in lst2]
        ls2 = [element for element in lst2 if element in lst2]
        if sorted(ls2) == sorted(ls1):
        # if ls2 == ls1:
            return True

    def choose_rand_cat_and_count_result(self, last_diceroll):
        cat_alredy_chosen = True
        while cat_alredy_chosen:
            rand_cat_name = self.names[random.randint(0, 12)]
                # if not found w bazie:
                #  cat_already_chosen = False
        getattr(self, rand_cat_name + '_count')(last_diceroll)
        s = 5
        return rand_cat_name
