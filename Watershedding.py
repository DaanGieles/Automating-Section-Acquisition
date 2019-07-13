# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 15:53:13 2019

@author: Daan Gieles

"""     
import matplotlib.pyplot as plt
import numpy as np
import os
import imageio 
import secdetect
location= 'C:\\Users\\TUDelftSID\\Documents\\Python Scripts'
from skimage.morphology import watershed
from skimage.feature import peak_local_max
from skimage.measure import regionprops
from skimage.transform import rotate

from statistics import mean 
from scipy import ndimage as ndi

from math import hypot
import math
#raw=secdetect.data.load(12)
def Watershedding(raw,PercOfMax):

    """ Apply secdetect and after that a watershedding method in order to seperate overlapping sections in an image and label seperate sections

    Parameters
    ------------
    raw : RGB
    Input Image
    
    PercOfMax : int 
    In order to minimize the number of false sections the distance transform of the bmp is modified: a certain percentage of the absolute minimum is placed there. This is PercOfMax
    
    Returns
    ------------

    labels : int32
    A 2D matrix indicating which pixels belong to which sections (or the background) by different integers
    
    """
    
    if len(np.shape(raw))==2:       #Om compatible te maken voor GT
        im=raw
    else:
        ds=secdetect.detect_sections(raw)
        im=ds>0
    plt.imshow(raw) #Necessary?   
    
    
    AveDistanceTo0=ndi.distance_transform_edt(im)
    
    #minima groter maken voor rare vormen
    #Eerst absoluut minimum vinden van de distance transform
    #We hebben het over maxima als we het hebben over de waarden, maar voor het doel van watersheding kunnen we het beter hebben over minima (waterputten)
    
    
    Put=AveDistanceTo0.max()
    
    
    A = np.where(AveDistanceTo0>int(PercOfMax)*Put/100,Put,AveDistanceTo0) #Enlarges the minimum's surface
    
    #Verder met watershed
    local_maxima = peak_local_max(A,indices=False,footprint=np.ones((10,10)))
    markers=ndi.label(local_maxima)[0]
    labels = watershed(-A, markers, mask=im)
    
    return (labels,AveDistanceTo0,im,raw)

def Analyse_Labels(labels,Pareamin,Pareamax):
    
    """
    Checks whether sections are too big or small to be deemed true. Gives arrays DuplicateSectionsArray and FalseSectionsArray with 
    section numbers deemed duplicate (consisting of more than 1 section) or false (too small).
    ---------------------------
    Parameters
    ------------------------------
     Pareamin :int
         At which percentage of the average section area do you consider a section as false (too small to be a section)?
    
     Pareamax : int
         At which percentage of the average section area do you consider a detected section to consist of multiple sections?

    -----------------------------
    Returns
    -----------------------------
    A : list
        list containing regionprops.area of the labels (seperate sections)
    
    FalseSectionsArray : list
        a list containing the numbers of all labeled section which are considered to be false
      
    DuplicateSectionsArray : list 
        A list containing the numbers of all labeled section which are considered to consist of multiple sections

    
    SeperateSections : list
        A list containing 2D-matrices, each corresponding to a labeled section. (equal to labels but seperated sections)
    
    VSA : list 
        List containing regionprops of every true label
    """

    N_S=labels.max()
    fig,axes=plt.subplots(ncols=N_S,figsize=(N_S*3,3),sharex=True,sharey=True)
    ax=axes.ravel()
    
    A=[]
    for q in range(N_S):
        A.append(regionprops(labels)[q].area)
    
    FalseSections= 0
    FalseSectionsArray=[]
    DuplicateSections=0
    DuplicateSectionsArray=[]
    SeperateSections=[]
    print('Would you like to use the histogram method to determine the mean section area? Select 1. Would you like to select the section area in a plot? Select 2. If you select 3, the average section area is updated every iteration')
    ans = input('(1/2/3) << ').lower()
    if ans in ['1']:
        VSA=Hist_A(A)
        VSA=[VSA,VSA]
        Q=0
    #Hiervoor moet %matplotlib auto, hoe doe ik dit in een script?
    if ans in ['2']:
        VSA=FindArea(labels)
        print(VSA)
        VSA=[VSA,VSA]
        Q=0
            
    if ans in ['3']:
        VSA=A
        Q=[]
    for x in range(N_S):
        if A[x]<mean(VSA)*int(Pareamin)/100:           #remove smallest areas (false areas)
            ax[x].imshow(labels==x+1,'Reds')
            ax[x].set_title(f'False section {x+1}')
            labels=np.where(labels==x+1,0,labels)
            FalseSections=FalseSections+1
            FalseSectionsArray.append(x+1)
        else:
            if A[x]>mean(VSA)*int(Pareamax)/100:
                ax[x].imshow(labels==x+1,'Oranges')
                ax[x].set_title(f'Problematic section {x+1}')
                DuplicateSections=DuplicateSections+1
                DuplicateSectionsArray.append(x+1)
            else:
                ax[x].imshow(labels==x+1,'Blues')
                ax[x].set_title(f'Section {x+1}')
                SeperateSections.append(labels==x+1)
                if isinstance(Q,(list,)):
                    Q.append(A[x])
                    if len(Q)>3:
                        VSA=Q
    return (DuplicateSectionsArray, FalseSectionsArray, SeperateSections, A, VSA)

def Hist_A(A):
    n, bins, patches = plt.hist(x=A, bins=labels.max(), color='#0504aa', alpha=0.7, rwidth=0.9)
    plt.title('Histogram of section area sizes')

    Index_Max=n.tolist().index(max(n))
    BetterMean=0.5*(bins[Index_Max]+bins[Index_Max+1])
    return BetterMean

def FindArea(image):
    plt.figure()
    plt.imshow(image)
    plt.show()
    print('Click 2 corners of a section')
    B=plt.ginput(n=2,show_clicks=True,timeout=15)
    
    Dim=math.hypot(B[0][0]-B[1][0],B[0][1]-B[1][1])
    BestMean=Dim*Dim
    return BestMean


#Use code below to plot the seperate sections, distance transform and contour plot.
if __name__=='__main__': #Hier de plots
    plt.close('all')
    image=secdetect.data.load(7)
    image=rotate(image,180)
    plt.imshow(image)
    plt.show()
    (labels,AveDistanceTo0,im,raw)=Watershedding(image,85)
    (DuplicateSectionsArray, FalseSectionsArray, SeperateSections, A, VSA) = Analyse_Labels(labels,50,140)
    
    plt.figure()
    plt.contour(AveDistanceTo0); plt.colorbar()
    plt.gca().set_aspect('equal')
    fig, axes = plt.subplots(ncols=3, figsize=(9, 3), sharex=True, sharey=True)
    ax = axes.ravel()
    
    ax[0].imshow(im, cmap=plt.cm.gray)
    ax[0].set_title('Input',fontsize=25)
    ax[1].imshow(-AveDistanceTo0, cmap=plt.cm.gray)
    ax[1].set_title('Distance Transform',fontsize=25)
    ax[2].imshow(labels,cmap=plt.cm.nipy_spectral)
    ax[2].set_title('Output',fontsize=25)
    
    for a in ax:
        a.set_axis_off()
    fig.tight_layout()
    
    plt.figure()
    plt.imshow(im,cmap=plt.cm.gray)
    

    