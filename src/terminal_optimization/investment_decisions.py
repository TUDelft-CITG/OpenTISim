
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd


# # 1 Investment triggers
# ### 1.1 Quay wall triggers

# In[ ]:


# Quay length is equal to sum of berth lengths


# ### 1.2 Berth triggers

# In[ ]:


allowable_berth_occupancy = 0.40  # Occupancy percentage which triggers the investment in a new berth


# ### 1.3 Crane triggers

# In[ ]:


# Number of cranes is always equal to sum of maximimum number of cranes per berth


# ### 1.4 Storage triggers

# In[2]:


storage_type            = 'Silos'
trigger_throughput_perc = 10            # Percentage of annual throughput which triggers the investment in a new storage unit
aspired_throughput_perc = 20            # Aspired of annual throughput which is realised due to the new storage unit


# ### 1.5 Loading station triggers

# In[ ]:


station_utilisation     = 0.60         # Loading station utilisation
trigger_throughput_perc = 80           # Percentage of hourly peak demand which triggers the investment in a new loading unit
aspired_throughput_perc = 120          # Aspired percentage of hourly peak demand which is realised due to the new loading unit


# ### 1.6 Conveyor triggers

# In[ ]:


# Conveyor capacity always equals the sum of peak capacities of all the cranes on the quay


# # 2 Investment functions

# ### 2.1 Quay wall investment functions
# Quay length is calculated as the sum of the berth lengths

# In[5]:


def initial_quay_setup(quays):
    
    online = quays[0].t0_length
    pending = 0
    
    quays[0].online_length = online
    quays[0].pending_length = pending
    
    return quays


# In[ ]:


def quay_online_transition(quays, year):
    
    online  = quays[0].online_length
    pending = quays[0].pending_length
    
    if quays[0].pending_length != 0:
        index = len(quays)-1
        if quays[index].online_date == year:
            for i in range (index):
                quays[i].online_lenth = online + pending
                quays[i].pending_lenth = 0
            
    return quays


# In[ ]:


def quay_invest_decision(berths, quays, year):
    if berths[0].pending_quantity != 0:
        index = len(berths)-1
        if berths[index].online_date == year + quays[0].delivery_time:
            return 'Invest in quay'
        else:
            return 'Do not invest in quay'
    else:
        return 'Do not invest in quay'


# In[ ]:


def quay_expansion(quays, quay_object, berths, year):
    
    # Calculate berth lengths
    online  = berths[0].online_quantity
    pending = berths[0].pending_quantity
    berth_lengths    = []
    
    for i in range (online, online + pending):
        berth_lengths.append(berths[i].length)
    
    # Add quay object
    quays.append(quay_object)
    quays[len(quays)-1].purchase_date = year
    quays[len(quays)-1].online_date = year + quays[0].delivery_time
    
    # Refresh pending lengths
    for i in range (len(quays)):
        quays[i].pending_length = np.sum(berth_lengths)
    
    # Register quay length added this timestep
    quays[0].delta = quays[0].pending_length
    
    return quays


# ### 2.2 Berth investment functions
# The number of berths is initially set to one after which the berth occupancy is calculated. If the berth occupancy is higher than the allowable threshold, an extra berth is added

# In[12]:


def initial_berth_setup(berths, cranes, handysize, handymax, panamax, timestep):
    
    online = berths[0].t0_quantity
    pending = 0
    
    for i in range (len(berths)):
        berths[i].online_quantity = online
        berths[i].pending_quantity = pending
        berths[i].remaining_calcs(berths, cranes, handysize, handymax, panamax, timestep)
    
    return berths


# In[ ]:


def berth_online_transition(berths, year):
    
    online  = berths[0].online_quantity
    pending = berths[0].pending_quantity
    
    for i in range (online, online + pending):
        if berths[i].online_date == year:
            for j in range (len(berths)):
                berths[j].online_quantity = (online+1)
                berths[j].pending_quantity = (pending-1)
            
    return berths


# In[13]:


