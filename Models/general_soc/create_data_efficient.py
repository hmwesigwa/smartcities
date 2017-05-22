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
import copy

INCREASE_LENGTH = 1
EPSILON_LENGTH = 1
DECREASE_SPEED = 0.1

#functions to change soc resolution
def standard_soc_to_range_soc(standard_soc, soc_lower_bound):
  diff = 1 - soc_lower_bound
  soc = standard_soc*diff + soc_lower_bound
  
  return soc
#@profile
def range_soc_to_standard_soc(range_soc, nLayers, soc_lower_bound):

  diff = 1.0 - soc_lower_bound
  real_soc = (range_soc - soc_lower_bound)/diff
  step = 1.0/(nLayers - 1)

  n = (real_soc - soc_lower_bound)/step
  n = round(n)
  standard_soc = soc_lower_bound + n*step
  if standard_soc <= 1.0e-10:
    return 0
  elif standard_soc >=1:
    return 1
  else:
    return standard_soc



  
#update data and data_var for a given route
#@profile
def path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers):
  
  #soure arcs
  next_node = roadSeg_to_node(path[0], nLayers)
  #Assume we start when fully charged
  #if not fully charged, we need to change next_node i.e (next_node + i)
  #data['arcs'] = "".join([data['arcs'], " (", str(pathNumber), ",source,", str(next_node), ")\n" ]) 
  #data['weight'] = "".join([data['weight'], " ", str(pathNumber), " source ", str(next_node), " 0\n" ]) 
  for i in range(nLayers):
    data_var['nodes'].add(next_node + i)
    #data['arcs'] = "".join([data['arcs'], " (", str(pathNumber), ",source,", str(next_node + i), ")\n" ]) 
    #data['weight'] = "".join([data['weight'], " ", str(pathNumber), " source ", str(next_node + i), " 0\n" ]) 
    
    data['arcs'].append("".join([" (", str(pathNumber), ",source,", str(next_node + i), ")\n" ]) )
    data['weight'].append( "".join([" ", str(pathNumber), " source ", str(next_node + i), " 0\n" ]))

  #destination arcs
  node = roadSeg_to_node(path[-1], nLayers)
  data_var['roadSegs'].add(path[-1])
  for i in range(nLayers):
    data_var['nodes'].add(node + i)
    data['arcs'].append("".join([ " (", str(pathNumber), ",", str(node + i), ", destination) \n" ]) )
    data['weight'].append("".join([ " ", str(pathNumber), " ", str(node + i), " destination 0 \n" ]) )
    standard_soc = node_to_soc(node + i, nLayers)
    data['boundary_node_weights'].append("".join([" ",str(pathNumber), " ", str(node + i),  " ", str(standard_soc),"\n" ]))
    data['boundary_nodes'].append("".join([ " (",str(pathNumber), ",", str(node + i),  ")\n" ]))
    
  for i, roadSeg in enumerate(path[:-1]):
    len_path = len(path)
    data_var['roadSegs'].add(roadSeg)
    next_roadSeg = path[i+1]
    start_node = roadSeg_to_node(roadSeg, nLayers)
    next_start_node = roadSeg_to_node(next_roadSeg, nLayers)
    for j in range(nLayers):
      current_node = start_node + j
      data_var['nodes'].add(current_node)
      current_standard_soc = node_to_soc(current_node, nLayers)
      if current_standard_soc < 1.0e-10:
        #boundary node
        data['arcs'].append("".join([ " (",str(pathNumber), ",", str(current_node), ",",  " destination)\n" ]))
        data['weight'].append("".join([" ",str(pathNumber), " ", str(current_node),  " destination 0\n" ]))
        data['boundary_node_weights'].append("".join([ " ",str(pathNumber), " ", str(current_node),  " ", str(-(len_path -1 -i)/(len_path -1)),"\n" ]))
        data['boundary_nodes'].append("".join([ " (",str(pathNumber), ",", str(current_node),  ")\n" ]))
      else:
        #INSTALL = True
        INSTALL = True
        velocity = graph.node[str(roadSeg - 2)]['speed_urban']*DECREASE_SPEED
        distance = graph.node[str(roadSeg - 2)]['length']*0.00621371*INCREASE_LENGTH + EPSILON_LENGTH
        current_range_soc = standard_soc_to_range_soc(current_standard_soc, soc_lower_bound)
        next_range_soc = write_data.nextSOC_real_data(current_range_soc, distance, 1, velocity, INSTALL)
        next_standard_soc = range_soc_to_standard_soc(next_range_soc, nLayers, soc_lower_bound)     
        next_node_posn = position_in_layer(next_standard_soc, nLayers)      
        next_node = next_start_node + next_node_posn
        data['arcs'].append("".join([" (",str(pathNumber), ",", str(current_node), ",", str(next_node), ") \n" ]))
        data['weight'].append("".join([ " ",str(pathNumber), " ", str(current_node), " ", str(next_node), " 1\n" ]))

        #INSTALL = False
        INSTALL = False
        velocity = graph.node[str(roadSeg - 2)]['speed_urban']*DECREASE_SPEED
        distance = graph.node[str(roadSeg - 2)]['length']*0.00621371*INCREASE_LENGTH + EPSILON_LENGTH
        current_range_soc = standard_soc_to_range_soc(current_standard_soc, soc_lower_bound)
        next_range_soc = write_data.nextSOC_real_data(current_range_soc, distance, 1, velocity, INSTALL)
        next_standard_soc = range_soc_to_standard_soc(next_range_soc, nLayers, soc_lower_bound)     
        next_node_posn = position_in_layer(next_standard_soc, nLayers)
        next_node = next_start_node + next_node_posn
        #print next_range_soc, next_standard_soc, next_node_posn, next_node
        data['arcs'].append("".join([ " (",str(pathNumber), ",", str(current_node), ",", str(next_node), ")\n" ]))
        data['weight'].append("".join([" ",str(pathNumber), " ", str(current_node), " ", str(next_node), " 0\n" ]))
        #print current_standard_soc, current_range_soc, next_range_soc
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
def init_dataFile(nLayers, budget, nRoutes, largeNumber, soc_lower_bound):
  
  data = {}
  data_var = {}
  '''
  data['nodes'] =       'set nodes := source destination'
  data['arcs'] =        'set arcs :=\n'
  data['roadSegs'] =    'set roadSegs :='
  data['route_no'] =      'set route_no :='
  data['nRoutes'] =     'param nRoutes :='
  data['nLayers'] =     'param nLayers :='
  data['largeNumber'] = 'param largeNumber :=' 
  data['soc_lower_bound']= 'param soc_lower_bound :='
  data['nRoadSegs'] =   'param nRoadSegs :='
  data['budget'] =      'param budget :='
  data['costInstall'] = 'param costInstall :=\n'
  data['weight'] =      'param weight :=\n'
  data['boundary_node_weights'] = 'param boundary_node_weights :=\n'
  data['boundary_nodes'] =        'set boundary_nodes :=\n'
  '''
  data['nodes'] =  ['set nodes := source destination']
  data['arcs'] =    ['set arcs :=\n']
  data['roadSegs'] =  ['set roadSegs :=']
  data['route_no'] =  ['set route_no :=']
  data['nRoutes'] =    ['param nRoutes :=']
  data['nLayers'] =     ['param nLayers :=']
  data['largeNumber'] = ['param largeNumber :=' ]
  data['soc_lower_bound']= ['param soc_lower_bound :=']
  data['nRoadSegs'] =   ['param nRoadSegs :=']
  data['budget'] =      ['param budget :=']
  data['costInstall'] = ['param costInstall :=\n']
  data['weight'] =      ['param weight :=\n']
  data['boundary_node_weights'] = ['param boundary_node_weights :=\n']
  data['boundary_nodes'] =       [ 'set boundary_nodes :=\n']


  
  data_var['nodes'] = set()
  data_var['roadSegs'] = set()
  data_var['nRoutes'] = nRoutes
  data_var['nLayers'] =  nLayers
  data_var['largeNumber'] = largeNumber
  data_var['budget'] =   budget
  data_var['soc_lower_bound'] = soc_lower_bound
  
  return data, data_var
 
