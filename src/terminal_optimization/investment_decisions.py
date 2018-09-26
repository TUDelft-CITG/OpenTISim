
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd


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
    
    #print ('Meters of quay added:', quays[0].delta)
    #print ('Current quay length:  ', quays[0].online_length)
    #print ()
    
    return quays


# ### Berth investment decision
# Starting with a single berth and asuming that vessels are distributed equally between all berths, the berth occupancy is calculated. If the occupancy is above the set 'allowable berth occupancy' an extra berth is added and the calculation is iterated. The length of each berth is related to the maximum LOA expected to call at port

# In[2]:


def berth_invest_decision(berths, cranes, berth_object, allowable_berth_occupancy, 
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
    online  = berths[0].online_quantity
    pending = berths[0].pending_quantity
    if online + pending == 0:
        current_occupancy = 100
        pending_occupancy = 100
        berths[0].current_occupancy = 100
        berths[0].pending_occupancy = 100
        invest_decision = 'Invest in berths'
    else:
        if online != 0:
            current_occupancy = berths[0].occupancy_calc(online, cranes, handysize, handymax, panamax, 
                                                         timestep, operational_hours)
        else:
            current_occupancy = 100
        if pending != 0:
            pending_occupancy = berths[0].occupancy_calc(online + pending, cranes, handysize, 
                                                         handymax, panamax, timestep, operational_hours)
        else:
            pending_occupancy = 0
        for i in range (len(berths)):
            berths[i].current_occupancy = current_occupancy
            berths[i].pending_occupancy = pending_occupancy
        if pending_occupancy < allowable_berth_occupancy:
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
    
    #print ('Number of berths added:  ', berths[0].delta)
    #print ('Pending number of berths:', berths[0].pending_quantity)
    #print ('Current number of berths:', berths[0].online_quantity)
    #print ()

    return berths, cranes


# ### Crane investment decision
# In this setup, the number of cranes is solely goverened by the number of berths. The number of cranes per berth is equal to the number of cranes that can work simultaeously on the largest vessel that calls to port during the current timestep. E.g. two cranes per berth in years where handymax is the largest vessel and three cranes per berth in years where panamax is the largest vessel

# In[ ]:


def crane_invest_decision(cranes, berths, cranes_object, year, timestep):
    # at t=0 run initial crane configuration
    if timestep == 0:
        for i in range (4):
            if cranes[i][0].t0_quantity != 0:
                for j in range (int(cranes[i][0].t0_quantity-1)):
                    cranes[i].append(cranes_object[i])
                for j in range (len(cranes[i])):
                    cranes[i][j].online_quantity  = cranes[i][0].t0_quantity
                    cranes[i][j].pending_quantity = 0
                    cranes[i][j].berth = 1
            else:
                cranes[i][0].online_quantity = 0
                cranes[i][0].pending_quantity = 0
                cranes[i][0].berth = 1

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
        if berths[len(berths)-1].online_date == year + cranes[0][0].delivery_time:
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
            gantry_cranes_added.append(berths[index].n_cranes)
        if berths[index].crane_type == 'Harbour cranes':
            harbour_cranes_added.append(berths[index].n_cranes)
        if berths[index].crane_type == 'Mobile cranes':
            mobile_cranes_added.append(berths[index].n_cranes)            
        if berths[index].crane_type == 'Screw unloaders':
            screw_unloaders_added.append(berths[index].n_cranes)
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
    else:
        for i in range (4):
            cranes[i][0].delta = 0

    #print ('Number of berths added:', berths[0].delta)
    #print ('Gantry cranes added:   ', cranes[0][0].delta)
    #print ('Harbour cranes added:  ', cranes[1][0].delta)
    #print ('Mobile cranes added:   ', cranes[2][0].delta)
    #print ('Screw unloaders added: ', cranes[3][0].delta)
    #print ()
    
    return cranes


# ### Storage investment decision
# In this setup, the storage investment is triggered whenever the storage capacity equals 10% of yearly demand. Once triggered, the storage is expanded to accomodate 20% of yearly throughput

# In[ ]:


def storage_invest_decision(storage, storage_object, trigger_throughput_perc, aspired_throughput_perc,
                            storage_type, commodities, year, timestep):
    
    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]
    
    # at t=0 run initial storage configuration
    if timestep == 0:
        for i in range (2):
            if storage[i][0].t0_capacity != 0:
                storage[i][0].online_capacity  = storage[i][0].t0_capacity
                storage[i][0].pending_quantity = 0
            else:
                storage[i][0].online_capacity  = 0
                storage[i][0].pending_capacity = 0
    
    # for each time step, check whether pending assets come online
    online   = []
    pending  = []
    for i in range (2):
        online.append(storage[i][0].online_capacity)
        pending.append(storage[i][0].pending_capacity)
        if pending[i] == 0:
            break
        coming_online = []
        for j in range(len(storage[i])):
            if storage[i][j].online_date == year:
                coming_online.append(storage[i][j].capacity)        
        capacity_coming_online = np.sum(coming_online)
        if capacity_coming_online != 0:
            for j in range(len(storage[i])):
                storage[i][j].online_capacity  = online[i] + capacity_coming_online
                storage[i][j].pending_capacity = 0

    # For each time step, decide whether to invest in storage
    # Calculate total storage capacity
    total_online_capacity  = storage[0][0].online_capacity + storage[1][0].online_capacity
    total_pending_capacity = storage[0][0].pending_capacity + storage[1][0].pending_capacity
    current_capacity       = total_online_capacity + total_pending_capacity
    current_demand         = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    
    # Determine whether to invest
    if current_capacity < current_demand * trigger_throughput_perc/100:
        invest_decision = 'Invest in storage'
    else:
        invest_decision = 'Do not invest in storage'

    # If investments are needed, calculate how much extra capacity should be added
    if invest_decision == 'Invest in storage':
        shortcoming = current_demand * aspired_throughput_perc/100 - current_capacity

        # Silo expansion method
        if storage_type == 'Silos':
            # Calculate requred capacity expansion
            silo_size = storage[0][0].silo_capacity
            added_silo_cap   = int(np.ceil(shortcoming/silo_size)*silo_size)
            added_warehouse_cap = 0
            # Assign purchase date and date on which asset comes online
            if total_online_capacity != 0:
                storage.append(storage_object[0])
            index = len(storage[0])-1
            storage[0][index].purchase_date = year
            storage[0][index].online_date = year + storage[0][0].delivery_time
            storage[0][index].capacity = added_silo_cap
            for i in range (len(storage[0])):
                storage[0][i].pending_capacity = added_silo_cap

        # Warehouse expansion method
        else:
            # Calculate required capacity expansion
            added_silo_cap = 0
            added_warehouse_cap = int(shortcoming)
            # Assign purchase date and date on which asset comes online
            if total_online_capacity != 0:
                storage.append(storage_object[1])
            index = len(storage[1])-1
            storage[1][index].purchase_date = year
            storage[1][index].online_date = year + storage[1][0].delivery_time
            storage[1][index].capacity = added_warehouse_cap
            for i in range (len(storage[1])):
                storage[1][i].pending_capacity = added_warehouse_cap

        storage[0][0].delta = added_silo_cap
        storage[1][0].delta = added_warehouse_cap
    
    else:
        storage[0][0].delta = 0
        storage[1][0].delta = 0

    #print ('Silo capacity added (t):       ', storage[0][0].delta)
    #print ('Current silo capacity (t):     ', storage[0][0].online_capacity)
    #print ('Warehouse capacity added (t):  ', storage[1][0].delta)
    #print ('Current warehouse capacity (t):', storage[1][0].online_capacity)
    #print ()
    
    return storage


