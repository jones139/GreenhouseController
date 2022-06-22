#!/usr/bin/python3

# SBS Lamp Control

import serial
import logging

class LampCtrl:
    comms = None
    lampStatus = None
    def __init__(self,cfg):
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])

        port = self.cfg['lampPort']
        print("LampCtrl.__init__(%s)" % port)
        self.logger.info("Initialising Arc Lamp Controller on Port %s" % port)
        try:
            self.comms = serial.Serial(port,
                                       baudrate=9600,
                                       bytesize=8,
                                       parity='N',
                                       stopbits=1,
                                       timeout=1)
            print("Serial communications opened ok")
        except serial.serialutil.SerialException as ex:
            print("ERROR:  LampCtrl.__init__: Failed to Open Communications to port %s" % port)
            print(ex)
            self.logger.error("Failed to Open Communications to Lamp Controller")
            self.logger.error(ex)
            #raise(ex)
        r = self.sendCmdNoWait('A-PRESET?\r')
        if (r == ''):
            print('ERROR:\tSBS PSU - connectivity failure (check switch is ON on front panel) - Returned \'%s\'' % r)
            self.logger.error('ERROR:\tSBS PSU - connectivity failure (check switch is ON on front panel) - Returned \'%s\'' % r)
            #exit(-1)
        #self.lampOff()

    def lampOff(self):
        """Switch Lamp Off - returns 0 on success or -1 on failure.
        """
        self.logger.info("Switching Lamp Off")
        r = self.sendCmdNoWait('STOP\r')
        if (r == ''):
            self.logger.error("Error switching Lamp Off")
            print("LampCtrl.lampOff(): ERROR switching off Lamp")
            return(-1)
        else:
            print("LampCtrl.lampOff(): Lamp Switched Off OK: %s" % r)
            self.lampStatus = 0
            return(0)

    def lampOn(self):
        """Switch Lamp On - returns 0 on success or -1 on failure.
        """
        self.logger.info("Switching Lamp On")
        r = self.sendCmdNoWait('START\r')
        if (r == ''):
            self.logger.error("Error switching Lamp On")
            print("LampCtrl.lampOn(): ERROR switching on Lamp - r=\'%s\'" % r)
            return(-1)
        else:
            print("LampCtrl.lampOn(): Lamp Switched On OK: %s" % r)
            self.lampStatus = 1
            return(0)

    def getPower(self):
        """Return the current lamp power in watts
        """
        self.logger.info("getPower")
        r = self.sendCmdNoWait('WATTS?\r')
        if (r == ''):
            self.logger.error("Error Reading lamp power")
            print("LampCtrl.lampOn(): ERROR reading lamp power - r=\'%s\'" % r)
            return(-1)
        else:
            powerVal = float(r.split('\r')[0])
            print("LampCtrl.lampOn(): Lamp power is: %s" % r)
            if (powerVal>100):
                self.lampStatus = 1
            else:
                self.lampStatus = 0
            return(powerVal)
        
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



