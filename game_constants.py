import json
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
GAME_CONSTANTS = json.loads('{}')
with open(dir_path + "/game_constants.json") as f:
    GAME_CONSTANTS = json.load(f)

class DIRECTIONS():
    NORTH = 'n'
    EAST = 'e'
    WEST ='w'
    SOUTH ='s'

    def getPerpendicular(direction):
        if direction == DIRECTIONS.EAST or direction == DIRECTIONS.WEST:
            return DIRECTIONS.SOUTH
        else:
            return DIRECTIONS.EAST

    def getOpposite(direction):
        if direction == DIRECTIONS.EAST:
            return DIRECTIONS.WEST
        elif direction == DIRECTIONS.WEST:
            return DIRECTIONS.EAST
        elif direction == DIRECTIONS.SOUTH:
            return DIRECTIONS.NORTH
        else:
            return DIRECTIONS.SOUTH
