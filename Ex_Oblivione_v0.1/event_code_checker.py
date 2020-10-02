# use this to get codes for different events in tcod
# this is for development purposes only. will not be used in actual project

import tcod
import tcod.event

tcod.console_init_root(50, 50)
con = tcod.console.Console(50,50)

while True:
    for event in tcod.event.wait():
        if event.type == "QUIT":
            print(event)
            raise SystemExit()
        elif event.type == "KEYDOWN":
            print(event)
        elif event.type == "MOUSEBUTTONDOWN":
            print(event)
        elif event.type == "MOUSEMOTION":
            print(event)
        else:
            print(event)
    tcod.console_flush()

    