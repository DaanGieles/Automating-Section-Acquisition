# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 13:09:45 2019

@author: Daan Gieles
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches #vierkantje tekenen
import numpy as np
from PIL import Image, ImageFilter
import os  #Zo kunnen we makkelijker werken met directories en afbeeldingen. 'Operating Software'
import time #Zo kunnen we vertraging instellen
import imageio #Afbeelding inladen
import pickle

from scipy import ndimage as ndi
from skimage.morphology import watershed
from skimage.feature import peak_local_max
from skimage.measure import regionprops
import piexif

from skimage.feature import canny
from skimage.segmentation import felzenszwalb, clear_border
from skimage.color import hed_from_rgb

from secdetect.adjust import enhance_contrast
from secdetect.ringdetect import find_ring, crop_to_ring
import imageio

import matplotlib.pyplot as plt
from skimage import img_as_ubyte
filepath="C:\\Users\\TUDelftSID\\Documents\\Python Scripts"
def Tiling(PixelSize, TileSize, labelsTiling, PercentageOverlap, DuplicateSectionsArray, FalseSectionsArray,margin):
    
    """ 
    Gives A tiling scheme for a 2D matrix representing the different sections as labels. Detects which tiles contain no information and marks them as such. Outputs a boolean matrix 
    indicating skippable tiles by 0, tile coordinate information is with respect to the upper left corner of a sections boundary box (min row and min col)
    
    After this function the section numbering assigned to the labels in WaterShed.py no longer applies. (So section 5 is not necessarily section 5 anymore)
    ----------------------------
    Parameters
    ----------------------------
    PixelSize : int
        the pixel size in microns
    
    TileSize : int
        the tile size (1 dimension)
    
    unit_length : string
        a string indicating with what unit PixelSize and TileSize are provided
    
    labelsTiling : Array (int32)
        a 2D matrix indicating which pixels belong to which sections (or the background) by different integers
    
    PercentageOverlap : int
        the desired percentage overlap between two adjacent tiles
    
    DuplicateSectionsArray : list
        a list containing the numbers of all labeled section which are considered to consist of multiple sections
    
    FalseSectionsArray : list
        an array containing the numbers of all labeled section which are considered to be false
        
    margin: int 
        a percentage which enlargens the documented surface (in case the labeling results in a section that doesn't contain all information)
    
    ---------------------------
    Returns
    ---------------------------
    AllCoordinates: list
    A list of all sections, with each index a list of all tile coordinates in meters
    ------------------------------
    """
    TileSizeInPixels=int(TileSize/PixelSize)

    PixelSize=PixelSize*1e-6
    TileSize=TileSize*1e-6
        
    N_S = labelsTiling.max()
    fig,axes=plt.subplots(ncols=N_S-len(FalseSectionsArray),figsize=(N_S*3,3),sharex=True,sharey=True)
    ax=axes.ravel()
    
    count=0
    BboxSizeX=[]
    BboxSizeY=[]
    plt.figure()
    
    BboxStartingPointX=[] #WRT the (minc,minr) point of the Bbox
    BboxStartingPointY=[]
    TileX=[]
    TileY=[]
    TilingInfo=[]
    margin=margin//100
    AllCoordinates=[]
    for x in range(N_S):
        if x in labelsTiling:
            if x+1 in FalseSectionsArray:
                print(f'False Section {x+1}')
            else:
                R = regionprops(labelsTiling)[x]
                minr,minc,maxr,maxc = R.bbox
                
                BboxStartingPointX.append(minc)#
                BboxStartingPointY.append(minr)#
                
                
                if x+1 in DuplicateSectionsArray:
                    ax[count].imshow(labelsTiling==x+1,'Purples')
                    ax[count].set_title(f'Possible duplicate section {x+1}',fontsize=25)
                    rect=patches.Rectangle((minc,minr),maxc-minc,maxr-minr,linewidth=1.5,edgecolor='r',facecolor='none')
                    ax[count].add_patch(rect)
                else:
                    ax[count].imshow(labelsTiling==x+1,'Blues')
                    ax[count].set_title(f'Section {x+1}',fontsize=25)
                    rect=patches.Rectangle((minc,minr),maxc-minc,maxr-minr,linewidth=1.5,edgecolor='r',facecolor='none')
                    ax[count].add_patch(rect)
        
                BboxSizeX.append((maxc-minc))
                BboxSizeY.append((maxr-minr))
                NumbTilesX=int(np.ceil(BboxSizeX[count]/(TileSizeInPixels*(1-PercentageOverlap/100)))) 
                NumbTilesY=int(np.ceil(BboxSizeY[count]/(TileSizeInPixels*(1-PercentageOverlap/100))))
                
                TilingInfoZeros=np.zeros((NumbTilesY,NumbTilesX))#
                CenterTileY=[]#
                for k in range(NumbTilesY):
                    CenterTileX=[]#
                    CenterTileY.append(BboxStartingPointY[count]*PixelSize+0.5*TileSize+k*TileSize*(1-PercentageOverlap/100))#
                    for l in range(NumbTilesX):
                        Check=0
                        CenterTileX.append(BboxStartingPointX[count]*PixelSize+0.5*TileSize+l*TileSize*(1-PercentageOverlap/100))
                        for m in range(TileSizeInPixels*1):
                            for n in range(TileSizeInPixels*1):
                                Check = Check + (labelsTiling==x+1)[minr+m+k*TileSizeInPixels-k*round(TileSizeInPixels*PercentageOverlap/100),minc+n+l*TileSizeInPixels-l*round(TileSizeInPixels*PercentageOverlap/100)]
                        if Check==0:
                            TilingInfoZeros[k,l]=False
                            rect_2=patches.Rectangle((minc+l*TileSizeInPixels*(1-PercentageOverlap/100),minr+k*TileSizeInPixels*(1-PercentageOverlap/100)),TileSizeInPixels,TileSizeInPixels,linewidth=1,edgecolor='b',facecolor='blue')
                            ax[count].add_patch(rect_2)
                            print(f'In section {x+1} skip Tile with center coordinates (x,y)=({CenterTileX[l]},{CenterTileY[k]}) in meters')
                        else:
                            TilingInfoZeros[k,l]=True
                            rect_2=patches.Rectangle((minc+l*TileSizeInPixels*(1-PercentageOverlap/100),minr+k*TileSizeInPixels*(1-PercentageOverlap/100)),TileSizeInPixels,TileSizeInPixels,linewidth=1,edgecolor='g',facecolor='none')
                            ax[count].add_patch(rect_2)
                            
                TileX.append(CenterTileX)
                TileY.append(CenterTileY)
                TilingInfo.append(TilingInfoZeros)
                count=count+1
                AllCoordinatesPerLabel=[]
                for t in range(len(CenterTileX)):
                    for r in range(len(CenterTileY)):
                        if TilingInfoZeros[r,t]!=0:
                            AllCoordinatesPerLabel.append([CenterTileX[t],CenterTileY[r]]) #X eerst, dan Y
                AllCoordinates.append(AllCoordinatesPerLabel)
                
    return (AllCoordinates)

