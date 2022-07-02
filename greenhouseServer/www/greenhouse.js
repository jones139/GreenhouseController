send_url = function(urlStr) {
    // Send the specified URL to the server, then call the get_settings function.
    $.ajax({url:urlStr,
	    success:function() {
		$("#errorBox").html("OK");
		get_status();
	    },
	    error: function (xhr, ajaxOptions, thrownError) {
		$("#errorBox").html(xhr.status + thrownError);
	    },
	    timeout: 5000
	   });
}

rebootSbs = function(){
    if (confirm('Reboot Controller?')) {
	url = "/rebootSbs";
	send_url(url);
    } else {
	console.log("Not rebooting")
    }   
};

lampOnOff = function(){
   url = "/lampOnOff";
   send_url(url);
};

kMirrorMove = function(){
    newPos = $("#kMirrorMoveTxt").val()
    url = "/kMirrorMoveTo/"+newPos;
    console.log(url);
    send_url(url);
};



function refresh_data(){
      get_status()
};

function refresh_charts(){
      $("#chart1").attr("src","/static/data/chart1.png?"+new Date().getTime());
      $("#chart2").attr("src","/static/data/chart2.png?"+new Date().getTime());
};

function show_error(xhr, ajaxOptions, thrownError) {
    //alert("show_error");
    if (thrownError=="timeout") {
	$("#errorBox").html("WARNING - LOST COMMUNICATIONS WITH CONTROLLER");
	$("#errorBox").addClass("warn");
    }
    
};

getConfig = function() {
    $.ajax({url:"/config",success:onGetConfig,
	   error: show_error
	   });
};

onGetConfig = function(configStr) {
    configObj = JSON.parse(configStr);
    //alert(configStr);
}

function get_status() {
    //alert("get_status");
    $.ajax({url:"/status",
	    success:populate_form,
	    error: show_error,
	    timeout: 5000
	   });

    
};

function populate_form(statusStr) {
    var valTxt;
    var lblTxt;
    var tmpStr;
    var cfg;
    //$("#msgBox").html(statusStr);
    $("#errorBox").html("OK");
    $("#errorBox").removeClass("warn");
    var statusObj = JSON.parse(statusStr);


    // Environment
    //$("#tempTxt").html(statusObj.monitorData.data.temp.toFixed(1) +" degC");
    $("#temp2Txt").html(statusObj.monitorData.data.temp2.toFixed(1) +" degC");
    $("#humidityTxt").html(statusObj.monitorData.data.humidity.toFixed(1) +" %");
    $("#lightTxt").html(statusObj.monitorData.data.light.toFixed(1) +" lux");


    // Watering
    $("#cycleSecsTxt").html(statusObj.waterCtrl.cycleSecs.toFixed(1) +" sec");
    $("#onSecsTxt").html(statusObj.waterCtrl.onSecs.toFixed(1) +" sec");
    if (statusObj.waterCtrl.waterStatus) {
	$("#waterStatusTxt").html("**ON**");
    } else {
	$("#waterStatusTxt").html("OFF");
    }
    
    $("#msgBox").html(statusObj.msg); // + JSON.stringify(configObj));
   
    //$("#camImg").attr("src","/static/camImg.jpg?" + new Date().getTime());
};

$(document).ready(function(){
    $("#rebootSbsBtn").click(rebootSbs);


    configObj = null;
    getConfig();
    setInterval("refresh_data();",1000);
    setInterval("refresh_charts();",10*1000);
    get_status();

});
