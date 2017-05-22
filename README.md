# Optimal Installation of Wireless Charging Lanes
## How to run the model using pyomo + CPLEX
Choose a model
Edit the model file to for appropiate input graph
Create a dat file mydata.dat using create_data.py
Run pyomo. e.g
`pyomo solve --solve=cplex --solver-options="<your-options>" create_model.py mydata.dat`


