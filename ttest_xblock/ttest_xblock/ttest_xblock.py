"""TO-DO: Write a description of what this XBlock is."""

from django.shortcuts import render
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, Boolean, String 
import cv2
from django.http import StreamingHttpResponse
from django.urls import path

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
        frag.add_javascript(self.resource_string("static/js/src/src.js"))
        frag.initialize_js('TestXBlock')
        return frag

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'

        self.count += 2
                
        return {"count": self.count}
    
    # @XBlock.json_handler
    # def stream(self,data, suffix =''):
    #     return render()
        # cap = cv2.VideoCapture(0) 

        # while True:
        #     ret, frame = cap.read()

        #     if not ret:
        #         print("Error: failed to capture image")
        #         break
        #     cv2.imwrite("static/image/streaming.jpg", frame)
        #     self.streaming = pkg_resources.resource_filename(__name__,"static/image/streaming.jpg")
        #     print(self.streaming)
        #     return {"streaming" : f"{self.streaming}"}
    # def video_feed(request):
    #     def stream():
    #         cap = cv2.VideoCapture(0) 

    #         while True:
    #             ret, frame = cap.read()

    #             if not ret:
    #                 print("Error: failed to capture image")
    #                 break

    #             cv2.imwrite('demo.jpg', frame)
    #             yield (b'--frame\r\n'
    #                 b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')

    
    #     return StreamingHttpResponse(stream(), content_type='multipart/x-mixed-replace; boundary=frame')

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("TestXBlock",
             """<ttest_xblock/>
             """),
        ]
