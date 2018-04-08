import math
import pickle
import collections
import numpy
import random
import time
import traceback
from multiprocessing import Pool

import matplotlib.pyplot as plt

beginnerSlope = 0.06
intermediateSlope = 0.25
difficultSlopes = 0.4

class Point():
    def __init__(self, x, y, h, _id):
        self.x = x
        self.y = y
        self.h = h
        self._id = _id

class Layer():
    def __init__(self, h, points=[]):
        self.h = h
        self.points = points
        self.pointsNum = 1

class Solution():
    def __init__(self, path, degs, slopes, distance):
        self.path = path
        self.degs = degs
        self.slopes = slopes
        self.distance = distance

def computeslopes(point1, point2):
    return abs(point2.h - point1.h) / (math.sqrt((point1.x - point2.x) ** 2 +  (point1.y - point2.y) ** 2))

def computeDistance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2 + (point1.h - point2.h) ** 2)

def computeHorizontalDistance(point1,point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def computeDegree(point1, point2, point3):
    a = [point1.x - point2.x, point1.y - point2.y, point1.h - point2.h]
    b = [point3.x - point2.x, point3.y - point2.y, point3.h - point2.h]
    vecProduct = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    norm_a = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)
    norm_b = math.sqrt(b[0] ** 2 + b[1] ** 2 + b[2] ** 2)
    return math.acos(min(1, max(-1, (vecProduct / (norm_a * norm_b))))) * 180 / math.pi

def intersection(line1, line2):
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    if x3 == x4:
        (x1, y1), (x2, y2) = line2
        (x3, y3), (x4, y4) = line1
    if x1 == x2:
        if x3 == x4:
            if x1 == x3:
                y1, y2 = min(y1, y2), max(y1, y2)
                if (y4 >= y1 and y4 <= y2) or (y3 >= y1 and y3 <= y2):
                    return 1000
                else:
                    return 0
            return 0
        else:
            x3, x4 = min(x3, x4), max(x3, x4)
            if x1 >= x3 and x1 <= x4:
                k2 = (y4 - y3) / (x4 - x3)
                b2 = y4 - k2 * x4
                y0 = k2 * x1 + b2
                y1, y2 = min(y1, y2), max(y1, y2)
                if y0 >= y1 and y0 <= y2:
                    return 1
                else:
                    return 0
            else:
                return 0
    k1 = (y2 - y1) / (x2 - x1)
    k2 = (y4 - y3) / (x4 - x3)
    if k1 == k2:
        b1 = k1 * x1 + y1
        b2 = k2 * x2 + y2
        if b1 == b2:
            x1, x2 = min(x1, x2), max(x1, x2)
            if ((x4 >= x1 and x4 <= x2) or (x3 >= x1 and x3 <= x2)):
                return 1000
            else:
                return 0
        else:
            return 0
    x0 = (k1 * x2 - k2 * x4 - y2 + y4) / (k1 - k2)
    x1, x2 = min(x1, x2), max(x1, x2)
    x3, x4 = min(x3, x4), max(x3, x4)
    if x1 <= x0 and x0 <= x2 and x3 <= x0 and x0 <= x4:
        return 1
    else:
        return 0

def intersectionOfMany(lines1, lines2):
    num = 0
    for t_line in lines1:
        for tt_line in lines2:
            num += intersection(t_line, tt_line)
    return num

pointsNumForEachHeight = collections.defaultdict(int)
pointsDict = collections.defaultdict(list)
heightList = []
layers = []


def loadData(filename):
    heightSet = set([])
    with open(filename) as f:
        lines = [x.strip() for x in f.readlines()]
        for line in lines:
            points = [x.strip() for x in line.split()]
            trueheight = float(points[0])
            height = int(trueheight) / 20 * 20
            heightSet.add(height)
            for point in points[1:]:
                x, y = [float(x) for x in point.split(',')]
                newpoint = Point(x, y, trueheight, pointsNumForEachHeight[height])
                pointsNumForEachHeight[height] += 1
                pointsDict[height].append(newpoint)
    for h in heightSet:
        heightList.append(h)
    heightList.sort(reverse=True)
    for h in heightList:
        layers.append(Layer(h, pointsDict[h]))

def preProcess():
    pass

