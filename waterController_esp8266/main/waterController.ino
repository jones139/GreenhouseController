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

// A function at address zero is the same as resetting the microcontroller.
void (*reset)(void) = 0; 

/**
 * getString(i, buffer)
 * copy string number I into memory at address buffer.
 * param int i - the index in string_table[] of the string to be retrieved.
 * param char *buffer - the address of the memory area to store the string.
 *  NOTE - NO checking is performed on the validity of the memory area buffer
 *    - you must make sure there is enough space for the string!!
 */
void getString(int i, char *buffer) {
  strcpy_P(buffer, (char *)pgm_read_word(&(string_table[i])));
}


void printString(int i) {
  char buffer[125];
  getString(i, buffer);
  Serial.print(buffer);
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
  char buffer[125];
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
	  getString(CYCLE_SECS_STR, buffer);
	  Serial.print(buffer);
	  Serial.print("=");
	  Serial.println(cycleSecs);
	} else if (k=="ON_SECS") {
	  getString(ON_SECS_STR, buffer);
	  Serial.print(buffer);
	  Serial.print("=");
	  Serial.println(onSecs);
	} else if (k=="DEBUG") {
	  Serial.print("DEBUG=");
	  Serial.println(debug);
	} else if (k=="RESET") {
	  Serial.print("Resetting....");
	  reset();
	} else {
	  // Unrecognised Parameter
	  printString(1);
	  Serial.println(k);
	}
      } else {
	if (k=="CYCLE_SECS") {    
	  printString(SETTING_STR);
	  printString(CYCLE_SECS_STR);
	  Serial.print("=");
	  Serial.println(v);
	  if (v.toInt()>onSecs) {
	    cycleSecs = v.toInt();
	    EEPROM.put(EEPROM_CYCLE_ADDR, cycleSecs);
	  }
	  else {
	    printString(CYCLE_SECS_ERR_STR);
	  }
	} else if (k=="ON_SECS") { 
	  printString(SETTING_STR);
	  printString(ON_SECS_STR);
	  Serial.print("=");
	  Serial.println(v);
	  if (v.toInt()<cycleSecs) {
	    onSecs = v.toInt();
	    EEPROM.put(EEPROM_ON_ADDR, onSecs);
	  }
	  else {
	    printString(ON_SECS_ERR_STR);
	    Serial.println();
	  }
	} else if (k=="DEBUG") { 
	  Serial.print("Setting DEBUG=");
	  Serial.println(v);
	  debug = v.toInt();
	  EEPROM.put(EEPROM_DEBUG_ADDR, debug);
	} else {
	  printString(UNREC_PARAM_ERR_STR);
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
    // Switch on the water at teh start of the cycle
    if (debug) Serial.println("WATER ON");
    digitalWrite(VALVE_PIN, HIGH);
    // We only delay for 1 sec to avoid integer overflow on number of
    // ticks to delay.
    for (int i=0; i<onSecs; i++) {
      vTaskDelay( 1000 / portTICK_PERIOD_MS );
    }
    if (debug) Serial.println("WATER OFF");
    digitalWrite(VALVE_PIN, LOW);    
    // Now wait for the rest of the cycle with the water off.
    // Again we only delay for 1 sec to avoid integer overruns.
    for (int i=0; i<(cycleSecs-onSecs); i++) {
      vTaskDelay( 1000 / portTICK_PERIOD_MS );
    }
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
    printString(ON_SECS_STR);
    Serial.print("=");
    Serial.println(onSecs);
    EEPROM.get(EEPROM_CYCLE_ADDR, cycleSecs);
    printString(CYCLE_SECS_STR);
    Serial.print("=");
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
	      ,  128  // stack size
	      ,  NULL
	      ,  2  
	      ,  NULL );
  


  xTaskCreate(
	      TaskCommandInterpreter
	      ,  "Command Interpreter"   // A name just for humans
	      ,  256  // stack size
	      ,  NULL
	      ,  2  // Priority
	      ,  NULL );
 
}


void loop() {
// Empty - freeRTOS is handling the main loop.
}
