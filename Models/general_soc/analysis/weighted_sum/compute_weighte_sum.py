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
INCREASE_DISTANCE = 10
def path_feasible(path, graph, init_soc, install_dic):

    current_range_soc = init_soc
    for roadSeg in path:
        INSTALL = install_dic[roadSeg]
        velocity = graph.node[roadSeg]['speed_urban']*DECREASE_SPEED #this is modified such that if we install every then final_soc = 1 if start_soc = 1
        distance = graph.node[roadSeg]['length']*0.000621371*INCREASE_DISTANCE
        current_range_soc = write_data.nextSOC_real_data(current_range_soc, distance, 1, velocity, INSTALL)
        #print current_range_soc

    return current_range_soc
   




def modify_graph_weights(graph):
  
  for edge in graph.edges():
    u, v = edge
    distance = graph[u][v]['weight']*0.000621371*INCREASE_DISTANCE
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


    
def centrality_solution(graph, budget_in_meters, centrality):
    road_seg = []
    
    if centrality  == 'betweenness':
        print 'computing btn centrality'
        cen_measure = nx.betweenness_centrality(graph, weight='time')
        print 'computing btn centrality... complete'
    elif centrality == 'eigen_vector':
        print 'computing eigen_vector eigen_vector'
        cen_measure = nx.eigenvector_centrality_numpy(graph, weight='time')
        print 'computing eigen_vector centrality... complete'

    else:
        raise nx.NetworkXError('centrality_solution() ','centrality must be either betweenness or eigen_vector')

    
    sorted_road_seg = sorted([(cen_measure[key], key) for key in cen_measure], reverse=True)
    
    budget_used = 0
    
    for val, road in sorted_road_seg:

        if budget_used + float(graph.node[road]['length']) <= budget_in_meters:
            road_seg.append(road)
            budget_used += float(graph.node[road]['length'])
        if budget_used >= budget_in_meters:
            break
            
    if centrality  == 'betweenness':        
      cen_file = open("30_greenville_btn_seg_install.txt", "w")
    else:
      cen_file = open("30_greenvile_eig_vector_seg_install.txt", "w")
    for i in road_seg:
        cen_file.write(str(i) + '\n')
    cen_file.close()
    return road_seg


    
if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="compute weighted sum of 100k random routes for 2 solutions")
  parser.add_argument("--model_solution", metavar="myFile", default=" ", type=str, help="model solution")
  parser.add_argument("--btn_solution", metavar="myFile", default=" ", type=str, help="btn solution")
  parser.add_argument("--palmetto_job", type=int, default=0,help='is palmetto job?')
  args = parser.parse_args()
  model_file = open(getattr(args, 'model_solution'), 'r')
  btn_file = open(getattr(args, 'btn_solution'), 'r')
  palmetto_job = getattr(args, 'palmetto_job')
                        
  graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/lower_manhattan1_5.graphml")
  #graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/greenville1_5.graphml")
  modify_graph_weights(graph)
  model_location = {}
  btn_location = {}
  no_install = {}
  all_location = {}
  total_distance = 0
  for node in graph.nodes():
    model_location[node] = False
    btn_location[node] = False
    no_install[node] = False
    all_location[node] = True
    total_distance += float(graph.node[node]['length'])
  
  model_distance = 0
  for line in model_file:
    model_location[str(int(line))] = True
    model_distance += float(graph.node[str(int(line))]['length'])
  btn_distance = 0
  for line in btn_file:
    btn_location[str(int(line))] = True
    btn_distance += float(graph.node[str(int(line))]['length'])
    
  nnodes = nx.number_of_nodes(graph)
  tuple_indx = range(nnodes*nnodes)
  random.shuffle(tuple_indx)
  route_indx = 0
  init_soc = 1
  
  weighted_no_install = 0
  weighted_model_install = 0
  weighted_btn_install = 0
  weighted_all_install = 0
  if not palmetto_job:
    count = 0
    #get weight of 100 random routes
    print "model budget:", model_distance/total_distance
    print "btn budget:", btn_distance/total_distance
    
    while count < 10:
    
      route_no = tuple_indx[route_indx]
      col = route_no%nnodes
      row = (route_no - col)/nnodes
      row = int(row) 
      start = str(row + 1) #indexing of nodes is from 1 to n
      end = str(col + 1)
      route_indx += 1
      if start != end and nx.has_path(graph, start, end):
        shortest_path = nx.shortest_path(graph, source=start, target=end, weight='time') 
        no_install_soc = path_feasible(shortest_path, graph, init_soc, no_install)
        if no_install_soc < 0.8:
          
          count += 1
          model_install_soc = path_feasible(shortest_path, graph, init_soc, model_location)
          btn_install_soc = path_feasible(shortest_path, graph, init_soc, btn_location)
          all_install_soc = path_feasible(shortest_path, graph, init_soc, all_location)
          weighted_no_install += no_install_soc
          weighted_model_install += model_install_soc
          weighted_btn_install += btn_install_soc
          weighted_all_install += all_install_soc
          print no_install_soc,  model_install_soc, btn_install_soc
          #print (weighted_no_install, weighted_model_install, weighted_btn_install, 
         #   weighted_all_install), (weighted_no_install/count, 
          #  weighted_model_install/count, weighted_btn_install/count, weighted_all_install/count)
          
  
 
