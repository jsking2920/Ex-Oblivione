# keeps track of game states
# from: http://rogueliketutorials.com/tutorials/tcod/part-5/

from enum import Enum

class GameStates(Enum):
    PLAYERS_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEATH = 3
    PLAYER_WINS = 4