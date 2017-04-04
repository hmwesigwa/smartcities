import json
from pprint import pprint
import pygraphviz
import sys
import argparse
import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
import scipy
from networkx.drawing.nx_agraph import graphviz_layout


json_filename = '/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/results.json'
roadSegGraph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/lower_manhattan1_5.graphml")
edgeFile = open("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/edges.edges", 'r')
routesFile = open("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/routes.txt", 'r')

edges = []
for line in edgeFile:
  u, v = line.split()
  edge = (u, v)
  edges.append(edge)

with open(json_filename) as data_file:    
    data = json.load(data_file)
nroutes = 0
for line in routesFile:
  nroutes += 1

#pprint(data)
Install_seg = []
#print type(data['Solution'][1]['Variable'])
variables = data['Solution'][1]['Variable']
for key in variables:
  
  if key[0] == 'r':
    #print int(key[len('roadInstall') + 1:-1]) - 2
    node =  int(key[len('roadInstall') + 1:-1]) - 2
    value =  variables[key]['Value']
    if node != 0 and value > 0.1:
      Install_seg.append(str(node))

cost = 0
for seg in Install_seg:
  cost += float(roadSegGraph.node[str(seg)]['length']*0.236)

pos = graphviz_layout(roadSegGraph, prog='sfdp')

node_sizes = [50 if node in Install_seg else 1 for node in roadSegGraph.nodes()]
node_colors = ['red' if node in Install_seg else 'gray' for node in roadSegGraph.nodes()]
edge_colors = ['blue' if edge in edges else 'gray' for edge in roadSegGraph.edges()]
edge_width = [4.0 if edge in edges else 1.0 for edge in roadSegGraph.edges()]
nnodes = len(node_sizes)
num_install = len(Install_seg)
graph_title = " ".join([str(nnodes), "nodes", str(num_install), "units", "$" + str(round(cost,3)),"thousand", str(nroutes), "routes" ])
plt.title(graph_title)
pic_name = "_".join([str(nnodes), "nodes", str(num_install), "units"])
nx.draw(roadSegGraph, pos,  node_size=node_sizes, node_color=node_colors,edge_color=edge_colors, arrows=False,with_labels=False)
#plt.savefig(pic_name+'.png', dpi=400)
plt.show()

