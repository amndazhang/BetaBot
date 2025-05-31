import copy
from dlgo.gotypes import Player

class Move():
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)
    
    @classmethod
    def resign(cls):
        return Move(is_resign=True)

class GoString():
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    def remove_liberty(self, point):
        self.liberties.remove(point)
    
    def add_liberty(self, point):
        self.liberties.add(point)
    
    def merged_with(self, go_string):
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        combined_liberties = (self.liberties | go_string.liberties) - combined_stones
        return GoString(self.color, combined_stones, combined_liberties)
    
    @property
    def num_liberties(self):
        return len(self.liberties)
    
    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
                self.stones == other.stones and \
                    self.liberties == other.liberties
    
class Board():
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}

    def place_stone(self, color, point):
        assert self.is_on_grid(point)
        assert self._grid[point] is None

        # evaluate direct neighbors
        adjacent_same_color = {}
        adjacent_opp_color = {}
        liberties = {}
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self.get_go_string(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == color:
                adjacent_same_color.add(neighbor_string)
            else:
                adjacent_opp_color.add(neighbor_string)

        new_string = GoString(color, {point}, liberties)

        # same color neighbors
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)
        for new_point in new_string.stones:
            self._grid[new_point] = new_string
        
        # opp color neighbors
        for opp_color_string in adjacent_opp_color:
            opp_color_string.remove_liberty(point)
        for opp_color_string in adjacent_opp_color:
            if opp_color_string.num_liberties == 0:
                self._remove_string(opp_color_string)

    def _remove_string(self, string):
        for point in string:
            # create new liberties of neighbors
            for neighbor in point.neighbors():
                neighbor_string = self.get_go_string(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string: # add liberty if neighbor not in string
                    neighbor_string.add_liberty(point)
            self._grid[point] = None
    
    # board utils
    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and 1 <= point.cols <= self.num_cols

    def get_go_string(self, point):
        return self._grid.get(point)

    def get_color(self, point):
        string = self.get_go_string(point)
        return string.color if string is not None else None
    
    def __eq__(self, other):
        return isinstance(other, Board) and \
            self.num_rows == other.num_rows and \
                self.num_cols == other.num_cols and \
                    self._grid == other._grid