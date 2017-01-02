# import necessary packages
import argparse
import cv2
import pandas as pd
import numpy as np

# initialize global variables
painting = False
points   = set()
modes    = ['idle','label','erase']
mode_idx = 0
mode     = modes[mode_idx]
labels   = [1,2,3,4]
current_label = labels[label_idx]

label_colors = {
    1:(0,255,0),
    2:(0,0,255),
    3:(255,0,0),
    4:(255,125,0)
}

# TODO Add color picker so label colors can be dynamic at run time
# TODO Ensure label overwrites are handled
# TODO Add erasure mode to 'undo' mislabeled areas

def onMouse(event, x,y, flags, param):
    """Callback function to handle mouse events"""
    global painting, points
    print('mode: {} @ {},{}, labeled: {}'.format(mode,x,y,current_label))
    if event == cv2.EVENT_LBUTTONDOWN:
        if mode == 'label':
            painting = True
            points.add((x,y,current_label))
            cv2.circle(clone, (x,y), 2, label_colors[current_label],-1)

    elif event == cv2.EVENT_MOUSEMOVE:
        if painting == True:
            points.add((x,y,current_label))
            cv2.circle(clone, (x,y), 2, label_colors[current_label],-1)

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
    #global modes, modes_idx, labels, label_idx, current_label
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser(description='Open and hand annotate an image')
    ap.add_argument('-i',"--image", required=True,
                    help="Path to the image")
    args = vars(ap.parse_args())

    # load image, clone it, and setup mouse callback function
    image = cv2.imread(args["image"])
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", onMouse)

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
            mode_idx += 1
            mode = modes[mode_idx % len(modes)]

        elif key in list(map(lambda s: ord(str(s)),labels)):
            current_label = int(chr(key))
            print('number {} selected'.format(int(chr(key))))

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
