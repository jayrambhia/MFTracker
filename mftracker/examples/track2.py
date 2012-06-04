from SimpleCV import *
from cv2.cv import *
from cv2 import *
import time
import math
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
            nccLKCleaned[nRealPoints]=ncc[i][0][0]
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

def ecludianDistance(point1,point2,nPts):
    match=[]
    for i in range(nPts):
        match.append(math.sqrt((point1[i][0] - point2[i][0]) * (point1[i][0] - point2[i][0]) 
                    + (point1[i][1] - point2[i][1]) * (point1[i][1] - point2[i][1])))
    return match

def normCrossCorrelation(img1, img2, pt0, pt1, nPts, status, winsize, method):
    result = []
    for i in range(nPts):
        if status[i] == 1:
            patch1 = getRectSubPix(img1,(winsize,winsize),tuple(pt0[i]))
            patch2 = getRectSubPix(img2,(winsize,winsize),tuple(pt1[i]))
            result.append(matchTemplate(patch1,patch2,method))
        else:
            result.append(0.0)
    return result
            

def lktrack(img1, img2, ptsI, nPtsI, ptsJ, nPtsJ):
    winsize_ncc = 10
    template_pt = []
    target_pt = []
    fb_pt = []
    win_size_lk = 4
    for i in range(nPtsI):
        template_pt.append((ptsI[2*i],ptsI[2*i+1]))
        target_pt.append((ptsJ[2*i],ptsJ[2*i+1]))
        fb_pt.append((ptsI[2*i],ptsI[2*i+1]))
    
    template_pt = np.asarray(template_pt,dtype="float32")
    target_pt = np.asarray(target_pt,dtype="float32")
    fb_pt = np.asarray(fb_pt,dtype="float32")
    target_pt, status, track_error = calcOpticalFlowPyrLK(img1, img2, template_pt, target_pt, 
                                     winSize=(win_size_lk, win_size_lk), flags = OPTFLOW_USE_INITIAL_FLOW,
                                     criteria = (TERM_CRITERIA_EPS | TERM_CRITERIA_COUNT, 10, 0.03))
    fb_pt, status_bt, track_error_bt = calcOpticalFlowPyrLK(img2,img1, target_pt,fb_pt, 
                                       winSize = (win_size_lk,win_size_lk),flags = OPTFLOW_USE_INITIAL_FLOW,
                                       criteria = (TERM_CRITERIA_EPS | TERM_CRITERIA_COUNT, 10, 0.03))
    
    for i in range(nPtsI):
        if status[i] == 1 and status_bt[i] == 1:
            status[i]=1
        else:
            status[i]=0
    ncc = normCrossCorrelation(img1, img2, template_pt, target_pt, nPtsI, status, winsize_ncc, CV_TM_CCOEFF_NORMED)
    fb = ecludianDistance(template_pt, target_pt, nPtsI)
    
    for i in range(nPtsI):
        if status[i] == 1 and status_bt[i] == 1:
            ptsJ[2 * i] = target_pt[i][0]
            ptsJ[2 * i + 1] = target_pt[i][1]
        else:
            ptsJ[2 * i] = None
            ptsJ[2 * i + 1] = None
            fb[i] = None
            ncc[i] = None
            
    return fb, ncc, status, ptsJ
    
def calculateBBCenter(bb):
    center = (0.5*(bb[0] + bb[2]),0.5*(bb[1]+bb[3]))
    return center
    
def getFilledBBPoints(bb, numM, numN, margin):
    pointDim = 2
    bb_local = (bb[0] + margin, bb[1] + margin, bb[2] - margin, bb[3] - margin)
    if numM == 1 and numN == 1 :
        pts = calculateBBCenter(bb_local)
        return pts
    
    elif numM > 1 and numN == 1:
        divM = numM - 1
        divN = 2
        spaceM = (bb_local[3]-bb_local[1])/divM
        center = calculateBBCenter(bb_local)
        pt = [0.0]*(2*numM*numN)
        for i in range(numN):
            for j in range(numM):
                pt[i * numM * pointDim + j * pointDim + 0] = center[0]
                pt[i * numM * pointDim + j * pointDim + 1] = bb_local[1] + j * spaceM
                
        return pt
        
    elif numM == 1 and numN > 1:
        divM = 2
        divN = numN - 1
        spaceN = (bb_local[2] - bb_local[0]) / divN
        center = calculateBBCenter(bb_local)
        pt = [0.0]*((numN-1)*numM*pointDim+numN*pointDim)
        for i in range(numN):
            for j in range(numN):
                pt[i * numM * pointDim + j * pointDim + 0] = bb_local[0] + i * spaceN
                pt[i * numM * pointDim + j * pointDim + 1] = center[1]
        return pt
        
    elif numM > 1 and numN > 1:
        divM = numM - 1
        divN = numN - 1
    
    spaceN = (bb_local[2] - bb_local[0]) / divN
    spaceM = (bb_local[3] - bb_local[1]) / divM

    pt = [0.0]*((numN-1)*numM*pointDim+numM*pointDim)
    
    for i in range(numN):
        for j in range(numM):
            pt[i * numM * pointDim + j * pointDim + 0] = float(bb_local[0] + i * spaceN)
            pt[i * numM * pointDim + j * pointDim + 1] = float(bb_local[1] + j * spaceM)
    return pt

