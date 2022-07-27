#!/usr/bin/env python
import os
import json
import argparse
import logging
import logging.handlers
import bottle
import WebControlClass
import sbsCfg
import greenhouseCtrl

class GreenhouseSvr(WebControlClass.WebControlClass):
    mCtrl = None
    statusObj = {
        'lampOnOff' : 'Off',
        'kMirrorOnOff' : 'Off',
        }

    def __init__(self, configFname="sbscfg.json"):
        print("GreenhouseSvr.__init__(%s)" % configFname)
        self.cfg = sbsCfg.loadConfig(configFname)

        # Create Log file output folder
        if not os.path.exists(self.cfg['logFolder']):
            os.makedirs(self.cfg['logFolder'])
        
        # Create Logger in folder specified in config file.
        self.logger = logging.getLogger(self.cfg['logName'])
        self.logger.setLevel(logging.DEBUG)
        fh = logging.handlers.TimedRotatingFileHandler(os.path.join(
            self.cfg['logFolder'], 
            "%s.log" % self.cfg['logName']),
            when='d', interval=1)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s.%(funcName)s[%(lineno)s] - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.info("Initialising Water Controller Server")


        credFname = os.path.join(os.path.dirname(os.path.realpath(__file__)),"credentials.json")
        print("Loading Credentials from credFname=%s"% credFname)
        credStr = open(credFname,"r").read()
        self.mCred = json.loads(credStr.encode('utf-8'))
        print(self.mCred)
        self.mCtrl = greenhouseCtrl.GreenhouseCtrl(configFname)
        super().__init__('0.0.0.0',8080)
        self.logger.info("Web Server Started")


    def stop(self):
        print("sbsSvr.stop()")
        self.logger.info("sbsSr.stop()")
        self.mCtrl.stop()
        #self.wwwThread.stop()
        

    def is_authenticated(user, password):
        for idObj in self.mCred:
            if (idObj['uname'].equals(user) and idObj['passwd'].equals(password)):
                return True
        return False
        
    def onWwwCmd(self,cmdStr,valStr, methodStr,request):
        ''' Process the command, with parameter 'valStr' using request
        method methodStr, and return the appropriate response.
        request is the bottlepy request associated with the command
        '''
        #if (request.auth is None):
            #print("Authentication Data not Provided")
            #return bottle.Response("Provide Credentials",401,{'WWW-Authenticate':'Basic realm="User"'})
            #return bottle.HTTPResponse(status=401, body="Authentication Data not PRovided")
            #bottle.abort(401,"Access Denied")
        #if (not self.is_authenticated(request.auth[0],request.auth[1])):
        #    print("NOT AUTHENTICATED")
            #return bottle.Response("403Unauthorised",403,{'WWW-Authenticate':'Basic realm="User"'})

        retVal = "onWwwCmd - ERROR, command not recognised"
        if (cmdStr=="status"):
            retVal=self.getStatus()
        if (cmdStr=="config"):
            retVal=self.getConfig()
        if (cmdStr=="rebootSbs"):
            retVal=self.rebootSbs()
        if (cmdStr=="opMode"):
            retVal=self.mCtrl.setOpMode(valStr)
        if (cmdStr=="onSecs"):
            retVal=self.mCtrl.setOnSecs(int(valStr))
        if (cmdStr=="cycleSecs"):
            retVal=self.mCtrl.setCycleSecs(int(valStr))
        if (cmdStr=="setpoint"):
            retVal=self.mCtrl.setSetpoint(float(valStr))
        if (cmdStr=="Kp"):
            retVal=self.mCtrl.setKp(float(valStr))
        if (cmdStr=="Ki"):
            retVal=self.mCtrl.setKi(float(valStr))
        if (cmdStr=="Kd"):
            retVal=self.mCtrl.setKd(float(valStr))
        self.logger.info("SbsSvr.onWwwCmd(%s/%s %s): returning %s" % (cmdStr,valStr,methodStr,retVal))
        return(retVal)

    def getStatus(self):
        statusObj = self.mCtrl.getStatus()
        return json.dumps(statusObj)

    def getConfig(self):
        return json.dumps(self.mCtrl.getConfig())

    def rebootSbs(self):
        retVal = os.system("sudo reboot")
        return retVal
    
    
    def lampOnOff(self):
        if (self.mCtrl.getStatus()['lampOn'] == False):
            self.mCtrl.setLamp(True)
        else:
            self.mCtrl.setLamp(False)
        return(self.mCtrl.getStatus())



    
    #def kMirrorOnOff(self):
    #    if (self.statusObj['kMirrorOnOff'] == "Off"):
    #        # FIXME really mirror motor on
    #        self.statusObj['kMirrorOnOff'] = 'On'
    #    else:
    #        # FIXME really turn mirror motor on
    #        self.statusObj['kMirrorOnOff'] = 'Off'
    #    return(self.statusObj)

    
if (__name__ == "__main__"):
    print("greenhouseSvr.__main__()")

    parser = argparse.ArgumentParser(description='Greenhouse Server')
    parser.add_argument('--config', default="sbscfg.json",
                        help='Configuration file name')
    #parser.add_argument('-n', '--nContours',
    #                    default=10,
    #                    help='Number of Contours')
    #parser.add_argument('-t', '--title',
    #                    default="Beam Profile",
    #                    help='Plot Title')
    parser.add_argument('--debug', '-d', default=False,
                        action='store_true', dest='debug',
                        help='Run in debug mode')

    args = parser.parse_args()
    args = vars(args)
    print(args)

    configFname = args['config']

    svr = GreenhouseSvr(configFname)
    svr.startServer()


    try:
        while svr.wwwThread.is_alive():
            svr.wwwThread.join(5)
    finally:
        svr.stop()
