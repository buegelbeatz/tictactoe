import random
import os
import re
import math
from settings import Settings

class Player:
    COLOR_RED, COLOR_GREEN, COLOR_RESET = "\u001b[31m", "\u001b[32m", "\u001b[0m"
    REGEXP_MAGIC_TEMPLATE = r"^((.{n}){0,nm1}(P){n}|.{0,nm1}(P.{nm1}){nm1}P|(P.{n}){nm1}P|.{nm1}(P.{nm2}){nm1}P)"

    def __init__(self, char=" ", size=3):
        self.char = char
        self.win_regexp = Player.REGEXP_MAGIC_TEMPLATE.replace("nm1", str(size - 1)).replace("nm2", str(size - 2)).replace("n", str(size)).replace("P", char)
        self.could_still_win = self.win_regexp.replace(char, r"({}|\s)".format(char))
        self.other_player_could_still_win = self.could_still_win.replace(char, "X" if char == "O" else "O")

    def wins(self, board):
        return self if re.match(self.win_regexp, board.key) else False

    def no_one_could_win(self, board):
        return not (re.match(self.could_still_win, board.key) or re.match(self.other_player_could_still_win, board.key))

    def __str__(self):
        return Player.str(self.char)

    def get_input(self, board):
        raise Exception("'get_input' needs to be implemented!")

    def str(char):
        return "{}{}{}".format((Player.COLOR_RED if char == 'X' else Player.COLOR_GREEN if char == 'O' else ""), char, Player.COLOR_RESET)


class HumanPlayer(Player):
    def get_input(self, board):
        return str(input())


class RandomPlayer(Player):
    def get_input(self, board):
        return str(random.randint(0, board.size - 1)) + str(random.randint(0, board.size - 1))


class TrainedPlayer(Player):
    def __init__(self, char=' ', size=3):
        super().__init__(size=size, char=char)
        settings = Settings(size)
        self.recommendations = settings.load()
        if not self.recommendations:
            raise Exception("Please run the training program first...")

    def get_input(self, board):
        if board.key in self.recommendations.keys():
            return self.recommendations[board.key]
        else:
            return str(random.randint(0, board.size - 1)) + str(random.randint(0, board.size - 1))


class Board:
    def __init__(self, key=None, size=3):
        self.size, self.key = size, key if key is not None else " " * size * size
        self.visualize_format = "\n".join(
          [""] + ["  " + " ".join([str(i) for i in range(self.size)]) + "+".join(["-" for i in range(self.size)]).join(
            ["\n{} {}\n  ".format(str(i), "|".join(["{}" for i in range(self.size)])) for i in range(self.size)])] + [""])

    def add(self, player, index):
        if self.key[index] != " ":
            return False, False
        self.key = self.key[:index] + player.char + self.key[index + 1:]
        if player.no_one_could_win(self):
            return True, None
        return True, player.wins(self)

    def __str__(self):
        return self.visualize_format.format(*[str(Player.str(x)) for x in self.key])


class Game:
    REGEXP_INPUT_TEMPLATE = r"^ *([0-nm1]) *([0-nm1]) *$"

    def __init__(self, start='X', size=3, player_x_class=Player, player_o_class=Player):
        self.regexp_input, self.size = Game.REGEXP_INPUT_TEMPLATE.replace("nm1", str(size - 1)), size if size <= 9 and size >= 3 else 3
        self.players, self.player_index, self.board = [player_x_class("X", size=self.size), player_o_class("O", size=self.size)], 0, Board(size=self.size)
        self.players = list(reversed(self.players)) if start == "O" else self.players

    def _current_player(self):
        return self.players[self.player_index]

    def _move(self, index):
        done, winner = self.board.add(self._current_player(), index)
        self.player_index = abs(self.player_index - 1) if done and winner is False else self.player_index
        return done, winner

    def move(self, log=True):
        if log: print("\x1b[2J\x1b[H{}\nplayer '{}' please move now. (f.e. '01' for column 0 and row 1): ".format(self.board, self._current_player()), end='')
        match = re.search(self.regexp_input, self._current_player().get_input(self.board))
        if not match:
            if log: print("\nplease enter 2 digits between 0-{}".format(self.size - 1))
            return False, False
        done, winner = self._move(int(match.group(1)) + self.size * int(match.group(2)))
        if log: print("\nplease choose an empty cell." if not done and winner is False else "")
        return match.group(0) if done else False, winner


def main():
    size = 3 if 'SIZE' not in os.environ.keys() or not re.match(r"^[3-9]$", os.environ['SIZE']) else int(os.environ['SIZE'])
    start = "X" if 'START' not in os.environ.keys() or not re.match(r"^(X|O)$", os.environ['START']) else os.environ['START']
    player_x_class, player_o_class = HumanPlayer, HumanPlayer
    if 'PLAYER_X' in os.environ.keys():
        if os.environ['PLAYER_X'] == 'RandomPlayer':
            player_x_class = RandomPlayer
        if os.environ['PLAYER_X'] == 'TrainedPlayer':
            player_x_class = TrainedPlayer
    if 'PLAYER_O' in os.environ.keys():
        if os.environ['PLAYER_O'] == 'RandomPlayer':
            player_o_class = RandomPlayer
        if os.environ['PLAYER_O'] == 'TrainedPlayer':
            player_o_class = TrainedPlayer

    game, winner = Game(size=size, player_x_class=player_x_class, player_o_class=player_o_class, start=start), False
    while winner is False:
        _, winner = game.move()
    print("\x1b[2J\x1b[H", game.board, "No one wins!\n" if winner is None else f"the winner is player '{winner}'!\n")


if __name__ == "__main__":
    main()
