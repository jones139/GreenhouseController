#!/usr/bin/python3

# Greenhouse water controller interface
# Assumes water control valve is actuated by GPIO pin
# cfg['waterControlPin']

import os
import time
import datetime
import threading
import logging
import RPi.GPIO as GPIO
import dbConn

class _waterCtrlThread(threading.Thread):
    runDaemon = False
    DEBUG = False
    curTime = None
    cycleStartTime = None
    waterStartTime = None
    waterStatus=0
    def __init__(self, cfg, debug = False):
        print("_waterCtrlThread.__init__()")
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])
        self.waterControlPin = cfg['waterControlPin']
        threading.Thread.__init__(self)
        self.dbPath = os.path.join(cfg['dataFolder'],cfg['dbFname'])

        # Initialise settings from database, or config file if DB values not set
        self.db = dbConn.DbConn(self.dbPath)
        dbOnSecs, dbCycleSecs = self.db.getWaterControlVals()
        self.db.close()
        if (dbOnSecs is None):
            self.onSecs = cfg['waterOnSecs']
        else:
            self.onSecs = dbOnSecs
        if (dbCycleSecs is None):
            self.cycleSecs = cfg['waterCycleSecs']
        else:
            self.cycleSecs = dbCycleSecs

        self.logger.info("_waterCtrlThread.__init__(): onSecs=%f, cycleSecs=%f" % (self.onSecs, self.cycleSecs))

        self.DEBUG = debug
        self.runThread = True
        self.curTime = datetime.datetime.now()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.waterControlPin], GPIO.OUT)
        
    def run(self):
        """
        The main loop of the thread  repeatedly checks to see if it is time
        to switch the water on or off.
        """
        print("waterCtrlThread.run()")
        # re-open db for this thread.
        self.db = dbConn.DbConn(self.dbPath)

        while self.runThread:
            # Start cycle
            self.cycleStartTime = datetime.datetime.now()
            # Write current watering status to db before we change anything.
            dt = datetime.datetime.now()
            self.db.writeWaterData(dt, self.waterStatus, self.onSecs, self.cycleSecs);
            self.waterOn()
            self.logger.info("_waterCtrlThread.run(): waterOn")
            #if (self.DEBUG): print("_waterCtrlThread.run(): waterOn")
            dt = datetime.datetime.now()
            self.db.writeWaterData(dt, self.waterStatus, self.onSecs, self.cycleSecs);
            # Wait for time to switch water off.
            while (dt - self.waterOnTime).total_seconds() < self.onSecs:
                time.sleep(0.1)
                dt = datetime.datetime.now()
            dt = datetime.datetime.now()
            self.db.writeWaterData(dt, self.waterStatus, self.onSecs, self.cycleSecs);
            self.waterOff()
            dt = datetime.datetime.now()
            self.db.writeWaterData(dt, self.waterStatus, self.onSecs, self.cycleSecs);
            self.logger.info("_waterCtrlThread.run(): waterOff")
            #if (self.DEBUG): print("_waterCtrlThread.run(): waterOff")
            while (dt - self.cycleStartTime).total_seconds() < self.cycleSecs:
                time.sleep(0.1)
                dt = datetime.datetime.now()
            self.logger.info("_waterCtrlThread.run(): end of Cycle")
            if (self.DEBUG): print("_waterCtrlThread.run(): end of Cycle")
        print("waterCtrlThread.run() - Exiting")
        self.waterOff()

    def stop(self):
        """ Stop the background thread"""
        print("_waterCtrlThread.stop() - Stopping thread")
        self.runThread = False

    def waterOn(self):
        self.logger.info("_waterCtrlThread.waterOn()")
        if (self.DEBUG): print("_waterCtrlThread.waterOn()")
        GPIO.output(self.waterControlPin, GPIO.HIGH)
        self.waterOnTime = datetime.datetime.now()
        self.waterStatus=1

    def waterOff(self):
        self.logger.info("_waterCtrlThread.waterOff()")
        if (self.DEBUG): print("_waterCtrlThread.waterOff()")
        GPIO.output(self.waterControlPin, GPIO.LOW)
        self.waterStatus=0

class WaterCtrlDaemon():
    '''
    Start a thread that runs in the background
    '''
    DEBUG = False
    waterCtrlThread = None

    def __init__(self,cfgObj, debug=False):
        '''
        Initialise the class using data provided in object cfgObj
        '''
        print("waterCtrlDaemon.__init__()")
        self.cfg = cfgObj
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("WaterCtrlDaemon.__init__()")
        self.waterCtrlThread = _waterCtrlThread(cfgObj, debug)
        self.waterCtrlThread.daemon = True


    def start(self):
        ''' Start the background process
        '''
        print("waterCtrlDaemon.start()")
        self.logger.info("WaterCtrlDaemon.start()")
        self.waterCtrlThread.start()

    def stop(self):
        ''' Stop the background process
        '''
        print("waterCtrlDaemon.stop()")
        self.logger.info("WaterCtrlDaemon.stop()")
        self.waterCtrlThread.stop()

    def setOnSecs(self, onSecs):
        print("waterCtrlDaemon.setOnSecs(%f)" % onSecs)
        self.logger.info("WaterCtrlDaemon.stop(%f)" % onSecs)
        if (self.waterCtrlThread.cycleSecs >= onSecs):
            self.waterCtrlThread.onSecs = onSecs
            #dt = datetime.datetime.now()
            #self.db.writeWaterData(dt, self.waterStatus, self.onSecs, self.cycleSecs);
            return("OK")
        else:
            print("waterCtrlDaemon.setOnSecs - ERROR - onSecs must not be more than cycleSecs")
            return("ERROR")

    def getStatus(self):
        statusObj = {}
        statusObj['onSecs'] = self.waterCtrlThread.onSecs
        statusObj['cycleSecs'] = self.waterCtrlThread.cycleSecs
        statusObj['waterStatus']=self.waterCtrlThread.waterStatus
        return statusObj
        
if __name__ == '__main__':
    print("waterCtrl.__main__()")

    cfgObj = {
        "logName": "waterCtrl",
        "waterControlPin": 22,
        "waterMonitorPin": 23,
        "waterCycleSecs": 5,
        "waterOnSecs": 2,
        }

    waterCtrl = WaterCtrlDaemon(cfgObj, debug=True)
    waterCtrl.start()
    time.sleep(20)
    waterCtrl.stop()
    time.sleep(10)
    print("exiting")
