#!/usr/bin/env python

"""
SBS Temperature Monitoring daemon.  Based on S4 Control Unit script pd_flux2.py
by Brijen Hathi

Software to interface with the Terma ICCS EGSE from Airbus
Developed by Brijen Hathi, brijenhathi@yahoo.com.

This module works via the CCOGSE Server software.

# Versions log
pd_flux2.py
            (20/02/19) PDs - SLO PD added. Note, LSM not present
pd_sbs.py   (26/04/20) GJ Stripped out all LSM bits so it will work on SBS
            (22/09/21) GJ added Picolog adc support
            (23/09/21) GJ changed to use fixed gain thorabls pd amplifier rather than TZA because reliability poor after adding extra ADC via USB.
Note 45.1 uA gives 0.933 V

"""

import logging
import numpy as np
import pylab
from datetime import datetime as dt
import time,sys
import serial, string
import struct
import binascii as ba
import pickle
from subprocess import Popen
from threading import Thread, Lock, RLock
import adc_sbs as adc

# PhotoDiodes (PDs) types
pdStat = False  # PD status is set 'True'  by ISP_connect
lck = Lock()
pdFs = [0., 1.2e-2, 1.2e-3, 1.2e-4, 1.2e-5, 1.2e-6, 1.2e-7 ] # full scale
ack1 = False # acknowledge set True if adc connected

path = '/home/shared_files/PhotoDiode_intensity_logs/'
comms = None


