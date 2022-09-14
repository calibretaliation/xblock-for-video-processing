function TestXBlock(runtime, element) {

const originalVideoElem = document.getElementById('ovideo')
var startBtn = document.getElementById('start-record')
var endBtn = document.getElementById('stop-record')
// Update ID input when backend success 
function IDUpdate(result) {
    document.getElementById('student').textContent = result.student_id;
}
const form = document.getElementById('form_id');
// Send ID input to backend, update on calling IDUpdate function 
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

function diemdanhUpdate(result) {
    window.alert(result.diemdanh);
}

// Show update result from backend process
function SuccessUpdate(result) {
    console.log(result.pose_check)
    if (result.state == 1) {
        document.getElementById('state').textContent = "DROWSY";
    }
    else {
        document.getElementById('state').textContent= "NOT DROWSY";
    }
    if (result.pose_check == "2 FACE") {
        document.getElementById('pose').textContent= result.pose_check;

        // window.alert("THERE ARE 2 FACES");
    }
    else if (result.pose_check == "FACE NOT FOUND") {
        document.getElementById('pose').textContent= result.pose_check;

        // window.alert("FACE NOT FOUND");
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

// click start, start record video and send video chunks on streaming
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

        // Every 100 miliseconds, stop recorder to raise a dataavailable event and start again 
        // Restarting recorder does not affect media device 
        // because recorder only do the recording job, not the running camera job
        interval_1 = window.setInterval(function() {
            recorder.stop();
            recorder.start();
        }, 200)
        var counter = 0;
        // Every 1001 milisecond, we have 10 chunks of video in BlobContainer
        // But to make sending faster and lighter, I took only the last video chunks to send.
        interval_2 = window.setInterval(function(){
            if (counter < 10) {
                counter += 1;
                var video = new Blob(blobContainer.splice(blobContainer.length - 1, 1), { type: 'video/mp4'});

                var diemdanhUrl = runtime.handlerUrl(element, 'diemdanh');
                // FileReader reads blob to base64 string to send
                var reader = new FileReader();
                reader.readAsDataURL(video);
                // On reading complete, send data
                reader.onload = function() {
                    var Mydata_2 = {"file": reader.result};
                    $.ajax({
                        type: "POST",
                        url: diemdanhUrl,
                        data: JSON.stringify(Mydata_2),
                        processData: false,
                        contentType: false,
                        success: diemdanhUpdate
                    }); 
                }
                // Empty the Blob to reduce memory, and continue recording the next 1001 ms 
                blobContainer = []
            }
            else {
                // Cut off all other video chunks except for the last chunk (blob)
                var video = new Blob(blobContainer.splice(blobContainer.length - 1, 1), { type: 'video/mp4'});

                var streamUrl = runtime.handlerUrl(element, 'receive_video');
                // FileReader reads blob to base64 string to send
                var reader = new FileReader();
                reader.readAsDataURL(video);
                // On reading complete, send data
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
    
                // Empty the Blob to reduce memory, and continue recording the next 1001 ms 
                blobContainer = []
            }
            
        }, 1010)

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
