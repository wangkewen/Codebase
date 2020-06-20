'''
Created on Feb 13, 2015
@author: Kewen Wang
wkw
'''
import numpy
import pylab
import scipy.io
import os
from scipy.sparse import csr_matrix
from PIL import Image,ImageDraw
from numpy.oldnumeric.linear_algebra import eigenvectors
from sklearn.preprocessing import normalize
from numpy import float64
from scipy.spatial.distance import pdist,seuclidean,euclidean,cosine
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.feature_extraction.text import TfidfTransformer
import scipy.cluster.hierarchy as shc

from matplotlib.mlab import PCA

'sampling to choose m entries'
def sample(label,doc):
    tm=10
    m=tm*numpy.unique(label).size
    print('m:',m)
    print(label.shape)
    N=numpy.unique(label)
    no=list(label.reshape(1,-1)[0])
    classsize=[no.count(N[i]) for i in range(N.size)]
    print(classsize)
    lab=numpy.zeros((m,1), int)
    for i in range(numpy.unique(label).size):
        for j in range(tm):
            lab[tm*i+j,0]=i+1
    print('sample...')
    print(doc.shape[0])
    X=numpy.empty((doc.shape[0],0))
    ac=0
    doc=doc.toarray()
    for i in range(numpy.unique(label).size):
        tmp=doc[:,ac:ac+tm]
        tmp=numpy.array(tmp).reshape(-1,tm)
        if ac==0:
            X=tmp
        else:
            X=numpy.hstack((X,tmp))
        ac+=classsize[i]
    return lab,X
'load document data'
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
    '''
    normX=normalize(X,norm='l2',axis=0,copy=False)
    
   
    print("norm:",normX.shape)
    transform=TfidfTransformer(norm='l2',use_idf=True,smooth_idf=True,sublinear_tf=False)
    tfidfX=transform.fit_transform(X.T).T
    tfidfX=tfidfX.toarray()
    #if not os.path.isfile('tfidf.mat'):
    #    scipy.io.savemat('tfidf.mat',{'X':tfidfX,'label':label,'m':m,'nn':nn})
    print("tfidf:",tfidfX.shape)
    '''
    for i in range(nn):
        r=numpy.std(X[i,:])
        if r==0:
            Xstd.append(1) 
        else: 
            Xstd.append(r)
    print("Xstd",len(Xstd),' ',Xstd[0])
    return label,m,nz,nn,X,u,normX,tfidfX,Xstd
'load face image data'
def loadimgdata():
    images = scipy.io.loadmat("image_analysis.mat")
    faces = images['X']
    label = images['label']
    print(scipy.io.whosmat("image_analysis.mat"))
    print(faces.shape)
    m=faces.shape[1] #number of sample
    n=faces[:, 0][0].shape[0] #number of cell
    nn=n*n
    c=10
    X=numpy.empty((nn, 0), int);
    stdX=numpy.empty((nn, 0), float);
    for matrix in faces[0]:
        xl=numpy.empty((n,0),int)
        for column in matrix.T:
            if xl.shape[1]==0:
                xl=column.reshape(-1,1)
            else:
                xl=numpy.vstack((xl,column.reshape(-1,1)))
        X=numpy.hstack((X,xl))
        stdX=numpy.hstack((stdX,(xl-numpy.mean(xl))/numpy.std(xl)))
    u=X.mean(axis=1).reshape(-1,1)
    normX=normalize(X.astype(float64),norm='l2',axis=0)
    Xstd=[]
    for i in range(nn):
        r=numpy.std(X[i,:])
        if r==0:
            Xstd.append(1) 
        else: 
            Xstd.append(r)
    print("Xstd",len(Xstd))
    return label,m,n,nn,X,u,normX,stdX,Xstd
