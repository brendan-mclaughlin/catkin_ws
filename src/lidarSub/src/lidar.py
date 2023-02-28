import rospy
from sensor_msgs.msg import LaserScan

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