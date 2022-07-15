#!/usr/bin/env python3

import datetime
import sqlite3
import pandas as pd

class DbConn:
    def __init__(self,dbFname):
        self.db = sqlite3.connect(dbFname)

    def writeMonitorData(self,data_date,temp1, temp2, rh, light,soil):
        # Note - triple quote for multi line string
        cur = self.db.cursor()
        cur.execute("""insert into 'environment'
        ('data_date', 'temp1', 'temp2', 'rh', 'light', 'soil')
        values (?, ?, ?, ?, ?, ?);""",
                        (data_date, temp1, temp2, rh, light, soil))

        self.db.commit()

        
    def getMonitorData(self, sdate, edate, retDf=False):
        #print(sdate,type(sdate), edate, type(edate))
        queryStr = """select data_date, temp1, temp2, rh, light, soil from environment where data_date >= ? and data_date <= ?;"""
        paramsTuple = (sdate, edate)
        if retDf:
            df = pd.read_sql (queryStr,
                              self.db,
                              params=paramsTuple)
            return df
        else:
            cur = self.db.cursor()
            cur.execute(queryStr,
                        paramsTuple)
            return cur.fetchall()

    def getLatestMonitorData(self):
        queryStr = """select data_date, temp1, temp2, rh, light, soil from environment order by rowid desc limit 1;"""
        cur = self.db.cursor()
        cur.execute(queryStr)
        return cur.fetchone()

        
    def writeWaterData(self,data_date,waterStatus, onTime, cycleTime, controlVal):
        # Note - triple quote for multi line string
        cur = self.db.cursor()
        cur.execute("""insert into 'water'
        ('data_date', 'waterStatus', 'onTime', 'cycleTime','controlVal')
        values (?, ?, ?, ?,?);""",
                        (data_date, waterStatus, onTime, cycleTime, controlVal))

        self.db.commit()

        
    def getWaterData(self, sdate, edate, retDf=False):
        #print(sdate,type(sdate), edate, type(edate))
        queryStr = """select data_date, waterStatus from water where data_date >= ? and data_date <= ?;"""
        paramsTuple = (sdate, edate)
        if retDf:
            df = pd.read_sql (queryStr,
                              self.db,
                              params=paramsTuple)
            return df
        else:
            cur = self.db.cursor()
            cur.execute(queryStr,
                        paramsTuple)
            return cur.fetchall()

    def getWaterControlVals(self):
        ''' returns tupe (onSecs, cycleSecs) which is the current control parameters.
'''
        queryStr = """select onTime, cycleTime from water order by rowid desc limit 1;"""
        cur = self.db.cursor()
        cur.execute(queryStr)
        return cur.fetchone()
        

        
    def importCsv(self, csvFname):
        infile = open(csvFname,"r")
        for lineStr in infile:
            #print(lineStr)
            linParts = lineStr.split(',')
            dateStr = linParts[0].strip()
            dataDate = datetime.datetime.strptime(linParts[0],
                                                  "%Y-%m-%d %H:%M:%S")
            timeStamp = int(linParts[1])
            temp1 = float(linParts[2])
            rh = float(linParts[3])
            light = float(linParts[4])
            print(dateStr, dataDate, temp1, rh, light)
            self.writeMonitorData(dataDate, temp1, -999,rh,light,0)

    def close(self):
        self.db.close()

    
if __name__ == "__main__":
    print("dbConn main()")
    db = DbConn("greenhouse.db")
    #db.writeData(datetime.datetime.now(), 23, 25,52,1234)

    #db.importCsv("datalog.csv")
    
    edate = datetime.datetime.now()
    sdate = edate - datetime.timedelta(days=1.0)
    print (db.getMonitorData(sdate, edate))
    print (db.getMonitorData(sdate, edate, retDf=True))
    db.close()
