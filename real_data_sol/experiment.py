import networkx as nx
import random
import re, os, sys
#create data
#run pyomo
#read results
#draw picuture

os.system("python create_data.py")
os.system("pyomo solve --solver=cplex --stream-solver --solver-options='mipgap=1.0' create_model.py mydata.dat")
os.system("python get_edges.py")
os.system("python solutions/visualize.py")


