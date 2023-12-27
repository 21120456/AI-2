#!/bin/env python3
# The main program.

# Configurables
ASSETS_THEME      = 'images'

TILES_SHOW_HIDDEN = True
WINDOW_TITLE      = 'Wumpus World'
FONT              = 'Consolas'
FONTBT = ('Consolas',10)
AUTOSTEP_DELAY    = 105 # ms
KEYB_OPEN         = 'o'
KEYB_RESET        = 'r'
KEYB_STEP         = 's'
KEYB_AUTOSTEP     = 'p'

####################

import os
import controller

# Working directories
BASE_DIR   = os.path.dirname(os.path.realpath(__file__)) + '/..'
MAPS_DIR   = BASE_DIR + '/maps'
ASSETS_DIR = BASE_DIR + '/assets/' + ASSETS_THEME

# GUI: constants
TILE_SIZE   = 32
WINDOW_UNIT = 8

# GUI: onboarding messages (status, log)
ONBOARDING_MSG = [
# (Status)
"""Wumpus World
OPEN A MAP TO BEGIN.
""",

# (Log) keyboard shortcut hints
"""
Click the buttons on GUI, or you can use short key:
[O] Open  : open and choose a mapfile
[R] Reset : reset the game
[S] Step  : game run step by step
[P] Play  : game auto run

Explain information of the status bar:
MAP: G - gold, W -  wumpus, P - pit count
PLAYER: current location and orientation,
        a - arrows used, s - score
"""
]

####################

if __name__ == "__main__":
    main_app = controller.Controller()
    main_app.start()
