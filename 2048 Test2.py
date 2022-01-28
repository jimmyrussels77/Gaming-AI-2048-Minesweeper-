import random
import copy
import pygame
import sys
from pygame.locals import *
import pygame.locals
from pygame import key, event
import functools
import time
import csv


pygame.init()
fpsClock = pygame.time.Clock()
SIZE = 4
BLOCKSIZE = 100
HEIGHT = 500
BOARDHEIGHT = 400
BOARDWIDTH = 400
MAX = SIZE * BLOCKSIZE
_GameEnd = None
_GameOver = None
windowSurfaceObj = pygame.display.set_mode((BOARDWIDTH, HEIGHT))
pygame.display.set_caption('2048')

redColor = pygame.Color(255, 0, 0)
greenColor = pygame.Color(0, 255, 0)
blueColor = pygame.Color(0, 0, 255)
whiteColor = pygame.Color(255, 255, 255)
lightblue = pygame.Color(173, 216, 230)
lighterblue = pygame.Color(235, 255, 255)
grey = pygame.Color(145, 141, 142)
gold = pygame.Color(255, 215, 0)
black = pygame.Color(0, 0, 0)
granite = pygame.Color(131, 126, 124)
box1 = pygame.Color(201, 196, 194)
color2 = (229, 228, 227)
color4 = pygame.Color(229, 182, 147)
background = pygame.Color(187, 173, 162)
resetColor = pygame.Color(237, 153, 91)

colors = {'': (187, 173, 162),
          '2': (238, 228, 219),
          '4': (238, 223, 200),
          '8': (242, 177, 121),
          '16': (236, 141, 85),
          '32': (243, 125, 99),
          '64': (234, 90, 56),
          '128': (242, 208, 75),
          '256': (242, 208, 75),
          '512': (228, 192, 42),
          '1024': (227, 186, 20),
          '2048': (236, 196, 2),
          '4096': (96, 217, 146),
          '8192': (0, 0, 100),
          '16384': (30, 0, 0),
          '32768': (60, 0, 0)}
mousex, mousey = (0, 0)

fontObj = pygame.font.SysFont('verdana', 32)
fontObj2 = pygame.font.SysFont('verdana', 32)
fontObj16 = pygame.font.SysFont('verdana', 28)
fontObj128 = pygame.font.SysFont('verdana', 26, bold=True)
fontObj1024 = pygame.font.SysFont('verdana', 24, bold=True)
fontObj16384 = pygame.font.SysFont('verdana', 23, bold=True)
fontObjSmall = pygame.font.SysFont('verdana', 22, bold=True)
fonts = [fontObj2, fontObj16, fontObj128, fontObj1024, fontObj16384, fontObjSmall]


lineArray = []
for a in range(0, MAX, BLOCKSIZE):  # 100 400 100    ?? 500 800 100
    lineArray.append((0, a))
    lineArray.append((MAX, a))
    lineArray.append((MAX, a + BLOCKSIZE))

lineArray.append((MAX, 0))
lineArray.append((0, 0))

for a in range(0, MAX, BLOCKSIZE):  # 100 400 100 ??
    lineArray.append((a, 0))
    lineArray.append((a, MAX))
    lineArray.append((a + BLOCKSIZE, 400))
print(lineArray)


class Move:
    def __init__(self, initalProb, moveNum, av, timeCounter, avgAv, name, totReward):
        self.initalProb = initalProb
        self.moveNum = moveNum
        self.av = av
        self.timeCounter = timeCounter
        self.avgAv = avgAv
        self.name = name
        self.totReward = totReward


def push_row(row, left=True):
    """Push all tiles in one row; like tiles will be merged together."""
    row = row[:] if left else row[::-1]
    new_row = [item for item in row if item]
    for i in range(len(new_row)-1):
        if new_row[i] and new_row[i] == new_row[i+1]:
            new_row[i], new_row[i+1:] = new_row[i]*2, new_row[i+2:]+[""]
    new_row += [""]*(len(row)-len(new_row))
    return new_row if left else new_row[::-1]


