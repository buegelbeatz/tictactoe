from tictactoe import Board, Game, RandomPlayer
import random
from settings import Settings

def inverse_key(key):
    new_key, mapping = "", {'X': 'O', 'O': 'X', ' ': ' '}
    for c in key:
        new_key += mapping[c]
    return new_key

def run_a_game(start="X"):
    game, winner, history, current_player = Game(start=start, size=3, player_x_class=RandomPlayer, player_o_class=RandomPlayer), False, [], start
    previous_key = game.board.key
    while winner is False:
        done, winner = game.move(False)
        if done:
            history.append({'start' : start, 'player': current_player,
                            'move' : done, 'previous': previous_key})
            previous_key = game.board.key
            current_player = "X" if current_player == "O" else "O"
    return list(reversed(history)), winner

def get_reward(history, winner):
    if winner:
        reward = 2.0 if winner.char == "X" else -5.0
    else:
        reward = 0.75 if history[0]['start'] == "O" else 0.5
    rewards = {}
    for move_x in history:
        if move_x['player'] == "X":
            rewards.setdefault(move_x['previous'], {}).setdefault(move_x['move'], 0)
            rewards[move_x['previous']][move_x['move']] += reward
            reward = reward * 0.6
    return rewards

def get_recommended_move_mapping(mapping):
    recommended_mapping = {}
    for board_key in mapping.keys():
        value, recommended_move = -10000.0, None
        for move_key in mapping[board_key].keys():
            if mapping[board_key][move_key] > value:
                value = mapping[board_key][move_key]
                recommended_move = move_key
        if recommended_move:
            recommended_mapping[board_key] = recommended_move
            recommended_mapping[inverse_key(board_key)] = recommended_move
    return recommended_mapping

def run_games(start="X", games_to_play=200000):
    mapping = {}
    for current_game in range(games_to_play):
        if (current_game % 10000) == 0 and current_game:
            print("run game {}/{}".format(current_game, games_to_play))
        start =  "X" if random.randint(0, 1) else "O"
        history, winner = run_a_game(start=start)
        rewards = get_reward(history, winner)
        for reward_key in rewards.keys():
            for move_key in rewards[reward_key].keys():
                mapping.setdefault(reward_key, {}).setdefault(move_key, 0)
                mapping[reward_key][move_key] += rewards[reward_key][move_key]
    return get_recommended_move_mapping(mapping)

def main():
    settings = Settings()
    settings.save(run_games())

if __name__ == "__main__":
    main()
