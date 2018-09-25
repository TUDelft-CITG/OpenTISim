
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

# ### 2.1 Quay investment decision
# In this setup, the decision to expand the quay is based on whether berth expansions are plannen or not. The length of the quay is defined as the sum of the length of the berths 

# In[ ]:


def quay_invest_decision(quays, berths, quay_object, year, timestep):

    # at t=0 run initial quay configuration
    if timestep == 0:
        quays[0].online_length = quays[0].t0_length
        quays[0].pending_length = 0

    # for each time step, check whether pending assets come online
    online  = quays[0].online_length
    pending = quays[0].pending_length
    if pending != 0:
        coming_online = []
        for i in range(len(quays)):
            if quays[i].online_date == year:
                coming_online.append(quays[i].length)
        capacity_coming_online = np.sum(coming_online)
        for i in range(len(quays)):
            quays[i].online_length  = online + capacity_coming_online
            quays[i].pending_length = pending - capacity_coming_online

    # for each time step, decide whether to invest in the quay
    if berths[0].pending_quantity != 0:
        index = len(berths)-1
        if berths[index].online_date == year + quays[0].delivery_time:
            invest_decision = 'Invest in quay'
        else:
            invest_decision = 'Do not invest in quay'

    # if investments are needed, calculate how much quay length should be added
    if invest_decision == 'Invest in quay':
        online_berths  = berths[0].online_quantity
        pending_berths = berths[0].pending_quantity
        berth_lengths  = []
        for i in range (online_berths, online_berths + pending_berths):
            berth_lengths.append(berths[i].length)
        # Add quay object
        quays.append(quay_object)
        index = len(quays)-1
        quays[index].purchase_date = year
        quays[index].online_date = year + quays[0].delivery_time
        quays[index].length = np.sum(berth_lengths)
        # Refresh pending lengths
        for i in range (len(quays)):
            quays[i].pending_length = np.sum(berth_lengths)
        # Register quay length added this timestep
        quays[0].delta = quays[0].pending_length
    else:
        quays[0].delta = 0
    
    print ('Meters of quay added: ', quays[0].delta)
    print ('Current quay length:  ', quays[0].online_length)
    print ()
    
    return quays


# ### Berth investment decision
# Starting with a single berth and asuming that vessels are distributed equally between all berths, the berth occupancy is calculated. If the occupancy is above the set 'allowable berth occupancy' an extra berth is added and the calculation is iterated. The length of each berth is related to the maximum LOA expected to call at port

# In[2]:


def berth_invest_decision(berths, cranes, berth_object, cranes_object, allowable_berth_occupancy, 
                          vessels, year, timestep, operational_hours):
    
    handysize = vessels[0]
    handymax  = vessels[1]
    panamax   = vessels[2]
    
    # at t=0 run initial berth configuration
    if timestep == 0:
        berths[0].online_quantity = berths[0].t0_quantity
        berths[0].pending_quantity = 0
        berths[0].remaining_calcs(berths, cranes, handysize, handymax, panamax, timestep)

    # for each time step, check whether pending assets come online
    online  = berths[0].online_quantity
    pending = berths[0].pending_quantity
    for i in range (online, online + pending):
        if berths[i].online_date == year:
            for j in range (len(berths)):
                berths[j].online_quantity = (online+1)
                berths[j].pending_quantity = (pending-1)

    # for each time step, decide whether to invest in berths
    if online + pending == 0:
        current_occupancy = 100
        pending_occupancy = 100
        invest_decision = 'Invest in berths'
    else:
        current_occupancy = berths[0].occupancy_calc(berths[0].online_quantity, cranes, handysize, handymax, panamax, 
                                                     timestep, operational_hours)
        pending_occupancy = berths[0].occupancy_calc(berths[0].online_quantity + berths[0].pending_quantity, cranes, handysize, 
                                                     handymax, panamax, timestep, operational_hours)
        for i in range (len(berths)):
            berths[i].current_occupancy = current_occupancy
            berths[i].pending_occupancy = pending_occupancy
        if berths[0].pending_occupancy < allowable_berth_occupancy:
            invest_decision = 'Do not invest in berths'
        else:
            invest_decision = 'Invest in berths'

    # if investments are needed, calculate how much berths should be added
    if invest_decision == 'Invest in berths':
        n_berths = online + pending
        old_n_berths = n_berths
        while pending_occupancy > allowable_berth_occupancy:
            n_berths = n_berths + 1
            pending_occupancy = berths[0].occupancy_calc(n_berths, cranes, handysize, handymax, panamax, 
                                                         timestep, operational_hours)
            if pending_occupancy < allowable_berth_occupancy:
                break
        new_n_berths = n_berths
        for i in range (old_n_berths, new_n_berths):
            if n_berths != 1:
                berths.append(berth_object)
            berths[i].purchase_date = year
            berths[i].online_date   = year + berths[i].delivery_time
            berths[i].remaining_calcs(berths, cranes, handysize, handymax, panamax, timestep)
        added_berths = new_n_berths - old_n_berths
        for i in range (len(berths)):
            berths[i].pending_quantity = berths[i].pending_quantity + added_berths
        berths[0].delta = added_berths
    else:
        berths[0].delta = 0
    
    print ('Number of berths added:  ', berths[0].delta)
    print ('Pending number of berths:', berths[0].pending_quantity)
    print ('Current number of berths:', berths[0].online_quantity)
    print ()

    return berths, cranes


