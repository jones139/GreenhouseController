const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
  </style>
</head>
<body>
  <h2>Greenhouse Monitor</h2>
  <div>
  <ul>
  <li>Temperature <span id="tempSpan">---</span> degC</li>
  <li>Humidity <span id="humiditySpan">---</span> pc</li>
  <li>Light Level <span id="lightSpan">---</span> lx</li>
  </ul>
  </div>
  <div id="messages">messages</div>
<script>
setInterval(getStatus,2000);

async function getStatus() {
  fetch("/status")
  .then(function(response) {
      if (!response.ok) {
        throw new Error("HTTP error, status = " + response.status);
      }
      jsonObj = response.json();
      return jsonObj;
    })
  .then(function(json) {
    console.log("json=",json);
    document.getElementById("tempSpan").innerHTML = json.temp;
    document.getElementById("humiditySpan").innerHTML = json.humidity;
    document.getElementById("lightSpan").innerHTML = json.light;      
  })
  .catch(function(error) {
      document.getElementById("messages").innerHtml = 'Error: ' + error.message
  });  
}
</script>
</body>
</html>
)rawliteral";
