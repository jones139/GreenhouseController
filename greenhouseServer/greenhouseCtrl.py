#
# sbsCtrl.py - generic functions to control the SBS
#
# Graham Jones, CfAI Durham University, 2021
#
import subprocess
import multiprocessing
import threading
import sys
import time
import json
import math
import datetime
import logging

import sbsCfg
import monitorDaemon
import flowDaemon
import waterCtrl
#import cameraDaemon

class GreenhouseCtrl:
    statusObj = { 'msg': '---'}

    def __init__(self,configFname = "sbscfg.json"):
        print("greenhouseCtrl.__init__(%s)" % configFname)
        self.cfg = sbsCfg.loadConfig(configFname)
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("GreenhouseCtrl.__init__()")

        
        self.waterCtrl = waterCtrl.WaterCtrlDaemon(self.cfg,debug=self.cfg['debug'])
        self.waterCtrl.start()
        self.monitorDaemon = monitorDaemon.MonitorDaemon(self.cfg, debug=False)
        self.monitorDaemon.start()
        self.flowDaemon = flowDaemon.FlowDaemon(self.cfg, debug=False)
        self.flowDaemon.start()


    def stop(self):
        """ Shutdown the various daemon processes / threads nicely """
        self.monitorDaemon.stop()
        self.flowDaemon.stop()
        self.waterCtrl.stop()


    def getStatus(self):
        ''' Populates the status object with the latest photodiode
        and temperature data, and returns the current status object '''
        self.statusObj['monitorData'] = self.monitorDaemon.getData()
        self.statusObj['waterCtrl'] = self.waterCtrl.getStatus()
        self.statusObj['waterStatus'] = self.flowDaemon.getWaterStatus()
        return self.statusObj

    def getConfig(self):
        ''' Return the current confinguration object.
        '''
        return self.cfg

    def setOpMode(self, opMode):
        return self.waterCtrl.setOpMode(opMode)

    def setOnSecs(self, onSecs):
        return self.waterCtrl.setOnSecs(onSecs)

    def setCycleSecs(self, cycleSecs):
        return self.waterCtrl.setCycleSecs(cycleSecs)

    def setSetpoint(self, setpoint):
        return self.waterCtrl.setSetpoint(setpoint)
    
    def setKp(self, Kp):
        return self.waterCtrl.setKp(Kp)
    def setKi(self, Ki):
        return self.waterCtrl.setKi(Ki)
    def setKd(self, Kd):
        return self.waterCtrl.setKd(Kd)
    def setLightThresh(self, lightThresh):
        return self.waterCtrl.setLightThresh(lightThresh)
    
        
if __name__ == "__main__":
    print("greenhouseCtrl.__main__()")

    ctrl = GreenhouseCtrl()

