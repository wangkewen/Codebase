#!/bin/bash
awk -F, 'BEGIN{strs="1 2 4 6 28 32 61 62 64 68 70 71 72 97 103 104 106 127 130"; len=split(strs,keys," ");} NR>1 {if($104>10000) printf"1 ";else printf"0 ";   for(k=1;k<=len;k++) {if(k==1) for(i=1;i<keys[k];i++) if($i=="") printf"-1 "; else printf("%d ",$i); else for(j=keys[k-1]+1;j<keys[k];j++) if($j=="") printf"-1 "; else printf("%d ",$j);} print"";}' $1
