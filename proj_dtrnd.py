"""This code process the AUCT generated data to find the projection data of a single file.
The proj_data values are peak to peak values with outliers removed.
It take the mean of the final amplitudes.
filename: name of the data file
Select trend ==1 if you see significant trend in the data.
NOTE: Selecting the trend slowdown the timing efficiency.
@Author = ANKUR
"""
def proj_dtrnd(filename,N_packets,pulsedata,trend):
    import pandas as pd
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import find_peaks
    from scipy.signal import find_peaks_cwt
    #function [proj_data]=proj_dtrnd(filename,N_packets,num_peak,pulsedata,trend)
    # address='D:\Ankur Research Data\AUCT Data\DataF1Mhz\AL_WP5_f1MHz_NT5_NR5'
    # trend=1
    # N_packets=5;
    # num_peak=10;
    # pulsedata=0;
    # file='3_3.xls'
    # filename=os.path.join(address,file)
    if type(pulsedata)==int:
        pulsedata=np.loadtxt(filename)
    
    time=pulsedata[:,0]
    Amp=pulsedata[:,1]
    
    # To remove any offset in amplitude.
    Amp=Amp-np.average(Amp)
    N_rows=len(Amp)
    Length_of_Single_Packet=round(N_rows/N_packets)-1;
 #   trans_peak_amp=np.zeros(N_packets)
    trans_peak_time=np.zeros(N_packets)
    trans_trough=np.zeros(N_packets)
    trans_trough_time=np.zeros(N_packets)
    
    # trans_ptp_trough1=[];trans_ptp_trough_time1=[];
    
    # Some transmission data have noise only and does not contribute to
    # the actual result. Discarding those signal files based on the
    # amplitude difference.
    # This code also checks if the data have trend.
    # If significant trend found, signal is detrended.
    # To check if the data have trend affecting the peak detection.
    def allNumAvg(values):
        return np.average(values)
    
    def posNumAvg(values):
        arr_v = np.asarray(values) 
        return np.average(arr_v[arr_v>0]) 
    
    def negNumAvg(values):
        arr_v = np.asarray(values) 
        return np.average(arr_v[arr_v<0]) 
    
    nmean=negNumAvg(Amp)
    if trend==1:
        pmean=posNumAvg(Amp)
        nmean=negNumAvg(Amp)
        sum_pnmean=pmean-nmean
        opol = 20;
        p= np.polyfit(time,Amp,opol)           # fit the data.
        f_y = np.polyval(p,time)        # generate the ploynomial to subtract.
        
        Amp1 = Amp - f_y
        # To check whether their is significant trend. 
        # Only taking the positive amplitudes. 
        pmean1=posNumAvg(Amp1)
        nmean1=negNumAvg(Amp1)
        sum_pnmean1=pmean1-nmean1;
        if sum_pnmean>sum_pnmean1*2:
            Amp=Amp1;
    # plt.plot(time,Amp)
    # plt.show()
    j=0  
    D=Amp[(j*Length_of_Single_Packet+1):((j+1)*Length_of_Single_Packet)]
#   D=D.reset_index(drop=True)     # Required if pandas dataframe are used.
#   pandas is used in case of excel file.
    T=time[(j*Length_of_Single_Packet+1):((j+1)*Length_of_Single_Packet)]
#   T=T.reset_index(drop=True)
    #obtaining peaks
    height=2*nmean
    npeaks,_=find_peaks(Amp*(-1),height=height,distance=0.9*len(D)) 
    ppeaks=np.zeros([len(npeaks)])
    for i in range(0,len(npeaks)):
        # Positive Peak will be searched only in between these.
        # Proximity of the peak to peak possibility is in between 100 data points.
        proximity=100
        if npeaks[i]>proximity:
            l_bound=npeaks[i]-proximity     
        else:
            l_bound=0
            
        u_bound=npeaks[i]+proximity
        #peak=max(Amp[l_bound:u_bound])
        pp=np.argmax(Amp[l_bound:u_bound])
        ppeaks[i]=l_bound+pp
    
    ppeaks=ppeaks.astype(int)
    # plt.plot(Amp)
    # plt.plot(npeaks, Amp[npeaks], "x")
    # plt.plot(ppeaks, Amp[ppeaks], "x")
    # plt.plot(np.zeros_like(Amp), "--", color="gray")
    # plt.show()  
    # x=trans_peak_amp
    # bound=5
    def rmoutliers(x,bound):                   # Bound is the %age above and below average.
        len_x=len(x)
        avg_x=np.average(x)
        bound_val=avg_x*bound/100
        neg_bound=avg_x-bound_val
        pos_bound=avg_x+bound_val
        y=[]
        for i in range(0,len_x):
            # print(i)
            if ((x[i]<pos_bound) and (x[i]>neg_bound)):
                #print('x=',x[i],'\t\t','avg=',avg_x,'\n')
                y.append(x[i])
                #print(y)
        return y
    
    trans_peak_amp=np.zeros(len(npeaks))
    for i in range(0,len(npeaks)):   
        a=Amp[ppeaks[i]]
        b=Amp[npeaks[i]]
        # print('a= \t b= \n',abs(a),abs(b))
        trans_peak_amp[i]=abs(a)+abs(b)
        # print('Trans_peak_Amp=',trans_peak_amp[i])
        
    # Finding the average transmitted amplitude by averaging out peaks and troughs and removing outliers.
    mag_abs_peak_ro=rmoutliers(trans_peak_amp,25)
    proj_data=np.average(mag_abs_peak_ro)
    
    if proj_data<.5*np.average(trans_peak_amp):
        proj_data=.7*max(trans_peak_amp)
    
    return proj_data