def ToSend(AllCoordinates,CroppedImage,samplenumber,filepath):
    """
    
    Formats the list of tile coordinates in meters and the cropped sample image in a file. It will be saved in the fp as the file
    'SendToMicroscope'+'samplenumber'+'.txt'
    
    Parameters
    ----------
    AllCoordinates : list
    A list of all sections, with each index a list of all tile coordinates in meters
    
    Cropped image: uint8
    The output of Crop_Image. Should be the cropped image of the sample that will be used for calibration
    
    samplenumber: string
    The number of the sample, used for naming the file outputted
    
    filepath: string
    Location where the file should be saved. Could be a flashdrive
    -------    
    Returns
    -------
    Nothing. Only saves a file
    """
    #Create CroppedImage by using 'Cropoing Image.py'        
    SendToMicroscope = [CroppedImage,AllCoordinates]
    with open(filepath+"\\SendToMicroscope"+samplenumber+".txt","wb") as fp:        
        pickle.dump(SendToMicroscope,fp,protocol=2)
        

def Crop_Image(image, enhance_contrast_kws=None,
                    canny_kws=None, find_ring_kws=None,
                    felzenszwalb_kws=None, clear_border_kws=None):
    """Crops image to the ring. Code snippet from 'Automated detection of EPON-embedded sections on ITO-coated sample glass', I. Postmes. Delft University of Technology, 2018
    Parameters
    ----------
    image : ndarray
        Input optical overview image
    enhance_contrast_kws : dict (optional)
        Keyword arguments for `enhance_contrast`
    canny_kws : dict (optional)
        Keyword arguments for `canny`
    find_ring_kws : dict (optional)
        Keyword arguments for `find_ring`
    felzenszwalb_kws : dict (optional)
        Keyword arguments for `felzenswalb`
    clear_border_kws : dict (optional)
        Keyword arguments for `clear_border`
    -------    
    Returns
    -------
    imcr : ndarray
        Cropped Image
    """
    # Make unnecessary copy of input image to preserve it
    imin = image.copy()

    # Set default parameters for `enhance_contrast`
    if enhance_contrast_kws is None:
        enhance_contrast_kws = {}
    enhance_contrast_kws.setdefault('clip', True)
    enhance_contrast_kws.setdefault('pct', 1.0)
    enhance_contrast_kws.setdefault('channel', 2)
    enhance_contrast_kws.setdefault('conv_matrix', hed_from_rgb)

    # Set default parameters for `canny`
    if canny_kws is None:
        canny_kws = {}
    canny_kws.setdefault('sigma', 4)
    canny_kws.setdefault('low_threshold', 0.10)
    canny_kws.setdefault('high_threshold', 0.99)
    canny_kws.setdefault('use_quantiles', True)

    # Set default parameters for `find_ring`
    if find_ring_kws is None:
        find_ring_kws = {}
    find_ring_kws.setdefault('ransac_kws', None)

    # Set default parameters for `felzenswalb`
    if felzenszwalb_kws is None:
        felzenszwalb_kws = {}
    felzenszwalb_kws.setdefault('scale', 750)
    felzenszwalb_kws.setdefault('sigma', 1.0)
    felzenszwalb_kws.setdefault('min_size', 500)
    felzenszwalb_kws.setdefault('multichannel', imin.ndim>2)

    # Set default parameters for `clear_border`
    if clear_border_kws is None:
        clear_border_kws = {}
    clear_border_kws.setdefault('buffer_size', 50)

    # Enhance contrast
    imec = enhance_contrast(imin, **enhance_contrast_kws)
    # Canny edge detector for ring detection
    imcn = canny(imec, **canny_kws)
    # Find ring from edges and extract paramters (center coords, radius)
    cx, cy, r = find_ring(imcn, **find_ring_kws)
    # Crop to ring and remove background
    imcr = crop_to_ring(imin, cx=cx, cy=cy, radius=r)
    # Felzenswalb segmentation
    imcr=img_as_ubyte(imcr)
    return imcr





