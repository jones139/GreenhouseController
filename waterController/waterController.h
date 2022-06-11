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