'txtPCA multiply for high dimension document data'
def multiply(A,B):
    Am=A.shape[0]
    An=A.shape[1]
    Bm=B.shape[0]
    Bn=B.shape[1]
    nzA=A.nonzero()
    nzB=B.nonzero()
    nA=[]
    nB=[]
    #print(nzA)
    for i in range(nzA[0].size):
        nA.append(A[nzA[0][i],nzA[1][i]])
    As=csr_matrix((nA,(nzA[0],nzA[1])),shape=(Am,An)).toarray()
    #print("As",As.shape)
    if Am==Bn and An==Bm:
        Bs=As.transpose()
    elif Bn!=1:
        for i in range(nzB[0].size):
            nB.append(B[nzB[0][i],nzB[1][i]])
        Bs=csr_matrix((nB,(nzB[0],nzB[1])),shape=(Bm,Bn)).toarray()
    else:
        Bs=B
    #print("Bs:",Bs.shape)    

    result=As.dot(Bs)
    #print("result:",result.shape)
    return result
'PCA for document data'
def txtpca(label,m,nz,nn,X,u):
    u=X.mean(axis=1).reshape(-1,1)
    u=numpy.array(u)
    if os.path.isfile('txtpca.mat')==True:
        txtpcaf=scipy.io.loadmat('txtpca.mat')
        index=txtpcaf['index']
        eigenvalues=txtpcaf['values']
        eigenvectors=txtpcaf['vectors']
    else:
        if os.path.isfile('xTx.mat')==True:
            xTx=scipy.io.loadmat('xTx.mat')['xx']
        else:
            xTx=multiply(X.T,X)
            scipy.io.savemat('xTx.mat',{'xx':xTx})
        xTu=multiply(X.T,u)
        uTx=xTu.T
        uTu=numpy.dot(u.T,u)
        CT=xTx-uTx-xTu+uTu
        eigenvalues,eigenvectors=numpy.linalg.eigh(CT)
        index=numpy.argsort(-eigenvalues)
        eigenvalues=eigenvalues[index]
        eigenvectors=eigenvectors[:,index]
        scipy.io.savemat('txtpca.mat',{'index':index,'values':eigenvalues,'vectors':eigenvectors})
    print(eigenvalues.shape)
    #eigenvectors=numpy.dot((X-u),eigenvectors)
    #peigen=[]
    #for i in range(eigenvalues[0,:].size):
    #    if not eigenvalues[0,i]<0:
    #        peigen.append(eigenvalues[0,i])
    #print(1.0*numpy.sum(eigenvalues[0,0:1200])/numpy.sum(numpy.fabs(eigenvalues[0,:])))
    #print(1.0*numpy.sum(eigenvalues[0,0:1200])/numpy.sum(peigen))
    print(1.0*numpy.sum(eigenvalues[0,0:6])/numpy.sum(eigenvalues[0,:]))
    pylab.plot(numpy.arange(m),eigenvalues[0,0:m])
    pylab.show()
    if os.path.isfile('rX.mat'):
        rxmat=scipy.io.loadmat('rX.mat')
        index=rxmat['index']
        rX=rxmat['X']
    else:
        xTx=scipy.io.loadmat('xTx.mat')['xx']
        uTx=multiply(X.T,u).T
        rX=multiply(eigenvectors[:,0:6].T,xTx-uTx)
        print("rX",rX.shape)
        scipy.io.savemat('rX.mat',{'index':index,'X':rX})
        print("Done...")
    
    print(rX.shape)
    return index,rX

'LDA for document data'
def txtlda(label,m,nz,nn,X,u):
    if os.path.isfile('rX.mat'):
        rxmat=scipy.io.loadmat('rX.mat')
        X=rxmat['X']
    else:
        X=txtpca(m,nz,nn,X,u)
    nn=X.shape[0]
    m=X.shape[1]
    u=X.mean(axis=1).reshape(-1,1)
    cluster=numpy.unique(label)
    no=list(label.reshape(1,-1)[0])
    clustersize=[no.count(cluster[i]) for i in range(cluster.size)]
    print(clustersize)
    sw=numpy.zeros((nn,nn))
    sb=numpy.zeros((nn,nn))
    startindex=0
    for i in range(cluster.size):
        xi=X[:,startindex:startindex+clustersize[i]]
        ximean=xi.mean(axis=1).reshape(-1,1)
        sw = sw + numpy.dot((xi-ximean),(xi-ximean).T)
        sb = sb + clustersize[i]*numpy.dot((xi-u),(xi-u).T)
        #print("cluster:",cluster[i])
        startindex+=clustersize[i]
    eigenvalues,eigenvectors=numpy.linalg.eigh(numpy.dot(numpy.linalg.inv(sw),sb))
    index = numpy.argsort(-eigenvalues)
    eigenvalues=eigenvalues[index].reshape(1,-1)
    eigenvectors=eigenvectors[:,index]
    print(1.0*(numpy.sum(numpy.fabs(eigenvalues[0,800:1200]))
                         +numpy.sum(numpy.fabs(eigenvalues[0,0:400])))/numpy.sum(numpy.fabs(eigenvalues[0,:])))
    pylab.plot(numpy.arange(1200),eigenvalues[0,0:1200])
    pylab.show()
    
