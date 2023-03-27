#!/usr/bin/env python3
# Description:
# - Subscribes to real-time streaming video from your built-in webcam.
#
# Author:
# - Addison Sears-Collins
# - https://automaticaddison.com
 
# Import the necessary libraries
import rospy # Python library for ROS
from sensor_msgs.msg import Image # Image is the message type
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge # Package to convert between ROS and OpenCV Images
import cv2 # OpenCV library
import numpy as np
import random
from remoteControl import MotorControl
from time import sleep

current=0
timeMeasurement=0
greenAvg=0
redAvg=0
def callback(data):
 
      # Used to convert between ROS and OpenCV images
      br = CvBridge()

      # Output debugging information to the terminal
      rospy.loginfo("receiving video frame")



      #decimg = cv2.imdecode(data,1)   
      # Convert ROS Image message to OpenCV image

      np_arr=np.fromstring(data.data,np.uint8)
      img=cv2.imdecode(np_arr,cv2.IMREAD_COLOR)

      #current_frame = br.imgmsg_to_cv2(data)

      # Display image

      #img=current_frame.copy()
      # Change first 100 rows to random pixels
      #img.setflags(write=1)

      # Copy part of image

      #tag = img[100:200, 50:150]
      #img[0:100, 75:175] = tag
      hsv =cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
      #lower_green=np.array([30,101,101])
      #upper_green=np.array([52,213,255])

      lower_green=np.array([37,95,95])
      upper_green=np.array([80 ,255,255])

      lower_red=np.array([0,95,95])
      upper_red=np.array([12,256,256]) 

      Tlower_red=np.array([168,95,95])
      Tupper_red=np.array([180,256,256]) 
      greenmask=cv2.inRange(hsv,lower_green,upper_green)

      greencount =np.sum(greenmask)
      print("Green: ",greencount)


      redmask=cv2.inRange(hsv,lower_red,upper_red)+cv2.inRange(hsv,Tlower_red,Tupper_red);
      redcount=np.sum(redmask); 

      print("Red: ",redcount)
      cv2.imshow("green_mask",greenmask)
      cv2.imshow("camera",img)
      cv2.imshow("red_mask",redmask)
      #cv2.imshow("camera", image_np)

      #rospy.init_node("ControlStation1") 
      motorControl=MotorControl()
      global current
      print(current)
      num=current
      global greenAvg
      global redAvg
      global timeMeasurement
      print(timeMeasurement)
  
  
      if timeMeasurement==8:
  
            if(greenAvg>80000 and redAvg>80000):
                  motorControl.direction=0
                  motorControl.speed=0
            elif (greenAvg>800000 ):
                  motorControl.direction=0
                  motorControl.speed=100

            elif (redAvg>800000 ):
                  motorControl.direction=1
                  motorControl.speed=100

            if (greenAvg<80000 and redAvg<80000):
                  motorControl.speed=0
                  motorControl.direction=0

            
            motorControl.control_pub.publish(f"1, {motorControl.steer}, {motorControl.direction}, {motorControl.speed}\n")        
            timeMeasurement=0
            greenAvg=0
            redAvg=0
      else:
            greenAvg+=greencount
            redAvg+= redcount
            timeMeasurement=timeMeasurement+1   
      cv2.waitKey(1)
      
def receive_message():
 
  # Tells rospy the name of the node.
  # Anonymous = True makes sure the node has a unique name. Random
  # numbers are added to the end of the name. 
  rospy.init_node('video_sub_py', anonymous=True)
  
  # Node is subscribing to the video_frames topic
  #rospy.Subscriber('video_frames', Image, callback)

  rospy.Subscriber('/camera/image/compressed', CompressedImage, callback, queue_size=1)
  
  # spin() simply keeps python from exiting until this node is stopped
  rospy.spin()
 
  # Close down the video stream when done
  cv2.destroyAllWindows()

def setCurrent(num):
  global current
  current=num
  	
if __name__ == '__main__':
  setCurrent(0)
  receive_message()
