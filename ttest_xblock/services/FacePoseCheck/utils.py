from multiprocessing import connection
from sre_constants import SUCCESS
from turtle import circle
import cv2 
import mediapipe as mp 
import numpy as np 
import time 

mp_face_mesh = mp.solutions.face_mesh 
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

def checkFacePose(image):
    # suppose input image is RGB 
    image = np.copy(image) # copy
    image = cv2.flip(image, 1)
    results = face_mesh.process(image)
    img_h, img_w, _ = image.shape 
    face_3d = [] 
    face_2d = [] 
     
    if results.multi_face_landmarks:
        if len(results.multi_face_landmarks) > 1:
            return '2 FACE' # detect more than 1 face
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):
                if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                    if idx == 1:
                        nose_2d = (lm.x * img_w, lm.y * img_h)
                        nose_3d = (lm.x * img_w, lm.y * img_h, lm.z*3000)
                    x, y = int(lm.x * img_w), int(lm.y * img_h)
                    # get the 2d coordinate 
                    face_2d.append([x, y])
                    # get the 3d coordinate
                    face_3d.append([x, y, lm.z])
                    
            # conver to numpy array 
            face_2d = np.array(face_2d, dtype=np.float64)
            face_3d = np.array(face_3d, dtype=np.float64)
            
            # camera matrix 
            focal_length = 1 * img_w 
            # cam_matrix[0 ,2] = img_h / 2 
            # cam_matrix[1, 2] = img_w / 2
            cam_matrix = np.array([
                [focal_length, 0, img_h / 2],
                [0, focal_length, img_w / 2],
                [0, 0, 1]
            ])
            # the distance matrix 
            dist_matrix = np.zeros((4, 1), dtype=np.float64)
            # solve pnp 
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d,cam_matrix, dist_matrix)
            
            # get rotational matrix 
            rmat, jac = cv2.Rodrigues(rot_vec)
            # get angles
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
            # get the y rotation degree 
            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360 
            
            # see where the user head tilting 
            if y > -5 and y < 5 and x > -5 and x < 5:
                text = 'CORRECT'
            else:
                text = 'NOT CORRECT'
            return text 
    else:
        return 'FACE NOT FOUND'

def run_check_pose_video(video):
    cap = cv2.VideoCapture(video)
    pose_result = ""
    while True:
        _, frame = cap.read()
        
        if not  _:
            break
        pose_result = checkFacePose(frame)       

    cap.release()
    
    return pose_result
