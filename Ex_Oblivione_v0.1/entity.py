# classes for game entities like the player and enemies
# from: http://rogueliketutorials.com/tutorials/tcod/part-2/   and part 5
import math
import tcod
from random import randint

from pathfinding import bfs_pathfinder
from game_messages import Message


# checks a location for entities that can't be walked through
def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity
    return None

# a generic object to represent players, enemies, items, etc.
class Entity:
    # stores position, representing char, name, color, and whether or not it can be walked through which is automatically false
    def __init__(self, x, y, char, color, name, blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name
    
    # move the entity by a given amount
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    # gets distance between two entities
    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)


# Everything below this is original work


# subclass for stairs that take player down to a new floor
class Stairs(Entity):
    def take_stairs(self, player, game_map, entities, message_log):
        # resets tiles and entities
        game_map.tiles = game_map.initialize_tiles()
        entities = [player]

        # makes map and adds one to depth to keep track of floor
        game_map.make_map(player, entities)
        game_map.depth += 1

        # prints a message telling player what floor they're on
        message_log.add_message(Message(f'You descend to floor {game_map.depth}', tcod.yellow))
        return entities

# class for etities that can engage in combat
class Fighter(Entity):
    # same traits as any entity but with an hp value (hit points), mp value (magic/mana points), and power stat. block is automatically set to true
    def __init__(self, x, y, char, color, max_hp, max_mp, power, name, fov_range=0):
        super().__init__(x, y, char, color, name, True)
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_mp = max_mp
        self.mp = max_mp
        self.power = power
        self.is_dead = False
        self.fov_range = fov_range # distance the entity can see. defaults to 0

    # deals damage to a targets hp based on power stat. kills target if hp is 0
    def attack(self, target, message_log):
        target.hp -= self.power
        message_log.add_message(Message(f'{target.name} takes {self.power} damage'))
        if target.hp <= 0:
            target.kill_entity(message_log)

    # heals an entity
    def heal(self, amount):
        if (self.hp + amount <= self.max_hp):
            self.hp += amount

    # restores entities mp
    def restore_mp(self, amount):
        if (self.mp + amount <= self.max_mp):
            self.mp += amount

    # deals a set amount of damage to enemies within a certain area of effect
    def cast_fireball(self, entities, message_log):
        # sets parameters for spell
        spell_cost = 15
        spell_range = 3
        spell_damage = 3
        spell_name = 'fireball'
        spell_color = tcod.red

        # only lets player cast spell if they have enough mp
        if self.mp >= spell_cost:
            
            # prints message saying a spell was cast
            message_log.add_message(Message(f'{self.name} casts {spell_name}', spell_color))

            # gets targets within range
            targets = []
            for entity in entities:
                if ((isinstance(entity, Enemy)) and (entity.is_dead == False) and (self.distance_to(entity) <= spell_range)):
                    targets.append(entity)

            # does damage to all targets
            for target in targets:
                target.hp -= spell_damage
                message_log.add_message(Message(f'{target.name} takes {spell_damage} damage from spell'))
                if target.hp <= 0:
                    target.kill_entity(message_log)
        
            # reduces entities mp by appropriate value
            self.mp -= spell_cost

        # tell the player they dont have enough mp
        else:
            message_log.add_message(Message(f"{self.name} must have {spell_cost} mp to cast {spell_name}", tcod.light_blue))

    # heals an entity proportional to their max_hp
    def cast_cure(self, message_log):
        # sets parameters for spell
        spell_cost = 20
        amount = int(0.25 * self.max_hp)
        spell_name = 'cure'
        spell_color = tcod.green

        # only lets player cast spell if they have enough mp
        if self.mp >= spell_cost:

            message_log.add_message(Message(f'{self.name} casts {spell_name} and heals for {amount}', spell_color))

            # heals up to entities max_hp
            if self.hp + amount > self.max_hp:
                self.hp = self.max_hp
            else:
                self.hp += amount

            # reduces entities mp by appropriate value
            self.mp -= spell_cost

        # tell the player they dont have enough mp
        else:
            message_log.add_message(Message(f"{self.name} must have {spell_cost} mp to cast {spell_name}", tcod.light_blue))

    # clears a tile in a straight line in a given direction
    def cast_tunnel(self, game_map, fov_map, message_log, dx, dy):
        # sets parameters for spell
        spell_cost = 3
        spell_name = 'tunnel'
        spell_color = tcod.sepia
        spell_range = 2

        # gets the tiles that are being targeted
        tiles_to_clear = []
        for i in range(spell_range):
            tile_x = self.x + (dx*(i+1))
            tile_y = self.y + (dy*(i+1))
            tiles_to_clear.append((tile_x, tile_y))

        # only lets player cast spell if they have enough mp
        if self.mp >= spell_cost:

            message_log.add_message(Message(f'{self.name} casts {spell_name}', spell_color))

            # clears tiles one by one, checking each to make sure they are clearable
            for tile in tiles_to_clear:
                tile_x = tile[0]
                tile_y = tile[1]

                # checks to make sure player stays in bounds
                if ((tile_x > 0) and (tile_x < game_map.width-1) and (tile_y > 0) and (tile_y < game_map.height-1)):
                    # clears the tile and updates the fov map appropriately
                    game_map.tiles[tile_x][tile_y].blocked = False
                    game_map.tiles[tile_x][tile_y].block_sight = False
                    tcod.map_set_properties(fov_map, tile_x, tile_y, not game_map.tiles[tile_x][tile_y].block_sight, not game_map.tiles[tile_x][tile_y].blocked)
                else:
                    message_log.add_message(Message('Wall is too strong', tcod.red))

            # reduces entities mp by appropriate value
            self.mp -= spell_cost

        # tell the player they dont have enough mp
        else:
            message_log.add_message(Message(f'{self.name} must have {spell_cost} mp to cast {spell_name}', tcod.light_blue))
    
    # shows the position of the stairs on the floor
    def cast_clairvoyance(self, game_map, message_log):
        # sets parameters for spell
        spell_cost = 35
        spell_name = 'clairvoyance'
        spell_color = tcod.light_purple

        # only lets player cast spell if they have enough mp
        if self.mp >= spell_cost:

            message_log.add_message(Message(f'{self.name} casts {spell_name}', spell_color))

            # reveals position of stairs
            stairs_x = game_map.stairs.x
            stairs_y = game_map.stairs.y
            game_map.tiles[stairs_x][stairs_y].explored = True

            # reduces entities mp by appropriate value
            self.mp -= spell_cost

        # tell the player they dont have enough mp
        else:
            message_log.add_message(Message(f'{self.name} must have {spell_cost} mp to cast {spell_name}', tcod.light_blue))

    # increases the distance the entity can see for a turn
    def cast_flash(self, message_log):
        # sets parameters for spell
        spell_cost = 10
        spell_name = 'flash'
        spell_color = tcod.light_yellow
        added_range = 10

        # only lets player cast spell if they have enough mp
        if self.mp >= spell_cost:

            message_log.add_message(Message(f'{self.name} casts {spell_name}', spell_color))

            # increases players fov_range by set amount
            self.fov_range += added_range

            # reduces entities mp by appropriate value
            self.mp -= spell_cost

        # tell the player they dont have enough mp
        else:
            message_log.add_message(Message(f'{self.name} must have {spell_cost} mp to cast {spell_name}', tcod.light_blue))

    # handles the death of an entity if they're hp drops to 0
    def kill_entity(self, message_log):
        self.char = ','
        self.color = tcod.black
        self.is_dead = True
        self.blocks = False # bodies can be walked over. prevents attacking corpses
        message_log.add_message(Message(f'{self.name} dies'))
        self.name = self.name + ' corpse'

