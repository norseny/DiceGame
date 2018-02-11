from app.models.game import *
from app.models.category import *

class ComputerPlayer(Player):

    def __init__(self, id):
        self.id = id

