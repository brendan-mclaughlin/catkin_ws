#! /usr/bin/python3

from curtsies import Input
import rospy
from std_msgs.msg import String
import sys
#import webcam_sub

class MotorControl:
    def __init__(self):
       
        self.steer, self.speed, self.direction = 128, 0,0
        self.control_pub = rospy.Publisher("control_cmd", String, queue_size = 0)

