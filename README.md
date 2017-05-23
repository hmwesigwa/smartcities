# Optimal Installation of Wireless Charging Lanes
## How to run the model using `pyomo + CPLEX`
1. Choose a model
2. Edit the model file to for appropiate input graph
3. Create a dat file `mydata.dat` using `create_data.py`
4. Run pyomo. e.g
- `pyomo solve --solve=cplex --solver-options="<your-options>" create_model.py mydata.dat`

### The following models are availble
1. Simple SOC funcition
2. General SOC function
3. Real SOC function

#### Simple SOC funcition
This function assumes that all road segments are equivalent. In this case, an EV that drives along a WCL will have its SOC increase by one unit. If an EV drives along a road segment that does not contain a WCL, the SOC will decrease by 1 unit. The SOC will always be between 0 and k units for a fixed k.

#### General SOC function
All road segments are first prepocessed and classified into m categories for a fixed m such that the SOC will increase and decrease by one unit if a WCL is installed or not installed at on that road segment respectively. 

#### Real SOC function
This model takes a realistic SOC functionn into account. The output of this function is rounded to the nearest k decimal digits where k is a value depedent on the parameter nLayers used in the model. 
