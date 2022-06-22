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
    if (confirm('Reboot SBS Controller?')) {
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

kMirrorOn = function(){
   url = "/kMirrorStart";
   send_url(url);
};

kMirrorOff = function(){
   url = "/kMirrorStop";
   send_url(url);
};

kMirrorMove = function(){
    newPos = $("#kMirrorMoveTxt").val()
    url = "/kMirrorMoveTo/"+newPos;
    console.log(url);
    send_url(url);
};


function populateKMirrorSettings(statusObj) {
    //console.log("populateKMirrorSettings: "+statusStr);
    //var statusObj = JSON.parse(statusStr);
    //console.log("cmin="+statusObj.cmin);
    $("#kMirrorMinPosTxt").val(statusObj.cmin);
    $("#kMirrorMaxPosTxt").val(statusObj.cmax);
    $("#kMirrorAccelTxt").val(statusObj.acc);
    $("#kMirrorSpeedTxt").val(statusObj.speed);
    kMirrorSettingsObj = statusObj;
};



kMirrorShowSettings = function() {
    console.log("kMirrorShowSettings");
    $("#kMirrorSettingsDiv").show();
    $.ajax({url:"/kMirrorSettings",success:populateKMirrorSettings,
	   error: show_error
	   });
};

kMirrorUpdateSettings = function() {
    console.log("kMirrorUpdateSettings");
    if ($("#kMirrorMinPosTxt").val() != kMirrorSettingsObj.cmin) {
	url = "/kMirrorSetCMin/"+$("#kMirrorMinPosTxt").val();
	console.log(url);
	send_url(url);
    }
    if ($("#kMirrorMaxPosTxt").val() != kMirrorSettingsObj.cmax) {
	url = "/kMirrorSetCMax/"+$("#kMirrorMaxPosTxt").val();
	console.log(url);
	send_url(url);
    }
    if ($("#kMirrorAccelTxt").val() != kMirrorSettingsObj.acc) {
	url = "/kMirrorSetAcc/"+$("#kMirrorAccelTxt").val();
	console.log(url);
	send_url(url);
    }
    if ($("#kMirrorSpeedTxt").val() != kMirrorSettingsObj.speed) {
	url = "/kMirrorSetSpeed/"+$("#kMirrorSpeedTxt").val();
	console.log(url);
	send_url(url);
    }
    // Repopulate form so we can be sure it has worked.
    $.ajax({url:"/kMirrorSettings",success:populateKMirrorSettings,
	   error: show_error
	   });
    $("#kMirrorSettingsDiv").hide();

}

kMirrorCancelSettings = function() {
    console.log("kMirrorCancelSettings");
    $("#kMirrorSettingsDiv").hide();
    // Restore current settings
    $.ajax({url:"/kMirrorSettings",success:populateKMirrorSettings,
	   error: show_error
	   });
}


  function refresh(){
      $("#chart").attr("src","/static/out.png?"+new Date().getTime());
      get_status()
};

function show_error(xhr, ajaxOptions, thrownError) {
    //alert("show_error");
    if (thrownError=="timeout") {
	$("#errorBox").html("WARNING - LOST COMMUNICATIONS WITH SBS");
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

    // Lamp Status
    if (statusObj.lampOn) {
	$("#lampStatusTxt").html("ON");
	$('#lampOnOffBtn').html("Switch OFF");
    }
    else {
	$("#lampStatusTxt").html("OFF");
	$('#lampOnOffBtn').html("Switch ON");
    }
    $("#lampPowerTxt").html(statusObj.lampPower + " W")
    
    // Interlock Status
    if (statusObj.flowCheck == -1 || statusObj.tempCheck == -1) {
	$("#interlockTxt").html("FAULT");
	$("#interlockLbl").addClass('warn');
	$("#interlockTxt").addClass('warn');
    } else {
	$("#interlockTxt").html("OK");
	$("#interlockLbl").removeClass('warn');
	$("#interlockTxt").removeClass('warn');
    }
    
    if (statusObj.flowCheck == 1 || statusObj.tempCheck == 1) {
	$("#interlockTxt").html("*** TRIP ***");
	$("#interlockLbl").addClass('alarm');
	$("#interlockTxt").addClass('alarm');
	//$('#lampOnOffBtn').prop('disabled', true);
    } else {
	$("#interlockTxt").html("OK");
	$("#interlockLbl").removeClass('alarm');
	$("#interlockTxt").removeClass('alarm');
	$('#lampOnOffBtn').prop('disabled', false);
    }

    /*
    switch(statusObj.kMirror.running) {
    case 1:
	$("#kMirrorStatusTxt").html("Running");
	$("#kMirrorOffBtn").addClass('warn');
	$("#kMirrorMoveBtn").addClass('disabled');
	$("#kMirrorMoveTxt").addClass('disabled');
	break;
    case 0:
	$("#kMirrorStatusTxt").html("Stopped at "+statusObj.kMirror.curpos);
	$("#kMirrorOffBtn").removeClass('warn');
	$("#kMirrorMoveBtn").removeClass('disabled');
	$("#kMirrorMoveTxt").removeClass('disabled');
	//$("#kMirrorMoveTxt").val(statusObj.kMirror.curpos);
	break;
    case -1:
	$("#kMirrorStatusTxt").html("Inactive");
	$("#kMirrorOffBtn").removeClass('warn');
	$("#kMirrorMoveBtn").addClass('disabled');
	$("#kMirrorMoveTxt").addClass('disabled');
    }
    */

    // Photodiode
    $("#photodiodeTxt").html(statusObj.pdVal.toExponential(2) +" A");
    $("#adcTxt").html(statusObj.adcVal.toExponential(2) +" V");

    // Flow Rate
    lblTxt = configObj['flowMtr']['desc'];
    if (configObj['flowMtr']['tripActive'])
	lblTxt = lblTxt + '*';
    $("#coolingFlowLbl").html(lblTxt);
    $("#coolingFlowTxt").html(statusObj.flowRate.toFixed(1) +" l/min");
    tmpStr = "OK";
    $("#flowStatus").removeClass("alarm");
    $("#flowStatus").removeClass("warn");
    
    if (statusObj['flowCheck']>0) {
	$("#flowStatus").html("ABNORMAL");
	$("#flowStatus").addClass("alarm");
    } 
	
    if (statusObj['flowCheck']<0) {
	$("#flowStatus").html("FAULT");
	$("#flowStatus").addClass("warn");
    }
    
    if (configObj['flowMtr']['warnActive']) {
	if (statusObj.flowRate < configObj['flowMtr']['warnLo']) {
	    $("#coolingFlowLbl").addClass('warn');
	    $("#coolingFlowTxt").addClass('warn');
	} else {
	    $("#coolingFlowLbl").removeClass('warn');
	    $("#coolingFlowTxt").removeClass('warn');
	}
    }
    if (configObj['flowMtr']['tripActive']) {
	if (statusObj.flowRate < configObj['flowMtr']['tripLo']) {
	    $("#coolingFlowLbl").addClass('alarm');
	    $("#coolingFlowTxt").addClass('alarm');
	} else {
	    $("#coolingFlowLbl").removeClass('alarm');
	    $("#coolingFlowTxt").removeClass('alarm');
	}
    }

    



    // Temperature
    tmpStr = "OK";
    if (statusObj['tempCheck']>0) tmpStr = "ABNORMAL";
    if (statusObj['tempCheck']<0) tmpStr = "FAULT";
    $("#tempStatus").html(tmpStr);

    var i;
    for (i=0; i<statusObj.tempVals.length; i++) {
	var valIdStr = "#temp"+(i+1)+"Txt";
	var lblIdStr = "#temp"+(i+1)+"Lbl";
	if (configObj) {
	    cfg = configObj['temps']['tempDevices'][i];
	    if (statusObj.tempVals[i] < -273.15)
		valTxt = "----- degC";
	    else
		valTxt = statusObj.tempVals[i].toFixed(1) + " degC ";// + JSON.stringify(cfg);
	    $(valIdStr).html(valTxt);

	    lblTxt = cfg['desc'];
	    if (cfg['tripActive'])
		lblTxt = lblTxt + '*';
	    $(lblIdStr).html(lblTxt)
	    if (cfg['warnActive']) {
		if ((statusObj.tempVals[i] < cfg['warnLo']) ||
		    (statusObj.tempVals[i] > cfg['warnHi'])) {
		    $(valIdStr).addClass('warn');
		    $(lblIdStr).addClass('warn');
		} else {
		    $(valIdStr).removeClass('warn');
		    $(lblIdStr).removeClass('warn');
		}
	    }
	    if (cfg['tripActive']) {
		if ((statusObj.tempVals[i] < cfg['tripLo']) ||
		    (statusObj.tempVals[i] > cfg['tripHi'])) {
		    $(valIdStr).addClass('alarm');
		    $(lblIdStr).addClass('alarm');
		} else {
		    $(valIdStr).removeClass('alarm');
		    $(lblIdStr).removeClass('alarm');
		}
	    }
	}
    }
    
    $("#msgBox").html(statusObj.msg); // + JSON.stringify(configObj));
   
    //$("#camImg").attr("src","/static/camImg.jpg?" + new Date().getTime());
};

$(document).ready(function(){
    $("#rebootSbsBtn").click(rebootSbs);
    $("#lampOnOffBtn").click(lampOnOff);
    //$("#kMirrorOnBtn").click(kMirrorOn);
    //$("#kMirrorOffBtn").click(kMirrorOff);
    //$("#kMirrorMoveBtn").click(kMirrorMove);
    //$("#kMirrorShowSettingsBtn").click(kMirrorShowSettings);
    //$("#kMirrorSettingsSaveBtn").click(kMirrorUpdateSettings);
    //$("#kMirrorSettingsCancelBtn").click(kMirrorCancelSettings);
    //$("#kMirrorSettingsDiv").hide();

    configObj = null;
    getConfig();
    setInterval("refresh();",5000);
    get_status();

});
