
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd


# # Import general port parameters
# This imports the 'General Port parameters' from the notebook so that they can be used for calculations within this package

# In[4]:


def import_notebook_parameters():
    
    global year
    global simulation_window
    global start_year
    global timestep
    global operational_hours
    
    year              = parameters.year
    simulation_window = parameters.simulation_window
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


def initial_quay_setup(quays):
   
    quays[0].online_length_calc(initial_quay_length)
    quays[0].pending_length_calc(0)
    
    if initial_quay_length != 0:
        quays[0].quantity_calc(1)
    else:
        quays[0].quantity_calc(0)
    
    return quays


# In[ ]:


def quay_online_transition(quays):
    
    online  = quays[0].online_length
    pending = quays[0].pending_length
    
    if quays[0].pending_length != 0:
        index = quays[0].quantity
        if quays[index].online_date == year:
                quays[index].online_length_calc(quays[index].online_length + quays[index].pending_length)
                quays[index].pending_length_calc(0)
            
    return quays


# In[ ]:


def quay_invest_decision(berths, quays):
    if berths[0].pending_quantity != 0:
        berth_index = (berths[0].online_quantity + berths[0].pending_quantity) - 1
        if berths[berth_index].online_date == year + quays[0].delivery_time:
            return 'Invest in quay'
        else:
            return 'Do not invest in quay'
    else:
        return 'Do not invest in quay'


# In[ ]:


def quay_expansion(quays, berths):
    
    number_of_berths = berths[0].pending_quantity
    berth_lengths    = []
    
    for i in range (berths[0].online_quantity, berths[0].online_quantity + berths[0].pending_quantity):
        berth_lengths.append(berths[i].length)
    
    quays[quays[0].quantity].purchase_date = year
    quays[quays[0].quantity].online_date = year + quays[0].delivery_time
    quays[0].pending_length_calc(np.sum(berth_lengths))
    quays[0].quantity_calc(quays[0].quantity + 1)
    
    quays[0].delta = quays[0].pending_length
    
    return quays


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
    
    berths_added = new_number_of_berths - original_number_of_berths    # register how many berths were added
    
    berths[0].delta = berths_added
    
    return berths


# ### Crane investment decision
# In this setup, the number of cranes is solely goverened by the number of berths. The number of cranes per berth is equal to the number of cranes that can work simultaeously on the largest vessel that calls to port. E.g. two cranes per berth in years where handymax is the largest vessel and three cranes per berth in years where panamax is the largest vessel

# In[ ]:


initial_gantry_cranes   = 0
initial_harbour_cranes  = 0
initial_mobile_cranes   = 0
initial_screw_unloaders = 0


# In[6]:


def initial_crane_setup(cranes):
    
    online = [initial_gantry_cranes, initial_harbour_cranes, initial_mobile_cranes, initial_screw_unloaders]
    pending = [0,0,0,0]
    
    for i in range (4):
        if online[i] != 0:
            for j in range (len(cranes[i])):
                cranes[i][j].online_quantity  = online[i]
                cranes[i][j].pending_quantity = pending[i]
        else:
            for j in range (len(cranes[i])):
                cranes[i][j].online_quantity  = 0
                cranes[i][j].pending_quantity = 0
    
    return cranes


# In[ ]:


def crane_online_transition(cranes):
    
    online  = []
    pending = []
    
    for i in range (4):
        online.append(cranes[i][0].online_quantity)
        pending.append(cranes[i][0].pending_quantity)
    
    for i in range (4):
        coming_online = []
        for j in range(online[i], online[i] + pending[i]):
            if cranes[i][j].online_date == year:
                coming_online.append(1)
            cranes[i][0].online_quantity_calc(online[i] + np.sum(coming_online))
            cranes[i][0].pending_quantity_calc(pending[i] - np.sum(coming_online))
            
    return cranes


# In[ ]:


def crane_invest_decision(cranes, berths):
    if berths[0].pending_quantity != 0:
        berth_index = (berths[0].online_quantity + berths[0].pending_quantity) - 1
        if berths[berth_index].online_date == year + cranes[0][0].delivery_time + 1:
            return 'Invest in cranes'
        else:
            return 'Do not invest in cranes'
    else:
        return 'Do not invest in cranes'


