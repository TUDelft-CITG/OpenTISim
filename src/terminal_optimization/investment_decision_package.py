
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

# In[ ]:


initial_quay_length = 0


# In[5]:


def initial_quay_setup(quay):
   
    quay.online_length = initial_quay_length
    
    return quay


# In[ ]:


def quay_online_transition(quay):
    
    online  = quay.online_length
    pending = quay.pending_length
    
    for i in range (online, online + pending):
        if berths[i].online_date == year:
            berths[i].online_quantity_calc(online+1)
            berths[i].pending_quantity_calc(pending-1)
            
    return berths


# In[ ]:


def quay_invest_decision(berth_invest_decision):
    if berth_invest_decision == 'Invest in berths':
        return 'Invest in quay'
    else:
        return 'Do not invest in quay'


# In[ ]:


def quay_expansion(quay, berths):
    
    number_of_berths = berths[0].pending_quantity
    berth_lengths    = []
    
    for i in range (number_of_berths):
        berth_lengths.append(berths[i].length)
    
    quay.pending_length = np.sum(berth_lengths)
    
    quay.length
    quay_added = new_quay_length - original_quay_length
    
    return [quay, quay_added]


# ### Berths
# The number of berths is initially set to one after which the berth occupancy is calculated. If the berth occupancy is higher than the allowable threshold, an extra berth is added

# In[ ]:


initial_number_of_berths  = 0
crane_type                = 'Mobile cranes'
allowable_berth_occupancy = 0.40


# In[12]:


def initial_berth_setup(berths):
    
    berths[0].online_quantity_calc(initial_number_of_berths)
    berths[0].pending_quantity_calc(0)
    
    for i in range (len(berths)):
        berths[i].crane_type = crane_type
    berths[0].remaining_calcs()
        
    return berths


# In[ ]:


def berth_online_transition(berths):
    
    online  = berths[0].online_quantity
    pending = berths[0].pending_quantity
    
    for i in range (online, online + pending):
        if berths[i].online_date == year:
            berths[i].online_quantity_calc(online+1)
            berths[i].pending_quantity_calc(pending-1)
            
    return berths


# In[13]:


def berth_invest_decision(berths):

    number_of_berths = berths[0].online_quantity +  berths[0].pending_quantity
    
    if number_of_berths == 0:
        return 'Invest in berths'
    
    occupancy = berths[0].occupancy_calc(number_of_berths)
    if occupancy < allowable_berth_occupancy:
        return 'Do not invest in berths'
    else:
        return 'Invest in berths'


# In[ ]:


def berth_expansion(berths):
    
    original_number_of_berths = berths[0].online_quantity +  berths[0].pending_quantity
    
    for i in range (original_number_of_berths, len(berths)): # increase nr of berths untill occupancy is satisfactory        number_of_berths = i+1
        berths[i].remaining_calcs()
        berths[i].purchase_date = year
        berths[i].online_date = year + berths[i].delivery_time
        occupancy = berths[i].occupancy_calc(i+1)
        if occupancy < allowable_berth_occupancy:
            berths[i].pending_quantity_calc(i+1)
            new_number_of_berths = i+1
            break
    print ('new', new_number_of_berths)
    print ('old', original_number_of_berths)
    
    berths_added = new_number_of_berths - original_number_of_berths    # register how many berths were added
    
    return [berths, berths_added]


# ### Crane investment decision
# In this setup, the number of cranes is solely goverened by the number of berths. The number of cranes per berth is equal to the number of cranes that can work simultaeously on the largest vessel that calls to port. E.g. two cranes per berth in years where handymax is the largest vessel and three cranes per berth in years where panamax is the largest vessel

# In[ ]:


initial_gantry_cranes   = 0
initial_harbour_cranes  = 0
initial_mobile_cranes   = 0
initial_screw_unloaders = 0


# In[6]:


def initial_crane_setup(cranes):
    
    cranes[0][0].quantity_calc(initial_gantry_cranes, 'Gantry crane')
    cranes[1][0].quantity_calc(initial_harbour_cranes, 'Harbour crane')
    cranes[2][0].quantity_calc(initial_mobile_cranes, 'Mobile crane')
    cranes[3][0].quantity_calc(initial_screw_unloaders, 'Screw unloader')
    
    for i in range (4):
        if not "quantity" in dir(cranes[i][0]):
            cranes[i][0].quantity = 0
    
    return cranes


# In[ ]:


def crane_invest_decision(berth_invest_decision):
    if berth_invest_decision == 'Invest in berths':
        return 'Invest in cranes'
    else:
        return 'Do not invest in cranes'


# In[2]:


def crane_expansion(cranes, berths, berths_added):
    
    # Determine original number of cranes
    original_number_of_cranes = [cranes[0][0].quantity, cranes[1][0].quantity, cranes[2][0].quantity, cranes[3][0].quantity]
 
    gantry_cranes_added   = []
    harbour_cranes_added  = []
    mobile_cranes_added   = []
    screw_unloaders_added = []
    
    # Required cranes at each berth
    for i in range (berths[0].quantity - berths_added, berths[0].quantity):            
        if berths[i].crane_type == 'Gantry cranes':
            gantry_cranes_added.append(berths[i].n_cranes)
        if berths[i].crane_type == 'Harbour cranes':
            harbour_cranes_added.append(berths[i].n_cranes)
        if berths[i].crane_type == 'Mobile cranes':
            mobile_cranes_added.append(berths[i].n_cranes)            
        if berths[i].crane_type == 'Screw unloaders':
            screw_unloaders_added.append(berths[i].n_cranes)
    
    # Number of cranes that have been added
    gantry_cranes_added   = int(np.sum(gantry_cranes_added))                            
    harbour_cranes_added  = int(np.sum(harbour_cranes_added))
    mobile_cranes_added   = int(np.sum(mobile_cranes_added))
    screw_unloaders_added = int(np.sum(screw_unloaders_added))
    
    # Assign the new quantities
    cranes[0][0].quantity_calc(original_number_of_cranes[0] + gantry_cranes_added, 'Gantry crane')
    cranes[1][0].quantity_calc(original_number_of_cranes[1] + harbour_cranes_added, 'Harbour crane')
    cranes[2][0].quantity_calc(original_number_of_cranes[2] + mobile_cranes_added, 'Mobile crane')
    cranes[3][0].quantity_calc(original_number_of_cranes[3] + screw_unloaders_added, 'Screw unloader')
    
    # Cranes can be bought later than berth is purchased
    delay_purchase = berths[0].delivery_time - cranes[0][0].delivery_time                     
    
    # Assign purchase dates and date on which asset comes online
    assign_purchase_date(cranes[0], original_number_of_cranes[0], gantry_cranes_added, delay_purchase)  
    assign_purchase_date(cranes[1], original_number_of_cranes[1], harbour_cranes_added, delay_purchase)     
    assign_purchase_date(cranes[2], original_number_of_cranes[2], mobile_cranes_added, delay_purchase)
    assign_purchase_date(cranes[3], original_number_of_cranes[3], screw_unloaders_added, delay_purchase)
    
    return [cranes, gantry_cranes_added, harbour_cranes_added, mobile_cranes_added, screw_unloaders_added]


# ### Storage investment decision
# In this setup, the storage investment is triggered whenever the storage capacity equals 10% of yearly demand. Once triggered, the storage is expanded to accomodate 20% of yearly throughput

# In[ ]:


initial_silo_capacity       = 0
initial_warehouse_capacity  = 0
storage_type                = 'Silos'
silo_size                   = 6000
trigger_throughput_perc     = 10
aspired_throughput_perc     = 20


# In[4]:


def initial_storage_setup(storage):
    
    if initial_silo_capacity != 0:
        storage[0][0].quantity = 1
    else:
        storage[0][0].quantity = 0
    
    if initial_warehouse_capacity != 0:
        storage[1][0].quantity = 1
    else:
        storage[1][0].quantity = 0
         
    storage[0][0].capacity = initial_silo_capacity
    storage[1][0].capacity =initial_warehouse_capacity
    
    return storage


# In[ ]:


def storage_invest_decision(storage):
    
    # Determine current overall capacity 
    silo_groups = storage[0][0].quantity
    warehouse_groups = storage[1][0].quantity
        
    if silo_groups != 0 or warehouse_groups != 0:
        silo_cap = []
        warehouse_cap = []
        for i in range (silo_groups):
            silo_cap.append(storage[0][i].capacity)
        for i in range (warehouse_groups):
            warehouse_cap.append(storage[1][i].capacity)
        storage[0][0].overall_capacity_calc(int(np.sum(silo_cap), silo_groups, 'Silos'))
        storage[1][0].overall_capacity_calc(int(np.sum(warehouse_cap), warehouse_groups, 'Warehouses'))

    else:
        storage[0][0].overall_capacity = 0
        storage[1][0].overall_capacity = 0
                
    # Decide whether to invest
    current_cap = storage[0][0].overall_capacity + storage[1][0].overall_capacity
    current_demand = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    
    if current_cap < trigger_throughput_perc/100 * current_demand:
        return ['Invest in storage', storage]
    else:
        return ['Do not invest in storage', storage]


