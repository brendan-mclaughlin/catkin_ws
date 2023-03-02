

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import cv2
from scipy import signal
from scipy.signal import find_peaks
from sklearn import linear_model
from os import listdir
from clear_cache import clear as clear_cache
import matplotlib #inline


path = "/home/selfdrivingcar/catkin_ws/src/lane_detection/src/images/"

def getResizedImage(fileName, scale_percent=50):
    img = cv2.imread(path + fileName)
    #img = cv2.imread(r'/home/ubuntu/catkin_ws/src/lane_detection/src/images' + fileName)

    #Resize
    #assert not isinstance(img,type(None)), 'image not found'

    print('Original Dimensions : ',img.shape)
    #scale_percent = 20 # percent of original size
    # img.set(3,640)
    # img.set(4,480)
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    resized_image = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    # Change COLOR mode
    rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
    
    return rgb_image


def preprocessImage(image, low_threshold = 40, high_threshold = 250):
    kernel = np.ones((3,3),np.float32)/9

    dst = cv2.filter2D(image,-1,kernel)
    
    img_dilation = cv2.dilate(dst, kernel, iterations=3)
    img_erosion2 = cv2.erode(img_dilation, kernel, iterations=3)
    
#     low_threshold = 100
#     high_threshold = 250 

    
   
    edges = cv2.Canny(img_erosion2, low_threshold, high_threshold)
    fig = plt.figure(figsize=(20, 10))
    fig.add_subplot(1, 5, 1)
    plt.imshow(edges, cmap="gray")
    
    
    sobelx = cv2.Sobel(src=edges, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5) # Sobel Edge Detection on the X axis
    sobely = cv2.Sobel(src=edges, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=5) # Sobel Edge Detection on the Y axis
    sobelxy = cv2.Sobel(src=edges, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5) # Sobel Edge Detection on the Y axis
    temp = cv2.bitwise_and(sobelx, sobely)
    temp[:130,:]=-2000
    print(img_erosion2)
    for i in range(110):
        temp[239-i, :20+i]=-2000
        temp[239-i, 290-i:]=-2000
        temp[239-i, 80+i:220-i]=-2000
   

    fig.add_subplot(1, 5, 2)
    plt.imshow(sobelx)
    fig.add_subplot(1, 5, 3)
    plt.imshow(sobely)
    fig.add_subplot(1, 5, 4)
    plt.imshow(temp)
    fig.add_subplot(1, 5, 5)
    plt.imshow(sobelxy)
    plt.show()
    
   

    return temp

def detectDataPoint(img):
    Y_coor = []
    lefts = []
    rights = []

    y = img.shape[0] - 1 
    print(img.shape)
    while y >= 120:
        if (len(lefts) >= 50):  
            break
        horizontal_pixels = img[y,:]
        if (horizontal_pixels.min() >=0):
            y -= 1
            continue
        else:
            leftPos = np.argmin(horizontal_pixels) #Returns the indices of the minimum values along an axis.
            if (horizontal_pixels[leftPos:].max() <= 0):
                y -= 1
                continue
            else:
                rightPos = leftPos + np.argmax(horizontal_pixels[leftPos:])

                tempBuffer = y/240 * 170
                if rightPos - leftPos > tempBuffer:
                    print("HOORAY")
                    # Add pairs
                    Y_coor.append(y)
                    lefts.append(leftPos)
                    rights.append(rightPos)
        ### update 
        #y -= 10
        y -= 1
    
    return Y_coor, lefts, rights


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

    for i in range(copy3.shape[0]):
        if i < int(Y_intercept):
            continue
        leftDot  = int(ransacLeft.predict(np.array([[i]])))
        rightDot = int(ransacRight.predict(np.array([[i]])))
        if  leftDot <  copy3.shape[1] and leftDot >= 0:
            copy3[i, leftDot] = [255, 0, 0]
            theme[i, leftDot] = [0, 0, 0]
        if  rightDot <  copy3.shape[1] and rightDot >= 0:
            copy3[i, rightDot] = [255, 0, 0]
            theme[i, rightDot] = [0, 0, 0]
        if np.abs(rightDot - leftDot) < 1:
            print(f"Intercept at [{leftDot}/{rightDot}, {i}]")
    
    return [X_intercept, Y_intercept], copy3, theme

def plotFrame(intercept, copy3, theme):
    # create figure
    fig = plt.figure(figsize=(10, 7))

    # setting values to rows and column variables
    rows = 1
    columns = 2

    fig.add_subplot(rows, columns, 1)

    # showing image
    plt.imshow(copy3)
    # plt.axis('off')

    # Adds a subplot at the 2nd position
    fig.add_subplot(rows, columns, 2)
    
    # for i in range(len(lefts)):
    #     plt.scatter(lefts[i], Y_coor[i], color='blue')
    # plt.plot([X_intercept, 100 + theme.shape[1]/2], [Y_intercept, theme.shape[1]], color="red", linewidth=3)
    plt.scatter(intercept[0], intercept[1], color='blue')
    plt.plot([theme.shape[1]/2,  theme.shape[1]/2], [0, theme.shape[1]], color="red", linewidth=3)
    plt.imshow(theme)
    plt.show()
    
def response(intercept):
    if (np.abs(intercept[0] - 400) < 50):
        print("No adjustment")
    elif (intercept[0] - 400 < 0):
        print("Adjust to the left")
    else: 
        print("Adjust to the right")




counter = 1
for fileName in listdir(path)[0:1]:
    print(f"\n[Picture {counter}]")
    counter += 1
    ### Get Image
    #img = cv2.imread(r'/home/ubuntu/catkin_ws/src/lane_detection/src/images' + fileName)

    print(fileName)
    rgb_image = getResizedImage(fileName)
    ### Preprocess Image
    temp = preprocessImage(rgb_image)

    ### Detect data points
    Y_coor, lefts, rights = detectDataPoint(temp)
    if(len(lefts) > 1) : 

        ransacLeft, ransacRight =  fitRANSAC(Y_coor, lefts, rights)

        ### Output Frame
        intercept, outFrame, theme =  outputFrame(rgb_image, ransacLeft, ransacRight)

        ### Plot
        print(len(lefts))
        plotFrame(intercept, outFrame, theme)
        xx = 10
            ### Answer
        response(intercept)
        rgb_image = None
        plt.imshow(outFrame)  
        plt.figure(0).clear()    
    
    else : 
        print("Bad Values ")
    ### Fit Ransac
    




