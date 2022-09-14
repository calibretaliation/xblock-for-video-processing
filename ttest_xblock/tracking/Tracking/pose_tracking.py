import cv2
import mediapipe as mp
import pandas as pd


mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils
lm_list = []

def make_landmark_timestep(results):
    c_lm = []
    for id, lm in enumerate(results.pose_landmarks.landmark):
        c_lm.append(lm.x)
        c_lm.append(lm.y)
        c_lm.append(lm.z)
        c_lm.append(lm.visibility)
    return c_lm

def draw_landmark_on_image(mp_drawing, results, img):
    mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    for id, lm in enumerate(results.pose_landmarks.landmark):
        h, w, c = img.shape
        cx, cy = int(lm.x*w), int(lm.y*h)
        cv2.circle(img,(cx, cy), 5, (255, 0, 0), cv2.FILLED)
    return img
def runPoseCheck(video_name):
    cap = cv2.VideoCapture(video_name)
    while True:
        ret, frame = cap.read()
        if ret:
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frameRGB)
            if results.pose_landmarks:
                lm = make_landmark_timestep(results)
                lm_list.append(lm)
                frame = draw_landmark_on_image(mp_drawing, results, frame)

            cv2.imwrite("image.jpg",frame)

        else:
            break

    cap.release()
    cv2.destroyAllWindows()





