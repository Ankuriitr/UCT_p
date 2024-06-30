# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 17:25:34 2021

This code is written by Ankur Kumar, DD Imaging Lab, Physics, IIT Roorkee
It controls two stepper motors, a DSO, and Wave generator.
The stepper motors are controlled via Arduino.
This code perform the 2D Ultrasound CT scanning of the object.
# function [scan_time,Exp_loc,filename]= ScanUCT(file_address,Exp_name,N_packets,distance,ard_port,wave_type,freq,amplitude,rise_time,fall_time,N_rot,N_translation)
# 24/07/2021  Included automatic time division selection in the DSO and automatic object placing.

@author: Ankur
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import serial
import pyvisa
import time
from acq_dso_data import *
from W_matrix import *
from proj_dtrnd import *
from reconstruct import *
from time import sleep

  
# store starting time
begin = time.time()
# INPUT
os.chdir(r'E:\Ankur\Python\Test_folder')
file_address=r'E:\Ankur\Python\Test_folder' 
Exp_name='Testing_Al'
N_packets=7
distance=22                             # in mm.
ard_port='COM5'
wavetype='PULSE'
freq=1500000
amplitude=20
rise_time=0.0000000104
fall_time=0.0000000084
pulse_width=0.0000000290
# Rotation angles are taken from 1 degree to 180 degree for iradon based reconstruction.
# Otherwise max_rot_angle will be 360 for MART.
max_rot_angle=180           
NR=15       
NT=15
# scp=0; % set this 0 for manual positioning of the starting scanning point.

N_rot=NR;
N_translation=NT
Exp_name=Exp_name+'AL_WP10_f'+str(freq)+'MHz_NT'+str(NT)+'NR'+str(NR)
path=os.path.join(file_address,Exp_name)
fldr_exist=os.path.isdir(path)

if fldr_exist==False:
    os.mkdir(Exp_name)
    
Exp_loc=path                    # All data will be saved here.

#### Connceting the devices
## Connecting Arduino
arduino=serial.Serial(port='COM5', baudrate=9600, timeout=.1)
print('Arduino Connected\n')

# Comments: We create a serial communication object on port COM4
# in your case, the Ardunio microcontroller might not be on COM4, to
# double check, go to the Arduino editor, and on click on "Tools". Under the "Tools" menu, there
# is a "Port" menu, and there the number of the.......... communication port should
# be displayed

# Define some other parameter, check the MATLAB help for more details
# InputBufferSize = 8;
# Timeout = 0.1;
# set(arduino , 'InputBufferSize', InputBufferSize);
# set(arduino , 'Timeout', Timeout);
# set(arduino , 'Terminator', 'CR');

rm = pyvisa.ResourceManager()
rm.list_resources()
## Connecting Wave Generator
wavegen=rm.open_resource('USB0::0xF4EC::0xEE38::SDG2XCAD2R3765::INSTR')

print(" \n Wave Generator Connected  \n")

## Connecting DSO
# Receiving data while communication header off.
dso=rm.open_resource('USB0::0x05FF::0x1023::3517N53447::INSTR')  # USB0=Type,0x05ff=Manufacturer iD,Model code,USBSerial number.
dso.write('COMM_HEADER OFF')
print("\n DSO Connected \n")

# Calculations to select the timebase according to the wavepackets.
period=1/freq
tim_div=N_packets*period/10
## To represent 2.33334...e-07 to 2e-07
# td=repr(tim_div)
# td1,td2=td.split('.')
# td21,td22=td2.split('e')
# tim_div_sent=float(td1)*pow(10,float(td22))
dso.write("TIME_DIV "+str(tim_div))        #set(deviceObj.Acquisition(1), 'Timebase', tim_div);
# Set Wave parameters for the instrument.
# value of rise, fall time,pulse width should be in sec.
# Units of freq in Hz, Amplitude in V.
# To set output on, C1:OUTP ON
# data1 = query(wavegen, '*IDN?');
# data2 = wavegen.query(wavegen, '*RST');