def write_data_to_file(filename, graph, data, data_var):

  myFile = open(filename, 'w')
  #nodes
  for i in data_var['nodes']:
    data['nodes'].append(" ")
    data['nodes'].append(str(i))
  data['nodes'].append(';\n')
  
  #arcs
  if data['arcs'][-1] == '\n':
    data['arcs'] = ';\n'
  else:
    data['arcs'].append(';\n')
    
  #roadSegs
  for roadSeg in data_var['roadSegs']:
    data['roadSegs'].append(" ")
    data['roadSegs'].append(str(roadSeg))
  data['roadSegs'].append(';\n')
  
  #routes
  for i in range(1, data_var['nRoutes'] +1):
    data['route_no'].append(" ")
    data['route_no'].append(str(i))
  data['route_no'].append(';\n')
  
  #nRoutes
  data['nRoutes'].append(str(data_var['nRoutes']))
  data['nRoutes'].append(';\n')
  
  #nLayers
  data['nLayers'].append(' ')
  data['nLayers'].append(str(data_var['nLayers']))
  data['nLayers'].append(';\n')
  
  #largeNumber
  data['largeNumber'].append(' ')
  data['largeNumber'].append(str(data_var['largeNumber']))
  data['largeNumber'].append(';\n')
  
  #soc_lower_bound
  data['soc_lower_bound'].append(' ')
  data['soc_lower_bound'].append(str(data_var['soc_lower_bound']))
  data['soc_lower_bound'].append(';\n')
  
  #nRoadSegs
  data['nRoadSegs'].append(' ')
  data['nRoadSegs'].append(str(len(data_var['roadSegs'])))
  data['nRoadSegs'].append(';\n')
  
  #budget
  data['budget'].append(' ')
  data['budget'].append(str(data_var['budget']))
  data['budget'].append(';\n')
  
  #costInstall
  for roadSeg in data_var['roadSegs']:
    if roadSeg != 1:
      seg = str(roadSeg -2)
      cost = graph.node[seg]['length']*0.236 # $236 per meter or $0.236 per km
      data['costInstall'].append(str(roadSeg) + " " + str(cost) + "\n")
    else:
      data['costInstall'].append(str(roadSeg) + " 1\n")
  if data['costInstall'][-1] == '\n':
    data['costInstall'][-1] = ';\n'
  else:
    data['costInstall'].append(';\n')
  
  #weight
  if data['weight'][-1] == '\n':
    data['weight'][-1] = ';\n'
  else:
    data['weight'].append(';\n')
  
  #boundary_node_weights
  if data['boundary_node_weights'][-1] == '\n':
    data['boundary_node_weights'][-1]= ';\n'
  else:
    data['boundary_node_weights'].append(';\n')
  #boundary_nodes
  if data['boundary_nodes'][-1] == '\n':
    data['boundary_nodes'][-1] = ';\n'
  else:
    data['boundary_nodes'].append(';\n') 
  for val in data:
    myFile.write("".join(data[val]))

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
  
  
def is_path_maximal(graph, left_end, right_end):
  neigh_left = graph.in_edges(left_end)
  for u,v in neigh_left:
    if u != right_end:
      new_path = nx.shortest_path(graph, source=u, target=right_end, weight='time')
      if new_path[1] == left_end:
        return False
  neigh_right = graph.out_edges(right_end)
  for u,v in neigh_right:
    if v != left_end:
      new_path = nx.shortest_path(graph, source=left_end, target=v, weight='time')
      if new_path[-2] == right_end:
        return False
  
  return True
    




