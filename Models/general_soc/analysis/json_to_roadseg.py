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


json_filename = '/home/hushiji/Research/smart_cities/smart_cities/general_soc/greenville_exp.json'
roadSegGraph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/greenville1_5.graphml")


seg_installFile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/exp_seg_install.txt", "w")



with open(json_filename) as data_file:    
    data = json.load(data_file)

Install_seg = []
variables = data['Solution'][1]['Variable']
for key in variables:
  
  if key[0] == 'r':

    node =  int(key[len('roadInstall') + 1:-1]) - 2
    value =  variables[key]['Value']
    if node != 0 and value > 0.1:
      Install_seg.append(str(node))


for seg in Install_seg:
  seg_installFile.write(seg+"\n")
  
seg_installFile.close()

