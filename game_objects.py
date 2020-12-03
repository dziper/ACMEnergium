from typing import List
from .position import Position
from .game_constants import GAME_CONSTANTS, DIRECTIONS
ALL_DIRECTIONS = [DIRECTIONS.EAST, DIRECTIONS.NORTH, DIRECTIONS.WEST, DIRECTIONS.SOUTH]
import math
import sys
class Base:
    def __init__(self, team: int, x, y):
        self.team = team
        self.pos = Position(x, y)

    def addTargets(self, targets, targetsTaken):
        self.targets = targets
        self.targetsTaken = targetsTaken

    def spawn_unit(self):
        return 'c {} {}'.format(self.pos.x, self.pos.y)


class Unit:
    initialized = False

    def __init__(self, team: int, unitid: int, x, y, last_repair_turn, turn):
        self.team = team
        self.id = unitid
        self.pos = Position(x, y)
        self.last_repair_turn = last_repair_turn
        self.match_turn = turn
        #units are getting reinitted every turnnnn
        # may need to change structure so that bot.py remembers all the unit data and chucks it back to the unit at the beginning of each turn

    def initialize(self, data):
        # print("initting unit " + str(self.id), file = sys.stderr)

        if self.initialized:
            return
        self.agent = data[0]
        self.player = self.agent.players[self.agent.id]
        self.opponent = self.agent.players[(self.agent.id + 1) % 2];

        self.energiumThresh = data[1]
        self.base = data[2]

        self.target = data[3]
        self.isHunting = data[4]

        self.overridePath = data[5]
        self.overrideIndex = data[6]

        self.initialized = True

        self.counter = data[8]
        self.prevLoc = data[9]
        if self.prevLoc == None:
            self.prevLoc = self.pos

        self.overrideMove = data[10] #init at None

        self.nextTurnPos = data[11]

    def pathfindTo(self, target):
        #run this if we run into a wall
        #generates a self.path to follow
        xToTarget = target.x - self.pos.x
        yToTarget = target.y - self.pos.y

        dirToGo = self.pos.direction_to(target)
        otherDirToGo = self.pos.otherDirectionTo(target)

        print("target: " + str(target.x) + " " + str(target.y), file = sys.stderr)

        if self.overrideIndex == None:
            self.overrideIndex = 0;
        else:
            self.overrideIndex += 1

        # print("overrideIndex: " + str(self.overrideIndex), file = sys.stderr)

        thoroughPathFind = True
        if self.overrideIndex > 3:
            thoroughPathFind = False

        directionsToCheck = [otherDirToGo, DIRECTIONS.getOpposite(otherDirToGo), DIRECTIONS.getOpposite(dirToGo), dirToGo]

        if thoroughPathFind:
            # print("running thorough", file = sys.stderr)
            for dir in directionsToCheck:
                positionToCheck = self.pos.translate(dir, 1)
                if not self.willKillMe(positionToCheck) and self.getEnergium(positionToCheck) >= 0 and not self.prevLoc.equals(positionToCheck):
                    self.overrideMove = dir
                    # print("unit " + str(self.id) + " pathfinding to " + self.overrideMove, file = sys.stderr)
                    return

            for dir in directionsToCheck:
                positionToCheck = self.pos.translate(dir, 1)
                if not self.willKillMe(positionToCheck) and not self.prevLoc.equals(positionToCheck):
                    self.overrideMove = dir
                    # print("unit " + str(self.id) + " pathfinding to " + self.overrideMove, file = sys.stderr)
                    return

        for dir in directionsToCheck:
            positionToCheck = self.pos.translate(dir, 1)
            if not self.willKillMe(positionToCheck):
                self.overrideMove = dir
                # print("unit " + str(self.id) + " pathfinding to " + self.overrideMove, file = sys.stderr)
                return

        print("not moving", file = sys.stderr)
        self.overrideMove = "NO"
        # print("unit " + str(self.id) + " pathfinding to " + self.overrideMove, file = sys.stderr)




    def getEnergium(self, pos):
        return self.agent.map.get_tile_by_pos(pos).energium

    def getData(self):
        if self.initialized == False:
            print("fetch data from unit " + str(self.id) + " init: " + str(self.initialized), file = sys.stderr)
            return
        data = []
        data.append(self.agent)
        data.append(self.energiumThresh)
        data.append(self.base)
        data.append(self.target)
        data.append(self.isHunting)
        data.append(self.overridePath)
        data.append(self.overrideIndex)
        data.append(self.initialized)
        data.append(self.counter)
        data.append(self.prevLoc)
        data.append(self.overrideMove)
        data.append(self.nextTurnPos)
        return data

    def willKillMe(self, pos):
        if (pos == None):
            return False
        opponentUnits = self.opponent.units
        my_units = self.player.units

        if not self.inBounds(pos):
            return True

        for unit in my_units:

            if unit.pos.equals(pos):
                return True
            if unit.initialized and unit.nextTurnPos.equals(pos):
                print("nextTurn crash", file = sys.stderr)
                return True
        for opponentUnit in opponentUnits:
            if opponentUnit.pos.equals(pos):
                if opponentUnit.get_breakdown_level() < self.get_breakdown_level():
                    return True
                #return something else if we can kill opponent?
        return False

    def get_breakdown_level(self):
        return math.floor((self.match_turn - self.last_repair_turn) / GAME_CONSTANTS['PARAMETERS']['BREAKDOWN_TURNS'])

    def move(self, dir):
        self.prevLoc = self.pos
        self.counter += 1
        dirToGo = dir
        if self.overrideMove != None:
            if self.overrideMove == "NO":
                print("unit " + str(self.id) + " not moving", file = sys.stderr)
                self.overrideMove = None
                self.nextTurnPos = Position(self.pos.x, self.pos.y);
                return
            dirToGo = self.overrideMove
            print("overrode unit " + str(self.id) + " from " + dir + " to " + dirToGo, file = sys.stderr)

        self.overrideMove = None
        self.nextTurnPos = self.pos.translate(dirToGo, 1)
        return 'm {} {}'.format(self.id, dirToGo)


    def hunt(self):
        opponentUnits = self.opponent.units
        for opUnit in opponentUnits:
            if(opUnit.get_breakdown_level() + 1< self.get_breakdown_level()):
                print("hunting", file=sys.stderr)
                self.target = opUnit.pos
                return

        print("hunt failed", file=sys.stderr)
        self.isHunting = True

    def findOverridePath(self, initialDir):
        #Out of commission
        my_units = self.player.units
        self.overridePath = []

        perpADir = DIRECTIONS.getPerpendicular(initialDir)
        perpAPos = self.pos.translate(perpADir, 1)
        perpADirOK = True

        perpBDir = DIRECTIONS.getOpposite(perpADir)
        perpBPos = self.pos.translate(perpBDir, 1)
        perpBDirOK = True

        oppoDir = DIRECTIONS.getOpposite(initialDir)
        oppoPos = self.pos.translate(oppoDir, 1)

        for other_unit in my_units:
            if other_unit == self:
                continue
            if other_unit.pos.equals(perpAPos):
                perpADirOK = False
            if other_unit.pos.equals(perpBPos):
                perpBDirOK = False

        if perpADirOK:
            self.overridePath = [perpADir,perpADir,perpADir]
        elif perpBDirOK:
            self.overridePath = [perpBDir,perpBDir,perpBDir]
        else:
            self.overridePath = [oppoDir, perpADir, perpADir]

        # print("overridePath length " + str(len(self.overridePath)), file = sys.stderr)
        self.overrideIndex = 0;
        print("overriding " + str(self.id) + " to " + str(self.overridePath), file=sys.stderr)

    def isGoodTarget(self, pos):
        my_units = self.player.units

        for unit in my_units:
            if unit == self:
                continue
            if unit.target == None:
                continue
            if unit.target.equals(pos):
                return False
        return True

    def inBounds(self, pos):
        return pos.x >= 0 and pos.x < self.agent.mapWidth and pos.y >= 0 and pos.y < self.agent.mapHeight




class Player:
    energium: int
    team: int
    units: List[Unit]
    bases: List[Base]
    def __init__(self, team):
        self.team = team
        self.bases = []
        self.units = []
        self.energium = 0
