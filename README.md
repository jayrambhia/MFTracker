MFTracker
=========

Medain Flow Tracker made in python using OpenCV 2.3.1 and SimpleCV

###SETUP:

    $ sudo python setup.py install

###Example:
    
    >>> import mftracker
    >>> mftracker.mftrack()
    
###Requirements:
    OpenCV 2.3.1 or higher (python interface - cv2)
    numpy
    SimpleCV (Only for mftracker.mftrack() - which uses SimpleCV Display, Camera, ImageClass. 
              You can use OpenCV's similar stuff if you don't have SimpleCV.)
