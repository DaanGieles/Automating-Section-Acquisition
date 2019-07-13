# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 14:39:48 2019

@author: Daan Gieles
"""

import matplotlib.pyplot as plt
import numpy as np
import secdetect
location= 'C:\\Users\\TUDelftSID\\Documents\\Python Scripts'
from skimage.measure import regionprops,label
from skimage import color
from statistics import mean 
from PIL import Image
from skimage.segmentation import clear_border
from pandas import DataFrame
import pandas as pd

filename='1_GT_cropped.png'
section_number='15'

GT=color.rgb2gray(np.array(Image.open(location+'\\'+filename)))
#GT=Sections
GT=np.multiply(GT,50) #Think some rounding happens for labeling. Not doing this results in label(GT) missing some sections...

#GT = clear_border(GT)
GT_labeled=label(GT)

for x in range(GT_labeled.max()):
    if np.count_nonzero(GT_labeled==x+1)<100:
        GT_labeled=np.where(GT_labeled==x+1,0,GT_labeled)
GT_labeled=label(GT_labeled)

ProperlyLabeled=[]
DuplicateLabels=[]
LabelsContainingSection=[]
SectionsMatched=[]
Duplicate=[]
SectionsInDuplicate=[]
for x in range(GT_labeled.max()):
    GTX=1*(GT_labeled==x+1)
    for y in range(labels.max()):
        labelsy=1*(labels==y+1)
        Subtraction=GTX-labelsy
        if np.count_nonzero(Subtraction>0)<0.5*np.count_nonzero(GTX):
            if y+1 not in DuplicateLabels:
                print(f'Section {x+1} embedded in label {y+1}')
                if y+1 in LabelsContainingSection:
                    print(f'Label {y+1} contains more than 1 section. So is being considered as a duplicate label')
                    SectionsInDuplicate.append(x+1)
                    DuplicateLabels.append(y+1)
                else:
                    ProperlyLabeled.append([x+1,y+1])
                    LabelsContainingSection.append(y+1)
                    SectionsMatched.append(x+1)

FN=np.zeros(np.shape(GT))
FP=np.zeros(np.shape(GT))
FA=np.zeros(np.shape(GT))
DuplicateSections=[]
DuplicateToFilter=[]
AreaFP=[]
AreaFN=[]


SectionsMatchedFiltered=SectionsMatched.copy()
print(SectionsMatched)
for q in range(len(DuplicateLabels)):
    for w in range(len(SectionsMatched)):
        if [SectionsMatched[w],DuplicateLabels[q]] in ProperlyLabeled:
            ToRemove=[SectionsMatched[w],DuplicateLabels[q]]
            print(ToRemove)
            ProperlyLabeled.remove(ToRemove)
            SectionsMatchedFiltered.remove(SectionsMatched[w])
            SectionsInDuplicate.append(SectionsMatched[w])




for o in range(len(DuplicateLabels)):
    FA=FA+2*(labels==DuplicateLabels[o])

##Label without section
AreaNoSection=0
for u in range(labels.max()):
    if u+1 not in DuplicateLabels:
        if u+1 not in LabelsContainingSection:   
            print(f'label {u+1} doesnt have any section which fits')
            FP=FP+1*(labels==u+1)
            AreaNoSection=AreaNoSection+np.count_nonzero(1*labels==u+1)

#Correct sections and labels
for i in range(len(ProperlyLabeled)):
    Stuff=1*(labels==ProperlyLabeled[i][1])-1*(GT_labeled==ProperlyLabeled[i][0])
    FP=FP+1*(Stuff>0)
    FN=FN-1*(Stuff<0)
    AreaFP.append(np.count_nonzero(Stuff>0))
    AreaFN.append(np.count_nonzero(Stuff<0))


#Section without label
AreaNoLabel=0
for k in range(GT_labeled.max()):
    if k+1 not in SectionsMatched:
        if k+1 not in SectionsInDuplicate:
            print(f'Section {k+1} has no label and isnt part of a duplicate label')
            FN=FN-1*(GT_labeled==k+1)
            AreaNoLabel=AreaNoLabel+np.count_nonzero(1*(GT_labeled==k+1))
FinalThing=np.where(FN!=0,FN,FP)
FinalThing=np.where(FA!=0,FA,FinalThing)
    
plt.close('all')
fig,ax=plt.subplots()
plt.imshow(FinalThing)
plt.colorbar()
ax.set_title('Ground truth for further processed sample 1',fontsize=20)
plt.show()
fig,ax=plt.subplots()
plt.imshow(labels)
ax.set_title('Labels resulting from software',fontsize=20)
plt.show()
fig,ax=plt.subplots()
plt.imshow(GT)
ax.set_title('Actual sections',fontsize=20)
plt.show()


TotalArea=0
SectionArea=[]
for v in range(len(SectionsMatchedFiltered)):
    SectionArea.append(np.count_nonzero(GT_labeled==SectionsMatchedFiltered[v]))
    TotalArea=TotalArea+np.count_nonzero(GT_labeled==SectionsMatchedFiltered[v])
    
AreaAve=TotalArea/len(SectionsMatchedFiltered)

FNList=np.divide(AreaFN,np.count_nonzero(1*(GT_labeled==SectionsMatchedFiltered[v])))
FPList=np.divide(AreaFP,np.count_nonzero(GT_labeled==SectionsMatchedFiltered[v]))
MissingLabelPercentage = 100*AreaNoLabel/TotalArea
FalseLabelPercentage = 100*AreaNoSection/TotalArea
FN_per_section=np.multiply(100,FNList)
FP_per_section=np.multiply(100,FPList)

FNPercentage=mean(FN_per_section)
FPPercentage=mean(FP_per_section)
print(f'The percentage of false positives is {FPPercentage}%')
print(f'The percentage of false negatives is {FNPercentage}%')
print(f'False label percentage is {FalseLabelPercentage}')
print(f'Missing label percentage is {MissingLabelPercentage}')

for q in range(len(FP_per_section)):
    FP_per_section[q]=format(FP_per_section[q],'.2f')
    FN_per_section[q]=format(FN_per_section[q],'.2f')

SectionIntegers=np.linspace(1,len(SectionsMatchedFiltered),len(SectionsMatchedFiltered),dtype='uint8')

Dict={'Section':SectionIntegers,
      'Percentage false positives':FP_per_section,
      'Percentage false negatives':FN_per_section}
df=DataFrame(Dict,columns=['Section','Percentage false positives','Percentage false negatives'])

string=df.to_latex()














    
    