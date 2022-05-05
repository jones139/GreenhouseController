/* GreenhouseController
 *  This app is intended to run on an ESP32-CAM device, with some additional hardware connected.     
 *  It provides the following
 *   - camera providing still images via web interface for monitoring the plants.
 *   - logging of temperature and humidity
 *   - logging of light levels
 *   - switching on and off of watering system at specified times.
 *   - monitoring of water flow rate.
 *   
 *   The following GPIO pins shoudl be connected.   Note that using these pins precludes the use of the SD card on the ESP32-CAM board, so do not try
 *    to use the SD card at the same time.
 *    - GPIO 12 : Input/Output: I2C SCL (for GY-302 light sensor module)
 *    - GPIO 13 : Input/Output: I2C SDA (for GY-302 light sensor module) 
 *    - GPIO 15 : Input/Output : DH22 Temperature/Humidity Sensor Data connector
 *    - GPIO 14 : Output : control watering.
 *    - GPIO  2 : Input : flow meter
 *    - GPIO  4 : Output : possible future plant food dosing control (but is also the on board camera flash LED)
 *    
 *    Libraries
 *    Uses DHTNEW library from https://github.com/RobTillaart/DHTNew
 *    BH1750 library from https://github.com/claws/BH1750
 */



#include "esp_camera.h"
#include <WiFi.h>
//#include <dhtnew.h>
#include <Wire.h>
#include <BH1750.h>
#include <SHT31.h>

#define CAMERA_MODEL_AI_THINKER // Has PSRAM
#include "camera_pins.h"

#include "credentials.h"
#include "main.h"

void startCameraServer();

#if CONFIG_FREERTOS_UNICORE
#define ARDUINO_RUNNING_CORE 0
#else
#define ARDUINO_RUNNING_CORE 1
#endif

// Global variables
//DHTNEW dhtSensor(DHT_PIN);
BH1750 lightMeter;
SHT31 shtSensor;

struct monitorDataStruct monitorData;
//struct monitorDataStruct monitorData2;
struct monitorDataStruct measArr[LOG_INTERVAL*60/MEAS_INTERVAL];
struct monitorDataStruct histArr[HISTORY_LENGTH*24*60/LOG_INTERVAL];
int measArrPosn = 0;
int histArrPosn = 0;
bool pauseLogging = 0;


// define two tasks for Blink & AnalogRead
void TaskBlink( void *pvParameters );
void TaskAnalogReadA3( void *pvParameters );


/*--------------------------------------------------*/
/*---------------------- Tasks ---------------------*/
/*--------------------------------------------------*/

void TaskBlink(void *pvParameters)  // This is a task.
{
  (void) pvParameters;
  // initialize digital LED_BUILTIN on pin 13 as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(WATER_PIN, OUTPUT);

  for (;;) // A Task shall never return or exit.
  {
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    digitalWrite(WATER_PIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    vTaskDelay(250);  // one tick delay (15ms) in between reads for stability
    digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
    digitalWrite(WATER_PIN, LOW);    // turn the LED off by making the voltage LOW
    vTaskDelay(1000);  // one tick delay (15ms) in between reads for stability
  }
}


void TaskLogger(void *pvParameters)
{
  (void) pvParameters;
  // DHT Sensor
  //dhtSensor.setDisableIRQ(1);

  //BH1750 Light Sensor and SHT31 Temp/Humitidy Sensors on I2C Bus
  Wire.begin(SCL_PIN, SDA_PIN);
  lightMeter.begin();
  shtSensor.begin(&Wire);

 
  for (;;) // A Task shall never return or exit.
  {
    if (pauseLogging) {
      Serial.println("Logging Paused...");
    }
    if (!pauseLogging)
    {
      //int retVal1 = dhtSensor.read();
      //monitorData2.temp = dhtSensor.getTemperature();
      //monitorData2.humidity = dhtSensor.getHumidity();
      monitorData.temp = shtSensor.getTemperature();
      monitorData.humidity = shtSensor.getHumidity();
      monitorData.light = lightMeter.readLightLevel();
      int retVal2 = shtSensor.read();
      Serial.print("retVal: ");
      //Serial.print(retVal1);
      //Serial.print("/");
      Serial.print(retVal2);
      Serial.print(", temp: ");
      Serial.print(monitorData.temp);
      //Serial.print("/");
      //Serial.print(monitorData2.temp);
      Serial.print(", humidity: ");
      Serial.print(monitorData.humidity);
      //Serial.print("/");
      //Serial.print(monitorData2.humidity);
      Serial.print("%, Light: ");
      Serial.print(monitorData.light);
      Serial.println(" lx");

      if (monitorData.temp == -999) {
        Serial.println("DHT Error - Resetting Device");
        //dhtSensor.reset();
        vTaskDelay(5000);   // Have a long wait after resetting to give things chance to calm down.
      }
  
    }
    //Serial.println("TaskDummy1");
    vTaskDelay(1000);
 
  }
}



void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // Now set up two tasks to run independently.
  xTaskCreatePinnedToCore(
    TaskBlink
    ,  "TaskBlink"   // A name just for humans
    ,  1024  // This stack size can be checked & adjusted by reading the Stack Highwater
    ,  NULL
    ,  2  // Priority, with 3 (configMAX_PRIORITIES - 1) being the highest, and 0 being the lowest.
    ,  NULL 
    ,  ARDUINO_RUNNING_CORE);


  // Now set up two tasks to run independently.
  xTaskCreatePinnedToCore(
    TaskLogger
    ,  "TaskLogger"   // A name just for humans
    ,  1024  // This stack size can be checked & adjusted by reading the Stack Highwater
    ,  NULL
    ,  2  // Priority, with 3 (configMAX_PRIORITIES - 1) being the highest, and 0 being the lowest.
    ,  NULL 
    ,  ARDUINO_RUNNING_CORE);



  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 10;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 5;
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1); // flip it back
    s->set_brightness(s, 1); // up the brightness just a bit
    s->set_saturation(s, -2); // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  s->set_framesize(s, FRAMESIZE_QVGA);

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");


}

void loop() {
  // put your main code here, to run repeatedly:
  
  delay(10000);
}
