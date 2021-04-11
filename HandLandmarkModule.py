from socket import AI_PASSIVE
import mediapipe as mp
import time
import cv2


class handLandmarkDetector:
    def __init__(self, mode=False, maxHands=2, detectionConf=0.5, trackConf=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionConf = detectionConf
        self.trackConf = trackConf

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.maxHands, self.detectionConf, self.trackConf)
        self.mp_draw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        img = cv2.flip(img,1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        if self.results.multi_hand_landmarks:
            # Draw hand to image
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return img
    
    def drawFingerPoint(self, img, drawLeft=True, drawRight=True, finger= 8): # finger id 8 is index finger
        # get handedness
        if self.results.multi_hand_landmarks:
            for id_hnd, hnd in enumerate(self.results.multi_handedness):
                hnd_name = hnd.classification[0].label
                hand = self.results.multi_hand_landmarks[id_hnd]

                h, w, c = img.shape
                
                for id, lm in enumerate(hand.landmark):
                    # draw left finger
                    if drawLeft:
                        if id == finger and hnd_name =='Left':
                            ind_finger_l_x = int(lm.x * w)
                            ind_finger_l_y = int(lm.y * h)
                            cv2.circle(img, (int(ind_finger_l_x), int(ind_finger_l_y)), 25, (0,255,0), cv2.FILLED)
                            cv2.putText(img, hnd_name, (int(w*0.25),int(h*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0), 3) # draws left to img if left hand is detected
                    
                    # draw right finger
                    if drawRight:
                        if id == finger and hnd_name =='Right':
                            ind_finger_r_x = int(lm.x * w)
                            ind_finger_r_y = int(lm.y * h)
                            cv2.circle(img, (int(ind_finger_r_x), int(ind_finger_r_y)), 25, (0,0,255), cv2.FILLED)
                            cv2.putText(img, hnd_name, (int(w*0.75),int(h*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 3) # draws left to img if left hand is detected
        
                    try:
                        return [(ind_finger_l_x, ind_finger_l_y),(ind_finger_r_x, ind_finger_r_y)]
                    except:
                        pass


def in_circle(center_x, center_y, radius, coords):
    x, y = coords
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= radius ** 2



# def main():

#     width = 1200
#     height = 700
#     fControl = True 
#     ptime = 0
#     ctime = 0
#     cap = cv2.VideoCapture(0)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#     counter = 0

#     detector = handLandmarkDetector()

#     while True:
#         success, img = cap.read()
#         img = detector.findHands(img)
#         fingerLs = detector.drawFringerPoint(img)
#         # print(counter)
#         ctime = time.time()
#         fps = 1/(ctime - ptime)
#         ptime = ctime
#         cv2.putText(img, str(int(fps)),(10,30), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,255), 2)
#         cv2.circle(img, (int(width * 0.1), int(height*0.1)), 25, (0,255,0), 2)
#         cv2.circle(img, (int(width * 0.9), int(height*0.1)), 25, (0,255,0), 2)

#         try:
#             if in_circle(int(width * 0.1), int(height*0.1), 25, fingerLs[0] ) and in_circle(int(width * 0.9), int(height*0.1), 25, fingerLs[1]):
#                 counter +=1
#                 if counter == 30:
#                     fControl = not fControl
#                     print('Control activated', fControl)
#             else:
#                 counter = 0
#         except:
#             pass
        
#         if fControl:    
#             cv2.putText(img, 'Control activated',(500,30), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,0), 3)

#             # left joystick
#             cv2.circle(img, (int(width * 0.3), int(height*0.5)), 125, (0,255,0), 7)
#             # cv2.circle(img, (int(width * 0.3), int(height*0.5)), 25, (0,255,0), cv2.FILLED)
#             # righ joystick
#             cv2.circle(img, (int(width * 0.7), int(height*0.5)), 125, (0,255,0), 7)
#             # cv2.circle(img, (int(width * 0.7), int(height*0.5)), 25, (0,255,0),  cv2.FILLED)

#             try:
#                 if in_circle(int(width * 0.3), int(height*0.5), 125, fingerLs[0]) and in_circle(int(width * 0.7), int(height*0.5), 125, fingerLs[1]):

#                     print('left idx F: ', fingerLs[0], 'right idx F: ', fingerLs[1])
#                 else:
#                     cv2.circle(img, (int(width * 0.3), int(height*0.5)), 25, (0,255,0), cv2.FILLED)
#                     cv2.circle(img, (int(width * 0.7), int(height*0.5)), 25, (0,255,0),  cv2.FILLED)
#             except:
#                 cv2.circle(img, (int(width * 0.3), int(height*0.5)), 25, (0,255,0), cv2.FILLED)
#                 cv2.circle(img, (int(width * 0.7), int(height*0.5)), 25, (0,255,0),  cv2.FILLED)
#                 pass


#         else:
#             cv2.putText(img, 'Control deactivated',(500,30), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,0), 3)
        
        
#         cv2.imshow('MediaPipe Hands', img)

#         if cv2.waitKey(5) & 0xFF == 27:
#             break

#     cap.release()

# if __name__ == main():
#     main()