# In[2]:


def crane_expansion(cranes, berths):
    
    # Determine original number of cranes
    online  = []
    pending = []
    
    for i in range (4):
        online.append(cranes[i][0].online_quantity)
        pending.append(cranes[i][0].pending_quantity)
    
    # Required cranes at the berths that are due to come online 
    berth_index = (berths[0].online_quantity + berths[0].pending_quantity) - 1
    gantry_cranes_added   = []
    harbour_cranes_added  = []
    mobile_cranes_added   = []
    screw_unloaders_added = []
    
    if berths[berth_index].crane_type == 'Gantry cranes':
        gantry_cranes_added.append(berths[berth_index].n_cranes)
    if berths[berth_index].crane_type == 'Harbour cranes':
        harbour_cranes_added.append(berths[berth_index].n_cranes)
    if berths[berth_index].crane_type == 'Mobile cranes':
        mobile_cranes_added.append(berths[berth_index].n_cranes)            
    if berths[berth_index].crane_type == 'Screw unloaders':
        screw_unloaders_added.append(berths[berth_index].n_cranes)
    
    cranes_added = [int(np.sum(gantry_cranes_added)), int(np.sum(harbour_cranes_added)),
                    int(np.sum(mobile_cranes_added)), int(np.sum(screw_unloaders_added))]
    
    # Assign purchase dates and dates on which assets come online
    for i in range (4):
        if cranes_added[i] != 0:
            for j in range (online[i], online[i] + cranes_added[i]):
                cranes[i][j].purchase_date = year
                cranes[i][j].online_date = year + cranes[i][j].delivery_time
            for k in range (online[i]+pending[i]+cranes_added[i]):
                cranes[i][k].pending_quantity = pending[i]+cranes_added[i]
        
        cranes[i][0].delta = cranes_added[i]
    
    return cranes


# ### Storage investment decision
# In this setup, the storage investment is triggered whenever the storage capacity equals 10% of yearly demand. Once triggered, the storage is expanded to accomodate 20% of yearly throughput

# In[ ]:


initial_silo_capacity       = 0
initial_warehouse_capacity  = 0
storage_type                = 'Warehouses'
silo_size                   = 6000
trigger_throughput_perc     = 10
aspired_throughput_perc     = 20


# In[1]:


def initial_storage_setup(storage):
    
    online  = [initial_silo_capacity, initial_warehouse_capacity]
    pending = [0,0]
    
    for i in range (2):
        if online[i] != 0:
            for j in range (len(storage[i])):
                storage[i][j].online_capacity  = online[i]
                storage[i][j].pending_quantity = pending[i]
                storage[i][j].quantity         = 1
        else:
            for j in range (len(storage[i])):
                storage[i][j].online_capacity  = 0
                storage[i][j].pending_capacity = 0
                storage[i][j].quantity         = 0
    
    return storage


# In[ ]:


def storage_online_transition(storage):
    
    online   = []
    pending  = []
    quantity = []
    
    for i in range (2):
        online.append(storage[i][0].online_capacity)
        pending.append(storage[i][0].pending_capacity)
        quantity.append(storage[i][0].quantity)
    
    for i in range (2):
        coming_online = []
        
        for j in range(quantity[i]):
            if storage[i][j].online_date == year:
                coming_online.append(storage[i][j].pending_capacity)
                
        capacity_coming_online = np.sum(coming_online)
        
        if capacity_coming_online != 0:
            for j in range(quantity[i]):
                storage[i][j].online_capacity  = online[i] + capacity_coming_online
                storage[i][j].pending_capacity = 0
            
    return storage


# In[ ]:


def storage_invest_decision(storage):
    
    # Determine current capacity
    online   = []
    pending  = []
    quantity = []
    
    for i in range (2):
        online.append(storage[i][0].online_capacity)
        pending.append(storage[i][0].pending_capacity)
        quantity.append(storage[i][0].quantity)
    
    total_online_capacity  = np.sum(online[0]) + np.sum(online[1])
    total_pending_capacity = np.sum(pending[0]) + np.sum(pending[1])
    current_demand         = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    
    for i in range (2):
        for j in range(max(quantity[i],1)):
            storage[i][j].total_online_capacity = total_online_capacity
            storage[i][j].total_pending_capacity = total_pending_capacity
            storage[i][j].current_demand = current_demand
            
    # Decide whether current capacity requires further investment
    if total_online_capacity + total_pending_capacity < current_demand * trigger_throughput_perc/100:
        return ['Invest in storage', storage]
    else:
        return ['Do not invest in storage', storage]


