import cv2
import socket
import mediapipe as mp

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
success, img = cap.read()
h, w, _ = img.shape

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    
    poseData = []
    pose_direction = ""
    
    if results.pose_landmarks:
        lmList = []
        for id, lm in enumerate(results.pose_landmarks.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append((id, cx, cy))
            poseData.extend([id, cx, h - cy])
        
        right1 = lmList[19][2] > lmList[9][2]
        right2 = lmList[24][2] > lmList[20][2]
        left1 = lmList[20][2] > lmList[9][2]
        left2 = lmList[24][2] > lmList[19][2]
        
        if left1 and left2:
            pose_direction = "left"
        elif right1 and right2:
            pose_direction = "right"
        
        if pose_direction:
            print(pose_direction)
            sock.sendto(str.encode(pose_direction), serverAddressPort)
    
    mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.imshow("img", img)
    cv2.waitKey(1)
