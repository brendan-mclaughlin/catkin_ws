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


path = "/home/selfdrivingcar/Pictures/DIRT.png"

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
        

print("H")
print(max(H))
print(min(H))
print('New HighH ')
#print(np.average(H))
newhighH = 2*np.std(H) + np.average(H)
print(newhighH)
print('New LowH ')
newlowH =  np.average(H) - 2*np.std(H) 
print(newlowH)

print("S")
print(max(S))
print(min(S))
print('New highS ')
#print(np.average(H))
newhighS = 2*np.std(S) + np.average(S)
print(newhighS)
print('New LowS ')
newlowS =  np.average(S) - 2*np.std(S) 
print(newlowS)

print("V")
print(max(V))
print(min(V))
print('New HighV ')
#print(np.average(H))
newhighV = 2*np.std(V) + np.average(V)
print(newhighV)
print('New LowV ')
newlowV =  np.average(V) - 2*np.std(V) 
print(newlowV)






cv2.waitKey(0)
cv2.destroyAllWindows() 