def maximal_path(graph, left_end,right_end):
  
  #path = nx.shortest_path(graph, source=left_end, target=right_end, weight='time')
  
  #left side
  grow_left = True
  while grow_left:
    neigh_edges = graph.in_edges(left_end)
    size = len(neigh_edges)

    ran_neigh_indx = list(range(size))
    random.shuffle(ran_neigh_indx)
    if size == 0:
      grow_left = False
      new_path = nx.shortest_path(graph, source=left_end, target=right_end, weight='time')
    non_candidate = 0
    for indx in ran_neigh_indx:
      ran_edge = neigh_edges[indx]
      new_left, old_left = ran_edge
      path = nx.shortest_path(graph, source=new_left, target=right_end, weight='time')
      if new_left != right_end:
        if path[1] == old_left:
          left_end = new_left
          new_path = copy.copy(path)
          break
        else:
          non_candidate += 1
      else:
        non_candidate += 1
    if non_candidate == size:
      grow_left = False
      new_path = nx.shortest_path(graph, source=left_end, target=right_end, weight='time')
        
  #right side
  grow_right = True
  while grow_right:
    neigh_edges = graph.out_edges(right_end)
    size = len(neigh_edges)
    ran_neigh_indx = list(range(size))
    random.shuffle(ran_neigh_indx)
    if size == 0:
      grow_right = False
    non_candidate = 0
    for indx in ran_neigh_indx:
      ran_edge = neigh_edges[indx]
      old_right, new_right = ran_edge
      if left_end != new_right:
        path = nx.shortest_path(graph, source=left_end, target=new_right, weight='time')

        if path[-2] == old_right:
          right_end = new_right
          new_path = copy.copy(path)
          break
        else:
          non_candidate += 1
      else:
        non_candidate += 1
    if non_candidate == size:
      grow_right = False  
      #path = nx.shortest_path(graph, source=new_left, target=right_end, weight=None) 
      
  
  return new_path
 