visitedPoint = set([])


def generatePath(randomseed=None):
    random.seed(randomseed)
    isStart = 1
    startLayer = random.choice(range(len(layers) - 30))
    lastLayer = startLayer
    lastPoint = random.choice(range(layers[lastLayer].pointsNum))
    path = []
    for i in range(lastLayer):
        path.append(None)
    path.append(lastPoint)
    degrees = []
    slopes = []
    totalDistance = 0
    while lastLayer < len(layers) - 2:
        toBeChoosedPoints = []
        probs = []
        t_slopes = []
        for point in layers[lastLayer + 1].points:
            toBeChoosedPoints.append((lastLayer + 1, point._id))
        for point in layers[lastLayer + 2].points:
            toBeChoosedPoints.append((lastLayer + 2, point._id))
        toBeChoosedPoints = [point for point in toBeChoosedPoints if computeHorizontalDistance(layers[point[0]].points[point[1]], layers[lastLayer].points[lastPoint]) < 250]

        if isStart == 1:
            isStart = 0
            for point in toBeChoosedPoints:
                slope = computeslopes(layers[lastLayer].points[lastPoint], layers[point[0]].points[point[1]])
                t_slopes.append(slope)
                if slope <= intermediateSlope:
                    probs.append(6.66)
                elif slope <= difficultSlopes:
                    probs.append(1.64)
                elif slope <= 0.6:
                    probs.append(1.6)
                else:
                    probs.append(0)
            probTarget = sum(probs) * random.random()
            if probTarget == 0:             
                return Solution(path, degrees, slopes, totalDistance)
            for i, prob in enumerate(probs):
                probTarget -= prob
                if probTarget < 0:
                    if toBeChoosedPoints[i][0] - lastLayer == 1:
                        path.append(toBeChoosedPoints[i][1])
                    else:
                        path.append(None)
                        path.append(toBeChoosedPoints[i][1])
                    totalDistance += computeDistance(layers[toBeChoosedPoints[i][0]].points[toBeChoosedPoints[i][1]], layers[lastLayer].points[lastPoint])
                    lastLayer = toBeChoosedPoints[i][0]
                    lastPoint = toBeChoosedPoints[i][1]
                    slopes.append(t_slopes[i])
                    break
            continue
        t_degs = []
        for point in toBeChoosedPoints:
            if path[-2] != None:
                deg = computeDegree(layers[len(path) - 2].points[path[-2]], layers[lastLayer].points[lastPoint], layers[point[0]].points[point[1]])
            else:
                deg = computeDegree(layers[len(path) - 3].points[path[-3]], layers[lastLayer].points[lastPoint], layers[point[0]].points[point[1]])
            t_degs.append(deg)
            slope = computeslopes(layers[lastLayer].points[lastPoint], layers[point[0]].points[point[1]])
            t_slopes.append(slope)
            if deg <= 45:
                probs.append(0)
            elif slope <= intermediateSlope:
                probs.append(6.66)
            elif slope <= difficultSlopes:
                probs.append(1.64)
            elif slope <= 0.6:
                probs.append(1.2)
            else:
                probs.append(0)
        probTarget = sum(probs) * random.random()
        if probTarget == 0:
            break
        for i, prob in enumerate(probs):
            probTarget -= prob
            if probTarget < 0:
                if toBeChoosedPoints[i][0] - lastLayer == 1:
                    path.append(toBeChoosedPoints[i][1])
                else:
                    path.append(None)
                    path.append(toBeChoosedPoints[i][1])
                totalDistance += computeDistance(layers[toBeChoosedPoints[i][0]].points[toBeChoosedPoints[i][1]], layers[lastLayer].points[lastPoint])
                lastLayer = toBeChoosedPoints[i][0]
                lastPoint = toBeChoosedPoints[i][1]
                degrees.append(t_degs[i])
                slopes.append(t_slopes[i])
                break
    return Solution(path, degrees, slopes, totalDistance)


def score(solution):
    s = solution.distance
    for deg in solution.degs:
        s -= 0.5 * max(0, 120 - deg) ** 2
    return s

