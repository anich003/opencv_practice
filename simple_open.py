import cv2
labels = [1,2,3,4]
img = cv2.imread('./data/shannyn.jpg')
cv2.imshow('image',img)
while True:
    k = cv2.waitKey(0) & 0xFF
    if k in list(map(lambda s: ord(str(s)),labels)):
        print('number {} selected'.format(int(chr(k))))

    elif k == ord('q'):
        break
cv2.destroyAllWindows()