def berth_invest_decision(berths, cranes, handysize, handymax, panamax, timestep, operational_hours):

    number_of_berths = berths[0].online_quantity + berths[0].pending_quantity
    
    if number_of_berths == 0:
        berths[0].current_occupancy = 100
        berths[0].pending_occupancy = 100
        return ['Invest in berths', berths]
    
    else:
        current_occupancy = berths[0].occupancy_calc(berths[0].online_quantity, cranes, handysize, handymax, panamax, 
                                                     timestep, operational_hours)
        pending_occupancy = berths[0].occupancy_calc(berths[0].online_quantity + berths[0].pending_quantity, cranes, handysize, 
                                                     handymax, panamax, timestep, operational_hours)
        for i in range (len(berths)):
            berths[i].current_occupancy = current_occupancy
            berths[i].pending_occupancy = pending_occupancy
    
    if berths[0].pending_occupancy < allowable_berth_occupancy:
        return ['Do not invest in berths', berths]
    else:
        return ['Invest in berths', berths]


# In[ ]:


def berth_expansion(berths, berth_object, cranes, handysize, handymax, panamax, year, timestep, operational_hours):
    
    n_berths = berths[0].online_quantity +  berths[0].pending_quantity
    pending_occupancy = berths[0].pending_occupancy
    
    old_n_berths = n_berths
    while pending_occupancy > allowable_berth_occupancy:
        n_berths = n_berths + 1
        pending_occupancy = berths[0].occupancy_calc(n_berths, cranes, handysize, handymax, panamax, timestep, operational_hours)
        if pending_occupancy < allowable_berth_occupancy:
            break
    new_n_berths = n_berths
            
    for i in range (old_n_berths, new_n_berths):
        if n_berths != 1:
            berths.append(berth_object)
        berths[i].purchase_date = year
        berths[i].online_date = year + berths[i].delivery_time
        berths[i].remaining_calcs(berths, cranes, handysize, handymax, panamax, timestep)
        
    for i in range (len(berths)):
        berths[i].pending_quantity = berths[i].pending_quantity + new_n_berths - old_n_berths
    
    berths[0].delta = new_n_berths - old_n_berths
    
    return berths


# ### 2.3 Crane investment functions
# In this setup, the number of cranes is solely goverened by the number of berths. The number of cranes per berth is equal to the number of cranes that can work simultaeously on the largest vessel that calls to port. E.g. two cranes per berth in years where handymax is the largest vessel and three cranes per berth in years where panamax is the largest vessel

# In[6]:


def initial_crane_setup(cranes):
    
    online = [int(cranes[0][0].t0_quantity), int(cranes[1][0].t0_quantity), 
              int(cranes[2][0].t0_quantity), int(cranes[3][0].t0_quantity)]
    pending = [0,0,0,0]
    
    for i in range (4):
        if online[i] != 0:
            cranes[i].append((online[i]-1)*cranes[i])
            for j in range (online[i]):
                cranes[i][j].online_quantity  = online[i]
                cranes[i][j].pending_quantity = pending[i]
        else:
            cranes[i][0].online_quantity  = 0
            cranes[i][0].pending_quantity = 0
    
    return cranes


# In[ ]:


def crane_online_transition(cranes, year):
    
    online  = []
    pending = []
    
    for i in range (4):
        online.append(cranes[i][0].online_quantity)
        pending.append(cranes[i][0].pending_quantity)
    
    for i in range (4):
        coming_online = []
        for j in range(online[i], online[i] + pending[i]):
            if cranes[i][j].online_date == year:
                cranes[i][j].berth = berths[0].online_quantity
                coming_online.append(1)   
        for j in range (len(cranes[i])):
            cranes[i][j].online_quantity = int(np.sum(coming_online))
            cranes[i][j].pending_quantity = int(cranes[i][j].pending_quantity - np.sum(coming_online))
                
    return cranes


# In[1]:


def crane_invest_decision(cranes, berths, year):
    if berths[0].pending_quantity != 0:
        if berths[len(berths)-1].online_date == year + cranes[0][0].delivery_time + 1:
            return 'Invest in cranes'
        else:
            return 'Do not invest in cranes'
    else:
        return 'Do not invest in cranes'


# In[2]:


def crane_expansion(cranes, cranes_object, berths, year):
    
    # Determine original number of cranes
    online  = []
    pending = []
    
    for i in range (4):
        online.append(cranes[i][0].online_quantity)
        pending.append(cranes[i][0].pending_quantity)
    
    # Required cranes at the berths that are due to come online 
    berth_index = len(berths)-1
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
            if len(cranes[i]) == 1:
                for j in range (cranes_added[i]-1):
                    cranes[i].append(cranes_object[i])
            else:
                for j in range (cranes_added[i]):
                    cranes[i].append(cranes_object[i])
            for j in range (online[i], online[i] + cranes_added[i]):
                cranes[i][j].purchase_date = year
                cranes[i][j].online_date = year + cranes[i][j].delivery_time
            for j in range (len(cranes[i])):
                cranes[i][j].pending_quantity = pending[i]+cranes_added[i]
        
        cranes[i][0].delta = cranes_added[i]
    
    return cranes


