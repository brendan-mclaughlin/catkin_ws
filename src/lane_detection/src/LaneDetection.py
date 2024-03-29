import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import cv2
import os
from scipy import signal
from scipy.signal import find_peaks
from sklearn import linear_model
from os import listdir
from remoteControl import MotorControl
from clear_cache import clear as clear_cache
import matplotlib  # inline
import time
import rospy
import math

prev = 0


# No longer used but here in case of scaling purposes
def getResizedImage(img, scale_percent=20):

    # img = cv2.imread(r'/home/ubuntu/catkin_ws/src/lane_detection/src/images' + fileName)

    # Resize
    # assert not isinstance(img,type(None)), 'image not found'

    print('Original Dimensions : ', img.shape)
    # scale_percent = 20 # percent of original size
    # img.set(3,640)
    # img.set(4,480)
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    resized_image = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    # Change COLOR mode
    # rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)

    return resized_image


# Makes the output frame graph, usesful for debugging but not for live feed
def plotFrame(intercept, copy3, theme, grey):
    # create figure
    fig = plt.figure(figsize=(20, 15))

    # setting values to rows and column variables
    rows = 1
    columns = 3
    fig.add_subplot(rows, columns, 1)
    plt.imshow(grey)
    fig.add_subplot(rows, columns, 2)

    # showing image
    plt.imshow(copy3)
    # plt.axis('off')

    # Adds a subplot at the 2nd position
    fig.add_subplot(rows, columns, 3)

    # for i in range(len(lefts)):
    #     plt.scatter(lefts[i], Y_coor[i], color='blue')
    # plt.plot([X_intercept, 100 + theme.shape[1]/2], [Y_intercept, theme.shape[1]], color="red", linewidth=3)
    plt.scatter(intercept[0], intercept[1], color='blue')
    plt.plot([theme.shape[1]/2,  theme.shape[1]/2],
             [0, theme.shape[1]], color="red", linewidth=3)
    plt.imshow(theme)

    plt.show(block=False)
    plt.pause(.8)
    plt.close()


def response(intercept, shape, motorControl):
    # print(intercept)
    global prev

    # 0is left
    # 1 if right

    # xMax=shape[0]
    xMax = 320
    yMax = 240
    # yMax=shape[1]

    x = intercept[0]
    y = intercept[1]
    # motorControl=MotorControl()

    xDif = np.abs(xMax/2 - x)

    # comment or uncomment depending on side of sidewalk

    # Hughes sidewalk is larger, these values are farther tested as well
    #

    # HughesSidewalk
    # xConst = .075
    # noAdjust=15
    # turnboundary=50
    # prevCount=8
    # speed=90

    # BentonSidwalk
    xConst = .1
    noAdjust = 10
    turnboundary = 30
    prevCount = 8
    speed = 70

    yBoundary = 75

    # Sets the xturn gain constant
    xTurn = math.floor(xConst*xDif)

    # print("Turning: " + xTurn)
    motorControl.direction = 0
    motorControl.speed = speed

    # if bad Y intercrpt ignore. Above/below middle y threshold
    if (y < yMax/2-yBoundary or y > yMax/2+yBoundary):
        print("Incorrect Y intercept Values")
        return
    elif (np.abs(x - xMax/2) < noAdjust):
        print("No adjustment")
        prev += 1
        if (prev == prevCount):
            motorControl.steer = 128
    elif (xMax/2 - x > 0):
        prev = 0
        if (x < ((xMax/2) - 40)):
            # far right fail safe
            # if xpixel is > 40 pixels left of center turn more
            print("Adjust BIG left: " + str(xTurn))
        else:
            print("Adjust SMALL left")
        motorControl.steer -= xTurn
    elif (xMax/2 - x < 0):
        prev = 0
        # if xpixel is > 40 pixels left of center turn more
        print("Adjust BIG Right: " + str(xTurn))
        motorControl.steer += xTurn

    if (motorControl.steer < 128-turnboundary):
        motorControl.steer = 128-turnboundary
    elif (motorControl.steer > 128+turnboundary):
        motorControl.steer = 128+turnboundary
    if (prev < prevCount+1):
        # publishs the motor speed and steering

        ''' 
        This is where the lidar implementation would fit in.  It would be very easy to subscribe to the lidar 
        and implement the lidar speed here

        Changing the motorControl.speed =lidarspeed

        '''
        motorControl.control_pub.publish(
            f"1, {motorControl.steer}, {motorControl.direction}, {motorControl.speed}\n")


def outputFrame(image, ransacLeft, ransacRight):
    copy3 = image.copy()
    theme = 255 * np.ones_like(image)
    # Calculate interception
    a1 = ransacLeft.estimator_.coef_
    b1 = ransacLeft.estimator_.intercept_

    a2 = ransacRight.estimator_.coef_
    b2 = ransacRight.estimator_.intercept_

    # a1 * Y1 + b1 = X1
    # a2 * Y1 + b2 = X1

    Y_intercept = (b2-b1) / (a1 - a2)
    X_intercept = a1 * Y_intercept + b1
    # TODO: X and Y acceptable intercept ranges
    for i in range(copy3.shape[0]):
        if i < int(Y_intercept):
            continue
        leftDot = int(ransacLeft.predict(np.array([[i]])))
        rightDot = int(ransacRight.predict(np.array([[i]])))
        if leftDot < copy3.shape[1] and leftDot >= 0:
            copy3[i, leftDot] = [255, 0, 0]
            theme[i, leftDot] = [0, 0, 0]
        if rightDot < copy3.shape[1] and rightDot >= 0:
            copy3[i, rightDot] = [255, 0, 0]
            theme[i, rightDot] = [0, 0, 0]
        if np.abs(rightDot - leftDot) < 1:
            print(f"Intercept at [{leftDot}/{rightDot}, {i}]")

    return [X_intercept, Y_intercept], copy3, theme


