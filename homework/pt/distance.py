'''
Created on Feb 13, 2015
@author: Kewen Wang
'''
import numpy
import scipy.io
import os
from scipy.spatial.distance import minkowski
def loadtxtdata():
    txt = scipy.io.loadmat("document_analysis.mat") 
    label=txt['labels']
    doc=txt['X']
    X=doc
    m=doc.shape[1]
    nn=doc.shape[0]
    u=X.mean(axis=1).reshape(-1,1)
    #u=numpy.mean(X.toarray(),axis=1)
    nz=None
    normX=None
    tfidfX=None
    Xstd=[]
    #nz=doc.nonzero()
    print("doc:",doc.shape)
    #print("nz:",nz[0].shape)
    #print(numpy.unique(label))
    X=X.toarray()
  
    tfidf=scipy.io.loadmat("tfidf.mat")
    tfidfX=tfidf['X'].toarray()
    tfidflabel=tfidf['label']
        #print("tfidflabel",tfidflabel)
    print("tfidf:",tfidfX.shape)
    X=tfidfX
    for i in range(nn):
        r=numpy.std(X[i,:])
        if r==0:
            Xstd.append(1) 
        else: 
            Xstd.append(r)
    print("Xstd",len(Xstd),' ',Xstd[0])
    return label,m,nz,nn,X,u,normX,tfidfX,Xstd
'load face image data'

'Main function for whole program'
if __name__ == '__main__':
    j=0

    label,m,nz,nn,X,u,normX,tfidfX,Xstd=loadtxtdata()
    print(X.shape)
    l1dis=numpy.zeros((m,m))
    for i in range(0,m-1):
        for j in range(i+1,m):
            #eudis[i,j]=minkowski(X[:,i],X[:,j],2)
            l1dis[i,j]=minkowski(X[:,i],X[:,j],1)
            l1dis[j,i]=l1dis[i,j]
        print(i)
    print(l1dis.shape)
    if not os.path.isfile('l1dis.mat'):
        scipy.io.savemat('l1dis.mat',{'dis':l1dis})
    else:
        l1dis=scipy.io.loadmat('l1dis.mat')['dis']
