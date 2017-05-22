import json
from pprint import pprint
#import pygraphviz
import sys
import argparse
import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
import scipy
from networkx.drawing.nx_agraph import graphviz_layout


json_filename = '/home/hushiji/Research/smart_cities/smart_cities/general_soc/copy_random_start_soc_1150.json'
seg_installFile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/copy_random_start_soc_1150_25percent_gap_seg_install.txt", "w")


with open(json_filename) as data_file:    
    data = json.load(data_file)
nroutes = 0

Install_seg = []

variables = data['Solution'][1]['Variable']
for key in variables:
  
  if key[0] == 'r':
    #print int(key[len('roadInstall') + 1:-1]) - 2
    node =  int(key[len('roadInstall') + 1:-1]) - 2
    value =  variables[key]['Value']
    if node != 0 and value > 0.1:
      Install_seg.append(str(node))


for seg in Install_seg:
  seg_installFile.write(seg+"\n")
  
seg_installFile.close()

