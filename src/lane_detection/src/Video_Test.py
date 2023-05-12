from LaneDetection import *
import rospy


rospy.init_node('lane_detection', anonymous=True)


# Reads the video form this path
path = "/home/selfdrivingcar/Videos/"

cap = cv2.VideoCapture(path+"capture14.mp4")
# Preprocess Image
motorControl = MotorControl()

i = 0
while (cap.isOpened()):
    ret, img = cap.read()
    if ret == False:
        print("ret=False")
        break
    i += 1

    if (not (i % 48 == 0)):  # change this value to change how many frame you want to see
        continue

    # img=getResizedImage(img)

    # print(img.shape[0])
    # print(img.shape[1])

       # runs grass dection in the LaneDetection.py
    temp = grassDetection(img, True)
    # videoStitch.append(temp)
    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Detect data points
    Y_coor, lefts, rights = detectDataPoint(temp)

    # if we find enough data points then run the algorithm, if less than 3 then dont not enough points
    if (len(lefts) > 3):

        ransacLeft, ransacRight = fitRANSAC(Y_coor, lefts, rights)

        # Output Frame
        intercept, outFrame, theme = outputFrame(
            rgb_image, ransacLeft, ransacRight)

        # Plot
        # print(len(lefts))

        plotFrame(intercept, outFrame, theme, temp)
        cv2.destroyAllWindows()

        # Answer

        shape = [img.shape[0], img.shape[1]]
        # gets the motor responce from the frame
        response(intercept, shape, motorControl)
        rgb_image = None
        # plt.imshow(outFrame)
        # plt.figure(0).clear()
    elif (False):
        print("Bad Values ")
motorControl.control_pub.publish(f"1, 128, 0, 0\n")
