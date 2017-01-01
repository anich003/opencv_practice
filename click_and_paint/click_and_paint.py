# import necessary packages
import argparse
import cv2
import pandas as pd
import numpy as np

# initialize global variables
painting = False
mode     = True
mode_color = {
    True:(0,255,0),
    False:(0,0,255)
}

# TODO Update to allow for labeling of more than 2 different groups

points = set()

def click_and_paint(event, x,y, flags, param):
    """Callback function to handle mouse events"""
    global painting, points
    if event == cv2.EVENT_LBUTTONDOWN:
        painting = True
        points.add((x,y,mode))
        cv2.circle(clone, (x,y), 2, mode_color[mode],-1)

    elif event == cv2.EVENT_MOUSEMOVE:
        print('mode: {} @ {},{}'.format(mode,x,y))
        if painting == True:
            points.add((x,y,mode))
            cv2.circle(clone, (x,y), 2, mode_color[mode],-1)

    elif event == cv2.EVENT_LBUTTONUP:
        painting = False


def _close():
    """ close/destroy all windows """
    cv2.destroyAllWindows()

def generate_stats():
    print('generating statistics')

    # if recently 'reset' and points is currently empty, do nothing
    if not points:
        return

    # Convert set of tuples to pandas DataFrame
    df = pd.DataFrame(np.asarray(list(points)), columns = ['x','y','label'])
    # Grab bgr values from original image
    df[['b','g','r']] = df.apply(lambda row: image[row.y,row.x], axis=1)

    # print out current statistics
    print(df.groupby(['label']).mean().ix[:,['r','g','b']])

if __name__ == '__main__':
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i","--image", required=True,
                    help="Path to the image")
    args = vars(ap.parse_args())

    # load image, clone it, and setup mouse callback function
    image = cv2.imread(args["image"])
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_paint)

    # counter for logging
    cycle = 0
    # keep looping until the 'q' key is pressed
    while True:
        cv2.imshow('image',clone)

        if cycle > 50:
            # Log events to console
            cycle = 0

        key = cv2.waitKey(1) & 0xFF

        # if the 'r' key is pressed, reset image
        if key == ord('r'):
            print('r pressed')
            clone = image.copy()
            points = set()

        elif key == ord('m'):
            mode = not mode

        elif key == ord('a'):
            print('length of points:\t{}'.format(len(points)))

        # Calculate statistics
        elif key == ord('c'):
            generate_stats()

        # if the 'q' key is pressed, quit program
        elif key == ord('q'):
            print('q pressed')
            _close()
            break

        cycle += 1
