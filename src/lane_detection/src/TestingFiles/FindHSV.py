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
import time
import math


path = "/home/selfdrivingcar/Pictures/NewGrassImages/dirt22.png"

img=cv2.imread(path)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.imshow("Image",hsv)
print(hsv.shape[0])
print(hsv.shape[1])



H=[]
S=[]
V=[]

for i in range(hsv.shape[0]):
  for j in range(hsv.shape[1]):
        H.append(hsv[i][j][0])
        S.append(hsv[i][j][1])
        V.append(hsv[i][j][2])
        
stdVar = 5
print("H")
print(max(H))
print(min(H))
print('New HighH ')
#print(np.average(H))
newhighH = stdVar*np.std(H) + np.average(H)
print(newhighH)
print('New LowH ')
newlowH =  np.average(H) - stdVar*np.std(H) 
print(newlowH)

print("S")
print(max(S))
print(min(S))
print('New highS ')
#print(np.average(H))
newhighS = stdVar*np.std(S) + np.average(S)
print(newhighS)
print('New LowS ')
newlowS =  np.average(S) - stdVar*np.std(S) 
print(newlowS)

print("V")
print(max(V))
print(min(V))
print('New HighV ')
#print(np.average(H))
newhighV = stdVar*np.std(V) + np.average(V)
print(newhighV)
print('New LowV ')
newlowV =  np.average(V) - stdVar*np.std(V) 
print(newlowV)


print("cv2.inRange(hsv, ("+str(math.ceil(newlowH))+", "+str(math.ceil(newlowS))+", "+str(math.ceil(newlowV))+"), ("+str(math.ceil(newhighH))+", "+str(math.floor(newhighS))+","+str(math.floor(newhighV))+"))")



#cv2.waitKey(0)
cv2.destroyAllWindows() 

# Sunny New Grasscv2.inRange(hsv, (6, 52, 67), (34, 125,108))
# (32, 91, 35), (41, 206,155))
# (30, 93, 87), (34, 172,139))
# (33, 97, 82), (38, 145,108))
# (34, 91, 89), (37, 146,138))
# (33, 97, 88), (39, 143,119))

#Concrete: (18, 41, 202), (22, 47,216))

#Dirt: 
 #cv2.inRange(hsv, (6, 61, 69), (25, 119,106))
 # cv2.inRange(hsv, (1, 47, 59), (29, 133,116))
 # cv2.inRange(hsv, (-8, 18, 39), (39, 163,135))


#  cv2.inRange(hsv, (14, 74, 79), (25, 102,95))
# cv2.inRange(hsv, (11, 67, 75), (28, 110,100))
# cv2.inRange(hsv, (6, 52, 67), (34, 125,108))