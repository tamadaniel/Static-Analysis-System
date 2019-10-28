import matplotlib.pyplot as plt
import numpy as np
from gatspy.periodic import LombScargleFast

import pandas as pd
from pandas.tseries.frequencies import to_offset

import elipse as el

from scipy import signal

def resample(tseries, rate='10ms', short_rate=None, max_gap=None):
    """ Resample (unevenly spaced) timeseries data linearly by first upsampling to a
        high frequency (short_rate) then downsampling to the desired rate.
    
    :param tseries: a pandas timeseries object
    :param rate: rate that tseries should be resampled to
    :param short_rate: intermediate upsampling rate; if None, smallest interval of tseries is used
    :param max_gap: null intervals larger than `max_gap` are being treated as missing
        data and not interpolated. if None, always interpolate. must be provided as pandas
        frequency string format, e.g. '6h'
        
    Copyright (c) 2017 WATTx GmbH
    License: Apache License
    """
    # return series if empty
    if tseries.empty:
        return tseries

    # check for datetime index
    assert isinstance(
        tseries.index[0], pd.tslib.Timestamp), 'Object must have a datetime-like index.'

    # sort tseries by time
    tseries.sort_index(inplace=True)

    # create timedelta from frequency string
    rate_delta = to_offset(rate).delta

    # compute time intervals
    diff = np.diff(tseries.index) / np.timedelta64(1, 's')

    if max_gap is not None:
        # identify intervals in tseries larger than max_gap
        idx = np.where(np.greater(diff, to_offset(max_gap).delta.total_seconds()))[0]
        start = tseries.index[idx].tolist()
        stop = tseries.index[idx + 1].tolist()
        # store start and stop indices of large intervals
        big_gaps = list(zip(start, stop))

    if short_rate is None:
        # use minimal nonzero interval of original series as short_rate
        short_rate = '%dS' % diff[np.nonzero(diff)].min()
        # create timedelta from frequency string
        short_rate_delta = to_offset(short_rate).delta
        # if smallest interval is still larger than rate, use rate instead
        if short_rate_delta > rate_delta:
            short_rate = rate
    else:
        # convert frequency string to timedelta
        short_rate_delta = to_offset(short_rate).delta
        # make sure entered short_rate is smaller than rate
        assert rate_delta >= short_rate_delta, 'short_rate must be <= rate'

    # upsample to short_rate
    tseries = tseries.resample(short_rate, how='mean').interpolate()

    # downsample to desired rate
    #tseries = tseries.resample(rate, how='ffill')
    tseries = tseries.resample(rate).ffill()

    # replace values in large gap itervals with NaN
    if max_gap is not None:
        for start, stop in big_gaps:
            tseries[start:stop] = None

    return tseries

def graph(name):
    
    i=0
    for i in range(len(name)):
        df=pd.read_csv(name[i]+'.csv',sep=',',parse_dates=[0])
        df['time']=pd.to_datetime(df['datetime'])        
        
        x=df['x']
        x=x.values
        y=df['y']
        y=y.values

        topLeft=df['topLeft']
        topLeft=topLeft.values
        topRight=df['topRight']
        topRight=topRight.values
        bottomLeft=df['bottomLeft']
        bottomLeft=bottomLeft.values
        bottomRight=df['bottomRight']
        bottomRight=bottomRight.values

        datetime=df['datetime']
        datetime=datetime.values

        time=df['time']
        time=time.values 

        time=time.astype(np.int64)/10**5 #ns -> ms 
        time=time-time[0] ## starts from 0ms
        
    ########################################################
    ################### Outlier remover #####################
    ########################################################

        a = np.array(x)
        a=sorted(a)
        Q3 = np.percentile(a, 75)
        Q1 = np.percentile(a, 25)
        IQR = (Q3 - Q1)

        j=0
        while j < len(x):
            if (x[j] < (Q1 - 1.5 * IQR)) |(x[j] > (Q3 + 1.5 * IQR)):
                # print(time[i])
                time=np.delete(time,j)
                datetime=np.delete(datetime,j)
                x=np.delete(x,j)
                y=np.delete(y,j)
                topLeft=np.delete(topLeft,j)
                topRight=np.delete(topRight,j)
                bottomLeft=np.delete(bottomLeft,j)
                bottomRight=np.delete(bottomRight,j)
                
                j=j-2
            j+=1
  ########################### save as pandas format #######################
    data={
        'datetime':datetime,
        'x':x,
        'y':y,
        'topLeft':topLeft,
        'topRight':topRight,
        'bottomLeft':bottomLeft,
        'bottomRight':bottomRight,
    }

    df=pd.DataFrame(data)
    df = df.set_index('datetime')
    df.to_csv('2.csv')

    series_resample=resample(df,'10ms','1ms')
    series_resample.to_csv(name[i]+'.csv')

    ################### imports the regular sample data #################
    df=pd.read_csv(name[i]+'.csv',sep=',',parse_dates=[0])
    df['time']=pd.to_datetime(df['datetime'])        
    
    x=df['x']
    x=x.values
    y=df['y']
    y=y.values

    topLeft=df['topLeft']
    topLeft=topLeft.values
    topRight=df['topRight']
    topRight=topRight.values
    bottomLeft=df['bottomLeft']
    bottomLeft=bottomLeft.values
    bottomRight=df['bottomRight']
    bottomRight=bottomRight.values

    datetime=df['datetime']
    datetime=datetime.values

    time=df['time']
    time=time.values 

    time=time.astype(np.int64)/10**6 #ns -> ms 
    time=(time-time[0]) ## starts from 0s
    time=[float(i) for i in time]

    seconds=[]
    for i in range(len(time)):
        seconds.append(time[i]/1000)
    time=seconds
    ##############################
    ####################### Low pass filter #################

    # fs=100 #10ms - 100hz
    # fc = 12  # Cut-off frequency of the filter
    # w = fc / (fs / 2) # Normalize the frequency
    # order=5
    # b, a = signal.butter(order, w, btype='low',analog = False)
    # output = signal.filtfilt(b, a, x)
    # plt.figure(num=3,figsize=(80,60))
    # plt.plot(time, output, label='filtered')
    # plt.title('x filter', fontsize=24)
    
