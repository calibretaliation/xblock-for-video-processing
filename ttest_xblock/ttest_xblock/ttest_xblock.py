"""TO-DO: Write a description of what this XBlock is."""

import base64
import io
import json
from django.shortcuts import render
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, Boolean, String 
import cv2
from django.http import HttpResponse, StreamingHttpResponse
from django.urls import path
from django.core.files.storage import FileSystemStorage
from flask_uploads import UploadSet
from werkzeug.utils import secure_filename
#Change import in flask_uploads.py
from flask import Flask, jsonify, request
import requests

class TestXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    count = Integer(
        default=0, scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )
    upvotes = Integer(help="Number of up votes", default=0,
        scope=Scope.user_state_summary)
    downvotes = Integer(help="Number of down votes", default=0,
        scope=Scope.user_state_summary)
    voted = Boolean(help="Has this student voted?", default=False,
        scope=Scope.user_state)
    streaming = String(help = "Streaming image", default="",
        scope=Scope.user_state_summary)
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the TestXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/index.html")
        frag = Fragment(html.format(self=self))
        frag.add_javascript(self.resource_string("static/js/src/stream.js"))
        frag.initialize_js('TestXBlock')
        return frag
    @XBlock.json_handler
    def receive_video(self, data, suffix=''):
            video_content = data['file'][23:]
            #fs.save('video.mp4', myfile)
            print(len(data['file']))
            print(type(data['file']))
            decoded_string = base64.b64decode(video_content) 

            with open('video.webm', 'wb') as wfile:
                wfile.write(decoded_string)

            # print(json.loads(video_content))
            with open('video.txt', 'w') as f_vid:
                f_vid.write(video_content)
            return {"value": "1"}
            # uploaded_file_url = fs.url(filename)

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("TestXBlock",
             """<ttest_xblock/>
             """),
        ]
