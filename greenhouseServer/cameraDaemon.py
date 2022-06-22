#/usr/bin/python3
import picamera
import time
import threading
import os
import sbsCfg

class SbsCam:
    camThread = None
    
    def __init__(self, configFname):
        self.cfg = sbsCfg.loadConfig(configFname)
        print(self.cfg)
        self.outFname = self.cfg['camImg']
        self.tmpFname = "%s.tmp.jpg" % self.outFname
        self.cam = picamera.PiCamera()
        time.sleep(3)
        self.start()

    def start(self):
        self.camThread = threading.Thread(target= self.run)
        self.camThread.do_run = True
        self.camThread.start()

    def stop(self):
        self.camThread.do_run = False
        self.camThread.join()

    def isRunning(self):
        return self.camThread.do_run

    def run(self):
        while(self.camThread.do_run):
            self.cam.capture(self.tmpFname)
            os.remove(self.outFname)
            os.rename(self.tmpFname, self.outFname)
            time.sleep(1)
        

if __name__ == "__main__":
    print("cameraDaemon main()")
    cam = SbsCam("sbscfg.json")

