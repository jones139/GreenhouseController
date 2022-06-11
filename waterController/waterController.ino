/**
 * This file is part of waterController.
 *
 * WaterController is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * WaterController  is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with WaterController. If not, see <https://www.gnu.org/licenses/>.
 *
 * Copyright Graham Jones 2022 (graham@openseizuredetector.org.uk)
 *
 */


#include "waterController.h"
#include <Arduino_FreeRTOS.h>
#include <EEPROM.h>

void TaskWaterController( void *pvParameters );
void TaskCommandInterpreter( void *pvParameters );

int onSecs;
int cycleSecs;
int debug;


void printString(int i) {
  char buffer[125];
  Serial.print(strcpy_P(buffer, (char *)pgm_read_word(&(string_table[i]))));
}


int parseCmd(String cmdLine, String *key,String *value) {
  int equalsPos;
  equalsPos = cmdLine.indexOf('=');
  if (equalsPos==-1) {
    *key=cmdLine;
    *value="";
  }
  else {
    *key=cmdLine.substring(0,equalsPos);
    *value=cmdLine.substring(equalsPos+1);
  }
  return(equalsPos);
}

void TaskCommandInterpreter(void *pvParameters)
{
  String readString;
  String k,v;
      readString = "";

  ////////////////////////////////////////////////
  // respond to commands from serial.
  ////////////////////////////////////////////////
  for (;;)  {

    while (Serial.available()) {
      if (Serial.available() > 0) {
	char c = Serial.read();
	Serial.print(c);
	readString += c;
      }
    }
  
    if(readString[readString.length()-1]=='\n') {
      Serial.println (readString);
      parseCmd(readString, &k,&v);
      k.trim();
      if (debug) Serial.print("parseCmd k=");
      if (debug) Serial.print(k);
      if (debug) Serial.print(". v=");
      if (debug) Serial.print(v);
      if (debug) Serial.println(".");
      
      // If no value specified we return the parameter value
      //
      if (v=="") {
	if (k=="CYCLE_SECS") {
	  Serial.print("CYCLE_SECS=");
	  Serial.println(cycleSecs);
	} else if (k=="ON_SECS") {
	  Serial.print("ON_SECS=");
	  Serial.println(onSecs);
	} else if (k=="DEBUG") {
	  Serial.print("DEBUG=");
	  Serial.println(debug);
	} else {
	  // Unrecognised Parameter
	  printString(1);
	  Serial.println(k);
	}
      } else {
	if (k=="CYCLE_SECS") {    
	  //Serial.print("Setting CYCLE_SECS=");
	  printString(2);
	  Serial.println(v);
	  if (v.toInt()>onSecs) {
	    cycleSecs = v.toInt();
	    EEPROM.put(EEPROM_CYCLE_ADDR, cycleSecs);
	  }
	  else {
	    //Serial.println("ERROR - must be greater than ON_SECS");
	    printString(3);
	  }
	} else if (k=="ON_SECS") { 
	  Serial.print("Setting ON_SECS=");
	  Serial.println(v);
	  if (v.toInt()<cycleSecs) {
	    onSecs = v.toInt();
	    EEPROM.put(EEPROM_ON_ADDR, onSecs);
	  }
	  else {
	    printString(5);
	    Serial.println();
	    //Serial.println("ERROR  must be less than CYCLE_SECS");
	  }
	} else if (k=="DEBUG") { 
	  Serial.print("Setting DEBUG=");
	  Serial.println(v);
	  debug = v.toInt();
	  EEPROM.put(EEPROM_DEBUG_ADDR, debug);
	} else {
	  Serial.print("Error - unrecognised parameter ");
	  Serial.println(k);
	}
      }
      readString = "";
    }
    
  }
}


void TaskWaterController(void *pvParameters)  // This is a task.
  {
    (void) pvParameters;

  pinMode(VALVE_PIN, OUTPUT);
  //if (debug) Serial.println("TaskWaterController - starting loop");
  for (;;) // A Task shall never return or exit.
  {
    //if (debug) Serial.println("TaskWaterController - WATER ON");
    digitalWrite(VALVE_PIN, HIGH);   
    vTaskDelay( onSecs*1000 / portTICK_PERIOD_MS ); // wait for one second
    //if (debug) Serial.println("TaskWaterController - WATER OFF");
    digitalWrite(VALVE_PIN, LOW);    // turn the LED off by making the voltage LOW
    vTaskDelay( (cycleSecs-onSecs)*1000 / portTICK_PERIOD_MS ); // wait for one second
  }
}

void setup() {
  Serial.begin(115200);
  //Serial.println("WaterController Starting");
  char storedCheckVal;
  EEPROM.get(EEPROM_CHECK_ADDR,storedCheckVal);
  Serial.print("storedCheckVal=");
  Serial.println((uint8_t)storedCheckVal);
  Serial.print("EEPROM_CHECK_VAL=");
  Serial.println(EEPROM_CHECK_VAL);
  if ((uint8_t)storedCheckVal != EEPROM_CHECK_VAL) {
    Serial.println("EEPROM Not Initialised - Initialising from defaults");
    // We have not initialised the EEPROM, so initialise from defaults.
    onSecs = DEFAULT_ON_SECS;
    cycleSecs = DEFAULT_CYCLE_SECS;
    debug = DEFAULT_DEBUG;
    
    EEPROM.put(EEPROM_ON_ADDR, onSecs);
    EEPROM.put(EEPROM_CYCLE_ADDR, cycleSecs);
    EEPROM.put(EEPROM_DEBUG_ADDR, debug);
    EEPROM.put(EEPROM_CHECK_ADDR, EEPROM_CHECK_VAL);
  } else {
    Serial.println("Initialising from EEPROM stored values");
    EEPROM.get(EEPROM_ON_ADDR, onSecs);
    Serial.print("onSecs=");
    Serial.println(onSecs);
    EEPROM.get(EEPROM_CYCLE_ADDR, cycleSecs);
    Serial.print("cycleSecs=");
    Serial.println(cycleSecs);
    if (cycleSecs<onSecs) cycleSecs=onSecs;
    EEPROM.get(EEPROM_DEBUG_ADDR, debug);
    Serial.print("debug=");
    Serial.println(debug);

  }



  // Now set up two tasks to run independently.
  xTaskCreate(
	      TaskWaterController
	      ,  "Water Controller"   // A name just for humans
	      ,  128  // This stack size can be checked & adjusted by reading the Stack Highwater
	      ,  NULL
	      ,  2  // Priority, with 3 (configMAX_PRIORITIES - 1) being the highest, and 0 being the lowest.
	      ,  NULL );
  


  xTaskCreate(
	      TaskCommandInterpreter
	      ,  "Command Interpreter"   // A name just for humans
	      ,  128  // This stack size can be checked & adjusted by reading the Stack Highwater
	      ,  NULL
	      ,  2  // Priority, with 3 (configMAX_PRIORITIES - 1) being the highest, and 0 being the lowest.
	      ,  NULL );
 
}


void loop() {
// Empty - freeRTOS is handling the main loop.
}
