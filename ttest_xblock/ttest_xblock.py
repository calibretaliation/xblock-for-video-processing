import base64
import json
import time
from tokenize import String
from django.shortcuts import render
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock, XBlockAside
from xblock.fields import Integer, Scope, Dict, String
#from tracking.Tracking.Pose_tracker import PoseTracker
#from tracking.Tracking.pose_tracking import runPoseCheck
#from tracking.Tracking.eye_tracker import EyeTracker
#from services.FacePoseCheck.utils import  checkFacePose
import requests
from threading import Thread
# from django.http import HttpResponse, StreamingHttpResponse
# from django.urls import path
# from django.core.files.storage import FileSystemStorage
# from flask_uploads import UploadSet
# from werkzeug.utils import secure_filename
# from PhoneDetection.yolov4_detect_phone import detect
#Change import in flask_uploads.py
# from flask import Flask, jsonify, request
# from tracking.Tracking.pose_tracking import runPoseCheck
# from tracking.Tracking.eye_tracking import  eye_track_frame
# from face_recognition.face_recog_module import face_recog_module
class TestXBlock(XBlock):

    student_id = Integer(help = "Student ID", 
        scope = Scope.user_state)
    sleepy_state = Integer(help="SLEEPY STATE", default=0,
        scope=Scope.user_state)
    head_pose_check = String(help="POSE RESULT", default="CORRECT",
        scope=Scope.user_state)    
    count = Integer(help = "count of video", default=0,
        scope=Scope.user_state)
    has_phone = String(help = "Phone detection", default = "False",
        scope = Scope.user_state)
    ten_diemdanh = String(help = "Ket qua diem danh", default = "Unknown",
        scope = Scope.user_state)
    pose_check = String(help = "Body estimate", default = "NORMAL",
        scope = Scope.user_state)

    student_count = Integer(help = "total number of student", default = 0, 
        scope = Scope.user_state_summary)
    student_summary =Dict(help = "All students state", default = {},
        scope = Scope.user_state_summary)
    
    
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        self.count = 0
        html = self.resource_string("static/html/index1.html")
        frag = Fragment(html.format(self=self))
        frag.add_javascript(self.resource_string("static/js/src/stream.js"))
        frag.initialize_js('TestXBlock')
        return frag

    def teacher_view(self, context = None):
        html = self.resource_string("static/html/teacher.html")
        frag = Fragment(html.format(self=self))
        frag.add_javascript(self.resource_string("static/js/src/teacher.js"))
        frag.initialize_js('TestXBlock')

        return frag

    @XBlock.json_handler
    def receive_video(self, data, suffix=''): #receive and process videos sent when click start
        start = time.time()
        self.diemdanh = ""
        video_content = data['file'][22:]
        decoded_string = base64.b64decode(video_content) 
        hash_id = hash(start)
        video_name = f"video_{hash_id}.mp4"
        with open(f"videos/{video_name}", 'wb') as wfile:
            wfile.write(decoded_string)
        def run_phone_service():
            test_result_phone = requests.request('GET', f"http://localhost:50000/phone-detect/{video_name}")
            self.has_phone = json.loads(test_result_phone.text)['data']
        def run_pose_track_service():
            test_result_pose = requests.request('GET', f"http://localhost:50001/pose-tracking/{video_name}")
            # print(type(test_result_pose.text))
            # print(json.loads(test_result_pose.text)['data'])
            self.pose_check = json.loads(test_result_pose.text)['data']
        def run_head_pose_service():
            test_result_head = requests.request('GET', f"http://localhost:50002/head-pose/{video_name}")
            self.head_pose_check = json.loads(test_result_head.text)['data']
        def run_eye_service():
            test_eye_check = requests.request('GET', f"http://localhost:5005/eye-check/{video_name}")
            self.sleepy_state = json.loads(test_eye_check.text)['data']

        # thread_phone = Thread(target=run_phone_service)
        # thread_phone.start()
        # thread_pose = Thread(target = run_pose_track_service)
        # thread_pose.start()
        # thread_head = Thread(target = run_head_pose_service)
        # thread_head.start()
        # thread_eye = Thread(target = run_eye_service)
        # thread_eye.start()

        # thread_phone.join()
        # thread_pose.join()
        # thread_head.join()
        # thread_eye.join()
        self.student_summary[f"{self.student_id}"] = f"{self.sleepy_state}"

        return{"state": f"{self.sleepy_state}",
                    "head_pose_check": f"{self.head_pose_check}",
                    "student_id": f"{self.student_id}",
                    "has_phone": f"{self.has_phone}",
                    "pose_check": f"{self.pose_check}"
                    }

    @XBlock.json_handler
    def diemdanh(self, data, suffix=''): 
        test_result = requests.request('POST', f"http://localhost:49999/face-recog/", obj = data).json()
        for result in test_result['data']:
            if int(data['counter']) <= int(data['counter_thres']) and result not in ["Unknown", "2 FACE", "NOT FOUND"]:
                    self.ten_diemdanh = result
            elif int(data['counter']) >  int(data['counter_thres']):
                self.ten_diemdanh = result

    
        return{"diemdanh": f"{self.ten_diemdanh}"}


    @XBlock.json_handler
    def receive_id(self, data, suffix=''): #save student ID from front end
        print(data['student_id'])
        self.student_id = int(data['student_id'])
        # self.student_summary[f"{self.student_id}"] = f"{self.sleepy_state}"
        return {"student_id": f"{self.student_id}"}
    @XBlock.json_handler
    def student_summary_update(self, data, suffix=''):
        return self.student_summary
    @staticmethod
    def workbench_scenarios():
        return [
            ("TestXBlock",
             """<ttest_xblock/>
             """),
        ]


class TestXBlockBlock(TestXBlock, XBlock):
    """
    Create Block for Xblock
    """

class TestXBlockAside(TestXBlock, XBlockAside):
    """
    An XBlockAside with online exam support.
    Each student is recorded and Ai will analyst the video to find if student are cheating or not.
    This demonstrates multiple data scopes and ajax handlers.
    """
    @XBlockAside.aside_for('student_view')
    def student_view_aside(self, block, context=None):  # pylint: disable=unused-argument
        
        fragment = self.student_view(context)
        fragment.initialize_js('TestXBlockAside')
        return fragment
