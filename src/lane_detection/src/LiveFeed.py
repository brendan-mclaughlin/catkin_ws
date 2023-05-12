import rospy  # Python library for ROS
from sensor_msgs.msg import Image  # Image is the message type
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge  # Package to convert between ROS and OpenCV Images
import cv2  # OpenCV library
import numpy as np
import random
from remoteControl import MotorControl
from time import sleep
from LaneDetection import *
import warnings
warnings.simplefilter("ignore", DeprecationWarning)


# global frame count
timeMeasurement = 0

# adds ability to publish commands to the robot
motorControl = MotorControl()


def callback(data):

    # Used to convert between ROS and OpenCV images

    global timeMeasurement

    global motorControl
    if timeMeasurement == 5:  # Every 5 frames but this can be changed
        br = CvBridge()

        print("Recieved video frame")

        # Gets the image from the data paramater
        np_arr = np.fromstring(data.data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        timeMeasurement = 0

        # runs grass dection in the LaneDetection.py
        temp = grassDetection(img)

        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Detect data points
        Y_coor, lefts, rights = detectDataPoint(temp)

        # if we find enough data points then run the algorithm, if less than 3 then dont not enough points
        if (len(lefts) > 3):

            ransacLeft, ransacRight = fitRANSAC(Y_coor, lefts, rights)

            # Output Frame
            intercept, outFrame, theme = outputFrame(
                rgb_image, ransacLeft, ransacRight)

            # Uncomment these lines to see the output frame

            # plotFrame(intercept, outFrame, theme,temp)
            # cv2.destroyAllWindows()

            # Answer

            shape = [img.shape[0], img.shape[1]]

            # gets the motor responce from the frame
            response(intercept, shape, motorControl)
            rgb_image = None
            # plt.imshow(outFrame)
            # plt.figure(0).clear()
        elif (False):
            print("Bad Values ")

    else:
        timeMeasurement += 1


# initializing video subscriber node
rospy.init_node('video_sub_py', anonymous=True)

# Node is subscribing to the video_frames topic

# calls the callback function every frame
rospy.Subscriber('/camera/image/compressed',
                 CompressedImage, callback, queue_size=1)

# spin() simply keeps python from exiting until this node is stopped
rospy.spin()

# Close down the video stream when done
cv2.destroyAllWindows()
