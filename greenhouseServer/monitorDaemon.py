#!/usr/bin/env python
import os
import time
import datetime
import threading
import logging
import smbus

import sbsCfg
import sht3x_main
import bh1750

class _monitorThread(threading.Thread):
    LOG_INTERVAL = 10  # sec
    runDaemon = False
    DEBUG = False
    curTime = None
    curData = {}
    dataBuffer = []
    def __init__(self, cfg, debug = False):
        print("_monitorThread.__init__()")
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("_monitorThread.__init__()")
        threading.Thread.__init__(self)
        self.DEBUG = debug
        self.runThread = True
        self.outFname = cfg['monitorFname']
        self.logInterval = cfg['logInterval']
        print("_monitorThread._init__: outFname=%s" % self.outFname)
        self.curData = {}
        self.curTime = datetime.datetime.now()

        if (sht3x_main.init()):
            print("Initialised sht3x sensor");

        self.bus = smbus.SMBus(1)
        self.lightSensor = bh1750.BH1750(self.bus)
    
    def calcMeans(self,buf):
        tempSum = 0.
        humSum = 0.
        lightSum = 0.
        count = 0
        for rec in buf:
            tempSum += rec['temp']
            humSum += rec['humidity']
            lightSum += rec['light']
            count += 1
        tempMean = tempSum / count
        humMean = humSum / count
        lightMean = lightSum / count
        return(tempMean, humMean, lightMean)
        
    def run(self):
        """ The main loop of the thread  repeatedly scans all of the 
        devices and saves the result to  a file
        """
        print("monitorThread.run()")
        outFile = open(self.outFname,'a')
        data = {}
        lastLogTime = datetime.datetime.now()
        while self.runThread:
            dt = datetime.datetime.now()
            tData, hData = sht3x_main.read()
            hum, temp = sht3x_main.calculation(tData,hData)
            light = self.lightSensor.measure_high_res()
            
            data['humidity'] = hum
            data['temp'] = temp
            data['light'] = light
            self.curTime = dt
            self.curData = data
            self.dataBuffer.append(data)
            if (dt.timestamp() - lastLogTime.timestamp())>=self.logInterval:
                (meanTemp, meanHumidity, meanLight) = self.calcMeans(self.dataBuffer)
                #outFile.seek(0)  # Return to start of file
                outFile.write(dt.strftime("%Y-%m-%d %H:%M:%S"))
                outFile.write(", %ld, %.1f, %.1f, %.1f\n" % (
                    self.curTime.timestamp(),
                    meanTemp, meanHumidity, meanLight))
                outFile.flush()
                lastLogTime = dt
                self.dataBuffer = []

            if (self.DEBUG): print(self.curTime, self.curData)
            self.logger.debug(self.curData)
            #time.sleep(0.01)
            time.sleep(1.0)
        outFile.close()
        print("monitorThread.run() - Exiting")

    def stop(self):
        """ Stop the background thread"""
        print("_moitorThread.stop() - Stopping thread")
        self.runThread = False

    def getData(self):
        """ Return an object containing the current time and sensor readings
        """
        retObj = {}
        retObj['time'] =self.curTime.timestamp()
        retObj['data'] = self.curData
        if (self.DEBUG): print(retObj)
        return(retObj)
            


class MonitorDaemon():
    '''
    Start a thread that runs in the background to repeatedly poll 
    the sensors
    Saves the measured readings to a file.
    The devices to be monitored, their order and the output filename are
    specified in a configuration object that is passed on initialisation of
    the class.
    It produces hourly averags of the data which are logged to the file.
    '''
    DEBUG = False
    devices = {}
    tempThread = None

    def __init__(self,cfgObj, debug=False):
        '''
        Initialise the class using data provided in object cfgObj
        '''
        print("MonitorDaemon.__init__()")
        self.cfg = cfgObj
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("TempDaemon.__init__()")
        self.monitorThread = _monitorThread(cfgObj, debug)
        self.monitorThread.daemon = True


    def start(self):
        ''' Start the background process to monitor temperatures
        '''
        print("monitorDaemon.start()")
        self.logger.info("MonitorDaemon.start()")
        self.monitorThread.start()

    def stop(self):
        ''' Stop the background process to monitor temperatures
        '''
        print("monitorDaemon.stop()")
        self.logger.info("MonitorDaemon.stop()")
        self.monitorThread.stop()

    def getData(self):
        retObj = self.monitorThread.getData()
        return retObj

    
if __name__ == '__main__':
    print("sbsSvr.__main__()")

    cfgObj = {
        "logName": "monitorDaemon",
        "monitorFname": "/tmp/temps.csv",
        "tempIds" : [
	    "28-0300a279514b",
            "28-0300a279731d",
	    "28-0300a279797a",
	    "28-0300a2799892",
	    "28-0300a279b55d",
	    "28-0300a279b58f",
	    "28-0300a279baf5",
	    "28-0300a279c631",
	    "28-0300a279de5e",
	    "28-0300a279e62d",
	],
        }

    #cfgObj = sbsCfg.loadConfig("sbscfg.json")
    #print(cfgObj['temps'])

    mon = MonitorDaemon(cfgObj, debug=True)
    mon.start()
    time.sleep(20)
    mon.stop()
    time.sleep(10)
    print("exiting")


 
