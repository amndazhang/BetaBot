import random
from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo.goboard_slow import Move
from dlgo.gotypes import Point

class RandomBot(Agent):
    # random valid move that preserves eyes
    def select_move(self, game_state):
        # 10% chance to pass even if there are valid moves (so game can end)
        if random.random() < 0.1:
            return Move.pass_turn()
            
        candidates = []
        for r in range(1, game_state.board.num_rows + 1):
            for c in range(1, game_state.board.num_cols + 1):
                candidate = Point(r, c)
                if game_state.is_valid_move(Move.play(candidate)) and \
                    not is_point_an_eye(game_state.board, 
                                        candidate, 
                                        game_state.next_player):
                    candidates.append(candidate)

        if not candidates:
            return Move.pass_turn()
        return Move.play(random.choice(candidates))