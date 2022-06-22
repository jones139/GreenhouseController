#!/usr/bin/env python
import os
import time
import datetime
import threading
import logging

import sbsCfg


class _tempThread(threading.Thread):
    rootPath = '/sys/bus/w1/devices/'
    fname = 'w1_slave'
    runDaemon = False
    DEBUG = False
    curTime = None
    curTemps = []
    def __init__(self, cfg, debug = False):
        print("_tempThread.__init__()")
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("_tempThread.__init__()")
        threading.Thread.__init__(self)
        self.DEBUG = debug
        self.runThread = True
        self.outFname = cfg['temps']['tempFname']
        print("_tempThread._init__: outFname=%s" % self.outFname)
        self.devices = []
        for d in cfg['temps']['tempDevices']:
            self.devices.append(d['addr'])
        print("_tempThread._init__: devices =")
        self.curTemps = []
        for d in self.devices:
            print(d)
            self.curTemps.append(-300)
        self.curTime = datetime.datetime.now()


    def run(self):
        """ The main loop of the thread  repeatedly scans all of the 
        specified devices on the 1-wire bus, and saves the result to  a file
        """
        print("tempThread.run()")
        outFile = open(self.outFname,'w')
        while self.runThread:
            dt = datetime.datetime.now()
            outFile.seek(0)  # Return to start of file
            outFile.write(dt.strftime("%Y-%m-%d %H:%M:%S"))
            temps = []
            for id in self.devices:
                if (self.DEBUG): print(id)
                currTemp = self.readDevice(id)
                if (self.DEBUG): print(id, currTemp)
                outFile.write(","+'{:.3f}'.format(currTemp))
                temps.append(float(currTemp))
            self.curTime = dt
            self.curTemps = temps
            if (self.DEBUG): print(self.curTime, self.curTemps)
            self.logger.debug(self.curTemps)
            outFile.write("\n")
            outFile.flush()
            time.sleep(0.01)
            #time.sleep(1.0)
        outFile.close()
        print("tempThread.run() - Exiting")

    def stop(self):
        """ Stop the background thread"""
        print("_tempThread.stop() - Stopping thread")
        self.runThread = False

    def getTemps(self):
        """ Return an object containing the current time and list of current
        temperature readings.
        """
        retObj = {}
        retObj['time'] =self.curTime
        retObj['temps'] = self.curTemps
        if (self.DEBUG): print(retObj)
        return(retObj)
            
    def readDevice(self, id):
        """ Attemptot read the value of temperature device id off the bus
        and return the temperature in degC.
        Returns -300 if there is an error
        """
        try:
            tempStr = ''
            fpath = os.path.join(self.rootPath,id,self.fname)
            if (self.DEBUG): print("fpath=%s" %fpath)
            f = open(fpath,'r')
            line = f.readline()
            crc = line.rsplit(' ',1)
            crc = crc[1].strip()
            if (self.DEBUG): print("line=%s, crc=%s" % (line,crc))
            if (crc=='YES'):
                line = f.readline()
                tempStr = line.rsplit('t=',1)[1]
                if (self.DEBUG): print("line=%s, tempStr=%s" % (line, tempStr))
            else:
                tempStr = '-301000'
            f.close
            return(int(tempStr)/1000.)
        except Exception as e:
            self.logger.info("_tempThread.readDevice(%s) Exception" % id)
            self.logger.info(e)
            if (self.DEBUG): print("Exception running getTemp", e)
            return -300.



class TempDaemon():
    '''
    Start a thread that runs in the background to repeatedly poll DS18B20
    temperature sensors on the 1-wire bus that is accessed at
    /sys/bus/w1/devies
    Saves the measured temperatures to a file.
    The devies to be monitored, their order and the output filename are
    specified in a configuration object that is passed on initialisation of
    the class.
    '''
    DEBUG = False
    devices = {}
    tempThread = None

    def __init__(self,cfgObj, debug=False):
        '''
        Initialise the class using data provided in object cfgObj
        '''
        print("tempDaemon.__init__()")
        self.cfg = cfgObj
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("TempDaemon.__init__()")
        self.tempThread = _tempThread(cfgObj, debug)
        self.tempThread.daemon = True


    def start(self):
        ''' Start the background process to monitor temperatures
        '''
        print("tempDaemon.start()")
        self.logger.info("TempDaemon.start()")
        self.tempThread.start()

    def stop(self):
        ''' Stop the background process to monitor temperatures
        '''
        print("tempDaemon.stop()")
        self.logger.info("TempDaemon.stop()")
        self.tempThread.stop()

    def getTemps(self):
        retObj = self.tempThread.getTemps()
        return retObj

    
if __name__ == '__main__':
    print("sbsSvr.__main__()")

    cfgObj = {
        "tempFname": "/tmp/temps.csv",
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

    cfgObj = sbsCfg.loadConfig("sbscfg.json")
    print(cfgObj['temps'])

    tempMon = TempDaemon(cfgObj['temps'], debug=False)
    tempMon.start()
    time.sleep(20)
    tempMon.stop()
    time.sleep(10)
    print("exiting")


 
