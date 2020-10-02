# contains all rendering functions
# modified from: http://rogueliketutorials.com/tutorials/tcod/part-2/
# and part 4

import tcod

# draws entire map and UI panel that been explored with all entities that are within sight
def render_all(con, panel, message_log, entities, player, game_map, fov_map, fov_recompute, screen_width, screen_height, bar_width, panel_height, panel_y):
    # Only draw things if the players position has actually changed and they can see different things. prevents unnecessary work
    if (fov_recompute == True):
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight
                # tiles in sight
                if (visible == True):
                    if (wall == True):
                        tcod.console_set_char_background(con, x, y, game_map.colors.get('light_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, game_map.colors.get('light_ground'), tcod.BKGND_SET)
                    # if a tile has been seen, it will continue to be remembered
                    game_map.tiles[x][y].explored = True

                # renders tiles that have been seen but are no longer in sight or all tiles if lights are turned on
                elif (game_map.lights_on == True) or (game_map.tiles[x][y].explored == True):
                    if (wall == True):
                        tcod.console_set_char_background(con, x, y, game_map.colors.get('dark_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, game_map.colors.get('dark_ground'), tcod.BKGND_SET)
    
    # draws entities in given list
    for entity in entities:
        draw_entity(con, entity, fov_map)

    # updates entire bitmap within specified rectangle
    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    # draws UI elements to panel
    # from: http://rogueliketutorials.com/tutorials/tcod/part-7/
    tcod.console_set_default_background(panel, tcod.black) # black background
    tcod.console_clear(panel)

    # renders an hp and mp bar on the 'panel' console. coordinates relative to the panel not the whole window
    render_bar(panel, 1, 1, bar_width, 'HP', player.hp, player.max_hp, tcod.light_red, tcod.darker_red)
    render_bar(panel, 1, 3, bar_width, 'MP', player.mp, player.max_mp, tcod.light_blue, tcod.darker_blue)
    

    # Print the game messages, one line at a time
    y = 1
    for message in message_log.messages:
        tcod.console_set_default_foreground(panel, message.color)
        tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
        y += 1
 
    # blits whole panel 
    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

# draws bars for UI elements such as health bars
# from: http://rogueliketutorials.com/tutorials/tcod/part-7/
def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    # figures out how much of bar should be 'full'. accounts for bars that arent the same width as the max value. in that case a bar would 'empty' proportionally
    bar_width = int(float(value) / maximum * total_width)

    # Draws the whole bar with the background color
    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    # draws the 'full' portion of the bar over the background bar. this gives an 'emptying' sort of effect
    tcod.console_set_default_background(panel, bar_color)
    if (bar_width > 0):
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    # draws text in the middle of the bar that shows numeric values and the name of the bar
    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER, f'{name}: {value}/{maximum}')

# clears previous position of entities to avoid leaving a trail while moving
def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

# draws a given entity if they are within sight
def draw_entity(con, entity, fov_map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        # sets color of console so that the entity is drawn with the right color
        tcod.console_set_default_foreground(con, entity.color)
        # puts entities char in given console, at given coordinates, and with a given background
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

# erase the character that represents this entity
def clear_entity(con, entity):
    # puts empty space in given cell
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)

# completely clears a console
def clear_console(con, screen_width, screen_height):
    for x in range(screen_width):
        for y in range(screen_height):
            # makes every cell black
            tcod.console_set_char_background(con, x, y, tcod.black, tcod.BKGND_SET)
