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

DECREASE_SPEED = 0.3
INCREASE_LENGTH = 10
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
  
  
#
def path_feasible(path, graph, init_soc):

    current_range_soc = init_soc
    for roadSeg in path:
        velocity = graph.node[roadSeg]['speed_urban']*DECREASE_SPEED #this is modified such that if we install every then final_soc = 1 if start_soc = 1
        distance = graph.node[roadSeg]['length']*0.000621371*INCREASE_LENGTH
       
        current_range_soc = write_data.nextSOC_real_data(current_range_soc, distance, 1, velocity, False)

    return current_range_soc

#determine ith position from the top of layered graph in a given s
#zero based index
def position_in_layer(soc, nLayers):
  posn = (nLayers-1)*(1 - soc) 
  posn = round(posn)
  return int(posn)
  
  
#
def prevSOC(currentSOC, nLayers, prev_road_cat):
  
  prev_soc = set()
  for i in range(1,nLayers):
    p_soc = i/(nLayers-1)
    if prev_road_cat != 0:
      soc = nextSOC(p_soc, True, nLayers, prev_road_cat)

      if soc <= currentSOC + 1.0e-10 and soc >= currentSOC - 1.0e-10:
        prev_soc.add(p_soc)

      soc = nextSOC(p_soc, False, nLayers, prev_road_cat)
      if soc <= currentSOC + 1.0e-10 and soc >= currentSOC - 1.0e-10:
        prev_soc.add(p_soc)
    else:
      soc = nextSOC(p_soc, False, nLayers, prev_road_cat)
      if soc <= currentSOC + 1.0e-10 and soc >= currentSOC - 1.0e-10:
        prev_soc.add(p_soc)
  return prev_soc
 
 
#categorize road in order to determine inc and dec of soc
def road_category_by_time(graph, num_categories, min_time, max_time, nLayers):
  #category
  # 0 -- Do not install
  # i -- soc goes up/down by i units
  if nLayers/2 < num_categories:
    raise ValueError("ERROR: nLayers/2 should be greater than num_categories")
  
  road_category = {}
  step_size = (max_time - min_time)/(num_categories)
  #print min_time, max_time
  timeframe = [min_time + n*step_size for n in range(num_categories + 1) ]
  #print timeframe
  for road in graph.nodes():
    velocity = graph.node[road]['speed_urban']*DECREASE_SPEED
    distance = graph.node[road]['length']*0.000621371 
    t = distance/velocity*3600
    
    for i in range(num_categories):
      if t >= timeframe[i] and t <= timeframe[i+1]:
        road_category[road] = i + 1
        break
    
      
  return road_category
  
#convert a road seg# to node#
def roadSeg_to_node(roadSeg, nLayers):
  
  node = (roadSeg-1)*nLayers + 1
  
  return node

#
def node_to_soc(node, nLayers):
  posn = (node-1)%nLayers 
  soc =  1-  posn/(nLayers-1)
  
  return soc
  
#
def nextSOC(currentSOC, INSTALL, nLayers, road_cat):
  if currentSOC == 0:
    return currentSOC
  
  if INSTALL:
    return min(1, currentSOC + road_cat/(nLayers-1))
  else:
    return max(0, currentSOC - road_cat/(nLayers-1))

#
#determine corresponding roadSeg for a given node
def node_to_roadSeg(node, nLayers):

  if node == 'source' or node == 'destination':
    return node
  else:
    roadSeg = math.ceil(node/nLayers)
  return int(roadSeg)
 
 
