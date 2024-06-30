# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:12:32 2021
To acquire data from DSO and convert it any array of time and anplitude

@author: Ankur, DD Imaging lab, IIT Roorkee.
"""
def acq_dso_data(dso,channel):
    import pyvisa
    import numpy as np
    # Turning the comm header off.  Required: otherwise we have to also account for it.
    dso.write("COMM_HEADER OFF")
    
    # # Setting the Sample size to be acquired.
    # Sample_size=10e+4
    # Sample_size=str(Sample_size)
    # dso.write('MSIZ'+Sample_size)
    
    time_div=float(dso.query("TIME_DIV?"))
    
    #dso.write("TIME_DIV 10E-6")
    # get horizontal interval and convert to float
    d = dso.query(channel+':INSPECT? \'HORIZ_INTERVAL\'')
    idx1 = d.find(':')
    idx2 = d.find('e')
    dt = float(d[idx1 + 2:idx2 + 4])
    total_time_sampleon_display=time_div*10/dt    #Display have 10 time divisions.
    
    #Acquiring the data only.
    dso.write(channel+":INSPECT? DATA_ARRAY_1")
    data1=dso.read()
    len_data1=len(data1)
    
    # data2=dso.write("C1:WAVEFORM? DATA_ARRAY_2")
    dso.query("COMM_FORMAT?")
    set_comm_format=dso.write("COMM_FORMAT , BYTE")
    
    # Converting the data1 to list array.
    data1=data1.replace('"','') 
    data1=data1.replace('\r','') 
    data1=data1.replace('\n','') 
    len_data1=len(data1)
    d_arr_len=round(len_data1/14)
    data1_array=[0]*d_arr_len
    
    for i in range(0,d_arr_len):
        data1_array[i]=float(data1[i*14:(i+1)*14])
    
    amp_len=len(data1_array)
    # Generating the time array.
    time1 = np.arange(0, amp_len * dt, dt)
    data=np.stack([time1,data1_array],axis=1)
    return data