# In[7]:


def storage_expansion(storage):
    
    # Calculate capacity shortcoming
    current_capacity = storage[0][0].total_online_capacity + storage[0][0].total_online_capacity
    shortcoming      = storage[0][0].current_demand * aspired_throughput_perc/100 - current_capacity
    
    # Silo expansion method
    if storage_type == 'Silos':
        
        # Calculate requred capacity expansion
        added_silo_cap   = int(np.ceil(shortcoming/silo_size)*silo_size)
        added_warehouse_cap = 0
        
        # Assign purchase date and date on which asset comes online
        index = storage[0][0].quantity
        storage[0][index].purchase_date = year
        storage[0][index].online_date   = year + storage[0][0].delivery_time
        for i in range (len(storage[0])):
            storage[0][i].quantity = storage[0][i].quantity + 1
            storage[0][i].pending_capacity = added_silo_cap
            
    # Warehouse expansion method
    else:
        
        # Calculate requred capacity expansion
        added_silo_cap = 0
        added_warehouse_cap = int(shortcoming)
        
        # Assign purchase date and date on which asset comes online
        index = storage[0][0].quantity
        storage[1][index].purchase_date = year
        storage[1][index].online_date   = year + storage[1][0].delivery_time
        for i in range (len(storage[1])):
            storage[1][i].quantity = storage[1][i].quantity + 1
            storage[1][i].pending_capacity = added_warehouse_cap
            
    storage[0][0].delta = added_silo_cap
    storage[1][0].delta = added_warehouse_cap
    
    return storage


# ### Loading station investment decision
# In this setup, it is assumed that the loading station has a utilisation rate of 60%. The loading station investment is triggered whenever the yearly loading capacity equals 80% of yearly demand, taking the utilisation rate into account. Once triggered, the loading rate is expanded to accomodate 120% of yearly throughput in steps of 300 t/h

# In[ ]:


initial_station_capacity = 0
station_modular_capacity_steps   = 300
station_utilisation      = 0.60
trigger_throughput_perc  = 80
aspired_throughput_perc  = 20


# In[2]:


def initial_station_setup(stations):
    
    online  = initial_station_capacity
    pending = 0
    
    if online != 0:
        for i in range (len(stations)):
            stations[i].online_capacity  = online
            stations[i].pending_quantity = pending
            stations[i].quantity         = 1
    else:
        for i in range (len(stations)):
            stations[i].online_capacity  = 0
            stations[i].pending_capacity = 0
            stations[i].quantity         = 0
    
    return stations


# In[ ]:


def station_online_transition(stations):
    
    online   = stations[0].online_capacity
    pending  = stations[0].pending_capacity
    quantity = stations[0].quantity
    
    coming_online = []

    for i in range(quantity):
        if stations[i].online_date == year:
            coming_online.append(stations[i].pending_capacity)

    capacity_coming_online = np.sum(coming_online)

    if capacity_coming_online != 0:
        for i in range(quantity):
            stations[i].online_capacity  = online + capacity_coming_online
            stations[i].pending_capacity = 0
            
    return stations


# In[8]:


def station_invest_decision(stations):
    
    online   = stations[0].online_capacity
    pending  = stations[0].pending_capacity
    quantity = stations[0].quantity

    # Decide whether to invest
    current_capacity = online + pending 
    current_demand   = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    trigger_capacity = current_demand * trigger_throughput_perc/100/operational_hours/station_utilisation
                   
    if current_capacity < trigger_capacity:
        return 'Invest in loading stations'
    else:
        return 'Do not invest in loading stations'


# In[9]:


def station_expansion(stations):
    
    online   = stations[0].online_capacity
    pending  = stations[0].pending_capacity
    quantity = stations[0].quantity
    
    # Calculate required capacity expansion
    current_capacity  = online + pending
    current_demand    = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    required_capacity = current_demand * aspired_throughput_perc/100/operational_hours/station_utilisation
    shortcoming       = required_capacity - current_capacity
    added_station_cap = int(np.ceil(shortcoming/station_modular_capacity_steps)*station_modular_capacity_steps)
    
    # Assign purchase date and date on which asset comes online
    stations[quantity].purchase_date = year
    stations[quantity].online_date   = year + stations[0].delivery_time
    for i in range (len(stations)):
        stations[i].quantity = quantity + 1
        stations[i].pending_capacity = added_station_cap
        
    stations[0].delta = added_station_cap
    
    return stations


# ### Conveyor investment decision
# #### Quay conveyor
# In this setup, the quay-side conveyor investment dicision is triggered whenever the the crane investment is triggered. The conveyor capacity is always sufficient to cope with the cranes' peak unloading capacity. It is assumed that each additional conveyor built increases conveying capacity by 400 t/h.

# In[ ]:


initial_quay_conveyor_capacity = 0    # in t/h
quay_conveyor_length           = 500 # in meters
quay_modular_capacity_steps    = 400  # in t/h


# In[11]:


def initial_conveyor_setup(q_conveyors):
    
    online  = initial_quay_conveyor_capacity
    pending = 0
    
    if online != 0:
        for i in range (len(q_conveyors)):
            q_conveyors[i].online_capacity  = online
            q_conveyors[i].pending_quantity = pending
            q_conveyors[i].quantity         = 1
            q_conveyors[i].length           = quay_conveyor_length
    else:
        for i in range (len(q_conveyors)):
            q_conveyors[i].online_capacity  = 0
            q_conveyors[i].pending_capacity = 0
            q_conveyors[i].quantity         = 0
            q_conveyors[i].length           = quay_conveyor_length
    
    return q_conveyors


# In[ ]:


def conveyor_online_transition(q_conveyors):
    
    online   = q_conveyors[0].online_capacity
    pending  = q_conveyors[0].pending_capacity
    quantity = q_conveyors[0].quantity
    
    coming_online = []

    for i in range(quantity):
        if q_conveyors[i].online_date == year:
            coming_online.append(q_conveyors[i].pending_capacity)

    capacity_coming_online = np.sum(coming_online)

    if capacity_coming_online != 0:
        for i in range(quantity):
            q_conveyors[i].online_capacity  = online + capacity_coming_online
            q_conveyors[i].pending_capacity = 0
            
    return q_conveyors


# In[ ]:


def quay_conveyor_invest_decision(q_conveyors, cranes):
    
    online   = q_conveyors[0].online_capacity
    pending  = q_conveyors[0].pending_capacity
    quantity = q_conveyors[0].quantity

    # Decide whether to invest
    current_capacity = online + pending 
    current_demand   = int(cranes[0][0].peak_capacity * cranes[0][0].online_quantity +                           cranes[1][0].peak_capacity * cranes[1][0].online_quantity +                           cranes[2][0].peak_capacity * cranes[2][0].online_quantity +                           cranes[3][0].peak_capacity * cranes[3][0].online_quantity)
    pending_demand   = int(cranes[0][0].peak_capacity * cranes[0][0].pending_quantity +                           cranes[1][0].peak_capacity * cranes[1][0].pending_quantity +                           cranes[2][0].peak_capacity * cranes[2][0].pending_quantity +                           cranes[3][0].peak_capacity * cranes[3][0].pending_quantity)
    
    for i in range (max(quantity, 1)):
        q_conveyors[i].current_demand = current_demand
        q_conveyors[i].pending_demand = pending_demand
                   
    if current_capacity < current_demand + pending_demand:
        return ['Invest in quay conveyors', q_conveyors]
    else:
        return ['Do not invest in quay conveyors', q_conveyors]


# In[ ]:


def quay_conveyor_expansion(q_conveyors, cranes):
    
    online   = q_conveyors[0].online_capacity
    pending  = q_conveyors[0].pending_capacity
    quantity = q_conveyors[0].quantity
    
    # Calculate required capacity expansion
    current_capacity    = online + pending
    current_demand      = q_conveyors[0].current_demand
    pending_demand      = q_conveyors[0].pending_demand
    shortcoming         = current_demand + pending_demand - current_capacity
    added_conveying_cap = int(np.ceil(shortcoming/quay_modular_capacity_steps)*quay_modular_capacity_steps)
    
    # Assign purchase date and date on which asset comes online
    q_conveyors[quantity].purchase_date = year
    q_conveyors[quantity].online_date   = year + q_conveyors[0].delivery_time
    for i in range (len(q_conveyors)):
        q_conveyors[i].quantity = quantity + 1
        q_conveyors[i].pending_capacity = added_conveying_cap
        
    q_conveyors[0].delta = added_conveying_cap
    
    return q_conveyors


