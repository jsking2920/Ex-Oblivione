!README!
----------------------------------------------------------------------------------------------------
Name: Scott King
Andrew ID: jsking

Description:
Ex Oblivione is a roguelike game created by Scott King for the 15-112 term project
in the spring of 2020. In it, a player moves through procedurally generated floors
fighting enemies. If the player makes it through enough floors, they win. Ex Oblivione 
features several different algortihms for generating dungeons, field of view and
pathfinding algorithms, five unique spells, and a text based interface reminiscent 
of many old-school roguelikes.


Notice:
This is the version of the project that I have worked on since submitting it as a term project
and is NOT what I submitted for a grade. Very little has changed (so far) but if I continue to 
add to the game in the future, it will be on this branch.


How to run Ex Oblivione:
Run the file named "main.py" in an editor with python-tcod installed to play the game.


Dependencies:
Ex Oblivione was created using the python port of libtcod. Directions for installing 
python tcod can be found at https://python-tcod.readthedocs.io/en/latest/installation.html

More info on python tcod is included in the file named "Resources.txt" in the documentation folder
as well as other miscellaneous citations and resources used for research.


Controls/Shortcuts:

Exit: esc
Toggle fullscreen: left alt + enter
Restart game: shift + r
Show map: l (this lets you see the entire floor to see the map gen algorithms at work more easily)

Movement: WASD for cardinal directions and QEZC for diagonal movement (this also attacks as in most roguelikes)
Wait in place: space
Take stairs: enter (stairs are represented by >)

Fireball spell: f (deals damage to enemies in a radius around player)
Cure spell: h (heals player)
Clairvoyance spell: v (shows stairs)
Flash spell: g (increases player's fov)
Tunnel spell: arrow keys (tunnels through walls in direction of arrow key)

