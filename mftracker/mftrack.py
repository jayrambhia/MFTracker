from fbtrack import *
from bb import getBB, getRectFromBB
import cv2
class mftrack:
    def __init__(self, source=None, bb=None):
        self.mouse_p1 = None
        self.mouse_p2 = None
        self.mouse_drag = False
        self.bb = None
        self.img = None
        self.mouseFlag = True
        if source:
            self.cam = cv2.VideoCapture(source)
        else:
            self.cam = cv2.VideoCapture(0)
        if not bb:
            self.start()
        else:
            self.bb = bb
            _, self.img = self.cam.read()
            self.track()
        
    def start(self):
        _, self.img = self.cam.read()
        cv2.imshow("img", self.img)
        cv.SetMouseCallback("img", self.__mouseHandler, None)
        if not self.bb:
            _, self.img = self.cam.read()
            cv2.imshow("img", self.img)
            cv2.waitKey(30)
        cv2.waitKey(0)
    
    def __mouseHandler(self, event, x, y, flags, params):
        if self.mouseFlag == False:
            return
        _, self.img = self.cam.read()
        if event == cv.CV_EVENT_LBUTTONDOWN and not self.mouse_drag:
            self.mouse_p1 = (x, y)
            self.mouse_drag = True
        elif event == cv.CV_EVENT_MOUSEMOVE and self.mouse_drag:
            cv2.rectangle(self.img, self.mouse_p1, (x, y), (255, 0, 0), 1, 8, 0)
        elif event == cv.CV_EVENT_LBUTTONUP and self.mouse_drag:
            self.mouse_p2 = (x, y)
            self.mouse_drag=False
        cv2.imshow("img",self.img)
        cv2.waitKey(30)
        if self.mouse_p1 and self.mouse_p2:
            cv2.destroyWindow("img")
            print self.mouse_p1
            print self.mouse_p2
            xmax = max(self.mouse_p1[0],self.mouse_p2[0])
            xmin = min(self.mouse_p1[0],self.mouse_p2[0])
            ymax = max(self.mouse_p1[1],self.mouse_p2[1])
            ymin = min(self.mouse_p1[1],self.mouse_p2[1])
            self.bb = [xmin,ymin,xmax-xmin,ymax-ymin]
            self.track()

    def track(self):
        self.mouseFlag = False
        oldg = cv2.cvtColor(self.img, cv2.cv.CV_BGR2GRAY)
        bb = self.bb
        bb = [bb[0], bb[1], bb[0]+bb[3], bb[1]+bb[3]]
        while True:
            t = time.time()
            _, img = self.cam.read()
            newg = cv2.cvtColor(img, cv2.cv.CV_BGR2GRAY)
            newbb, shift = fbtrack(oldg, newg, bb, 12, 12, 3, 12)
            #print newbb, "newbb", shift, "shift"
            oldg = newg
            bb = newbb
            cv2.rectangle(img, (bb[0], bb[1]), (bb[2], bb[3]), (255, 0, 0))
            cv2.imshow("Media Flow Tracker", img)
            print (time.time() - t)*1000,"msec"
            k = cv2.waitKey(1)
            if k == 27:
                self.mouseFlag = False
                cv2.destroyAllWindows()
                break
        return None