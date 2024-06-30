# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 15:22:34 2021
This code is written by Ankur Kumar, DD Imaging Lab, Physics, IIT Roorkee
This code reconstruct the image from projection data for various methods.
Method 1= MART 1
Method 2= MART 3
Method 3= iradon
@author: Ankur
"""
import numpy as np
# from skimage.data import shepp_logan_phantom
# from skimage.transform import radon, rescale
from skimage.transform import iradon
from MART import *
from proj_dtrnd import *
from W_matrix import *

def reconstruct(NR,NT,N_pixel,proj,method):
    

    # NR=18
    # NT=9
    # proj=np.random.rand(9,18)
    # N_pixel=9
    # method=1
    # M=NR*NT
    # N=N_pixel*N_pixel
    # exon=1
    max_iter=100
    accuracy=0.001
    u=0.8
    beam=1
    screen_width=28
    det_arr_width=24
    emit_arr_width=24
    det_emit_dis=30
    # max_rot=360
    angles=np.linspace(0.0, 180.0, NR, endpoint=False)   # [0:max_rot/NR:(max_rot-max_rot/NR)]
    
    if method==1 or method==2:
        # generating the weight matrix.
        W=W_matrix(beam,NT,NR,screen_width,det_emit_dis,det_arr_width,emit_arr_width)
    
    # Method 1
    if method==1:
        rec_image=MART(W,proj,NT,NR,accuracy,u,max_iter,1)   # Mart_num =1 
        rec_image=np.reshape(rec_image,(N_pixel,N_pixel))
    # Method 2
    elif method==2:
        rec_image=MART(W,proj,NT,NR,accuracy,u,max_iter,3)   # Mart_num =3
        rec_image=np.reshape(rec_image,(N_pixel,N_pixel))
    # Method 3
    else:
        rec_image=iradon(proj,theta=angles,filter_name='ramp')   
        
    return rec_image