# ### 2.4 Storage investment functions
# In this setup, the storage investment is triggered whenever the storage capacity equals 10% of yearly demand. Once triggered, the storage is expanded to accomodate 20% of yearly throughput

# In[1]:


def initial_storage_setup(storage):
    
    online  = [storage[0][0].t0_capacity, storage[1][0].t0_capacity]
    pending = [0,0]
    
    for i in range (2):
        if online[i] != 0:
            storage[i][0].online_capacity  = online[i]
            storage[i][0].pending_quantity = pending[i]
        else:
            storage[i][0].online_capacity  = 0
            storage[i][0].pending_capacity = 0
    
    return storage


# In[ ]:


def storage_online_transition(storage, year):
    
    online   = []
    pending  = []
    
    for i in range (2):
        online.append(storage[i][0].online_capacity)
        pending.append(storage[i][0].pending_capacity)
    
        if pending[i] == 0:
            break
        
        else:
            coming_online = []
            for j in range(len(storage[i])):
                if storage[i][j].online_date == year:
                    coming_online.append(storage[i][j].pending_capacity)        

            capacity_coming_online = np.sum(coming_online)

            if capacity_coming_online != 0:
                for j in range(len(storage[i])):
                    storage[i][j].online_capacity  = online[i] + capacity_coming_online
                    storage[i][j].pending_capacity = 0
            
    return storage


# In[ ]:


def storage_invest_decision(storage, maize, soybean, wheat, timestep):
    
    # Determine current capacity
    online   = []
    pending  = []
    
    for i in range (2):
        online.append(storage[i][0].online_capacity)
        pending.append(storage[i][0].pending_capacity)
    
    total_online_capacity  = np.sum(online)
    total_pending_capacity = np.sum(pending)
    current_demand         = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    
    for i in range (2):
        for j in range(len(storage[i])):
            storage[i][j].total_online_capacity = total_online_capacity
            storage[i][j].total_pending_capacity = total_pending_capacity
            storage[i][j].current_demand = current_demand
            
    # Decide whether current capacity requires further investment
    if total_online_capacity + total_pending_capacity < current_demand * trigger_throughput_perc/100:
        return ['Invest in storage', storage]
    else:
        return ['Do not invest in storage', storage]


# In[7]:


def storage_expansion(storage, year):
    
    # Calculate capacity shortcoming
    current_capacity = storage[0][0].total_online_capacity + storage[1][0].total_online_capacity
    shortcoming      = storage[0][0].current_demand * aspired_throughput_perc/100 - current_capacity
    
    # Silo expansion method
    if storage_type == 'Silos':
        
        # Calculate requred capacity expansion
        silo_size = storage[0][0].silo_capacity
        added_silo_cap   = int(np.ceil(shortcoming/silo_size)*silo_size)
        added_warehouse_cap = 0
        
        # Assign purchase date and date on which asset comes online
        index = len(storage[0])-1
        storage[0][index].purchase_date = year
        storage[0][index].online_date   = year + storage[0][0].delivery_time
        for i in range (len(storage[0])):
            storage[0][i].pending_capacity = added_silo_cap
            
    # Warehouse expansion method
    else:
        
        # Calculate requred capacity expansion
        added_silo_cap = 0
        added_warehouse_cap = int(shortcoming)
        
        # Assign purchase date and date on which asset comes online
        index = len(storage[1])-1
        storage[1][index].purchase_date = year
        storage[1][index].online_date   = year + storage[1][0].delivery_time
        for i in range (len(storage[1])):
            storage[1][i].pending_capacity = added_warehouse_cap
            
    storage[0][0].delta = added_silo_cap
    storage[1][0].delta = added_warehouse_cap
    
    return storage


# ### 2.6 Loading station investment functions
# In this setup, it is assumed that the loading station has a utilisation rate of 60%. The loading station investment is triggered whenever the yearly loading capacity equals 80% of yearly demand, taking the utilisation rate into account. Once triggered, the loading rate is expanded to accomodate 120% of yearly throughput in steps of 300 t/h

