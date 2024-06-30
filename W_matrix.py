# Code for generating the weight matrix.
"""
Created on Thu Sep 23 18:49:55 2021

@author: Ankur
"""
""" This code is written by Ankur, DD Imaging Lab, IITR.
This code returns the 2D weight matrix for parallel and fanbeam.
""" 
def W_matrix(beam,N_translation,N_rot,screen_width,det_emit_dis,det_arr_width,emit_arr_width):
    import numpy as np
    import math
    import matplotlib.pyplot as plt
    
    # The input variables.
    
    # beam=1                                                     # Select 1 for parallel beam and otherwise for fanbeam.
    # N_translation=30
    # N_rot=30
    # screen_width=12.0                                           # Pixels are located in the screen.
    # det_emit_dis=15.0
    # det_arr_width=10.0                                          # Detector array width.
    # emit_arr_width=10.0                                         # Emitter array width.

        
    
    fanbeam_angle=45.0                                          # Fanbeam angle.
    ndet=N_translation                                        # No. of detector= no. of linear translation for single det. UCT.
    max_rot=360.0
    start_angle=0.0
    theta=((max_rot-start_angle)/N_rot)*math.pi/180
    theta_max=max_rot*math.pi/180
    npixel=N_translation                                      # Number of pixels in each array.

    def decimal_range(start,stop,increment):
        while start < stop: # and not math.isclose(start, stop): Py>3.5
            yield start
            start += increment

    
    sx=np.zeros([ndet,1])
    sy=np.zeros([ndet,1])                 # Source initial coordinates array.
    dx=np.zeros([ndet,1])
    dy=np.zeros([ndet,1])                 # Detector initial coordinates array.
    px=np.zeros([ndet+1,1])
    py=np.zeros([ndet+1,1])               # pixel coordinates array.
    # screen and detectors position coordinates calculation based on the beam type.
    # For PARALLEL beam  
    if (beam==1):                                                                   
        for i in range(0,ndet): 
     #       print('i= \t',i)                            
            sx[i]=-det_emit_dis/2                             # x coordinates of source.
        for i in range(0,ndet):
            sy[i]=emit_arr_width/2-i*emit_arr_width/(ndet-1)
        for i in range(0,ndet):
            dx[i]=det_emit_dis/2
        for i in range(0,ndet):
            dy[i]=det_arr_width/2-i*det_arr_width/(ndet-1)
    # For FANBEAM.
    else:                                                        
        for i in range(0,ndet):
            sx[i]=-det_emit_dis/2
            sy[i]=0;
        for i in range(0,ndet):
            dx[i]=det_emit_dis*math.cos((fanbeam_angle/2-i*fanbeam_angle/(ndet-1))*math.pi/180)+sx[i]
        for i in range(0,ndet):
            dy[i]=det_emit_dis*math.sin((fanbeam_angle/2-i*fanbeam_angle/(ndet-1))*math.pi/180)
    xpixel=screen_width/npixel;
    ypixel=xpixel
    px[0]=-screen_width/2                                     # dividing into two parts such that centre lie in the middle point.
    for i in range(1,(npixel+1)):                             # Finding the coordinates of pixels. 
            px[i]=px[0]+i*xpixel
    py[0]=-screen_width/2
    for i in range(1,(npixel+1)):     
        py[i]=py[0]+(i)*ypixel
    yul=float(py[npixel])                                            # upper limit of y coordinates.
    yll=float(py[0])                                                 # Lower limit of y coordinates.
    xul=float(px[npixel])                                            # upper limit of x coordinates.   
    xll=float(px[0])                                                 # Lower limit of x coordinates.
    row=ndet*N_rot
    colmn=pow(npixel,2)
    L=np.zeros([row,colmn])                                   # defining the size of the final distance matrix.
    rloop=0
    for r in decimal_range(start_angle,theta_max-theta/2,theta):        #For loop for rotations.
        rloop=rloop+1
        # print('r= \t',r)
    #     angle=180/pi*r;
    
        inty=np.zeros([npixel+1,1])
        intx=np.zeros([npixel+1,1])
        for i in range(0,ndet):                                          #For loop for each detector for each rotation.
            xtemp1=[]
            ytemp1=[]
            xtemp2=[]
            ytemp2=[]
            
            # for p in range(0,npixel+2):
            #     print(p)
            #     xtemp3=0
            #     ytemp3=0
            vy=(sy[i]*math.cos(r)-sx[i]*math.sin(r))
            vx=(sx[i]*math.cos(r)+sy[i]*math.sin(r))
            dyyy=(dy[i]*math.cos(r)-dx[i]*math.sin(r))
            dxxx=(dx[i]*math.cos(r)+dy[i]*math.sin(r))
    #finding y coordinates of intersection points.
            for j in range(0,npixel+1):
                inty[j]=((dyyy-vy)/(dxxx-vx))*(px[j]-vx)+vy
                if (inty[j]>=yll) and (inty[j]<=yul):
                    xtemp=float(px[j])
                    ytemp=float(inty[j])
                    xtemp1=xtemp1+[xtemp]
                    ytemp1=ytemp1+[ytemp]
                    # print(inty[j])
                    
            xtemp2=xtemp1
            ytemp2=ytemp1
    #finding x coordinates on intersection points.
            for j in range(0,npixel+1):
                intx[j]=((dxxx-vx)/(dyyy-vy))*(py[j]-vy)+vx
                if (intx[j]>=xll) and (intx[j]<=xul):
                    ytemp=float(py[j])
                    xtemp=float(intx[j])
                    ytemp2=ytemp2+[ytemp]
                    xtemp2=xtemp2+[xtemp]
            
            if (dyyy>=0) and (dxxx>=0):          # Quadrant 1, x and y are positive.
                ytemp2.sort()
                xtemp2.sort()
                for j in range(0,len(ytemp2)-1):
                    for s in range(0,ndet):
                        lim1=yul-s*ypixel
                        lim2=yul-(s+1)*ypixel
                        if (ytemp2[j]<lim1) and (ytemp2[j]>=lim2):
                            for n in range(0,npixel):
                                lim3=xll+n*xpixel
                                lim4=xll+(n+1)*xpixel
                                if (xtemp2[j]>=lim3) and (xtemp2[j]<lim4):
                                    L[npixel*(rloop-1)+i,npixel*s+n]=math.sqrt(pow((ytemp2[j]-ytemp2[j+1]),2)+pow((xtemp2[j]-xtemp2[j+1]),2))
       
            elif (dyyy<0) and (dxxx>0):           # Quadrant 2, x  positive and y are negative.
                ytemp2.sort(reverse=True)
                xtemp2.sort()
                for j in range(0,len(ytemp2)-1):
                    for s in range(0,ndet):
                        lim1=yul-s*ypixel
                        lim2=yul-(s+1)*ypixel
                        if (ytemp2[j]<lim1) and (ytemp2[j]>=lim2):
                            for n in range(0,npixel):
                                lim3=xll+n*xpixel
                                lim4=xll+(n+1)*xpixel
                                if (xtemp2[j]>=lim3) and (xtemp2[j]<lim4):
                                     L[npixel*(rloop-1)+i,npixel*s+n]=math.sqrt(pow((ytemp2[j]-ytemp2[j+1]),2)+pow((xtemp2[j]-xtemp2[j+1]),2))
    
            elif (dyyy>0) and (dxxx<0):           # Quadrant 3, x negative and y are positive.
                ytemp2.sort()
                xtemp2.sort(reverse=True)
                for j in range(0,len(ytemp2)-1):
                    for s in range(0,ndet):
                        lim1=yul-s*ypixel
                        lim2=yul-(s+1)*ypixel
                        if (ytemp2[j]<lim1) and (ytemp2[j]>=lim2):
                            for n in range(0,npixel):
                                lim3=xll+n*xpixel
                                lim4=xll+(n+1)*xpixel
                                if (xtemp2[j]>lim3) and (xtemp2[j]<=lim4):
                                     L[npixel*(rloop-1)+i,npixel*s+n]=math.sqrt(pow((ytemp2[j]-ytemp2[j+1]),2)+pow((xtemp2[j]-xtemp2[j+1]),2))
    
            else:                                 # Quadrant 4, x negative and y are negative.
                ytemp2.sort(reverse=True)
                xtemp2.sort(reverse=True)
                for j in range(0,len(ytemp2)-1):
                    for s in range(0,ndet):
                        lim1=yul-s*ypixel
                        lim2=yul-(s+1)*ypixel
                        if (ytemp2[j]<lim1) and (ytemp2[j]>=lim2):
                            for n in range(0,npixel):
                                lim3=xll+n*xpixel
                                lim4=xll+(n+1)*xpixel
                                if (xtemp2[j]>lim3) and (xtemp2[j]<=lim4):
                                     L[npixel*(rloop-1)+i,npixel*s+n]=math.sqrt(pow((ytemp2[j]-ytemp2[j+1]),2)+pow((xtemp2[j]-xtemp2[j+1]),2))
    
    W=L                                                    #The Weight Matrix
    # plt.imshow(W)
    # plt.colorbar()
    # plt.show()
    return W