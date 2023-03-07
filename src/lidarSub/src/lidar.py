import rospy
from sensor_msgs.msg import LaserScan
import numpy as np

class Lidar:
    def __init__(self):
        self.lidar_ready = False
        self.lidar_sub = rospy.Subscriber("/scan",LaserScan,self.lidar_callback,queue_size = None)
    def lidar_callback(self,msg):
        self.lidar_ready = True
        self.distance = msg.ranges
    def get_lidar(self, angle):
        if not self.lidar_ready:
            return 1.1
        return self.distance[angle]
    def get_minimumDist(self):
        if not self.lidar_ready:
            return 1.1
        temp = np.append(self.distance[0:15],self.distance[344:359])
        for x in temp:
            if(x==0.0):
                x=1000
        return np.amin(temp)