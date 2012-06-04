from SimpleCV import Camera, Image, Display
from fbtrack import *

def mftrack():
    cam = Camera()
    p1 = None
    p2 = None
    d = Display()
    while d.isNotDone():
        try:
            img = cam.getImage()
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
    while True:
        try:
            newbb, shift = fbtrack(i.getGrayNumpy(),img1.getGrayNumpy(), bb)
            print newbb, shift
            img1.drawBB((newbb[0],newbb[1]),(newbb[2],newbb[3]),width=5)
            img1.save(d)
            time.sleep(0.1)
            i = img1.copy()
            img1 = cam.getImage()
        except KeyboardInterrupt:
            break
