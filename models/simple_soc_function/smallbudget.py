from __future__ import division
from pyomo.environ import *
import math
import write_data
model = AbstractModel()
model.nodes =    Set()
model.route_no = Set()
model.nRoutes = Param(within=NonNegativeIntegers)
model.nLayers = Param(within=NonNegativeIntegers)
model.largeNumber = Param(within=NonNegativeIntegers)
model.budget = Param(within=NonNegativeIntegers)
model.nRoadSegs = Param(within=NonNegativeIntegers)
model.arcs =     Set(within=model.route_no*model.nodes*model.nodes)
model.weight    =     Param(model.arcs, within=NonNegativeReals)
model.roadSegs = Set()
model.roadInstall = Var(model.roadSegs, within=Boolean)
model.x    =     Var(model.arcs, within=Boolean)
model.costInstall = Param(model.roadSegs)
model.boundary_nodes = Set(within=model.route_no*model.nodes)
model.boundary_node_weights = Param(model.boundary_nodes)



model.Routes = {}
#read routes from file
myFile = open("routes.txt", "r")
count = 1
for line in myFile:
  lines_split = line.split()
  route = [int(r) for r in lines_split]
  model.Routes[count] = route
  count += 1
myFile.close()

def roadSeg_to_node(model, roadSeg):
  
  node = (roadSeg-1)*model.nLayers.value + 1
  
  return node

def node_to_roadSeg(model, node):
  if node == 'source' or node == 'destination':
    return node
  else:
    roadSeg = math.ceil(node/model.nLayers.value)
    #roadSeg = (node - node%(model.nLayers.value))/model.nLayers.value + 1
  return int(roadSeg)
 
 
def boundary_nodes_init(model, route_no):
  
  out = []
  for roadSeg in model.Routes[route_no][1:-1]:
    start_node = write_data.roadSeg_to_node(roadSeg, model.nLayers.value)
    out.append(start_node + model.nLayers.value -1)
  roadSeg = model.Routes[route_no][-1]
  start_node = start_node = write_data.roadSeg_to_node(roadSeg, model.nLayers.value)
  for i in range(model.nLayers.value):
    out.append(start_node +i)
  return out
    
#model.boundary_nodes = Set(model.route_no, initialize=boundary_nodes_init) 


def NodesOut_init(model, node, route_no):
  out = []

  if node == 'source':
    start_node = write_data.roadSeg_to_node(model.Routes[route_no][0], model.nLayers.value)
    for i in range( model.nLayers.value ):
      out.append(start_node + i)
  
  elif node == 'destination':
    return out
  
  else:
    
    roadSeg = write_data.node_to_roadSeg(node, model.nLayers.value)
    if roadSeg not in model.Routes[route_no]:
      return out
    soc = write_data.node_to_soc(node, model.nLayers.value)
    if soc < 1.0e-10 and roadSeg != model.Routes[route_no][0]:
      out.append('destination')
      return out
      
    if roadSeg == model.Routes[route_no][-1]:
      out.append('destination')
    elif roadSeg == model.Routes[route_no][0]:
      next_roadSeg = model.Routes[route_no][1]
      next_start_node = write_data.roadSeg_to_node(next_roadSeg, model.nLayers.value)
      if node == write_data.roadSeg_to_node(roadSeg, model.nLayers.value):
        out.append(next_start_node)
        out.append(next_start_node + 1)
    else:    
      roadSeg_indx = model.Routes[route_no].index(roadSeg)     
      next_roadSeg = model.Routes[route_no][roadSeg_indx + 1]
      next_start_node = write_data.roadSeg_to_node(next_roadSeg, model.nLayers.value)
      current_soc = write_data.node_to_soc(node, model.nLayers.value)
      if current_soc > 1.0e-10:
        #INSTALL = True
        INSTALL = True
        next_soc = write_data.nextSOC(current_soc, INSTALL, model.nLayers.value)
        next_node_posn = write_data.position_in_layer(next_soc, model.nLayers.value)
        next_node = next_start_node + next_node_posn
        out.append(next_node)
        
        #INSTALL = False
        INSTALL = False
        next_soc = write_data.nextSOC(current_soc, INSTALL, model.nLayers.value)
        next_node_posn = write_data.position_in_layer(next_soc, model.nLayers.value)
        next_node = next_start_node + next_node_posn
        if next_node != out[-1]:
          out.append(next_node)
      
  return out
  
model.NodesOut = Set(model.nodes,model.route_no, initialize=NodesOut_init)


def NodesIn_init(model, node, route_no):
  out = []

  
  
  if node == 'source':
    return out
  
  elif node == 'destination':
    start_node = write_data.roadSeg_to_node(model.Routes[route_no][-1], model.nLayers.value)
    for i in range( model.nLayers.value ):
      out.append(start_node + i)
    for roadSeg in model.Routes[route_no][1:-1]:
      start_node = write_data.roadSeg_to_node(roadSeg, model.nLayers.value)
      out.append(start_node + model.nLayers.value -1)
  
  else:
    roadSeg = write_data.node_to_roadSeg(node, model.nLayers.value)
    if roadSeg not in model.Routes[route_no]:
      return out
    if roadSeg == model.Routes[route_no][0]:
      out.append('source')
    else:
      roadSeg_indx = model.Routes[route_no].index(roadSeg)     
      prev_roadSeg = model.Routes[route_no][roadSeg_indx - 1]
      prev_start_node = write_data.roadSeg_to_node(prev_roadSeg, model.nLayers.value)
      current_soc = write_data.node_to_soc(node, model.nLayers.value)
      prev_soc = write_data.prevSOC(current_soc, model.nLayers.value)
      posn = [write_data.position_in_layer(soc, model.nLayers.value) for soc in prev_soc]
      if roadSeg == model.Routes[route_no][1]:
        if 0 in posn:
          out.append(prev_start_node)
      else:
        out = [prev_start_node + i for i in posn]
        
      
  return out
  
