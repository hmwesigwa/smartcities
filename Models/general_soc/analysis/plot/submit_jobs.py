import os
import sys
import scipy
import time 
import networkx as nx
import random
#folder = "/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/solutions"

def alter_palmetto_file(start):
	
	str = """#!/bin/bash      
#PBS -N example      
#PBS -l select=1:ncpus=1:mem=2gb:interconnect=1g,walltime=00:45:00  
#PBS -j oe      

source /etc/profile.d/modules.sh  
module purge   
module add gcc
cd /home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis


"""
	pal_FILE= open('palmetto.txt','w')
	pal_FILE.write(str)
	str2 = "".join(["python method_comparison.py ", start])
	pal_FILE.write(str2)
	
	pal_FILE.close()
	

#graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/lower_manhattan1_5.graphml")
graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/greenville1_5.graphml")
count = 0
nodes = graph.nodes()
random.shuffle(nodes)
for start in nodes:
    count += 1
    if count%30 == 0:
        time.sleep(10*60)
    alter_palmetto_file(start)	
	
    command = "/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/plot/submitall.sh"

    os.system( command)
		

