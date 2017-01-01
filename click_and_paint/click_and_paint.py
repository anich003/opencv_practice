# import necessary packages
import argparse
import cv2

# initialize global variables
painting = False
mode     = True
mode_color = {
    True:(0,255,0),
    False:(0,0,255)
}

def click_and_paint(event, x,y, flags, param):
    """Callback function to handle mouse events"""
    global painting
    if event == cv2.EVENT_LBUTTONDOWN:
        painting = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if painting == True:
            cv2.circle(clone, (x,y), 2, mode_color[mode],-1)

    elif event == cv2.EVENT_LBUTTONUP:
        painting = False


def close():
    """ close/destroy all windows """
    cv2.destroyAllWindows()

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

        elif key == ord('m'):
            mode = not mode

        # if the 'q' key is pressed, quit program
        elif key == ord('q'):
            print('q pressed')
            close()
            break

        cycle += 1
