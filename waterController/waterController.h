#define VALVE_PIN 13

#define DEFAULT_CYCLE_SECS 5  //3600  // 1 hour cycle
#define DEFAULT_ON_SECS 1   //30       // 30 seconds per hour.
#define DEFAULT_DEBUG 1



// EEPROM Adresss to store settings in non-volatile memory
#define EEPROM_CHECK_VAL 170 // 10101010 - we use this value to signify that the EEPROM has been initialised.
#define EEPROM_CHECK_ADDR 0
#define EEPROM_CYCLE_ADDR 1
#define EEPROM_ON_ADDR 6
#define EEPROM_DEBUG_ADDR 11

#include <avr/pgmspace.h>
const char string_0[] PROGMEM = "String 0"; // "String 0" etc are strings to store - change to suit.
const char string_1[] PROGMEM = "ERROR - Unrecognised Parameter ";
const char string_2[] PROGMEM = "Setting CYCLE_SECS=";
const char string_3[] PROGMEM = "ERROR - CYCLE_SECS must be greater than ON_SECS";
const char string_4[] PROGMEM = "Setting ON_SECS=";
const char string_5[] PROGMEM = "ERROR ON_SECS must be less than CYCLE_SECS";


const char *const string_table[] PROGMEM = {string_0, string_1, string_2, string_3, string_4, string_5};

