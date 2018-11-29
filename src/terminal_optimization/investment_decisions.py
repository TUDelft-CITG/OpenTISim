
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import terminal_optimization.infrastructure as infra


# # 2 Investment functions

# ### 2.1 Quay investment decision
# In this setup, the decision to expand the quay is based on whether berth expansions are plannen or not. The length of the quay is defined as the sum of the length of the berths 

# In[ ]:


def quay_invest_decision(quays, berths, year, timestep):

    # for each time step, check whether pending assets come online
    online_length = []
    offline_length = []
    for i in range(len(quays)):
        if quays[i].online_date <= year:
            online_length.append(quays[i].length)
        if quays[i].online_date > year:
            offline_length.append(quays[i].length)
    for i in range(len(quays)):
        quays[i].online_length = int(np.sum(online_length))
        quays[i].offline_length = int(np.sum(offline_length))

    # for each time step, decide whether to invest in the quay
    if berths[0].offline != 0:
        index = len(berths)-1
        if berths[index].online_date == year + infra.quay_object.delivery_time:
            invest_decision = 'Invest in quay'
        else:
            invest_decision = 'Do not invest in quay'
    else:
        invest_decision = 'Do not invest in quay'

    # if investments are needed, calculate how much quay length should be added
    if invest_decision == 'Invest in quay':
        online_berths  = berths[0].online
        pending_berths = berths[0].offline
        berth_lengths  = []
        for i in range (online_berths, online_berths + pending_berths):
            berth_lengths.append(berths[i].length)
        # Add quay object
        quays.append(infra.quay_wall_class(**infra.quay_data))
        index = len(quays)-1
        quays[index].purchase_date = year
        quays[index].online_date = year + quays[0].delivery_time
        quays[index].length = np.sum(berth_lengths)
        # Refresh pending lengths
        for i in range (len(quays)):
            quays[i].offline_length = np.sum(berth_lengths)
            quays[i].delta = np.sum(berth_lengths)
         
    else:
        for i in range (len(quays)):
            quays[i].delta = 0
    
    return quays


# ### Berth and crane investment decision
# 
# Starting with a single berth and asuming that vessels are distributed equally between all berths, the berth occupancy is calculated by combining the combined effective unloading rate of the cranes. If the occupancy is above the set 'allowable berth occupancy' an extra crane is added and the calculation is iterated. If there are not enough slots to harbour an extra crane, an extra berth is added. The length of each berth is related to the maximum LOA expected to call at port

# In[ ]:


def berth_invest_decision(berths, cranes, vessels, allowable_waiting_time, year, timestep, operational_hours):

    # for each time step, check whether pending berths come online
    online = []
    offline = []
    for i in range(len(berths)):
        if berths[i].online_date <= year:
            online.append(1)
        if berths[i].online_date > year:
            offline.append(1)
    for i in range(len(berths)):
        berths[i].online = int(np.sum(online))
        berths[i].offline = int(np.sum(offline))
    
    # for each time step, check whether pending cranes come online
    for i in range (4):
        online = []
        offline = []
        for j in range(len(cranes[i])):
            if cranes[i][j].online_date <= year:
                online.append(1)
            if cranes[i][j].online_date > year:
                offline.append(1)
        for j in range(len(cranes[i])):
            cranes[i][j].online = int(np.sum(online))
            cranes[i][j].offline = int(np.sum(offline))

    # for each time step, decide whether to invest in the quay side
    if len(berths) == 0:
        invest_decision = 'Invest in berths or cranes'
    else:
        # Determine the unloading capacity of each berth
        berth_service_rate = []
        for i in range (len(berths)):
            service_rate = []
            for j in range(4):
                for k in range(len(cranes[j])):
                    if cranes[j][k].berth == i+1:
                        service_rate.append(cranes[j][k].effective_capacity * cranes[j][k].utilisation)                  
            berth_service_rate.append(int(np.sum(service_rate)))
        total_service_rate = np.sum(berth_service_rate)
        
        # Traffic distribution according to ratio service rate of each berth
        traffic_ratio = []
        for i in range (len(berths)):
            traffic_ratio.append(berth_service_rate[i]/total_service_rate)
            
        # Determine total time that vessels are at each berth
        occupancy = []
        service_times = []
        for i in range (len(berths)):            
            berth_time = []
            for j in range (3):
                calls          = vessels[j].calls[timestep] * traffic_ratio[i] / len(berths)
                service_time   = vessels[j].call_size / berth_service_rate[i]
                mooring_time   = vessels[j].mooring_time
                time_at_berth  = service_time + mooring_time
                berth_time.append(time_at_berth * calls)
            berth_time = np.sum(berth_time)
            service_times.append(service_time)
            occupancy.append(berth_time / operational_hours)
        
        # Determine the waiting time of each vessel type
        waiting_times = []
        waiting_factors = []
        for i in range (len(berths)):    
            factor = berths[0].occupancy_to_waitingfactor(occupancy[i], len(berths))
            vessel_wait_times = []
            for j in range (3):
                calls           = vessels[j].calls[timestep] * traffic_ratio[i]
                service_time    = vessels[j].call_size / berth_service_rate[i]
                individual_wait = service_time * factor
                vessel_wait_times.append(individual_wait)
            waiting_times.append(max(vessel_wait_times))
            waiting_factors.append(factor)
        
        # Decide whether investments are needed
        if max(waiting_factors) < allowable_waiting_time:
            invest_decision = 'Do not invest in berths or cranes'
        else:
            invest_decision = 'Invest in berths or cranes'
        
    # If investments are needed, calculate how much cranes should be added and whether an extra berth should be added
    if invest_decision == 'Invest in berths or cranes':
        berths_added          = []
        gantry_cranes_added   = []
        harbour_cranes_added  = []
        mobile_cranes_added   = []
        screw_unloaders_added = []
        
        if len(berths) == 0:
            berths_added.append(1)
            berths.append(infra.berth_class(**infra.berth_data))
            berths[len(berths)-1].purchase_date = year
            berths[len(berths)-1].online_date = year + berths[0].delivery_time
            berths[len(berths)-1].remaining_calcs(berths, vessels, timestep)
        
        # Add cranes untill berth occupancy is sufficiently reduced
        max_iterations = 10
        iteration = 1
        while iteration < max_iterations:
        
            # Determine how many crane slots are available at each berth
            available_slots = []
            for i in range (len(berths)):
                used_slots = []
                for j in range (4):
                    for k in range (len(cranes[j])):
                        if cranes[j][k].berth == i+1:
                            used_slots.append(1)
                used_slots = np.sum(used_slots)
                available_slots.append(int(berths[i].max_cranes - used_slots))
            if np.sum(available_slots) == 0:
                berths_added.append(1)
                berths.append(infra.berth_class(**infra.berth_data))
                berths[len(berths)-1].purchase_date = year
                berths[len(berths)-1].online_date = year + berths[0].delivery_time
                berths[len(berths)-1].remaining_calcs(berths, vessels, timestep)
                available_slots.append(berths[len(berths)-1].max_cranes)
            
            # If a slot is available, add a crane
            for i in range(len(available_slots)):
                if available_slots[i] != 0:
                    if berths[i].crane_type == 'Gantry cranes':
                        gantry_cranes_added.append(1)
                        cranes[0].append(infra.cyclic_unloader(**infra.gantry_crane_data))
                        cranes[0][len(cranes[0])-1].berth = i+1
                        cranes[0][len(cranes[0])-1].purchase_date = year
                        cranes[0][len(cranes[0])-1].online_date = year + berths[0].delivery_time
                        berths[i].cranes_present.append('Gantry crane')
                    elif berths[i].crane_type == 'Harbour cranes':
                        harbour_cranes_added.append(1)
                        cranes[1].append(infra.cyclic_unloader(**infra.harbour_crane_data))
                        cranes[1][len(cranes[1])-1].berth = i+1
                        cranes[1][len(cranes[1])-1].purchase_date = year
                        cranes[1][len(cranes[1])-1].online_date = year + berths[0].delivery_time
                        berths[i].cranes_present.append('Harbour crane')
                    elif berths[i].crane_type == 'Mobile cranes':
                        mobile_cranes_added.append(1)
                        cranes[2].append(infra.cyclic_unloader(**infra.mobile_crane_data))
                        cranes[2][len(cranes[2])-1].berth = i+1
                        cranes[2][len(cranes[2])-1].purchase_date = year
                        cranes[2][len(cranes[2])-1].online_date = year + berths[0].delivery_time
                        berths[i].cranes_present.append('Mobile crane')
                    elif berths[i].crane_type == 'Screw unloaders':
                        screw_unloaders_added.append(1)
                        cranes[3].append(continuous_unloader(**continuous_screw_data))
                        cranes[3][len(cranes[3])-1].berth = i+1
                        cranes[3][len(cranes[3])-1].purchase_date = year
                        cranes[3][len(cranes[3])-1].online_date = year + berths[0].delivery_time
                        berths[i].cranes_present.append('Screw unloader')
                    
                    available_slots[i] = available_slots[i] - 1
            
            # Determine the new unloading capacity of each berth
            berth_service_rate = []
            for j in range (len(berths)):
                service_rate = []
                for k in range(4):
                    for l in range(len(cranes[k])):
                        if cranes[k][l].berth == j+1:
                            service_rate.append(cranes[k][l].effective_capacity * cranes[k][l].utilisation)                  
                berth_service_rate.append(int(np.sum(service_rate)))
            total_service_rate = np.sum(berth_service_rate)

            # Traffic distribution according to ratio service rate of each berth
            traffic_ratio = []
            for j in range (len(berths)):
                traffic_ratio.append(berth_service_rate[j]/total_service_rate)
                berths[j].traffic_ratio = berth_service_rate[j]/total_service_rate

            # Determine total time that vessels are at each berth
            if berth_service_rate[len(berths)-1] != 0:
                occupancy = []
                for j in range (len(berths)):            
                    berth_time = []
                    for k in range (3):
                        calls          = vessels[k].calls[timestep] * traffic_ratio[j] / len(berths)
                        service_time   = vessels[k].call_size / berth_service_rate[j]
                        mooring_time   = vessels[k].mooring_time
                        time_at_berth  = service_time + mooring_time
                        berth_time.append(time_at_berth * calls)
                    berth_time = np.sum(berth_time)
                    occupancy.append(berth_time / operational_hours)
                    berths[j].occupancy = occupancy[j]

            # Determine the waiting time of each vessel type
            waiting_times = []
            waiting_factors = []
            for i in range (len(berths)):            
                factor = berths[0].occupancy_to_waitingfactor(occupancy[i], len(berths))
                vessel_wait_times = []
                for j in range (3):
                    calls           = vessels[j].calls[timestep] * traffic_ratio[i]
                    service_time    = vessels[j].call_size / berth_service_rate[i]
                    individual_wait = service_time * factor
                    vessel_wait_times.append(individual_wait)
                waiting_times.append(max(vessel_wait_times))
                waiting_factors.append(factor)  
            
            iteration = iteration + 1
            
            if max(waiting_factors) < allowable_waiting_time:
                break
                    
        cranes_added = [int(np.sum(gantry_cranes_added)), int(np.sum(harbour_cranes_added)),
                        int(np.sum(mobile_cranes_added)), int(np.sum(screw_unloaders_added))]
        
        # Evaluate how many berths and cranes haven been added
        online = []
        offline = []
        for i in range(len(berths)):
            berths[i].delta = int(np.sum(berths_added))
            if berths[i].online_date <= year:
                online.append(1)
            if berths[i].online_date > year:
                offline.append(1)
        for i in range(len(berths)):
            berths[i].online = int(np.sum(online))
            berths[i].offline = int(np.sum(offline))
        for i in range (4):
            online = []
            offline = []
            for j in range (len(cranes[i])):
                cranes[i][j].delta = cranes_added[i]
                if cranes[i][j].online_date <= year:
                    online.append(1)
                if cranes[i][j].online_date > year:
                    offline.append(1)
            for j in range (len(cranes[i])):
                cranes[i][j].online = int(np.sum(online))
                cranes[i][j].offline = int(np.sum(offline))
                
    else:
        berths[0].delta = 0
        for i in range (4):
            for j in range (len(cranes[i])):
                cranes[i][j].delta = 0

    return berths, cranes


