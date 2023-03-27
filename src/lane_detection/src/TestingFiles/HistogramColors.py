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
counter=0
for fileName in listdir(path)[0:1]:
    print(f"\n[Picture {counter}]")
    counter += 1

    img=cv2.imread("image/img3.jpg")
    print(img.shape)
    cv2.imshow("img",img)

   
   
   
   
    croppedimg=img[330:,460:]
norm=cv2.normalize(croppedimg,None,0 ,1.0,cv2.NORM_MINMAX,dtype=cv2.CV_32F)