from mftracker import *
import cv2
cap = cv2.VideoCapture("inputcar.avi")
_, img = cap.read()
_, img = cap.read()

bb = [74, 90, 30, 40]
cv2.imshow("image", img)
cv2.waitKey(0)

mftrack("inputcar.avi", bb)