input_parameters='C1:BSWV WVTP,'+wavetype+',FRQ,'+str(freq)+',AMP,'+str(amplitude)+',WIDTH,'+str(pulse_width)+',RISE,'+str(rise_time)+',FALL,'+str(fall_time)
wavegen.write(input_parameters)
wavegen.write('C1:OUTP ON')
wave_data=wavegen.query('C1:BSWV?')

# Correcting the N_packets according to the output from the DSO. As it cant set
# timebase in desired way.
get1=dso.query("TIME_DIV?")        
# gtd1,gtd2=get1.split('V ')       # Required while comm header is on.
# gtd3,gtd4=gtd2.split(' ')
get_tim_div=float(get1)
N_packets=round(get_tim_div*10/period)      # Exact number of wave packets are corrected

# Calculations required to set the various parameters.
# Input Data: Direction, Distance and Speed.
# distance= object will move within this displacement.
# N_rot=4;   %No. of projections

speed=900                            #fix 550 for smooth movement    upper limit 1000.
direction=1                          #0 for Translation towards the stepper motor.
tmp_speed=2500-speed
one_mm_steps=200                     #Stepper steps in one mm movement.
#During Rotation, there shouldnt be any translational motion and vice-versa
no_translational_steps=0
no_rotational_steps=0

# Calculations required to set the various parameters.
# Input Data: Direction, Distance and Speed.
# distance=10;          %distance= object will move within this displacement.
dis_step_size=distance/N_translation
#nGle=max_rot_angle/N_rot

total_steps_dist=round(one_mm_steps*distance)   # Rounding to avoid the unexpected movement.
total_steps_rot=1600                            # Total stepper steps in one rotation.


# Calculating the no. of steps according to the distance(in mm).
# The threaded rod used have a pitch of 8mm/turn.
# Also the stepper motor is moving 1600 steps per turn. steps in one rotation=1600;
step_size_rotation=round(total_steps_rot/N_rot)    # stepper steps one in rotational step.
num_translation_steps=total_steps_dist/(one_mm_steps*dis_step_size)   # Total no of translational steps in the distance.
step_size_translation=round(total_steps_dist/num_translation_steps)   # Stepper steps in one translational steps.

# To format data to be sent to arduino in proper form.
# direction = 1 char, steps= 4 char(rotation) + 4 char(translation) , speed= 4 char .

data_to_arduino_rotation=str(0)+str(step_size_rotation).zfill(4)+str(no_translational_steps).zfill(4)+str(tmp_speed).zfill(4)

## Generating the Weight matrix for reconstruction.
beam=1
screen_width=distance
det_emit_dis=3.0
det_arr_width=distance
emit_arr_width=distance
# W=W_matrix(beam,NT,NR,screen_width,det_emit_dis,det_arr_width,emit_arr_width)  # For Parallel Beam, Beam =1.

