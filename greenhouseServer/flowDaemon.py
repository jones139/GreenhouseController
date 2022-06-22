#!/usr/bin/env python

# Based on https://medium.com/@rxseger/interrupt-driven-i-o-on-raspberry-pi-3-with-leds-and-pushbuttons-rising-falling-edge-detection-36c14e640fef
# interrupt-based GPIO example using LEDs and pushbuttons

import time
import datetime
import threading
import logging

import RPi.GPIO as GPIO
import sbsCfg


class _flowThread(threading.Thread):
    """ Background process that will calculate the flow rate every
    second based on the pulse count collected from an interrupt driven
    routine.
    """
    rate_delay = 1.0 # sec
    loop_delay = 0.01 # sec

    def __init__(self, cfg, debug=False):
        print("_flowThread.__init__()")
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])

        threading.Thread.__init__(self)
        self.DEBUG = debug
        self.runThread = True
        self.count = 0
        self.flowEncPin = cfg['flowMtr']['dataPin']
        self.pulsesPerLitre = cfg['flowMtr']['pulsesPerLitre']
        self.outFname = cfg['flowMtr']['flowFname']
        self.curTime = datetime.datetime.now()
        self.curFlow = -1
        print("outFname=%s, flowEncPin=%d, pulsesPerLitre=%f" %
              (self.outFname, self.flowEncPin, self.pulsesPerLitre))

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup([self.flowEncPin], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.flowEncPin, GPIO.FALLING,
                              self.incrementCount)


    def incrementCount(self, pin):
        ''' Interupt driven routine to increment pulse count.'''
        if (pin == self.flowEncPin):
            self.count += 1


    def run(self):
        """ Main loop of nhread - every time rate_delay seconds have
        elsapsed, calculates rate, and resets counter.
        """
        started = time.time()
        while self.runThread:
            dt = time.time() - started
            if dt > self.rate_delay:
                pulseRate = 1.0*self.count/dt  # pulses per second
                rate = 60.* pulseRate/self.pulsesPerLitre  # l/min
                tnow = datetime.datetime.now()
                outFile = open(self.outFname,'w')
                outFile.seek(0)  # go to start of file
                outFile.write(tnow.strftime("%Y-%m-%d %H:%M:%S"))
                outFile.write(", %.3f\n" % rate)
                outFile.flush()
                if (self.DEBUG): print("Count = %d, Rate = %f" % (self.count,rate))
                self.count = 0
                started = time.time()
                self.curTime = tnow
                self.curFlow = rate
            time.sleep(self.loop_delay)

    def stop(self):
        """ Stop the background thread"""
        print("_flowThread.stop() - Stopping thread")
        self.runThread = False
        GPIO.remove_event_detect(self.flowEncPin)

    def getFlow(self):
        """ Return an object containing the current time and flow rate
        """
        retObj = {}
        retObj['time'] =self.curTime
        retObj['flow'] = self.curFlow
        #print(retObj)
        return(retObj)


class FlowDaemon():
    '''
        Start a thread that runs in the background to repeatedly calculate
        flow rate from accumulated pulses.  Pulse count is incremented using
        inerrupts.
        Saves the measured flow rate to a file.
        The pin the meter is attached to and the output filename are
        specified in a configuration object that is passed on initialisation of
        the class.
        '''
    DEBUG = False
    devices = {}
    flowThread = None

    def __init__(self,cfgObj, debug=False):
        '''
        Initialise the class using data provided in object cfgObj
        '''
        print("flowDaemon.__init__()")
        self.cfg = cfgObj
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("Initialising flow meter")

        self.DEBUG = debug
        self.flowThread = _flowThread(cfgObj, debug)
        self.flowThread.daemon = True


    def start(self):
        ''' Start the background process to monitor flow rate
        '''
        print("flowDaemon.start()")
        self.logger.info("Starting flow meter")
        self.flowThread.start()

    def stop(self):
        ''' Stop the background process to monitor flow rate
        '''
        print("flowDaemon.stop()")
        self.logger.info("Stopping flow meter")
        self.flowThread.stop()

    def getFlow(self):
        retObj = self.flowThread.getFlow()
        return retObj


if (__name__ == "__main__"):    
    print("starting thread")
    daemon("sbscfg.json")
