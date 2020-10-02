# from: http://rogueliketutorials.com/tutorials/tcod/part-3/

# helper class for dungeon generation
class Rect:
    # constructed with a point (x, y) and dimensions
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        # calculates and stores (x2, y2)
        self.x2 = x + w
        self.y2 = y + h

    # finds center of rectangle and returns as a tuple (x, y)
    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    # returns true if this rectangle intersects with another one
    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)