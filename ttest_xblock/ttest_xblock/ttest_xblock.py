"""TO-DO: Write a description of what this XBlock is."""

import base64
import io
import json
import cv2
from django.shortcuts import render
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, Boolean, String 
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
    """
    TO-DO: document what your XBlock does.
    """

    sleepy_state = Integer(help="SLEEPY STATE", default=0,
        scope=Scope.user_state)
    student_id = Integer(help = "Student ID")
    count = Integer(help = "count of video", default=0,
        scope=Scope.user_state)
    student_count = Integer(help = "total number of student", default = 0, 
        scope = Scope.user_state_summary)
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the TestXBlock, shown to students
        when viewing courses.
        """
        self.student_count += 1
        self.student_id = self.student_count
        self.count = 0
        html = self.resource_string("static/html/index.html")
        frag = Fragment(html.format(self=self))
        frag.add_javascript(self.resource_string("static/js/src/stream.js"))
        frag.initialize_js('TestXBlock')
        return frag

    def teacher_view(self, context = None):
        html = self.resource_string("static/html/index.html")
        frag = Fragment(html.format(self=self))
        frag.add_javascript(self.resource_string("static/js/src/stream.js"))
        frag.initialize_js('TestXBlock')

        return frag
    @XBlock.json_handler
    def receive_video(self, data, suffix=''):
            video_content = data['file'][22:]
            print(len(data['file']))

            print(type(data['file']))
            decoded_string = base64.b64decode(video_content) 
            video_name = f"video_{self.student_id}_{self.count}.mp4"
            with open(video_name, 'wb') as wfile:
                wfile.write(decoded_string)
            self.count += 1
            self.sleepy_state = run_eye_check(video_name)
            print(self.sleepy_state)
            if  self.sleepy_state == 1:
                # state_image = cv2.imread("drowsy_detect.jpg")
                # image_string = base64.b64encode(state_image)
                return{"state": f"{ self.sleepy_state}"}
                                # "image":f"{image_string}"}
            elif  self.sleepy_state == 0:
                return {"state": f"{ self.sleepy_state}"}


    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("TestXBlock",
             """<ttest_xblock/>
             """),
        ]