# ### Storage investment decision
# In this setup, the storage investment is triggered whenever the storage capacity equals 10% of yearly demand. Once triggered, the storage is expanded to accomodate 20% of yearly throughput

# In[ ]:


def storage_invest_decision(storage, trigger_throughput_perc, aspired_throughput_perc, storage_type, commodities, year, timestep):
    
    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]
    
    # for each time step, check whether pending storage comes online
    online = []
    offline = []
    for i in range (2):
        online_capacity = []
        offline_capacity = []
        for j in range(len(storage[i])):
            if storage[i][j].online_date <= year:
                online_capacity.append(storage[i][j].capacity)
            if storage[i][j].online_date > year:
                offline_capacity.append(storage[i][j].capacity) 
        for j in range(len(storage[i])):
            storage[i][j].online  = int(np.sum(online_capacity))
            storage[i][j].offline = int(np.sum(offline_capacity))
        online.append (np.sum(online_capacity))
        offline.append (np.sum(offline_capacity))

    # For each time step, decide whether to invest in storage
    # Calculate total storage capacity
    total_online_capacity  = np.sum(online)
    total_offline_capacity = np.sum(offline)
    current_capacity       = total_online_capacity + total_offline_capacity
    current_demand         = maize.demand[timestep] + soybean.demand[timestep] + wheat.demand[timestep]
    
    # Determine whether to invest
    if current_capacity < current_demand * trigger_throughput_perc:
        invest_decision = 'Invest in storage'
    else:
        invest_decision = 'Do not invest in storage'

    # If investments are needed, calculate how much extra capacity should be added
    if invest_decision == 'Invest in storage':
        shortcoming = current_demand * aspired_throughput_perc - current_capacity

        # Silo expansion method
        if storage_type == 'Silos':
            # Calculate requred capacity expansion
            storage[0].append(infra.storage(**infra.silo_data))
            silo_size = storage[0][len(storage[0])-1].silo_capacity
            added_silo_cap = int(np.ceil(shortcoming/silo_size)*silo_size)
            added_warehouse_cap = 0
            storage[0][len(storage[0])-1].capacity = added_silo_cap
            storage[0][len(storage[0])-1].purchase_date = year
            storage[0][len(storage[0])-1].online_date = year + storage[0][0].delivery_time

        # Warehouse expansion method
        else:
            # Calculate required capacity expansion               
            storage[1].append(infra.storage(**infra.warehouse_data))
            added_silo_cap = 0
            added_warehouse_cap = int(shortcoming)
            added_silo_cap = int(np.ceil(shortcoming/silo_size)*silo_size)
            storage[0][len(storage[0])-1].capacity = added_warehouse_cap
            storage[0][len(storage[0])-1].purchase_date = year
            storage[0][len(storage[0])-1].online_date = year + storage[1][0].delivery_time
        
        for i in range(len(storage[0])):
            storage[0][i].offline = added_silo_cap
            storage[0][i].delta   = added_silo_cap
        for i in range(len(storage[1])):
            storage[1][i].offline = added_warehouse_cap
            storage[1][i].delta   = added_warehouse_cap  
    
    else:
        for i in range (2):
            for j in range (len(storage[i])):
                storage[i][j].delta = 0
    
    return storage