# 
def path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers, initial_soc):
  
  #soure arcs
  next_node = roadSeg_to_node(path[0], nLayers)

  #source -> path[0]
  for i in range(nLayers):
    data_var['nodes'].add(next_node + i)  
    data['arcs'].append("".join([" (", str(pathNumber), ",source,", str(next_node + i), ")\n" ]) )
    data['weight'].append( "".join([" ", str(pathNumber), " source ", str(next_node + i), " 0\n" ]))

  #path[-1] -> destination
  node = roadSeg_to_node(path[-1], nLayers)
  data_var['roadSegs'].add(path[-1])
  for i in range(nLayers):
    data_var['nodes'].add(node + i)
    data['arcs'].append("".join([ " (", str(pathNumber), ",", str(node + i), ", destination) \n" ]) )
    data['weight'].append("".join([ " ", str(pathNumber), " ", str(node + i), " destination 0 \n" ]) )
    standard_soc = node_to_soc(node + i, nLayers)
    data['boundary_node_weights'].append("".join([" ",str(pathNumber), " ", str(node + i),  " ", str(standard_soc),"\n" ]))
    data['boundary_nodes'].append("".join([ " (",str(pathNumber), ",", str(node + i),  ")\n" ]))
    
  #path[i] -> path[i + 1]
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
        data['arcs'].append("".join([ " (",str(pathNumber), ",", str(current_node), ",",  " destination)\n" ]))
        data['weight'].append("".join([" ",str(pathNumber), " ", str(current_node),  " destination 0\n" ]))
        data['boundary_node_weights'].append("".join([ " ",str(pathNumber), " ", str(current_node),  " ", str(-(len_path -1 -i)/(len_path -1)),"\n" ]))
        data['boundary_nodes'].append("".join([ " (",str(pathNumber), ",", str(current_node),  ")\n" ]))
      else:
        road_cat = road_category[str(roadSeg-2)]
        if road_cat != 0:
  #########
          #random start soc
          if roadSeg == path[0]:
            current_soc = initial_soc
            current_node = start_node + position_in_layer(initial_soc, nLayers)
          #INSTALL = True
          #print current_soc
          INSTALL = True
          next_soc = nextSOC(current_soc, INSTALL, nLayers, road_cat)
          next_node_posn = position_in_layer(next_soc, nLayers)
          next_node = next_start_node + next_node_posn
          data['arcs'].append("".join([" (",str(pathNumber), ",", str(current_node), ",", str(next_node), ") \n" ]))
          data['weight'].append("".join([ " ",str(pathNumber), " ", str(current_node), " ", str(next_node), " 1\n" ]))

          #INSTALL = False
          INSTALL = False
          next_soc = nextSOC(current_soc, INSTALL, nLayers,road_cat)
          next_node_posn = position_in_layer(next_soc, nLayers)
          next_node = next_start_node + next_node_posn
          data['arcs'].append("".join([ " (",str(pathNumber), ",", str(current_node), ",", str(next_node), ")\n" ]))
          data['weight'].append("".join([" ",str(pathNumber), " ", str(current_node), " ", str(next_node), " 0\n" ]))
          #print current_standard_soc, current_range_soc, next_range_soc
          #Assume vehicle starts fully charged thus only one layer for first roadSeg
          if roadSeg == path[0]:
            break
       
        else: #road_category == 0
          INSTALL = False
          if roadSeg == path[0]:
            current_soc = initial_soc
            current_node = start_node + position_in_layer(initial_soc, nLayers)
          next_soc = nextSOC(current_soc, INSTALL, nLayers,road_cat)
          next_node_posn = position_in_layer(next_soc, nLayers)
          next_node = next_start_node + next_node_posn
          data['arcs'].append("".join([ " (",str(pathNumber), ",", str(current_node), ",", str(next_node), ")\n" ]))
          data['weight'].append("".join([" ",str(pathNumber), " ", str(current_node), " ", str(next_node), " 0\n" ]))
          #print current_standard_soc, current_range_soc, next_range_soc
          #Assume vehicle starts fully charged thus only one layer for first roadSeg
          if roadSeg == path[0]:
            break
           

  return data, data_var

def modify_road_category(graph, road_category, btn_filepath, threshold):
  
    btn_file = open(btn_filepath, 'r')
    node = 1
    centrality = {}
    
    for line in btn_file:
      cen = float(line)
      centrality[str(node)] = cen
      if cen <= threshold:
        road_category[str(node)] = 0
      node += 1
    return road_category, centrality


#initialize data and data_var
def init_dataFile(nLayers, budget, nRoutes, largeNumber):
  
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
  #data['soc_lower_bound']= ['param soc_lower_bound :=']
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
  #data_var['soc_lower_bound'] = soc_lower_bound
  
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
  #data['soc_lower_bound'].append(' ')
  #data['soc_lower_bound'].append(str(data_var['soc_lower_bound']))
  #data['soc_lower_bound'].append(';\n')
  
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
  
def write_route_to_file(path,initial_soc, write):
  myFile = open('routes.txt', write)
  initial_soc_file = open('/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/iterative_initial_soc.txt', write)
  out = [str(i) for i in path]
  out = " ".join(out)
  out += "\n"
  myFile.write(out)
  myFile.close()
  
  initial_soc_file.write(str(initial_soc)+"\n")
  initial_soc_file.close()


#
def modify_graph_weights(graph):
  
  for edge in graph.edges():
    u, v = edge
    distance = graph[u][v]['weight']*0.0006213710
    location = graph.node[u]['location']
    speed = graph.node[u]['speed_urban']*DECREASE_SPEED
    time = distance/speed*3600
    graph[u][v]['time'] = time

  

