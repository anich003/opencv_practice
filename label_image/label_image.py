##############################################################################
# DONE Downsample image to reasonable size
# TODO **Implement bayesian esimate in new window based on labeled data
# REACH
# TODO Improve painting process so it doesn't skip on fast mouse
# TODO Add ghost brush over/under mouse so user knows current size of brush
# TODO Add color picker so label colors can be dynamic at run time
# TODO Resizable windows
##############################################################################

# Import necessary packages
import argparse
import cv2
import pandas as pd
import numpy as np

##############################################################################
# Initialize global variables
##############################################################################
painting = False
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
brush_idx   = 0
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

def posterior_onMouse(event, x,y, flags, param):
    "Handle mouse events on posterior window"
    if event == cv2.EVENT_LBUTTONDOWN:
        #print('Mouse at:\t{},{}'.format(x,y))
        cv2.destroyWindow('posterior')



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

def _reset_data():
    global mus, covs, priors
    mus = []
    covs = []
    priors = []

def _print_stats():
    "Print current pixel statistics to terminal"
    for i,mu in enumerate(mus):
        print('Label {0}:'.format(i))
        print(mu)
        print()

def generate_stats():
    """
    Given a mask and an original image, generate statistics for
    each label

    Input:

    Output:

    """
    print('generating statistics')

    # if recently 'reset' and points is currently empty, do nothing
    # if not points:
    #     return

    # Convert set of tuples to pandas DataFrame
    #df = pd.DataFrame(np.asarray(points), columns = ['x','y','label'])
    #df.to_csv('../df.csv', index=False)

    # Grab bgr values from original image
    # df[['b','g','r']] = df.apply(lambda row: img[row.x,row.y], axis=1)

    # print out current statistics
    # print(df.groupby(['label']).mean().ix[:,['r','g','b']])

def mvn_likelihood(x,mu,cov):
    from numpy import linalg
    k = len(mu)
    A = np.log(linalg.det(cov))
    B = (x-mu).dot(linalg.inv(cov).dot((x-mu)))
    C = k*np.log(2*np.pi)
    return np.exp(-0.5 * (A + B + C))
###############################################################################

if __name__ == '__main__':

    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser(description='Open and hand annotate an image')
    ap.add_argument('-i',"--image", required=True,
                    help="Path to the image")
    args = vars(ap.parse_args())

    # load image, clone it, and setup mouse callback function
    img = cv2.imread(args["image"])

    # Desired image dimensions (downsampled)
    from skimage.transform import resize
    max_width = 300
    h,w,_ = img.shape
    scale = max_width / w
    new_height = int(h * scale)
    img = resize(img,(new_height, max_width))

    # Create copy where annotations will take place
    cpy = img.copy()

    # Set up a resizable window to keep number of pixels reasonable
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 400,300)
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
            _reset_data()

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
            _reset_data()

            mask = generate_mask(img,cpy)

            for label,color in label_colors.items():
                xs,ys = np.where(np.all(mask==color, axis=-1))

                if (len(xs) > 0) and (len(ys) > 0):
                    tmp = img[xs,ys]

                    mus.append(tmp.mean(axis=0))
                    covs.append(np.cov(tmp.T))
                    priors.append(tmp.shape[0])

            _print_stats()


            if len(mus) == 2: # only want to handle 2-label case
                # Calculate posterior
                mu_class1    = mus[0]
                cov_class1   = covs[0]
                prior_class1 = priors[0]

                mu_class2    = mus[1]
                cov_class2   = covs[1]
                prior_class2 = priors[1]

                like_1 = np.apply_along_axis(mvn_likelihood,2,img,mu_class1,cov_class1)
                like_2 = np.apply_along_axis(mvn_likelihood,2,img,mu_class2,cov_class2)

                den    = like_1 * prior_class1 + like_2 * prior_class2
                num    = like_1 * prior_class1

                posterior = num / den

                # Create posterior window
                cv2.namedWindow('posterior')
                cv2.imshow('posterior', posterior)
                cv2.setMouseCallback('posterior',posterior_onMouse)

            else:

                print('Multi-Class posterior not yet implemented')


        # if the 'q' key is pressed, quit program
        elif key == ord('q'):
            print('q pressed')
            _close()
            break

        elif key == ord('s'):
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