# ### 3.2.3 Crane investment decision
# In this setup, the number of cranes is solely goverened by the number of berths. The number of cranes per berth is equal to the number of cranes that can work simultaeously on the largest vessel that calls to port during the current timestep. E.g. two cranes per berth in years where handymax is the largest vessel and three cranes per berth in years where panamax is the largest vessel

# In[6]:


def initial_crane_setup(cranes):
    

    
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


# In[ ]:


def crane_invest_decision(
    # at t=0 run initial crane configuration
    if timestep == 0:
        for i in range (4):
            if cranes[i][0].t0_quantity != 0:
                for j in range (int(cranes[i][0].t0_quantity-1)):
                    cranes[i].append(cranes_object[i])
                for j in range (len(cranes[i])):
                    cranes[i][j].online_quantity  = cranes[i][0].t0_quantity
                    cranes[i][j].pending_quantity = 0
            else:
                cranes[i][0].online_quantity = 0
                cranes[i][0].pending_quantity = 0

    # for each time step, check whether pending assets come online
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

    # for each time step, decide whether to invest in the cranes
        if berths[0].pending_quantity != 0:
            if berths[len(berths)-1].online_date == year + cranes[0][0].delivery_time + 1:
                invest_decision = 'Invest in cranes'
            else:
                invest_decision = 'Do not invest in cranes'
        else:
            invest_decision = 'Do not invest in cranes'

    # if investments are needed, calculate how much cranes should be added
    if invest_decision == 'Invest in cranes':
        # Required cranes at the berths because berths are coming online 
        index = len(berths)-1
        gantry_cranes_added   = []
        harbour_cranes_added  = []
        mobile_cranes_added   = []
        screw_unloaders_added = []
        if berths[index].crane_type == 'Gantry cranes':
            gantry_cranes_added.append(berths[berth_index].n_cranes)
        if berths[index].crane_type == 'Harbour cranes':
            harbour_cranes_added.append(berths[berth_index].n_cranes)
        if berths[index].crane_type == 'Mobile cranes':
            mobile_cranes_added.append(berths[berth_index].n_cranes)            
        if berths[index].crane_type == 'Screw unloaders':
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












        cranes = invest.crane_expansion(cranes, cranes_object, berths, year)
    else:
        for i in range (4):
            cranes[i][0].delta = 0

    print ('Number of berths added:', berths[0].delta)
    print ('Gantry cranes added:   ', cranes[0][0].delta)
    print ('Harbour cranes added:  ', cranes[1][0].delta)
    print ('Mobile cranes added:   ', cranes[2][0].delta)
    print ('Screw unloaders added: ', cranes[3][0].delta)


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
        storage[0][index].capacity = added_silo_cap
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
        storage[1][index].capacity = added_warehouse_cap
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
                coming_online.append(conveyors[i].capacity)

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
    q_conveyors[index].capacity = added_conveying_cap
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
    h_conveyors[index].capacity = added_conveying_cap
    for i in range (len(h_conveyors)):
        h_conveyors[i].pending_capacity = added_conveying_cap
        
    h_conveyors[0].delta = added_conveying_cap
    
    return h_conveyors

