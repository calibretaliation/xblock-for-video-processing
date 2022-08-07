function TestXBlock(runtime, element) {
console.log(JSON.stringify(runtime));
console.log(JSON.stringify(element));
console.log(JSON.stringify($('button', element)))
const videoElem = document.getElementById('video')

var startBtn = document.getElementById('start-record')
var endBtn = document.getElementById('stop-record')
function SuccessUpdate(result) {
    window.alert(result.value);
}
var recorder;

const settings = {
video: true,
audio: true
}

startBtn.addEventListener('click', function (e) {
    navigator.mediaDevices.getUserMedia(settings).then((stream) => {
        console.log(stream);
        videoElem.srcObject = stream

        recorder = new MediaRecorder(stream)
        console.log(recorder);

        recorder.start();

        const blobContainer = [];

        recorder.ondataavailable = function (e) {
            blobContainer.push(e.data)
        }

        recorder.onerror = function (e) {
            return console.log(e.error || new Error(e.name));
        }

        


        recorder.onstop = function (e) {

            var video = new Blob(blobContainer, { type: 'video/webm'});
            console.log(video);
            var streamUrl = runtime.handlerUrl(element, 'receive_video');
            // var a = document.createElement('a');
            // a.download = 'download.webm';
            // a.href = window.URL.createObjectURL(video);
            // console.log(a.href);
            // a.click();
            // var Mydata = {"file": a.href};  
            var reader = new FileReader();
            reader.readAsDataURL(video);
            reader.onload = function() {
                var Mydata_2 = {"file": reader.result};
                console.log(reader.result.length);
                console.log(reader.result);
                var a = document.createElement('a');
                a.download = 'download.txt';
                a.href = window.URL.createObjectURL(new Blob([JSON.stringify(Mydata_2)]));
                a.click();
                $.ajax({
                    type: "POST",
                    url: streamUrl,
                    data: JSON.stringify(Mydata_2),
                    processData: false,
                    contentType: false,
                    success: SuccessUpdate
                }); 
            }
            
            // $.ajax({
            //     type: "POST",
            //     url: streamUrl,
            //     data: JSON.stringify(Mydata_2),
            //     processData: false,
            //     contentType: false,
            //     success: SuccessUpdate
            // }); 
        }
    })
    
})



endBtn.addEventListener('click', function (e) {
    videoElem.pause();
    recorder.stop();
    
})
}