channel='C1'           # Data acquired from this channel.
proj_data=np.zeros([NT,NR])
for rot in range(0,NR):

    a=pow((-1),(rot+1))
    if a==1:
        direction=0
    else:
        direction=1

    i=0
    data_to_arduino_translation=str(direction)+str(no_rotational_steps).zfill(4)+str(step_size_translation).zfill(4)+str(tmp_speed).zfill(4)
    
    # Linear Translation Loop.

    for dis in range(0,NT):
        arduino.write(data_to_arduino_translation.encode())     # Send the data to arduino in the required format.
        sleep(0.01)
        #d2=fscanf(arduino,'%d')                                # Translation #  =
        # Acquiring the data from DSO.
        data=acq_dso_data(dso,channel)
        f_name=str(rot)+'_'+str(i)+'.txt'
        filename=os.path.join(Exp_loc,f_name)
        with open(filename,'w') as f:                           # To save data to text file.
            np.savetxt(f,data)
            f.close()
        proj_data[dis,rot]=proj_dtrnd(filename,N_packets,0,0)      # Generate the projection data based on CLT.
        i=i+1

        ## End of linear translation loop
    if a==1:
        proj_data[:,rot]=np.flip(proj_data[:,rot])                           # As rotation are alternate. 
    
    # Data to arduino to rotate the object.
    arduino.write(data_to_arduino_rotation.encode());
    sleep(.01)
    # Image 1, The amplitude attenuation while object is translating linearly.
    fig1=plt.plot(proj_data)
    plt.xlabel('Distance')
    plt.ylabel('Amplitude')
    plt.title("Amplitude Attenuation")
    plt.show()
    plt.close()
    # if rot==0:
    #     proj_data_all=proj_data
    # else:
    #     proj_data_all=np.stack([proj_data_all,proj_data],axis=1)
    proj_data_all=proj_data
    proj_data_all=pow(proj_data_all,2)
    # Show sinogram of the data either row wise or pixel wise.
    proj_data_all_tpose=np.transpose(proj_data_all)
    fig2=plt.imshow(proj_data_all,cmap=plt.cm.Greys_r)
    plt.title("Sinogram")
    plt.show()
    plt.close()
    av_proj_data_all=np.average(proj_data_all)
    # proj_rcnst=(proj_data_all-av_proj_data_all)/max(proj_data_all.flatten())
    # Show reconstruction of the data either row wise or pixel wise.
    reconst_data=reconstruct(NR,NT,NT,sinogram,2)    # It take projection data in which rotations are stored in column.
    fig3=plt.imshow(reconst_data,cmap=plt.cm.Greys_r)
    plt.title("Reconstruction")
    plt.colorbar()
    plt.show()
    plt.close()
    
    ## End of rotation loop.

# To rotate the object to its initial position.
data_to_arduino_rotation=str(1)+str(1600).zfill(4)+str(no_translational_steps).zfill(4)+str(tmp_speed).zfill(4)
arduino.write(data_to_arduino_rotation.encode()) 
if NR%2==1:
    # To move the object at initial position. Movement towards stepper motor.
    data_to_arduino_translation=str(0)+str(no_rotational_steps).zfill(4)+str(distance*one_mm_steps).zfill(4)+str(tmp_speed).zfill(4)
    arduino.write(data_to_arduino_translation.encode())

## Processed data saving.
Processed_data='Processed_data'
p_data_path=os.path.join(Exp_loc,Processed_data)

fldr_exist=os.path.isdir(p_data_path)
if fldr_exist==False:
    os.mkdir(p_data_path)

# Saving the projection data (Sinogram).
proj_file=os.path.join(p_data_path,'Proj_data.txt');
with open(proj_file,'w') as f:                           # To save data to text file.
    np.savetxt(f,proj_data_all_tpose)
    f.close()
    
# store end time
end = time.time()
time_taken=end-begin

# Saving the triggered wave parameters data and N_packets.
wave_data_file=os.path.join(p_data_path,'wave_data.txt')
with open(wave_data_file,'w') as f:
    f.write(wave_data)
    f.write("\n\n N_packets = %d "% N_packets)
    f.write("\n\n Time Taken = %f" %time_taken)
    f.write("\n Distance linearly translated= %f" %distance)
    f.close()

# Saving the Final Sinogram and Reconstructed image.
# Sinogram Image.
sino_path=os.path.join(p_data_path,'sinogram.tiff')
fig4=plt.imshow(proj_data_all)
plt.title("Sinogram")
plt.savefig(sino_path,dpi=plt.gcf().dpi)  
plt.show()  
plt.close()  


# Reconstructed Image
reco_path=sino_path=os.path.join(p_data_path,'reconstruction.tiff')
fig5=plt.imshow(reconst_data)
plt.title("Reconstruction")       
plt.savefig(reco_path)
plt.show() 
plt.close()    
# Close the connected devices
arduino.close()
dso.close()
wavegen.close()

