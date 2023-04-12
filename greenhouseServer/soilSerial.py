#!/usr/bin/python3

# Interface to serial (Arduino) based interface to analogue soil moisture meters
# based on SBS K-Mirror Interface

# 11/04/2023 GJ Updated to use firmata protocol so microcontroller can just run
#               the standard firmata firmware.

import pyfirmata
import time
import serial
import logging


class SoilSerial:
    comms = None
    def __init__(self,cfg, debug=False):
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])
        port = self.cfg['soilSerialDevice']
        print("SoilSerial.__init__(%s)" % port)
        self.debug=debug
        try:
            board = pyfirmata.Arduino(port)
            it = pyfirmata.util.Iterator(board)
            it.start()
            print("Serial communications opened ok")
            self.logger.info("Serial communications opened ok")
            self.pins = []
            for pinNo in range(0,4):
                pin = board.analog[pinNo]
                pin.enable_reporting()
                print(pin, pin.read())
                self.pins.append(pin)
                
            self.comms = True    
        except serial.serialutil.SerialException as ex:
            print("ERROR:  SoilSerial.__init__: Failed to Open Communications to port %s" % port)
            self.logger.error("ERROR:  SoilSerial.__init__: Failed to Open Communications to port %s" % port)
            print(ex)
            self.logger.error(ex)
            self.comms = None
            #raise(ex)



    def getStatus(self):
        #print("kmCtrl.getStatus()")
        statusLst = []
        if (self.comms is None):
            print("SoilSerial - ERROR - communications not established")
        else:
            for pin in self.pins:
                val = pin.read()
                print(pin, val)
                statusLst.append(val)
        return(statusLst)

        
        
    def close(self):
        if (self.comms is None):
            print("SoilSerial.close() - comms is None - not doing anything")
            self.logger.info("SoilSerial.close() - comms is None - not doing anything")
        else:
            # FIXME - do we need to stop the iterator?
            self.logger.info("SoilSerial.close()")


if __name__=="__main__":
    print("soilSerial.main()")

    cfgObj={
        "logName": "soilSerial",
        "soilSerialDevice": "/dev/ttyUSB0"
    }

    soil = SoilSerial(cfgObj, debug=True)
    print(soil.getStatus())


