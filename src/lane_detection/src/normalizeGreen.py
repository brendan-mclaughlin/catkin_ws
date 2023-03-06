import cv2
import numpy as np

## Read
img = cv2.imread('/home/selfdrivingcar/catkin_ws/src/lane_detection/src/images/img2.jpg')

## convert to hsv


dst = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)

hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)

## mask of green (36,25,25) ~ (86, 255,255)
# mask = cv2.inRange(hsv, (36, 25, 25), (86, 255,255))
grassmask = cv2.inRange(hsv, (35, 20, 20), (77, 255,255))
deadGrassMask = cv2.inRange(hsv, (20, 43, 46), (34, 255,255))
dirtmask=cv2.inRange(hsv,(19,24,33),(50,50,255))
mask=cv2.bitwise_or(grassmask,deadGrassMask)
mask=cv2.bitwise_or(mask,dirtmask)


## slice the green0
imask = mask>0
green = np.zeros_like(img, np.uint8)
green[imask] = img[imask]










## save 
cv2.imshow("Original", img)

cv2.imshow("Blur", green)

cv2.imwrite("grassImg.png",green)
cv2.waitKey(0)
cv2.destroyAllWindows()


