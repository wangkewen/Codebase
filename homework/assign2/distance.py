'''
Created on Feb 13, 2015
@author: Kewen Wang
wkw
'''
import numpy
import scipy.io

def loadtxtdata():
    txt = scipy.io.loadmat("document_analysis.mat") 
    print(scipy.io.whosmat("document_analysis.mat"))
    label=txt['labels']
    doc=txt['X']
    #label,doc=sample(label,doc)
    X=doc
    m=doc.shape[1]
    nn=doc.shape[0]
    u=X.mean(axis=1).reshape(-1,1)
    #u=numpy.mean(X.toarray(),axis=1)
    #print(doc)
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
    edis=numpy.zeros((m,m))
    l1dis=numpy.zeros((m,m))
    for i in range(0,m-1):
        for j in range(i+1,m-1):
            edis[i,j]=X[0,i]-X[0,j]
            edis[j,i]=edis[i,j]
        print(i)
    print(edis.shape)
    
    
    