'PCA for face image data (lower dimension)'
def pca(label,m,n,nn,X,u,pcn):
    CT=numpy.dot((X-u).T,(X-u))
    eigenvalues,eigenvectors=numpy.linalg.eigh(CT)
    eigenvectors=numpy.dot((X-u),eigenvectors)
    index=numpy.argsort(-eigenvalues)
    eigenvalues=eigenvalues[index]
    eigenvectors=eigenvectors[:,index]
    pcavalues=eigenvalues[0:10]
    pcavectors=eigenvectors[:,0:10]
    #print(pcavectors.shape)
    #print(pcavalues.size)
    #pylab.figure()
    #pylab.gray()
    #for i in range(10):
        #pylab.imshow(pcavectors[:,i].reshape(n,n).T)
    #pylab.imshow(u.reshape(n,n).T)
        #pylab.show()
    #print(1.0*(numpy.sum(numpy.fabs(eigenvalues[0:120])))/numpy.sum(numpy.fabs(eigenvalues[0:400])))
    x=numpy.arange(100)
    y=eigenvalues[0:100]
    #pylab.plot(x,y)
    #pylab.show()
    #pcn=(400-40)
    eigenvectors=eigenvectors[:,0:pcn]
    rX=numpy.dot(eigenvectors.T,X)
    return rX,eigenvectors
    
'LDA for face image data (lower dimension)'
def lda(label,m,n,nn,X,u):
    c=10
    X,W=pca(label,m,n,nn,X,u,(400-40))
    nn=X.shape[0]
    u=X.mean(axis=1).reshape(-1,1)
    cluster=numpy.unique(label)
    sw=numpy.zeros((nn,nn))
    sb=numpy.zeros((nn,nn))
    for i in cluster:
        xi=X[:,(i-1)*c:i*c]
        ximean=xi.mean(axis=1).reshape(-1,1)
        sw = sw + numpy.dot((xi-ximean),(xi-ximean).T)
        sb = sb + c*numpy.dot((xi-u),(xi-u).T)
    eigenvalues,eigenvectors=numpy.linalg.eigh(numpy.dot(numpy.linalg.inv(sw),sb))
    index = numpy.argsort(-eigenvalues)
    eigenvalues=eigenvalues[index]
    eigenvectors=eigenvectors[:,index]
    pcvalues=eigenvalues[0:10]
    pcvectors=eigenvectors[:,0:10]
    pcvectors=numpy.dot(W,pcvectors)
    #print(1.0*(numpy.sum(numpy.fabs(eigenvalues[0:100])))/numpy.sum(numpy.fabs(eigenvalues[0:400])))
    #pylab.plot(numpy.arange(100),eigenvalues[0:100])
    pylab.figure()
    pylab.gray()
    for i in range(10):
        pylab.imshow(pcvectors[:,i].reshape(n,n).T)
    #pylab.imshow(u.reshape(n,n).T)
        pylab.show()
    #pylab.imshow(u.reshape(n,n).T)
    #pylab.show()
    print(eigenvalues.shape)
    
