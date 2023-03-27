#! /usr/bin/python3

import rospy
import time
from lidar import Lidar
from std_msgs.msg import String
from remoteControl import MotorControl
 
def callback(data):
   rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)

def listener():

     # In ROS, nodes are uniquely named. If two nodes with the same
     # name are launched, the previous one is kicked off. The
     # anonymous=True flag means that rospy will choose a unique
     # name for our 'listener' node so that multiple listeners can
     # run simultaneously.
    rospy.init_node('lidar_subscriber', anonymous=True)
 
    #creates lidar object, which subscribes to the lidar topic "/scan"
    lid = Lidar()
    motorControl=MotorControl()
    time.sleep(1) #waiting for one rotation to complete
    while True:
        #a=lid.getLidar(1)
        time.sleep(0.5)
        
        a=lid.get_minimumDist()

        #print(a)
        #if(a<1.5):
            #print("SLOW DOWN")
            #motorControl.direction=0
            #motorControl.speed=0
        #else:
            #print("SPEED UP")
            #motorControl.direction=0
            #motorControl.speed=50
    
    # spin() simply keeps python from exiting until this node is stopped
    #rospy.spin()
 
if __name__ == '__main__':
    listener()