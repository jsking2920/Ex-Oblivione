# initializes a new game on start up by setting constants
# Modified and expanded from: http://rogueliketutorials.com/tutorials/tcod/part-10/

import tcod

from entity import Entity, Fighter
from map_objects.game_map import GameMap
from game_messages import MessageLog, Message
from fov_functions import initialize_fov

# returns constants neccasary to set up game
def get_constants():
    # sets title of the game window (name comes from an H.P. Lovecraft poem)
    window_title = 'Ex Oblivione'

    # dimensions of window
    screen_width = 120
    screen_height = 82

    # dimensions of map
    map_width = 120
    map_height = 75

    # dimensions of UI panel, bars, and message log
    bar_width = 25
    panel_height = 7
    panel_y = screen_height - panel_height
    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    # field of view settings
    fov_algorithm = 0 # what alg. tcod will use
    fov_light_walls = True # whether walls get lit up or not
    default_fov_radius = 10 # radius that player can see by default

    # player beginning stats
    player_max_hp = 50
    player_start_power = 2
    player_max_mp = 50

    # sets amount of turns in between hp and mp regeneration
    hp_regen_delay = 10
    mp_regen_delay = 10

    # The floor on which the player wins the game 
    winning_floor = 4

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'map_width': map_width,
        'map_height': map_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'default_fov_radius': default_fov_radius,
        'player_max_hp': player_max_hp,
        'player_max_mp': player_max_mp,
        'player_start_power': player_start_power,
        'hp_regen_delay': hp_regen_delay,
        'mp_regen_delay': mp_regen_delay,
        'winning_floor': winning_floor
    }

    return constants

# intitializes game variables
def get_game_variables(constants):
    player = Fighter(0, 0, '@', None, constants['player_max_hp'], constants['player_max_mp'], constants['player_start_power'], 'player', constants['default_fov_radius'])
    entities = [player]

    # initializes variables to track when a player regenerates hp and mp
    hp_regen_tick = 0
    mp_regen_tick = 0

    # initializes a blank map
    game_map = GameMap(constants['map_width'], constants['map_height'])
    # chooses algorithm at random to make a map
    game_map.make_map(player, entities)

    # sets up fov map and initializes value telling game whether or not it needs to redraw the players fov
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    # sets up message log and prints start-up messages
    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])
    message_log.add_message(Message('Welcome to Ex Oblivione', tcod.yellow))
    message_log.add_message(Message('Reach floor 4 to win'))

    return player, entities, game_map, fov_recompute, fov_map, message_log, hp_regen_tick, mp_regen_tick