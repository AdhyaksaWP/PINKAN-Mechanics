import cv2
import socket
import mediapipe as mp

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
success, img = cap.read()
h, w, _ = img.shape

mp_hands = mp.solutions.hands
hands_module = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8)
mp_drawing = mp.solutions.drawing_utils

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)

def process_hand(hand_landmarks, h):
    handData = []
    lmList = [(lm.x * w, h - lm.y * h) for lm in hand_landmarks.landmark]
    for lm in lmList:
        handData.extend([int(lm[0]), int(lm[1])])
    
    grab1 = lmList[1][0] < lmList[4][0] or abs(lmList[1][0] - lmList[4][0]) < 1
    grab2 = lmList[5][1] > lmList[8][1]
    grab3 = lmList[9][1] > lmList[12][1]
    grab4 = lmList[13][1] > lmList[16][1]
    grab5 = lmList[17][1] > lmList[20][1]
    
    if grab1 and grab2 and grab3 and grab4 and grab5: 
        pose = "grab"
    else:
        pose = "idle"
    
    handData.append(pose)
    return handData

while True:
    success, img = cap.read()
    if not success:
        break
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands_module.process(imgRGB)
    
    hand1Data, hand2Data = [], []
    
    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            if i == 0:
                hand1Data = process_hand(hand_landmarks, h)
            elif i == 1:
                hand2Data = process_hand(hand_landmarks, h)
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    print(hand1Data)
    print(hand2Data)
    
    cv2.imshow("Frame", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
