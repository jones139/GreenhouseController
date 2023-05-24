#!/usr/bin/python3

# Interface to serial (Arduino) based interface to analogue soil moisture meters
# based on SBS K-Mirror Interface

# 11/04/2023 GJ Updated to use firmata protocol so microcontroller can just run
#               the standard firmata firmware.

import os
import sys
import time
import datetime
import logging
import tzlocal
import soilSerial

if __name__=="__main__":
    print("soilSerLogger.main()")

    cfgObj={
        "logName": "soilSerLogger.csv",
        "logInterval": 60,
        "soilSerialDevice": "/dev/ttyUSB0"
    }

    if (os.path.exists(cfgObj['logName'])):
        logf = open(cfgObj['logName'],'a')
    else:
        logf = open(cfgObj['logName'],'w')
        logf.write("tstamp, time, A0, A1, A2, A3\n")
        logf.flush()

    print("Connecting to Serial Device...")
    soil = soilSerial.SoilSerial(cfgObj, debug=True)
    print("Logging to file: %s....." % cfgObj['logName'])
    try:
        while(True):
            soilVals = soil.getStatus()
            tnow = time.time()
            local_timezone = tzlocal.get_localzone() # get pytz timezone
            #tstr = datetime.datetime.utcfromtimestamp(tnow).strftime('%Y%m%d%H%M%S')
            tstr = datetime.datetime.fromtimestamp(tnow, local_timezone).strftime('%Y%m%d%H%M%S')
            logf.write("%d, %s, %.3f, %.3f, %.3f, %.3f\n" %\
                       (tnow, tstr,
                        soilVals[0], soilVals[1], soilVals[2], soilVals[3]))
            logf.flush()
            sys.stdout.write("%d, %s, %.3f, %.3f, %.3f, %.3f\r" %\
                       (tnow, tstr,
                        soilVals[0], soilVals[1], soilVals[2], soilVals[3]))
            sys.stdout.flush()
            time.sleep(cfgObj['logInterval'])
    finally:
        print("finally....")
        logf.close()