#########################  Figures ###################
##################### x,y vs t ###################
    
    plt.figure(num=1,figsize=(80,60))
    plt.subplot(2,1,1)
    plt.plot(time,x)
    #plt.plot(time,x, linestyle ='--', marker='o', color='b') #shows markes on data

    plt.title('(x,y) vs time', fontsize=24)
    plt.ylabel('x (normalized)', fontsize=18)
    plt.rc('font', size=18)

    plt.subplot(2,1,2)
    plt.plot(time,y)
    plt.xlabel('time (ms)', fontsize=18)
    plt.ylabel('y (normalized)', fontsize=18)
    plt.rc('font', size=18)

######################## x vs y ###################

    plt.figure(num=2,figsize=(80,60))
    plt.plot(x, y)
    plt.title('x vs y', fontsize=24)
    plt.ylabel('y (normalized)', fontsize=18)
    plt.xlabel('x (normalized)', fontsize=18)
    plt.rc('font', size=18)
    
    # plt.xlim(-1, 1) #graph axis limits
    # plt.ylim(-1, 1)
    # plt.axhline(0, color='b', linestyle='-') #horizontal line
    # plt.axvline(0, color='b', linestyle='-') #vertical line
            
##################### Frequency analysis ###################
##################### Lomb-Scargle Power ###################
    
    # xmodel = LombScargleFast().fit(time, x)
    # xperiods, xpower = xmodel.periodogram_auto()
    # xfrequencies = 1 / xperiods
        
    # ymodel = LombScargleFast().fit(time, y)
    # yperiods, ypower = ymodel.periodogram_auto()
    # yfrequencies = 1 / yperiods
    
    # plt.figure(num=4,figsize=(80,60))
    # plt.subplot(2,1,1)
    # plt.plot(xfrequencies, xpower)
    # plt.title('Lomb-Scargle Power', fontsize=24)
    # plt.rc('font', size=18)
    # plt.grid()
    # plt.ylabel('x', fontsize=18)
    # plt.xlim(0, 2) #graph axis limits
    
    # plt.subplot(2,1,2)
    # plt.plot(yfrequencies,ypower)
    # plt.xlabel('frequency (hz)', fontsize=18)
    # plt.ylabel('y', fontsize=18)
    # plt.rc('font', size=18)
    # plt.grid()
    # plt.xlim(0, 2) #graph axis limits

    ############################ Elipse #####################################

    fig, ax_kwargs = plt.subplots(figsize=(6, 6))
    plt.title('Ellipse - x vs y ', fontsize=24)
    plt.ylabel('y (normalized)', fontsize=18)
    plt.xlabel('x (normalized)', fontsize=18)
    plt.rc('font', size=18)

    # Plot the ellipse with zorder=0 in order to demonstrate
    # its transparency (caused by the use of alpha).
    ellipse,ell_radius_x,ell_radius_y,rotation=el.confidence_ellipse(x, y, ax_kwargs,
        alpha=0.5, facecolor='pink', edgecolor='purple', zorder=0)
    # ax.add_patch(ellipse)
    print(ell_radius_x)
    print(ell_radius_y)
    print((rotation))

    ##################### Elipse Area ######################
    area=3.1415*ell_radius_x*ell_radius_y
    print(area)
    ax_kwargs.scatter(x, y, s=0.5)

    ##################### Path length ######################
    length = el.pathlength(x,y)
    print (length)

    plt.show()