def showGraph(graph, savePath=None):
    for s in graph:
        x = []
        y = []
        for i, p_id in enumerate(s.path):
            if p_id == None:
                continue
            x.append(layers[i].points[p_id].x)
            y.append(layers[i].points[p_id].y)
        plt.plot(x,y)
    if savePath:
        plt.savefig(savePath)
    else:
        plt.show()
    plt.clf()

def showPath(solution):
    x = []
    y = []
    for i, p_id in enumerate(solution.path):
        if p_id == None:
            continue
        print '---->', layers[i].h, layers[i].points[p_id].x / 1000 * 94, layers[i].points[p_id].y / 1000 * 77
        x.append(layers[i].points[p_id].x)
        y.append(layers[i].points[p_id].y)
    plt.plot(x, y)
    plt.show()
    

def trainSave(filename):
    loadData(filename)
    solutions = []
    for i in range(10000):
        if i %100 == 0: print i
        try:            
            solutions.append(generatePath(int(time.time()) + i))
        except Exception as e:
            print e
    pickle.dump(solutions, open(filename.split('.')[0] + 'solutions.pkl', 'wb'))

def t_generatePath(seed):
    try:
        if not layers: loadData('center.txt')
        return generatePath(seed)
    except Exception as e:
        print e
        traceback.print_exc()
        
def trainSaveF(filename):
    loadData(filename)
    solutions = []
    tasks = [i + int(time.time()) for i in range(200000)]
    pool = Pool(8)
    solutions = pool.map(t_generatePath, tasks)
    pool.close()
    pool.join()
    solutions = [x for x in solutions if x is not None]
    print solutions[0].path
    pickle.dump(solutions, open(filename.split('.')[0] + 'solutions.pkl', 'wb'))

def path2coor(path):
    lines = []
    for i in range(len(path) - 1):
        if path[i] is None:
            continue
        if path[i + 1] is not None:
            j = i + 1
        else:
            j = i + 2
        lines.append(((layers[i].points[path[i]].x, layers[i].points[path[i]].y), (layers[j].points[path[j]].x ,layers[j].points[path[j]].y)))
    return lines

def generateGraph(solutions, randomseed = 0, targetDistance = 20000):
    random.seed(randomseed)
    linesPool = []
    graph = []
    choosedSolutions = set([])
    totScore = 0
    currDistance = 0
    ix = random.randint(1,100)
    linesPool.extend(path2coor(solutions[ix].path))
    currDistance += solutions[ix].distance
    totScore += solutions[ix].distance
    while currDistance <= targetDistance:
        maxscore = -1
        maxi = 0
        for i in range(ix, ix+8000):
            if i in choosedSolutions:
                continue
            
            score = solutions[i].distance - 150 * intersectionOfMany(linesPool, path2coor(solutions[i].path))
            if score > maxscore:
                maxscore = score
                maxi = i
        print maxscore
        if maxscore <= 0:
            print 'Warning'
            return graph, totScore, currDistance
        else:
            choosedSolutions.add(maxi)
            print maxi, solutions[maxi].distance, intersectionOfMany(linesPool, path2coor(solutions[i].path))
            currDistance += solutions[maxi].distance
            totScore += maxscore
            graph.append(solutions[maxi])
            ix = ix + random.randint(1,2000)
            linesPool.extend(path2coor(solutions[maxi].path))
    return graph, totScore, currDistance

def main():
    loadData('center.txt')
    solutions = pickle.load(open('centersolutions.pkl', 'rb'))
    for solution in solutions:
        solution.score = score(solution)
    solutions.sort(key = lambda x: x.score, reverse = True)
    pickle.dump(solutions, open('centersolutions.pkl', 'wb'))
    maxInfo = None
    maxscore = -1
    infoList = []
    for i in range(10):
        seed = i + int(time.time())
        g, s, dis = generateGraph(solutions, seed, 100000)
        infoList.append((g, s, dis))
        print i, seed, i, s, dis
        showGraph(g, str(seed) + '.png')
        pickle.dump(g, open(str(seed)+'.pkl', 'wb'))
        if s > maxscore:
            maxscore = score
            maxInfo = (g, s, dis)
    pickle.dump(infoList, open('result.pkl','wb'))
    print maxInfo[2]
    print maxInfo[1]
    showGraph(maxInfo[0])


if __name__ == '__main__':
    main()

    