def contain_atleast_one_high_central_node(road_category, path):
  
  for seg in path:
    if road_category[seg] > 0:
      return True
  
  return False


#
def most_central_node_within_budget(btn_filepath, budget, graph):

  total_distance = 0
  for road in graph.nodes():
    total_distance += float(graph.node[road]['length'])
  
  centrality_file = open(btn_filepath, 'r')
  centrality = {}
  node = 1
  for line in centrality_file:
    centrality[str(node)] = float(line)
    node += 1
  sorted_centrality = sorted([(centrality[node], node) for node in graph.nodes()], reverse=True)
  print 'total distance', total_distance
  top_nodes = []
  
  max_distance = total_distance*budget
  distance_used = 0
  
  for cen, road in sorted_centrality:
    if distance_used + float(graph.node[road]['length']) <= max_distance:
      top_nodes.append(road)
      distance_used += float(graph.node[road]['length'])
      
  return top_nodes, total_distance
  
#
def choose_routes_randomly():
  num_routes  = 1
  budget = 10*1608 # in thousand dollars
  largeNumber = 20**10
  filename = 'mydata.dat'

  nnodes = nx.number_of_nodes(graph)
  pathNumber = 1
  data, data_var = init_dataFile(nLayers, budget, num_routes, largeNumber)

  
  tuple_indx = range(nnodes*nnodes)
  print 'shuffling all n^2 routes...'
  random.shuffle(tuple_indx)
  print 'shuffle complete'
  route_indx = 0
  
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
    
    if nx.has_path(graph, start, end) and start != end:
      #shortest_path = maximal_path(graph, start, end)
      shortest_path = nx.shortest_path(graph, source=start, target=end, weight='time') 
      start = shortest_path[0]
      end = shortest_path[-1]
      #current_range_soc = no_install_final_soc(graph, shortest_path)
      valid_path = contain_atleast_one_high_central_node(road_category, shortest_path)
      if valid_path:
        print pathNumber
        
        path  = [int(v) + 2 for v in shortest_path] 
        path.append(1)
        if pathNumber > 1:
          write = 'a'
        else:
          write = 'w'
        
        write_route_to_file(path,initial_soc, write)

        data, data_var = path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers, initial_soc)

        pathNumber += 1
        
  write_data_to_file(filename, graph, data, data_var) 
  
  
  
  
  
#
def expand_top_nodes_to_path():

  budget_percentage = 0.1
  top_nodes, total_distance = most_central_node_within_budget(btn_filepath, budget_percentage, graph)

  num_routes  = 1000
  budget = 10*1610 # in thousand dollars
  largeNumber = 20**10
  filename = 'mydata.dat'

  nnodes = nx.number_of_nodes(graph)
  pathNumber = 1
  data, data_var = init_dataFile(nLayers, budget, num_routes, largeNumber)
  
  used_path = {}
  while pathNumber <= num_routes:
    top_road = random.choice(top_nodes)
    
    #if nx.has_path(graph, start, end) and start != end:
    shortest_path = maximal_path(graph, top_road, top_road)
    #shortest_path = nx.shortest_path(graph, source=start, target=end, weight='time') 
    start = shortest_path[0]
    end = shortest_path[-1]
    #current_range_soc = no_install_final_soc(graph, shortest_path)

    if len(shortest_path) > 20 and (start, end) not in used_path:
      print pathNumber
      used_path[(start,end)] = True
      path  = [int(v) + 2 for v in shortest_path] 
      path.append(1)
      if pathNumber > 1:
        write = 'a'
      else:
        write = 'w'
      
      write_route_to_file(path, initial_soc, write)

      data, data_var = path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers, initial_soc)

      pathNumber += 1
        
  write_data_to_file(filename, graph, data, data_var) 


def top_node_dic(graph, top_nodes):
  
  is_top_node = {}
  
  for node in graph.nodes():
    if node in top_nodes:
      is_top_node[node] = True
    else:
      is_top_node[node] = False
 
  return is_top_node

def contains_top_node(path, is_top_node):

  for node in path:
    if is_top_node[node]:
      return True
      
  return False
 
 
 
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


