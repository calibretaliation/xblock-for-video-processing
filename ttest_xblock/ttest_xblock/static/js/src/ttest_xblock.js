/* Javascript for TestXBlock. */
function TestXBlock(runtime, element) {

    function updateCount(result) {
        $('.count', element).text(result.count);
    }
    function stream(result) {
        $(".image", element).attr("src", result.streaming);
    }

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');
    var streamUrl = runtime.handlerUrl(element, 'stream');
    $('p', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"hello": "world"}),
            success: updateCount
        });
    });

    $(function (eventObject) {
        $.ajax({
            type: "POST",
            url: streamUrl,
            data: JSON.stringify({"hello": "world"}),
            success: stream
        });
    });
}
