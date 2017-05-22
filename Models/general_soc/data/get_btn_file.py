#!/usr/bin/python
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


def modify_graph_weights(graph):
  
  for edge in graph.edges():
    u, v = edge
    distance = graph[u][v]['weight']*0.000621371
    location = graph.node[u]['location']

    speed = graph.node[u]['speed_urban']*0.3
    time = distance/speed*3600
    graph[u][v]['time'] = time

    
if __name__ == "__main__":
    #graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/lower_manhattan1_5.graphml")
    #graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/greenville1_5.graphml")
    graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/manhattan_neigborhood.graphml")
    modify_graph_weights(graph)
    cen_measure = nx.betweenness_centrality(graph, weight='time')
    cen_file = open("manhattan_neigh_betweenness.centrality", "w")
    
    for node in range(1, nx.number_of_nodes(graph) + 1):
      cen = cen_measure[str(node)]
      cen_file.write(str(cen) + '\n')
    
    cen_file.close()
    