'K-means clustering for both data'
def kmeans(ci,label,m,n,nn,X,u,pcn):
    K=[5,10,20,30,40,50,4]
    changed=True
    k=K[ci]
    '''
    tfidf=scipy.io.loadmat('tfidf.mat')
    X=tfidf['X'].toarray()
    label=tfidf['label']
    m=tfidf['m']
    nn=tfidf['nn']
    nz=0
    '''  
    #X=X.toarray()
    #X,W=pca(label,m,n,nn,X,u,pcn)
    nn=X.shape[0]
    u=X.mean(axis=1).reshape(-1,1)
    clustercenters=numpy.zeros((nn,k))
    nodesclass=numpy.zeros((m,2))
    nodemin=numpy.amin(X, axis=1).reshape(-1,1)
    nodemax=numpy.amax(X, axis=1).reshape(-1,1)
    for p in range(nn):
        clustercenters[p,:]=nodemin[p]+(nodemax[p]-nodemin[p])*numpy.random.rand(1,k)
    #print(clustercenters)
    iteration=0;
    while(changed):
        iteration= iteration + 1
        changed=False
        for i in range(m):
            node=X[:,i].reshape(-1,1)
            mindis=numpy.Inf
            minIndex=-1
            for j in range(k):
                center=clustercenters[:,j].reshape(-1,1)
                distance=numpy.sqrt(numpy.sum((node-center)**2))
                if distance < mindis:
                    mindis=distance
                    minIndex=j
            if nodesclass[i,0]!=minIndex: changed=True
            nodesclass[i,:]=minIndex,mindis
        for ct in range(k):
            if numpy.nonzero(nodesclass[:,0]==ct)[0].size!=0:
                sumx=X[:,numpy.nonzero(nodesclass[:,0]==ct)[0]]
                clustercenters[:,ct]=numpy.mean(sumx,axis=1)
        print("Iteration Number:",iteration)
    #print(nodesclass)
    purity=numpy.zeros(k)
    N=numpy.unique(label)
    no=list(label.reshape(1,-1)[0])
    classsize=[no.count(N[i]) for i in range(N.size)]
    #print(classsize)
    count=numpy.zeros((N.size,k))
    beginIndex=0
    for p in range(N.size):
        nodes=nodesclass[beginIndex:beginIndex+classsize[p],0].reshape(-1,1)
        for t in range(k):
            count[p,t]=numpy.sum(nodes[:,0]==t)
        beginIndex+=classsize[p]
    num=numpy.sum(count, axis=0)
    #print(count)

    for h in range(num.size):
        if num[h]==0:
            num[h]=1
    purity=numpy.amax(count, axis=0)/num
    print("\\\    Cluster Purity:",purity)

    B=0
    C=0
    for i in range(N.size):
        tempA=0.0
        for j in range(k):
            tempA = tempA + count[i,j]*(count[i,j]-1)/2.0
        B = B - tempA + numpy.sum(count[i,:])*(numpy.sum(count[i,:])-1)/2.0
    for i in range(k):
        tempA=0.0
        for j in range(N.size):
            tempA = tempA + count[j,i]*(count[j,i]-1)/2.0
        C = C - tempA + numpy.sum(count[:,i])*(numpy.sum(count[:,i])-1)/2.0
    randSum=(label.size)*(label.size-1)/2.0    
    RandIndex=(randSum-(B+C))/randSum
    print("\\\    Rand Index:",RandIndex)
    return RandIndex
'hierarchical clustering tree structure'
class tree:
    def __init__(self,node,left=None,right=None,dist=0.0,id=None,item=[]):
        self.left=left
        self.right=right
        self.node=node
        self.dist=dist
        self.id=id
        self.item=item
'hierarchical clustering cluster merging method'
def mergedis(x,y,Xstd):
    nodesX=[]
    nodesY=[]
    if len(x.item)==0:
        nodesX.append(x)
    else:
        nodesX=x.item
    if len(y.item)==0:
        nodesY.append(y)
    else:
        nodesY=y.item
    dmax=0.0
    dmin=numpy.Inf
    davg=0.0
    for i in range(len(nodesX)):
        for j in range(len(nodesY)):
            if dists.get((nodesX[i].id,nodesY[j].id)) == None:
                #dists[(nodesX[i].id,nodesY[j].id)]=numpy.sqrt(numpy.sum(((nodesX[i].node-nodesY[j].node)/Xstd)**2))
                dists[(nodesX[i].id,nodesY[j].id)]=cosine(nodesX[i].node,nodesY[j].node)
            dis=dists.get((nodesX[i].id,nodesY[j].id))
            if dis < dmin:
                dmin=dis
            if dis > dmax:
                dmax=dis
            davg = davg+dis
        #print("ddd:",i)
    #print("lenX:",len(nodesX)," lenY:",len(nodesY))
    davg=davg/(len(nodesX)*len(nodesY))
    return dmax,dmin,davg
