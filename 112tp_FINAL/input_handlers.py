# module to handle what should happen when a user gives input
# completely reworked version of input handling from: http://rogueliketutorials.com/tutorials/tcod/part-1/
# uses new appropriate tcod.event functionality and completely different structure and has many more inputs

import tcod
import tcod.event

# takes an input event and dispatches it to another function based on the type of event
def event_dispatcher(event):
    # closing the window with the "X"
    if (event.type == 'QUIT'):
        return handle_quit(event)
    # pressing a non-alphanumeric key down
    elif (event.type == 'KEYDOWN'):
        return handle_keypress(event)
    # tcod registers alphanumeric keys as text input
    elif event.type == 'TEXTINPUT':
        return handle_text(event)
    # any other event we dont care about
    else: return {}

# handles keypresses
def handle_keypress(event):
    # escape exits game
    if (event.sym == tcod.event.K_ESCAPE):
        return {'exit_game': True}

    # arrow keys cast tunneling spell in given direction
    elif (event.sym == tcod.event.K_UP):
        return {'spell': 'tunnel_up'}
    elif (event.sym == tcod.event.K_DOWN):
        return {'spell': 'tunnel_down'}
    elif (event.sym == tcod.event.K_LEFT):
        return {'spell': 'tunnel_left'}
    elif (event.sym == tcod.event.K_RIGHT):
        return {'spell': 'tunnel_right'}

    # left alt + enter toggles fullscreen
    elif (event.sym == tcod.event.K_RETURN) and (event.mod & tcod.event.KMOD_LALT):
        return {'fullscreen': True}

    # Enter takes a player down stairs
    elif event.sym == tcod.event.K_RETURN:
        return {'take_stairs': True}

    # any other keys we dont care about
    else: return {}

# handles alphanumeric keys
def handle_text(event):
    # shift+r restarts game
    if (event.text == 'R'):
        return {'restart': True}

    # WASD Movement
    elif event.text == 'w':
        return {'move': (0, -1)}
    elif (event.text == 's'):
        return {'move': (0, 1)}
    elif (event.text == 'a'):
        return {'move': (-1, 0)}
    elif (event.text == 'd'):
        return {'move': (1, 0)}
    # space waits a turn
    elif (event.text == ' '):
        return {'move': (0, 0)} 

    # Diagonal Movement using QEZC
    elif event.text == 'q':
        return {'move': (-1, -1)}
    elif (event.text == 'e'):
        return {'move': (1, -1)}
    elif (event.text == 'z'):
        return {'move': (-1, 1)}
    elif (event.text == 'c'):
        return {'move': (1, 1)}

    # casts a fireball spell
    elif (event.text == 'f'):
        return {'spell': 'fireball'}
    # casts cure spell
    elif (event.text == 'h'):
        return {'spell': 'cure'}
    # casts clairvoyance spell
    elif (event.text == 'v'):
        return {'spell': 'clairvoyance'}
    # casts flash spell
    elif (event.text == 'g'):
        return {'spell': 'flash'}

    # l shows the whole map regardless of fov for demonstration purposes
    elif (event.text == 'l'):
        return {'toggle_lights': True}

    # any other keys we dont care about
    else: return {}

# handles quit type events such as closing the window by exiting game
def handle_quit(event):
    return {'exit_game': True}
