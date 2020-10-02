# handles fov using built in tcod functionality
# from: http://rogueliketutorials.com/tutorials/tcod/part-4/

import tcod

# initializes an fov map
def initialize_fov(game_map):
    fov_map = tcod.map_new(game_map.width, game_map.height)

    for x in range(game_map.width):
        for y in range(game_map.height):
            tcod.map_set_properties(fov_map, x, y, not game_map.tiles[x][y].block_sight, not game_map.tiles[x][y].blocked)

    return fov_map

# recomputes fov map based on player position
def recompute_fov(fov_map, x, y, radius, light_walls, algorithm):
    tcod.map_compute_fov(fov_map, x, y, radius, light_walls, algorithm)