# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:16:59 2019
Required to run first: Watershedding.py,Tiling.py,KmeansClustering.py
@author: Daan Gieles
"""
import matplotlib.pyplot as plt
import numpy as np
import os
import imageio 
import secdetect
from skimage.morphology import watershed
from skimage.feature import peak_local_max
from skimage.measure import regionprops

from statistics import mean 
from scipy import ndimage as ndi

''' Required: NewLabelsInOne,labels,DuplicateSectionsArray

    Combines the results from K-means clustering with those from the watershed.
'''



B,NewLabelsInOne,n_clusters=KMeansClustering(VSA,A,DuplicateSectionsArray,labels)

def ProcessLabels(NewLabelsInOne,labels,DuplicateSectionsArray,n_clusters):
    
    """ 
    Allows you to choose for which problematic (duplicate) section you would like to apply k-means clustering to and combines
    it into one 2d array labels_split, which can be inserted into Tiling.py. Also removes faulty sections deemed too small.
    
    -----------------------
    Parameters
    -----------------------
    
    NewLabelsInOne : A list of 2d arrays of all duplicate labels split up into seperate sections
    
    DuplicateSectionsArray : an array containing the numbers of the section Watershedding.py considers to be 'duplicate' or 'problematic'
    KEEP IN MIND: the numbering follows Watershedding.py so doesn't work with the indexing in Tiling.py 
    (where false sections are completely removed from NumbTilesX, BboxStartingPointX etc.)
    
    labels : A 2D matrix indicating which pixels belong to which sections (or the background) by different integers (output of Watershedding.py)
    
   ------------------------
   Returns
   ------------------------
   labels_split : An array containing 2D matrix indicating which pixels belong to which sections (or the background) by different integers, same as labels but with the faulty sections removed and larger ones split up.
   Made to be compatible for using in Tiling.py.
    """
#First remove false sections
    print('Would you like to add a false section to one of the surrounding sections?')
    ans=input('(Y/N) <<').lower()
    if ans in['yes','y']:    
        labels=StitchTogether(labels,FalseSectionsArray)
    labels_filtered=labels
    for h in range(len(FalseSectionsArray)):
        labels=np.where(labels==FalseSectionsArray[h],0,labels_filtered) #Hiervoor nog stitchen

    print('Would you like to apply k-means clustering to a problematic sections?')
    ans=input('(Y/N) <<').lower()
    if ans in['yes','y']:   
        labels=ApplyKMeans(labels,DuplicateSectionsArray,n_clusters)
        
        
    print('Would you like to remove a section?')
    ans=input('(Y/N) <<').lower()
    if ans in['yes','y']:   
        labels=RemoveLabels(labels)
    
    #Now the gaps are filled. The labels are placed in order again.
    
    labels_split=labels
    count=0
    for v in range(labels.max()):
        if v+1 in labels:
            count=count+1
            labels_split=np.where(labels==v+1,count,labels_split)
    return (labels_split)

def StitchTogether(labels,FalseSectionsArray): #In progress
    for x in range(labels.max()):
        value=x+1
        plt.figure()
        plt.imshow(labels==value)
        plt.show()
        print('Would you like to stitch this section to a surrounding one?')
        ans=input('(Y/N) <<').lower()
        click=False
        labels_stitch=labels
        if ans in['yes','y']:
            while click==False:
                plt.imshow(labels_stitch,cmap=plt.cm.nipy_spectral)
                plt.show()
                
                print('Scroll through the sections to which you want to append')
                ans=input('(Next/Previous/Select/Exit) <<').lower()
                if ans in['next','n']:
                    value=value+1
                    labels_stitch=np.where(labels==x+1,value,labels)
                if ans in['previous','p']:
                    value=value-1
                    labels_stitch=np.where(labels==x+1,value,labels)
                if ans in['select','s']:
                    labels=labels_stitch
                    click=True
                    if value in FalseSectionsArray:
                        FalseSectionsArray.remove(value)
                if ans in['exit','e']:
                    click=True
                    
                    
    return labels
    
def RemoveLabels(labels):
    for x in range(labels.max()):
        plt.figure()
        plt.imshow(labels==x+1) #0 overslaan
        plt.show()
        print('Would you like to remove this label?')
        ans=input('(Y/N/Done) <<').lower()
        if ans in['yes','y']:
            labels=np.where(labels==x+1,0,labels)
        if ans in['d','done']:
            break
    return labels
def ApplyKMeans(labels,DuplicateSectionsArray,n_clusters):
    for i in range(len(DuplicateSectionsArray)):
        LoopTool=False
        NewLabelsTemp=NewLabelsInOne[i]
        while LoopTool==False:
            print(np.shape(NewLabelsTemp))
            p=DuplicateSectionsArray[i]
            plt.figure()
            plt.imshow(labels==p)
            plt.figure()
            plt.imshow(NewLabelsTemp,cmap=plt.cm.nipy_spectral)
            plt.show()
            print('Would you like to apply the K-means clustering result to this problematic section?')
            ans = input('(Y/N/More/Less) << ').lower()
            plt.figure()
            if ans in ['yes', 'y']:
                labels=np.where(labels==p,NewLabelsTemp,labels)
                LoopTool=True
            if ans in ['more','m']:
                B,NewLabelsTemp,n_clusters=KMeansClustering(1,1,[p],labels,n_clusters+1)
                NewLabelsTemp=NewLabelsTemp[0]
            if ans in ['Less','l']:
                B,NewLabelsTemp,n_clusters=KMeansClustering(1,1,[p],labels,n_clusters-1)
                NewLabelsTemp=NewLabelsTemp[0]
            if ans in ['No','n']:
                LoopTool=True
    return labels
if __name__=='__main__':
    labels  = ProcessLabels(NewLabelsInOne,labels,DuplicateSectionsArray,n_clusters)
    DuplicateSectionsArray=[]   
    FalseSectionsArray=[]