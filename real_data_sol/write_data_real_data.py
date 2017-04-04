#!/usr/bin/python
from __future__ import division
import write_data
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
    

  
#update data and data_var for a given route
def path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers):
  
  #soure arcs
  next_node = roadSeg_to_node(path[0], nLayers)
  #Assume we start when fully charged
  #if not fully charged, we need to change next_node i.e (next_node + i)
  #data['arcs'] = "".join([data['arcs'], " (", str(pathNumber), ",source,", str(next_node), ")\n" ]) 
  #data['weight'] = "".join([data['weight'], " ", str(pathNumber), " source ", str(next_node), " 0\n" ]) 
  for i in range(nLayers):
    data_var['nodes'].add(next_node + i)
    data['arcs'] = "".join([data['arcs'], " (", str(pathNumber), ",source,", str(next_node + i), ")\n" ]) 
    data['weight'] = "".join([data['weight'], " ", str(pathNumber), " source ", str(next_node + i), " 0\n" ]) 
  
  #destination arcs
  node = roadSeg_to_node(path[-1], nLayers)
  data_var['roadSegs'].add(path[-1])
  for i in range(nLayers):
    data_var['nodes'].add(node + i)
    data['arcs'] = "".join([data['arcs'], " (", str(pathNumber), ",", str(node + i), ", destination) \n" ]) 
    data['weight'] = "".join([data['weight'], " ", str(pathNumber), " ", str(node + i), " destination 0 \n" ]) 
    soc = node_to_soc(node + i, nLayers)
    data['boundary_node_weights'] = "".join([data['boundary_node_weights'], " ",str(pathNumber), " ", str(node + i),  " ", str(soc),"\n" ])
    data['boundary_nodes'] = "".join([data['boundary_nodes'], " (",str(pathNumber), ",", str(node + i),  ")\n" ])
    
  for i, roadSeg in enumerate(path[:-1]):
    len_path = len(path)
    data_var['roadSegs'].add(roadSeg)
    next_roadSeg = path[i+1]
    start_node = roadSeg_to_node(roadSeg, nLayers)
    next_start_node = roadSeg_to_node(next_roadSeg, nLayers)
    for j in range(nLayers):
      current_node = start_node + j
      data_var['nodes'].add(current_node)
      current_soc = node_to_soc(current_node, nLayers)
      if current_soc < 1.0e-10:
        #boundary node
        data['arcs'] = "".join([data['arcs'], " (",str(pathNumber), ",", str(current_node), ",",  " destination)\n" ])
        data['weight'] = "".join([data['weight'], " ",str(pathNumber), " ", str(current_node),  " destination 0\n" ])
        data['boundary_node_weights'] = "".join([data['boundary_node_weights'], " ",str(pathNumber), " ", str(current_node),  " ", str(-(len_path -1 -i)/(len_path -1)),"\n" ])
        data['boundary_nodes'] = "".join([data['boundary_nodes'], " (",str(pathNumber), ",", str(current_node),  ")\n" ])
      else:
        #INSTALL = True
        INSTALL = True
        velocity = graph.node[str(roadSeg - 2)]['speed_urban']
        distance = graph.node[str(roadSeg - 2)]['length']*0.000621371
        next_soc = write_data.nextSOC_real_data(current_soc, distance, 1, velocity, INSTALL)
        #next_soc = nextSOC(current_soc, INSTALL, nLayers)
        next_node_posn = position_in_layer(next_soc, nLayers)
        next_node = next_start_node + next_node_posn
        data['arcs'] = "".join([data['arcs'], " (",str(pathNumber), ",", str(current_node), ",", str(next_node), ") \n" ])
        data['weight'] = "".join([data['weight'], " ",str(pathNumber), " ", str(current_node), " ", str(next_node), " 1\n" ])

        #INSTALL = False
        INSTALL = False
        velocity = graph.node[str(roadSeg - 2)]['speed_urban']
        distance = graph.node[str(roadSeg - 2)]['length']*0.000621371
        next_soc = write_data.nextSOC_real_data(current_soc, distance, 1, velocity, INSTALL)
        #next_soc = nextSOC(current_soc, INSTALL, nLayers)
        next_node_posn = position_in_layer(next_soc, nLayers)
        next_node = next_start_node + next_node_posn
        data['arcs'] = "".join([data['arcs'], " (",str(pathNumber), ",", str(current_node), ",", str(next_node), ")\n" ])
        data['weight'] = "".join([data['weight'], " ",str(pathNumber), " ", str(current_node), " ", str(next_node), " 0\n" ])
        
        #Assume vehicle starts fully charged thus only one layer for first roadSeg
        if roadSeg == path[0]:
          break

  return data, data_var
    
