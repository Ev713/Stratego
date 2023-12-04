import math


class Piece:
    def __init__(self, num, side):
        self.num = num
        self.side = side  # 1 or 0
        self.id = None
        self.known = False

    def __gt__(self, other):
        return self.num > other.num or (self.num == 1 and other.num == 10) or (self.num == 0 and other.num != 3)

    def __lt__(self, other):
        return other > self

    def __eq__(self, other):
        return self.num == other.num

    def is_bomb(self):
        return self.num == 0

    def is_flag(self):
        return self.num == -1

    def can_move(self):
        return not self.is_flag() and not self.is_bomb()

    def __hash__(self):
        return self.num, self.side, self.id

    def __copy__(self):
        copy = Piece(self.num, self.side)
        copy.id = self.id
        copy.known = self.known
        return copy


class Game:
    def __init__(self):
        self.board = [[None, None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None, None],
                      [None, None, 'X', 'X', None, None, 'X', 'X', None, None],
                      [None, None, 'X', 'X', None, None, 'X', 'X', None, None],
                      [None, None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None, None]]
        self.outside = [
            Piece(-1, 0),
            Piece(0, 0), Piece(0, 0),
            Piece(1, 0),
            Piece(2, 0), Piece(2, 0),
            Piece(3, 0), Piece(3, 0),
            Piece(5, 0),

            Piece(-1, 1),
            Piece(0, 1), Piece(0, 1),
            Piece(1, 1),
            Piece(2, 1), Piece(2, 1),
            Piece(3, 1), Piece(3, 1),
            Piece(5, 1)
        ]
        self.set_ids()
        self.pieces = {hash(p): p for p in self.outside}

    def placement_legal(self, piece, row, col):
        if self.board[row][col] is not None:
            return False
        return (row < 5 and piece.side == 0) or (row > 6 and piece.side == 1)

    def set_pieces(self, policy):
        for p in policy:
            if not self.placement_legal(p, policy[p][0], policy[p][1]):
                raise Exception("Illegal policy")
            else:
                self.board[policy[p][0]][policy[p][1]] = p

    def get_loc(self, piece):
        for row in range(10):
            for col in range(10):
                if self.board[row][col] is piece:
                    return row, col

    def move_is_legal(self, piece, row, col):
        piece_row, piece_col = self.get_loc(piece)
        return (((abs(piece_row - row) == 1) ^ (abs(piece_col - col) == 1))
                and self.board[row][col] != 'X') and piece.can_move()

    def move_piece(self, piece, row, col):
        piece_row, piece_col = self.get_loc(piece)

        if not self.move_is_legal(piece, row, col):
            raise Exception("Illegal move!")

        if not self.board[row][col] is None:
            enemy = self.board[row][col]
            piece.known = True
            enemy.known = True
            if enemy > piece:
                self.board[piece_row][piece_col] = None
                return
            elif enemy == piece:
                self.board[row][col] = None
                return
        self.board[row][col] = piece
        self.board[piece_row][piece_col] = None

    def set_ids(self):
        pieces = {}
        for p in self.outside:
            if (p.num, p.side) not in pieces:
                pieces[(p.num, p.side)] = 1
            else:
                pieces[(p.num, p.side)] += 1
            p.id = pieces[(p.num, p.side)]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pass
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
