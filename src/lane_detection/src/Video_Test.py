from LaneDetection import *
import rospy
from LiveFeed import *



rospy.init_node('lane_detection', anonymous=True)


## Read
path = "/home/selfdrivingcar/Videos/"

cap=cv2.VideoCapture(path+"capture0.mp4")
### Preprocess Image
motorControl=MotorControl()

i =0
while(cap.isOpened()):
    ret, img = cap.read()
    if ret == False:
        print("ret=False")
        break
    i+=1
    
    if(not(i%48==0)):
        continue      
    
    #img=getResizedImage(img)

    #print(img.shape[0])
    #print(img.shape[1])



    temp = grassDetection(img)
    #videoStitch.append(temp)
    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    ### Detect data points
    Y_coor, lefts, rights = detectDataPoint(temp)
    
    
    if(len(lefts) > 3) : 

        ransacLeft, ransacRight =  fitRANSAC(Y_coor, lefts, rights)

        ### Output Frame
        intercept, outFrame, theme =  outputFrame(rgb_image, ransacLeft, ransacRight)

        ### Plot
        #print(len(lefts))
        
        
        
        plotFrame(intercept, outFrame, theme,temp)
        cv2.destroyAllWindows() 

            ### Answer 

        shape=[img.shape[0],img.shape[1]]

        response(intercept,shape, motorControl)
        rgb_image = None
        #plt.imshow(outFrame)  
        #plt.figure(0).clear()  
    elif(False): 
        print("Bad Values ")
motorControl.control_pub.publish(f"1, 128, 0, 0\n")        

    #fourcc = cv2.VideoWriter_fourcc(*'XVID')

    #video=cv2.VideoWriter("GrayScale.avi",0,30,(480,640))
    #video = cv2.VideoWriter("videoTest.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30,(640,480))

    #for i in videoStitch:
    #    video.write(i)

    #video.release()

    #cap.release()
    #cv2.destroyAllWindows()  
        

    ### Fit Ransac