# In[2]:


def initial_station_setup(stations):
    
    online  = stations[0].t0_capacity
    pending = 0
    
    if online != 0:
        stations[0].online_capacity  = online
        stations[0].pending_capacity = pending
    else:
        stations[0].online_capacity  = 0
        stations[0].pending_capacity = 0

    return stations


# In[ ]:


def station_online_transition(stations, year):
    
    online   = stations[0].online_capacity
    pending  = stations[0].pending_capacity
    coming_online = []
    
    if pending == 0:
        return stations
    
    else:
        for i in range(len(stations)):
            if stations[i].online_date == year:
                coming_online.append(stations[i].pending_capacity)

        capacity_coming_online = np.sum(coming_online)

        for i in range(len(stations)):
            stations[i].online_capacity  = online + capacity_coming_online
            stations[i].pending_capacity = pending - capacity_coming_online
        return stations


# In[8]:


def station_invest_decision(stations, maize, soybean, wheat, timestep, operational_hours):
    
    online   = stations[0].online_capacity
    pending  = stations[0].pending_capacity

    # Decide whether to invest
    current_capacity = online + pending 
    current_demand   = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    trigger_capacity = current_demand * trigger_throughput_perc/100/operational_hours/station_utilisation
                   
    if current_capacity < trigger_capacity:
        return 'Invest in loading stations'
    else:
        return 'Do not invest in loading stations'


# In[9]:


def station_expansion(stations, maize, soybean, wheat, year, timestep, operational_hours):
    
    online   = stations[0].online_capacity
    pending  = stations[0].pending_capacity
    
    # Calculate required capacity expansion
    cap_steps         = stations[0].capacity_steps
    current_capacity  = online + pending
    current_demand    = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    required_capacity = current_demand * aspired_throughput_perc/100/operational_hours/station_utilisation
    shortcoming       = required_capacity - current_capacity
    added_station_cap = int(np.ceil(shortcoming/cap_steps)*cap_steps)
    
    # Assign purchase date and date on which asset comes online
    index = len(stations)-1
    stations[index].purchase_date = year
    stations[index].online_date   = year + stations[0].delivery_time
    for i in range (len(stations)):
        stations[i].pending_capacity = added_station_cap
        
    stations[0].delta = added_station_cap
    
    return stations


# ### 2.7 Conveyor investment functions
# #### 2.7.1 Quay conveyor
# In this setup, the quay-side conveyor investment dicision is triggered whenever the the crane investment is triggered. The conveyor capacity is always sufficient to cope with the cranes' peak unloading capacity. 

# In[11]:


def initial_conveyor_setup(conveyors):
    
    online  = conveyors[0].t0_capacity
    pending = 0
    
    if online != 0:
        conveyors[0].online_capacity  = online
        conveyors[0].pending_capacity = pending
    else:
        conveyors[0].online_capacity  = 0
        conveyors[0].pending_capacity = 0
    
    return conveyors


# In[ ]:


def conveyor_online_transition(conveyors, year):
    
    online   = conveyors[0].online_capacity
    pending  = conveyors[0].pending_capacity
    coming_online = []
    
    if pending == 0:
        return conveyors
    
    else:
        for i in range(len(conveyors)):
            if conveyors[i].online_date == year:
                coming_online.append(conveyors[i].pending_capacity)

        capacity_coming_online = np.sum(coming_online)

        for i in range(len(conveyors)):
            conveyors[i].online_capacity  = online + capacity_coming_online
            conveyors[i].pending_capacity = pending - capacity_coming_online
        return conveyors


# In[ ]:


def quay_conveyor_invest_decision(q_conveyors, cranes):
    
    online   = q_conveyors[0].online_capacity
    pending  = q_conveyors[0].pending_capacity

    # Decide whether to invest
    current_capacity = online + pending 
    current_demand   = int(cranes[0][0].peak_capacity * cranes[0][0].online_quantity +                           cranes[1][0].peak_capacity * cranes[1][0].online_quantity +                           cranes[2][0].peak_capacity * cranes[2][0].online_quantity +                           cranes[3][0].peak_capacity * cranes[3][0].online_quantity)
    pending_demand   = int(cranes[0][0].peak_capacity * cranes[0][0].pending_quantity +                           cranes[1][0].peak_capacity * cranes[1][0].pending_quantity +                           cranes[2][0].peak_capacity * cranes[2][0].pending_quantity +                           cranes[3][0].peak_capacity * cranes[3][0].pending_quantity)
    
    for i in range (len(q_conveyors)):
        q_conveyors[i].current_demand = current_demand
        q_conveyors[i].pending_demand = pending_demand
                   
    if current_capacity < current_demand + pending_demand:
        return ['Invest in quay conveyors', q_conveyors]
    else:
        return ['Do not invest in quay conveyors', q_conveyors]