# Runs the ransac algorithm to get rid ouf outliers and form our linear model.
def fitRANSAC(Y_coor, lefts, rights):
    # Y data
    Y_data = np.array(Y_coor).reshape(-1, 1)

    # Left line
    X_left = np.array(lefts).reshape(-1, 1)

    # Right line
    X_right = np.array(rights).reshape(-1, 1)

    # Robustly fit linear model with RANSAC algorithm
    ransacLeft = linear_model.RANSACRegressor()

    ransacLeft.fit(Y_data, X_left)
    ransacRight = linear_model.RANSACRegressor()
    ransacRight.fit(Y_data, X_right)

    return ransacLeft, ransacRight


# No longer being used however using this in corporation of color dection might be a great way to increase stability
def preprocessImage(image, low_threshold=40, high_threshold=250):
    kernel = np.ones((3, 3), np.float32)/9

    dst = cv2.filter2D(image, -1, kernel)

    img_dilation = cv2.dilate(dst, kernel, iterations=3)
    img_erosion2 = cv2.erode(img_dilation, kernel, iterations=3)

#     low_threshold = 100
#     high_threshold = 250

    edges = cv2.Canny(img_erosion2, low_threshold, high_threshold)

    # Sobel Edge Detection on the X axis
    sobelx = cv2.Sobel(src=edges, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5)
    # Sobel Edge Detection on the Y axis
    sobely = cv2.Sobel(src=edges, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=5)
    sobelxy = cv2.bitwise_and(sobelx, sobely)
    return sobelxy


# Finds points on the edge of the grass, if a point is found it is added to the lefts and rights array to be used
# with the ranasac algorithm
def detectDataPoint(img):
    Y_coor = []
    lefts = []
    rights = []
    y = img.shape[0]-1
    height = img.shape[0]
    width = img.shape[1]
    width2 = int(width/2)

    while y >= height/2:
        leftF = True  # Left and right found
        rightF = True
        horPixels = img[y, :]
        rightIndex = -1
        leftIndex = -1
        horPixels[horPixels != 0] = 1
        for i in range(width2-10):
            # looks for consecutive pixels(AKA the sidewalk)
            if (leftIndex == -1 and sum(horPixels[width2-i-30:width2-i]) > 25):
                # print("Left")
                leftIndex = i
            if (rightIndex == -1 and sum(horPixels[width2+i:width2+30+i]) > 25):
                # print("Right")
                rightIndex = i

            if (not (rightF) and not (leftF)):
                break

        # Checks that the sidewalk is on bothsides
        if (not (rightIndex == -1) and not (leftIndex == -1)):
            if (leftIndex+rightIndex > 100):
                lefts.append(width2-leftIndex)
                rights.append(width2+rightIndex)
                Y_coor.append(y)
        y -= 1

    return Y_coor, lefts, rights


# uses HSV values to find the concrete, grass and dirt masks to form a solid image
# Adding in TRUE in the function call allows you to view the grayscale image
def grassDetection(img, grayScale=False):

    dst = cv2.GaussianBlur(img, (5, 5), cv2.BORDER_DEFAULT)

    hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)

    # mask of green (36,25,25) ~ (86, 255,255)
    # mask = cv2.inRange(hsv, (36, 25, 25), (86, 255,255))
    grassmask = cv2.inRange(hsv, (35, 20, 20), (77, 255, 255))  # grass mask
    # grassmask = cv2.inRange(hsv, (25, 50, 100), (77, 255,255))

    deadGrassMask = cv2.inRange(
        hsv, (20, 43, 46), (34, 255, 255))  # dead grass mask

    concreteMask = cv2.inRange(hsv, (0, 0, 0), (255, 60, 255))  # concrete mask

    dirtmask = cv2.inRange(hsv, (11, 67, 75), (28, 110, 100))
    mask = cv2.bitwise_or(grassmask, deadGrassMask)
    # mask=cv2.bitwise_or(mask,dirtmask)
    mask = cv2.bitwise_or(mask, dirtmask)
    combinedMask = cv2.bitwise_and(mask, concreteMask)

    mask = mask-combinedMask  # subtracks the concrete mask for better performance

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    # slice the green0
    imask = mask > 0
    green = np.zeros_like(img, np.uint8)
    green[imask] = img[imask]
    gray = cv2.cvtColor(green, cv2.COLOR_BGR2GRAY)
    if (grayScale):
        cv2.imshow("Blur", gray)
        cv2.waitKey(0)
    return gray


def FinalizeImage(image):

    return 'deez'
