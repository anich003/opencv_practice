##############################################################################
# TODO Remove list of points and inplace add list of mu and cov for each label
# TODO Implement bayesian esimate in new window based on labeled data
# TODO Improve painting process so it doesn't skip on fast mouse
# TODO Add ghost brush over/under mouse so user knows current size of brush
# TODO Add color picker so label colors can be dynamic at run time
##############################################################################

# Import necessary packages
import argparse
import cv2
import pandas as pd
import numpy as np

from skimage import io
##############################################################################
# Initialize global variables
##############################################################################
painting = False
points   = []
modes    = ['idle','label','erase']
mode_idx = 0
mode     = modes[mode_idx]
labels   = [1,2,3,4]
current_label = labels[0]

label_colors = {
    1:(0,255,0),
    2:(0,0,255),
    3:(255,0,0),
    4:(255,125,125)
}

brush_sizes = [2,4,6,8,10]
brush_idx   = 2
brush_size = brush_sizes[brush_idx]

erase_color = (1,1,1)

# Statistics vars
mus    = []
covs   = []
priors = []

##############################################################################
# Helper functions
##############################################################################
def onMouse(event, x,y, flags, param):
    """Callback function to handle mouse events"""
    global painting
    #print('mode: {} @ {},{}, labeled: {}'.format(mode,x,y,current_label))

    if event == cv2.EVENT_LBUTTONDOWN:
        painting = True
        if mode == 'label':
            cv2.circle(cpy, (x,y),
                       brush_size,
                       label_colors[current_label],-1)
        elif mode == 'erase':
            cv2.circle(cpy, (x,y),
                       brush_size,
                       erase_color,-1)

    elif event == cv2.EVENT_MOUSEMOVE:
        if painting == True:
            if mode == 'label':
                cv2.circle(cpy, (x,y),
                           brush_size,
                           label_colors[current_label],-1)
            elif mode == 'erase':
                cv2.circle(cpy, (x,y),
                           brush_size,
                           erase_color,-1)

    elif event == cv2.EVENT_LBUTTONUP:
        painting = False


def _close():
    """ close/destroy all windows """
    cv2.destroyAllWindows()

def generate_mask(img,cpy):
    """
    Takes original and annotated image and returns mask,
    where each color is a different label

    Input:
    img    -    original image
    cpy    -    annotated image

    Returns:
    mask   -    Blacked out image, except for annotations
    """

    xs,ys = np.where(cpy!=img)[:-1]
    mask  = np.zeros_like(cpy)
    mask[xs,ys] = cpy[xs,ys]
    return mask


def generate_stats():
    """
    Given a mask and an original image, generate statistics for
    each label

    Input:

    Output:

    """
    print('generating statistics')

    # if recently 'reset' and points is currently empty, do nothing
    if not points:
        return

    # Convert set of tuples to pandas DataFrame
    df = pd.DataFrame(np.asarray(points), columns = ['x','y','label'])
    #df.to_csv('../df.csv', index=False)

    # Grab bgr values from original image
    df[['b','g','r']] = df.apply(lambda row: img[row.x,row.y], axis=1)

    # print out current statistics
    print(df.groupby(['label']).mean().ix[:,['r','g','b']])
###############################################################################

if __name__ == '__main__':

    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser(description='Open and hand annotate an image')
    ap.add_argument('-i',"--image", required=True,
                    help="Path to the image")
    args = vars(ap.parse_args())

    # load image, clone it, and setup mouse callback function
    img = cv2.imread(args["image"])
    cv2.imwrite('../data/img.jpg', img)
    cpy = img.copy()

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", onMouse)

    # counter for logging
    cycle = 0

    # keep looping until the 'q' key is pressed
    while True:
        cv2.imshow('image',cpy)

        if cycle > 50:
            # Log events to console
            cycle = 0

        key = cv2.waitKey(1) & 0xFF

        # if the 'r' key is pressed, reset image
        if key == ord('r'):
            print('r pressed')
            cpy = img.copy()
            points = []
            mus = []
            covs = []
            priors = []

        #    cycle through mouse modes: idle, label, erase
        elif key == ord('m'):
            mode_idx += 1
            mode = modes[mode_idx % len(modes)]
            print('Current mode: {}'.format(mode))

        # check to see if a number was selected and if so, change
        # label number to corresponding number
        elif key in list(map(lambda s: ord(str(s)),labels)):
            current_label = int(chr(key))
            print('number {} selected'.format(int(chr(key))))

        # check for '[' or ']' key press to increase or decrease brush size
        elif key == ord('['):
            brush_idx -= 1
            brush_size = brush_sizes[brush_idx % len(brush_sizes)]
        elif key == ord(']'):
            brush_idx += 1
            brush_size = brush_sizes[brush_idx % len(brush_sizes)]

        # Calculate statistics
        elif key == ord('c'):

            #mask = np.where(cpy!=img,cpy,0)
            mask = generate_mask(img,cpy)
            #tmp = []
            for label,color in label_colors.items():
                xs,ys = np.where(np.all(mask==color, axis=-1))
                #xs = matches[0]
                #ys = matches[1]
                #tmp.append(list(zip(xs,ys,[label]*len(xs))))
                if (len(xs) > 0) and (len(ys) > 0):
                    tmp = img[xs,ys]

                    mus.append(tmp.mean(axis=0))
                    covs.append(np.cov(tmp.T))
                    priors.append(tmp.shape[0])
            # points = []
            # for sublist in tmp:
            #     points.extend(sublist)

            #generate_stats()

            for mu in mus:
                print(mu, end='\n')
            print()
            for cov in covs:
                print(cov, end='\n')

        # general purpose status checking
        elif key == ord('a'):
            #print('length of points:\t{}'.format(len(points)))
            #print(to_erase)
            print('hello!')

        # if the 'q' key is pressed, quit program
        elif key == ord('q'):
            print('q pressed')
            _close()
            break

        elif key == ord('s'):
            #io.imsave('../data/cpy.jpg', cpy)
            cv2.imwrite('../data/cpy.jpg', cpy)
            print('cpy saved!')

        # Check to see if any pixels in cpy match erase color
        # and if so revert that part of cpy back to img
        to_erase = np.where(np.all(cpy==erase_color, axis=-1))
        if to_erase:
            xs = to_erase[0]
            ys = to_erase[1]
            cpy[xs,ys] = img[xs,ys]

        cycle += 1
