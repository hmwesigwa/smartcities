from __future__ import division
import random
nlayers = 11
nroutes = 786
soc = range(3, nlayers)
initial_soc_file = open("/home/hushiji/Research/smart_cities/smart_cities/general_soc/analysis/iterative_initial_soc.txt", "w")

for i in range(3,nlayers):
	soc[i-3] = soc[i-3]/(nlayers -1)

for line in range(nroutes):
	rand_soc = random.choice(soc)
	initial_soc_file.write(str(rand_soc)+"\n")
initial_soc_file.close()
