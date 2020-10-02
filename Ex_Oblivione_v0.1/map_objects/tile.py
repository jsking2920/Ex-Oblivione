# class for tiles from: http://rogueliketutorials.com/tutorials/tcod/part-2/
# and part 4

# a tile on a map. It may or may not be blocked, and may or may not block sight.
class Tile:
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        
        self.block_sight = block_sight

        # keeps track of whether or not a tile has been seen
        self.explored = False