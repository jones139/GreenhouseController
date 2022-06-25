#!/usr/bin/env python3

import datetime
import sqlite3
import pandas as pd

class DbConn:
    def __init__(self,dbFname):
        self.db = sqlite3.connect(dbFname)

    def writeData(self,data_date,temp1, temp2, rh, light):
        # Note - triple quote for multi line string
        cur = self.db.cursor()
        cur.execute("""insert into 'environment'
        ('data_date', 'temp1', 'temp2', 'rh', 'light')
        values (?, ?, ?, ?, ?);""",
                        (data_date, temp1, temp2, rh, light))

        self.db.commit()

        
    def getData(self, sdate, edate, retDf=False):
        #print(sdate,type(sdate), edate, type(edate))
        queryStr = """select data_date, temp1, temp2, rh, light from environment where data_date >= ? and data_date <= ?;"""
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
            self.writeData(dataDate, temp1, -999,rh,light)

    def close(self):
        self.db.close()

    
if __name__ == "__main__":
    print("dbConn main()")
    db = DbConn("greenhouse.db")
    #db.writeData(datetime.datetime.now(), 23, 25,52,1234)

    db.importCsv("datalog.csv")
    
    edate = datetime.datetime.now()
    sdate = edate - datetime.timedelta(days=1.0)
    print (db.getData(sdate, edate))
    print (db.getData(sdate, edate, retDf=True))
    db.close()
