import cv2
import dlib
from scipy.spatial import distance


def calculate_EAR(eye):
    A = distance.euclidean(eye[1],eye[2])
    B = distance.euclidean(eye[2],eye[4])
    C = distance.euclidean(eye[0],eye[3])
    EAR = (A+B)/(2.0*C)
    EAR = round(EAR,2)
    return EAR

def calculate_MAR(mouth):
    A = distance.euclidean(mouth[1], mouth[7])
    B = distance.euclidean(mouth[2], mouth[6])
    C = distance.euclidean(mouth[3], mouth[5])
    D = distance.euclidean(mouth[0], mouth[4])
    MAR = (A+B+C)/(3.0*D)
    MAR = round(MAR,2)
    return MAR
def run_eye_check(video = "video.mp4", id = 0):
    cap = cv2.VideoCapture(video)
    countClose = 0
    currState = 0
    alarmThreshold = 3

    hog_face_detector = dlib.get_frontal_face_detector()
    dlib_facelandmark = dlib.shape_predictor("ttest_xblock/tracking/Tracking/68_face_landmarks_predictor.dat")

    while True:
        _, frame = cap.read()
        if not  _:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = hog_face_detector(gray)

        for face in faces:

            face_landmarks = dlib_facelandmark(gray, face)
            left_eye = []
            right_eye = []
            mouth = []

            for n in range(0, 68):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                cv2.circle(frame, (x, y), 1, (0, 255, 255), 1)

            for n in range(36, 42):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                left_eye.append((x, y))
                next_point = n + 1
                if n == 41:
                    next_point = 36
                x2 = face_landmarks.part(next_point).x
                y2 = face_landmarks.part(next_point).y
                cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

            for n in range(42, 48):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                right_eye.append((x, y))
                next_point = n + 1
                if n == 47:
                    next_point = 42
                x2 = face_landmarks.part(next_point).x
                y2 = face_landmarks.part(next_point).y
                cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

            for n in range(48,60):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                mouth.append((x, y))
                next_point = n + 1
                if n == 59:
                    next_point = 48
                x2 = face_landmarks.part(next_point).x
                y2 = face_landmarks.part(next_point).y
                cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

            for n in range(60,68):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                mouth.append((x, y))
                next_point = n + 1
                if n == 67:
                    next_point = 60
                x2 = face_landmarks.part(next_point).x
                y2 = face_landmarks.part(next_point).y
                cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

            left_EAR = calculate_EAR(left_eye)
            right_EAR = calculate_EAR(right_eye)
            EAR = (left_EAR + right_EAR) / 2

            MAR = calculate_MAR(mouth)

            if EAR < 0.1:
                currState = 1
                countClose += 1
            else:
                currState = 0
                countClose = 0
            # print("EAR :", EAR)

            if MAR > 0.75:
                cv2.putText(frame, "YAWN", (450, 100),cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                cv2.putText(frame, "Are you Sleepy?", (20, 400),cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                # print("Drowsy")
                # countClose +=1
                currState = 1
            else:
                currState = 0
                # countClose = 0
            # print("MAR", MAR)

        if countClose > alarmThreshold:
            cv2.putText(frame, "DROWSY", (20, 100),cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            cv2.putText(frame, "Are you Sleepy?", (20, 400),cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            # print("Drowsy")

        cv2.imwrite(f"drowsy_detect_{id}.jpg", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break
    cap.release()
    return currState
