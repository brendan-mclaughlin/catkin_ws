motorControl=MotorControl()
    
    time.sleep(1) #waiting for one rotation to complete
    while True:

        maxSpeed = 100
        #a=lid.getLidar(1)
        time.sleep(0.5)
        
        a=lid.get_minimumDist()
        
        print(a)
        
        if(a<0.2):
            motorControl.speed=0
        elif((a<.45)&(a>=0.2)&(motorControl.speed<=maxSpeed)):
            motorControl.speed=motorControl.speed-1
            #print("SLOW DOWN")
            #motorControl.direction=0
            #motorControl.speed=0
        elif((a>0.55)&(motorControl.speed<maxSpeed)):
            if(motorControl.speed<20):#this statement is to set it to the minimum movement speed
                time.sleep(3)
                motorControl.speed=50
                motorControl.direction=1
                motorControl.steer=128
                print("Executed")
            motorControl.speed=motorControl.speed+1

        motorControl.control_pub.publish(f"1, {motorControl.steer}, {motorControl.direction}, {motorControl.speed}\n")
            #print("SPEED UP")
            #motorControl.direction=0
            #motorControl.speed=50