# makes maps for each floor

import tcod
from random import randint

from map_objects.tile import Tile
from map_objects.rectangle import Rect
from entity import Entity, Enemy, Stairs

# stores map as a 2d list of tiles
class GameMap:
    # constructor makes empty map
    def __init__(self, width, height, depth=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        # initializes stairs entity within map and depth
        self.stairs = Stairs(0, 0, '>', tcod.black, 'stairs')
        self.depth = 1

        # cant see whole map by defualt
        self.lights_on = False

        # initializes colors for a map
        self.colors = {
            'dark_wall': None,
            'dark_ground': None,
            'light_wall': None,
            'light_ground': None
        }

    # inititializes 2d list of impassable (wall) tiles with the maps width and height
    # from: http://rogueliketutorials.com/tutorials/tcod/part-3/
    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    # makes map by choosing an algorithm at random
    def make_map(self, player, entities):
        algorithm = randint(0,2)
        # basic rectangle algorithm
        if (algorithm == 0):
            self.make_basic_map(player, entities)
        # bsp algorithm
        elif (algorithm == 1):
            self.make_bsp_map(player, entities)
        # random walk algorithm
        else:
            self.make_random_walk_map(player, entities)

    # generates a map by digging out rectangles and connecting them with tunnels
    # modified from: http://rogueliketutorials.com/tutorials/tcod/part-3/
    def make_basic_map(self, player, entities):
        # gets dimensions
        map_width = self.width
        map_height = self.height
        map_area = map_width * map_height

        # sets parameters for map gen using ratios that can be tweaked to affect the results
        max_rooms = int(map_area/200)
        room_min_size = int(map_area/2000)
        room_max_size = int(map_area/400)

        # sets parameters for enemies
        max_enemies_per_room = 2
        enemy_max_hp =  3
        enemy_power = 3
        enemy_char = 'w'
        enemy_name = 'wolf'

        # sets colors for this kind of floor (blue and yellow)
        self.colors['dark_wall'] = tcod.Color(68, 200, 226)
        self.colors['dark_ground'] = tcod.Color(37, 168, 255)
        self.colors['light_wall'] = tcod.Color(180, 160, 50)
        self.colors['light_ground'] = tcod.Color(200, 180, 50)
        player.color = tcod.yellow
        stairs_color = tcod.yellow
        enemy_color = tcod.yellow
        
        # keeps track of rooms that have been made
        rooms = []
        num_rooms = 0

        # make rooms up to the max number of rooms
        for r in range(max_rooms):
            # random width and height within parameters
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width-w-1)
            y = randint(0, map_height-h-1)

            # Rect class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            for other_room in rooms:
                if (new_room.intersect(other_room)):
                    break 

            # this means there are no intersections, so this room is valid
            else:
                # add it to the map's tiles
                self.create_rect_room(new_room)

                # center coordinates of new room
                (new_x, new_y) = new_room.center()

                # this is the first room, where the player starts at
                if (num_rooms == 0):
                    player.x = new_x
                    player.y = new_y

                else:
                    # all rooms after the first:
                    # connect it to the previous room with two tunnels, one horizontal and one vertical

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms-1].center()

                    # flip a coin
                    if (randint(0, 1) == 1):
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                    # places enemies in new room
                    self.place_enemies(new_room, entities, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, enemy_color)

                # append the new room to the list
                rooms.append(new_room)
                num_rooms += 1
        
        # places stairs at random and puts them in entities list
        self.make_stairs(player, map_width, map_height, stairs_color)
        entities.append(self.stairs)

    # helper function to place stairs at random on a floor
    def make_stairs(self, player, map_width, map_height, color):
        # sets the stairs position at random and color 
        self.stairs.x = randint(0, map_width-1)
        self.stairs.y = randint(0, map_height-1)
        self.stairs.color = color

        # checks to make sure location is in a room and that its a sufficent distance away from the player
        while (self.is_blocked(self.stairs.x, self.stairs.y) or (self.stairs.distance_to(player) < map_height/3)):
            self.stairs.x = randint(0, map_width-1)
            self.stairs.y = randint(0, map_height-1)

    # places enemies for map gen algorithms that don't use rectangular rooms
    # based on: http://rogueliketutorials.com/tutorials/tcod/part-5/
    def place_enemies_in_open_map(self, map_width, map_height, entities, min_enemies, max_enemies, enemy_max_hp, enemy_power, enemy_char, enemy_name, enemy_color):
        num_enemies = randint(min_enemies, max_enemies)

        for i in range(num_enemies):
            enemy_x = randint(1, map_width-1)
            enemy_y = randint(1, map_height-1)

            while self.is_blocked(enemy_x, enemy_y):
                enemy_x = randint(1, map_width-1)
                enemy_y = randint(1, map_height-1)

            if not any([entity for entity in entities if entity.x == enemy_x and entity.y == enemy_y]):
                enemy = Enemy(enemy_x, enemy_y, enemy_char, enemy_color, enemy_max_hp, 0, enemy_power, enemy_name)
                entities.append(enemy)

    # places enemies in a room
    # modified from: http://rogueliketutorials.com/tutorials/tcod/part-5/
    def place_enemies(self, room, entities, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, color):
        # chooses random number of enemies up to max
        num_enemies = randint(0, max_enemies_per_room)

        for i in range(num_enemies):
            # picks random spot within room
            enemy_x = randint(room.x1+1, room.x2-1)
            enemy_y = randint(room.y1+1, room.y2-1)

            # checks to make sure new enemy wont be overlapping with any other entities
            if not any([entity for entity in entities if entity.x == enemy_x and entity.y == enemy_y]):
                # makes enemies with given characteristics
                enemy = Enemy(enemy_x, enemy_y, enemy_char, color, enemy_max_hp, 0, enemy_power, enemy_name)
                entities.append(enemy)


    # go through the tiles in the rectangle object and make them passable (floors)
    # from: http://rogueliketutorials.com/tutorials/tcod/part-3/
    def create_rect_room(self, room):
        # non-inclusive so the cleared space is within the rectangle. walls are the sides of the rectangle
        for x in range(room.x1+1, room.x2):
            for y in range(room.y1+1, room.y2):
                # "carves out" the tile, making it into a passable floor tile
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    # creates a straight horizontal "tunnel" or line of cleared floor tiles
    # from: http://rogueliketutorials.com/tutorials/tcod/part-3/
    def create_h_tunnel(self, x1, x2, y):
        left = min(x1, x2)
        right = max(x1, x2)
        # inclusive so the left and right points will be cleared as well
        for x in range(left, right + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    # creates a straight vertical tunnel
    # from: http://rogueliketutorials.com/tutorials/tcod/part-3/
    def create_v_tunnel(self, y1, y2, x):
        top = min(y1, y2)
        bottom = max(y1, y2)
        # inclusive so the left and right points will be cleared as well
        for y in range(top, bottom+1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    # checks a tile to see if its blocked
    # from: http://rogueliketutorials.com/tutorials/tcod/part-3/
    def is_blocked(self, x, y):
        if (self.tiles[x][y].blocked == True):
            return True
        else: return False

    # creates a map of connected rectangles that is random but fills space a little more evenly
    # works by partioning the map into two containers and then recursively partioning those containers in the same way
    # each container is then filled with a room
    def make_bsp_map(self, player, entities):
        # gets dimensions -1 to leave a broder around console
        map_width = self.width -1
        map_height = self.height-1

        # sets parameters and colors by choosing a preset at random
        # max_depth is the number of times the containers will be partioned. increase for more smaller rooms
        # width to height ratios set allowable ratios for partitioning. set it tighter (close to 1) and the algorithm will widen it as neccasary
        # padding sets the amount of padding rooms are made with. higher means smaller more seperated rooms on average
        preset = randint(0,3)
        # rooms right against eachother. jail-like. many weak enemies
        if preset == 0:
            max_depth = 7 # lots of partitions
            min_width_to_height = 0.75
            max_width_to_height = 1.5  
            max_padding_ratio = 0 #no padding
            padding_min = 0

            max_enemies_per_room = 1
            enemy_max_hp =  2
            enemy_power = 3
            enemy_char = 'c'
            enemy_name = 'convict'

            self.colors['dark_wall'] = tcod.Color(21, 21, 21)
            self.colors['dark_ground'] = tcod.Color(39, 39, 39)
            self.colors['light_wall'] = tcod.Color(30, 30, 30)
            self.colors['light_ground'] = tcod.Color(60, 60, 60)
            player.color = tcod.orange
            stairs_color = tcod.orange
            enemy_color = tcod.orange

        # standard looking bsp dungeon. average rooms and corridors
        elif preset == 1:
            max_depth = 5
            min_width_to_height = 0.75
            max_width_to_height = 1.5  
            max_padding_ratio = 1/3
            padding_min = 1

            max_enemies_per_room = 2
            enemy_max_hp =  3
            enemy_power = 3
            enemy_char = 'T'
            enemy_name = 'troll'

            self.colors['dark_wall'] = tcod.Color(0, 0, 100)
            self.colors['dark_ground'] = tcod.Color(50, 50, 150)
            self.colors['light_wall'] = tcod.Color(130, 110, 50)
            self.colors['light_ground'] = tcod.Color(200, 180, 50)
            player.color = tcod.white
            stairs_color = tcod.white
            enemy_color = tcod.white

        # more rooms that are smaller
        elif preset == 2:
            max_depth = 6 # higher depth so more recursive splits
            min_width_to_height = 0.75
            max_width_to_height = 1.5  
            max_padding_ratio = 1/3
            padding_min = 0

            max_enemies_per_room = 1
            enemy_max_hp =  2
            enemy_power = 3
            enemy_char = 'r'
            enemy_name = 'rat'

            self.colors['dark_wall'] = tcod.Color(10, 10, 10)
            self.colors['dark_ground'] = tcod.Color(34, 34, 34)
            self.colors['light_wall'] = tcod.Color(15, 15, 15)
            self.colors['light_ground'] = tcod.Color(50, 50, 50)
            player.color = tcod.red
            stairs_color = tcod.red
            enemy_color = tcod.red

        # big rooms
        else:
            max_depth = 4 # less splits
            min_width_to_height = 0.65 # higher variance
            max_width_to_height = 1.7  
            max_padding_ratio = 3/8 # more room for padding, higher variance
            padding_min = 1

            max_enemies_per_room = 3
            enemy_max_hp =  2
            enemy_power = 3
            enemy_char = 'O'
            enemy_name = 'orc'

            self.colors['dark_wall'] = tcod.Color(10, 10, 10)
            self.colors['dark_ground'] = tcod.Color(45, 48, 71)
            self.colors['light_wall'] = tcod.Color(15, 15, 15)
            self.colors['light_ground'] = tcod.Color(60, 67, 90)
            player.color = tcod.Color(250, 72, 85)
            stairs_color = tcod.Color(250, 72, 85)
            enemy_color = tcod.Color(250, 72, 85)

        # actually makes the map
        self.bsp(0, 0, map_width, map_height, min_width_to_height, max_width_to_height, padding_min, max_padding_ratio, entities, enemy_color, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, max_depth)

        # randomly places player in unblocked spot
        player_x = randint(1, map_width-1)
        player_y = randint(1, map_height-1)
        while self.is_blocked(player_x, player_y):
            player_x = randint(1, map_width-1)
            player_y = randint(1, map_height-1)
        player.x = player_x
        player.y = player_y

        # places stairs at random
        self.make_stairs(player, map_width, map_height, stairs_color)
        entities.append(self.stairs)

    # recursive helper fuction that makes a map using bsp algorithm
    def bsp(self, x, y, width, height, min_width_to_height, max_width_to_height, padding_min, max_padding_ratio, entities, enemy_color, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, depth):
        # base case: when map has been partioned the appropriate number of times, set by depth parameter, stop partitioning and make a room in given container
        if (depth == 0):
            # padding puts space in between edge of container and the walls of the room
            # padding ratio determines max amount of padding based on dimensions of room
            room_width_padding = randint(padding_min, int(width*max_padding_ratio))
            room_height_padding = randint(padding_min, int(height*max_padding_ratio))

            # actually makes room and puts in in map
            new_room = Rect(x+room_width_padding, y+room_height_padding, width-room_width_padding, height-room_height_padding)
            self.create_rect_room(new_room)

            # places enemies in rooms
            self.place_enemies(new_room, entities, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, enemy_color)

        # recursive case: partion the space into to pieces randomly and make a tunnel between them
        else:
            # flip a coin to decide whether space is split horizontally or vertically
            if (randint(0,1) == 0):
                # splits into right and left pieces, left chosen randomly, right takes the rest
                left_width = randint(0, width)  
                right_width = width - left_width

                # re-partitions if the width to height ratio is too small for either partition
                if (min(left_width/height, right_width/height) < min_width_to_height):
                    # every time it retries the partition it widens the ratio allowance to prevent infinite recursion
                    # This means earlier partitions will be more even and later partitions will be more random
                    self.bsp(x, y, width, height, min_width_to_height*0.99, max_width_to_height*1.01, padding_min, max_padding_ratio, entities, enemy_color, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, depth)

                # if dimensions are appropriate, make the containers and recurse
                else:
                    # makes rectangles that track the x, y position of the partitions
                    left_partition = Rect(x, y, left_width, height)
                    right_partition = Rect(x+left_width, y, right_width, height)

                    # gets centers of partitions for the tunnel
                    (left_center_x, left_center_y) = left_partition.center()
                    (right_center_x, right_center_y) = right_partition.center()

                    # makes tunnel from center of one new partition to the other. this ensures all rooms are connected
                    self.create_h_tunnel(left_center_x, right_center_x, left_center_y)
                    
                    # recursively partitions the left and right pieces
                    self.bsp(left_partition.x1, left_partition.y1, left_width, height, min_width_to_height, max_width_to_height, padding_min, max_padding_ratio, entities, enemy_color, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, depth-1)
                    self.bsp(right_partition.x1, right_partition.y1, right_width, height, min_width_to_height, max_width_to_height, padding_min, max_padding_ratio, entities, enemy_color, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, depth-1)

            # horizontal split
            else:
                # splits into top and bottom pieces, top chosen randomly, bottom takes the rest.
                top_height = randint(1, height-1) # 1 prevents division by 0   
                bottom_height = height - top_height

                # re-partitions if the width to height ratio is too small for either partition
                if (max(width/top_height, width/bottom_height) > max_width_to_height):
                    # every time it retries the partition it widens the ratio allowance to prevent infinite recursion
                    self.bsp(x, y, width, height, min_width_to_height*0.99, max_width_to_height*1.01, padding_min, max_padding_ratio, entities, enemy_color, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, depth)

                # if dimensions are appropriate, make the containers and recurse
                else:
                    # makes rectangles that track the x, y position of the partitions
                    top_partition = Rect(x, y, width, top_height)
                    bottom_partition = Rect(x, y+top_height, width, bottom_height)

                    # gets centers of partitions for the tunnel
                    (top_center_x, top_center_y) = top_partition.center()
                    (bottom_center_x, bottom_center_y) = bottom_partition.center()

                    # makes tunnel from center of one new partition to the other. this ensures all rooms are connected
                    self.create_v_tunnel(top_center_y, bottom_center_y, top_center_x)
                    
                    # recursively partitions the top and bootom pieces, reduces depth by 1
                    self.bsp(top_partition.x1, top_partition.y1, width, top_height, min_width_to_height, max_width_to_height, padding_min, max_padding_ratio, entities, enemy_color, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, depth-1)
                    self.bsp(bottom_partition.x1, bottom_partition.y1, width, bottom_height, min_width_to_height, max_width_to_height, padding_min, max_padding_ratio, entities, enemy_color, max_enemies_per_room, enemy_max_hp, enemy_power, enemy_char, enemy_name, depth-1)

    # generates a dugeon by carving out tiles in a path at random. does not use rooms and tunnels
    def make_random_walk_map(self, player, entities):
        # gets dimensions
        map_width = self.width
        map_height = self.height
        total_map_area = map_width * map_height

        # sets tiles to be cleared in relation to total area
        tiles_to_be_cleared = int(total_map_area * 1.5)

        # sets parameters for enemies
        min_enemies = 5
        max_enemies = 15
        enemy_max_hp = 2
        enemy_power = 3
        enemy_char = 'r'
        enemy_name = 'rat'

        # sets colors for floor
        self.colors['dark_wall'] = tcod.Color(21, 21, 21)
        self.colors['dark_ground'] = tcod.Color(39, 39, 39)
        self.colors['light_wall'] = tcod.Color(30, 30, 30)
        self.colors['light_ground'] = tcod.Color(60, 60, 60)
        player.color = tcod.orange
        stairs_color = tcod.orange
        enemy_color = tcod.orange
        
        # picks a random starting point and clears that tile
        starting_x = randint(1, map_width-1)
        starting_y = randint(1, map_height-1)
        self.tiles[starting_x][starting_y].blocked = False
        self.tiles[starting_x][starting_y].block_sight = False

        # puts player at first cleared tile
        player.x = starting_x
        player.y = starting_y

        # list of possible directions to go (up, down, right, left)
        possible_directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]

        # keeps track of how many tiles have ben cleared
        cleared_tiles = 1

        # clears one tile per iteration. one tile already cleared at starting point
        while cleared_tiles <= tiles_to_be_cleared:
            # picks a direction at random
            direction = randint(0, 3)

            #checks to make sure it doesn't walk out of bounds
            while (starting_x + possible_directions[direction][0] >= map_width-1 or
                   starting_x + possible_directions[direction][0] < 1 or
                   starting_y + possible_directions[direction][1] >= map_height-1 or
                   starting_y + possible_directions[direction][1] < 1):
                # pick a new direction if its about to go out of bounds
                direction = randint(0, 3)

            # moves to new tile and clears it
            new_tile_x = starting_x + possible_directions[direction][0]
            new_tile_y = starting_y + possible_directions[direction][1]
            self.tiles[new_tile_x][new_tile_y].blocked = False
            self.tiles[new_tile_x][new_tile_y].block_sight = False
            cleared_tiles += 1

            # sets new tile as the starting point for the next iteration
            starting_x = new_tile_x
            starting_y = new_tile_y

        # places stairs
        self.make_stairs(player, map_width, map_height, stairs_color)
        entities.append(self.stairs)

        # places enemies
        self.place_enemies_in_open_map(map_width, map_height, entities, min_enemies, max_enemies, enemy_max_hp, enemy_power, enemy_char, enemy_name, enemy_color)






