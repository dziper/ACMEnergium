from energium.game_constants import GAME_CONSTANTS, DIRECTIONS
ALL_DIRECTIONS = [DIRECTIONS.EAST, DIRECTIONS.NORTH, DIRECTIONS.WEST, DIRECTIONS.SOUTH]
from energium.kit import Agent
from energium.position import Position
import copy
import sys
import math
import random

# Create new agent
agent = Agent()

# initialize agent
agent.initialize()
player = agent.players[agent.id];
my_bases = player.bases;

def inBounds(pos):
    return pos.x >= 0 and pos.x < agent.mapWidth and pos.y >= 0 and pos.y < agent.mapHeight

def initializeUnit(unit):
    newUnitData = [agent, energiumThresh, None, None, False, None, None, True, 0, None, None, unit.pos]
    if not twoBases:
        newUnitData[2] = my_bases[0]
    else:
        base0Dist = unit.pos.distance_to(my_bases[0].pos)
        base1Dist = unit.pos.distance_to(my_bases[1].pos)

        if base0Dist < base1Dist:
            newUnitData[2] = my_bases[0]
        else:
            newUnitData[2] = my_bases[1]
    unit.initialize(newUnitData)

twoBases = (len(my_bases) > 1)

energiumThresh = 0;
doneFindingEnergiumThresh = False
targets = []

# TODO: make targets not count low energium spaces?

for i in range(agent.mapWidth):
    for j in range(agent.mapHeight):
        pos = Position(i,j)
        energ = agent.map.get_tile_by_pos(pos).energium

        if energ > 0:
            targets.append((pos, energ))

        if energ > energiumThresh:
            energiumThresh = energ


for i in range(len(targets)-1, -1, -1):
    if targets[i][1] < energiumThresh/2 - 1:
        targets.pop(i)
        #remove relatively low value targets

#sort target list by energium
for i in range(len(targets)):
    maxIndex = i
    maxVal = 0
    for j in range(i,len(targets)):
        if targets[j][1] > targets[maxIndex][1]:
            maxIndex = j
            maxVal = targets[j][1]
    targ = targets.pop(maxIndex)
    targets.insert(i, targ)



for i in range(len(targets)):
    minIndex = i
    minVal = 100
    energ = targets[i][1]
    for j in range(i,len(targets)):
        if targets[j][1] != energ:
            break
        distanceToPos = targets[j][0].distance_to(my_bases[0].pos)
        if distanceToPos < minVal:
            minIndex = j
            minVal = distanceToPos

    targ = targets.pop(minIndex)
    targets.insert(i, targ)


if twoBases:
    targets1 = copy.deepcopy(targets)
    for i in range(len(targets1)):
        minIndex = i
        minVal = 100
        energ = targets1[i][1]
        for j in range(i,len(targets1)):
            if targets1[j][1] != energ:
                break
            distanceToPos = targets1[j][0].distance_to(my_bases[1].pos)
            if distanceToPos < minVal:
                minIndex = j
                minVal = distanceToPos

        targ = targets1.pop(minIndex)
        targets1.insert(i, targ)

print("base 0 targets, pos is " + str(my_bases[0].pos.x) + " " + str(my_bases[0].pos.y), file = sys.stderr)
for target in targets:
    print(str(target[0].x) + " " + str(target[0].y) + " e: " + str(target[1]), file = sys.stderr)

if twoBases:
    print("base 1 targets, pos is " + str(my_bases[1].pos.x) + " " + str(my_bases[1].pos.y), file = sys.stderr)
    for target in targets1:
        print(str(target[0].x) + " " + str(target[0].y) + " e: " + str(target[1]), file = sys.stderr)

targetsTaken = [False]*len(targets)
if twoBases:
    targetsTaken1 = [False] * len(targets1)

my_bases[0].addTargets(targets, targetsTaken)
if twoBases:
    my_bases[1].addTargets(targets1, targetsTaken1)