def get_column(grid, column_index):
    """Return the column from the grid at column_index  as a list."""
    return [row[column_index] for row in grid]


def set_column(grid, column_index, new):
    """
    Replace the values in the grid at column_index with the values in new.
    The grid is changed inplace.
    """
    for i, row in enumerate(grid):
        row[column_index] = new[i]


def push_all_rows(grid, left=True):
    """
    Perform a horizontal shift on all rows.
    Pass left=True for left and left=False for right.
    The grid will be changed inplace.
    """
    for i, row in enumerate(grid):
        grid[i] = push_row(row, left)


def push_all_columns(grid, up=True):
    """
    Perform a vertical shift on all columns.
    Pass up=True for up and up=False for down.
    The grid will be changed inplace.
    """
    for i, val in enumerate(grid[0]):
        column = get_column(grid, i)
        new = push_row(column, up)
        set_column(grid, i, new)


def get_start_grid(cols=4, rows=4):

    # Create Grid that starts off as a 4 x 4
    # Done in the beginning of the game
    #

    grid = [[""]*cols for i in range(rows)]
    for i in range(2):
        empties = get_empty_cells(grid)
        y, x = random.choice(empties)
        grid[y][x] = 2 if random.random() < 0.9 else 4
    return grid


def get_empty_cells(grid):

    # Get all of the empty cells
    # used to place random number
    # used to check for possible moves

    empty = []
    for j, row in enumerate(grid):
        for i, val in enumerate(row):
            if not val:
                empty.append((j, i))
    return empty


def any_possible_moves(grid):

    # Check if theree is any possible moves.
    # Game over if no more moves possible
    #

    if get_empty_cells(grid):
        return True
    for row in grid:
        if any(row[i] == row[i + 1] for i in range(len(row)-1)):
            return True
    for i, val in enumerate(grid[0]):
        column = get_column(grid, i)
        if any(column[i] == column[i + 1] for i in range(len(column)-1)):
            return True
    return False


def prepare_next_turn(grid):

    #
    #
    #

    empties = get_empty_cells(grid)
    y, x = random.choice(empties)
    grid[y][x] = 2 if random.random() < 0.9 else 4
    return any_possible_moves(grid)


def print_grid(grid):

    #
    #
    #

    print("")
    wall = "+------"*len(grid[0])+"+"
    print(wall)
    for row in grid:
        meat = "|".join("{:^6}".format(val) for val in row)
        print("|{}|".format(meat))
        print(wall)


def drawBox(grid):

    border = gold
    tempList = []
    count = 0

    for row in grid:
        for val in row:
            tempList.append(val)

    for y in range(0, 400, 100):
        for x in range(0, 400, 100):
            msg = "{}".format(tempList[count])
            fillColor = colors[msg]
            myRect = pygame.draw.rect(windowSurfaceObj, border, (x + 2, y + 2, 98, 98), 0)

            windowSurfaceObj.fill(border, myRect)
            windowSurfaceObj.fill(fillColor, myRect.inflate(-5, -5))

            count += 1

            msgSurfaceObj = fontObj.render(msg, True, granite)
            msgRectobj = msgSurfaceObj.get_rect()

            msgRectobj.center = (x + 50, y + 52)
            windowSurfaceObj.blit(msgSurfaceObj, msgRectobj)


def left_possible(test_grid, left=True):

    temp_grid = copy.deepcopy(test_grid)
    print(temp_grid)
    print(test_grid)
    for i, row in enumerate(test_grid):
        test_grid[i] = push_row(row, left)

    print()
    print(temp_grid)
    print(test_grid)

    if test_grid != temp_grid:
        return True
    else:
        return False


def down_possible(test_grid, up=False):

    temp_grid = copy.deepcopy(test_grid)

    for i, val in enumerate(test_grid[0]):
        column = get_column(test_grid, i)
        new = push_row(column, up)
        set_column(test_grid, i, new)

    if test_grid != temp_grid:
        return True
    else:
        return False


