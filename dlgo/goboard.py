import copy
from dlgo.gotypes import Player
from dlgo import zobrist

__all__ = [
    'Board',
    'GameState',
    'Move',
]

class GoString():
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        new_libs = self.liberties - set([point])
        return GoString(self.color, self.stones, new_libs)

    def with_liberty(self, point):
        new_libs = self.liberties | set([point])
        return GoString(self.color, self.stones, new_libs)

    def merged_with(self, go_string):
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones)

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
        self._hash = zobrist.EMPTY_BOARD

    def place_stone(self, color, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None

        # evaluate direct neighbors
        adjacent_same_color = []
        adjacent_opp_color = []
        liberties = []
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self.get_go_string(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == color:
                adjacent_same_color.append(neighbor_string)
            else:
                adjacent_opp_color.append(neighbor_string)

        new_string = GoString(color, {point}, liberties)

        # same color neighbors
        for same_color_string in adjacent_same_color:  # merge adj strings of same color
            new_string = new_string.merged_with(same_color_string)
        for new_point in new_string.stones:
            self._grid[new_point] = new_string
        
        # apply hash
        self._hash ^= zobrist.HASH_CODE[point, color]

        # opp color neighbors
        for opp_color_string in adjacent_opp_color:  # reduce liberty of adj opp color string
            if point in opp_color_string.liberties:  # Only remove if the liberty exists
                opp_color_string.without_liberty(point)
            if opp_color_string.num_liberties == 0:  # remove string if zero liberties
                self._remove_string(opp_color_string)

    def _remove_string(self, string):
        for point in string.stones:
            # create new liberties of neighbors
            for neighbor in point.neighbors():
                neighbor_string = self.get_go_string(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string: # add liberty if neighbor not in string
                    neighbor_string.add_liberty(point)
            self._grid[point] = None

            # unapply hash
            self._hash ^= zobrist.HASH_CODE[point, string.color]
    
    # board utils
    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and 1 <= point.col <= self.num_cols

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
    
    def zobrist_hash(self):
        return self._hash

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

class GameState():
    def __init__(self, board, next_player, previous_state, last_move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous_state
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(previous_state.previous_states) | \
                set((previous_state.next_player, previous_state.board.zobrist_hash()))
        self.last_move = last_move
    
    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)
    
    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        if self.previous_state is None or self.previous_state.last_move is None:
            return False
        second_last_move = self.previous_state.last_move
        return self.last_move.is_pass and second_last_move.is_pass

    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0

    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player, next_board.zobrist_hash())
        return next_situation in self.previous_states
    
    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        # illegal moves
        return not self.board.get_color(move.point) and \
            not self.is_move_self_capture(self.next_player, move) and \
                not self.does_move_violate_ko(self.next_player, move)