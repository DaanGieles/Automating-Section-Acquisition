# -*- coding: utf-8 -*-
"""
Created on Thu May  2 11:31:58 2019
Requires you to first run Waterhedging.py and Tiling.py
@author: Daan Gieles
"""
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean 
from sklearn.cluster import KMeans #Had to install scikit (and update to Conda 4.6)
from matplotlib.pyplot import cm

def KMeansClustering(VSA, A, DuplicateSectionsArray, labels,K=None):
    """ 
    Applies a k-means clustering to sections which are deemed to be 'duplicate' or 'problematic' in Watershedding.py. 
    Outputs proposed centroids as well as the new labels (old one split up into K ones)
    
    -----------------------
    Parameters
    -----------------------
    
    VSA : array of regionprops of true labels
    
    A : array of regionprops of all labels
   
    DuplicateSectionsArray : an array containing the numbers of the section Watershedding.py considers to be 'duplicate' or 'problematic'
    KEEP IN MIND: the numbering follows Watershedding.py so doesn't work with the indexing in Tiling.py 
    (where false sections are completely removed from NumbTilesX, BboxStartingPointX etc.)
    
    labels : A 2D matrix indicating which pixels belong to which sections (or the background) by different integers (output of Watershedding.py)
    
   ------------------------
   Returns
   ------------------------
   seperatedlabels : An array containing 2D matrix indicating which pixels belong to which sections (or the background) by different integers, same as labels but split up into multiple sections.
   
    
    
    
    """
    Q=labels.max()
    NewLabelsInOne=[0]*len(DuplicateSectionsArray)
    centroids=[]
    AllSeperatedLabels=[]
    for o in range(len(DuplicateSectionsArray)):
        NewLabelsList=[]
        p = DuplicateSectionsArray[o] 
        plt.figure()
        plt.imshow(labels==p)
        plt.title(f'Problematic Section {p}')
        if K==None:
            K=round(A[p-1]/mean(VSA)) #p is the number of the section, but has the index p-1 (python starts at 0)
            print(A[p-1]/mean(VSA))
        print(K)
        y,x=np.where(labels==p)
        Coord=np.array([x,y]).T
        n_clusters=int(K)
        kmeans=KMeans(n_clusters)
        kmeans=kmeans.fit(Coord)
        kmeans_labels = kmeans.predict(Coord)
        centroids=kmeans.cluster_centers_
        
        plt.figure()
        plt.imshow(labels==p)
        plt.plot(centroids[:,0],centroids[:,1],'r+', mew=2)
        plt.title(f'Problematic Section {p} with K-means clustering centroids displayed')
        
        plt.figure()
        plt.imshow(labels==p)
        seperatedlabels=[]
        for n in range(max(kmeans_labels)+1):
            validlabelx=[]
            validlabely=[]
            newlabel=np.zeros(np.shape(labels))
            for m in range(len(x)):
                if kmeans_labels[m]==n:
                    validlabelx.append(x[m])
                    validlabely.append(y[m])
                    newlabel[y[m]][x[m]]=n+1+Q
            seperatedlabels.append(newlabel)
            plt.plot(validlabelx,validlabely)
            plt.title(f'Proposed seperation of problematic section {p}')
        AllSeperatedLabels.append(seperatedlabels)
        NewLabelsList=NewLabelsList+seperatedlabels
        NewLabelsInOne[o]=sum(NewLabelsList).astype(np.int32)
        Q=NewLabelsInOne[o].max()
        print(Q)
        
    #skimage slic for k means clustering
    return (AllSeperatedLabels,NewLabelsInOne,K)