# ### Loading station investment decision
# In this setup, it is assumed that the loading station has a utilisation rate of 60%. The loading station investment is triggered whenever the yearly loading capacity equals 80% of yearly demand, taking the utilisation rate into account. Once triggered, the loading rate is expanded to accomodate 120% of yearly throughput.

# In[ ]:


def station_invest_decision(stations, station_object, station_utilisation, trigger_throughput_perc, 
                            aspired_throughput_perc, commodities, year, timestep, operational_hours):

    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]
    
    # at t=0 import loading station class from infrastructure package and run initial laoding station configuration
    if timestep == 0:
        if stations[0].t0_capacity != 0:
            stations[0].online_capacity  = stations[0].t0_capacity
            stations[0].pending_capacity = 0
        else:
            stations[0].online_capacity  = 0
            stations[0].pending_capacity = 0

    # for each time step, check whether pending assets come online
    online   = stations[0].online_capacity
    pending  = stations[0].pending_capacity
    if pending != 0:
        coming_online = []
        for i in range(len(stations)):
            if stations[i].online_date == year:
                coming_online.append(stations[i].pending_capacity)
        capacity_coming_online = np.sum(coming_online)
        if capacity_coming_online != 0:
            for i in range(len(stations)):
                stations[i].online_capacity  = online + capacity_coming_online
                stations[i].pending_capacity = pending - capacity_coming_online
        
    # for each time step, decide whether to invest in storage
    online   = stations[0].online_capacity
    pending  = stations[0].pending_capacity
    current_capacity = online + pending
    current_demand   = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    trigger_capacity = current_demand * trigger_throughput_perc/100/operational_hours/station_utilisation              
    if current_capacity < trigger_capacity:
        invest_decision = 'Invest in loading stations'
    else:
        invest_decision = 'Do not invest in loading stations'

    # if investments are needed, calculate how much extra capacity should be added
    if invest_decision == 'Invest in loading stations':
        # Calculate required capacity expansion
        cap_steps         = stations[0].capacity_steps
        required_capacity = current_demand * aspired_throughput_perc/100/operational_hours/station_utilisation
        shortcoming       = required_capacity - current_capacity
        added_station_cap = int(np.ceil(shortcoming/cap_steps)*cap_steps)

        # Assign purchase date and date on which asset comes online
        if online != 0:
            stations.append(station_object)
        index = len(stations)-1
        stations[index].purchase_date = year
        stations[index].online_date = year + stations[0].delivery_time
        stations[index].capacity = added_station_cap
        for i in range (len(stations)):
            stations[i].pending_capacity = added_station_cap
        stations[0].delta = added_station_cap
        
    else:
        stations[0].delta = 0

    #print ('Loading station capacity added (t/h):  ', stations[0].delta)
    #print ('Current loading station capacity (t/h):', stations[0].online_capacity)
    #print ()
    
    return stations


