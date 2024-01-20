import math


class Reader:
    def __init__(self, filepath=False):
        self.read_from_file = filepath is not None
        if filepath is not None:
            file = open(filepath, 'r')
            self.lines = [line for line in file]
            self.line_index = -1

    def input(self, message=None):
        if not self.read_from_file:
            return input(message)
        else:
            if self.line_index == len(self.lines) - 1:
                print('File is over, need input from user')
                self.read_from_file = False
                return self.input(message)
            self.line_index += 1
            return self.lines[self.line_index]


class EndOfFileException(Exception):
    def __init__(self):
        pass


class Piece:
    def __init__(self, num, side):
        self.num = num
        self.side = side  # 1 or 0
        self.id = None
        self.known = False

    def _gt_(self, other):
        return self.num > other.num or (self.num == 1 and other.num == 10) or (self.num == 0 and other.num != 3)

    def _lt_(self, other):
        return other > self

    def _eq_(self, other):
        return self.num == other.num

    def is_bomb(self):
        return self.num == 0

    def is_flag(self):
        return self.num == -1

    def can_move(self):
        return not self.is_flag() and not self.is_bomb()

    def get_value(self):
        return self.num

    def hash(self):
        return self.num, self.side, self.id

    def _copy_(self):
        copy = Piece(self.num, self.side)
        copy.id = self.id
        copy.known = self.known
        return copy

    def str(self, side):
        if self.side == 0:
            left = '{'
            right = '}'
        else:
            left = '['
            right = ']'
        if self.known or self.side == side:
            return left + str(self.num) + right if self.num != -1 else left + 'P' + right
        return left + ' ' + right


class Game:
    def __init__(self, filepath=None):
        self.side = 0
        self.reader = Reader(filepath)
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
        self.pieces = {p.hash(): p for p in self.outside}

    def set_ids(self):
        for i in range(len(self.outside)):
            self.outside[i].id = i

    def get_pieces(self, side=None, known=None, out=None):
        pieces = []
        for p in self.pieces.values():
            if ((side is not None and p.side != side) or
                    (known is not None and p.known != known) or
                    (out is not None and p not in self.outside)):
                continue
        return pieces

    def placement_legal(self, piece, row, col):
        if self.board[row][col] is not None:
            print("The square is not empty")
            return False
        if not (row < 5 and piece.side == 0) and not (row > 6 and piece.side == 1):
            print(f"Incorrect side for piece of side {piece.side}")
            return False
        return True

    def change_side(self):
        self.side = (self.side + 1) % 2

    def set_pieces(self, policy):
        if policy is None:
            return False
        used_pieces = []
        for p in self.outside:
            if p.hash() not in policy:
                continue
            if not self.placement_legal(p, policy[p.hash()][0], policy[p.hash()][1]):
                print(f"{p.str(p.side)} illegal placement at  {policy[p.hash()][0], policy[p.hash()][1]}")
                return False
            else:
                self.board[policy[p.hash()][0]][policy[p.hash()][1]] = p
                used_pieces.append(p)
                print(f"{p.str(p.side)} set at  {policy[p.hash()][0], policy[p.hash()][1]}")
        for p in used_pieces:
            self.outside.remove(p)
        return True

    def get_loc(self, piece):
        for row in range(10):
            for col in range(10):
                if self.board[row][col] is piece:
                    return row, col

    def move_is_legal(self, piece, row, col):
        if (not isinstance(piece, Piece)) or piece.side != self.side:
            return False
        piece_row, piece_col = self.get_loc(piece)
        if isinstance(self.board[row][col], Piece) and self.board[row][col].side == piece.side:
            return False
        return ((piece_row == row ^ piece_col == col) and
                (piece.num == 2 or (abs(piece_row - row) == 1) ^ (abs(piece_col - col) == 1))) and piece.can_move()

    def move_piece(self, piece_row, piece_col, row, col):
        piece = self.board[piece_row][piece_col]
        if not self.move_is_legal(piece, row, col):
            return False

        if not self.board[row][col] is None:
            enemy = self.board[row][col]
            piece.known = True
            enemy.known = True
            if enemy > piece:
                self.board[piece_row][piece_col] = None
                self.outside.append(piece)
                return True
            elif enemy == piece:
                self.board[piece_row][piece_col] = None
                self.outside.append(piece)
                self.board[row][col] = None
                self.outside.append(enemy)
                return True
            else:
                self.outside.append(enemy)

        self.board[row][col] = piece
        self.board[piece_row][piece_col] = None
        return True

    def input_placement_policy(self):
        print(f"Player {self.side}, setting pieces.")
        placement = {}
        for p in self.outside:
            if p.side != self.side:
                continue
            row, col = self.reader.input(f"Choose {p.num} placement (\"row col\"): ").split(" ")
            row = int(row)
            col = int(col)
            placement[p.hash()] = (row, col)
        return placement

    def game_over(self):
        for p in self.outside:
            if p.num == -1:
                print(f"Player {(p.side + 1) % 2} has won!")
                return True
            return False

    def input_move(self):
        piece_row, piece_col = self.reader.input(
            f"Player {self.side}\nEnter row and column of the piece you want to move" + \
            " (\"row\" \"col\"): ").split(' ')
        piece_row = int(piece_row)
        piece_col = int(piece_col)
        target_row, target_col = self.reader.input(
            "Enter where do you want to go with the chosen piece (\'row\' \'col\'): ").split(' ')
        target_row = int(target_row)
        target_col = int(target_col)
        return piece_row, piece_col, target_row, target_col

    def str(self):
        board_str = ""
        for row_id in range(len(self.board)):
            row = self.board[row_id]
            board_str += f"{row_id} "
            for p in row:
                if p is None:
                    board_str += "    "
                elif isinstance(p, str):
                    board_str += 'XXX '
                else:
                    board_str += f"{p.str(self.side)} "
            board_str += "\n"
        board_str += "   "
        for i in range(len(self.board)):
            board_str += f"{i}   "
        board_str += "\n"
        return board_str

    def play(self):
        print(self.str())
        pieces_set = [False, False]
        game_over = False
        while not all(pieces_set):
            self.side = pieces_set.index(False)
            policy = self.input_placement_policy()
            pieces_set[self.side] = self.set_pieces(policy)
            if pieces_set[self.side]:
                print(self.str())
            else:
                print("Illegal placement!")

        self.side = 0
        move_made = [False, False]
        while True:
            if all(move_made):
                move_made = [False, False]
            self.side = move_made.index(False)
            print(self.str())
            print(f"Player {self.side} turn")
            move_made[self.side] = self.move_piece(*self.input_move())
            if self.game_over():
                return

            # while self.pieces[(-1, 0, 1)] not in self.outside and self.pieces[(-1, 0, 0)] not in self.outside:


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    game = Game('game.txt')
    game.play()
