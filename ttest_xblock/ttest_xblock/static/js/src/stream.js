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
            console.log(window.URL.createObjectURL(new Blob(blobContainer)));
            var newVideoEl = document.createElement('video')
            newVideoEl.height = '400'
            newVideoEl.width = '600'
            newVideoEl.autoplay = true
            newVideoEl.controls = true
            newVideoEl.innerHTML = `<source src="${window.URL.createObjectURL(new Blob(blobContainer))}"
             type="video/webm">`
            //document.body.removeChild(videoElem)
            //document.body.insertBefore(newVideoEl, startBtn);
            

            var video = new Blob(blobContainer);
            var Mydata = {"file": video};
            var streamUrl = runtime.handlerUrl(element, 'receive_video');
            
            $.ajax({
                type: "POST",
                url: streamUrl,
                contentType : 'application/json; charset=utf-8',
                data: JSON.stringify(Mydata),
                success: SuccessUpdate
            }); 
        }
        
    })
    
})



endBtn.addEventListener('click', function (e) {
    videoElem.pause();
    recorder.stop();
    
})
}