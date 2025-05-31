import enum
from collections import namedtuple

class Player(enum.Enum):
    black = 0
    white = 1

    @property
    def opp(self):
        return Player.black if self == Player.white else Player.white
    
class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1)
        ]