# ### Conveyor investment decision
# #### Quay conveyor
# In this setup, the quay-side conveyor investment dicision is triggered whenever the the crane investment is triggered. The conveyor capacity is always sufficient to cope with the combined cranes' peak unloading capacity.

# In[ ]:


def quay_conveyor_invest_decision(q_conveyors, cranes, quay_conveyor_object, year, timestep, operational_hours):
    
    # at t=0 run initial conveyor configuration
    if timestep == 0: 
        if q_conveyors[0].t0_capacity != 0:
            q_conveyors[0].online_capacity  = q_conveyor[0].t0_capacity
            q_conveyors[0].pending_capacity = 0
        else:
            q_conveyors[0].online_capacity  = 0
            q_conveyors[0].pending_capacity = 0

    # for each time step, check whether pending assets come online
    online  = q_conveyors[0].online_capacity
    pending = q_conveyors[0].pending_capacity
    if pending != 0:
        coming_online = []
        for i in range(len(q_conveyors)):
            if q_conveyors[i].online_date == year:
                coming_online.append(q_conveyors[i].capacity)
        capacity_coming_online = np.sum(coming_online)
        for i in range(len(q_conveyors)):
            q_conveyors[i].online_capacity  = online + capacity_coming_online
            q_conveyors[i].pending_capacity = pending - capacity_coming_online
        online  = q_conveyors[0].online_capacity
        pending = q_conveyors[0].pending_capacity

    # for each time step, decide whether to invest in quay conveyors
    current_capacity = online + pending 
    current_demand   = int(cranes[0][0].peak_capacity * cranes[0][0].online_quantity +                           cranes[1][0].peak_capacity * cranes[1][0].online_quantity +                           cranes[2][0].peak_capacity * cranes[2][0].online_quantity +                           cranes[3][0].peak_capacity * cranes[3][0].online_quantity)
    pending_demand   = int(cranes[0][0].peak_capacity * cranes[0][0].pending_quantity +                           cranes[1][0].peak_capacity * cranes[1][0].pending_quantity +                           cranes[2][0].peak_capacity * cranes[2][0].pending_quantity +                           cranes[3][0].peak_capacity * cranes[3][0].pending_quantity)             
    if current_capacity < current_demand + pending_demand:
        invest_decision = 'Invest in quay conveyors'
    else:
        invest_decision = 'Do not invest in quay conveyors'

    # if investments are needed, calculate how much extra capacity should be added
    if invest_decision == 'Invest in quay conveyors':
        # Calculate required capacity expansion
        capacity_steps      = q_conveyors[0].capacity_steps
        shortcoming         = current_demand + pending_demand - current_capacity
        added_conveying_cap = int(np.ceil(shortcoming/capacity_steps)*capacity_steps)

        # Assign purchase date and date on which asset comes online
        if online != 0:
            q_conveyors.append(quay_conveyor_object)
        index = len(q_conveyors)-1
        q_conveyors[index].purchase_date = year
        q_conveyors[index].online_date   = year + q_conveyors[0].delivery_time
        q_conveyors[index].capacity = added_conveying_cap
        for i in range (len(q_conveyors)):
            q_conveyors[i].pending_capacity = added_conveying_cap
        q_conveyors[0].delta = added_conveying_cap
    else:
        q_conveyors[0].delta = 0

    #print ('Quay conveyor length (m):             ', q_conveyors[0].length)
    #print ('Quay conveying capacity added (t/h):  ', q_conveyors[0].delta)
    #print ('Current quay conveying capacity (t/h):', q_conveyors[0].online_capacity)
    #print ()
    
    return q_conveyors