#need to check
#input is graph, howeever roadSegGraph is used
def modify_graph_weights(graph):
  
  for edge in graph.edges():
    u, v = edge
    distance = graph[u][v]['weight']*0.00621371*INCREASE_LENGTH+EPSILON_LENGTH
    location = graph.node[u]['location']
    speed = graph.node[u]['speed_urban']*DECREASE_SPEED
    time = distance/speed*3600
    graph[u][v]['time'] = time

def no_install_final_soc(graph, path):
  current_range_soc = 1
  
  #INSTALL = False
  for roadSeg in path:

    INSTALL = False
    velocity = graph.node[roadSeg]['speed_urban']
    distance = graph.node[roadSeg]['length']*0.00621371 #real soc no decrease or increase speed or distance
    current_range_soc = write_data.nextSOC_real_data(current_range_soc, distance, 1, velocity, INSTALL)


  return current_range_soc

#@profile
def choose_routes_at_random():
  #roadSegGraph = nx.read_graphml("roadSegGraph_968.graphml")
  #roadSegGraph = nx.read_graphml("roadSegGraph_110.graphml")
  #roadSegGraph = nx.read_graphml("roadSegGraph.graphml")
  roadSegGraph = nx.read_graphml("graph_data/lower_manhattan1_5.graphml")
  '''
  Budget: lower_manhattan1_5.graphml
  total_distance = 683531.637168
  1% budget = 1606299.347344
  2% budget = 3212598.694688
  4% budget = 6425197.389375
  8% budget = 12850394.778750
  16% budget = 25700789.557501


  '''
  modify_graph_weights(roadSegGraph)
  

  num_routes = 200
  nLayers = 11
  budget = 20*1608 # in thousand dollars
  largeNumber = 20**10
  filename = 'mydata_temp3.dat'
  
  nnodes = nx.number_of_nodes(roadSegGraph)
  pathNumber = 1
  data, data_var = init_dataFile(nLayers, budget, num_routes, largeNumber,soc_lower_bound)
  
  used_paths = {}
  while pathNumber <= num_routes:
    i, j = random.sample(range(1,nnodes+1), 2)
    start = str(i)
    end = str(j)
    #print i, j
    
    if nx.has_path(roadSegGraph, start, end):
      shortest_path = maximal_path(roadSegGraph, start, end)
      #shortest_path = nx.shortest_path(roadSegGraph, source=start, target=end, weight='time') 
      start = shortest_path[0]
      end = shortest_path[-1]
      current_range_soc = no_install_final_soc(roadSegGraph, shortest_path)
      if current_range_soc < 0.7 and (start, end) not in used_paths:
        used_paths[(start, end)] = True
        print pathNumber, current_range_soc, len(shortest_path)
        
        path  = [int(v) + 2 for v in shortest_path] 
        path.append(1)
        if pathNumber > 1:
          write = 'a'
        else:
          write = 'w'
        
        write_route_to_file(path, write)

        data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)

        pathNumber += 1
        
  write_data_to_file(filename, roadSegGraph, data, data_var) 
        
