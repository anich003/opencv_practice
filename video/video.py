import cv2
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(3,400)
cap.set(4,250)

while cap.isOpened():
    ret, frame = cap.read()
    print(ret)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame',frame)
    cv2.imshow('gray', gray)

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
