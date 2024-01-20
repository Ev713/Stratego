import math
import statistics

from main import Game, Piece


def other_player_num(player_num):
    if player_num == 1:
        return 0
    else:
        return 1


class SearchEngine:
    def __init__(self):
        self.pieces_of_value = {}
        self.root = Node()

    def create_node(self, game_state=None):
        node = Node()
        node.engine = self
        node.game_state = game_state
        return node


class Node:
    """

    If we assume a value of piece in a potential node, in that game it is known.

    """

    def __init__(self):
        self.engine = None
        self.player_to_move = None
        self.enemy = 1 if self.player_to_move == 0 else 0
        self.actions = {}
        self.assumptions = {}
        self.game_state = Game()
        self.value = 0
        self.pieces = {}

    def get_enemy_piece_possible_assumptions(self):
        pieces_left = self.engine.pieces_of_value.copy()
        for p in self.game_state.get_pieces(side=self.enemy):
            if (p not in self.game_state.outside) and (p.known is False):
                continue
            pieces_left[p.get_value()] -= 1
        return set([v for v in pieces_left if pieces_left[v] > 0])

    def eval(self):
        return sum(piece.get_value() * (1 if piece.side == 0 else 1) for piece in self.game_state.get_pieces(out=False))
