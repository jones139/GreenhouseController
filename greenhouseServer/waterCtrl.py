#!/usr/bin/python3

# Greenhouse water controller interface
# Users serial interface to set watering cycle on the water controller
# microcontroller.

import serial
import logging

class WaterCtrl:
    comms = None
    def __init__(self,cfg):
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])

        port = self.cfg['waterControllerPort']
        print("WaterCtrl.__init__(%s)" % port)
        self.logger.info("Initialising Water Controller on Port %s" % port)
        try:
            self.comms = serial.Serial(port,
                                       baudrate=9600,
                                       bytesize=8,
                                       parity='N',
                                       stopbits=1,
                                       timeout=1)
            print("Serial communications opened ok")
        except serial.serialutil.SerialException as ex:
            print("ERROR:  WaterCtrl.__init__: Failed to Open Communications to port %s" % port)
            print(ex)
            self.logger.error("Failed to Open Communications to Water Controller")
            self.logger.error(ex)
            #raise(ex)
        r = self.sendCmdNoWait('DEBUG\r')
        if (r == ''):
            print('ERROR:\tWater Controller - connectivity failure - Returned \'%s\'' % r)
            self.logger.error('ERROR:\tWater Controller - connectivity failure (check switch is ON on front panel) - Returned \'%s\'' % r)
            #exit(-1)
        #self.lampOff()


    def setOnSecs(self,onSecs):
        """ Set the number of seconds per period that the water will be on.
        """
        self.logger.info("Setting ON_SECS to %d" % onSecs)
        r = self.sendCmdNoWait('ONSECS=%d\r' % onSecs)
        if (r == ''):
            self.logger.error("Error setting ON_SECS")
            print("LampCtrl.lampOff(): ERROR setting ON_SECS")
            return(-1)
        else:
            print("LampCtrl.setOnSecs(): ok: %s" % r)
            self.onSecs = onSecs
            return(0)

        
    def close(self):
        self.comms.close()

    def sendCmdNoWait(self, cmd):
        try:
            dump = self.comms.write((cmd+'\r').encode())
            r = self.comms.readline().decode()
            #print("sendCmdNoWait() - cmd=%s, ret=%s" % (cmd, r.strip()))
            #print("sendCmdNoWait() - ret=%s" % (r.strip()))
        except Exception as e:
            print('ERROR executing %s' % (cmd))
            self.logger.error('ERROR executing %s' % (cmd))
            r=''
        return r



