########### 
########### 
from djitellopy import tello
import time
import cv2
import numpy as np
from HandLandmarkModule import handLandmarkDetector, in_circle


################# activate control center view (default=True) ##################
controlCenter = True
################# set up Tello speed ##################
speed = 40

################# set up Flight Control mode from start (default=False)##################
fControl = False

################# set up Tello ##################
myTello = tello.Tello()
myTello.connect()
print(myTello.get_battery())
myTello.streamon()

################# set up cam and other settings ##################
width = 1200
height = 700
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

BLACK = (0,0,0)

ptime = 0
ctime = 0
counter = 0
counterLandTakeoff = 0

detector = handLandmarkDetector()


while True:
    _, img = cap.read()
     
    if controlCenter:
        # create new frame for joystick image (control center mode)
        img2 = np.zeros((height, width, 3), np.uint8)
        img2[:] = (255,255,255)
        img = detector.findHands(img, draw=False)
        fingerLs = detector.drawFingerPoint(img2)
    # if control center mode is set to false
    else:
        img2 = img
        BLACK = (0,255,255) # turns black into yellow for better visibility
        img2 = detector.findHands(img, draw=False)
        fingerLs = detector.drawFingerPoint(img2)
    
    # get tello stream
    frame = myTello.get_frame_read().frame
    frame = cv2.resize(frame,(360,240))
    # print(counter)

    # get fps
    ctime = time.time()
    fps = 1/(ctime - ptime)
    ptime = ctime

    # draw control activation circles
    cv2.putText(img2, str(int(fps)),(10,30), cv2.FONT_HERSHEY_SIMPLEX, 1,BLACK, 2)
    cv2.circle(img2, (int(width * 0.4), int(height*0.1)), 25, BLACK, 3)
    cv2.circle(img2, (int(width * 0.6), int(height*0.1)), 25, BLACK, 3)

    ########### check if control mode is activated ###########
    ########### if both index fingers in circles: activates control mode ###########
    try:
        if in_circle(int(width * 0.4), int(height*0.1), 25, fingerLs[0]) and in_circle(int(width * 0.6), int(height*0.1), 25, fingerLs[1]):
            counter +=1
            if counter == 30:
                fControl = not fControl
                print('Control activated', fControl)
        else:
            counter = 0
    except:
        pass
    
    if fControl:    
        cv2.putText(img2, 'CONTROL ACTIVATED', (450,30), cv2.FONT_HERSHEY_SIMPLEX, 1, BLACK, 3)

        # left joystick
        cv2.circle(img2, (int(width * 0.3), int(height*0.45)), 125, BLACK, 15)
        # righ joystick
        cv2.circle(img2, (int(width * 0.7), int(height*0.45)), 125, BLACK, 15)
        # land drone circle
        cv2.circle(img2, (int(width * 0.4), int(height*0.25)), 25, BLACK, 2)
        cv2.putText(img2, str('Land'),(int(width * 0.4)-30, int(height * 0.25)-40), cv2.FONT_HERSHEY_SIMPLEX, 1, BLACK, 2)
        # takeoff drone circle
        cv2.circle(img2, (int(width * 0.6), int(height*0.25)), 25, BLACK, 2)
        cv2.putText(img2, str('Takeoff'),(int(width * 0.6)-40, int(height * 0.25)-40), cv2.FONT_HERSHEY_SIMPLEX, 1, BLACK, 2)

        ##########################################################################################################################################################
        ######## send landing and takeoff commands ########
        ##########################################################################################################################################################
        try:
            # Drone Landing
            if in_circle(int(width * 0.4), int(height*0.25), 25, fingerLs[0]) or in_circle(int(width * 0.4), int(height*0.25), 25, fingerLs[1]):
                counterLandTakeoff +=1
                if counterLandTakeoff == 20: myTello.land() 
                    # print('Tello Landing!!!!' )
                    
            elif in_circle(int(width * 0.6), int(height*0.25), 25, fingerLs[0]) or in_circle(int(width * 0.6), int(height*0.25), 25, fingerLs[1]):
                counterLandTakeoff +=1
                if counterLandTakeoff == 20: myTello.takeoff()
                    # print('Tello Takeoff!!!!' )
            else:
                counterLandTakeoff = 0
        except:
            pass
        ##########################################################################################################################################################
        ######## send direction/velocity commands ########
        ##########################################################################################################################################################
        try:
            if in_circle(int(width * 0.3), int(height*0.45), 125, fingerLs[0]) and in_circle(int(width * 0.7), int(height*0.45), 125, fingerLs[1]):

                # left joystick
                    # left right
                if fingerLs[0][0] > int(width * 0.3): lr = -((int(width * 0.3- fingerLs[0][0]))/125)
                else: lr = -(int(width * 0.3- fingerLs[0][0]))/125
                    # forward backward
                if fingerLs[0][1] > int(height*0.45): fb = (int(height*0.45-fingerLs[0][1]))/125
                else: fb = (int(height*0.45-fingerLs[0][1]))/125

                # right joystick
                    # yaw velocity
                if fingerLs[1][0] > int(width * 0.7): yv = -((int(width * 0.7 - fingerLs[1][0]))/125)
                else: yv = -(int(width * 0.7 - fingerLs[1][0]))/125
                    # up down
                if fingerLs[1][1] > int(height*0.45): ud = (int(height*0.45-fingerLs[1][1]))/125
                else: ud = (int(height*0.45-fingerLs[1][1]))/125
                # send rc to tello
                myTello.send_rc_control(int(lr*speed),int(fb*speed),int(ud*speed),int(yv*speed))
                # print('left idx F: ', (int(lr*speed),int(fb*speed)), 'right idx F: ', (int(ud*speed),int(yv*speed)))
        ##########################################################################################################################################################
        ######## for saftey reasons if one finger is outside of the joystick circles set veolcity to 0 ########
        ##########################################################################################################################################################
            else:
                myTello.send_rc_control(0,0,0,0)
                cv2.circle(img2, (int(width * 0.3), int(height*0.45)), 25, BLACK, cv2.FILLED)
                cv2.circle(img2, (int(width * 0.7), int(height*0.45)), 25, BLACK,  cv2.FILLED)
        except:
            cv2.circle(img2, (int(width * 0.3), int(height*0.45)), 25, BLACK, cv2.FILLED)
            cv2.circle(img2, (int(width * 0.7), int(height*0.45)), 25, BLACK,  cv2.FILLED)
            pass
        ######## Insert Tello live stream into control center image ########
        try:
            img2[460:700, 420:780] = frame
        except:
            pass
    ##########################################################################################################################################################
    ##########################################################################################################################################################
    else:
        cv2.putText(img2, 'CONTROL DEACTIVATED',(450,30), cv2.FONT_HERSHEY_SIMPLEX, 1,BLACK, 3)
        cv2.putText(img2, 'To activate Tello hand controller',(340,300), cv2.FONT_HERSHEY_SIMPLEX, 1,BLACK, 2)
        cv2.putText(img2, 'move both index fingers',(400,340), cv2.FONT_HERSHEY_SIMPLEX, 1,BLACK, 2)
        cv2.putText(img2, 'into the boxes above',(430,380), cv2.FONT_HERSHEY_SIMPLEX, 1,BLACK, 2)
        ######## Insert Tello videostream into control center ########
        try:
            img2[460:700, 420:780] = frame
        except:
            pass

    if controlCenter:
        cv2.imshow('Control Center', img2)
    else:
        cv2.imshow('Control Center', img2)
        cv2.imshow('WebcamImage', img)
        cv2.imshow('Tello', frame)

    if cv2.waitKey(5) & 0xFF == 27:
        myTello.streamoff()
        myTello.land()
        break

cap.release()