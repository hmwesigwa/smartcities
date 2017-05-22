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

def distance_of_path(graph, path):
  distance = 0
  
  for node in path:
    distance += float(graph.node[node]['length'])
    
  return distance
    
  
if __name__ == "__main__":
    #graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/lower_manhattan1_5.graphml")
    #graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/greenville1_5.graphml")
    graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/manhattan_neigborhood.graphml")
    cen_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/data/manhattan_neigh_betweenness.centrality")
    #model_installfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/exp_install.txt")
    #model_installfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/exp_10percent_85_58percentgap.txt")
    #model_installfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/rand_start_soc.txt")
    #model_installfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/random_start_soc_950_seg_install.txt")
    #model_installfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/exp_install_20percent.txt")
    #model_installfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/exp_install_20percent_6percentgap.txt")
    model_installfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/copy_random_start_soc_1150_25percent_gap_seg_install.txt")
    
    model_install = {}
    #myfile = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/20_percent_infeasible_routes.txt", "w")
    btn_cen = {}
    
    node = 1
    for line in cen_file:
      btn_cen[str(node)] = float(line)
      node += 1
      
    sorted_cen = sorted([(btn_cen[node], node ) for node in graph.nodes()], reverse=True)
    budget = 0.2
    total_distance = 0
    btn_install_dic = {}
    no_install_dic = {}
    for node in graph.nodes():  
      btn_install_dic[node] = False
      model_install[node] = False
      no_install_dic[node] = False
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
        btn_install_dic[node] = True
        distance_used += distance
      if model_install[node] == False and model_distance + distance   <= budget*total_distance :
        model_distance += distance
        model_install[node] = True
        model_distance += distance
    print "Budget: %f \t Model: %f \t Btn: %f" %(budget, model_distance/total_distance, distance_used/total_distance) 
    nnodes = nx.number_of_nodes(graph)
    tuple_indx = range(nnodes*nnodes)
    print 'before shuffle'
    random.shuffle(tuple_indx)
    print 'after shuffle'
    route_indx = 0

    btn_hist = []
    model_hist = []
    no_hist = []
    total_routes = nnodes**2-1
    pathNumber = 0
    #while pathNumber < 30000:
    all_distance = []
    while route_indx < nnodes*nnodes -1:
      route_no = tuple_indx[route_indx]
      col = route_no%nnodes
      row = (route_no - col)/nnodes
      row = int(row) 
      route_indx += 1
      if route_indx%10000 == 0:
        print route_indx
        
        
        
      #if route_indx >= total_routes:
      #  print "ERROR, num_routes too large"
      #  break
      start = str(row + 1) #indexing of nodes is from 1 to n
      end = str(col + 1)

      if nx.has_path(graph, start, end) and start != end:
        shortest_path = nx.shortest_path(graph, source=start, target=end, weight='time') 
        distance = distance_of_path(graph, shortest_path)
        avg_distance = 2861.51384791
        std_distance = 1429.38854176
        if distance > avg_distance + 2*std_distance:
          all_distance.append(distance)
          start = shortest_path[0]
          end = shortest_path[-1]
          init_soc = random.uniform(0.4,1)
          no_soc = path_feasible(shortest_path, graph, init_soc, no_install_dic)
          btn_soc = path_feasible(shortest_path, graph, init_soc, btn_install_dic)
          model_soc = path_feasible(shortest_path, graph, init_soc, model_install)

          #if no_soc < 0.8:
          no_hist.append(no_soc)
          #  myfile.write(start + " " + end + " " + str(model_soc) + " \n")
            
          btn_hist.append(btn_soc)
          model_hist.append(model_soc)
          
        pathNumber +=1 
    
    print 'average distance of path', np.mean(all_distance)
    print 'standar deviation of paths', np.std(all_distance)
    print 'longest path', max(all_distance)
    print "drawing hist"
    print "model", min(model_hist), max(model_hist), sum(np.array(model_hist) < 0.85)
    print "btn", min(btn_hist), max(btn_hist), sum(np.array(btn_hist) < 0.85)
    print "average soc, no install:" , np.mean(no_hist)
    print "average soc,model", np.mean(np.array(model_hist) )
    print "average soc,btn", np.mean(np.array(btn_hist) )
    print "number of routes considered", len(no_hist)
    #print "no install", len(no_hist)
    #myfile.close()
    bins=np.histogram(np.hstack((btn_hist,model_hist)), bins=50)[1] #get the bin edges
    plt.hist(no_hist, bins, histtype='bar',alpha=1, normed=0, color='g', label="0%")
    plt.hist(btn_hist, bins, histtype='bar',alpha=1, normed=0, color='r', label="20% betweenness")
    plt.hist(model_hist, bins, histtype='bar', alpha=0.8,normed=0, color='b', label="20% Model")
    #plt.axvline(x=0.85, color='g', linestyle='dashed')
    
    






    plt.legend(loc='upper right')
    plt.show()  