def choose_routes_with_top_nodes():
  num_routes = 100

  #budget = 30*1608 # in thousand dollars
  largeNumber = 20**10
  filename = 'mydata.dat'
  
  budget_percentage = 0.20
  top_nodes, total_distance = most_central_node_within_budget(btn_filepath, budget_percentage, graph)
  budget = int(budget_percentage*total_distance*0.237) # $237 per meter or $0.236 per km

  is_top_node = top_node_dic(graph, top_nodes)
  nnodes = nx.number_of_nodes(graph)
  
  pathNumber = 1
  data, data_var = init_dataFile(nLayers, budget, num_routes, largeNumber)
  
  used_paths = {}

  tuple_indx = range(nnodes*nnodes)
  print 'before shuffle'
  random.shuffle(tuple_indx)
  print 'after shuffle'
  route_indx = 0
  
  ratio_routes = [0 for i in range(2)] # 0.4, 0.6,0.8,1
  soc_hist = []
  path_len_hist = []
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

    if nx.has_path(graph, start, end) and start != end:
      #if is_path_maximal(graph, start, end):
      #shortest_path = maximal_path(graph, start, end)
      shortest_path = nx.shortest_path(graph, source=start, target=end, weight='time') 
      start = shortest_path[0]
      end = shortest_path[-1]
      
      current_range_soc = path_feasible(shortest_path, graph, 1)
      
      if (start,end) not in used_paths:
        #soc_hist.append(current_range_soc)
        #path_len_hist.append(len(shortest_path))
        if current_range_soc < 0.84 and ratio_routes[0] <= int(0.7*num_routes): 
          used_paths[(start,end)] = True
          ratio_routes[0] += 1
          print pathNumber, route_indx, current_range_soc, len(shortest_path)
          path  = [int(v) + 2 for v in shortest_path] 
          path.append(1)
          if pathNumber > 1:
            write = 'a'
          else:
            write = 'w'        
          write_route_to_file(path,initial_soc, write)
          data, data_var = path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers, initial_soc)
          pathNumber += 1
        elif current_range_soc < 0.85 and ratio_routes[1] <= int(0.3*num_routes) and contains_top_node(shortest_path, is_top_node):
          ratio_routes[1] += 1
          used_paths[(start,end)] = True
          print pathNumber, route_indx,current_range_soc, len(shortest_path),"top"
          path  = [int(v) + 2 for v in shortest_path] 
          path.append(1)
          if pathNumber > 1:
            write = 'a'
          else:
            write = 'w'        
          write_route_to_file(path, initial_soc, write)
          data, data_var = path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers, initial_soc)
          pathNumber += 1
            
  #print "drawing hist"
  #plt.hist(soc_hist, bins=100, histtype='bar', normed=1, color='g', label='time')
  #plt.show()    
  write_data_to_file(filename, graph, data, data_var)      
  
def choose_routes_from_file():
  routes_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/iterative_routes.txt", "r")
  #initial_soc_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/iterative_initial_soc.txt", "r")
  num_routes = 150
  
  

  #budget = 30*1608 # in thousand dollars
  largeNumber = 20**10
  filename = 'mydata.dat'
  
  budget_percentage = 0.20
  top_nodes, total_distance = most_central_node_within_budget(btn_filepath, budget_percentage, graph)
  budget = int(budget_percentage*total_distance*0.237) # $237 per meter or $0.236 per km

  nnodes = nx.number_of_nodes(graph)
  count = 0
  pathNumber = 1
  data, data_var = init_dataFile(nLayers, budget, num_routes, largeNumber)
  used_paths = {}
  for line in routes_file:
    count += 1
    start, end = line.split()
    #shortest_path = nx.shortest_path(graph, source=start, target=end, weight='time') 
    shortest_path = maximal_path(graph, start,end)
    start = shortest_path[0]
    end = shortest_path[1]
    current_range_soc = path_feasible(shortest_path, graph, 1)
    print pathNumber, count

    if (start,end) not in used_paths and current_range_soc < 0.85:
      #print pathNumber, count
      used_paths[(start,end)] = True
      path  = [int(v) + 2 for v in shortest_path] 
      path.append(1)
      if pathNumber > 1:
        write = 'a'
      else:
        write = 'w'  
      initial_soc = random.choice(range(5, nLayers))/(nLayers -1)      
      write_route_to_file(path, initial_soc, write)
      
      data, data_var = path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers, initial_soc)
      pathNumber += 1
      
      if pathNumber > num_routes:
        print pathNumber, num_routes
        break
 

  write_data_to_file(filename, graph, data, data_var)      
  


def distance_of_path(graph, path):
  distance = 0
  
  for node in path:
    distance += float(graph.node[node]['length'])
    
  return distance

##--

