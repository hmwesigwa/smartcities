#!/usr/bin/python

#script to compare different solutions

from __future__ import division
import json
import sys, os
import argparse
import math
import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
import scipy
import collections
import random

#accumulate to results from each job and plot. folder = output from palmetto



def extract_soc_data(filename):

    soc_file = open(filename, 'r')
    output = []
    for line in soc_file:

        if line[0].isdigit():
  
            output.append(line)
         

    return output


#folder = '/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/solutions/soc_data/soc_Install/1soc_install/'
#folder = '/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/solutions/soc_data/split_soc/run_data/less_than_01_run/'
#folder = '/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/solutions/soc_data/split_soc/run_data/accum_2/'
folder = '/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/plot/run_data/exp_data/'
print "plotting data"
acc0  = [0 for i in range(51)]
acc1  = [0 for i in range(51)]
acc2  = [0 for i in range(51)]
acc3  = [0 for i in range(51)]
acc4  = [0 for i in range(51)]
acc5  = [0 for i in range(51)]
for filename in os.listdir(folder):

    output = extract_soc_data(folder+filename)
    if len(output) > 0:

        #_acc0, _acc1, _acc2, _acc3, _acc4, _acc5= output
        _acc0, _acc1, _acc2 = output
      
        for k, i in enumerate(_acc0.split()):
            acc0[k] += int(i)
            
        for k, i in enumerate(_acc1.split()):
            acc1[k] += int(i)
        for k, i in enumerate(_acc2.split()):
            acc2[k] += int(i)
        #for k, i in enumerate(_acc3.split()):
        #    acc3[k] += int(i)       
        
        #for k, i in enumerate(_acc4.split()):
        #    acc4[k] += int(i)      
        #for k, i in enumerate(_acc5.split()):
        #    acc5[k] += int(i)  

#print acc0
#print acc1
#print acc2
#print acc3
#print acc4
plt.plot([i/50 for i in range(51)][20:], acc0[20:], color='b', linewidth=3.0, label='0%')  
plt.plot([i/50 for i in range(51)][20:], acc1[20:],  linewidth=3.0, color='g',label='30% model') 
plt.plot([i/50 for i in range(51)][20:], acc2[20:],  linewidth=3.0,color='r',label='30% betweenness') 
#plt.plot([i/50 for i in range(51)][20:], acc3[20:],  linewidth=3.0,color='k',label='ALL') 
#plt.axvline(x=0.7, linestyle='dashed')
#plt.plot([i/50 for i in range(51)][20:40], acc3[20:40],  label='1% eigen vector') 
#plt.plot([i/50 for i in range(51)], acc4,  label='1% eigen vector')   
#plt.plot([i/50 for i in range(51)], acc5, linewidth=3.0, label='1% model * routes * nlayer') 
plt.legend(loc='upper left')

plt.title("SOC Distribution")
plt.xlabel("SOC")
plt.ylabel("No. Routes")
ax = plt.axes()
#plt.show()

#fig = plt.figure()
plt.show()
