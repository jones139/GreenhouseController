//#define USE_CAMERA 1

#include <dhtnew.h>
#include <BH1750.h>
#include <SHT31.h>

#ifndef LED_BUILTIN
#define LED_BUILTIN 2 //4
#endif

#define DHT_PIN 15
#define SCL_PIN 22 // 12
#define SDA_PIN 21 // 13
#define WATER_PIN 14

#define MEAS_INTERVAL 5  // Seconds between measurements.
#define LOG_INTERVAL 60 // Minutes between logging data to history.
#define HISTORY_LENGTH 7 // Days we retain the history.

struct monitorDataStruct {
  float temp;
  float tempStd;
  float humidity;
  float humidityStd;
  float light;
  float lightStd;
};


// Global variables
extern DHTNEW dhtSensor;
extern SHT31 shtSensor;
extern BH1750 lightMeter;
extern struct monitorDataStruct monitorData;
extern struct monitorDataStruct measArr[LOG_INTERVAL*60/MEAS_INTERVAL];
extern struct monitorDataStruct histArr[HISTORY_LENGTH*24*60/LOG_INTERVAL];
extern int measArrPosn;
extern int histArrPosn;
extern bool pauseLogging;   // Flag to pause reading of sensors while we are doing camera operations to try to stop the DHT22 crashing.
