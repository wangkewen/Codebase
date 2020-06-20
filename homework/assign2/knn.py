'''
Created on Feb 13, 2015
@author: Kewen Wang
wkw
'''
import numpy
import scipy.io

from scipy.spatial.distance import cosine

def loadtxtdata():
    txt = scipy.io.loadmat("document_analysis.mat") 
    print(scipy.io.whosmat("document_analysis.mat"))
    label=txt['labels']
    doc=txt['X']
    #label,doc=sample(label,doc)
    X=doc
    m=X.shape[1]
    nn=X.shape[0]
    u=X.mean(axis=1).reshape(-1,1)
    
    #u=numpy.mean(X.toarray(),axis=1)
    #print(doc)
    nz=None
    normX=None
    tfidfX=None
    Xstd=[]
    #nz=doc.nonzero()
    #print("doc:",doc.shape)
    #print("nz:",nz[0].shape)
    #print(numpy.unique(label))
    X=X.toarray()
       
    tfidf=scipy.io.loadmat("tfidf.mat")
    tfidfX=tfidf['X'].toarray()
    tfidflabel=tfidf['label']
    
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

'k-Nearest Neighbor classification for both data'
def knn(c1,c2,label,m,n,X,u,Xstd,sigfile):   
    kNumber=[1,3,5,7]
    cvNumber=[10,5]
    K=kNumber[c1]
    cv=cvNumber[c2]
    #X,W=pca(label,m,n,n*n,X,u,120)
    #nn=X.shape[0]
    #u=X.mean(axis=1).reshape(-1,1)
    '''
    Xstd=[]
    for i in range(nn):
        r=numpy.std(X[i,:])
        if r==0:
            Xstd.append(1) 
        else: 
            Xstd.append(r)
    '''
    dist={}
    sigma=[1]*m
    print(len(sigma))
    result=[]
    for index in range(0,int(m/cv),int(m/(cv*cv))):
        train=[]
        trainIndex=[]
        test=[]
        testIndex=[]
        correct=0
        print("index:",index)
        print(int(m/(cv*cv)))
        print(int(m/cv))
        tm=m
        if int(m/(cv*cv))*cv*cv < m:
            tm=int(m/(cv*cv))*cv*cv
            print("tm:",tm)
        if not int(m/cv)-index < int(m/(cv*cv)):
            for cn in range(0,tm,int(tm/cv)):
                #print("cn:",cn)
                for i in range(cn+index,cn+index+int(tm/(cv*cv))):
                    test.append(X[:,i])
                    testIndex.append(i)
                for j in range(cn+index+int(tm/(cv*cv)),cn+int(tm/cv)):
                    train.append(X[:,j])
                    trainIndex.append(j)
                for j in range(cn,cn+index):
                    train.append(X[:,j])
                    trainIndex.append(j)
            for j in range(tm,m):
                train.append(X[:,j])
                trainIndex.append(j)
        else:
            for i in range(tm,m):
                test.append(X[:,i])
                testIndex.append(i)
            for j in range(0,tm):
                train.append(X[:,j])
                trainIndex.append(j)
        print("trainSize:",len(train),"testSize",len(test))
        #print(testIndex)
        #print(trainIndex )
        for i in range(len(test)):
            labelT=0
            mindis=[]
            mindisIndex=[]
            print(i)
            for l in range(K):
                mindis.append(numpy.Inf)
                mindisIndex.append(0)
            for j in range(len(train)):
                if dist.get((trainIndex[j],testIndex[i]))==None:
                    'c'
                    #dist[(trainIndex[j],testIndex[i])]=numpy.sqrt(numpy.sum(((train[j]-test[i])/Xstd)**2))
                    
                    dist[(trainIndex[j],testIndex[i])]=cosine(train[j],test[i])
                    #print(dist[(trainIndex[j],testIndex[i])])
                dis=dist[(trainIndex[j],testIndex[i])]
                if dis<mindis[K-1]:
                    del mindis[K-1]
                    del mindisIndex[K-1]
                    mindis.append(dis)
                    mindisIndex.append(label[trainIndex[j],0])
                    sindex=numpy.argsort(numpy.array(mindis))
                    mindis=list(numpy.array(mindis)[sindex])
                    mindisIndex=list(numpy.array(mindisIndex)[sindex])
            sigma[testIndex[i]]=mindis[K-1]
            #print('sigma dis:',mindis[K-1])
            if not mindis[K-1]>0:
                print("fffffffffffffffffffffffffffffffffff:",mindis[K-1])
                sigma[testIndex[i]]=0.01
            #print(mindisIndex)
            #print(mindis)
            if K==1:
                labelT=mindisIndex[0]
            else:
                countv=[]
                for v in mindisIndex:
                    countv.append(mindisIndex.count(v))
                labelT=mindisIndex[countv.index(max(countv))] 
            #print("labelT",labelT)
            #print("real Label",label[testIndex[i],0])
            if labelT==label[testIndex[i],0]: correct+=1
        #cratio=correct*1.0/(len(test))
        #print("correct Number: ",correct," ",cratio)
        #print(index) 
        #result.append(cratio)
        #print(sigma)  
    #print("\\\ Average:",numpy.mean(result))
    #print("\\\ Standard Deviation:",numpy.std(result))
    #print(len(sigma))
    scipy.io.savemat(sigfile,{'sigma':sigma})
    print('DONE......')
    return sigma



'Main function for whole program'
if __name__ == '__main__':
   
    
    label,m,nz,nn,X,u,normX,tfidfX,Xstd=loadtxtdata()
    knn(3,0,label,m,nz,X,u,Xstd,'sigma_X.mat')
  
    