# ### Loading station investment decision
# In this setup, it is assumed that the loading station has a utilisation rate of 60%. The loading station investment is triggered whenever the yearly loading capacity equals 80% of yearly demand, taking the utilisation rate into account. Once triggered, the loading rate is expanded to accomodate 120% of yearly throughput.

# In[ ]:


def station_invest_decision(stations, trains, allowable_waiting_time, commodities, timestep, year, operational_hours):
    
    # Demand 
    demand = []
    for i in range (3):
        demand.append(commodities[i].demand[timestep])
    demand = int(np.sum(demand))

    # Allowable waiting time --> max occupancy --> net loading time --> loading speed * nr of stations 

    # for each time step, check whether pending berths come online
    online = []
    offline = []
    for i in range(len(stations)):
        if stations[i].online_date <= year:
            online.append(1)
        if stations[i].online_date > year:
            offline.append(1)
    for i in range(len(stations)):
        stations[i].online = int(np.sum(online))
        stations[i].offline = int(np.sum(offline))

    # for each time step, decide whether to invest in hinterland loading stations
    if len(stations) == 0:
        invest_decision = 'Invest in stations'
    else:           
        # Determine total time that trains are at each station
        calls           = int(np.ceil(demand / trains.call_size / len(stations)))
        service_time    = trains.call_size / stations[-1].production
        prep_time       = trains.prep_time
        time_at_station = service_time + prep_time
        cumulative_time = time_at_station * calls
        occupancy       = cumulative_time / operational_hours / len(stations)
        waiting_factor  = trains.occupancy_to_waitingfactor(occupancy, len(stations))
        for i in range(len(stations)):
            stations[i].occupancy = occupancy
        if waiting_factor > allowable_waiting_time:
            invest_decision = 'Invest in stations'
        else:
            invest_decision = 'Do not invest in stations'
        
    # If investments are needed, add stations until waiting time is sufficiently reduced
    if invest_decision == 'Invest in stations':
        stations_added = []
        for i in range(5):
            
            # Add station
            stations_added.append(1)
            stations.append(infra.hinterland_station(**infra.hinterland_station_data))
            stations[-1].purchase_date = year
            stations[-1].online_date = year + stations[-1].delivery_time
            
            # Determine total time that trains are at each station
            calls           = int(np.ceil(demand / trains.call_size / len(stations)))
            service_time    = trains.call_size / stations[-1].production
            prep_time       = trains.prep_time
            time_at_station = service_time + prep_time
            cumulative_time = time_at_station * calls
            occupancy       = cumulative_time / operational_hours / len(stations)
            waiting_factor  = trains.occupancy_to_waitingfactor(occupancy, len(stations))
            for i in range(len(stations)):
                stations[i].occupancy = occupancy
            
            if waiting_factor < allowable_waiting_time:
                break

        # Evaluate how many stations have been added
        for i in range(len(stations)):
            stations[i].delta = np.sum(stations_added)
                
    else:
        for i in range(len(stations)):
            stations[i].delta = 0

    return stations, trains


