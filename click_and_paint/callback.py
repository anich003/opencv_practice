#callback.py

import cv2
import numpy as np

# Global variables
drawing = False
mode    = True
ix,iy   = -1, -1

# mouse callback function
def draw_circle(event,x,y, flags, param):
	global ix,iy,drawing,mode

	if event == cv2.EVENT_LBUTTONDOWN:
		drawing = True
		ix,iy   = x,y

	elif event == cv2.EVENT_MOUSEMOVE:
		if drawing == True:
			if mode == True:
				cv2.rectangle(cpy, (ix,iy), (x,y),(0,255,0), -1)
			else:
				cv2.circle(cpy, (x,y), 5, (0,0,255), -1)

	elif event == cv2.EVENT_LBUTTONUP:
		drawing = False
		if mode == True:
			cv2.rectangle(cpy, (ix,iy), (x,y), (0,255,0), -1)
		else:
			cv2.circle(cpy, (x,y), 5, (0,0,255), -1)

if __name__ == '__main__':
	img = np.zeros((512,512,3), np.uint8)
	cpy = img.copy()
	cv2.namedWindow('image')
	cv2.setMouseCallback('image',draw_circle)

	while True:
		cv2.imshow('image',cpy)
		k = cv2.waitKey(1) & 0xFF
		if k == ord('m'):
			mode = not mode
		if k == ord('r'):
			cpy = img.copy()
		elif k == 27:
			break

	cv2.destroyAllWindows()
