#!/usr/bin/python
from __future__ import division
import sys, os
import argparse
import math
import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
import scipy


if __name__ == "__main__":
  
  myFile = open("routes.txt", 'r')
  
  edges = []
  for line in myFile:
    route = line.split()
    route = route[:-1]
    
    for i, node in enumerate(route[:-1]):
      edge = (int(route[i]), int(route[i+1]))
      if edge not in edges:
        edges.append(edge)


  myFile.close()
  myFile = open("edges.edges", "w")
  
  for edge in edges:
    u, v = edge
    out = str(u -2 ) + " " + str(v -2) + "\n"
    myFile.write(out)

  myFile.close()
  


