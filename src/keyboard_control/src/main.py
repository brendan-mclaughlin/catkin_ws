#! /usr/bin/python3

from curtsies import Input
import rospy
from std_msgs.msg import String
import sys

class MotorControl:
    def __init__(self):
        #self.speed ranges from 0 to 510. If it is 255, car's not moving, lower than 255, car's moving backward, larger than 255, car's moving forward
        self.steer, self.speed = 128, 255
        self.control_pub = rospy.Publisher("control_cmd", String, queue_size = 0)
    def accelerate(self,change_val):
        if self.speed + change_val > 510:
            self.speed = 510
            return
        if self.speed + change_val < 0:
            self.speed = 0
            return
        self.speed+=change_val
    def steering(self,change_val):

        if self.steer + change_val > 255:
            self.steer = 255
            return
        if self.steer + change_val < 0:
            self.steer = 0
            return

        self.steer+=change_val
    def main(self): 
        with Input(keynames='curses') as input_generator:
            for k in input_generator:
                if k == 'w':
                    self.accelerate(1)
                elif k == 'x':
                    self.accelerate(-1)
                elif k == 's' or k == 'd':
                    self.speed = 255
                elif k == 'e':
                    self.accelerate(10)
                elif k == 'c':
                    self.accelerate(-10)
                elif k == 'j':
                    self.steering(-1)
                elif k == 'l':
                    self.steering(1)
                elif k == 'u':
                    self.steering(-10)
                elif k == 'o':
                    self.steering(10)
                elif k == 'k' or k == 'i':
                    self.steer = 128
                elif k == ' ':
                    self.steer = 128
                    self.speed = 255
                    self.publish()
                    break
                self.publish()
    def publish(self):
        direction = 0 #0 is forward, 1 is backward
        speed = self.speed - 255
        if speed < 0:
            direction = 1
            speed = -speed
        self.control_pub.publish(f"1, {self.steer}, {direction}, {speed}\n")
rospy.init_node("ControlStation")
motorControl = MotorControl()
print("Press space bar to quit")
motorControl.main()

