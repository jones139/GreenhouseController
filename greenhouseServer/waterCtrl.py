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
import simple_pid
import dbConn

class _waterCtrlThread(threading.Thread):
    runDaemon = False
    DEBUG = False
    curTime = None
    cycleStartTime = None
    waterStartTime = None
    soilCond = None
    soilRes = None
    setPoint = None
    controlVal = None
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
        dbSetpoint, dbKp, dbKi, dbKd, dbCycleSecs, dbControlVal = self.db.getWaterControlVals()
        self.db.close()
        if (dbSetpoint is None):
            self.setPoint = cfg['setPoint']
        else:
            self.setPoint = dbSetpoint
        if (dbCycleSecs is None):
            self.cycleSecs = cfg['waterCycleSecs']
        else:
            self.cycleSecs = dbCycleSecs
        if (dbKp is None):
            self.Kp = cfg['Kp']
        else:
            self.Kp = dbKp
        if (dbKi is None):
            self.Ki = cfg['Ki']
        else:
            self.Ki = dbKi
        if (dbKd is None):
            self.Kd = cfg['Kd']
        else:
            self.Kd = dbKd
        self.opMode = cfg['opMode']
        self.timeOnLimit = cfg['timeOnLimit']
            
        self.logger.info("_waterCtrlThread.__init__(): cycleSecs=%f, setpoint=%f" % (self.cycleSecs, self.setPoint))
        self.logger.info("_waterCtrlThread.__init__(): opMode=%s, (Kp,Ki,Kd)=(%f,%f,%f)" % (self.opMode, self.Kp, self.Ki, self.Kd))

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
        self.logger.info("waterCtrlThread.run()")
        # re-open db for this thread.
        self.db = dbConn.DbConn(self.dbPath)

        self.pid = simple_pid.PID(self.Kp, self.Ki, self.Kd,
                                  setpoint=self.setPoint,
                                  sample_time=None,
                                  output_limits=(0,self.timeOnLimit))
        
        while self.runThread:
            # Start cycle
            self.cycleStartTime = datetime.datetime.now()
            envData = self.db.getLatestMonitorData()
            self.soilRes = envData[5]
            self.soilCond = 1.0e6 * 1.0/self.soilRes  # micro-condy units
            self.controlVal = self.pid(self.soilCond)
            self.onSecs = self.controlVal
            self.logger.info("soilRes=%d, soilCond=%.1f, setPoint=%.1f, controlVal=%.1f" %
                  (self.soilRes, self.soilCond, self.setPoint, self.controlVal))
            # Write current watering status to db before we change anything.
            self.writeWaterData()
            self.waterOn()
            self.logger.info("waterOn")
            # Wait for time to switch water off.
            dt = datetime.datetime.now()
            while (dt - self.waterOnTime).total_seconds() < self.onSecs:
                time.sleep(0.1)
                dt = datetime.datetime.now()
            self.writeWaterData()
            self.waterOff()
            self.logger.info("waterOff")
            #if (self.DEBUG): print("_waterCtrlThread.run(): waterOff")
            while (dt - self.cycleStartTime).total_seconds() < self.cycleSecs:
                time.sleep(0.1)
                dt = datetime.datetime.now()
            self.logger.info("end of Cycle")
            if (self.DEBUG): print("_waterCtrlThread.run(): end of Cycle")
        self.logger.info("waterCtrlThread.run() - Exiting")
        self.waterOff()

    def stop(self):
        """ Stop the background thread"""
        self.logger.info("Stopping thread")
        self.runThread = False

    def writeWaterData(self):
        self.db = dbConn.DbConn(self.dbPath)
        dt = datetime.datetime.now()
        self.db.writeWaterData(dt, self.waterStatus,
                               self.onSecs,
                               self.cycleSecs,
                               self.controlVal,
                               self.setPoint,
                               self.Kp,
                               self.Ki,
                               self.Kd);
        self.db.close()

    def waterOn(self):
        self.logger.info("waterOn()")
        if (self.DEBUG): print("_waterCtrlThread.waterOn()")
        GPIO.output(self.waterControlPin, GPIO.HIGH)
        self.waterOnTime = datetime.datetime.now()
        self.waterStatus=1
        self.writeWaterData()

    def waterOff(self):
        self.logger.info("waterOff()")
        if (self.DEBUG): print("_waterCtrlThread.waterOff()")
        GPIO.output(self.waterControlPin, GPIO.LOW)
        self.waterStatus=0
        self.writeWaterData()


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
            return("OK")
        else:
            print("waterCtrlDaemon.setOnSecs - ERROR - onSecs must not be more than cycleSecs")
            return("ERROR")

    def setSetpoint(self,setpoint):
        self.logger.info("setpoint=%f" % setpoint)
        self.waterCtrlThread.pid.setpoint = setpoint
        self.waterCtrlThread.setPoint = setpoint
        self.waterCtrlThread.writeWaterData()

    def setGains(self,Kp,Ki,Kd):
        self.logger.info("Kp,Ki,Kd==%f,%f,%f" % (Kp,Ki,Kd))
        self.waterCtrlThread.Kp=Kp
        self.waterCtrlThread.Ki=Ki
        self.waterCtrlThread.Kd=Kd
        self.waterCtrlThread.pid.tunings=(Kp,Ki,Kd)
        self.waterCtrlThread.writeWaterData()
        
    def setKp(self,Kp):
        self.logger.info("Kp==%f" % (Kp))
        self.waterCtrlThread.Kp=Kp
        self.waterCtrlThread.pid.Kp=Kp
        self.waterCtrlThread.writeWaterData()
        
    def setKi(self,Ki):
        self.logger.info("Ki==%f" % (Ki))
        self.waterCtrlThread.Ki=Ki
        self.waterCtrlThread.pid.Ki=Ki
        self.waterCtrlThread.writeWaterData()

    def setKd(self,Kd):
        self.logger.info("Kd==%f" % (Kd))
        self.waterCtrlThread.Kd=Kd
        self.waterCtrlThread.pid.Kd=Kd
        self.waterCtrlThread.writeWaterData()

    def getStatus(self):
        statusObj = {}
        statusObj['onSecs'] = self.waterCtrlThread.onSecs
        statusObj['cycleSecs'] = self.waterCtrlThread.cycleSecs
        statusObj['waterStatus']=self.waterCtrlThread.waterStatus
        statusObj['soilCond']=self.waterCtrlThread.soilCond
        statusObj['soilRes']=self.waterCtrlThread.soilRes
        statusObj['setPoint']=self.waterCtrlThread.pid.setpoint
        statusObj['controlVal']=self.waterCtrlThread.controlVal
        statusObj['Kp']=self.waterCtrlThread.pid.tunings[0]
        statusObj['Ki']=self.waterCtrlThread.pid.tunings[1]
        statusObj['Kd']=self.waterCtrlThread.pid.tunings[2]
        statusObj['Cp']=self.waterCtrlThread.pid.components[0]
        statusObj['Ci']=self.waterCtrlThread.pid.components[1]
        statusObj['Cd']=self.waterCtrlThread.pid.components[2]
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
