### Tic Tac Toe

#### Training

First run

```bash
python3 ./train.py
```
This generates a file './tictactoe_recommended_mapping_3.json' which is used by the **TrainedPlayer** as recommendation.

#### Playing

Just run

```bash
PLAYER_X=TrainedPlayer PLAYER_O=RandomPlayer START=X   python3 ./tictactoe.py
```

You could also use **HumanPlayer** as parameter for *PLAYER_O* if you want to play against the trained model.