# ### Conveyor investment decision
# #### Quay conveyor
# In this setup, the quay-side conveyor investment dicision is triggered whenever the the crane investment is triggered. The conveyor capacity is always sufficient to cope with the combined cranes' peak unloading capacity.

# In[ ]:


def quay_conveyor_invest_decision(q_conveyors, cranes, year, timestep, operational_hours):

    # For each time step, check whether pending assets come online
    
    online_capacity = []
    offline_capacity = []
    for i in range(len(q_conveyors)):
        if q_conveyors[i].online_date <= year:
            online_capacity.append(q_conveyors[i].capacity)
        if q_conveyors[i].online_date > year:
            offline_capacity.append(q_conveyors[i].capacity)
    for i in range(len(q_conveyors)):
        q_conveyors[i].online = int(np.sum(online_capacity))
        q_conveyors[i].offline = int(np.sum(offline_capacity))

    # for each time step, decide whether to invest in quay conveyors
    online = np.sum(online_capacity)
    pending = np.sum(offline_capacity)
    capacity = online + pending 
    demand = []
    for i in range(4):
        for j in range(len(cranes[i])):
            demand.append(cranes[i][j].peak_capacity)
    demand = np.sum(demand)
    
    if capacity < demand:
        invest_decision = 'Invest in quay conveyors'
    else:
        invest_decision = 'Do not invest in quay conveyors'

    # if investments are needed, calculate how much extra capacity should be added
    if invest_decision == 'Invest in quay conveyors':
        # Calculate required capacity expansion
        q_conveyors.append(infra.conveyor(**infra.quay_conveyor_data))
        index = len(q_conveyors)-1
        capacity_steps = q_conveyors[index].capacity_steps
        shortcoming = demand - capacity
        added_conveying_cap = int(np.ceil(shortcoming/capacity_steps)*capacity_steps)
        q_conveyors[index].purchase_date = year
        q_conveyors[index].online_date = year + q_conveyors[0].delivery_time
        q_conveyors[index].capacity = added_conveying_cap
        for i in range (len(q_conveyors)):
            q_conveyors[i].offline = added_conveying_cap
            q_conveyors[i].delta = added_conveying_cap
    else:
        q_conveyors[0].delta = 0
    
    return q_conveyors