def ShowTiles(AllCoordinates,labels,TileSize):
    '''Provides a plot of the tiles, overlayed over the 'labels' image
    Parameters
    ----------
    AllCoordinates : list
    A list of all sections, with each index a list of all tile coordinates in meters
    
    labels: Array (int32)
        a 2D matrix indicating which pixels belong to which sections (or the background) by different integers
        
    TileSize: int
    Tilesize in microns
    
    Returns
    ----------
    LabelsZeros: array
    2D matrix indicating for each pixel how many times it will be acquired with the current tiling scheme
    
    '''
    LabelsZeros=np.zeros(np.shape(labels))
    PixelSize=np.multiply(20,1e-6)
    TileSizeInPixels=np.multiply(TileSize,1e-6)/PixelSize
#    fig=plt.figure()
    ax=plt.axes()
    plt.imshow(labels)
    for i in range(len(AllCoordinates)):
        for j in range(len(AllCoordinates[i])):
            x=round(np.divide(AllCoordinates[i][j][0],PixelSize))
            y=round(np.divide(AllCoordinates[i][j][1],PixelSize))
#            minc=x-TileSizeInPixels
#            minr=y-TileSizeInPixels
#            rect_2=patches.Rectangle((minc,minr),TileSizeInPixels,TileSizeInPixels,linewidth=0,edgecolor='none',facecolor='white')
#            ax.add_patch(rect_2)
            plt.plot(x,y,'r+')
            for u in range(int(round(TileSizeInPixels))):
                for z in range(int(round(TileSizeInPixels))):
                    LabelsZeros[int(y+u)][int(x+z)]=LabelsZeros[int(y+u)][int(x+z)]+1
    return LabelsZeros
            