'hierarchical clustering used for both data'
def hc(j,label,m,n,nn,X,u,Xstd):
    K=[5,10,20,30,40,50]
    kc=K[j]
    X,W=pca(label,m,n,nn,X,u,1200)
    nn=X.shape[0]
    u=X.mean(axis=1).reshape(-1,1)
    Xstd=[]
    for i in range(nn):
        r=numpy.std(X[i,:])
        if r==0:
            Xstd.append(1) 
        else: 
            Xstd.append(r)
    treenodes=[tree(X[:,i],id=i) for i in range(m)]
    newnodeid=m
    global dists
    dists={}
    iteration=0
    #euclidean_distances(X[:,0:10],X[:,0:10])
    #print("step...")
    dty=0
    #dmax,dmin,davg
    while len(treenodes)>1:
        mindis=numpy.Inf
        minpair=None
        for i in range(len(treenodes)):
            for j in range(i+1,len(treenodes)):
                if dists.get((treenodes[i].id,treenodes[j].id)) == None:
                    dists[(treenodes[i].id,treenodes[j].id)]=mergedis(treenodes[i],treenodes[j],Xstd)[dty]
                dis=dists.get((treenodes[i].id,treenodes[j].id))
                if dis < mindis:
                    mindis = dis
                    minpair=(i,j)
                #print("stepj:",j)
            #print("*******stepii",i)
        node=(treenodes[minpair[0]].node+treenodes[minpair[1]].node)/2.0
        newtreenode=tree(node,left=treenodes[minpair[0]],right=treenodes[minpair[1]],dist=mindis,id=newnodeid,item=[])
        for c in range(2):
            if len(treenodes[minpair[c]].item)>=1:
                for i in range(len(treenodes[minpair[c]].item)):
                    newtreenode.item.append(treenodes[minpair[c]].item[i])
            else:
                newtreenode.item.append(treenodes[minpair[c]])
        del treenodes[minpair[1]]
        del treenodes[minpair[0]]
        treenodes.append(newtreenode)
        iteration+=1
        newnodeid+=1
        #print("iteration:",iteration)
    #print("tree size:",len(treenodes))
    notes=[str(label[k,0]) for k in range(label.size)]
    dendrogram(treenodes[0],m,notes)
    purity=numpy.zeros(kc)
    N=numpy.unique(label)
    no=list(label.reshape(1,-1)[0])
    classsize=[no.count(N[i]) for i in range(N.size)]
    print(classsize)
    
    count=numpy.zeros((N.size,kc))
    Xclusters=[]
    ic=0
    t=None
    while(len(Xclusters)<kc):
        ic+=1
        if len(Xclusters)==0:
            Xclusters.append(treenodes[0])
        else:
            root=Xclusters[0]
            nl=len(Xclusters)
            if nl>1:
                for i in range(nl-1):
                    Xclusters[i]=Xclusters[i+1]
                del Xclusters[nl-1]
            else: del Xclusters[0]
            if root.left!=None:
                Xclusters.append(root.left)
            if root.right!=None:
                Xclusters.append(root.right)
        print(len(Xclusters))
        if ic>m:
            print("No result...")
            break
            return
    #for i in range(len(Xclusters)):
        #print(len(Xclusters[i].item))
    for i in range(kc):
        for j in range(N.size):
            ns=0
            for ik in range(len(Xclusters[i].item)):
                if label[Xclusters[i].item[ik].id]==j+1:
                    ns+=1
            count[j,i]=ns
        print('i:',i)
    num=numpy.sum(count, axis=0)
    for h in range(num.size):
        if num[h]==0:
            num[h]=1
    purity=numpy.amax(count, axis=0)/num
    print("\\\    Cluster Purity:",purity)
    B=0
    C=0
    for i in range(N.size):
        tempA=0.0
        for j in range(kc):
            tempA = tempA + count[i,j]*(count[i,j]-1)/2.0
        B = B - tempA + numpy.sum(count[i,:])*(numpy.sum(count[i,:])-1)/2.0
    for i in range(kc):
        tempA=0.0
        for j in range(N.size):
            tempA = tempA + count[j,i]*(count[j,i]-1)/2.0
        C = C - tempA + numpy.sum(count[:,i])*(numpy.sum(count[:,i])-1)/2.0
    randSum=(label.size)*(label.size-1)/2.0    
    RandIndex=(randSum-(B+C))/randSum
    print("\\\    Rand Index:",RandIndex)
    