# In[7]:


def storage_expansion(storage):

    # Demand in current timestep
    maize_demand   = maize.demand[timestep]
    soybean_demand = soybean.demand[timestep]
    wheat_demand   = wheat.demand[timestep]
    total_demand   = maize_demand + soybean_demand + wheat_demand
    
    # Silo expansion method
    if storage_type == 'Silos':
        
        # Calculate requred capacity expansion
        current_capacity = storage[0][0].overall_capacity + storage[1][0].overall_capacity
        shortcoming      = total_demand*aspired_throughput_perc/100 - current_capacity
        added_silo_cap   = int(np.ceil(shortcoming/silo_size)*silo_size)
        added_warehouse_cap = 0
        
        # Assign purchase dates and date on which asset comes online
        number_of_silo_groups = storage[0][0].quantity
        storage[0][number_of_silo_groups].capacity = added_silo_cap
        storage[0][number_of_silo_groups].purchase_date = year
        storage[0][number_of_silo_groups].online_date   = year + storage[0][0].delivery_time
        storage[0][0].quantity_calc(storage[0][0].quantity + 1, 'Silos')
        storage[0][0].overall_capacity_calc(storage[0][0].overall_capacity + added_silo_cap, storage[0][0].quantity, 'Silos')
        
    # Warehouse expansion method
    else:
        # Calculate required capacity expansion
        current_capacity    = storage[0][0].overall_capacity
        shortcoming         = total_demand*aspired_throughput_perc/100 - current_capacity
        added_warehouse_cap = int(shortcoming)
        added_silo_cap      = 0
        
        # Assign purchase dates and date on which asset comes online
        number_of_warehouse_groups = storage[1][0].quantity
        storage[1][number_of_warehouse_groups].capacity = added_warehouse_cap
        storage[1][number_of_warehouse_groups].purchase_date = year
        storage[1][number_of_warehouse_groups].online_date   = year + storage[1][0].delivery_time
        storage[1][0].quantity_calc(storage[1][0].quantity + 1, 'Warehouses')
        storage[1][0].overall_capacity_calc(storage[1][0].overall_capacity + added_warehouse_cap, storage[1][0].quantity, 'Warehouses')
    
    return [storage, added_silo_cap, added_warehouse_cap]


# ### Loading station investment decision
# In this setup, it is assumed that the loading station has a utilisation rate of 60%. The loading station investment is triggered whenever the yearly loading capacity equals 80% of yearly demand, taking the utilisation rate into account. Once triggered, the loading rate is expanded to accomodate 120% of yearly throughput in steps of 300 t/h

# In[ ]:


initial_station_capacity = 0
modular_capacity_steps   = 300
station_utilisation      = 0.60
trigger_throughput_perc  = 80
aspired_throughput_perc  = 20


# In[ ]:


def initial_station_setup(stations):
    
    if initial_station_capacity != 0:
        stations[0].quantity_calc(1)
    else:
        stations[0].quantity_calc(0)
        
    stations[0].capacity_calc(initial_station_capacity)

    return stations


# In[8]:


def station_invest_decision(stations):
    
    # Determine current overall capacity 
    number_of_stations = stations[0].quantity
        
    if number_of_stations != 0:
        station_cap = []
        for i in range (number_of_stations):
            station_cap.append(station[i].capacity)
        station[0].overall_capacity_calc(int(np.sum(station_cap)))

    else:
        stations[0].overall_capacity_calc(0)         

    # Decide whether to invest
    current_cap = stations[0].overall_capacity
    utilisation = station_utilisation
    current_demand = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    required_capacity = current_demand*trigger_throughput_perc/100/operational_hours
    
    if current_cap < required_capacity:
        return ['Invest in loading stations', stations]
    else:
        return ['Do not invest in loading stations', stations]


# In[9]:


def station_expansion(stations):

    # Demand in current timestep
    maize_demand   = maize.demand[timestep]
    soybean_demand = soybean.demand[timestep]
    wheat_demand   = wheat.demand[timestep]
    total_demand   = maize_demand + soybean_demand + wheat_demand

    # Calculate requred capacity expansion
    current_capacity  = stations[0].overall_capacity
    hourly_demand     = total_demand/operational_hours/station_utilisation
    shortcoming       = hourly_demand * trigger_throughput_perc/100 - current_capacity
    added_station_cap = int(np.ceil(shortcoming/modular_capacity_steps)*modular_capacity_steps)

    # Assign purchase date and date on which asset comes online
    stations[stations[0].quantity].capacity = added_station_cap
    stations[stations[0].quantity].purchase_date = year
    stations[stations[0].quantity].online_date   = year + stations[0].delivery_time
    stations[0].quantity_calc(stations[0].quantity + 1)
    stations[0].overall_capacity_calc(stations[0].overall_capacity + added_station_cap)
    
    return [stations, added_station_cap]


# ### Conveyor investment decision
# #### Quay conveyor
# In this setup, the quay-side conveyor investment dicision is triggered whenever the the crane investment is triggered. The conveyor capacity is always sufficient to cope with the cranes' peak unloading capacity. It is assumed that each additional conveyor built increases conveying capacity by 400 t/h.

# In[ ]:


initial_quay_conveyor_capacity = 0    # in t/h
quay_conveyor_length           = 1000 # in meters
modular_capacity_steps         = 400  # in t/h


# In[11]:


def initial_quay_conveyor_setup(q_conveyors):
    
    q_conveyors[0].capacity = initial_quay_conveyor_capacity
    
    if initial_quay_conveyor_capacity != 0:
        q_conveyors[0].quantity = 1
    else:
        q_conveyors[0].quantity = 0
         
    for i in range (len(q_conveyors)):
        q_conveyors[i].length = quay_conveyor_length
    
    return q_conveyors


# In[ ]:


def quay_conveyor_invest_decision(q_conveyors, cranes):
    
    # Determine current overall capacity 
    n_conveyors = q_conveyors[0].quantity
        
    if n_conveyors != 0:
        conveyor_cap = []
        for i in range (n_conveyors):
            conveyor_cap.append(q_conveyors[i].capacity)
        q_conveyors[0].overall_capacity_calc(int(np.sum(conveyor_cap), n_conveyors, 'Quay'))

    else:
        q_conveyors[0].overall_capacity = 0
                
    # Decide whether to invest
    current_cap = q_conveyors[0].overall_capacity
    current_demand = int(cranes[0][0].peak_capacity * cranes[0][0].quantity +                         cranes[1][0].peak_capacity * cranes[1][0].quantity +                         cranes[2][0].peak_capacity * cranes[2][0].quantity +                         cranes[3][0].peak_capacity * cranes[3][0].quantity)
    
    if current_cap < current_demand:
        return ['Invest in quay conveyors', q_conveyors]
    else:
        return ['Do not invest in quay conveyors', q_conveyors]


# In[ ]:


def quay_conveyor_expansion(q_conveyors, cranes):

    # Demand in current timestep
    current_demand = int(cranes[0][0].peak_capacity * cranes[0][0].quantity +                         cranes[1][0].peak_capacity * cranes[1][0].quantity +                         cranes[2][0].peak_capacity * cranes[2][0].quantity +                         cranes[3][0].peak_capacity * cranes[3][0].quantity)
        
    # Calculate required capacity expansion
    current_capacity    = q_conveyors[0].overall_capacity
    shortcoming         = current_demand - current_capacity
    added_conveying_cap = int(np.ceil(shortcoming/modular_capacity_steps)*modular_capacity_steps)

    # Assign purchase date and date on which asset comes online
    n_conveyors = q_conveyors[0].quantity
    q_conveyors[n_conveyors].capacity = added_conveying_cap
    q_conveyors[n_conveyors].purchase_date = year
    q_conveyors[n_conveyors].online_date = year + q_conveyors[0].delivery_time
    q_conveyors[0].quantity_calc(n_conveyors + 1, 'Quay')
    q_conveyors[0].overall_capacity_calc(q_conveyors[0].overall_capacity + added_conveying_cap, q_conveyors[0].quantity, 'Quay')
        
    return [q_conveyors, added_conveying_cap]


# # Investment functions

# ### Assign purchase date

# In[ ]:


# When assets are expanded, the new instances get branded with a purchase date and a date on which they come online
def assign_purchase_date(asset, originial_quantity, added_quantity, delay_purchase):
    for i in range (originial_quantity, originial_quantity + added_quantity):
        asset[i].purchase_date = year + delay_purchase
        asset[i].online_date   = asset[i].purchase_date + asset[i].delivery_time