#determine soc for a given node in layered graph
def node_to_soc(node, nLayers):
  posn = (node-1)%nLayers 
  soc =  1-  posn/(nLayers-1)
  
  return soc
  
  


#determine ith position from the top of layered graph in a given s
#zero based index
def position_in_layer(soc, nLayers):
  posn = (nLayers-1)*(1 - soc) 
  posn = round(posn)
  return int(posn)
  
#determine top most node of layered graph for a given roadSeg
def roadSeg_to_node(roadSeg, nLayers):
  
  node = (roadSeg-1)*nLayers + 1
  
  return node

#determine corresponding roadSeg for a given node
def node_to_roadSeg(node, nLayers):

  if node == 'source' or node == 'destination':
    return node
  else:
    roadSeg = math.ceil(node/nLayers)
  return int(roadSeg)
 
 
 
#initialize data and data_var
def init_dataFile(nLayers, budget, nRoutes, largeNumber):
  
  data = {}
  data_var = {}
  data['nodes'] =       'set nodes := source destination'
  data['arcs'] =        'set arcs :=\n'
  data['roadSegs'] =    'set roadSegs :='
  data['route_no'] =      'set route_no :='
  data['nRoutes'] =     'param nRoutes :='
  data['nLayers'] =     'param nLayers :='
  data['largeNumber'] = 'param largeNumber :=' 
  data['nRoadSegs'] =   'param nRoadSegs :='
  data['budget'] =      'param budget :='
  data['costInstall'] = 'param costInstall :=\n'
  data['weight'] =      'param weight :=\n'
  data['boundary_node_weights'] = 'param boundary_node_weights :=\n'
  data['boundary_nodes'] =        'set boundary_nodes :=\n'
  data_var['nodes'] = set()
  data_var['roadSegs'] = set()
  data_var['nRoutes'] = nRoutes
  data_var['nLayers'] =  nLayers
  data_var['largeNumber'] = largeNumber
  data_var['budget'] =   budget
  
  return data, data_var
 
def write_data_to_file(filename, data, data_var):

  myFile = open(filename, 'w')
  #nodes
  for i in data_var['nodes']:
    data['nodes'] += " "
    data['nodes'] += str(i)
  data['nodes'] += ';\n'
  
  #arcs
  if data['arcs'][-1] == '\n':
    data['arcs'] = data['arcs'][:-1] +  ';\n'
  else:
    data['arcs'] += ';\n'
    
  #roadSegs
  for roadSeg in data_var['roadSegs']:
    data['roadSegs'] += " "
    data['roadSegs'] += str(roadSeg)
  data['roadSegs'] += ';\n'
  
  #routes
  for i in range(1, data_var['nRoutes'] +1):
    data['route_no'] += " "
    data['route_no'] += str(i)
  data['route_no'] += ';\n'
  
  #nRoutes
  data['nRoutes'] += str(data_var['nRoutes'])
  data['nRoutes'] += ';\n'
  
  #nLayers
  data['nLayers'] += ' '
  data['nLayers'] += str(data_var['nLayers'])
  data['nLayers'] += ';\n'
  
  #largeNumber
  data['largeNumber'] += ' '
  data['largeNumber'] += str(data_var['largeNumber'])
  data['largeNumber'] += ';\n'
  
  #nRoadSegs
  data['nRoadSegs'] += ' '
  data['nRoadSegs'] += str(len(data_var['roadSegs']))
  data['nRoadSegs'] += ';\n'
  
  #budget
  data['budget'] += ' '
  data['budget'] +=  str(data_var['budget'])
  data['budget'] += ';\n'
  
  #costInstall
  for roadSeg in data_var['roadSegs']:
    data['costInstall'] += str(roadSeg) + " 1\n"
  if data['costInstall'][-1] == '\n':
    data['costInstall'] = data['costInstall'][:-1] +  ';\n'
  else:
    data['costInstall'] += ';\n'
  
  #weight
  if data['weight'][-1] == '\n':
    data['weight'] = data['weight'][:-1] +  ';\n'
  else:
    data['weight'] += ';\n'
  
  #boundary_node_weights
  if data['boundary_node_weights'][-1] == '\n':
    data['boundary_node_weights'] = data['boundary_node_weights'][:-1] +  ';\n'
  else:
    data['boundary_node_weights'] += ';\n'
  #boundary_nodes
  if data['boundary_nodes'][-1] == '\n':
    data['boundary_nodes'] = data['boundary_nodes'][:-1] +  ';\n'
  else:
    data['boundary_nodes'] += ';\n' 
  for val in data:
    myFile.write(data[val])

  myFile.close()
  
def write_route_to_file(path,write):
  myFile = open('routes.txt', write)
  
  out = [str(i) for i in path]
  out = " ".join(out)
  out += "\n"
  myFile.write(out)
  myFile.close()
 