class PdSBS():
    comms = None
    rvThread = None
    tzaVals = None
    adcVals = None
    dataTime = 0

    ampsPerVolt = 45.2e-6/0.933   # ADC using Thorlabs PDA220C on Gain 3.
    
    def __init__(self,cfg=None):
        self.cfg = cfg
        if (cfg is None):
           print("Error - we need a configuration file")
           exit(-1)
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("Initialising Photodiode Logger")
        self.haveAdc = False

        self.haveAdc = adc.adc_init()

        pdCon = self.cfg['pdPort']
        if pdCon != "ADC":
            try:
                self.comms = serial.Serial(pdCon,baudrate=115200,
                                           bytesize=8, parity='N',
                                           stopbits=1, timeout=1)
                print("pd Communications opened ok")
                self.logger.info("tza500 pd Communications opened ok")
                r = self.sendCmdNoWait('$U')
                if (r== 'U OK\n'):
                    print('PhotoDiode ready to use')
                    n=1
                    self.setBandWidth(4)
                    self.setGain(1)
                    #self.autoGain()
                else:
                    print('pd_sbs.init(): ERROR: response = [ %s ] not as expected' %r)
                    n=0
                    self.comms = None                
            except serial.serialutil.SerialException as ex:
                print("ERROR:  pd_sbs.__init__: Failed to Open Communications to port %s" % pdCon)
                print(ex)
        else:
            print("Photodiode port set to ADC - assuming fixed gain PD amplifier with no output readout - readout via separate Pico ADC20 ADC")
            self.logger.info("Photodiode port set to ADC - assuming fixed gain PD amplifier with no output readout - readout via separate Pico ADC20 ADC")

        self.startAuto()


            
    def close(self):
        if (self.isAuto()):
            self.killAuto()
        if (self.comms is not None):
            self.comms.close()
        if (self.haveAdc):
            adc.adc_close()

    def getRawVals(self):
        '''returns the current set of raw values as a numpy array'''
        return(self.tzaVals)

    def getAdcVals(self):
        return(self.adcVals)
    
    def getVal(self):
        return(self.getTzaVal())
    
    def getTzaVal(self):
        ''' returns the current value, which is the mean, standard deviation, 
        count and acquisition time for the current set of raw values'''
        if (self.tzaVals is not None):
            if (self.tzaVals.mean() == 0):
                return (self.tzaVals.mean(), 0.0 ,self.tzaVals.size, self.dataTime)
            else:
                return (self.tzaVals.mean(), self.tzaVals.std()/self.tzaVals.mean(),self.tzaVals.size, self.dataTime)
        else:
            return(None,None,None,0)

    def getAdcVal(self):
        ''' returns the current value, as measured by the ADC  
        which is the mean, standard deviation, 
        count and acquisition time for the current set of raw values'''
        if (self.adcVals is not None):
            if (self.adcVals.mean() == 0):
                return (self.adcVals.mean(), 0.0 ,self.adcVals.size, self.dataTime)
            else:
                return (self.adcVals.mean(), self.adcVals.std()/self.adcVals.mean(),self.adcVals.size, self.dataTime)
        else:
            return(None,None,None,0)

        
    def sendCmdNoWait(self, cmd):
        if (self.comms is None):
            return(-1)
        try:
            dump = self.comms.write((cmd+'\r').encode())
            r = self.comms.readline().decode()
            #print("sendCmdNoWait() - cmd=%s, ret=%s" % (cmd, r.strip()))
        except Exception as e:
            r = 'ERROR executing %s' % (cmd)

        return r
    
    def setBandWidth(self,n):
        '''
        set bandwidth: 10KHz, 1KHz, 100Hz, 10Hz from n=1 to n=4 gain
        higher gain switches output to a nA units. 
        '''
        if (self.comms is not None):
            s = 'B%d' %n
            r = self.sendCmdNoWait(s)
            #print("sent %s, returned %s" % (s, r.strip()))
            if (r == ('\r'+s+' OK\n')):
                print('bandwidth set to %d' %n)
                self.logger.info('bandwidth set to %d' %n)
            else:
                print('Error Setting Bandwidth - %s' % r)
                self.logger.error('Error Setting Bandwidth - %s' % r)
            return r
        else:
            return(-1)

    def setGain(self,n):
        ''' set up gain in steps of x10, from n=1 = x1 gain to n=6 = x100k gain
        generally n=3 works with room lights
        higher gain switches output to a nA units. 
        '''
        if (self.comms is not None):
            restartAuto = False
            if self.isAuto():
                print("setGain - killing auto")
                self.killAuto()
                restartAuto = True
            s = 'V%d' %n
            r = self.sendCmdNoWait(s)
            if (r == ('\r'+s+' OK\n')):
                print('gain set to %d' %n)
                self.gain = n
            else:
                print('Error Setting Gain - %s' % r)
                self.logger.error('Error Setting Gain - %s' % r)
                self.gain = -1
            if restartAuto:
                print("setGain - restarting auto")
                self.startAuto()
        else:
            self.gain = -1
        return(self.gain)

    def autoGain(self):
        ''' Three autogain functions below.
        use autoGain() for M2, autoGain3() for Ekspla
        Gradually reduce gain until we start to see varying readings,
        indicating that we are not saturated.
        '''
        if (self.comms is not None):
            err = 0
            self.killAuto()
            print('Auto gain measurements....')
            for i in range(6, 0, -1):
                self.setGain(i)
                time.sleep(0.5)
                a = np.asarray(self.readVals(15))
                b = a.std(ddof=1)/a.mean()
                print('Gain=%d, a=%f, b=%f' % (i,a.mean(),b))
                if (abs(b) > 0.015):
                    break
            self.startAuto()

            msgs = 'Gain Set to %d' % (i)
            print(msgs)
            self.gain = i
            self.logger.info(msgs)
            return (msgs)
        else:
            self.gain=-1
            return(-1)
            
            
    def startAuto(self):
        self.rvThread = Thread(target= self.pd_rv)
        self.rvThread.do_run = True
        self.rvThread.start()

    def killAuto(self):
        if (self.rvThread is not None):
            self.rvThread.do_run = False
            self.rvThread.join()
            time.sleep(1)

    def isAuto(self):
        if (self.rvThread is not None):
            return self.rvThread.do_run
        else:
            return(-1)

    #PD polling rate set to 1 second
    def pd_rv(self):
        while getattr(self.rvThread, "do_run"):
            t1 = time.time()

            if (self.haveAdc):
                self.adcVals = adc.adc_readVals(5)
            else:
                self.adcVals = np.zeros(5)

            if (self.comms is not None):
                self.tzaVals = np.asarray(self.readVals(5))
            else:
                if (self.haveAdc):
                    self.tzaVals = self.adcVals * self.ampsPerVolt
                else:
                    self.tzaVals = np.zeros(15)
            t2 = time.time()
            self.dataTime = t2
            dtt1 = t2 -t1
            if (dtt1<1.):
                time.sleep(1. - dtt1)
            else:
                print("pd_rv overrun - dtt1 = %f" % dtt1)

    def readVals(self,n):
        '''Read n values from the tza amplifier, returning a list of 
        float values.'''
        output1 = []
        if (self.comms is not None):
            for i in range(n):
                r = self.sendCmdNoWait('$E')
                #print("readvals -r = %s" % r.strip())
                r1 = r[2:-1].replace(',','.')
                r2 = r1.replace('uA','E-6')
                r2 = r2.replace('nA','E-9')
                r2 = r2.split('6 OK')[0]
                try:
                    output1.append(float(r2))
                except:
                    #print("Ignoring bad data %s" % r2)
                    pass
        return(output1)



if (__name__ == "__main__"):
    print("pd_sbs.main()")
    import sbsCfg
    cfg = sbsCfg.loadConfig("/home/shared_files/sbs_data/sbscfg.json")
    pd = PdSBS(cfg)
    print("PdSBS Returned - starting continuous monitoring")

    for n in range(0,10):
        print(pd.getVal(), pd.getAdcVal())
        time.sleep(1)
    print(pd.getRawVals())
    print(pd.getAdcVals())
    pd.close()
