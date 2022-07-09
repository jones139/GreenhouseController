#!/usr/bin/env python3

import os
import datetime
import dbConn
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # avoid warnings about GUIs and threads
import matplotlib.pyplot as plt


def plotGraphs(dbPath, dataFolder, timeSpanDays, averageStr='H'):
    # create plots of hourly data for web interface
    edate = datetime.datetime.now()
    sdate = edate - datetime.timedelta(days=timeSpanDays)

    # Monitoring Data
    db = dbConn.DbConn(dbPath)
    df = db.getMonitorData(sdate, edate, retDf=True)

    df['data_date'] = pd.to_datetime(df['data_date'])
    df.index=df['data_date']

    if averageStr is not None:
        df = df.resample(averageStr).mean()

    plotTempRhGraph(df,
                    "GreenHouse History (temperature)\n(to %s)"
                    % (df.index[-1].strftime("%d-%m-%y %H:%M")),
                    os.path.join(dataFolder,"chart1.png")
                    )

    plotLightGraph(df,
                   "GreenHouse History (light level)\n(to %s)"
                   % (df.index[-1].strftime("%d-%m-%y %H:%M")),
                   os.path.join(dataFolder,"chart2.png")
                   )

    plotSoilGraph(df,
                   "GreenHouse History (Soil Resistance)\n(to %s)"
                   % (df.index[-1].strftime("%d-%m-%y %H:%M")),
                   os.path.join(dataFolder,"chart3.png")
                   )

    # Watering Data
    df = db.getWaterData(sdate, edate, retDf=True)
    df['data_date'] = pd.to_datetime(df['data_date'])
    df.index=df['data_date']

    plotWaterGraph(df,
                   "GreenHouse History (Water Status)\n(to %s)"
                   % (df.index[-1].strftime("%d-%m-%y %H:%M")),
                   os.path.join(dataFolder,"chart4.png")
                   )

    db.close()
    del df
    
    
def plotTempRhGraph(df, titleStr, outFname):
    fig, ax = plt.subplots()
    df.plot(ax=ax, y='temp2')#, x='data_date')
    df.plot(ax=ax, y='rh')#, x='data_date')
    dateFormat = matplotlib.dates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(dateFormat)
    ax.set_ylabel("Temp (degC) / RH (%)")
    ax.set_ylim((0,100))
    ax.set_xlabel("Time (hh:mm)")
    ax.grid(True)
    ax.set_title(titleStr)
    fig.savefig(outFname)
    print("Figure saved to %s" % outFname);
    

def plotLightGraph(df, titleStr, outFname):
    # Light Chart
    fig, ax = plt.subplots()
    df.plot(ax=ax, y='light')#, x='data_date')
    dateFormat = matplotlib.dates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(dateFormat)
    ax.set_ylabel("Light Level (lux)")
    ax.set_xlabel("Time (hh:mm)")
    ax.grid(True)
    ax.set_title(titleStr)
    fig.savefig(outFname)
    print("Figure saved to %s" % outFname);

def plotSoilGraph(df, titleStr, outFname):
    # Soil Moisture Chart
    fig, ax = plt.subplots()
    df.plot(ax=ax, y='soil')#, x='data_date')
    dateFormat = matplotlib.dates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(dateFormat)
    ax.set_ylabel("Soil Resistance (adc counts)")
    ax.set_ylim(10000,15000)
    ax.set_xlabel("Time (hh:mm)")
    ax.grid(True)
    ax.set_title(titleStr)
    fig.savefig(outFname)
    print("Figure saved to %s" % outFname);

def plotWaterGraph(df, titleStr, outFname):
    # Watering Status Chart
    fig, ax = plt.subplots()
    df.plot(ax=ax, y='waterStatus')#, x='data_date')
    dateFormat = matplotlib.dates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(dateFormat)
    ax.set_ylabel("Watering Status")
    ax.set_xlabel("Time (hh:mm)")
    ax.grid(True)
    ax.set_title(titleStr)
    fig.savefig(outFname)
    print("Figure saved to %s" % outFname);


if __name__ == "__main__":
    print("graphs.py.__main__")
    plotGraphs(os.path.join("/home/graham/GreenhouseController/greenhouseServer/www/data","greenhouse.db"), "/home/graham/GreenhouseController/greenhouseServer/www/data", 2.0, 'H')