# #### 2.7.2 Hinterland conveyor
# In this setup, the hinterland conveyor investment dicision is triggered in order to always live up to loading station demand.

# In[ ]:


def hinterland_conveyor_invest_decision(h_conveyors, stations, year, timestep, operational_hours):

    # For each time step, check whether pending assets come online
    online_capacity = []
    offline_capacity = []
    for i in range(len(h_conveyors)):
        if h_conveyors[i].online_date <= year:
            online_capacity.append(h_conveyors[i].capacity)
        if h_conveyors[i].online_date > year:
            offline_capacity.append(h_conveyors[i].capacity)
    for i in range(len(h_conveyors)):
        h_conveyors[i].online = int(np.sum(online_capacity))
        h_conveyors[i].offline = int(np.sum(offline_capacity))

    # For each time step, decide whether to invest in hinterland conveyors
    online = np.sum(online_capacity)
    pending = np.sum(offline_capacity)
    capacity = online + pending 
    demand = []
    for i in range(len(stations)):
        if stations[i].online_date <= year:
            demand.append(stations[i].production)
    demand = np.sum(demand)               
    if capacity < demand:
        invest_decision = 'Invest in hinterland conveyors'
    else:
        invest_decision = 'Do not invest in hinterland conveyors'

    # If investments are needed, calculate how much extra capacity should be added
    if invest_decision == 'Invest in hinterland conveyors':
        # Calculate required capacity expansion
        h_conveyors.append(infra.conveyor(**infra.hinterland_conveyor_data))
        capacity_steps      = h_conveyors[0].capacity_steps
        shortcoming         = demand - capacity
        added_conveying_cap = int(np.ceil(shortcoming/capacity_steps)*capacity_steps)
        index = len(h_conveyors)-1
        h_conveyors[index].purchase_date = year
        h_conveyors[index].online_date = year + h_conveyors[0].delivery_time
        h_conveyors[index].capacity = added_conveying_cap
        for i in range (len(h_conveyors)):
            h_conveyors[i].offline = added_conveying_cap
            h_conveyors[i].delta = added_conveying_cap
    else:
        for i in range(len(h_conveyors)):
            h_conveyors[i].delta = 0
    
    return h_conveyors

