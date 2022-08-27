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

cap = cv2.VideoCapture(0)

# with np.load('./CameraParams.npz') as file:
#     cam_matrix, dist_matrix, rvecs, tvecs = [file[i] for i in ('cameraMatrix', 'dist', 'rvecs', 'tvecs')]

while cap.isOpened():
    SUCCESS, image = cap.read()
    start = time.time()
    
    # Flip image horizontal for a later
    # conver bgr to rgb 
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # to improve performance 
    image.flags.writeable = False 
    # get the result 
    results = face_mesh.process(image)
    # to improve performance 
    image.flags.writeable = True 
    # convert rgb to bgr 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    img_h, img_w, _ = image.shape 
    face_3d = [] 
    face_2d = [] 
    
    if results.multi_face_landmarks:
        if len(results.multi_face_landmarks) > 1:
            text = '2 FACE' # detect more than 1 face
            cv2.putText(image, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
        else:
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
                if y > -15 and y < 15 and x > -15 and x < 15:
                    text = 'CORRECT'
                else:
                    text = 'NOT CORRECT'
                # display nose direction 
                nose_3d_project, jab = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)
                
                p1 = (int(nose_2d[0]), int(nose_2d[1]))
                p2 = (int(nose_2d[0] + y * 10), int(nose_2d[1] - x * 10))
                cv2.line(image, p1, p2, (255, 0, 0), 3)
                # add text on the image 
                cv2.putText(image, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                cv2.putText(image, "x: " + str(round(x, 2)), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
                cv2.putText(image, "y: " + str(round(y, 2)), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
                cv2.putText(image, "z: " + str(round(x, 2)), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
            
            end = time.time()
            totalTime = end - start 
            fps = round(1 / totalTime, 2)
            print("FPS: ", fps)
            
            cv2.putText(image, f'FPS: {fps}', (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
            mp_drawing.draw_landmarks(
                image=image, 
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec
            )
    cv2.imshow('HEAD POSE ESTIMATION', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
             
             
cap.release()                   
    
    