'methods for drawing dendrogram'
def high(tree):
    if tree.left==None and tree.right==None:
        return 1
    return high(tree.left)+high(tree.right)
def deep(tree):
    if tree.left==None and tree.right==None:
        return 0
    return numpy.maximum(deep(tree.left),deep(tree.right))+tree.dist
def paintnode(paint,tree,m,x,y,factor,notes):
    if tree.id>=m:
        ha=high(tree.left)*5*3
        hb=high(tree.right)*5*3
        hig=y-(ha+hb)/2
        low=y+(ha+hb)/2
        linelen=tree.dist*factor
        paint.line((x,hig+ha/2,x,low-hb/2),fill=(0,0,255))
        paint.line((x,hig+ha/2,x+linelen,hig+ha/2),fill=(0,0,255))
        paint.line((x,low-hb/2,x+linelen,low-hb/2),fill=(0,0,255))
        paintnode(paint,tree.left,m,x+linelen,hig+ha/2,factor,notes) 
        paintnode(paint,tree.right,m,x+linelen,low-hb/2,factor,notes)
    else:
        paint.text((x+3,y-5),notes[tree.id],(0,0,0))
'main function for dendrogram drawing'
def dendrogram(tree,m,notes):
    h=high(tree)*5*3
    w=500
    d=deep(tree)
    factor=1.0*(w-200*0.1)/d
    img=Image.new('RGB',(w,h),(255,255,255))
    paint=ImageDraw.Draw(img)
    paint.line((0,h/2,5,h/2),fill=(0,0,255))
    paintnode(paint, tree, m, 5, h/2, factor, notes)
    img.save("dendrogram_raw_max.png", "PNG")  
    #img.save("dendrogram_std_min.png", "PNG")  
    #img.save("dendrogram_std_avg.png", "PNG") 
'k-Nearest Neighbor classification for both data'
def knn(c1,c2,label,m,n,X,u,Xstd,sigfile):   
    kNumber=[1,3,5]
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
    result=[]
    for index in range(0,int(m/cv),int(m/(cv*cv))):
        train=[]
        trainIndex=[]
        test=[]
        testIndex=[]
        correct=0
        print("index:",index)
        #print(int(m/(cv*cv)))
        #print(int(m/cv))
        tm=m
        if int(m/(cv*cv))*cv*cv < m:
            tm=int(m/(cv*cv))*cv*cv
            #print("tm:",tm)
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
                    dist[(trainIndex[j],testIndex[i])]=numpy.sqrt(numpy.sum(((train[j]-test[i])/Xstd)**2))
                    
                    #dist[(trainIndex[j],testIndex[i])]=cosine(train[j],test[i])
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
        cratio=correct*1.0/(len(test))
        print("correct Number: ",correct," ",cratio)
        print(index) 
        result.append(cratio)
        #print(sigma)  
    print("\\\ Average:",numpy.mean(result))
    print("\\\ Standard Deviation:",numpy.std(result))
    print(len(sigma))
    scipy.io.savemat(sigfile,{'sigma':sigma})
    print('DONE......')
    return sigma
