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
    maxSpeed=100
    while True:
        time.sleep(0.5)
        a=lid.get_minimumDist()

        print(a)
        if(a<0.2):
            motorControl.speed=0
        elif((a<.45)&(a>=0.2)&(motorControl.speed<=maxSpeed)&(motorControl.speed>0)):
            motorControl.speed=motorControl.speed-1
            #print("SLOW DOWN")
            #motorControl.direction=0
            #motorControl.speed=0
        elif((a>0.55)&(motorControl.speed<maxSpeed)):
            if(motorControl.speed<20):#this statement is to set it to the minimum movement speed
                time.sleep(3)
                motorControl.speed=50
                motorControl.direction=0
                motorControl.steer=128
                print("Executed")
            motorControl.speed=motorControl.speed+1
        

        motorControl.control_pub.publish(f"1, {motorControl.steer}, {motorControl.direction}, {motorControl.speed}\n")
                
    
    # spin() simply keeps python from exiting until this node is stopped
    #rospy.spin()
 
if __name__ == '__main__':
    main()