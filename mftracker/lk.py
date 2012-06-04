from cv2 import *
from cv2.cv import *
import math
import time
import numpy as np

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
