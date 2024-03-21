/*********
 * Wifi weather station - records temperature and humidity using
 *      DS18B20 and DHT22 sensors.  Runs on a ESP8266 D1 Mini board.
 *
 * Uses the following libraries:
 *    DallasTemperature https://github.com/milesburton/Arduino-Temperature-Control-Library
 *    OneWire https://github.com/PaulStoffregen/OneWire
 *    DHT Library: https://github.com/adafruit/DHT-sensor-library
 *    Adafruit Unified Sensor Libarry: https://github.com/adafruit/Adafruit_Sensor
 *
 *
 * Based on a couple of examples by Rui Santos
 * https://randomnerdtutorials.com/esp8266-ds18b20-temperature-sensor-web-server-with-arduino-ide/

*********/

#include <ESP8266WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>

#include <ThingSpeak.h>
#include "credentials.h"

// Define which GPIO pins are connected to the sensors.
// NOTE GPIO Pin numbers are not the same as the Board D0, D1 etc. pin numbers.
//     See: https://i0.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/ESP8266-WeMos-D1-Mini-pinout-gpio-pin.png?quality=100&strip=all&ssl=1
#define DHTPIN 4     // Digital pin connected to the DHT sensor - GPIO 4 is D1 on Wemos D1 Mini Board
#define ONEWIREPIN 5 // GPIO Pin of OneWire Bus - GPIO5 is D1 on Wemos D1 Mini board

// Uncomment the type of sensor in use:
//#define DHTTYPE    DHT11     // DHT 11
#define DHTTYPE    DHT22     // DHT 22 (AM2302)
//#define DHTTYPE    DHT21     // DHT 21 (AM2301)

// ThingSpeak information.
#define NUM_FIELDS 2          
#define TEMPERATURE_FIELD 1                      
#define HUMIDITY_FIELD 2                       
#define THING_SPEAK_ADDRESS "api.thingspeak.com"
#define UPLOAD_PERIOD_MS 60000

////////////////////////////////////////////
// Global Variables
DHT dht(DHTPIN, DHTTYPE);

// GPIO where the DS18B20 is connected to
const int oneWireBus = ONEWIREPIN;    // Pin D1 on Wemos D1 Mini
// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(oneWireBus);
// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature dallasSensors(&oneWire);

WiFiClient client;

//////////////////////////////////////////////
void setup() {
  // Start the Serial Monitor
  Serial.begin(115200);
  Serial.println();
  Serial.print( "Connecting to Wi-Fi SSID: " );
  Serial.println(SSID);
  WiFi.begin( SSID , PASSWD );
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay( 500 );
  }
  Serial.println();
  Serial.print("Connected to ");
  Serial.println(SSID);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Start the DS18B20 sensor
  dallasSensors.begin();
  dht.begin();

  ThingSpeak.begin(client);
}

void loop() {
  dallasSensors.requestTemperatures(); 
  float temperatureC = dallasSensors.getTempCByIndex(0);
  Serial.print(temperatureC);
  Serial.println("ºC (dallas)");

  // Read DHT temperature as Celsius (the default)
  float dhtT = dht.readTemperature();
  if (isnan(dhtT)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print (dhtT);
    Serial.println("ºC (DHT)");
  }
  // Read Humidity
  float dhtH = dht.readHumidity();
  // if humidity read failed, don't change h value 
  if (isnan(dhtH)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print (dhtH);
    Serial.println("%RH (DHT)");
  }

  ThingSpeak.setField(TEMPERATURE_FIELD, temperatureC);
  ThingSpeak.setField(HUMIDITY_FIELD, dhtH);
  int httpCode = ThingSpeak.writeFields(THINGSPEAK_CHANNEL_ID, THINGSPEAK_API_KEY);
  if (httpCode == 200) {
    Serial.println("Channel write successful - multiple");
  }
  else {
    Serial.println("Problem writing to channel. HTTP error code " + String(httpCode));
  }



  delay(UPLOAD_PERIOD_MS);
}