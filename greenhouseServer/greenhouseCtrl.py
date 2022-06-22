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

        
        self.waterCtrl = waterCtrl.WaterCtrl(self.cfg)
        self.monitorDaemon = monitorDaemon.MonitorDaemon(self.cfg, debug=False)
        self.monitorDaemon.start()
        self.flowDaemon = flowDaemon.FlowDaemon(self.cfg, debug=False)
        self.flowDaemon.start()


    def stop(self):
        """ Shutdown the various daemon processes / threads nicely """
        self.monitorDaemon.stop()
        self.flowDaemon.stop()



    def getStatus(self):
        ''' Populates the status object with the latest photodiode
        and temperature data, and returns the current status object '''
        self.statusObj['monitorData'] = self.monitorDaemon.getData()
        #self.statusObj['flowRate'] = self.getCoolingFlow()['flow']
        return self.statusObj


    def getConfig(self):
        ''' Return the current confinguration object.
        '''
        return self.cfg

        
if __name__ == "__main__":
    print("greenhouseCtrl.__main__()")

    ctrl = GreenhouseCtrl()

