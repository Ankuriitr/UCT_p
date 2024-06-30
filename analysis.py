# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 15:33:59 2021

@author: Ankur
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.signal import find_peaks_cwt
from reconstruct import *
import xlrd
address='D:\Ankur Research Data\AUCT Data\DataF1Mhz\AL_WP5_f1MHz_NT15_NR25\Processed_data'
file='Proj_data.xls'
filename=os.path.join(address,file)
proj=pd.read_excel(filename,header=None)
proj=proj.to_numpy()
NT=15
NR=25
method=3
N_pixel=15
image=reconstruct(NR,NT,N_pixel,proj,method)
image=np.square(image)
# plt.imshow(image)
# plt.colorbar()
# plt.show()

fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("Reconstruction\nFiltered back projection")
ax1.imshow(image)
ax2.set_title("Sinogram")
ax2.imshow(proj)
plt.show()
