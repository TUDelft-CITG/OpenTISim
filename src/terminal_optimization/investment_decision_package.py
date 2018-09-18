
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd


# # Import general port parameters
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


# # Investment triggers

# ### Quay wall
# Quay length is calculated as the sum of the berth lengths

# In[23]:


def initial_quay_setup(quay, initial_quay_length):
   
    quay.length = initial_quay_length
    
    return quay


# In[ ]:


def quay_expansion(quay, berths):
    
    original_quay_length = quay.length
    
    number_of_berths = berths[0].quantity
    berth_lengths    = []
    
    for i in range (number_of_berths):
        berth_lengths.append(berths[i].length)
    
    quay.length = np.sum(berth_lengths)
    
    new_quay_length = quay.length
    quay_added = new_quay_length - original_quay_length
    
    return [quay, quay_added]


# ### Berths
# The number of berths is initially set to one after which the berth occupancy is calculated. If the berth occupancy is higher than the allowable threshold, an extra berth is added

# In[ ]:


def initial_berth_setup(berths, initial_number_of_berths, crane_type):
    
    berths[0].quantity_calc(initial_number_of_berths)
    for i in range (len(berths)):
        berths[i].crane_type = crane_type
    berths[0].remaining_calcs()
        
    return berths


# In[13]:


def berth_invest_decision(berths):
    
    global allowable_berth_occupancy
    allowable_berth_occupancy = 0.40
        
    # Investment trigger 
    number_of_berths = berths[0].quantity
    
    if number_of_berths == 0:
        return 'Invest in berths'
    
    occupancy = berths[0].occupancy_calc(number_of_berths)
    if occupancy < allowable_berth_occupancy:
        return 'Do not invest in berths'
    else:
        return 'Invest in berths'


# In[18]:


def berth_expansion(berths):
    
    original_number_of_berths = berths[0].quantity
    
    for i in range (max(original_number_of_berths,1), len(berths)+1): # increase nr of berths untill occupancy is satisfactory        number_of_berths = i+1
        occupancy = berths[0].occupancy_calc(i)
        if occupancy < allowable_berth_occupancy:
            berths[0].quantity_calc(i)
            new_number_of_berths = i
            break
    
    berths[0].remaining_calcs()                                        # assign length and depth to each berth
    
    berths_added = new_number_of_berths - original_number_of_berths    # register how many berths were added
    
    return [berths, berths_added]


# ### Crane investment decision
# In this setup, the number of cranes is solely goverened by the number of berths. The number of cranes per berth is equal to the number of cranes that can work simultaeously on the largest vessel that calls to port. E.g. two cranes per berth in years where handymax is the largest vessel and three cranes per berth in years where panamax is the largest vessel

# In[ ]:


def initial_crane_setup(cranes, initial_gantry_cranes, initial_harbour_cranes, initial_mobile_cranes, initial_screw_unloaders):
    
    cranes[0][0].quantity_calc(initial_gantry_cranes)
    cranes[1][0].quantity_calc(initial_harbour_cranes)
    cranes[2][0].quantity_calc(initial_mobile_cranes)
    cranes[3][0].quantity_calc(initial_screw_unloaders)
    
    return cranes


# In[ ]:


def crane_invest_decision(berths):
        
    # Investment trigger 
    number_of_berths = berths[0].quantity
    number_of_cranes = []
    for i in range (number_of_berths):                            # Compute how mucht cranes are required at each berth
        if berths[i].crane_type == 'Gantry cranes':
            number_of_cranes[i,0] = berths[i].n_cranes
        if berths[i].crane_type == 'Harbour cranes':
            number_of_cranes[i,1] = berths[i].n_cranes
        if berths[i].crane_type == 'Mobile cranes':
            number_of_cranes[i,2] = berths[i].n_cranes            
        if berths[i].crane_type == 'Screw unloaders':
            number_of_cranes[i,3] = berths[i].n_cranes
            
    cranes[0][0].quantity_calc(np.sum(number_of_cranes[:,0]))     # Assign the new quantities to each crane type
    cranes[1][0].quantity_calc(np.sum(number_of_cranes[:,1]))
    cranes[2][0].quantity_calc(np.sum(number_of_cranes[:,2]))
    cranes[3][0].quantity_calc(np.sum(number_of_cranes[:,3]))
        
    number_of_cranes = np.sum(number_of_cranes)
    
    if number_of_berths == 0:
        return 'Invest in berths'
    
    occupancy = berths[0].occupancy_calc(number_of_berths)
    if occupancy < allowable_berth_occupancy:
        return 'Do not invest in berths'
    else:
        return 'Invest in berths'


# In[ ]:


def berth_expansion(berths):
    
    original_number_of_berths = berths[0].quantity
    
    for i in range (max(original_number_of_berths,1), len(berths)+1): # increase nr of berths untill occupancy is satisfactory        number_of_berths = i+1
        occupancy = berths[0].occupancy_calc(i)
        if occupancy < allowable_berth_occupancy:
            berths[0].quantity_calc(i)
            new_number_of_berths = i
            break
    
    berths[0].remaining_calcs()                                        # assign length and depth to each berth
    
    berths_added = new_number_of_berths - original_number_of_berths    # register how many berths were added
    
    return [berths, berths_added]

