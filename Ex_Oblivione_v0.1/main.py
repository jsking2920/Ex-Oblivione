# Main engine of game. Contains game loop. Run this to play game
# Originally based on but heavily modified and expanded from: http://rogueliketutorials.com/tutorials/tcod/

import tcod
import tcod.event

from input_handlers import event_dispatcher
from render_functions import clear_all, render_all, clear_console
from loader_functions.initialize_new_game import get_constants, get_game_variables
from fov_functions import recompute_fov, initialize_fov
from entity import get_blocking_entities_at_location, Enemy
from game_states import GameStates
from game_messages import MessageLog, Message

def main():
    #initialize constants, game variables, fov, message log, and font
    const = get_constants()
    player, entities, game_map, fov_recompute, fov_map, message_log, hp_regen_tick, mp_regen_tick = get_game_variables(const)

    # font from: http://rogueliketutorials.com/tutorials/tcod/part-0/
    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    #sets game state to be players turn to begin with
    game_state = GameStates.PLAYERS_TURN

    # main game loop. Root console being created in context with 'with' so that it closes nicely instead of freezing and crashing
    with tcod.console_init_root(const['screen_width'], const['screen_height'], const['window_title'], fullscreen=False, order='F', vsync=True) as root_console:
        # initializes main console and console for UI elements
        con = tcod.console.Console(const['screen_width'], const['screen_height'], order='F')
        panel = tcod.console.Console(const['screen_width'], const['panel_height'], order='F')

        # main game loop
        while True:
            # gets user input and sends input events to a handler that returns a dictionary of actions
            for event in tcod.event.wait(): 
                action = event_dispatcher(event)

            # recomputes fov when necessary
            if (fov_recompute == True):
                recompute_fov(fov_map, player.x, player.y, player.fov_range, const['fov_light_walls'], const['fov_algorithm'])
                
            # renders whole map on console
            render_all(con, panel, message_log, entities, player, game_map, fov_map, fov_recompute, const['screen_width'], const['screen_height'], const['bar_width'], const['panel_height'], const['panel_y'])
            tcod.console_flush()

            # resets fov_recompute to prevent wasteful computation
            fov_recompute = False

            # clears console to avoid trails when moving
            clear_all(con, entities)
                       
            # gets actions inputted by player from dictionary
            move = action.get('move')
            exit_game = action.get('exit_game')
            fullscreen = action.get('fullscreen')
            restart = action.get('restart')
            take_stairs = action.get('take_stairs')
            toggle_lights = action.get('toggle_lights')
            spell = action.get('spell')

            # player's turn taken only if player gives input
            if (move != None) and (game_state == GameStates.PLAYERS_TURN) and (player.is_dead == False):
                dx, dy = move
                # only move player if the cell is unblocked and moving within the map
                if ((player.x+dx < game_map.width-1) and (player.y+dy < game_map.height-1) and (not game_map.is_blocked(player.x + dx, player.y + dy))):
                    # checks for entities that block movement in destination being moved to
                    target = get_blocking_entities_at_location(entities, player.x+dx, player.y+dy)

                    # space is empty so player moves. if player is waiting in place it is treated as a normal move to prevent them from atacking themselves
                    if (target == None) or (dx == 0 and dy == 0):
                        player.move(dx, dy)
                        # only recomputes fov when player moves to avoid unnecessary computation
                        fov_recompute = True
                    # attack target
                    else:
                        player.attack(target, message_log)
                
                # increments tick by one if the player is below full health/mp. Player must always wait for the full delay after losing hp/mp at max
                if (player.hp < player.max_hp):
                    hp_regen_tick += 1
                if (player.mp < player.max_mp):
                    mp_regen_tick += 1

                # player statically regenerates hp and mp periodically
                if (hp_regen_tick == const['hp_regen_delay']):
                    player.heal(1)
                    hp_regen_tick = 0 # resets tick
                if (mp_regen_tick == const['mp_regen_delay']):
                    player.restore_mp(1)
                    mp_regen_tick = 0 # resets tick

                # resets players fov range in case they have casted flash
                player.fov_range = const['default_fov_radius']

                # passes turn to enemies. this happens even if player walks into a wall
                game_state = GameStates.ENEMY_TURN

            # handles spells
            if (spell != None) and (game_state == GameStates.PLAYERS_TURN) and (player.is_dead == False):
                # f key casts a fireball spell that does damage in a radius around the player
                if (spell == 'fireball'):
                    player.cast_fireball(entities, message_log)
                # h key casts cure which heals for a portion of players max hp
                elif (spell == 'cure'):
                    player.cast_cure(message_log)
                # v key casts clairvoyance which reveals position of stairs
                elif (spell == 'clairvoyance'):
                    player.cast_clairvoyance(game_map, message_log)
                # g key casts flash which increases the distance the player can see for a turn
                elif (spell == 'flash'):
                    player.cast_flash(message_log)       
                # arrow keys cast in appropriate direction
                elif (spell == 'tunnel_up'):
                    player.cast_tunnel(game_map, fov_map, message_log, 0, -1)
                elif (spell == 'tunnel_down'):
                    player.cast_tunnel(game_map, fov_map, message_log, 0, 1)
                elif (spell == 'tunnel_left'):
                    player.cast_tunnel(game_map, fov_map, message_log, -1, 0)
                elif (spell == 'tunnel_right'):
                    player.cast_tunnel(game_map, fov_map, message_log, 1, 0)    

                # increments tick by one if the player is below full health.
                if (player.hp < player.max_hp):
                    hp_regen_tick += 1
                # resets mp regen tick so a player must wait full delay after casting a spell to start mp regen
                mp_regen_tick = 0

                # hp regen unaffected by casting a spell
                if (hp_regen_tick == const['hp_regen_delay']):
                    player.heal(1)
                    hp_regen_tick = 0 # resets tick

                # resets player's fov range unless they cast flash. this makes flash only last one turn
                if (spell != 'flash'):
                    player.fov_range = const['default_fov_radius']

                # recomputes fov since some spells affect the map/fov
                fov_recompute = True

                game_state = GameStates.ENEMY_TURN
            
            # enemy's turn
            if (game_state == GameStates.ENEMY_TURN):
                # loops through all enemies
                for entity in entities:
                    if (isinstance(entity, Enemy)):
                        # enemy gets a real turn if they are within the players fov, or if they have seen the player
                        if ((fov_map.fov[entity.y, entity.x]) or (entity.knows_player_location == True)):
                            # attacks player if they are adjacent or moves towards player using bfs pathfinding algorithm
                            entity.take_turn(player, game_map, entities, message_log)

                            # enemy will continue to follow the player after being seen for the first time, regardless of fov
                            if entity.knows_player_location == False:
                                entity.knows_player_location = True

                        # enemies outside of fov just move around at random
                        else:
                            entity.random_move(game_map, entities)

                # checks to see if the player died
                if (player.is_dead == True):
                    game_state = GameStates.PLAYER_DEATH
                else:  
                    # passes turn back to player even if the enemies didn't do anything
                    game_state = GameStates.PLAYERS_TURN

            # handles death of player
            if (game_state == GameStates.PLAYER_DEATH):
                message_log.add_message(Message('You Lose', tcod.darker_red))

            # takes player to new floor
            if (take_stairs == True) and (player.x == game_map.stairs.x) and (player.y == game_map.stairs.y):
                # makes new floor and resets entities list
                entities = game_map.stairs.take_stairs(player, game_map, entities, message_log)

                # resets fov
                fov_map = initialize_fov(game_map)
                fov_recompute = True

                # clears the console to remove the last floor from the screen
                clear_console(con, const['screen_width'], const['screen_height'])

                # player wins if they make it to the 4th floor
                if (game_map.depth == const['winning_floor']):
                    game_state = GameStates.PLAYER_WINS

            # player wins after getting to a set floor
            if game_state == GameStates.PLAYER_WINS:
                message_log.add_message(Message('You Win!', tcod.yellow))
            
            # restarts game
            if (restart == True):
                # resets everything to beginning state
                const = get_constants()
                player, entities, game_map, fov_recompute, fov_map, message_log, hp_regen_tick, mp_regen_tick = get_game_variables(const)

                # clears the console to remove the last floor from the screen
                clear_console(con, const['screen_width'], const['screen_height'])

                # new game starts with players turn
                game_state = GameStates.PLAYERS_TURN

            # toggles lights to see the whole map for deomonstration
            if (toggle_lights == True):
                game_map.lights_on = not game_map.lights_on
                if game_map.lights_on == False:
                    clear_console(con, const['screen_width'], const['screen_height'])
                fov_recompute = True
            
            # breaks loop if player exits
            if (exit_game == True):
                raise SystemExit()

            # toggles fullscreen
            if (fullscreen == True):
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

if __name__ == '__main__':
    main()