def choose_routes_from_file_and_random(num_routes_to_add):
  routes_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/iterative_routes.txt", "r")
  #initial_soc_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/iterative_initial_soc.txt", "r")
  num_routes = 150 + num_routes_to_add

  #budget = 30*1608 # in thousand dollars
  largeNumber = 20**10
  filename = 'mydata.dat'
  
  budget_percentage = 0.20
  top_nodes, total_distance = most_central_node_within_budget(btn_filepath, budget_percentage, graph)
  budget = int(budget_percentage*total_distance*0.237) # $237 per meter or $0.236 per km

  nnodes = nx.number_of_nodes(graph)
  count = 0
  pathNumber = 1
  data, data_var = init_dataFile(nLayers, budget, num_routes, largeNumber)
  used_paths = {}
  for line in routes_file:
    count += 1
    start, end = line.split()
    #shortest_path = nx.shortest_path(graph, source=start, target=end, weight='time') 
    shortest_path = maximal_path(graph, start,end)
    start = shortest_path[0]
    end = shortest_path[1]
    current_range_soc = path_feasible(shortest_path, graph, 1)
    print pathNumber, count

    if (start,end) not in used_paths and current_range_soc < 0.85:
      #print pathNumber, count
      used_paths[(start,end)] = True
      path  = [int(v) + 2 for v in shortest_path] 
      path.append(1)
      if pathNumber > 1:
        write = 'a'
      else:
        write = 'w'  
      initial_soc = random.choice(range(4, nLayers))/(nLayers -1)      
      write_route_to_file(path, initial_soc, write)
      
      data, data_var = path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers, initial_soc)
      pathNumber += 1
      if pathNumber > num_routes:
        print pathNumber, num_routes
        break

  #add random long paths
  print "complete: routes from file", pathNumber, num_routes
  avg_distance = 2861.51384791
  std_distance = 1429.38854176
  route_indx = 0
  tuple_indx = range(nnodes*nnodes)
  while pathNumber <= num_routes:
    route_no = tuple_indx[route_indx]
    col = route_no%nnodes
    row = (route_no - col)/nnodes
    row = int(row) 
    route_indx += 1
    if route_indx >= nnodes*nnodes:
      print "ERROR, num_routes too large"
      break
    start = str(row + 1) #indexing of nodes is from 1 to n
    end = str(col + 1)

    if nx.has_path(graph, start, end) and start != end:
      #shortest_path = maximal_path(graph, start, end)
      shortest_path = nx.shortest_path(graph, source=start, target=end, weight='time') 
      start = shortest_path[0]
      end = shortest_path[-1]
      #current_range_soc = no_install_final_soc(graph, shortest_path)

      if  distance_of_path(graph, shortest_path) > avg_distance + 2*std_distance:
        print pathNumber
        
        path  = [int(v) + 2 for v in shortest_path] 
        path.append(1)
        if pathNumber > 1:
          write = 'a'
        else:
          write = 'w'
        initial_soc = random.choice(range(4, nLayers))/(nLayers -1)
        write_route_to_file(path,initial_soc, write)
        data, data_var = path_to_layeredGraph(graph, path, pathNumber, data, data_var, nLayers, initial_soc)

        pathNumber += 1
        
  write_data_to_file(filename, graph, data, data_var) 
  
  
   
 

##global variables--
#graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/lower_manhattan1_5.graphml")
#graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/greenville1_5.graphml")
graph = nx.read_graphml("/home/hushiji/Research/smart_cities/smart_cities/real_data_sol/graph_data/manhattan_neigborhood.graphml")
time_lst = []
modify_graph_weights(graph)

for road in graph.nodes():
  d = graph.node[road]['length']*0.0006213710
  s = graph.node[road]['speed_urban']*DECREASE_SPEED
  t = d/s*3600
  graph.node[road]['time'] = t
  time_lst.append(t)


num_categories = 5
min_time = min(time_lst)
max_time = max(time_lst)
nLayers =11
install_btn_threshold =  0.0001
#btn_filepath = "/home/hushiji/Research/smart_cities/smart_cities/general_soc/data/betweenness.centrality"
#btn_filepath = "/home/hushiji/Research/smart_cities/smart_cities/general_soc/data/greenville_betweenness.centrality"
btn_filepath = "/home/hushiji/Research/smart_cities/smart_cities/general_soc/data/manhattan_neigh_betweenness.centrality"
road_category = road_category_by_time(graph, num_categories, min_time, max_time, nLayers)
road_category, centrality = modify_road_category(graph, road_category, btn_filepath, install_btn_threshold)





### main ###  
if __name__ == "__main__":

  ##
  #choose_routes_randomly()
  #choose_routes_with_top_nodes()
  #choose_routes_from_file()
  num_routes_to_add = 800
  choose_routes_from_file_and_random(num_routes_to_add)
  
