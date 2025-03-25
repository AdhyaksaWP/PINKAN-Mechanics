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

count = 0
previous_count = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)

while True:
    success, img = cap.read()
    if not success:
        break
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands_module.process(imgRGB)
    
    total_fingers_up = 0
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lmList = [(lm.x * w, lm.y * h) for lm in hand_landmarks.landmark]
            
            thumbUp = abs(lmList[4][0] - lmList[5][0]) > 40
            indexFingerUp = lmList[8][1] < lmList[4][1] - 50
            middleFingerUp = lmList[12][1] < lmList[4][1] - 50
            ringFingerUp = lmList[16][1] < lmList[4][1] - 50
            pinkyFingerUp = lmList[20][1] < lmList[4][1] - 40
            
            fingers_up = sum([thumbUp, indexFingerUp, middleFingerUp, ringFingerUp, pinkyFingerUp])
            total_fingers_up += fingers_up
            
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    if total_fingers_up != previous_count:
        count = total_fingers_up
        previous_count = total_fingers_up
        print(f"Count: {count}")
        sock.sendto(str(count).encode(), serverAddressPort)
    
    cv2.putText(img, f"Fingers Up: {count}", (540, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv2.imshow("Math Game", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
