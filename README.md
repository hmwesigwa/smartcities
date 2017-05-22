# Optimal Installation of Wireless Charging Lanes
## How to run the model using pyomo + CPLEX
1. Choose a model
2. Edit the model file to for appropiate input graph
3. Create a dat file `mydata.dat` using create_data.py
4. Run pyomo. e.g
- `pyomo solve --solve=cplex --solver-options="<your-options>" create_model.py mydata.dat`


