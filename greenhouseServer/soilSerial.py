#!/usr/bin/python3

# Interface to serial (Arduino) based interface to analogue soil moisture meters
# based on SBS K-Mirror Interface

import time
import serial
import logging

class SoilSerial:
    comms = None
    def __init__(self,cfg, debug=False):
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])
        port = self.cfg['soilSerialDevice']
        print("SoilSerial.__init__(%s)" % port)
        self.debug=debug
        try:
            self.comms = serial.Serial(port,
                                       baudrate=115200,
                                       bytesize=8,
                                       parity='N',
                                       stopbits=1,
                                       timeout=1)
            print("Serial communications opened ok")
            self.logger.info("Serial communications opened ok")
        except serial.serialutil.SerialException as ex:
            print("ERROR:  SoilSerial.__init__: Failed to Open Communications to port %s" % port)
            self.logger.error("ERROR:  SoilSerial.__init__: Failed to Open Communications to port %s" % port)
            print(ex)
            self.logger.error(ex)
            self.comms = None
            #raise(ex)



    def getStatus(self):
        #print("kmCtrl.getStatus()")
        statusLst = []
        if (self.comms is None):
            print("SoilSerial - ERROR - communications not established")
        else:
            r = self.readStr()
            if (r == ''):
                print("SoilSerial.getStatus(): ERROR getting status - r=\'%s\'" % (r))
            else:
                #if (self.debug):
                print("SoilSerial.getStatus(): retrieved %s (%d chars) OK" % (r,len(r)))
                try:
                    setParts = r.strip().split(",")
                    statusLst = setParts
                except:
                    print("SoilSerial.getStatus() - ERROR Parsing return value %s" % r)
        return(statusLst)

        
        
    def close(self):
        if (self.comms is None):
            print("SoilSerial.close() - comms is None - not doing anything")
            self.logger.info("SoilSerial.close() - comms is None - not doing anything")
        else:
            self.comms.close()
            self.logger.info("SoilSerial.close()")

    def flushSerial(self):
        if (self.comms is None):
            self.logger.info("SoilSerial.flushSerial() - comms is None - not doing anything")
        else:
            try:
                r=''
                retLine='xxxx'
                while (len(retLine)>0):
                    retLine = self.comms.readline().decode()
                    r = "%s:%s" % (r,retLine)
            except Exception as e:
                print('ERROR flushing serial buffer')
                self.logger.error("SoilSerial.flushSerial() - Error flushing serial buffer")
                r=''
            return r
        
        
    def sendCmdNoWait(self, cmd):
        if (self.comms is None):
            pass
        else:
            flushStr = self.flushSerial()
            if (self.debug): print("sendCmdNoWait() flushStr=%s " % flushStr)
            try:
                r=''
                if (self.debug): print("sending %s" % cmd.encode())
                dump = self.comms.write((cmd+'\n').encode())
                time.sleep(0.2)
                retLine='xxxx'
                while (len(retLine)>0):
                    retLine = self.comms.readline().decode()
                    r = "%s,%s" % (r,retLine)
                if (self.debug): print("sendCmdNoWait() - cmd=%s, ret=%s" % (cmd, r.strip()))
            except Exception as e:
                print('ERROR executing %s' % (cmd))
                r=''
            return r

    def readStr(self):
        if (self.comms is None):
            return ''
        else:
            r = self.comms.readline().decode()
            return r

if __name__=="__main__":
    print("soilSerial.main()")

    cfgObj={
        "logName": "soilSerial",
        "soilSerialDevice": "/dev/ttyUSB0"
    }

    km = SoilSerial(cfgObj,debug=True)
    print("readStr=%s" % km.readStr())
    print("readStr=%s" % km.readStr())
    print("readStr=%s" % km.readStr())
    print("getStatus=",km.getStatus())
    #print(km.getStatus())

