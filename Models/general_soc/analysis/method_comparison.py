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
def path_feasible(path, graph, init_soc, install_dic):

    current_range_soc = init_soc
    for roadSeg in path:
        INSTALL = install_dic[roadSeg]
        #INSTALL = False
        velocity = graph.node[roadSeg]['speed_urban']*DECREASE_SPEED #this is modified such that if we install every then final_soc = 1 if start_soc = 1
        distance = graph.node[roadSeg]['length']*0.00621371
       
        current_range_soc = write_data.nextSOC_real_data(current_range_soc, distance, 1, velocity, INSTALL)
        #print current_range_soc

    return current_range_soc
   




def modify_graph_weights(graph):
  
  for edge in graph.edges():
    u, v = edge
    distance = graph[u][v]['weight']*0.00621371
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


'''    
def random_solution_fixed_routes(graph, budget, route_filename):

    return road_seg
'''
    
if __name__ == "__main__":
    #graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/lower_manhattan1_5.graphml")
    graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/greenville1_5.graphml")
    start = sys.argv[1]
    #seg_installFile0 = open("0seg_install.txt", "r")
    
    seg_installFile1 = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/exp_seg_install.txt", "r")
    seg_installFile2 = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/30_greenville_btn_seg_install.txt", "r")


    modify_graph_weights(graph)
    
    WRITE_ROAD_SEG_FOR_CENTRALITY = False
    if WRITE_ROAD_SEG_FOR_CENTRALITY:
      #total_distance = 683531.637168
      #1% budget = 1606299.347344
      #2% budget = 3212598.694688
      #4% budget = 6425197.389375
      #8% budget = 12850394.778750
      #16% budget = 25700789.557501


     
      #total_distance = 683531.637168 #new york
      total_distance = 1174281.36952 #greenville
      budget_in_meters = total_distance*0.3 # 1%

      print 'here'
      seg_install1 =  centrality_solution(graph, budget_in_meters, 'betweenness')
      seg_install2 =  centrality_solution(graph, budget_in_meters, 'eigen_vector')
      
      print len(seg_install1), nx.number_of_nodes(graph)
      miles_used = 0
      for i in seg_install1:
          road_len = graph.node[i]['length']
          miles_used += float(road_len)

      print miles_used/total_distance
      
    else:
      
      
      seg_install0 = []
      install_dic0 = {}
      
      seg_install1 = []
      install_dic1 = {}

      seg_install2 = []
      install_dic2 = {}
      
      #seg_install4 = []
      #install_dic4 = {}
      
      #seg_install8 = []
      #install_dic8 = {}

      #seg_install9 = []
      #install_dic9 = {}
          
      seg_installALL = []
      install_dicALL = {}
      nodes = graph.nodes()
      random.shuffle(nodes)
      for node in nodes:
          install_dic0[node] = False
          install_dic1[node] = False
          install_dic2[node] = False
          #install_dic4[node] = False
          #install_dic8[node] = False
          #install_dic9[node] = False
          #install_dicALL[node] = True
      
      

      for line in seg_installFile1:
          line = line.strip("\n")
          seg_install1.append(line)
          install_dic1[str(line)] = True

      for line in seg_installFile2:
          line = line.strip("\n")
          seg_install2.append(line)
          install_dic2[str(line)] = True
          
      #for line in seg_installFile4:
      #    line = line.strip("\n")
      #    seg_install4.append(line)
      #    install_dic4[str(line)] = True
          
      #for line in seg_installFile8:
      #    line = line.strip("\n")
      #    seg_install8.append(line)
      #    install_dic8[str(line)] = True   
          
      #for line in seg_installFile9:
      #    line = line.strip("\n")
      #    seg_install9.append(line)
      #    install_dic9[str(line)] = True  
          
      seg_installFile1.close()
      seg_installFile2.close()
      #seg_installFile4.close()
      #seg_installFile8.close()
      #seg_installFile9.close()
      init_soc = 1
    
      acc0  = []
      acc1  = []
      acc2  = []
      #acc3  = []
      #acc4  = []
      #acc5  = []
      count = 0
      for sink in graph.nodes():
          if start != sink:
              if nx.has_path(graph, start, sink):
                  
                  path = nx.shortest_path(graph, source=start, target=sink, weight='time')
                  if len(path) > 5:
                    count += 1
                    if count > 100:
                      break
                      
                    final_soc0 = path_feasible(path, graph, init_soc, install_dic0)
                    final_soc1 = path_feasible(path, graph, init_soc, install_dic1)
                    final_soc2 = path_feasible(path, graph, init_soc, install_dic2)
                   # final_soc4 = path_feasible(path, graph, init_soc, install_dic4)
                    #final_soc8 = path_feasible(path, graph, init_soc, install_dic8)
                    #final_soc9 = path_feasible(path, graph, init_soc, install_dic9)
                    #final_socALL = path_feasible(path, graph, init_soc, install_dicALL)
                    #print final_soc0, final_soc1, final_soc2, final_soc4,final_soc8
                    acc0.append(final_soc0)
                    acc1.append(final_soc1)
                    acc2.append(final_soc2)
                    #acc3.append(final_soc4)
                    #acc4.append(final_soc8)
                    #acc5.append(final_socALL)


      threshold = [i/50 for i in range(51)]
      count0 = [0 for i in range(51) ]
      count1 = [0 for i in range(51)]
      count2 = [0 for i in range(51)]
      #count3 = [0 for i in range(51)]
      #count4 = [0 for i in range(51)]
      #count5 = [0 for i in range(51)]

      for k in range(len(acc0)):
          for i, th in enumerate(threshold):
              if acc0[k] <= th:
                  count0[i] += 1
              if acc1[k] <= th:
                  count1[i] += 1 
              if acc2[k] <= th:
                  count2[i] += 1
              #if acc3[k] <= th:
              #    count3[i] += 1
              #if acc4[k] <= th:
              #    count4[i] += 1      
              #if acc5[k] <= th:
              #    count5[i] += 1      
                         
      for i in count0:
          print i,
      print '\n'
      for i in  count1:
          print i,
      print '\n'
      for i in  count2:
          print i,
      print '\n'
      #for i in  count3:
      #    print i,
      #print '\n'
      #for i in  count4:
      #    print i,
      #print '\n'
      #for i in  count5:
      #    print i,
      #print '\n'       


#for i in range(51):
#    print count0[i], count1[i], count2[i], count5[i], threshold[i]
'''

#plt.hist(acc0, bins=100, histtype='step', normed=0, color='g', label='0%')
plt.hist(acc1, bins=20, histtype='step', normed=0, color='b', label='1%')
#plt.hist(acc2, bins=100, histtype='step', normed=0, color='grey', label='2%')
#plt.hist(acc3, bins=100, histtype='step', normed=0, color='orange', label='4%')
plt.hist(acc4, bins=20, histtype='step', normed=0, color='r', label='8%')
      
#plt.plot([i/50 for i in range(51)], acc0,  label='0%')  
#plt.plot([i/50 for i in range(51)], acc1,  label='1% model') 
#plt.plot([i/50 for i in range(51)], acc2,  label='1% betweenness') 
#plt.plot([i/50 for i in range(51)], acc3,  label='1% random') 
#plt.plot([i/50 for i in range(51)], acc4,  label='1% eigen vector')   

plt.legend(loc='upper left')

plt.title("SOC Distribution")
plt.xlabel("SOC")
plt.ylabel("No. Routes")
ax = plt.axes()
#plt.show()

fig = plt.figure()
plt.show()
  
   ''' 
  
 