# #### 2.7.2 Hinterland conveyor
# In this setup, the hinterland conveyor investment dicision is triggered in order to always live up to loading station demand.

# In[ ]:


def hinterland_conveyor_invest_decision(h_conveyors, stations, hinterland_conveyor_object, year, timestep, operational_hours):
    
    # at t=0 run initial conveyor configuration
    if timestep == 0: 
        if h_conveyors[0].t0_capacity != 0:
            h_conveyors[0].online_capacity  = q_conveyor[0].t0_capacity
            h_conveyors[0].pending_capacity = 0
        else:
            h_conveyors[0].online_capacity  = 0
            h_conveyors[0].pending_capacity = 0

    # for each time step, check whether pending assets come online
    online  = h_conveyors[0].online_capacity
    pending = h_conveyors[0].pending_capacity
    if pending != 0:
        coming_online = []
        for i in range(len(h_conveyors)):
            if h_conveyors[i].online_date == year:
                coming_online.append(h_conveyors[i].capacity)
        capacity_coming_online = np.sum(coming_online)
        for i in range(len(h_conveyors)):
            h_conveyors[i].online_capacity  = online + capacity_coming_online
            h_conveyors[i].pending_capacity = pending - capacity_coming_online
        online  = h_conveyors[0].online_capacity
        pending = h_conveyors[0].pending_capacity

    # for each time step, decide whether to invest in hinterland conveyors
    current_capacity = online + pending 
    current_demand   = stations[0].online_capacity
    pending_demand   = stations[0].pending_capacity         
    if current_capacity < current_demand + pending_demand:
        invest_decision = 'Invest in hinterland conveyors'
    else:
        invest_decision = 'Do not invest in hinterland conveyors'

    # if investments are needed, calculate how much extra capacity should be added
    if invest_decision == 'Invest in quay conveyors':
        # Calculate required capacity expansion
        capacity_steps      = h_conveyors[0].capacity_steps
        shortcoming         = current_demand + pending_demand - current_capacity
        added_conveying_cap = int(np.ceil(shortcoming/capacity_steps)*capacity_steps)

        # Assign purchase date and date on which asset comes online
        if online != 0:
            h_conveyors.append(hinterland_conveyor_object)
        index = len(h_conveyors)-1
        h_conveyors[index].purchase_date = year
        h_conveyors[index].online_date   = year + h_conveyors[0].delivery_time
        h_conveyors[index].capacity = added_conveying_cap
        for i in range (len(h_conveyors)):
            h_conveyors[i].pending_capacity = added_conveying_cap
        h_conveyors[0].delta = added_conveying_cap
    else:
        h_conveyors[0].delta = 0

    #print ('Hinterland conveyor length (m):             ', h_conveyors[0].length)
    #print ('Hinterland conveying capacity added (t/h):  ', h_conveyors[0].delta)
    #print ('Current hinterland conveying capacity (t/h):', h_conveyors[0].online_capacity)
    #print ()
    
    return h_conveyors

