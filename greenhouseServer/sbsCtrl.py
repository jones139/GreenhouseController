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
import psutil
import json
import math
import datetime
import logging

import sbsCfg
import tempDaemon
import flowDaemon
import lampCtrl
import cameraDaemon

class SbsCtrl:
    statusObj = { 'msg': '---'}

    def __init__(self,configFname = "sbscfg.json"):
        print("sbsCtrl.__init__(%s)" % configFname)
        self.cfg = sbsCfg.loadConfig(configFname)
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("SbsCtrl.__init__()")

        
        self.lampCtrl = lampCtrl.LampCtrl(self.cfg)
        self.lampCtrl.getPower()
        self.statusObj['lampOn'] = self.lampCtrl.lampStatus
        self.tempDaemon = tempDaemon.TempDaemon(self.cfg, debug=False)
        self.tempDaemon.start()
        self.flowDaemon = flowDaemon.FlowDaemon(self.cfg, debug=False)
        self.flowDaemon.start()


    def stop(self):
        """ Shutdown the various daemon processes / threads nicely """
        self.tempDaemon.stop()
        self.flowDaemon.stop()



    def getTemps(self):
        tempsObj = self.tempDaemon.getTemps()
        return(tempsObj)

    def getStatus(self):
        ''' Populates the status object with the latest photodiode
        and temperature data, and returns the current status object '''
        self.statusObj['tempVals'] = self.getTemps()['temps']
        self.statusObj['flowRate'] = self.getCoolingFlow()['flow']
        return self.statusObj


    def getConfig(self):
        ''' Return the current confinguration object.
        '''
        return self.cfg

        
if __name__ == "__main__":
    print("sbsCtrl.__main__()")