def row(num, n):
  return int(math.ceil(num/n))

def col(num, n):
  return num - (row(num,n) -1)*n
  
def random_routes(graph):
  nodes = graph.nodes()
  nnodes = nx.number_of_nodes(graph)
  all_route_no = range(1,nnodes*nnodes + 1) 
  random.shuffle(all_route_no)
  out = []
  
  for num in all_route_no:
    r = row(num, nnodes)
    c = col(num, nnodes)
    
    out.append((nodes[r-1],nodes[c-1]))
  
  #out = out[:num_routes]
  return out
  
def remove_subroute(path, non_subroute, nnodes, nodes_list, node_indx):
  #node_indx['1'] = 0 node 1 is at inx 0
  if len(path) ==2:
    start = path[0]
    end = path[-1]
    c = node_indx[start] + 1
    r = node_indx[end] + 1
    route_no = (r-1)*nnodes + c 
    #print (start,end), route_no , nodes_list[c-1], nodes_list[r-1]
    non_subroute[route_no] = False
  else:
    for i, start in enumerate(path[:-1]):
      for end in path[i :]:
        if (start, end) != (path[0], path[-1]):
          #r,c are 0 based inde
          c = node_indx[start] + 1
          r = node_indx[end] + 1
          route_no = (r-1)*nnodes + c 
          #print (start,end), route_no , nodes_list[c-1], nodes_list[r-1]
          non_subroute[route_no] = False
        
  return non_subroute
    
if __name__ == "__main__":
  soc_threshold = 0.9
  #roadSegGraph = nx.read_graphml("roadSegGraph_968.graphml")
  #roadSegGraph = nx.read_graphml("roadSegGraph_110.graphml")
  #roadSegGraph = nx.read_graphml("roadSegGraph.graphml")
  roadSegGraph = nx.read_graphml("graph_data/lower_manhattan1_5.graphml")
  
  for edge in roadSegGraph.edges():
    u, v = edge
    distance = roadSegGraph[u][v]['weight']*0.000621371
    location = roadSegGraph.node[u]['location']
    speed = roadSegGraph.node[u]['speed_urban']*0.01
    time = distance/speed*3600
    roadSegGraph[u][v]['time'] = time
    next_soc_1 = write_data.nextSOC_real_data(0.5, distance, 1, speed, 1)
    next_soc_0 = write_data.nextSOC_real_data(0.5, distance, 1, speed, 0)
    print next_soc_0, next_soc_1, distance, speed, location
    #print distance, speed, 'time', time, roadSegGraph.node[u]['location'], roadSegGraph.node[u]['class']
  nLayers = 11
  budget = 11
  largeNumber = 10**7
  filename = 'smallbudget.dat'

  #number of routes
  num_routes = 1
  
  
  
  pathNumber = 1
  data, data_var = init_dataFile(nLayers, budget, num_routes, largeNumber)
  
  #rand_routes = random_routes(roadSegGraph)
  
  i = '1'
  j = '1000'
  shortest_path = nx.shortest_path(roadSegGraph, source=i, target=j, weight='time')
  path  = [int(v) + 2 for v in shortest_path] #add 2 to make node index start at 2
  path.append(1) #1 represents the destination layered roadseg
  if pathNumber > 1:
    write = 'a'
  else:
    write = 'w'
  write_route_to_file(path, write)
  data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)
  write_data_to_file(filename, data, data_var) 
  '''
  non_subroute = {}
  nnodes = nx.number_of_nodes(roadSegGraph)
  node_list = roadSegGraph.nodes()
  node_indx = {}
  count = 0
  for i in node_list:
    node_indx[i] = count
    count += 1

  for u in range(1,nnodes*nnodes + 1):
    non_subroute[u] = True

  for i, j in rand_routes:
    if i !=j :
      shortest_path = nx.shortest_path(roadSegGraph, source=i, target=j, weight='time')
      #non_subroute = remove_subroute(shortest_path, non_subroute, nnodes, node_list, node_indx)
      #if 0 < -3:
      if len(shortest_path) > 3:
        path  = [int(v) + 2 for v in shortest_path] #add 2 to make node index start at 2
        path.append(1) #1 represents the destination layered roadseg
        if pathNumber > 1:
          write = 'a'
        else:
          write = 'w'
        write_route_to_file(path, write)
        data, data_var = path_to_layeredGraph(path, pathNumber, data, data_var, nLayers)

        pathNumber +=1
        if pathNumber > num_routes:
          break
  print pathNumber -1, "routes"
  if pathNumber < num_routes:
    print "ERROR: less routes than desired"
    os.system("rm example_all_routes.dat")
  else:
    write_data_to_file(filename, data, data_var) 
      
  print 'number of roadSegs:', len(data_var['roadSegs']) -1
  '''
 
