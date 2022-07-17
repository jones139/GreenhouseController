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


kMirrorMove = function(){
    newPos = $("#kMirrorMoveTxt").val()
    url = "/kMirrorMoveTo/"+newPos;
    console.log(url);
    send_url(url);
};

changeSetpoint = function() {
    newSetpoint = $("#setpointInput").val();
    url = "/setpoint/"+newSetpoint;
    console.log(url);
    send_url(url);
};

changeKp = function() {
    newKp = $("#KpInput").val();
    url = "/Kp/"+newKp;
    console.log(url);
    send_url(url);
};

changeKi = function() {
    newKi = $("#KiInput").val();
    url = "/Ki/"+newKi;
    console.log(url);
    send_url(url);
};

changeKd = function() {
    newKd = $("#KdInput").val();
    url = "/Kd/"+newKd;
    console.log(url);
    send_url(url);
};


function refresh_data(){
      get_status()
};

function refresh_charts(){
      $("#chart1").attr("src","/static/data/chart1.png?"+new Date().getTime());
      $("#chart2").attr("src","/static/data/chart2.png?"+new Date().getTime());
      $("#chart3").attr("src","/static/data/chart3.png?"+new Date().getTime());
      $("#chart4").attr("src","/static/data/chart4.png?"+new Date().getTime());

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
    if (typeof statusObj.monitorData.data != "undefined") {
	//$("#tempTxt").html(statusObj.monitorData.data.temp.toFixed(1) +" degC");
	if (typeof statusObj.monitorData.data.temp2 != "undefined") 
	    $("#temp2Txt").html(statusObj.monitorData.data.temp2.toFixed(1) +" degC");
	if (typeof statusObj.monitorData.data.humidity != "undefined") 
	    $("#humidityTxt").html(statusObj.monitorData.data.humidity.toFixed(1) +" %");
	if (typeof statusObj.monitorData.data.light != "undefined") 
	    $("#lightTxt").html(statusObj.monitorData.data.light.toFixed(1) +" lux");
	if (typeof statusObj.monitorData.data.soil != "undefined") 
	    $("#soilTxt").html(statusObj.monitorData.data.soil.toFixed(0) +" counts (" +
		       (1e6*1.0/statusObj.monitorData.data.soil).toFixed(1) + " uC)");
    }

    // Controller
    $("#condyTxt").html(statusObj.waterCtrl.soilCond.toFixed(1) +" uC");
    $("#setpointTxt").html(statusObj.waterCtrl.setPoint.toFixed(1) +" uC");
    $("#controlValTxt").html(statusObj.waterCtrl.controlVal.toFixed(1)+" sec");
    $("#PIDTxt").html("Gains (P,I,D): ("
		      +statusObj.waterCtrl.Kp.toFixed(2)+", "
		      +statusObj.waterCtrl.Ki.toFixed(2)+", "
		      +statusObj.waterCtrl.Kd.toFixed(2)+")"
		      +"<br/>Contributions: ("
		      +statusObj.waterCtrl.Cp.toFixed(1)+", "
		      +statusObj.waterCtrl.Ci.toFixed(1)+", "
		      +statusObj.waterCtrl.Cd.toFixed(1)+")"
		     );

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
    $("#changeSetpointBtn").click(changeSetpoint);
    $("#changeKpBtn").click(changeKp);
    $("#changeKiBtn").click(changeKi);
    $("#changeKdBtn").click(changeKd);

    configObj = null;
    getConfig();
    setInterval("refresh_data();",1000);
    setInterval("refresh_charts();",10*1000);
    get_status();

});
