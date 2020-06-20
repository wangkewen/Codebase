import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
y=[]
high=300000
f=open('income11','r')
incomemax=0.0
incomemin=1.0
th=100000
thnum=0
for line in f:
    x=eval(line)
    y.append(x)
    if x>incomemax: incomemax=x
    if x<incomemin: incomemin=x
    if x<th: thnum+=1
print("Income <$10k: ",thnum)
print("Num:", len(y))
y.sort()
print("sorted...")
print(y[len(y)-1]," ",y[0])
gn = 30
interval = high * 1.0 / gn
xvalue = []
for i in range(gn+1):
    xvalue.append(interval*i)
xvalue.append(interval*(i+1))
stat = [0] * ( gn + 2 )
cn=0
index=0
svalue=0.0
for i in range(len(y)):
    svalue+=y[i]
    cn+=1
    if(index<=gn and y[i]>=index*interval):
        stat[index]=cn*100.0/len(y)
        cn=0
        index+=1
stat[index]=cn*100.0/len(y)  
print("Interval:",interval)      
print(stat)

'''
AVG: 32768.56448544411
Mean: 19600
'''
print("AVG:",svalue/len(y))
print("Mean:",y[int(len(y)*1.0/2)])
print("MIN:",incomemin)
print("MAX:",incomemax)
ax.scatter(xvalue, stat,marker = 'o')
plt.xticks([-5000,0,50000,100000,150000,200000,250000,300000,350000],['',0,50000,100000,150000,200000,250000,300000,int(incomemax)],fontsize = 15)
plt.yticks(fontsize = 15)
ax.set_xlabel('Income Value ($)', fontsize=20)
ax.set_ylabel('Income Distribution (%)', fontsize=20)
plt.show()

