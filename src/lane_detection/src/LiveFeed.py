import rospy # Python library for ROS
from sensor_msgs.msg import Image # Image is the message type
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge # Package to convert between ROS and OpenCV Images
import cv2 # OpenCV library
import numpy as np
import random
from remoteControl import MotorControl
from time import sleep
from LaneDetection import *
import warnings
warnings.simplefilter("ignore", DeprecationWarning)


timeMeasurement=0
motorControl=MotorControl()
def callback(data):
 
      # Used to convert between ROS and OpenCV images
    
    global timeMeasurement
    global motorControl
    if timeMeasurement==5:
        br = CvBridge()

      # Output debugging information to the terminal
        #rospy.loginfo("receiving video frame")
        print("Recieved video frame")

        #np_arr=np.frombuffer(data.data,np.uint8)

        np_arr=np.fromstring(data.data,np.uint8)
        img=cv2.imdecode(np_arr,cv2.IMREAD_COLOR)
        timeMeasurement=0
        temp = grassDetection(img)
        #videoStitch.append(temp)
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        ### Detect data points
        Y_coor, lefts, rights = detectDataPoint(temp)
        
        
        if(len(lefts) > 3) : 

          ransacLeft, ransacRight =  fitRANSAC(Y_coor, lefts, rights)

          ### Output Frame
          intercept, outFrame, theme =  outputFrame(rgb_image, ransacLeft, ransacRight)

          ### Plot
          #print(len(lefts))
          
          
          
          #plotFrame(intercept, outFrame, theme,temp)
          #cv2.destroyAllWindows() 


              ### Answer 

          shape=[img.shape[0],img.shape[1]]

          response(intercept,shape, motorControl)
          rgb_image = None
          #plt.imshow(outFrame)  
          #plt.figure(0).clear()  
        elif(False): 
            print("Bad Values ")
           
    else:
        timeMeasurement+=1

 


## Read

### Preprocess Image

rospy.init_node('video_sub_py', anonymous=True)
  
  # Node is subscribing to the video_frames topic
  #rospy.Subscriber('video_frames', Image, callback)

rospy.Subscriber('/camera/image/compressed', CompressedImage, callback, queue_size=1)
  
  # spin() simply keeps python from exiting until this node is stopped
rospy.spin()
 
  # Close down the video stream when done
cv2.destroyAllWindows()