'similarity network and heatmap'
def sn(c1,label,m,n,X,u,Xstd):
    nn=4852
    fname='tfidfX.mat'
    sigfile='sigma_X.mat'
    
    if os.path.isfile(fname):
        rxmat=scipy.io.loadmat(fname)
        X=rxmat['X']
    else:
        X=txtpca(m,1,nn,X,u)
    nn=X.shape[0]
    print('nn:',nn)
    u=X.mean(axis=1).reshape(-1,1)
    m=X.shape[1]
    Xstd=[]
    for i in range(nn):
        r=numpy.std(X[i,:])
        if r==0:
            Xstd.append(1) 
        else: 
            Xstd.append(r)
    #if os.path.isfile(sigfile):
    #    tdata=scipy.io.loadmat(sigfile)
    #    sigma=tdata['sigma'][0]
    #else: 
    sigma=knn(c1,0,label,m,n,X,u,Xstd,sigfile)
    print(len(sigma))
    #netfile='net_X.mat'
    #if os.path.isfile(netfile):
    #    td=scipy.io.loadmat(netfile)
    #    snet=td['net']
    #else:
    mc=600 
    snet=numpy.zeros((mc,mc))
    for i in range(mc):
        for j in range(i+1,mc):
            d=numpy.sum(((X[:,i]-X[:,j])/Xstd)**2)
            snet[i,j]=numpy.exp(-1.0*d/(2*sigma[i]*sigma[j]))
            snet[j,i]=snet[i,j]
            print('step:',i)
    #scipy.io.savemat(netfile,{'net':snet})
    
    pylab.pcolor(snet[0:mc,0:mc])
    pylab.show()
'KMeans batch for document data'
def tkmtest(j,label,m,nz,nn,X,u,normX,tfidfX,Xstd):
    t=100
    result=numpy.zeros((t,3))
    '''
    if os.path.isfile('X.mat'):
        rxmat=scipy.io.loadmat('X.mat')
        X=rxmat['X']
    for i in range(t):
        result[i,0]=kmeans(j,label,m,nz,nn,X,u,1)
        print("raw",i)
    if os.path.isfile('normX.mat'):
        rxmat=scipy.io.loadmat('normX.mat')
        normX=rxmat['X']
    for i in range(t):
        result[i,1]=kmeans(j,label,m,nz,nn,normX,u,1)
        print("norm",i)
    '''
    if os.path.isfile('tfidfX.mat'):
        rxmat=scipy.io.loadmat('tfidfX.mat')
        tfidfX=rxmat['X']
    for i in range(t):
        result[i,2]=kmeans(j,label,m,nz,nn,tfidfX,u,1)
        print("tfidf",i)

    x=range(t)
    #y=result[:,0]
    #z=result[:,1]
    w=result[:,2]
    #pylab.plot(x,y,label='Raw Data')
    #pylab.plot(x,z,label='Norm Data')
    pylab.plot(x,w,label='TF-IDF Data')
    pylab.ylim(0.0,1.0)
    pylab.legend(loc='lower right')
    pylab.show()
'KMeans batch for face image data'
def kmtest(j,label,m,nz,nn,X,u,normX,stdX,Xstd):
    t=100
    result=numpy.zeros((t,3))
    for i in range(t):
        result[i,0]=kmeans(j,label,m,nz,nn,X,u,1)
        print("raw",i)
    for i in range(t):
        result[i,1]=kmeans(j,label,m,nz,nn,normX,u,1)
        print("norm",i)
    for i in range(t):
        result[i,2]=kmeans(j,label,m,nz,nn,stdX,u,1)
        print("std",i)
    x=range(t)
    y=result[:,0]
    z=result[:,1]
    w=result[:,2]
    pylab.plot(x,y,label='raw')
    pylab.plot(x,z,label='norm')
    pylab.plot(x,w,label='standard')
    pylab.ylim(0.5,1.0)
    pylab.legend(loc='lower right')
    pylab.show()
