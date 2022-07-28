#!/usr/bin/env python

# Based on https://medium.com/@rxseger/interrupt-driven-i-o-on-raspberry-pi-3-with-leds-and-pushbuttons-rising-falling-edge-detection-36c14e640fef
# interrupt-based GPIO example using LEDs and pushbuttons

import os
import time
import datetime
import threading
import logging
import sqlite3

import RPi.GPIO as GPIO
import sbsCfg


class _flowThread(threading.Thread):
    """ Background process that will calculate the flow rate every
    second based on the pulse count collected from an interrupt driven
    routine.
    """
    rate_delay = 1.0 # sec
    loop_delay = 0.01 # sec

    def __init__(self, cfg, debug=False):
        print("_flowThread.__init__()")
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])

        threading.Thread.__init__(self)
        self.DEBUG = debug
        self.dbPath = os.path.join(cfg['dataFolder'],cfg['dbFname'])
        self.runThread = True
        self.count = 0
        self.flowEncPin = cfg['waterMonitorPin']
        self.curTime = datetime.datetime.now()
        self.curFlow = -1
        print("flowEncPin=%d" %
              (self.flowEncPin))

        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.flowEncPin], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.flowEncPin, GPIO.BOTH,
                              self.waterChangeDetect)

        if GPIO.input(self.flowEncPin):
            print("WATER_ON_DETECTED")
            self.waterStatus = 1
        else:
            print("WATER_OFF_DETECTED")
            self.waterStatus = 0
        self.writeToDb(self.waterStatus,"flowDaemon Initialised")
            

    def writeToDb(self, waterStatus, eventTxt=""):
        db = sqlite3.connect(self.dbPath)
        # Note - triple quote for multi line string
        cur = db.cursor()
        data_date = datetime.datetime.now()
        cur.execute(
            """insert into 'system'
            ('data_date', 'measuredWaterStatus', 'systemEvent')
            values (?, ?, ?);""",
            (data_date, waterStatus, eventTxt)
        )

        db.commit()

            

    def waterChangeDetect(self, pin):
        ''' Interupt driven routine to detect changes in water state.'''
        if (pin == self.flowEncPin):
            if GPIO.input(self.flowEncPin):
                print("WATER_ON_DETECTED")
                self.logger.info("WATER_ON_DETECTED")
                self.waterStatus = 1
                self.writeToDb(0,"Water_On")
                self.writeToDb(1,"Water_On")
            else:
                print("WATER_OFF_DETECTED")
                self.logger.info("WATER_OFF_DETECTED")
                self.waterStatus = 0
                self.writeToDb(1,"Water_Off")
                self.writeToDb(0,"Water_Off")
                
    def getWaterStatus(self):
        return self.waterStatus

    def run(self):
        """ Main loop of nhread - every time rate_delay seconds have
        elsapsed, calculates rate, and resets counter.
        """
        started = time.time()
        while self.runThread:
            #print(GPIO.input(self.flowEncPin))
            time.sleep(self.rate_delay)
        self.writeToDb(self.waterStatus,"flowDaemon Stopped")


    def stop(self):
        """ Stop the background thread"""
        print("_flowThread.stop() - Stopping thread")
        self.runThread = False
        GPIO.remove_event_detect(self.flowEncPin)

    def getFlow(self):
        """ Return an object containing the current time and flow rate
        """
        retObj = {}
        retObj['time'] =self.curTime
        retObj['flow'] = self.curFlow
        #print(retObj)
        return(retObj)


class FlowDaemon():
    '''
        Start a thread that runs in the background to repeatedly calculate
        flow rate from accumulated pulses.  Pulse count is incremented using
        inerrupts.
        Saves the measured flow rate to a file.
        The pin the meter is attached to and the output filename are
        specified in a configuration object that is passed on initialisation of
        the class.
        '''
    DEBUG = False
    devices = {}
    flowThread = None

    def __init__(self,cfgObj, debug=False):
        '''
        Initialise the class using data provided in object cfgObj
        '''
        print("flowDaemon.__init__()")
        self.cfg = cfgObj
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("Initialising flow meter")

        self.DEBUG = debug
        self.flowThread = _flowThread(cfgObj, debug)
        self.flowThread.daemon = True


    def start(self):
        ''' Start the background process to monitor flow rate
        '''
        print("flowDaemon.start()")
        self.logger.info("Starting flow meter")
        self.flowThread.start()

    def stop(self):
        ''' Stop the background process to monitor flow rate
        '''
        print("flowDaemon.stop()")
        self.logger.info("Stopping flow meter")
        self.flowThread.stop()

    def getFlow(self):
        retObj = self.flowThread.getFlow()
        return retObj

    def getWaterStatus(self):
        retObj = self.flowThread.getWaterStatus()
        return retObj

if (__name__ == "__main__"):    
    print("flowDaemon.main()")
    cfgObj = {
        "debug": True,
        "logName": "greenhouseSvr",
        "logFolder": "/home/graham/GreenhouseController/greenhouseServer/www/data",
        "dataFolder": "/home/graham/GreenhouseController/greenhouseServer/www/data",
        "dbFname": "greenhouse.db",
        "waterMonitorPin": 23,
    }

    flowThread = _flowThread(cfgObj, True)
    flowThread.writeToDb(0,"offTest")
    flowThread.writeToDb(1,"onTest")

