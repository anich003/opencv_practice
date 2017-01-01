#simple_callback.py
import cv2
import numpy as np

if False:
	events = [i for i in dir(cv2) if 'EVENT' in i]
	for event in events:
		print(event, sep='\n', end='\n')

# Callback function
def draw_circle(event, x,y, flags, param):
	if event == cv2.EVENT_LBUTTONDOWN:
		print('dbl clicked @ {},{}'.format(x,y))

if __name__ == '__main__':
	img = np.zeros((256,256,3), np.uint8)
	cpy = img.copy()

	cv2.namedWindow('image')
	cv2.setMouseCallback('image',draw_circle)

	while True:
		cv2.imshow('image',cpy)
		k = cv2.waitKey(0) & 0xFF
		if k == ord('q') or k == 27:
			break

	cv2.destroyAllWindows()
