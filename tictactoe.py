import re


class Player:
    COLOR_RED, COLOR_GREEN, COLOR_RESET = "\u001b[31m", "\u001b[32m", "\u001b[0m"

    def __init__(self, char=" "):
        self.char = char

    def __str__(self):
        return "{}{}{}".format((Player.COLOR_RED if self.char == 'X' else Player.COLOR_GREEN if self.char == 'O' else ""), self.char, Player.COLOR_RESET)


class Board:
    START_KEY = "         "
    CROSS_WINS_REGEXP = r"^(.{0,2}X..X..X|(...){0,2}XXX|X...X...X|..X.X.X)"
    CIRCLE_WINS_REGEXP = CROSS_WINS_REGEXP.replace('X', 'O')
    NO_ONE_WINS_REGEXP = r"^\S+$"
    VISUALIZE = "\n  0 1 2\n0 {}|{}|{}\n  -+-+-\n1 {}|{}|{}\n  -+-+-\n2 {}|{}|{}\n\n"

    def __init__(self, key=START_KEY):
        self.key = key

    def _verify(self):
        if re.match(Board.CROSS_WINS_REGEXP, self.key):
            return True, Player('X')
        if re.match(Board.CIRCLE_WINS_REGEXP, self.key):
            return True, Player('O')
        if re.match(Board.NO_ONE_WINS_REGEXP, self.key):
            return True, None
        return False, False

    def add(self, player, index):
        if self.key[index] == " ":
            self.key = self.key[:index] + player.char + self.key[index + 1:]
            return (True,) + self._verify()
        return False, False, False

    def __str__(self):
        return Board.VISUALIZE.format(*[str(Player(x)) for x in self.key])


class Game:
    INPUT_REGEXP = r"^ *([0-2]) *([0-2]) *$"

    def __init__(self, start='X'):
        self.players, self.player_index = [], 0
        self.players.append(Player(start))
        self.players.append(Player('O' if start == 'X' else 'X'))
        self.board = Board()

    def _toggle_user(self):
        self.player_index = abs(self.player_index - 1)

    def _current_player(self):
        return self.players[self.player_index]

    def move(self, index):
        done, finished, winner = self.board.add(self._current_player(), index)
        if done:
            if finished:
                return None, winner
            else:
                self._toggle_user()
            return self._current_player(), winner
        return False, False

    def manual_move(self):
        print("{}\nplayer '{}' please move now. (f.e. '01' for column 0 and row 1): ".format(self.board, self._current_player()), end='')
        match = re.search(Game.INPUT_REGEXP, str(input()))
        if not match:
            print("\nplease enter 2 numbers between 0-2")
            return self._current_player(), False
        next_player, winner = self.move(int(match.group(1)) + 3 * int(match.group(2)))
        if not next_player and winner is False:
            print("\nplease choose an empty cell.")
            return self._current_player(), False
        return next_player, winner


def main():
    game, winner = Game(), False
    while winner is False:
        next_player, winner = game.manual_move()
    print(game.board)
    if winner is None:
        print("No one wins!\n")
    else:
        print(f"the winner is player '{winner}'!\n")


if __name__ == "__main__":
    main()
