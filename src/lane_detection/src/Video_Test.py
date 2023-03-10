import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import cv2
import os
from scipy import signal
from scipy.signal import find_peaks
from sklearn import linear_model
from os import listdir
from clear_cache import clear as clear_cache
import matplotlib #inline




## Read
path = "/home/selfdrivingcar/Videos/"


def getResizedImage(img, scale_percent=20):
    
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
    #rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
    
    return resized_image


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



def preprocessImage(image, low_threshold = 40, high_threshold = 250):
    kernel = np.ones((3,3),np.float32)/9

    dst = cv2.filter2D(image,-1,kernel)
    
    img_dilation = cv2.dilate(dst, kernel, iterations=3)
    img_erosion2 = cv2.erode(img_dilation, kernel, iterations=3)
    
#     low_threshold = 100
#     high_threshold = 250 

    edges = cv2.Canny(img_erosion2, low_threshold, high_threshold)
  
    sobelx = cv2.Sobel(src=edges, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5) # Sobel Edge Detection on the X axis
    sobely = cv2.Sobel(src=edges, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=5) # Sobel Edge Detection on the Y axis
    sobelxy= cv2.bitwise_and(sobelx, sobely)
    return sobelxy




def detectDataPoint(img):
    Y_coor = []
    lefts = []
    rights = []
    y=img.shape[0]-1
    height=img.shape[0]
    width=img.shape[1]
    width2=int(width/2)

    while y >= height/2:
        leftF=True#Left and right found
        rightF=True
        horPixels=img[y,:]
        rightIndex=-1
        leftIndex=-1
        horPixels[horPixels != 0] = 1
        for i in range(width2-10):
            if(leftIndex==-1 and sum(horPixels[width2-i-30:width2-i])>25):
                #print("Left")
                leftIndex=i
            if(rightIndex==-1 and sum(horPixels[width2+i:width2+30+i])>25):
                #print("Right")
                rightIndex=i
                
            if(not(rightF) and not(leftF)):
                break

        if(not(rightIndex==-1) and not(leftIndex==-1)):
            if(leftIndex+rightIndex>100):
                lefts.append(width2-leftIndex)
                rights.append(width2+rightIndex)
                Y_coor.append(y)
        y-=1

    return Y_coor,lefts,rights




def grassDetection(img):

    dst = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)

    hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)

    ## mask of green (36,25,25) ~ (86, 255,255)
    # mask = cv2.inRange(hsv, (36, 25, 25), (86, 255,255))
    grassmask = cv2.inRange(hsv, (35, 20, 20), (77, 255,255))
    deadGrassMask = cv2.inRange(hsv, (20, 43, 46), (34, 255,255))
    dirtmask=cv2.inRange(hsv,(19,24,33),(50,50,255))
    mask=cv2.bitwise_or(grassmask,deadGrassMask)
    mask=cv2.bitwise_or(mask,dirtmask)

    mask=cv2.erode(mask,None,iterations=2)
    mask=cv2.dilate(mask,None,iterations=2)
    ## slice the green0
    imask = mask>0
    green = np.zeros_like(img, np.uint8)
    green[imask] = img[imask]
    gray = cv2.cvtColor(green, cv2.COLOR_BGR2GRAY)

    #cv2.imshow("Blur", gray)
    #cv2.waitKey(0)
    return gray






counter = 1
for counter in range(2): #fileName in listdir(path)[0:1]:
    #print(f"\n[Picture {counter}]")
    counter += 1
    ### Get Image
    #img = cv2.imread(r'/home/ubuntu/catkin_ws/src/lane_detection/src/images' + fileName)

    #print(fileName)

    #img=cv2.imread(path+fileName)


    videoStitch=[]



    cap=cv2.VideoCapture(path+"capture0.mp4")
    ### Preprocess Image
   
    i =0
    while(cap.isOpened()):
        ret, img = cap.read()
        if ret == False:
            print("ret=False")
            break
        #cv2.imwrite('kang'+str(i)+'.jpg',frame)
        i+=1
        if(i==30):
            break      
   
        #img=getResizedImage(img)

        #print(img.shape[0])
        #print(img.shape[1])
        temp = grassDetection(img)
        videoStitch.append(temp)
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        ### Detect data points
        Y_coor, lefts, rights = detectDataPoint(temp)
        
        
        if(len(lefts) < 0) : 

            ransacLeft, ransacRight =  fitRANSAC(Y_coor, lefts, rights)

            ### Output Frame
            intercept, outFrame, theme =  outputFrame(rgb_image, ransacLeft, ransacRight)

            ### Plot
            #print(len(lefts))
            plotFrame(intercept, outFrame, theme)
            xx = 10
            
                ### Answer 
            #response(intercept)
            rgb_image = None
            #plt.imshow(outFrame)  
            #plt.figure(0).clear()  
        elif(False): 
            print("Bad Values ")


    #fourcc = cv2.VideoWriter_fourcc(*'XVID')

    #video=cv2.VideoWriter("GrayScale.avi",0,30,(480,640))
    video = cv2.VideoWriter("videoTest.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30,(640,480))

    for i in videoStitch:
        video.write(i)

    video.release()

    cap.release()
    cv2.destroyAllWindows()  
        

    ### Fit Ransac
