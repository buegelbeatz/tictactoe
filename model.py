import re
from tictactoe import Board, Player

class Model:
    BOARD_KEY_REGEXP = r"^(O|X):(.)(.)(.)(.)(.)(.)(.)(.)(.)$"
    ROTATE_RIGHT_OUTPUT = r"\1:\8\5\2\9\6\3\10\7\4"
    MIRROW_RIGHT_OUTPUT = r"\1:\4\3\2\7\6\5\10\9\8"
    MEMORY_KEY = "{}:{}"

    def __init__(self):
        self.memory = {}

    def _rotate_key(self, key, repeat=0):
        if not repeat:
            return re.sub(Model.BOARD_KEY_REGEXP, Model.ROTATE_RIGHT_OUTPUT, key)
        return re.sub(Model.BOARD_KEY_REGEXP, Model.ROTATE_RIGHT_OUTPUT, self._rotate_key(key, repeat - 1))

    def _mirrow_key(self, key):
        return re.sub(Model.BOARD_KEY_REGEXP, Model.MIRROW_RIGHT_OUTPUT, key)

    def _inverse(self, key):
        return key.replace('X', 'temp').replace('O', 'X').replace('temp', 'O')

    def _get_transformed_keys(self, key):
        return [self._rotate_key(key, _index) for _index in range(3)] + [self._mirrow_key(key)] + [self._mirrow_key(self._rotate_key(key))]

    def _set_all_related(self, key):
        _transformed_keys = self._get_transformed_keys(key)
        _all_keys = _transformed_keys + [self._inverse(_key) for _key in _transformed_keys]
        for _key in _all_keys:
            if _key not in self.memory.keys():
                self.memory[_key] = {'parent': key}
                self.memory[key]['childs'].append(_key)

    def _set_weight(self, memory_key, index, value):
        self.memory[memory_key]['weights'][index] += value
        if self.memory[memory_key]['previous_key']:
            self._set_weight(self.memory[memory_key]['previous_key'], self.memory[memory_key]['previous_move'], value / 2)

    def _cleanup(self):
        pass

    def train(self, player=Player('X'), board=Board(), previous_key=None, previous_move=None):
        memory_key = Model.MEMORY_KEY.format(player.char, board.key)
        if memory_key not in self.memory.keys():
            self.memory[memory_key] = {'weights': [0, 0, 0, 0, 0, 0, 0, 0, 0], 'childs': [], 'previous_key': previous_key, 'previous_move': previous_move}
            self._set_all_related(memory_key)
            for index in range(9):
                _board = Board(board.key)
                done, winner = _board.add(player, index)
                if done:
                    if winner:
                        self._set_weight(memory_key, index, 3.0 if winner.char == 'X' else -2.0 if winner.char == 'O' else -1.0)
                    if winner is False:
                        self.train(player=Player('X' if player.char == 'O' else 'O'), board=_board, previous_key=memory_key, previous_move=index)
        if not previous_key:
            self._cleanup()

    def lookup(self):
        pass

def main():
    model = Model()
    model.train()
    print({k: v for k, v in model.memory.items() if 'parent' not in model.memory[k]})

if __name__ == "__main__":
    main()