# class for enemies. contains logic for enemy turns 
class Enemy(Fighter):
    # exact same as fighter but they have an added attribute that is automatically set to false
    def __init__(self, x, y, char, color, max_hp, max_mp, power, name, fov_range=0):
        super().__init__(x, y, char, color, max_hp, max_mp, power, name, fov_range)
        # tracks whether or not enemy has seen player
        self.knows_player_location = False

    # logic for a monsters turn
    def take_turn(self, target, game_map, entities, message_log):
        # only gets a turn if they are alive
        if (self.is_dead == False):
            # attacks player if they are adjacent or diagonal
            if (self.distance_to(target) < 2):
                self.attack(target, message_log)
            else:
                # uses a basic bfs pathfinding algorithm to move towards player
                self.bfs_move(target, game_map, entities)

    # enemies move around at random if they are not in the players fov
    def random_move(self, game_map, entities):
        # picks random direction
        dx = randint(-1, 1)
        dy = randint(-1, 1)
        new_x = self.x + dx
        new_y = self.y + dy
        # checks to prevent enemy from walking out of bounds or on top of another enemy
        if ((game_map.is_blocked(new_x, new_y) == False) and (get_blocking_entities_at_location(entities, new_x, new_y) == None)):
            self.move(dx, dy)

    # uses bfs algorithm to move towards target or stay in place if no path exists
    def bfs_move(self, target, game_map, entities):
        # gets full unblocked path to target
        path = bfs_pathfinder(self.x, self.y, target.x, target.y, game_map, entities)

        dx = path[0][0] - self.x
        dy = path[0][1] - self.y
        self.move(dx, dy)
        

