from LK import *
from BB import *
from medain import *
from copy import deepcopy

def fbtrack(imgI, imgJ, bb):
    numM = 10
    numN = 10
    nPoints = numM*numN
    sizePointsArray = nPoints*2
    
    pt = getFilledBBPoints(bb, numM, numN, 5)
    
    ptTracked = deepcopy(pt)
    
    fb, ncc, status, ptTracked = lktrack(imgI, imgJ, pt, nPoints, ptTracked, nPoints)
    
    nlkPoints = 0
    for i in range(nPoints):
        nlkPoints += status[i][0]

    startPoints = []
    targetPoints = []
    fbLKCleaned = [0.0]*nlkPoints
    nccLKCleaned = [0.0]*nlkPoints
    
    M = 2
    nRealPoints = 0

    for i in range(nPoints):
        if ptTracked[M*i] is not None:
            startPoints.append((pt[2 * i],pt[2*i+1]))
            targetPoints.append((ptTracked[2 * i], ptTracked[2 * i + 1]))
            fbLKCleaned[nRealPoints]=fb[i]
            nccLKCleaned[nRealPoints]=ncc[i]
            nRealPoints+=1
            
    medFb = getMedian(fbLKCleaned, nlkPoints)
    medNcc = getMedian(nccLKCleaned, nlkPoints)
    
    nAfterFbUsage = 0
    for i in range(nlkPoints):
        if fbLKCleaned[i] <= medFb and nccLKCleaned[i] >= medNcc:
            startPoints[nAfterFbUsage] = startPoints[i]
            targetPoints[nAfterFbUsage] = targetPoints[i]
            nAfterFbUsage+=1

    newBB, scaleshift = predictBB(bb, startPoints, targetPoints, nAfterFbUsage)
    
    return (newBB, scaleshift)