# #### 3.2.5.1 Hinterland conveyor
# In this setup, the hinterland conveyor investment dicision is triggered whenever the loading station investment is triggered. The conveyor capacity is always sufficient to cope with the hinterland loading stations' capacity. It is assumed that each additional conveyor built increases conveying capacity by 400 t/h.

# In[3]:


initial_hinterland_conveyor_capacity = 0    # in t/h
hinterland_conveyor_length           = 500 # in meters
hinterland_modular_capacity_steps    = 400  # in t/h


# In[4]:


def initial_hinterland_conveyor_setup(h_conveyors):
    
    online  = initial_hinterland_conveyor_capacity
    pending = 0
    
    if online != 0:
        for i in range (len(h_conveyors)):
            h_conveyors[i].online_capacity  = online
            h_conveyors[i].pending_quantity = pending
            h_conveyors[i].quantity         = 1
            h_conveyors[i].length           = initial_hinterland_conveyor_capacity
    else:
        for i in range (len(h_conveyors)):
            h_conveyors[i].online_capacity  = 0
            h_conveyors[i].pending_capacity = 0
            h_conveyors[i].quantity         = 0
            h_conveyors[i].length           = initial_hinterland_conveyor_capacity
    
    return h_conveyors


# In[ ]:


def hinterland_conveyor_online_transition(h_conveyors):
    
    online   = h_conveyors[0].online_capacity
    pending  = h_conveyors[0].pending_capacity
    quantity = h_conveyors[0].quantity
    
    coming_online = []

    for i in range(quantity):
        if h_conveyors[i].online_date == year:
            coming_online.append(h_conveyors[i].pending_capacity)

    capacity_coming_online = np.sum(coming_online)

    if capacity_coming_online != 0:
        for i in range(quantity):
            h_conveyors[i].online_capacity  = online + capacity_coming_online
            h_conveyors[i].pending_capacity = 0
            
    return h_conveyors


# In[ ]:


def hinterland_conveyor_invest_decision(h_conveyors, stations):
    
    online   = h_conveyors[0].online_capacity
    pending  = h_conveyors[0].pending_capacity
    quantity = h_conveyors[0].quantity

    # Decide whether to invest
    current_capacity = online + pending 
    current_demand   = stations[0].online_capacity
    pending_demand   = stations[0].pending_capacity
    
    for i in range (max(quantity, 1)):
        h_conveyors[i].current_demand = current_demand
        h_conveyors[i].pending_demand = pending_demand
                   
    if current_capacity < current_demand + pending_demand:
        return ['Invest in hinterland conveyors', h_conveyors]
    else:
        return ['Do not invest in hinterland conveyors', h_conveyors]


# In[ ]:


def hinterland_conveyor_expansion(h_conveyors, stations):
    
    online   = h_conveyors[0].online_capacity
    pending  = h_conveyors[0].pending_capacity
    quantity = h_conveyors[0].quantity
    
    # Calculate required capacity expansion
    current_capacity    = online + pending
    current_demand      = h_conveyors[0].current_demand
    pending_demand      = h_conveyors[0].pending_demand
    shortcoming         = current_demand + pending_demand - current_capacity
    added_conveying_cap = int(np.ceil(shortcoming/hinterland_modular_capacity_steps)*hinterland_modular_capacity_steps)
    
    # Assign purchase date and date on which asset comes online
    h_conveyors[quantity].purchase_date = year
    h_conveyors[quantity].online_date   = year + h_conveyors[0].delivery_time
    for i in range (len(h_conveyors)):
        h_conveyors[i].quantity = quantity + 1
        h_conveyors[i].pending_capacity = added_conveying_cap
        
    h_conveyors[0].delta = added_conveying_cap
    
    return h_conveyors


# # Investment functions

# ### Assign purchase date
