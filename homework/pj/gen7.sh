#!/bin/bash
attr=(RT SERIALNO PUMA ADJINC HINS4 INTP OIP PAP RETP SEMP SSIP SSP WAGP NAICSP PERNP PINCP POVPIP SOCP FAGEP)
attrid=(0)
i=0
k=0
field=`awk 'NR==1 {print$0}' $1`
field=(${field//,/ })
echo ${#field[@]}
#while [ $i -lt ${#attr[@]} ]
for at in ${attr[@]}
do
    while [ $k -lt ${#field[@]} ]
    do
        if [ $at == ${field[$k]} ] 
        then
           attrid[$i]=`echo "$k+1"|bc`
           break
        fi
        k=`echo "$k+1"|bc`
    done
    k=$k
    i=`echo "$i+1"|bc`
done
echo ${attrid[@]}
#awk -F, 'NR==1 { for(j=0;j<$N;j++) if(j==0){for(t=1;t<=attrid[$j];t++) printf$t" "} else {for(i=attrid[$j-1];i<attrid[$j];i++) printf$i" "} for(k=attrid[$N-1];k<=NF;k++) printf$k" "}' $1 > output
