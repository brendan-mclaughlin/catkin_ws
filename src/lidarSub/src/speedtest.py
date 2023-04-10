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
    
    while True:
        motorControl.speed=20
        time.sleep(1)
        motorControl.control_pub.publish(f"1, {motorControl.steer}, {motorControl.direction}, {motorControl.speed}\n")
                
    
    # spin() simply keeps python from exiting until this node is stopped
    #rospy.spin()
 
if __name__ == '__main__':
    main()