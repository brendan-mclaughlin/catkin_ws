#! /usr/bin/python3

import rospy
import time
from lidar import Lidar
from std_msgs.msg import String
from remoteControl import MotorControl

def main():

     # In ROS, nodes are uniquely named. If two nodes with the same
     # name are launched, the previous one is kicked off. The
     # anonymous=True flag means that rospy will choose a unique
     # name for our 'listener' node so that multiple listeners can
     # run simultaneously.
    #rospy.init_node('lidar_subscriber', anonymous=True)
 
    #creates lidar object, which subscribes to the lidar topic "/scan"
    lid = Lidar()
    motorControl=MotorControl()
    rospy.init_node('listener', anonymous=True)
    maxSpeed=150
    motorControl.speed=50
    while True:
        a=lid.get_minimumDist()
        time.sleep(0.1)
        
        print(a)
        print(motorControl.speed)
        #motorControl.speed=50
        # if((motorControl.speed+velocity)<0):
        #     motorControl.speed=0
        # elif(motorControl.speed+velocity>50):
        #     motorControl.speed=50
        # else:
        #     motorControl.speed=motorControl.speed+velocity
        
        if(a<1):
            motorControl.speed=0
        elif((a<2.3)&(a>=1)):
                if(motorControl.speed>25):
                    motorControl.speed=motorControl.speed-5
            #print("SLOW DOWN")
            #motorControl.direction=0
            #motorControl.speed=0
        elif((a>2.57)):
                if(motorControl.speed<maxSpeed):
                     motorControl.speed=motorControl.speed+5
        
        motorControl.control_pub.publish(f"1, {motorControl.steer}, {motorControl.direction}, {motorControl.speed}\n")

            
    
    # spin() simply keeps python from exiting until this node is stopped
    #rospy.spin()
 
if __name__ == '__main__':
    main()