#!/usr/bin/env python
import os
import time
import datetime
import threading
import logging
import smbus
import RPi.GPIO as GPIO
import Adafruit_ADS1x15

import sbsCfg
import sht3x_main
import bh1750
import dbConn
import graphs
import soilSerial

    


def counts2moisture(counts, mode="CAP"):
    if (mode=="RES"):
        moisture = 1e6 * 1.0 / counts
    elif (mode=="CAP"):
        moisture = 19096 - counts
    else:
        print("ERROR - Unrecognsised mode: %s" % mode)
        moisture = 9e99
    return moisture


def counts2moisture_new(counts,calObj):
    DRY_LEVEL = 0.0    #y1
    WET_LEVEL = 100.0  #y2
    dryVal = calObj['dryVal']  #x1
    wetVal = calObj['wetVal']  #x2

    moisture = DRY_LEVEL + (counts-dryVal) * (WET_LEVEL - DRY_LEVEL) / (wetVal-dryVal)
    return moisture

class _monitorThread(threading.Thread):
    LOG_INTERVAL = 10  # sec
    runDaemon = False
    DEBUG = False
    curTime = None
    curData = {}
    dataBuffer = []
    rootPath = '/sys/bus/w1/devices/'
    def __init__(self, cfg, debug = False):
        print("_monitorThread.__init__()")
        self.cfg = cfg
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("_monitorThread.__init__()")
        threading.Thread.__init__(self)
        self.DEBUG = debug
        self.runThread = True
        self.dataFolder = cfg['dataFolder']
        self.outFname = os.path.join(cfg['dataFolder'],cfg['monitorFname'])
        print("self.outFname=%s" % self.outFname)
        self.logInterval = cfg['logInterval']
        print("_monitorThread._init__: outFname=%s, log interval=%d s" % (self.outFname, self.logInterval))
        self.dbPath = os.path.join(cfg['dataFolder'],cfg['dbFname'])
        self.temp2Dev = cfg['temp2Dev']
        self.curData = {}
        self.curTime = datetime.datetime.now()
        #self.soilProbePin = cfg['soilProbePin']

        if (sht3x_main.init()):
            print("Initialised sht3x sensor");

        self.bus = smbus.SMBus(1)
        self.lightSensor = bh1750.BH1750(self.bus)

        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup([self.soilProbePin], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #self.soilMoistureLevel = GPIO.input(self.soilProbePin)

        self.adc = Adafruit_ADS1x15.ADS1115()
        #self.soilMoistureLevel = adc.read_adc(0,1)

        self.soilSerial = soilSerial.SoilSerial(self.cfg)
    
    def calcMeans(self,buf):
        tempSum = 0.
        temp2Sum = 0.
        humSum = 0.
        lightSum = 0.
        soilSum = 0.
        soilSum1 = 0.
        soilSum2 = 0.
        soilSum3 = 0.
        count = 0
        for rec in buf:
            tempSum += rec['temp']
            humSum += rec['humidity']
            lightSum += rec['light']
            temp2Sum += rec['temp2']
            soilSum += rec['soil1']
            soilSum1 += rec['soil2']
            soilSum2 += rec['soil3']
            soilSum3 += rec['soil4']
            count += 1
        tempMean = tempSum / count
        temp2Mean = temp2Sum / count
        humMean = humSum / count
        lightMean = lightSum / count
        soilMean = soilSum / count
        soil1Mean = soilSum1 / count
        soil2Mean = soilSum2 / count
        soil3Mean = soilSum3 / count
        return(tempMean, humMean, lightMean, temp2Mean,
               soilMean,
               soil1Mean,
               soil2Mean,
               soil3Mean
               )

    def readDs18B20(self, id):
        """ Attemptot read the value of the DS18B20 temperature device id 
        off the 1-wire bus and return the temperature in degC.
        Returns -300 if there is an error
        """
        try:
            tempStr = ''
            fpath = os.path.join(self.rootPath,id,"w1_slave")
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


        
    def run(self):
        """ The main loop of the thread  repeatedly scans all of the 
        devices and saves the result to  a file
        """
        print("monitorThread.run()")
        self.db = dbConn.DbConn(self.dbPath)
        #outFile = open(self.outFname,'a')
        data = {}
        data['meanTemp'] = -999
        data['meanHumidity'] = -999
        data['meanLight'] = -999
        data['meanTemp2'] = -999
        data['meanSoil'] = -999
        data['meanSoil1'] = -999
        data['meanSoil2'] = -999
        data['meanSoil3'] = -999

        lastLogTime = datetime.datetime.now()
        while self.runThread:
            dt = datetime.datetime.now()
            tData, hData = sht3x_main.read()
            hum, temp = sht3x_main.calculation(tData,hData)
            light = self.lightSensor.measure_high_res()
            temp2 = self.readDs18B20(self.temp2Dev)

            # soilMoisture is read from the ADC connected directly to the
            # Raspberry Pi - this is not used.
            # Use lowest gain to keep the sensors on scale as we are using 5V
            # supplies to the sensor and a 3.3V ADC.
            soilMoisture = counts2moisture_new(self.adc.read_adc(0,2/3),
                                                self.cfg['soilMonitors'][0])
            #soilMoisture = -1
            self.logger.info("soilMoisture=%d" % soilMoisture)

            # Read all four soil moisture readings from the Arduino
            # connected via USB.
            soilParts = self.soilSerial.getStatus()
            #print(soilParts)
            if (len(soilParts)<4):
                print("Error - did not receive 4 values from soilSerial")
                self.logger.info("Error - did not receive 4 values from soilSerial")
                soilMoisture1 = -1
                soilMoisture2 = -1
                soilMoisture3 = -1
                soilMoisture4 = -1
            else:
                #time.sleep(0.1)
                #soilMoisture1 = self.adc.read_adc(1,2/3)
                try:
                    soilMoisture1 = counts2moisture_new(5.0*soilParts[0],
                                                        self.cfg['soilMonitors'][1])
                except:
                    self.logger.info("Error parsing %s" % soilParts[0])
                    soilMoisture1 = -1
                self.logger.info("soilMoisture1=%d" % soilMoisture1)
                #time.sleep(0.1)
                #soilMoisture2 = self.adc.read_adc(2,2/3)
                #soilMoisture2 = -1
                try:
                    soilMoisture2 = counts2moisture_new(5.0*soilParts[1],
                                                        self.cfg['soilMonitors'][2])
                except:
                    self.logger.info("Error parsing %s" % soilParts[1])
                    soilMoisture2 = -1
                self.logger.info("soilMoisture2=%d" % soilMoisture2)
                #time.sleep(0.1)
                #soilMoisture3 = self.adc.read_adc(3,2/3)
                #soilMoisture3 = -1
                try:
                    soilMoisture3 = counts2moisture_new(5.0*soilParts[2],
                                                        self.cfg['soilMonitors'][3])
                except:
                    self.logger.info("Error parsing %s" % soilParts[2])
                    soilMoisture3 = -1
                self.logger.info("soilMoisture3=%d" % soilMoisture3)

                try:
                    soilMoisture4 = counts2moisture_new(5.0*soilParts[3],
                                                        self.cfg['soilMonitors'][4])
                except:
                    self.logger.info("Error parsing %s" % soilParts[3])
                    soilMoisture4 = -1

                self.logger.info("soilMoisture4=%d" % soilMoisture4)

            
            data['humidity'] = hum
            data['temp'] = temp
            data['light'] = light
            data['temp2'] = temp2
            data['soil'] = soilMoisture
            data['soil1'] = soilMoisture1
            data['soil2'] = soilMoisture2
            data['soil3'] = soilMoisture3
            data['soil4'] = soilMoisture4
            self.curTime = dt
            self.curData = data
            self.dataBuffer.append(data)

            # Log data to the local database
            if (dt.timestamp() - lastLogTime.timestamp())>=self.logInterval:
                (meanTemp, meanHumidity, meanLight, meanTemp2,
                 meanSoil,meanSoil1,meanSoil2,meanSoil3) = self.calcMeans(self.dataBuffer)
                data['meanTemp'] = meanTemp
                data['meanHumidity'] = meanHumidity
                data['meanLight'] = meanLight
                data['meanTemp2'] = meanTemp2
                data['meanSoil'] = meanSoil
                data['meanSoil1'] = meanSoil1
                data['meanSoil2'] = meanSoil2
                data['meanSoil3'] = meanSoil3
                print("Logging Data....")
                # write to database
                self.db.writeMonitorData(self.curTime,
                                         meanTemp, meanTemp2,
                                         meanHumidity,
                                         meanLight,
                                         meanSoil,
                                         meanSoil1,
                                         meanSoil2,
                                         meanSoil3)

                lastLogTime = dt
                self.dataBuffer = []

            if (self.DEBUG): print(self.curTime, self.curData)
            self.logger.debug(self.curData)
            #time.sleep(0.01)
            # Run this loop every second.
            time.sleep(1.0)
        #outFile.close()
        print("monitorThread.run() - Exiting")

    def stop(self):
        """ Stop the background thread"""
        print("_moitorThread.stop() - Stopping thread")
        self.runThread = False

    def getData(self):
        """ Return an object containing the current time and sensor readings
        """
        retObj = {}
        retObj['time'] =self.curTime.timestamp()
        retObj['data'] = self.curData
        if (self.DEBUG): print(retObj)
        return(retObj)
            


class MonitorDaemon():
    '''
    Start a thread that runs in the background to repeatedly poll 
    the sensors
    Saves the measured readings to a file.
    The devices to be monitored, their order and the output filename are
    specified in a configuration object that is passed on initialisation of
    the class.
    It produces hourly averags of the data which are logged to the file.
    '''
    DEBUG = False
    devices = {}
    tempThread = None

    def __init__(self,cfgObj, debug=False):
        '''
        Initialise the class using data provided in object cfgObj
        '''
        print("MonitorDaemon.__init__()")
        self.cfg = cfgObj
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.info("TempDaemon.__init__()")
        self.monitorThread = _monitorThread(cfgObj, debug)
        self.monitorThread.daemon = True


    def start(self):
        ''' Start the background process to monitor temperatures
        '''
        print("monitorDaemon.start()")
        self.logger.info("MonitorDaemon.start()")
        self.monitorThread.start()

    def stop(self):
        ''' Stop the background process to monitor temperatures
        '''
        print("monitorDaemon.stop()")
        self.logger.info("MonitorDaemon.stop()")
        self.monitorThread.stop()

    def getData(self):
        retObj = self.monitorThread.getData()
        return retObj

    
if __name__ == '__main__':
    print("sbsSvr.__main__()")

    cfgObj = {
        "logName": "monitorDaemon",
        "monitorFname": "/tmp/temps.csv",
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

    #cfgObj = sbsCfg.loadConfig("sbscfg.json")
    #print(cfgObj['temps'])

    mon = MonitorDaemon(cfgObj, debug=True)
    mon.start()
    time.sleep(20)
    mon.stop()
    time.sleep(10)
    print("exiting")


 
