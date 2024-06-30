# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 17:47:06 2022

@author: Eyepod
"""

import numpy as np
import pyvisa
import time

from acq_dso_data import *

freq=1500000

rm = pyvisa.ResourceManager()
rm.list_resources()
## Connecting DSO
# Receiving data while communication header off.
dso=rm.open_resource('USB0::0x05FF::0x1023::3517N53447::INSTR')  # USB0=Type,0x05ff=Manufacturer iD,Model code,USBSerial number.
dso.write('COMM_HEADER OFF')
print("\n DSO Connected \n")
channel='C1' 

time_w=np.zeros([100,7])
time_r=np.zeros([100,7])
time_acq=np.zeros([100,7])
tim_div=[10,20,50,100,200,500,1000]

for N_packets in range(0,7):
        
    # Calculations to select the timebase according to the wavepackets.
    ## To represent 2.33334...e-07 to 2e-07
    # td=repr(tim_div)
    # td1,td2=td.split('.')
    # td21,td22=td2.split('e')
    # tim_div_sent=float(td1)*pow(10,float(td22))
    dso.write("TIME_DIV "+str(tim_div[N_packets]*pow(10,(-9))))        #set(deviceObj.Acquisition(1), 'Timebase', tim_div);
    
    # Correcting the N_packets according to the output from the DSO. As it cant set
    # timebase in desired way.
    get1=dso.query("TIME_DIV?")        
    # gtd1,gtd2=get1.split('V ')       # Required while comm header is on.
    # gtd3,gtd4=gtd2.split(' ')
    get_tim_div=float(get1)
    
    data=acq_dso_data(dso,channel)
    
    #For data acq Speed
    for i in range(0,100):
        time_acq1=time.time()         
        data=acq_dso_data(dso, channel)       
        time_acq2=time.time()   
        time_acq[i,N_packets]=time_acq2-time_acq1
    
    # For write time.
    
    for i in range(0,100):
        time_write1=time.time()
        filename='E:\\Ankur\\P4_docs\\Test_data_temp\\Python\\'+str(N_packets)+'_'+str(i)+'.txt'
        with open(filename,'w') as f:                           # To save data to text file.
            np.savetxt(f,data)
            f.close()
        time_write2=time.time()
        time_w[i,N_packets]=time_write2-time_write1
    
    
    #For read speed
    for i in range(0,100):
        time_read1=time.time()       
        filename='E:\\Ankur\\P4_docs\\Test_data_temp\\Python\\'+str(N_packets)+'_'+str(i)+'.txt'
        data=np.loadtxt(filename)
        time_read2=time.time()     
        time_r[i,N_packets]=time_read2-time_read1
    

        
        
dso.close()     
   
time_write_file='E:\\Ankur\\P4_docs\\Time_analysis\\Python\\Write_files.dat'
with open(time_write_file,'w') as f:                           # To save data to text file.
    np.savetxt(f,time_w)
    f.close()
    
time_read_file='E:\\Ankur\\P4_docs\\Time_analysis\\Python\\Read_files.dat'
with open(time_read_file,'w') as f:                           # To save data to text file.
    np.savetxt(f,time_r)
    f.close()

time_acq_file='E:\\Ankur\\P4_docs\\Time_analysis\\Python\\Data_acq.dat'
with open(time_acq_file,'w') as f:                           # To save data to text file.
    np.savetxt(f,time_acq)
    f.close()
    
    