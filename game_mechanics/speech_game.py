import os
import cv2
import json
import socket
import mediapipe as mp
import speech_recognition as sr
import time
from dotenv import load_dotenv

load_dotenv()

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
success, img = cap.read()
h, w, _ = img.shape

mp_hands = mp.solutions.hands
hands_module = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)
mp_drawing = mp.solutions.drawing_utils

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)

r = sr.Recognizer()

def millis():
    return int(round(time.time() * 1000))

while True:
    success, img = cap.read()
    if not success:
        break
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands_module.process(imgRGB)
    handData = []
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lmList = [(lm.x * w, lm.y * h) for lm in hand_landmarks.landmark]
            
            grab1 = lmList[4][0] < lmList[5][0] or abs(lmList[4][0] - lmList[5][0]) < 1
            grab2 = lmList[8][1] < lmList[5][1]
            grab3 = lmList[12][1] < lmList[9][1]
            grab4 = lmList[16][1] < lmList[13][1]
            grab5 = lmList[20][1] < lmList[17][1]
            
            pose = "grab" if grab1 and grab2 and grab3 and grab4 and grab5 else "idle"
            handData.append(pose)
            
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    with sr.Microphone(device_index=0) as source2:
        r.adjust_for_ambient_noise(source2, duration=0.5)
        
        try:
            audio = r.listen(source2, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            continue
        
        start_time = millis()
        
        try:
            hasil = r.recognize_google(audio, credentials_json=json.loads(os.getenv('GOOGLE_CREDENTIALS')), language="id-ID")
            Text = hasil.lower()
            
            if millis() - start_time > 3000 or not Text:
                print("No response from Google or empty Text. Continuing to next iteration.")
                continue
            
            match Text:
                case "ka": Text = "k"
                case "ki": Text = "q"
                case "es": Text = "s"
                case "fe": Text = "v"
                case "why": Text = "w"
                case "di": Text = "d"
                case "ff": Text = "f"
                case "ha": Text = "h"
            
            print(Text)
            handData.append(Text)
            sock.sendto(str.encode(str(handData)), serverAddressPort)
        
        except sr.UnknownValueError:
            print("Google speech recognition could not understand audio")
        
        except sr.RequestError as e:
            print(f"Could not request results from Google speech recognition service; {e}")
    
    cv2.imshow("Frame", img)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