def getBBWidth(bb):
    return bb[2]-bb[0]+1
    
def getBBHeight(bb):
    return bb[3]-bb[1]+1
    
def predictBB(bb0, pt0, pt1, nPts):
    ofx = []
    ofy = []
    #print "nPts",str(nPts)
    for i in range(nPts):
        ofx.append(pt1[i][0]-pt0[i][0])
        ofy.append(pt1[i][1]-pt0[i][1])
    
    dx = getMedianUnmanaged(ofx, nPts)
    dy = getMedianUnmanaged(ofy, nPts)
    
    lenPdist = nPts * (nPts - 1) / 2
    dist0=[]
    for i in range(nPts):
        for j in range(i+1,nPts):
            temp0 = ((pt0[i][0] - pt0[j][0])**2 + (pt0[i][1] - pt0[j][1])**2)**0.5
            temp1 = ((pt1[i][0] - pt1[j][0])**2 + (pt1[i][1] - pt1[j][1])**2)**0.5
            dist0.append(float(temp1)/temp0)
    
    shift = getMedianUnmanaged(dist0, lenPdist)
    s0 = 0.5 * (shift-1) * getBBWidth(bb0)
    s1 = 0.5 * (shift-1) * getBBHeight(bb0)
    
    # problem here. I have chnaged this.
    p1x = abs(bb0[0] + s0 + dx)
    p1y = abs(bb0[1] + s1 + dy)
    p2x = abs(bb0[2] + s0 + dx)
    p2y = abs(bb0[3] + s1 + dy)
    
    bb1 = (p1x,p1y,p2x,p2y)
              
    return (bb1, shift)
    
def getMedianUnmanaged(a, n):
    low = 0
    high = n - 1
    median = (low + high) / 2
    while True:
        if high < 0:
            return 0
        if high <= low:
            return a[median]
        if high == low + 1:
            if a[low] > a[high]:
                a[low],a[high] = a[high],a[low]
            return a[median]
        middle = (low+high)/2
        if a[middle] > a[high]:
            a[middle],a[high] = a[high],a[middle]
        if a[low] > a[high]:
            a[low],a[high] = a[high],a[low]
        if a[middle] > a[low]:
            a[middle],a[low] = a[low],a[middle]
        a[middle],a[low+1] = a[low+1],a[middle]
        
        ll = low + 1
        hh = high
        
        while True:
            while True:
                ll +=1
                try:
                    if a[low] > a[ll]:
                        break                    
                except IndexError:
                    break
            while True:
                hh -= 1
                try:
                    if a[hh] > a[low]:
                        break
                except IndexError:
                    break
            if hh < ll:
                break
            try:
                a[ll],a[hh] = a[hh],a[ll]
            except IndexError:
                break
        try:
            a[low],a[hh] = a[hh],a[low]
        except IndexError:
            break
        if hh <= median:
            low = ll
        if hh >= median:
            high = hh - 1

def getMedian(a, n):
    median = getMedianUnmanaged(a, n)
    return median

def getBB():
    cam = VirtualCamera("inputcar.avi","video")
    p1 = None
    p2 = None
    d = Display()
    img = cam.getImage()
    
    while d.isNotDone():
        try:
            #img = cam.getImage()
            a=img.save(d)
            dwn = d.leftButtonDownPosition()
            up = d.leftButtonUpPosition()
            
            if dwn:
                p1 = dwn
            if up:
                p2 = up
                break

            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    if not p1 or not p2:
        return None
       
    bb = img.drawBB(p1,p2,width=5)
    i = img.copy()
    img.save(d)
    time.sleep(0.5)
    img1 = cam.getImage()
    print "fbtrack"
    newbb = copy(bb)
    while True:
        try:
            print newbb
            newbb, shift = fbtrack(i.getGrayNumpy(),img1.getGrayNumpy(), newbb)
            img1.drawBB((newbb[0],newbb[1]),(newbb[2],newbb[3]),width=5)
            img1.save(d)
            #time.sleep(1)
            i = img1.copy()
            img1 = cam.getImage()
        except KeyboardInterrupt:
            break

getBB()
