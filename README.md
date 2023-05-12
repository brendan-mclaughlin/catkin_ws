# ECE 448/449 Capstone 2023
Old capstone repository: https://github.com/BreadDisease/448-SELF-DRIVE/tree/main/vision

Important files:
catkin_ws/src/lane_detection/src/LaneDetection.py : Lane detection algorithm that sends motor commands to Pi after performing computer vision.

catkin_ws/src/lane_detection/src/LiveFeed.py : Program that pulls out compressed live feed from Pi camera stream and makes it usable for OpenCv work.

catkin_ws/src/lane_detection/src/Video_Test.py : Program that allows user to use lane detection algorithm on pre recorded video.