def up_possible(test_grid, up=True):

    temp_grid = copy.deepcopy(test_grid)

    for i, val in enumerate(test_grid[0]):
        column = get_column(test_grid, i)
        new = push_row(column, up)
        set_column(test_grid, i, new)

    if test_grid != temp_grid:
        return True
    else:
        return False


def right_possible(test_grid, left=False):

    temp_grid = copy.deepcopy(test_grid)

    for i, row in enumerate(test_grid):
        test_grid[i] = push_row(row, left)

    if test_grid != temp_grid:
        return True
    else:
        return False

def possible(test_grid, check):

    if check == 0:
        return left_possible(test_grid, left=True)
    elif check == 1:
        return down_possible(test_grid, up=False)
    elif check == 2:
        return up_possible(test_grid, up=True)
    elif check == 3:
        return right_possible(test_grid, left=False)



def random_move(test_grid):
    # check moves possible? (called before randomMove
    # 1 2 3 4 (Left Down Up Right)

    leftFlag = left_possible(test_grid, left=True)

    downFlag = down_possible(test_grid, up=False)
    upFlag = up_possible(test_grid, up=True)
    rightFlag = right_possible(test_grid, left=False)

    rngArray = [0, 1, 2, 3]

    if leftFlag:
        rngArray[0] = 0
    elif not leftFlag:
        rngArray[0] = -1

    if downFlag:
        rngArray[1] = 1
    elif not downFlag:
        rngArray[1] = -1

    if upFlag:
        rngArray[2] = 2
    elif not upFlag:
        rngArray[2] = -1

    if rightFlag:
        rngArray[3] = 3
    elif not rightFlag:
        rngArray[3] = -1

    print(rngArray)
    print()

    rngFlag = False

    while not rngFlag:
        rng = random.randint(0, 3)
        #print(rng)
        if rngArray[rng] != -1:
            rngFlag = True
            break

    print("before return")
    if rng == 0:
        return "left"
    elif rng == 1:
        return "down"
    elif rng == 2:
        return "up"
    elif rng == 3:
        return "right"


def aiSetup(moveList):

    moveList.append(Move(0.25, 0, 0.5, 0, 0, "left", 0))
    moveList.append(Move(0.25, 1, 0.5, 0, 0, "down", 0))
    moveList.append(Move(0.25, 2, 0.5, 0, 0, "up", 0))
    moveList.append(Move(0.25, 3, 0.5, 0, 0, "right", 0))

    return moveList
    # class Move:
    #     def __init__(self, initalProb, moveNum, av, timeCounter, avgAv, name, totReward):
    #         self.initalProb = initalProb
    #         self.moveNum = moveNum
    #         self.av = av
    #         self.timeCounter = timeCounter
    #         self.avgAv = avgAv


