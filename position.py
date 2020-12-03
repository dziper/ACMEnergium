from .game_constants import DIRECTIONS, GAME_CONSTANTS
import math
class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def equals(self, opos):
        return self.x == opos.x and self.y == opos.y

    def is_adjacent(self, pos):
        dx = self.x - pos.x;
        dy = self.y - pos.y;
        if (math.abs(dx) + math.abs(dy) > 1):
            return False
        return True
    def translate(self, direction, units):
        if direction == DIRECTIONS.NORTH:
            return Position(self.x, self.y - units)
        elif direction == DIRECTIONS.EAST:
            return Position(self.x + units, self.y)
        elif direction == DIRECTIONS.SOUTH:
            return Position(self.x, self.y + units)
        elif direction == DIRECTIONS.WEST:
            return Position(self.x - units, self.y)

    def distance_to(self, pos):
        dx = pos.x - self.x
        dy = pos.y - self.y
        return math.sqrt(dx * dx + dy * dy);

    def direction_to(self, targetPos):
        xDist = targetPos.x - self.x
        yDist = targetPos.y - self.y

        if abs(xDist)>abs(yDist):
            if xDist > 0:
                return DIRECTIONS.EAST
            else:
                return DIRECTIONS.WEST
        else:
            if yDist > 0:
                return DIRECTIONS.SOUTH
            else:
                return DIRECTIONS.NORTH

    def otherDirectionTo(self, targetPos):
        xDist = targetPos.x - self.x
        yDist = targetPos.y - self.y

        if abs(xDist)<=abs(yDist):
            if xDist > 0:
                return DIRECTIONS.EAST
            else:
                return DIRECTIONS.WEST
        else:
            if yDist > 0:
                return DIRECTIONS.SOUTH
            else:
                return DIRECTIONS.NORTH
