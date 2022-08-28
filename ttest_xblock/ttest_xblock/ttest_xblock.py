import base64
import io
import json
from bson import List
import cv2
from django.shortcuts import render
import pkg_resources
from services.FacePoseCheck.utils import run_check_pose_video
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, Dict, List
from django.http import HttpResponse, StreamingHttpResponse
from django.urls import path
from django.core.files.storage import FileSystemStorage
from flask_uploads import UploadSet
from werkzeug.utils import secure_filename
#Change import in flask_uploads.py
from flask import Flask, jsonify, request
import requests
from tracking.Tracking.eye_tracking import  run_eye_check
class TestXBlock(XBlock):
    student_id = Integer(help = "Student ID", 
        scope = Scope.user_state)
    sleepy_state = Integer(help="SLEEPY STATE", default=0,
        scope=Scope.user_state)
    pose_check = Integer(help="POSE RESULT", default=0,
        scope=Scope.user_state)    
    count = Integer(help = "count of video", default=0,
        scope=Scope.user_state)

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
        html = self.resource_string("static/html/index.html")
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
    def receive_video(self, data, suffix=''):
            #save received data
            video_content = data['file'][22:]
            decoded_string = base64.b64decode(video_content) 
            video_name = f"video_{self.student_id}_{self.count}.mp4"
            with open(video_name, 'wb') as wfile:
                wfile.write(decoded_string)
            #to mark parts of video
            self.count += 1
            #run eye check
            self.sleepy_state = run_eye_check(video_name, self.student_id)
            #run pose check
            self.pose_check = run_check_pose_video(video_name)
            if  self.sleepy_state == 1:
                self.student_summary[f"{self.student_id}"] = f"{self.sleepy_state}"
                print(self.student_summary)

                return{"state": f"{ self.sleepy_state}",
                            "pose_check": f"{self.pose_check}",
                            "student_id": f"{self.student_id}"}
            elif  self.sleepy_state == 0:
                self.student_summary[f"{self.student_id}"] = f"{self.sleepy_state}"
                print(self.student_summary)
                return{"state": f"{ self.sleepy_state}",
                            "pose_check": f"{self.pose_check}",
                            "student_id": f"{self.student_id}"}
    @XBlock.json_handler
    def receive_id(self, data, suffix=''):
        self.student_id = int(data['student_id'])
        self.student_summary[f"{self.student_id}"] = f"{self.sleepy_state}"
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