def ai_move(moveList, test_grid):
    tieBreak = [0, 0, 0, 0, 0]
    max = -1
    counter = 0

    for i in range(len(moveList)):
        if moveList[i].av > max:
            max = moveList[i].av
            print(max)
            temp = moveList[i].moveNum
        elif moveList[i].av == max:
            tieBreak[counter] = moveList[i].moveNum
            counter += 1
            temp = moveList[i].moveNum

    if counter > 0:
        rng = random.randint(1, counter)
        temp = tieBreak[rng]
        check = moveList[temp].moveNum
        if not possible(test_grid, check):
            moveList[temp].timeCounter += 1
            moveList[temp].totReward -= 0
            moveList[temp].av = (moveList[temp].totReward / moveList[temp].timeCounter)

            move = random_move(test_grid)
            if move == "left":
                moveList[0].timeCounter += 1
                moveList[0].totReward += 0
                moveList[0].av = (moveList[0].totReward / moveList[0].timeCounter)
            elif move == "down":
                moveList[1].timeCounter += 1
                moveList[1].totReward += 0
                moveList[1].av = (moveList[1].totReward / moveList[1].timeCounter)
            elif move == "up":
                moveList[2].timeCounter += 1
                moveList[2].totReward += 0
                moveList[2].av = (moveList[2].totReward / moveList[2].timeCounter)
            elif move == "right":
                moveList[3].timeCounter += 1
                moveList[3].totReward += 0
                moveList[3].av = (moveList[3].totReward / moveList[3].timeCounter)
            return move
        else:
            max = moveList[temp].av
            moveList[temp].timeCounter += 1
            moveList[temp].totReward += 1
            moveList[temp].av = (moveList[temp].totReward / moveList[temp].timeCounter)
            return moveList[temp].name
    else:
        check = moveList[temp]
        if not possible(test_grid, check):

            moveList[temp].timeCounter += 1
            moveList[temp].totReward -= 0
            moveList[temp].av = (moveList[temp].totReward / moveList[temp].timeCounter)

            move = random_move(test_grid)
            if move == "left":
                moveList[0].timeCounter += 1
                moveList[0].totReward += 0
                moveList[0].av = (moveList[0].totReward / moveList[0].timeCounter)
            elif move == "down":
                moveList[1].timeCounter += 1
                moveList[1].totReward += 0
                moveList[1].av = (moveList[1].totReward / moveList[1].timeCounter)
            elif move == "up":
                moveList[2].timeCounter += 1
                moveList[2].totReward += 0
                moveList[2].av = (moveList[2].totReward / moveList[2].timeCounter)
            elif move == "right":
                moveList[3].timeCounter += 1
                moveList[3].totReward += 0
                moveList[3].av = (moveList[3].totReward / moveList[3].timeCounter)
            return move
        else:
            moveList[temp].timeCounter += 1
            moveList[temp].totReward += 1
            moveList[temp].av = (moveList[temp].totReward / moveList[temp].timeCounter)
            return moveList[temp].name


def stats(moveList):
    for i in range (len(moveList)):
        print("\nMove:" + str(moveList[i].name) + "\nFinal Action value:" + str(moveList[i].av)
                           + "\nAmount of times used:" + str(moveList[i].timeCounter)
                           + "\nAverage Action Value:" + str(0 / 200))


def main():

    functions = {"left": functools.partial(push_all_rows, left=True),
                 "right": functools.partial(push_all_rows, left=False),
                 "up": functools.partial(push_all_columns, up=True),
                 "down": functools.partial(push_all_columns, up=False)}
    grid = get_start_grid(*map(int, sys.argv[1:]))
    drawBox(grid)
    print_grid(grid)
    moveList = []
    aiSetup(moveList)

    windowSurfaceObj.fill(background)  # Fills in the background
    drawBox(grid)

    pygame.draw.lines(windowSurfaceObj, lighterblue, False, lineArray, 2)  # Creates Divider

    fields = ["trial", "Run", "Number of Moves", "Moves"]
    filename = "csvtest.csv"
    rows = []

    for i in range(40):
        for j in range(5):
            rowToAdd = []
            csvListMoves = []
            counter = 0
            while True:
                # time.sleep(3)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()

                grid_copy = copy.deepcopy(grid)
                test_grid = copy.deepcopy(grid)
                #get_input = random_move(test_grid)
                get_input = ai_move(moveList, test_grid)
                csvListMoves.append(get_input)
                counter += 1

                if get_input in functions:
                    functions[get_input](grid)
                elif get_input == "q":
                    break
                else:
                    print("\nInvalid choice.")
                    continue
                if grid != grid_copy:
                    if not prepare_next_turn(grid):
                        drawBox(grid)
                        print_grid(grid)
                        print("You Lose!")
                        stats(moveList)

                        rowToAdd.append(i)
                        rowToAdd.append(j)
                        rowToAdd.append(counter)
                        rowToAdd.append(csvListMoves)
                        rows.append(rowToAdd)

                        grid = get_start_grid(*map(int, sys.argv[1:]))
                        break
                print_grid(grid)

            pygame.display.update()
            fpsClock.tick(30)

    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)

main()