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
    db = dbConn.DbConn(dbPath)
    df = db.getData(sdate, edate, retDf=True)
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
    
