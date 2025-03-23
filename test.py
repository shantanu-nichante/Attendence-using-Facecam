from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(str1):
    speak = Dispatch("SAPI.SpVoice")
    speak.Speak(str1)

# Load trained data
with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)

with open('data/faces.pkl', 'rb') as f:  # Corrected file name
    FACES = pickle.load(f)

# Ensure FACES and LABELS have the same length
if len(LABELS) != FACES.shape[0]:
    min_length = min(len(LABELS), FACES.shape[0])
    LABELS = LABELS[:min_length]
    FACES = FACES[:min_length]

print('Shape of Faces matrix --> ', FACES.shape)
print('Number of Labels --> ', len(LABELS))

# Train KNN classifier
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Initialize webcam and background image
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
imgBackground = cv2.imread("background.png")

COL_NAMES = ['NAME', 'TIME']

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        output = knn.predict(resized_img)

        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        exist = os.path.isfile("Attendance/Attendance_" + date + ".csv")

        # Draw bounding box and label
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
        cv2.putText(frame, str(output[0]), (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

        # Store attendance
        attendance = [str(output[0]), str(timestamp)]

    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Frame", imgBackground)

    k = cv2.waitKey(1)
    
    # Take attendance when 'o' is pressed
    if k == ord('o'):
        speak("Attendance Taken..")
        time.sleep(5)

        with open("Attendance/Attendance_" + date + ".csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not exist:
                writer.writerow(COL_NAMES)
            writer.writerow(attendance)

    if k == ord('q'):  # Quit program
        break

video.release()
cv2.destroyAllWindows()
