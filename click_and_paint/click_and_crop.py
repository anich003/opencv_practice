# import necessary packages
import argparse
import cv2

# initialize list of reference points
refPt = []
cropping = False
selection_rectangle_endpoint = []

def click_and_crop(event, x,y, flags, param):
    """Callback function to handle mouse events"""

    # grab references to global variables
    global refPt, cropping, selection_rectangle_endpoint

    # if the left mouse button was clicked, record starting
    # (x,y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x,y)]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x,y) coordinates and indicate that
        # cropping operation is finished
        refPt.append((x,y))
        cropping = False

        # draw rectable around region of interest
        ix, iy  = refPt[0]
        fx, fy  = refPt[1]
        topLeft_x,topLeft_y = min(ix,fx), min(iy,fy)
        botLeft_x,botLeft_y = topLeft_x+abs(ix-x), topLeft_y+abs(iy-y)
        refPt = [(topLeft_x,topLeft_y),(botLeft_x,botLeft_y)]
        cv2.rectangle(image, refPt[0], refPt[1], (0,255,0), 2)
        cv2.imshow("image", image)

    # to make box appear as it is being drawn
    elif event == cv2.EVENT_MOUSEMOVE and cropping:
        selection_rectangle_endpoint = [(x,y)]


def close():
    """ close/destroy all windows """
    cv2.destroyAllWindows()

def crop():
    # if there are two reference points, then crop the region of interest
    # from the image and display it
    if len(refPt) == 2:
        roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
        cv2.imshow("ROI", roi)
        cv2.waitKey(0)

if __name__ == '__main__':
    # set up list of rois
    rois = []

    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i","--image", required=True, help="Path to the image")
    args = vars(ap.parse_args())

    # load image, clone it, and setup mouse callback function
    image = cv2.imread(args["image"])
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)

    # counter for logging
    cycle = 0
    # keep looping until the 'q' key is pressed
    while True:
        if cycle > 50:
            print(cropping,selection_rectangle_endpoint)
            cycle = 0

        # display image and wait for key press
        if not cropping:
            cv2.imshow("image", image)
        elif cropping and selection_rectangle_endpoint:
            rect_cpy = image.copy()
            cv2.rectangle(rect_cpy, refPt[0],
                          selection_rectangle_endpoint[0], (0,255,0), 1)
            cv2.imshow("image", rect_cpy)
        key = cv2.waitKey(1) & 0xFF

        # if the 'r' key is pressed, reset cropping region
        if key == ord('r'):
            print('r pressed')
            image = clone.copy()

        # check key
        if key == ord('a'):
            print('a pressed')
            print(refPt)

        # if the 'c' key is pressed, crop and show in window
        elif key == ord('c'):
            print('c pressed')
            # if there are two reference points, then crop the region of interest
            # from the image and display it
            if len(refPt) == 2:
                roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
                rois.append(roi)
                windowName = "ROI " + str(len(rois))
                cv2.imshow(windowName, roi)
                #cv2.waitKey(0)

        # if the 'q' key is pressed, quit program
        elif key == ord('q'):
            print('q pressed')
            close()
            break

        cycle += 1
