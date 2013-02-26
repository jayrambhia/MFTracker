from lk import *
from bb import *
from median import *

def fbtrack(imgI, imgJ, bb, numM=10, numN=10,margin=5,winsize_ncc=10):
    """
    **SUMMARY**
    
    Forward-Backward tracking using Lucas-Kanade Tracker
    
    **PARAMETERS**
    
    imgI - Image contain Object with known BoundingBox (Numpy array)
    imgJ - Following image (Numpy array)
    bb - Bounding box represented through 2 points (x1,y1,x2,y2)
    numM - Number of points in height direction.
    numN - Number of points in width direction.
    margin - margin (in pixel)
    winsize_ncc - size of the search window at each pyramid level in LK tracker (in int)
    
    **RETURNS**
    
    newbb - Bounding box of object in track in imgJ
    scaleshift - relative scale change of bb
    
    """
    nPoints = numM*numN
    sizePointsArray = nPoints*2
    #print bb, "passed in fbtrack"
    pt = getFilledBBPoints(bb, numM, numN, margin)
    #print pt,"pt"
    fb, ncc, status, ptTracked = lktrack(imgI, imgJ, pt, nPoints, winsize_ncc)

    nlkPoints = sum(status)[0]
    #print nlkPoints
    #startPoints = np.zeros(shape=(nPoints, 2))
    #targetPoints = np.zeros(shape=(nPoints, 2))
    startPoints = np.array([[],[]])
    targetPoints = np.array([[],[]])
    fbLKCleaned = []
    nccLKCleaned = []
    M = 2
    nRealPoints = 0
    #print type(startPoints), type(pt), type(ptTracked), type(targetPoints)
    for i in set(np.nonzero(ptTracked != -1)[0]):

        startPoints = np.append(startPoints, pt[i])
        targetPoints = np.append(targetPoints, ptTracked[i])
        fbLKCleaned.append(fb[i])
        nccLKCleaned.append(ncc[i])
    
    startPoints = startPoints.reshape(startPoints.shape[0]/2,2)
    targetPoints = targetPoints.reshape(targetPoints.shape[0]/2,2)
    """
    for i in range(nPoints):
        if ptTracked[i] is not -1:
            startPoints.append((pt[2 * i],pt[2*i+1]))
            targetPoints.append((ptTracked[2 * i], ptTracked[2 * i + 1]))
            fbLKCleaned[nRealPoints]=fb[i]
            nccLKCleaned[nRealPoints]=ncc[i]
            nRealPoints+=1
    """     
    medFb = getMedian(fbLKCleaned)
    medNcc = getMedian(nccLKCleaned)
    
    nAfterFbUsage = 0
    
    for i in range(1, len(startPoints)):
        if fbLKCleaned[i] <= medFb and nccLKCleaned[i] >= medNcc:
            startPoints[nAfterFbUsage] = startPoints[i]
            targetPoints[nAfterFbUsage] = targetPoints[i]
            nAfterFbUsage+=1
    startPoints = startPoints[:nAfterFbUsage]
    targetPoints = targetPoints[:nAfterFbUsage]
    newBB, scaleshift = predictBB(bb, startPoints, targetPoints, nAfterFbUsage)
    #print newBB, "fbtrack passing newBB"
    return (newBB, scaleshift)