baseToggle = False

unitData = {}

while True:

    # wait for update from match engine
    agent.update()

    commands = []

    # player is your player object, opponent is the opponent's
    player = agent.players[agent.id];
    opponent = agent.players[(agent.id + 1) % 2];

    # all your collectorunits
    my_units = player.units;

    # all your bases
    my_bases = player.bases;

    # use print("msg", file=sys.stderr) to print messages to the terminal or your error log.
    # normal prints are reserved for the match engine. Uncomment the lines below to log something
    print('Turn {} | ID: {} - {} bases - {} units - energium {}'.format(agent.turn, player.team, len(my_bases), len(my_units), player.energium), file=sys.stderr);

    ### AI Code goes here ###




    #update targetsTaken to account for dead units






    maxUnits = 0
    if agent.turn < 100:
        maxUnits = 15
    elif agent.turn < 150:
        maxUnits = 7
    elif agent.turn < 185:
        maxUnits = 5
    else:
        maxUnits = 0

    if len(my_units) < maxUnits and player.energium >= GAME_CONSTANTS["PARAMETERS"]["UNIT_COST"]:
        doNotSpawn = False
        for unit in my_units:
            if unit.pos.equals(my_bases[baseToggle].pos):
                doNotSpawn = True
                break
        if not doNotSpawn:
            if len(my_bases) > 1:
                baseToggle = not baseToggle

            commands.append(my_bases[baseToggle].spawn_unit());

    for unit in my_units:
        if unit.id in unitData:
            unit.initialize(unitData[unit.id])
            # print("unit: " + str(unit.id) + " base: " + str(not unit.base == my_bases[0]), file = sys.stderr)

    for base in my_bases:
        base.targetsTaken = [False] * len(base.targets)
        for unit in my_units:
            if unit.initialized == False:
                continue
            if unit.isHunting:
                continue
            if unit.target == None:
                continue
            # print("checking unit with base", file = sys.stderr)
            for i in range(len(base.targets)):
                if base.targetsTaken[i]:
                    continue
                targetPos = base.targets[i][0]
                if targetPos.equals(unit.target):
                    base.targetsTaken[i] = True;
                    break

    # for base in my_bases:
    #     print("targets taken", file = sys.stderr)
    #     print(base.targetsTaken, file = sys.stderr)


    # iterate over all of our collectors and make them do something
    for unit in my_units:
        if unit.initialized == False:
            initializeUnit(unit)

        if unit.target == None:
            base = unit.base
            for i in range(len(base.targets)):
                if (not base.targetsTaken[i]):
                    unit.target = base.targets[i][0]
                    base.targetsTaken[i] = True
                    break

        # no targets remaining, hunt
        if unit.target == None:
            print("no targets found, hunting" , file = sys.stderr)
            unit.hunt()

        # no hunting targets either, do nothing
        if unit.target == None:
            print("No target for some reason", file = sys.stderr)
            continue

        if not unit.pos.equals(unit.target):
            dirToGo = unit.pos.direction_to(unit.target)
            posToGo = unit.pos.translate(dirToGo,1)

            if unit.getEnergium(posToGo) < 0:
                if unit.overrideIndex == None or unit.overrideIndex < 3:
                    unit.pathfindTo(unit.target)

            else:
                if unit.willKillMe(posToGo):
                    unit.pathfindTo(unit.target)

                



            commands.append(unit.move(dirToGo))
            unit.overrideMove = None



    for unit in my_units:
        myUnitData = unit.getData()
        if myUnitData == None:
            initializeUnit(unit)
            myUnitData = unit.getData()
            if myUnitData == None:
                print("still none :(", file = sys.stderr)
        # print(str(myUnitData), file = sys.stderr)
        unitData[unit.id] = myUnitData

    ### AI Code ends here ###

    # submit commands to the engine
    print(','.join(commands))

    # now we end our turn
    agent.end_turn()