# In[ ]:


def quay_conveyor_expansion(q_conveyors, cranes, year):
    
    online   = q_conveyors[0].online_capacity
    pending  = q_conveyors[0].pending_capacity
    
    # Calculate required capacity expansion
    capacity_steps      = q_conveyors[0].capacity_steps
    current_capacity    = online + pending
    current_demand      = q_conveyors[0].current_demand
    pending_demand      = q_conveyors[0].pending_demand
    shortcoming         = current_demand + pending_demand - current_capacity
    added_conveying_cap = int(np.ceil(shortcoming/capacity_steps)*capacity_steps)
    
    # Assign purchase date and date on which asset comes online
    index = len(q_conveyors)-1
    q_conveyors[index].purchase_date = year
    q_conveyors[index].online_date   = year + q_conveyors[0].delivery_time
    for i in range (len(q_conveyors)):
        q_conveyors[i].pending_capacity = added_conveying_cap
        
    q_conveyors[0].delta = added_conveying_cap
    
    return q_conveyors


# #### 2.7.2 Hinterland conveyor
# In this setup, the hinterland conveyor investment dicision is triggered in order always live up to loading station capacity.

# In[ ]:


def hinterland_conveyor_invest_decision(h_conveyors, stations):
    
    online   = h_conveyors[0].online_capacity
    pending  = h_conveyors[0].pending_capacity

    # Decide whether to invest
    current_capacity = online + pending 
    current_demand   = stations[0].online_capacity
    pending_demand   = stations[0].pending_capacity
    
    for i in range (len(h_conveyors)):
        h_conveyors[i].current_demand = current_demand
        h_conveyors[i].pending_demand = pending_demand
                   
    if current_capacity <= current_demand + pending_demand:
        return ['Invest in hinterland conveyors', h_conveyors]
    else:
        return ['Do not invest in hinterland conveyors', h_conveyors]


# In[3]:


def hinterland_conveyor_expansion(h_conveyors, stations, year):
    
    online   = h_conveyors[0].online_capacity
    pending  = h_conveyors[0].pending_capacity
    
    # Calculate required capacity expansion
    capacity_steps      = h_conveyors[0].capacity_steps
    current_capacity    = online + pending
    current_demand      = h_conveyors[0].current_demand
    pending_demand      = h_conveyors[0].pending_demand
    shortcoming         = current_demand + pending_demand - current_capacity
    added_conveying_cap = int(np.ceil(shortcoming/capacity_steps)*capacity_steps)
    
    # Assign purchase date and date on which asset comes online
    index = len(h_conveyors)-1
    h_conveyors[index].purchase_date = year
    h_conveyors[index].online_date   = year + h_conveyors[0].delivery_time
    for i in range (len(h_conveyors)):
        h_conveyors[i].pending_capacity = added_conveying_cap
        
    h_conveyors[0].delta = added_conveying_cap
    
    return h_conveyors


# # Throughput Calculations

# In[ ]:


def quay_throughput(berths, cranes):
    
    if berths[0].online_quantity == 0:
        return 0
    
    quay_throughput = []
    for i in range (len(berths)):
        occupancy = berths[i].current_occupancy/berths[i].online_quantity
        eff_unloading_rate = []
        for j in range (4):
            for k in range (len(cranes[j])):
                if cranes[i][j].berth == i+1:
                    eff_unloading_rate.append(crane[i][j].effective_capacity)
        online_eff_unloading_rate = np.sum(eff_unloading_rate)
        berth[i].throughput = online_eff_unloading_rate * occupancy
        quay_throughput.append(berth[i].throughput)
    return np.sum(quay_throughput)


# In[5]:


def quay_conveyor_throughput():
    pass


# In[ ]:


def storage_throughput():
    pass


# In[ ]:


def hinterland_conveyor_throughput():
    pass


# In[ ]:


def loading_station_throughput():
    pass