def choose_routes_evenly():
  #roadSegGraph = nx.read_graphml("roadSegGraph_968.graphml")
  #roadSegGraph = nx.read_graphml("roadSegGraph_110.graphml")
  #roadSegGraph = nx.read_graphml("roadSegGraph.graphml")
  roadSegGraph = nx.read_graphml("graph_data/lower_manhattan1_5.graphml")
  '''
  Budget: lower_manhattan1_5.graphml
  total_distance = 683531.637168
  1% budget = 1606299.347344
  2% budget = 3212598.694688
  4% budget = 6425197.389375
  8% budget = 12850394.778750
  16% budget = 25700789.557501


  '''
  modify_graph_weights(roadSegGraph)
  

  num_routes = 100
  nLayers = 11
  budget = 10*1608 # in thousand dollars
  largeNumber = 20**10
  filename = 'mydata_temp3.dat'
  
  nnodes = nx.number_of_nodes(roadSegGraph)
  
  pathNumber = 1
  data, data_var = init_dataFile(nLayers, budget, num_routes, largeNumber,soc_lower_bound)
  
  used_paths = {}
  
  tuple_indx = range(nnodes*nnodes)
  print 'before shuffle'
  random.shuffle(tuple_indx)
  print 'after shuffle'
  route_indx = 0
  
  ratio_routes = [0 for i in range(4)] # 0.4, 0.6,0.8,1
  
  total_routes = nnodes**2-1
  while pathNumber <= num_routes:
    route_no = tuple_indx[route_indx]
    col = route_no%nnodes
    row = (route_no - col)/nnodes
    row = int(row) 
    
    route_indx += 1
    if route_indx >= total_routes:
      print "ERROR, num_routes too large"
      break
    start = str(row + 1) #indexing of nodes is from 1 to n
    end = str(col + 1)

    if nx.has_path(roadSegGraph, start, end) and start != end:
      if is_path_maximal(roadSegGraph, start, end):
        #shortest_path = maximal_path(roadSegGraph, start, end)
        shortest_path = nx.shortest_path(roadSegGraph, source=start, target=end, weight='time') 
        start = shortest_path[0]
        end = shortest_path[-1]
        current_range_soc = no_install_final_soc(roadSegGraph, shortest_path)
        
        if (start,end) not in used_paths:
          if current_range_soc < 0.4 and ratio_routes[0] <= int(0.25*num_routes): 
            used_paths[(start,end)] = True
            ratio_routes[0] += 1
            print pathNumber
            path  = [int(v) + 2 for v in shortest_path] 
            path.append(1)
            if pathNumber > 1:
              write = 'a'
            else:
              write = 'w'        
            write_route_to_file(path, write)
            data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)
            pathNumber += 1
          elif current_range_soc >= 0.4 and current_range_soc < 0.6 and ratio_routes[1] <= int(0.25*num_routes):
            ratio_routes[1] += 1
            used_paths[(start,end)] = True
            print pathNumber
            path  = [int(v) + 2 for v in shortest_path] 
            path.append(1)
            if pathNumber > 1:
              write = 'a'
            else:
              write = 'w'        
            write_route_to_file(path, write)
            data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)
            pathNumber += 1
            
          elif current_range_soc >= 0.6 and current_range_soc < 0.8 and ratio_routes[2] <= int(0.25*num_routes):
            ratio_routes[2] += 1
            used_paths[(start,end)] = True
            print pathNumber
            path  = [int(v) + 2 for v in shortest_path] 
            path.append(1)
            if pathNumber > 1:
              write = 'a'
            else:
              write = 'w'        
            write_route_to_file(path, write)
            data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)
            pathNumber += 1  
          elif current_range_soc >= 0.8 and ratio_routes[3] <= int(0.25*num_routes):
            ratio_routes[3] += 1
            used_paths[(start,end)] = True
            print pathNumber
            path  = [int(v) + 2 for v in shortest_path] 
            path.append(1)
            if pathNumber > 1:
              write = 'a'
            else:
              write = 'w'        
            write_route_to_file(path, write)
            data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)
            pathNumber += 1 
        
  write_data_to_file(filename, roadSegGraph, data, data_var)         


