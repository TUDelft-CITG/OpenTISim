
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd


# # Import from notebook

# ### Import general port parameters
# This imports the 'General Port parameters' from the notebook so that they can be used for calculations within this package

# In[4]:


def import_notebook_parameters():
    
    global year
    global start_year
    global timestep
    global operational_hours
    
    year              = parameters.year
    start_year        = parameters.start_year
    timestep          = parameters.timestep
    operational_hours = parameters.operational_hours
    
    return


# ### Create notebook affiliated classes
# This creates the classes that are linked to data located within the notebook
# - Commodity characteristics at current timestep

# In[ ]:


def import_notebook_classes():
    
    global commodities
    
    class commodity_class():
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.maize_demand   = maize.demand[timestep]
            self.soybean_demand = soybean.demand[timestep]
            self.wheat_demand   = wheat.demand[timestep]
            self.demand         = self.maize_demand + self.soybean_demand + self.wheat_demand
    commodities = commodity_class()


# # Export to infrastructure package

# In[7]:


import terminal_optimization.infrastructure_package as infra

def export_infrastructure_package():
    infra.parameters = parameters
    infra.maize      = maize
    infra.soybean    = soybean
    infra.wheat      = wheat
    infra.handysize  = handysize
    infra.handymax   = handymax
    infra.panamax    = panamax
    infra.import_notebook_parameters()
    infra.import_notebook_classes()


# # Investment triggers

# ### Quay wall
# Quay length is calculated as the sum of the berth lengths

# In[ ]:


def quay_wall_length_calc():
    global quay
    quay = infra.quay
    
    n_berths = berths[0].quantity
    berth_lengths = []
    
    for i in range (n_berths):
        berth_lengths.append(berths[i].length)
    
    quay.length = np.sum(berth_lengths)


# ### Berths
# The number of berths is initially set to one after which the berth occupancy is calculated. If the berth occupancy is higher than the allowable threshold, an extra berth is added

# In[11]:


def number_of_berths_calc():
    global berths
    berths = infra.berths
    
    # Investment trigger 
    allowable_berth_occupancy = 0.40

    for i in range(1,1+len(berths)):
        berths[0].occupancy_calc(i)
        if berths[0].occupancy < allowable_berth_occupancy:
            berths[0].quantity_calc(i)
            break
    
    # Execute remaining berth calcs
    berths[0].remaining_calcs()


# In[17]:


def berth_invest_decision():
    global berths
    berths = infra.berths
    
    # Investment trigger 
    allowable_berth_occupancy = 0.04
    current_quantity  = 1
    occupancy         = berths[0].occupancy_calc(current_quantity)
    
    if occupancy < allowable_berth_occupancy:
        return False
    else:
        return True


# In[15]:


if 5 < 10:
    print ('True!!!')
else:
    print ('False!!!')  

