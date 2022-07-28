from tictactoe import Board, Game, RandomPlayer
import random
from settings import Settings


def inverse_key(key):
    """just change the game perspective to the other player"""
    new_key, mapping = "", {'X': 'O', 'O': 'X', ' ': ' '}
    for c in key:
        new_key += mapping[c]
    return new_key


def run_a_game(start="X"):
    """Run a single game and give back the history of the game and who wins"""
    game = Game(start=start, size=3, player_x_class=RandomPlayer, player_o_class=RandomPlayer)
    previous_key, winner, history, current_player = game.board.key, False, [], start
    while winner is False:
        done, winner = game.move(False)
        if done:
            # a move happened, save all relevant informations as a history entry
            history.append({'start' : start, 'player': current_player,
                            'move' : done, 'previous': previous_key})
            # save the current board key, after the next move the new board key has the key after that move
            previous_key = game.board.key
            # toggle player
            current_player = "X" if current_player == "O" else "O"
    # reverse the history, so it's easier for the reward to start the analyzing from the beginning of the list
    return list(reversed(history)), winner


def get_reward(history, winner):
    """Get the rewards for a complete game and every move in the game chain"""
    if winner:
        # if we win it's good, losing is bad
        reward = 2.0 if winner.char == "X" else -5.0
    else:
        # if no one wins it's still somehow ok
        reward = 0.75 if history[0]['start'] == "O" else 0.5
    rewards = {}
    for move_x in history:
        if move_x['player'] == "X":
            # give the relevant move and all the previous moves some reward
            rewards.setdefault(move_x['previous'], {}).setdefault(move_x['move'], 0)
            rewards[move_x['previous']][move_x['move']] += reward
            # previous moves get more and more unimportant
            reward = reward * 0.6
    return rewards


def get_recommended_move_mapping(mapping):
    """ Reduce a dictionary with possible moves for every board key to a single move recommendation for the highest reward value"""
    recommended_mapping = {}
    for board_key in mapping.keys():
        current_value, recommended_move = None, None
        # find the max value in the dict of all possible moves
        for move_key in mapping[board_key].keys():
            if current_value is None or mapping[board_key][move_key] > current_value:
                # found a new max
                current_value = mapping[board_key][move_key]
                recommended_move = move_key
        recommended_mapping[board_key] = recommended_move
        # setting also the inversed board key, so the trained model could not only play as 'X'
        recommended_mapping[inverse_key(board_key)] = recommended_move
    return recommended_mapping


def run_games(start="X", games_to_play=200000):
    """Running a series of test games, output is a mapping dict with a recommendation for every board key"""
    mapping = {}
    for current_game in range(games_to_play):
        if (current_game % 10000) == 0 and current_game:
            # Just some little console output, so you could see it's still working :-)
            print("run game {}/{}".format(current_game, games_to_play))
        # pick randomly a player to start with
        start =  "X" if random.randint(0, 1) else "O"
        history, winner = run_a_game(start=start)
        # getting the rewards for the current game
        rewards = get_reward(history, winner)
        for reward_key in rewards.keys():
            # bringing all the rewards together in one big mapping
            for move_key in rewards[reward_key].keys():
                mapping.setdefault(reward_key, {}).setdefault(move_key, 0)
                mapping[reward_key][move_key] += rewards[reward_key][move_key]
    return get_recommended_move_mapping(mapping)


def main():
    settings = Settings()
    settings.save(run_games())


if __name__ == "__main__":
    main()
