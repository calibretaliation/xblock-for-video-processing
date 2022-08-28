function TestXBlock(runtime, element) {
    function student_summary(result){
        let text = ""    
        for(let i =0; i<Object.keys(result).length;i++) {
            let text_1 = ""
            if (Object.values(result)[i] == '1'){
                text_1 = `STUDENT ID: ${Object.keys(result)[i]}, SLEEPY STATE: DROWSY \n `
            }
            else {
                text_1 = `STUDENT ID: ${Object.keys(result)[i]}, SLEEPY STATE: NOT DROWSY \n`
            }
            text = text.concat(text_1);
            console.log(text);
        }
        document.getElementById("student_summary").textContent= text;

    }
    var student_summaryUrl = runtime.handlerUrl(element, "student_summary_update")
    var interval = window.setInterval(function() {
        $.ajax({
            type: "POST",
            url: student_summaryUrl,
            data: JSON.stringify({"hello": "world"}),
            success: student_summary
        }); 
    }, 100)

    let stop_button = document.getElementById("stop_button");    
    stop_button.addEventListener("click", function(){
        clearInterval(interval);
    })
}