def choose_routes_iteratively():
  #roadSegGraph = nx.read_graphml("roadSegGraph_968.graphml")
  #roadSegGraph = nx.read_graphml("roadSegGraph_110.graphml")
  #roadSegGraph = nx.read_graphml("roadSegGraph.graphml")
  roadSegGraph = nx.read_graphml("graph_data/lower_manhattan1_5.graphml")
  prev_routesfile = open("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/solutions/data/prev_routes/routes1.txt", "r")
  modify_graph_weights(roadSegGraph)
  
  prev_routes = {}
  
  for line in prev_routesfile:
    _path = line.split()
    _path = _path[:-1]
    path = [int(i) - 2 for i in _path]
    prev_routes[(path[0], path[1])] = path
  
  num_routes = 100
  nLayers = 11
  budget = 10*1608 # in thousand dollars
  largeNumber = 20**10
  filename = 'mydata_temp_iterate.dat'
  
  nnodes = nx.number_of_nodes(roadSegGraph)
  
  pathNumber = 1
  data, data_var = init_dataFile(nLayers, budget, num_routes, largeNumber,soc_lower_bound)
  
  used_paths = {}
  
  tuple_indx = range(nnodes*nnodes)
  print 'before shuffle'
  random.shuffle(tuple_indx)
  print 'after shuffle'
  route_indx = 0
  
  ratio_routes = [0 for i in range(4)] # 0.4, 0.6,0.8,1
  
  total_routes = nnodes**2-1
  while pathNumber <= num_routes:
    route_no = tuple_indx[route_indx]
    col = route_no%nnodes
    row = (route_no - col)/nnodes
    row = int(row) 
    
    route_indx += 1
    if route_indx >= total_routes:
      print "ERROR, num_routes too large"
      break
    start = str(row + 1) #indexing of nodes is from 1 to n
    end = str(col + 1)

    if nx.has_path(roadSegGraph, start, end) and start != end:
      if is_path_maximal(roadSegGraph, start, end):
        #shortest_path = maximal_path(roadSegGraph, start, end)
        shortest_path = nx.shortest_path(roadSegGraph, source=start, target=end, weight='time') 
        start = shortest_path[0]
        end = shortest_path[-1]
        current_range_soc = no_install_final_soc(roadSegGraph, shortest_path)
        
        if (start,end) not in used_paths:
          if current_range_soc < 0.4 and ratio_routes[0] <= int(0.25*num_routes): 
            used_paths[(start,end)] = True
            ratio_routes[0] += 1
            print pathNumber
            path  = [int(v) + 2 for v in shortest_path] 
            path.append(1)
            if pathNumber > 1:
              write = 'a'
            else:
              write = 'w'        
            write_route_to_file(path, write)
            data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)
            pathNumber += 1
          elif current_range_soc >= 0.4 and current_range_soc < 0.6 and ratio_routes[1] <= int(0.25*num_routes):
            ratio_routes[1] += 1
            used_paths[(start,end)] = True
            print pathNumber
            path  = [int(v) + 2 for v in shortest_path] 
            path.append(1)
            if pathNumber > 1:
              write = 'a'
            else:
              write = 'w'        
            write_route_to_file(path, write)
            data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)
            pathNumber += 1
            
          elif current_range_soc >= 0.6 and current_range_soc < 0.8 and ratio_routes[2] <= int(0.25*num_routes):
            ratio_routes[2] += 1
            used_paths[(start,end)] = True
            print pathNumber
            path  = [int(v) + 2 for v in shortest_path] 
            path.append(1)
            if pathNumber > 1:
              write = 'a'
            else:
              write = 'w'        
            write_route_to_file(path, write)
            data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)
            pathNumber += 1  
          elif current_range_soc >= 0.8 and ratio_routes[3] <= int(0.25*num_routes):
            ratio_routes[3] += 1
            used_paths[(start,end)] = True
            print pathNumber
            path  = [int(v) + 2 for v in shortest_path] 
            path.append(1)
            if pathNumber > 1:
              write = 'a'
            else:
              write = 'w'        
            write_route_to_file(path, write)
            data, data_var = path_to_layeredGraph(roadSegGraph, path, pathNumber, data, data_var, nLayers)
            pathNumber += 1 
        
  write_data_to_file(filename, roadSegGraph, data, data_var)      
  
         
if __name__ == "__main__":
  soc_lower_bound = 0.6
  #choose_routes_evenly()
  choose_routes_at_random()
 