model.NodesIn = Set(model.nodes,model.route_no, initialize=NodesIn_init)



def flowRuleEfficient(model, node,route):
  #define paths
  #constraint_equation = True
  #for route in range(1, model.nRoutes.value + 1): 
  #source node

  if node == 'source':
    next_roadSeg = model.Routes[route][0]
    next_roadSegNode = roadSeg_to_node(model, next_roadSeg)
    flow_out = sum( \
      model.x[route, node, r] \
      for r in model.NodesOut[node,route] \
    )
        
    constraint_equation = (flow_out == 1)
  
  #destination node
  elif node == 'destination':

    prev_roadSeg = model.Routes[route][-1]
    prev_roadSegNode = roadSeg_to_node(model, prev_roadSeg)
    flow_in = sum( \
      model.x[route, r, node] \
      for r in model.NodesIn[node,route] \
    )

    
    constraint_equation = (flow_in == 1)

  #internal node
  else:
    roadSeg = node_to_roadSeg(model, node)

    if roadSeg not in model.Routes[route]:
      constraint_equation = Constraint.Feasible
      return constraint_equation
    #source roadSeg
    if roadSeg == model.Routes[route][0]:
      next_roadSeg = model.Routes[route][1]
      next_roadSegNode = roadSeg_to_node(model, next_roadSeg)
      prev_roadSegNode = 'source'
      
      amount_out = sum(\
        model.x[route, node, r] \
        for r in model.NodesOut[node,route] \
      )
      
      amount_in = model.x[route, prev_roadSegNode, node]
      constraint_equation = (amount_in - amount_out == 0)
    #destination roadSeg
    elif roadSeg == model.Routes[route][-1]:
      next_roadSegNode = 'destination'
      prev_roadSeg = model.Routes[route][-2]
      prev_roadSegNode = roadSeg_to_node(model, prev_roadSeg)
      amount_in = sum( \
        model.x[route, r, node] \
        for r in model.NodesIn[node,route] \
      )
      amount_out = model.x[route, node,  next_roadSegNode]

      constraint_equation = (amount_in - amount_out == 0)
      
    #internal roadSeg
    else:
      i = model.Routes[route].index(roadSeg)
      next_roadSeg = model.Routes[route][i + 1]
      prev_roadSeg = model.Routes[route][i - 1]
      next_roadSegNode = roadSeg_to_node(model, next_roadSeg)
      prev_roadSegNode = roadSeg_to_node(model, prev_roadSeg)
      amount_out = sum( \
        model.x[route, node, r] \
        for r in model.NodesOut[node,route] \
      ) 

      amount_in = sum( \
        model.x[route, r, node] \
        for r in model.NodesIn[node,route] \
      )
      constraint_equation = (amount_in - amount_out == 0)
      if type(amount_in) == int and type(amount_out) == int:
        constraint_equation = Constraint.Feasible



  return constraint_equation
        

model.flow = Constraint(model.nodes, model.route_no, rule=flowRuleEfficient) 


def number_required_to_install(model, roadSeg):

  number_required = 0

  for route in range(1, model.nRoutes.value + 1):
    for node in range(model.nLayers.value*(roadSeg - 1) +1, roadSeg*model.nLayers.value + 1):
      for u in model.NodesOut[node, route]:
        if u != 'destination':
          number_required += model.weight[route,node, u]*model.x[route, node,u]
  return number_required
  

def install_upper(model, roadSeg):
  constraint_equation = (model.roadInstall[roadSeg] <= number_required_to_install(model, roadSeg))
  
  return constraint_equation
  
model.installU = Constraint(model.roadSegs, rule=install_upper)

def install_lower(model, roadSeg):
  constraint_equation = (model.largeNumber.value*model.roadInstall[roadSeg] >= number_required_to_install(model, roadSeg) - 0.5)
  
  return constraint_equation
  
model.installL = Constraint(model.roadSegs, rule=install_lower)


      
       
#budget
def budget(model):
      
    out = 0
    for r in model.roadSegs:
      out += model.costInstall[r]*model.roadInstall[r]
      
    constraint_equation = (out <= model.budget.value)
    
    return constraint_equation
    
model.budgetLimit = Constraint(rule=budget)
    
    
def totalRule(model):

  output = 0

  for (r,i,j) in model.arcs:
    output += model.weight[r,i,j]*model.x[r,i,j]
    
  return output

#model.maxFlow = Objective(rule=totalRule, sense=maximize)    

def minBudget(model):

  output = 0
  
  for roadSeg in model.roadSegs:
    output += model.costInstall[roadSeg]*model.roadInstall[roadSeg]

  return output

#model.minBudget = Objective(rule=minBudget, sense=minimize) 

def maxSOC(model):
  output = 0
  
  for route_no,node in model.boundary_nodes:
    output += model.boundary_node_weights[route_no, node]*model.x[route_no, node, 'destination']
  return output
model.soc = Objective(rule=maxSOC, sense=maximize)     
