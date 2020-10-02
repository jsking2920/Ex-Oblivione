# functions for pathfinding

import collections

# helper function for bfs that gets neighboring nodes within map
def get_neighbors(x, y, game_map):
    up = (x, y-1)
    up_right = (x+1, y-1)
    right = (x+1, y)
    down_right = (x+1, y+1)
    down = (x, y+1)
    down_left = (x-1, y+1)
    left = (x-1, y)
    up_left = (x-1, y-1)
    return [up, up_right, right, down_right, down, down_left, left, up_left]

# helper function to get a path from one node to another from a dictionary made by bfs
def get_path(paths, target):
    # last node before reaching target
    step_back = paths[target]
    # this will hold the path in reverse order as its traced back from the end
    reverse_path = [target]

    # goes until you get to the start node in the dictionary
    while step_back != None:
        # add the last step of the path
        reverse_path.append(step_back)
        # set that node as the new target node
        target = step_back
        # find the step before the new target node
        step_back = paths[target]

    # path must be reversed to be in the right order
    reverse_path.reverse()
    return reverse_path[1:] # dont need the first step because it will just be the start node

# simple breadth first search pathfinding algorithm
# Same as Dijkstra’s algorithm but with all movement costs equal to each other
def bfs_pathfinder(start_x, start_y, target_x, target_y, game_map, entities):
    # start and end nodes stored as tuples -> (x, y)
    start = (start_x, start_y)
    target = (target_x, target_y)

    # these will keep track of what nodes need to be visited and what ones don't. 
    # deque makes accessing ends of list cheap and dictionary makes membership test cheap 
    to_visit = collections.deque([start])
    visited = {start: True}

    # came_from stores paths generated as a dictionary that can be traced with get_path()
    came_from = {start: None}

    while len(to_visit) != 0:
        # searches in the order that nodes are added to the queue
        current = to_visit.popleft()

        # goes through all adjacent neighbors of node being visited
        for node in get_neighbors(current[0], current[1], game_map):
            # found the target
            if node == target:
                # gets path to target and stops search to prevent unnecassary work
                came_from[target] = current
                path = get_path(came_from, target)
                return path

            # adds new nodes to list of nodes to search
            elif (node not in to_visit) and (node not in visited):
                # only look at walkable tiles 
                if not (game_map.is_blocked(node[0], node[1]) or any([entity for entity in entities if entity.x == node[0] and entity.y == node[1]])):
                    to_visit.append(node)
                    visited[node] = True
                    # keeps track of how to get to that new node
                    came_from[node] = current
                else:
                    # put unwalkable tiles in visited list so they're ignored. this keeps path bounded in the map since the map always has a wall on the outer edge
                    visited[node] = True

    # if no path is found, return just the starting point
    return [start]