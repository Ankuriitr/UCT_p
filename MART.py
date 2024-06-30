# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 15:49:55 2021
MART -1,2,3
This code perform 2D reconstruction based on the weight matrix and the
pojection data.

Weight matrix w(i,j) ; i be the ith ray and j be the jth pixel.
w(i,j)x(j)=B(i); x be the attenuation coefficients and B be the projection
data.
Steps:-
i. initial guess of the x(j) value.
ii. correction to the x(j) value.
iii. Application of the correction.
iv. Testing the convergence.

@author: ANKUR
"""

def MART(W,proj,ndet,nrot,accuracy,u,max_iter,mart_num,): 
    
    import numpy as np

    #INPUT
    # proj=np.random.rand(9,18)
    # mart_num=3
    # ndet=9
    # nrot=18
    # accuracy=0.0001                   #Accuracy/ Convergence criterion.
    # u=0.1                             #Relaxation factor.
    # max_iter=100
    # W= weight matrix
    
    proj_rows=len(proj)
    proj_cols=len(proj[0])
    
    if proj_cols>1:
        proj=proj.flatten()
    
    
    N_pixel=ndet*ndet
    M=ndet*nrot
    corrtn=np.zeros([ndet*nrot,1])
    pnew=np.zeros([M,1])     
    fnew=np.ones([N_pixel,1])         #The reconstructed image.
    iteration=0
    conv_factor=1
    fold=fnew
    # exon=1
    
    while ((conv_factor>accuracy) and (iteration<max_iter)):
        for i in range(0,M):
            pnew[i]=0
            for j in range(0,N_pixel):
                pnew[i]=pnew[i]+W[i,j]*(fnew[j])
        
            if (proj_rows==1):
                proj=np.transpose(proj)
            if (pnew[i]!=0):
                corrtn[i]=proj[i]/pnew[i]
            else:
                corrtn[i]=0
            
            if (mart_num==1):
                for j in range(0,N_pixel):
                    if ( W[i,j]!=0):
                        fnew[j]=fnew[j]*(1-u*(1-corrtn[i]))
                    else:
                        fnew[j]=fnew[j]
    
            elif(mart_num==2):
                #     fnew(j,1)=fnew(j,1)*((c(i,1)).^(lamda*w(i,j)/max(w(i,:))));     #LENT MART
                #       fnew(j,1)=fnew(j,1)*(1-lamda*w(i,j)*(1-c(i,1))/W(i,1));
                for j in range(0,N_pixel):
                    if (max(W[i,])!=0):
                        fnew[j]=fnew[j]*pow((corrtn[i]),(u*W[i,j]/max(W[i,])))
                    else:
                        fnew[j]=fnew[j]
    
            elif (mart_num==3):
                for j in range(0,N_pixel):
                    if ( W[i,j]!=0):
                        fnew[j]=fnew[j]*pow((corrtn[i]),(u*W[i,j]))              #K_MART   
                        #fnew[j,0]=fnew[j,0]*(1-u*W[i,j]*(1-corrtn[i,0])/max(W[i,]))   #M_MART
                    else:
                        fnew[j]=fnew[j]
        
        error=abs((fnew-fold)/fnew)
        conv_factor=100*(min(error))
        fold=fnew
        iteration=iteration+1
    return fnew

