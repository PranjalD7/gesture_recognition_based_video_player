from tensorflow.keras.models import load_model

model=load_model(r'C:\Users\pranj\OneDrive\Desktop\gesture_recognition\weights.h5')

import cv2
import mediapipe as mp
import math
from keras.preprocessing import image
import numpy as np
emptyt=()
class HandDetector:
    """
    Finds Hands using the mediapipe library. Exports the landmarks
    in pixel format. Adds extra functionalities like finding how
    many fingers are up or the distance between two fingers. Also
    provides bounding box info of the hand found.
    """
    
    def __init__(self, mode=False,maxHands=2, detectionCon=0.5, minTrackCon=0.5):
        """
        :param mode: In static mode, detection is done on each image: slower
        :param maxHands: Maximum number of hands to detect
        :param detectionCon: Minimum Detection Confidence Threshold
        :param minTrackCon: Minimum Tracking Confidence Threshold
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon, min_tracking_confidence = self.minTrackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.fingers = []
        self.lmList = []

    def findHands(self, img, draw=True, flipType=True):
        """
        Finds hands in a BGR image.
        :param img: Image to find the hands in.
        :param draw: Flag to draw the output on the image.
        :return: Image with or without drawings
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        allHands = []
        h, w, c = img.shape
        if  self.results.multi_hand_landmarks:
            for handType,handLms in zip(self.results.multi_handedness,self.results.multi_hand_landmarks):
                myHand={}
                ## lmList
                mylmList = []
                xList = []
                yList = []
                for id, lm in enumerate(handLms.landmark):
                    px, py = int(lm.x * w), int(lm.y * h)
                    mylmList.append([px, py])
                    xList.append(px)
                    yList.append(py)

                ## bbox
             
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx, cy = bbox[0] + (bbox[2] // 2), \
                         bbox[1] + (bbox[3] // 2)

                myHand["lmList"] = mylmList
                myHand["bbox"] = bbox
                myHand["center"] =  (cx, cy)

                if flipType:
                    if handType.classification[0].label =="Right":
                        myHand["type"] = "Left"
                    else:
                        myHand["type"] = "Right"
                else:myHand["type"] = handType.classification[0].label
                allHands.append(myHand)
            
                ## draw
                if draw:
                    
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                                  (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                                  (255, 0, 255), 2)
                    cv2.putText(img,myHand["type"],(bbox[0] - 30, bbox[1] - 30),cv2.FONT_HERSHEY_PLAIN,
                                2,(255, 0, 255),2)
        if not allHands:
             return allHands,img,emptyt
        else:
             return allHands,img,bbox
       

  

def main():
    import vlc
    media = vlc.MediaPlayer(r'C:\Users\pranj\Downloads\file_example_MP4_1920_18MG.mp4')
    media.play()
    
    cap = cv2.VideoCapture(0)
    
   

  
    class1=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    detector = HandDetector(detectionCon=0.8, maxHands=2)
    flag=0
    c=0
    while True:
        # Get image frame
        success, img = cap.read()
        # Find the hand and its landmarks
        hands,img,coor= detector.findHands(img)  # with draw
        
        # hands = detector.findHands(img, draw=False)  # without draw
        
        cv2.imshow("Image", img)
        if not hands:          
          continue
       
        test_image=img[coor[1] - 20 : coor[1] + coor[3] + 20 , coor[0] - 20 : coor[0] + coor[2] + 20]
        test_image=cv2.resize(test_image,(50,50))
 
        test_image=np.asarray(test_image)
        test_image=np.expand_dims(test_image, axis=0)
        result=class1[np.argmax(model.predict(test_image))]
        print(result)
        if result == 15:
            c+=1
        else:
            c=0
            
        if result == 0 and flag!=1:
             media.pause()
             flag=1
        elif c>=10:
            media.play()
            flag=0
   
     

        if cv2.waitKey(10) & 0xFF == ord('q'):
           break
       
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
