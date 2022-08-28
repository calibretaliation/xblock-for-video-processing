function TestXBlock(runtime, element) {

const originalVideoElem = document.getElementById('ovideo')
var startBtn = document.getElementById('start-record')
var endBtn = document.getElementById('stop-record')

function IDUpdate(result) {
    document.getElementById('student').textContent = result.student_id;
}
const form = document.getElementById('form_id');

form.addEventListener('submit', (event) => {
    event.preventDefault();
    var idUrl = runtime.handlerUrl(element, "receive_id");
    var student_id = form.elements['student_id'].value;
    $.ajax({
        type: "POST",
        url: idUrl,
        data: JSON.stringify({"student_id": student_id}),
        success: IDUpdate
    }); 
});

function SuccessUpdate(result) {
    console.log(result.pose_check)
    if (result.state == 1) {
        document.getElementById('state').textContent = "DROWSY";
    }
    else {
        document.getElementById('state').textContent= "NOT DROWSY";
    }
    if (result.pose_check == "2 FACE") {
        window.alert("THERE ARE 2 FACES");
    }
    else if (result.pose_check == "FACE NOT FOUND") {
        window.alert("FACE NOT FOUND");
    }
    else {
        document.getElementById('pose').textContent= result.pose_check;
    }

}

var recorder;

const settings = {
    video: true,
    audio: true
}

startBtn.addEventListener('click', function (e) {
    navigator.mediaDevices.getUserMedia(settings).then((stream) => {
        console.log(stream);
        originalVideoElem.srcObject = stream

        recorder = new MediaRecorder(stream)
        console.log(recorder);

        recorder.start();

        var blobContainer = [];

        recorder.ondataavailable = function (e) {
            blobContainer.push(e.data)
        }
        interval_1 = window.setInterval(function() {
            recorder.stop();
            recorder.start();
        }, 100)
        interval_2 = window.setInterval(function(){

            var video = new Blob(blobContainer.splice(blobContainer.length - 1, 1), { type: 'video/mp4'});

            var streamUrl = runtime.handlerUrl(element, 'receive_video');
            var reader = new FileReader();
            reader.readAsDataURL(video);
            reader.onload = function() {
                var Mydata_2 = {"file": reader.result};
                $.ajax({
                    type: "POST",
                    url: streamUrl,
                    data: JSON.stringify(Mydata_2),
                    processData: false,
                    contentType: false,
                    success: SuccessUpdate
                }); 
            }

            blobContainer = []
        }, 1001)

        recorder.onerror = function (e) {
            return console.log(e.error || new Error(e.name));
        }
    })



})

endBtn.addEventListener('click', function (e) {
    originalVideoElem.pause();
    recorder.stop();
    navigator.mediaDevices.getUserMedia(settings).then((stream) => {
    stream.getTracks().forEach( track => track.stop() ); 
    })
    clearInterval(interval_1);
    clearInterval(interval_2);
})

}
