DungeonRun
==========

Dungeon Run is a fast-paced, two-player game where you run around level upon level in a dungeon, collecting coins and avoiding restless monsters!
Each player tries to collect as many points as possible while not getting killed.
In its current version, you must install the Python and the PySDL2 library (linked below) first in order to play.

# Steps to play

1. Install Python 3.2+ and PySDL2 if you haven't already
    * PySDL2 Install Page: http://pysdl2.readthedocs.org/en/latest/install.html
      * Make sure to download and place the SDL2_Image DLL's: http://www.libsdl.org/projects/SDL_image/
      * The other 'SDL-related' DLLs listed below SDL2_Image on the PySDL2 install page shouldn't be necessary.
    * Python Download/Install Page: https://www.python.org/downloads/
2. Pull this DungeonRun repository
3. Run the DungeonRun.py script
4. Enjoy!

# Notes

- Two players are default right now.
- Arrow keys move Player 1, WASD moves player two (same arrangement as the arrow keys).
- Run to the door to progress to the next level.
- + (plus) and - (minus) on the keypad will accelerate and decelerate (respectively) the players and monsters.
- The points and end game score can currently be seen in the window header.
- The most recent code is in the top-level DungeonRun.py script, but stable versions with less features are in the version_release folders.
