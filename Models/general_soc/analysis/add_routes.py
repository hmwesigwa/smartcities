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
import write_data
from joblib import Parallel, delayed
#import multiprocessing
#import plotly.plotly as py

DECREASE_SPEED = 0.3
INCREASE_LENGTH = 10
def path_feasible(path, graph, init_soc, install_dic):

    current_range_soc = init_soc
    for roadSeg in path:
        INSTALL = install_dic[roadSeg]
        #INSTALL = False
        velocity = graph.node[roadSeg]['speed_urban']*DECREASE_SPEED #this is modified such that if we install every then final_soc = 1 if start_soc = 1
        distance = graph.node[roadSeg]['length']*0.000621371*INCREASE_LENGTH
       
        current_range_soc = write_data.nextSOC_real_data(current_range_soc, distance, 1, velocity, INSTALL)
        #print current_range_soc

    return current_range_soc
   




def modify_graph_weights(graph):
  
  for edge in graph.edges():
    u, v = edge
    distance = graph[u][v]['weight']*0.000621371
    location = graph.node[u]['location']

    speed = graph.node[u]['speed_urban']*0.3
    time = distance/speed*3600
    graph[u][v]['time'] = time
    
 
def random_solution(graph, budget_in_meters):


    
    budget_used = 0
    random_segment_index = range(nx.number_of_nodes(graph))
    random.shuffle(random_segment_index)
    
    road_seg = []
    
    for indx in random_segment_index:
        
        road = graph.nodes()[indx]

        if budget_used + float(graph.node[road]['length']) <= budget_in_meters:
            road_seg.append(road)
            budget_used += float(graph.node[road]['length'])
        if budget_used >= budget_in_meters:
            break
    rand_file = open("10random_seg_install.txt", "w")
    for i in road_seg:
        rand_file.write(str(i) + '\n')
    rand_file.close()
    return road_seg


    
  
if __name__ == "__main__":
    #graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/lower_manhattan1_5.graphml")
    #graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/greenville1_5.graphml")
    graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/manhattan_neigborhood.graphml")
    cen_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/data/manhattan_neigh_betweenness.centrality")
    #model_installfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/exp_install.txt")
    model_installfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/exp_install_20percent.txt")
    model_install = {}
    routes_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/100_routes_20percent.txt", "r")
    iterative_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/iterative_routes.txt", "w")
    infeasible_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/20_percent_infeasible_routes.txt", "r")
    
    
    used_routes = {}
    for line in routes_file:
      _path = line.split()
      start = str(int(_path[0]) -2 )
      end = str(int(_path[-2]) - 2)
      used_routes[(start,end)] = True
    
    btn_cen = {}
    node = 1
    for line in cen_file:
      btn_cen[str(node)] = float(line)
      node += 1
      
    sorted_cen = sorted([(btn_cen[node], node ) for node in graph.nodes()], reverse=True)
    budget = 0.2
    total_distance = 0
    btn_install_dic = {}
    
    for node in graph.nodes():  
      btn_install_dic[node] = False
      model_install[node] = False
      total_distance += float(graph.node[node]['length'])
    model_distance = 0
    
    for line in model_installfile:
      model_install[str(int(line))] = True
      model_distance += float(graph.node[str(int(line))]['length'])
    distance_used = 0
    btn_install_nodes = []
    
    for cen, node in sorted_cen:
      distance = float(graph.node[node]['length'])
      if distance_used + distance <= budget*total_distance:
        btn_install_nodes.append(node)
        btn_install_dic[node] = False
        distance_used += distance
    print "Budget: %f \t Model: %f \t Btn: %f" %(budget, model_distance/total_distance, distance_used/total_distance) 
    
    nnodes = nx.number_of_nodes(graph)
    tuple_indx = range(nnodes*nnodes)
    print 'before shuffle'
    random.shuffle(tuple_indx)
    print 'after shuffle'
    route_indx = 0
    total_routes = nnodes**2

    for line in infeasible_file:
      start, end, soc = line.split()
      if (start, end) not in used_routes:
        used_routes[(start, end)] = True

    for start, end in used_routes:
      iterative_file.write(start + " " + end + "\n")
     
    iterative_file.close()
