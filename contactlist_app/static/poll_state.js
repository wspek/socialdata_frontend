function show_progress(){
    $("#status-progress-bar").show()
    setTimeout(poll_state, 1000)
}

function poll_state(){
    jQuery.ajax({
        url: "poll_state/",
        type: "GET",
        success: function(result){
            set_progress(result);
            if (result["state"] == "SUCCESS") {
                // Redirect? Do something.
            }
            else {
                setTimeout(poll_state, 1000);
            }
        },
        error: function(){
            alert("Alert error!");
        },
    })
}

function set_progress(status){
    var progress = status["progress"];
    $('.progress-bar').css('width', progress+'%').attr('aria-valuenow', progress);
    $('.progress-bar').html(progress+'%');
}

$(document).ready(function(){
    $("#status-progress-bar").hide()

    // poll state of the current task
    $("#submit-id-get_contacts").click(show_progress);
});