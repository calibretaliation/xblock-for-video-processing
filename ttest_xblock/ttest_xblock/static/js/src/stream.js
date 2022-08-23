function TestXBlock(runtime, element) {

const originalVideoElem = document.getElementById('ovideo')
var startBtn = document.getElementById('start-record')
var endBtn = document.getElementById('stop-record')

function SuccessUpdate(result) {
    if (result.state == 1) {
        document.getElementById('state').textContent = "DROWSY";
    }
    else {
        document.getElementById('state').textContent= "NOT DROWSY";
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
            console.log("data chunk: ", e.data.size)
        }
        window.setInterval(function() {
            recorder.stop();
            recorder.start();

        }, 100)
        window.setInterval(function(){
            console.log(blobContainer)
            console.log(blobContainer.length)
            var video = new Blob(blobContainer.splice(blobContainer.length - 1, 1), { type: 'video/mp4'});
            console.log(video)

            var streamUrl = runtime.handlerUrl(element, 'receive_video');
            var reader = new FileReader();
            reader.readAsDataURL(video);
            reader.onload = function() {
                var Mydata_2 = {"file": reader.result};
                console.log("video blob: ", reader.result);
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
})


}