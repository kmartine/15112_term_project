"""
File Info:
    
    Creates a text based map file that can be downloaded and parsed
    to generate tile & map objects.

    Output Process:
    - generates a 2D list map from an empty list, ==>
    - converts different values to string characters, ==>
    - converts 2D list to a single string, ==>
    - writes map string to a file

"""
import pygame
import random
import math

#############################################
# basic functions
#############################################

def createMap(dimension):
    # creates an empty 2D list of specified size
    emptyMap = [[0 for i in xrange(dimension)] for i in xrange(dimension)]
    return emptyMap

def getInts(r):
    # given a set range, generate 2 random integers in a tuple
    int1 = random.randint(0,r)
    int2 = random.randint(0,r)
    return (int1, int2)

############################################
# noise generation
############################################

def interpolate(a, b, x):
    # smoothes curves
    f = (1 - math.cos(math.pi * x)) * .5
    return a*(1 - f) + b*f

def noise(x,y):
    # primary random noise function
    n = x + y *57
    n = (n<<13) ^ n
    return (1.0 - ( (n* (n**2 * 15731 + 789221) + 1376312589) 
        & 0x7fffffff) / 1073741824.0)

def smoothNoise(x,y):
    # initial smoothing
    corners = (noise(x - 1, y - 1) + noise(x + 1, y - 1) + 
        noise(x - 1, y + 1) + noise(x + 1, y + 1))/16 
    sides = (noise(x-1, y)  + noise(x + 1, y)  + noise(x, y - 1) +
        noise(x, y+1))/8
    center = noise(x,y)/4
    return corners + sides + center

def interpolNoise(x,y):
    # uses interpolation funct to smooth edges
    xInt = int(x)
    yInt = int(y)

    xFract = x - xInt
    yFract = y - yInt

    v1 = smoothNoise(xInt, yInt)
    v2 = smoothNoise(xInt + 1, yInt)
    v3 = smoothNoise(xInt, yInt + 1)
    v4 = smoothNoise(xInt + 1, yInt + 1)

    i1 = interpolate(v1, v2, xFract)
    i2 = interpolate(v3, v4, xFract)

    return interpolate(i1, i2, yFract)

def perlin2DNoise(x,y,persistence,n):
    # ties all the previous functions together
    total = 0
    for i in xrange(n):
        freq = 2**i
        amplitude = persistence**i
        total += interpolNoise(x*freq, y*freq) * amplitude
    return total

###########################################################
# map generation and filters
###########################################################

def makeSomeNoise(emptyMap):
    # applies noise funtion to each element of the an empty map
    (rows,cols) = (len(emptyMap),len(emptyMap[0]))
    persistence = .5
    n = 3
    for row in xrange(rows):
        for col in xrange(cols):
            (x,y) = getInts(5)
            offset = -x
            tile = perlin2DNoise(row,col,persistence,n)
            emptyMap[row][col] = tile*offset
    return emptyMap

def addItems(noisyMap):
    itemsPlaced = 0
    while (itemsPlaced < 5): #placing 5 items
        (row,col) = getInts(len(noisyMap)-1)
        if isClear(noisyMap, row, col):
            noisyMap[row][col] = 20
            itemsPlaced += 1
    return noisyMap

def isClear(noisyMap, row, col):
    # makes sure there's an open space to access the item
    (rows,cols) = (len(noisyMap),len(noisyMap[0]))
    dirs = [
    (-1,-1),(-1, 0),(-1,+1),
    ( 0,-1),        ( 0,+1),
    (+1,-1),(+1, 0),(+1,+1)
    ]
    for checkDir in dirs:
        (drow,dcol) = checkDir
        checkRow,checkCol = row+drow, col+dcol
        checkTile = noisyMap[checkRow][checkCol]
        if (checkTile < .5): # values for ground tiles
            return True
    return False


############################################################
# List to string conversion
############################################################

def getTypeStr(noisyMap):
    (rows,cols) = (len(noisyMap),len(noisyMap[0]))
    for row in xrange(rows):
        for col in xrange(cols):
            value = noisyMap[row][col]
            if (value == 20):
                # item location
                typeStr = "i"
            elif (value > 1 and value!= 20):
                # blocking type 1
                typeStr = "!"
            elif (value < 1 and value > .5):
                # blocking type 2
                typeStr = "#"
            elif (value < .5 and value >= 0):
                # ground type 3
                typeStr = "."
            elif (value < 0 and value > -1):
                # ground type 2
                typeStr = "-"
            else:
                # ground type 1
                typeStr = "+"
            noisyMap[row][col] = typeStr
    return noisyMap

def createString(maplist):
    rows = len(maplist)
    mapStr = ""
    for row in xrange(rows):
        mapRow = maplist[row]
        rowStr = ""
        for char in mapRow:
            rowStr += char
        mapStr = rowStr + "\n" + mapStr
    return mapStr

def getString(dimension):
    emptyMap = createMap(dimension)
    noisyMap = makeSomeNoise(emptyMap)
    mapWithItems = addItems(noisyMap) 
    mapWithStrings = getTypeStr(mapWithItems)
    outputString = createString(mapWithStrings)
    return outputString

############################################################
# File Output
############################################################

def writeMapFile(contents):
    with open('mapfiles/tempmap', 'w') as f:
        f.write(contents)

def buildFile(dimension):
    contents = getString(dimension)
    writeMapFile(contents)

############################################################
# File Reading
############################################################

def readMap(filename):
    try:
        with open(filename, 'r') as f:
            mapStr =""
            for line in f:
                mapStr += line
        return mapStr
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        return None
