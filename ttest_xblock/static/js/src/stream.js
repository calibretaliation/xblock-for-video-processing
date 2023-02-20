function TestXBlock(runtime, element) {

const originalVideoElem = document.getElementById('ovideo')

var endBtn = document.getElementById('stop-record')
var counter = 0;
var aiserver = "https://aiserver.daotao.ai:49999/";
var streamUrl = runtime.handlerUrl(element, 'receive_video');
var reader = new FileReader();
var counter_thres = Infinity;
var blobContainer = [];
var diemdanh_ok = true;
classID = document.getElementById('course').textContent;

function IDUpdate(result) {
    document.getElementById('student').textContent = result.student_id;
    diemdanh_ok = false;
}
const form = document.getElementById('form_id');
// Send ID input to backend, update on calling IDUpdate function 
form.addEventListener('submit', (event) => {
    event.preventDefault();
    var idUrl = runtime.handlerUrl(element, "receive_id");
    stuid = form.elements['student_id'].value;
    console.log("studentid: ", stuid, typeof(stuid))
    $.ajax({
        type: "POST",
        url: idUrl,
        data: JSON.stringify({"student_id": stuid}),
        success: IDUpdate
    }); 
});
// stuid = document.getElementById('student').textContent;

function send_video() {
    var blob = recorder.getBlob()
    var video = new Blob(blobContainer.splice(blobContainer.length - 1, 1), { type: 'video/mp4'});
    counter += 1
    // FileReader reads blob to base64 string to send
    reader.readAsDataURL(video);
    if (counter > counter_thres) {
        
        // On reading complete, send data
        // reader.onload = function() {
        //     var Mydata_2 = {"file": reader.result,
        //                                     "stuid": stuid};
        //     $.ajax({
        //         type: "POST",
        //         url: aiserver,
        //         data: JSON.stringify(Mydata_2),
        //         processData: false,
        //         contentType: false,
        //         success: SuccessUpdate
        //     }); 
        // }
        
        // // Empty the Blob to reduce memory, and continue recording the next 1001 ms 
        // blobContainer = []
    }
    else {
        
        // On reading complete, send data
        reader.onload = function() {
            var Mydata_2 = {"file": reader.result,
                            // "counter": counter,
                            // "counter_thres": counter_thres,
                            "classID":0,
                            "stuid": stuid};
            $.ajax({
                type: "POST",
                url: aiserver,
                data: JSON.stringify(Mydata_2),
                processData: false,
                contentType: false,
                success: diemdanhUpdate,
                headers: { 'Access-Control-Allow-Origin': '*' }
            }); 
        }
        // Empty the Blob to reduce memory, and continue recording the next 1001 ms 
        blobContainer = [] 
        
    }
        
}
function diemdanhUpdate(result) {
    // send_video();
    document.getElementById('diemdanh').textContent = result.data;
    document.getElementById('diemdanh').style.color = "black";
    if  (!['Người lạ', 'Phát hiện nhiều người trong khung hình', 'Không phát hiện người'].includes(result.data)) {
        diemdanh_ok = true;
        console.log(diemdanh_ok)
    }
}

// Show update result from backend process
function SuccessUpdate(result) {
    send_video()
    if (result.state == 1) {
        document.getElementById('state').textContent = "CẢNH BÁO BUỒN NGỦ !";
        document.getElementById('state').style.color = "red";

    }
    else {
        document.getElementById('state').textContent= "Bình thường";
        document.getElementById('state').style.color = "black";

    }

    if (['MORE THAN 1 FACE', 'NOT CORRECT', 'FACE NOT FOUND'].includes(result.head_pose_check)) {
        if (result.head_pose_check == 'MORE THAN 1 FACE') {
            document.getElementById('head_pose').textContent= "PHÁT HIỆN NHIỀU KHUÔN MẶT";
        }
        else if (result.head_pose_check == 'NOT CORRECT') {
            document.getElementById('head_pose').textContent= "CẢNH BÁO: TƯ THẾ KHÔNG CHÍNH XÁC";
        }
        else if (result.head_pose_check == 'FACE NOT FOUND') {
            document.getElementById('head_pose').textContent= "CẢNH BÁO: KHÔNG PHÁT HIỆN KHUÔN MẶT";
        }
        
        document.getElementById('head_pose').style.color= "red";
    }
    else {
        document.getElementById('head_pose').textContent= "Bình thường";
        document.getElementById('head_pose').style.color= "black";
    }

    if (result.pose_check == "IS LAYING") {
        document.getElementById('pose').textContent= "CẢNH BÁO: TƯ THẾ KHÔNG CHÍNH XÁC";
        document.getElementById('pose').style.color= "red";
    }
    else{
        document.getElementById('pose').textContent= "TƯ THẾ  CHÍNH XÁC";
        document.getElementById('pose').style.color= "black";

    }

    if (result.has_phone == "True") {
        document.getElementById('phone').textContent= "CẢNH BÁO: PHÁT HIỆN ĐIỆN THOẠI";
        document.getElementById('phone').style.color= "red";
    }
    else{
        document.getElementById('phone').textContent= "Bình thường";
        document.getElementById('phone').style.color= "black";
    }
}

const settings = {
    video: true,
    audio: false
}
window.addEventListener('load', function () {
    navigator.mediaDevices.getUserMedia(settings).then(function(stream) {
    originalVideoElem.srcObject = stream
    originalVideoElem.addEventListener('loadedmetadata', function() {
        ctx.translate(video.videoWidth, 0); 
        ctx.scale(-1, 1);
     });
    
    let recorder = RecordRTC(stream, {
        type: 'video/mp4',
        mimeType: 'video/webm',
        recorderType: MediaStreamRecorder,
    });

    interval_1 = window.setInterval(async function() {
        recorder.startRecording();

        const sleep = m => new Promise(r => setTimeout(r, m));
        await sleep(500);

        recorder.stopRecording(function(){
            var blob = this.getBlob();
            reader.readAsDataURL(blob);
            
            reader.onload =async function() {
                var Mydata_2 = {"file": reader.result,
                "counter": counter,
                "counter_thres": counter_thres,
                "classID": classID,
                "stuid": stuid};
                if (diemdanh_ok == false) {
                    counter += 1
                    console.log(counter)
                    await $.ajax({
                        type: "POST",
                        url: aiserver,
                        data: JSON.stringify(Mydata_2),
                        processData: false,
                        contentType: false,
                        success: diemdanhUpdate,
                        headers: { 'Access-Control-Allow-Origin': '*' }
                    }); 
                }
                else if (diemdanh_ok == true) {}
            }
        });
    }, 5000)        

    interval_2 = window.setInterval(function() {
        if (counter >= 1) {
            diemdanh_ok = false
            console.log("reset ", diemdanh_ok)
        }
    }, 150000);

})    

});

}