def AddTiles(AllCoordinates,labels,PercentageOverlap,PixelSize,TileSize):
    '''Allows the user to add a tile to the scheme. Set ' %matplotlib auto', run the function. The labeled image will pop up with all tile locations. Click the tile you would like to append a tile to.
    The selected tile will show a white cross. If the right tile is selected, middle click to choose this tile. The user will be given the choice to append a tile to the top, bottom left or right side of this tile.
    Parameters
    ----------
    AllCoordinates : list
    A list of all sections, with each index a list of all tile coordinates in meters
    
    labels: Array (int32)
        a 2D matrix indicating which pixels belong to which sections (or the background) by different integers
        
    PercentageOverlap: int
    The percentage overlap between the tiles
    
    TileSize: int
    Tilesize in microns
    
    PixelSize: int
    PixelSize in microns

    Returns
    ----------
    Returns nothing, only updates labels    
    '''

    plt.close('all')
    PixelSize=np.multiply(PixelSize,1e-6)
    TileSize=np.multiply(TileSize,1e-6)
    plt.ion()
    fig=plt.figure()
    plt.imshow(labels)
        
    click=False
    count=0
    AllCoordinates2D=[]
    for i in range(len(AllCoordinates)):
        for j in range(len(AllCoordinates[i])):
            x=round(np.divide(AllCoordinates[i][j][0],PixelSize))
            y=round(np.divide(AllCoordinates[i][j][1],PixelSize))
            AllCoordinates2D.append(AllCoordinates[i][j])
            if [i,j]==[0,count]:
                plt.plot(x,y,'g+')
            else:
                plt.plot(x,y,'r+')
    fig.canvas.draw()
    count=0
    plt.ion()
    while click==False:
        DistanceList=[]
        
        if click==False:
            print('Click close to the tile to which you would like to append a tile to')
            B=np.multiply(plt.ginput(n=-1,timeout=15),PixelSize)
            if len(B)!=0:
                B=B[len(B)-1]
                Distance=np.subtract(AllCoordinates2D,B)
                for q in range(len(Distance)):
                    DistanceList.append(Distance[q][0]**2+Distance[q][1]**2)
                MinPoint=DistanceList.index(min(DistanceList))
                print(MinPoint)
                plt.close(fig)
                fig=plt.figure()
                plt.imshow(labels)
                for p in range(len(AllCoordinates2D)):
                    x_unrounded=np.divide(AllCoordinates2D[p][0],PixelSize)
                    y_unrounded=np.divide(AllCoordinates2D[p][1],PixelSize)
                    x=round(x_unrounded)
                    y=round(y_unrounded)
                    if p==MinPoint:
                        plt.plot(x,y,'w+')
                        x_point=x
                        y_point=y
                    else:
                        plt.plot(x,y,'r+')
                plt.show()
            if len(B)==0:
                click=True
    print('Would you like to add a tile to the right, left, above or below?')
    ans = input('(L/R/A/B) << ').lower()
    
    #Nu de plek vinden waar ik de extra coordinaat moet appenden!
    count=0
    for t in range(len(AllCoordinates)):
        for j in range(len(AllCoordinates[i])):
            count=count+1
            if count==MinPoint:
                Append=t
    print(t)
    if ans in['left','l']:
        AllCoordinates[Append].append([x_point*PixelSize-TileSize*(1-PercentageOverlap/100),y_point*PixelSize])
    if ans in['right','r']:
        AllCoordinates[Append].append([x_point*PixelSize+TileSize*(1-PercentageOverlap/100),y_point*PixelSize])
    if ans in['above','a','up','u']:
        AllCoordinates[Append].append([x_point*PixelSize,y_point*PixelSize-TileSize*(1-PercentageOverlap/100)])
    if ans in['below','b','down','d']:
        AllCoordinates[Append].append([x_point*PixelSize,y_point*PixelSize+TileSize*(1-PercentageOverlap/100)])
    
            
if __name__=='__main__':
    PixelSize=25
    TileSize=200
    im_crop=Image.open('C:\\Users\\TUDelftSID\\Documents\\Python Scripts\\raw_cropped.png')
    AllCoordinates = Tiling(PixelSize, TileSize, labels, 15, DuplicateSectionsArray, FalseSectionsArray,0)
#    OverlapCheck=OverlapCheck(TilingInfo,AllCoordinates,labels,PixelSize,200)
#    PTimeSaved=SavedTime(OverlapCheck)