'KMeans with PCA'
def km_pca(j,label,m,nz,nn,X,u,normX,stdX,Xstd):
    ratio=[0.1,0.3,0.5,0.7,0.9]
    pcns=numpy.dot(m,ratio)
    print("\\\    {\\bf Raw Data:}")
    for i in range(5):
        print("\\\    {\\bf ",(int)(100*ratio[i]),"\\% PCA}")
        kmeans(j,label,m,nz,nn,X,u,pcns[i])
    print("\\\    {\\bf Normalized Data:}")
    for i in range(5):
        print("\\\    {\\bf ",(int)(100*ratio[i]),"\\% PCA}")
        kmeans(j,label,m,nz,nn,normX,u,pcns[i])
    print("\\\    {\\bf Standardized Data:}")
    for i in range(5):
        print("\\\    {\\bf ",(int)(100*ratio[i]),"\\% PCA}")
        kmeans(j,label,m,nz,nn,stdX,u,pcns[i])
'hierarchical clustering of different data'
def hctest(label,m,nz,nn,X,u,normX,stdX,Xstd):
    K=[5,10,20,30,40,50]
    for j in range(6):
        print(" {\\bf ",j+1,")} Number of cluster: ",K[j])
        print("\\begin{quote}")
        print("\\\    {\\bf Raw Data:}")
        hc(j,label,m,nz,nn,X,u,Xstd)
        print("\\\    {\\bf Normalized Data:}")
        hc(j,label,m,nz,nn,normX,u,Xstd)
        print("\\\    {\\bf Standardized Data:}")
        hc(j,label,m,nz,nn,stdX,u,Xstd)
        print("\\end{quote}")
'K-Nearest Neighbor of 10,5 cross fold validation'
def knntest(label,m,nz,nn,X,u,normX,stdX,Xstd):
    kNumber=[1,3,5]
    cvNumber=[10,5] 
    #knn(1,1,label,m,nz,stdX,u,Xstd)
    for i in range(3):
        print("\\\ ",kNumber[i],"-Nearest Neighbor")
        for j in range(2):
            print("\\\ ",cvNumber[j]," fold cross validation:")
            knn(i,j,label,m,nz,normX,u,Xstd)
'Main function for whole program'
if __name__ == '__main__':
    #label,m,nz,nn,X,u,normX,stdX,Xstd=loadimgdata()
    j=0
    #hc(j,label,m,nz,nn,X,u,Xstd)
    #pca(label,m,nz,nn,X,u,m)
    #lda(label,m,nz,nn,stdX,u)
    #for j in range(6):
        #kmeans(j,label,m,nz,nn,stdX,u,1)
    #for h in range(1,6):
        #kmtest(h,label,m,nz,nn,X,u,normX,stdX,Xstd)
    #for j in range(6):
        #km_pca(5,label,m,nz,nn,X,u,normX,stdX,Xstd)
    #hctest(label,m,nz,nn,X,u,normX,stdX,Xstd)   
    #knn(1,1,label,m,nz,X,u,Xstd)
    #sn(0,label,m,nz,stdX,u,Xstd)
    
    label,m,nz,nn,X,u,normX,tfidfX,Xstd=loadtxtdata()
    #txtpca(label,m,nz,nn,X,u)
    #txtlda(label,m,nz,nn,tfidfX,u)
    #kmeans(j,label,m,nz,nn,normX,u,1)
    #kmeans(j,None,0,0,0,None,None,1)
    #tkmtest(j,label,m,nz,nn,X,u,normX,tfidfX,Xstd)
    #hc(j,label,m,nz,nn,tfidfX,u,Xstd)
    #sn(2,label,m,nz,X,u,Xstd)
    
    label=label.reshape(1,-1)[0]
    labelclass=[0]*5
    n=1
    for i in range(m-1):
        if label[i]!=label[i+1]:
            labelclass[n]=i+1
            n+=1
    #labelclass[4]=m
    print(labelclass)
    k=20
    y=numpy.array(X[:,0:k]).reshape(-1,k)
    #y=numpy.hstack((y,numpy.array(X[:,1]).reshape(-1,1)))
    print(y.shape)
    for i in range(1,5):
        s=labelclass[i]
        x=numpy.array(X[:,s:s+k]).reshape(-1,k)
        y=numpy.hstack((y,x))
    print(y.shape)
    label=[1+(int)(i/k) for i in range(5*k)]
    print(label)
    
    pylab.plot(numpy.arange(100),label[0:100])
    pylab.show()
    