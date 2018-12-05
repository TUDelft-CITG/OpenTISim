
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import terminal_optimization.infrastructure as infra


# # 2 Investment functions

# ### 2.1 Quay investment decision
# In this setup, the decision to expand the quay is based on whether berth expansions are plannen or not. The length of the quay is defined as the sum of the length of the berths 

# In[2]:


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
    online_length = int(np.sum(online_length))

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
            
    for i in range(len(quays)):
        # Register berth characteristics under the berth instance
        matrix = np.zeros(shape=(1, 4))
        # Year
        matrix[-1,0] = int(round(year))
        # Length
        if online_length:
            matrix[-1,1] = int(round(online_length))
        else:
            matrix[-1,1] = 0
        # Depth
        matrix[-1,1] = int(round(quays[i].depth))
        # Freeboard 
        matrix[-1,2] = int(round(quays[i].freeboard))
        # Translate to dataframe
        df = pd.DataFrame(matrix, columns=['Year', 'Quay length', 'Berth depth', 'Freeboard'])
        # Register under vessel class
        if 'info' in dir(quays[i]):
            quays[i].info = quays[i].info.append(df)
        if 'info' not in dir(quays[i]):
            quays[i].info = df
    
    return quays


# ### Berth and crane investment decision
# 
# Starting with a single berth and asuming that vessels are distributed equally between all berths, the berth occupancy is calculated by combining the combined effective unloading rate of the cranes. If the occupancy is above the set 'allowable berth occupancy' an extra crane is added and the calculation is iterated. If there are not enough slots to harbour an extra crane, an extra berth is added. The length of each berth is related to the maximum LOA expected to call at port

# In[3]:


def berth_invest_decision(berths, cranes, commodities, vessels, allowable_waiting_factor, year, timestep, operational_hours):
    
    # Calculate demand and resulting number of vessel calls
    demand = commodities[0].demand[len(commodities[0].historic) + timestep]

    for i in range (3):
        if i == 0:
            percentage = commodities[0].handysize_perc/100
        if i == 1:
            percentage = commodities[0].handymax_perc/100
        if i == 2:
            percentage = commodities[0].panamax_perc/100  
        vessels[i].n_calls = demand * percentage / vessels[i].call_size
    
    # for each time step, check whether pending berths come online
    online = []
    offline = []
    for i in range(len(berths)):
        if berths[i].online_date <= year:
            online.append(1)
        if berths[i].online_date > year:
            offline.append(1)
    online_berths = int(np.sum(online))
    offline_berths = int(np.sum(offline))
    for i in range(len(berths)):
        berths[i].online = online_berths
        berths[i].offline = offline_berths
    
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
            
    # Determine the unloading capacity of each berth (including upcoming berths)
    pending_berth_service_rate = []
    for i in range (len(berths)):
        service_rate = []
        for j in range(4):
            for k in range(len(cranes[j])):
                if cranes[j][k].berth == i+1:
                    service_rate.append(cranes[j][k].effective_capacity)                  
        if service_rate:
            pending_berth_service_rate.append(int(np.sum(service_rate)))
    if pending_berth_service_rate:
        total_service_rate = np.sum(pending_berth_service_rate)

    # Traffic distribution according to ratio service rate of each berth
    traffic_ratio = []
    if pending_berth_service_rate:
        for i in range (len(pending_berth_service_rate)):
            traffic_ratio.append(pending_berth_service_rate[i]/total_service_rate)
    else:
        traffic_ratio = 0

    # Determine total time that vessels are at each berth
    pending_occupancy = []
    for i in range (len(pending_berth_service_rate)):            
        berth_time = []
        for j in range (3):
            calls          = vessels[j].n_calls * traffic_ratio[i]
            service_time   = vessels[j].call_size / pending_berth_service_rate[i]
            mooring_time   = vessels[j].mooring_time
            time_at_berth  = service_time + mooring_time
            berth_time.append(time_at_berth * calls)
        berth_time = np.sum(berth_time)
        pending_occupancy.append(berth_time / operational_hours)

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

    # Determine and register new berth characteristics                   
    for i in range (len(berths)):
        if i < len(pending_berth_service_rate):
            berth_occupancy   = pending_occupancy[i]
            eff_unloading_cap = pending_berth_service_rate[i]
            waiting_factor    = berths[i].occupancy_to_waitingfactor(berth_occupancy, len(pending_berth_service_rate))
        else:
            berth_occupancy   = 0
            eff_unloading_cap = 0
            waiting_factor    = 0
        slots_available   = available_slots[i]

        # Register berth characteristics under the berth class
        matrix = np.zeros(shape=(1, 8))
        # Year
        matrix[-1,0] = int(year)
        # Commodity demand
        matrix[-1,1] = int(demand)
        # Capcity
        if online_berths == 0:
            matrix[-1,2] = 0
        if online_berths != 0:
            matrix[-1,2] = int(eff_unloading_cap * operational_hours * berths[0].waitingfactor_to_occupancy(allowable_waiting_factor, online_berths))
        # Occupancy
        matrix[-1,3] = round(berth_occupancy,2)
        # Effective unloading capacity
        matrix[-1,4] = int(eff_unloading_cap)
        # Waiting factor
        matrix[-1,5] = round(waiting_factor,2)
        # Crane slots available
        matrix[-1,6] = slots_available
        # Number of berths
        matrix[-1,7] = len(berths)
        # Translate to dataframe
        df = pd.DataFrame(matrix, columns=['Year', 'Commodity demand', 'Capacity', 'Occupancy', 'Eff unloading capacity', 'Waiting factor', 'Available crane slots', 'Nr of berths'])
        # Register under berth instance
        if 'info' in dir(berths[i]):
            if int(berths[i].info[-1:]['Year']) == year:
                berths[i].info[-1:].update(df)
            else:
                berths[i].info = berths[i].info.append(df, sort=False)
        if 'info' not in dir(berths[i]):
            berths[i].info = df  
            
    waiting_factors = []
    for i in range (len(berths)):
        waiting_factors.append(int(100*berths[i].info[-1:]['Waiting factor']))
    if waiting_factors:
        max_waiting_factor = max(waiting_factors)/100
            
    # for each time step, decide whether to invest in the quay side
    if len(berths) == 0 or max_waiting_factor > allowable_waiting_factor:
        invest_decision = 'Invest in berths or cranes'
    else:
        invest_decision = 'Do not invest in berths or cranes'
    
    # If investments are needed, calculate how much cranes should be added and whether an extra berth should be added
    berths_added          = []
    gantry_cranes_added   = []
    harbour_cranes_added  = []
    mobile_cranes_added   = []
    screw_unloaders_added = []
    
    if invest_decision == 'Invest in berths or cranes':
                
        # Add cranes untill berth occupancy is sufficiently reduced
        max_iterations = 10
        iteration = 1
        while iteration < max_iterations:
            
            #If there are no berths present or there are no more available crane slots, add a berth
            available_slots = []
            for i in range (len(berths)):
                available_slots.append(int(berths[i].info[-1:]['Available crane slots']))
            if np.sum(available_slots) == 0:
                berths_added.append(1)
                berths.append(infra.berth_class(**infra.berth_data))
                berths[-1].purchase_date = year
                berths[-1].online_date = year + berths[0].delivery_time
                berths[-1].remaining_calcs(berths, vessels, timestep)
            
            # Determine the unloading capacity of each berth (including upcoming berths)
            pending_berth_service_rate = []
            for i in range (len(berths)):
                service_rate = []
                for j in range(4):
                    for k in range(len(cranes[j])):
                        if cranes[j][k].berth == i+1:
                            service_rate.append(cranes[j][k].effective_capacity)                  
                if service_rate:
                    pending_berth_service_rate.append(int(np.sum(service_rate)))
            if pending_berth_service_rate:
                total_service_rate = np.sum(pending_berth_service_rate)

            # Traffic distribution according to ratio service rate of each berth
            traffic_ratio = []
            if pending_berth_service_rate:
                for i in range (len(pending_berth_service_rate)):
                    traffic_ratio.append(pending_berth_service_rate[i]/total_service_rate)
            else:
                traffic_ratio = 0

            # Determine total time that vessels are at each berth
            pending_occupancy = []
            for i in range (len(pending_berth_service_rate)):            
                berth_time = []
                if pending_berth_service_rate:
                    for j in range (3):
                        calls          = vessels[j].n_calls * traffic_ratio[i]
                        service_time   = vessels[j].call_size / pending_berth_service_rate[i]
                        mooring_time   = vessels[j].mooring_time
                        time_at_berth  = service_time + mooring_time
                        berth_time.append(time_at_berth * calls)
                    berth_time = np.sum(berth_time)
                    pending_occupancy.append(berth_time / operational_hours)
                else:
                    pending_occupancy.append(0)

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

            # Determine and register new berth characteristics                   
            for i in range (len(berths)):
                if i < len(pending_berth_service_rate):
                    berth_occupancy   = pending_occupancy[i]
                    eff_unloading_cap = pending_berth_service_rate[i]
                    waiting_factor    = berths[i].occupancy_to_waitingfactor(berth_occupancy, len(pending_berth_service_rate))
                else:
                    berth_occupancy   = 0
                    eff_unloading_cap = 0
                    waiting_factor    = 0
                slots_available   = available_slots[i]

                # Register berth characteristics under the berth class
                sort=False
                matrix = np.zeros(shape=(1, 7))
                # Year
                matrix[-1,0] = int(year)
                # Commodity demand
                matrix[-1,1] = int(demand)
                # Capcity
                if online_berths == 0:
                    matrix[-1,2] = 0
                if online_berths != 0:
                    matrix[-1,2] = int(eff_unloading_cap * operational_hours * berths[0].waitingfactor_to_occupancy(allowable_waiting_factor, online_berths))
                # Occupancy
                matrix[-1,3] = round(berth_occupancy,2)
                # Effective unloading capacity
                matrix[-1,4] = int(eff_unloading_cap)
                # Waiting factor
                matrix[-1,5] = round(waiting_factor,2)
                # Crane slots available
                matrix[-1,6] = slots_available
                # Translate to dataframe
                df = pd.DataFrame(matrix, columns=['Year', 'Commodity demand', 'Capacity', 'Occupancy', 'Eff unloading capacity', 'Waiting factor', 'Available crane slots'])
                # Register under berth instance
                if 'info' in dir(berths[i]):
                    if int(berths[i].info[-1:]['Year']) == year:
                        berths[i].info = berths[i].info.iloc[:, ::-1]
                        berths[i].info[-1:].update(df)
                    else:
                        berths[i].info = berths[i].info.append(df, sort=False)
                if 'info' not in dir(berths[i]):
                    berths[i].info = df
            
            # If a slot is available, add a crane
            available_slots = []
            for i in range (len(berths)):
                available_slots.append(int(berths[i].info[-1:]['Available crane slots']))
            
            for i in range(len(available_slots)):
                if int(available_slots[i]) != 0:
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
            
            # Determine the new unloading capacity of each berth (including upcoming berths)
            pending_berth_service_rate = []
            for i in range (len(berths)):
                service_rate = []
                for j in range(4):
                    for k in range(len(cranes[j])):
                        if cranes[j][k].berth == i+1:
                            service_rate.append(cranes[j][k].effective_capacity)                  
                pending_berth_service_rate.append(int(np.sum(service_rate)))
            total_service_rate = np.sum(pending_berth_service_rate)

            # Traffic distribution according to ratio service rate of each berth
            traffic_ratio = []
            if pending_berth_service_rate:
                for i in range (len(pending_berth_service_rate)):
                    traffic_ratio.append(pending_berth_service_rate[i]/total_service_rate)
            else:
                traffic_ratio = 0

            # Determine total time that vessels are at each berth
            pending_occupancy = []
            for i in range (len(berths)):            
                berth_time = []
                if pending_berth_service_rate:
                    for j in range (3):
                        calls          = vessels[j].n_calls * traffic_ratio[i]
                        service_time   = vessels[j].call_size / pending_berth_service_rate[i]
                        mooring_time   = vessels[j].mooring_time
                        time_at_berth  = service_time + mooring_time
                        berth_time.append(time_at_berth * calls)
                    berth_time = np.sum(berth_time)
                    pending_occupancy.append(berth_time / operational_hours)
                else:
                     pending_occupancy.append(0)

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

            # Determine and register new berth characteristics                   
            for i in range (len(berths)):    
                berth_occupancy   = pending_occupancy[i]
                if pending_berth_service_rate:
                    eff_unloading_cap = pending_berth_service_rate[i]
                else:
                    eff_unloading_cap = 0
                waiting_factor    = berths[i].occupancy_to_waitingfactor(berth_occupancy, len(berths))
                slots_available   = available_slots[i]
                max_occupancy     = berths[0].occupancy_to_waitingfactor(berth_occupancy, len(berths))
                
                # Register berth characteristics under the berth instance
                sort=False
                matrix = np.zeros(shape=(1, 7))
                # Year
                matrix[-1,0] = int(year)
                # Commodity demand
                matrix[-1,1] = int(demand)
                # Capcity
                matrix[-1,2] = 0
                # Occupancy
                matrix[-1,3] = round(berth_occupancy,2)
                # Effective unloading capacity
                matrix[-1,4] = int(eff_unloading_cap)
                # Waiting factor
                matrix[-1,5] = round(waiting_factor,2)
                # Crane slots available
                matrix[-1,6] = slots_available
                # Translate to dataframe
                df = pd.DataFrame(matrix, columns=['Year', 'Commodity demand', 'Capacity', 'Occupancy', 'Eff unloading capacity', 'Waiting factor', 'Available crane slots'])
                # Register under vessel class
                if 'info' in dir(berths[i]):
                    if int(berths[i].info[-1:]['Year']) == year:
                        berths[i].info = berths[i].info.iloc[:, ::-1]
                        berths[i].info[-1:].update(df)
                    else:
                        berths[i].info = berths[i].info.append(df, sort=False)
                if 'info' not in dir(berths[i]):
                    berths[i].info = df  

            iteration = iteration + 1

            waiting_factors = []
            for i in range (len(berths)):
                waiting_factors.append(int(100*berths[i].info[-1:]['Waiting factor']))
            max_waiting_factor = max(waiting_factors)/100
                    
            if max_waiting_factor < allowable_waiting_factor:
                break
    
    # Once performance trigger is satisfied, redefine occupancy using only existing online assets
    # Determine the unloading capacity of each online berth
    online_berth_service_rate = []
    for i in range (online_berths):
        service_rate = []
        for j in range(4):
            for k in range(len(cranes[j])):
                if cranes[j][k].berth == i+1 and cranes[j][k].online_date <= year:
                    service_rate.append(cranes[j][k].effective_capacity)                  
        online_berth_service_rate.append(int(np.sum(service_rate)))
    total_service_rate = np.sum(online_berth_service_rate)

    # Traffic distribution according to ratio service rate of each berth
    traffic_ratio = []
    for i in range (online_berths):
        traffic_ratio.append(online_berth_service_rate[i]/total_service_rate)

    # Determine total time that vessels are at each berth
    occupancy = []
    for i in range (online_berths):            
        berth_time = []
        for j in range (3):
            calls          = vessels[j].n_calls * traffic_ratio[i]
            service_time   = vessels[j].call_size / online_berth_service_rate[i]
            mooring_time   = vessels[j].mooring_time
            time_at_berth  = service_time + mooring_time
            berth_time.append(time_at_berth * calls)
        berth_time = np.sum(berth_time)
        occupancy.append(berth_time / operational_hours)

    # Determine and register new berth characteristics                   
    for i in range (len(berths)):
        if berths[i].online_date <= year:
            berth_occupancy   = occupancy[i]
            eff_unloading_cap = online_berth_service_rate[i]
            waiting_factor    = berths[0].occupancy_to_waitingfactor(berth_occupancy, online_berths)
            slots_available   = available_slots[i]
            capacity          = int(eff_unloading_cap * operational_hours * berths[0].waitingfactor_to_occupancy(allowable_waiting_factor, online_berths))
        if berths[i].online_date > year:
            berth_occupancy   = 0
            eff_unloading_cap = 0
            waiting_factor    = 0
            slots_available   = available_slots[i]
            capacity          = 0

        # Register berth characteristics under the berth instance
        sort=False
        matrix = np.zeros(shape=(1, 7))
        # Year
        matrix[-1,0] = int(round(year))
        # Commodity demand
        matrix[-1,1] = int(round(demand))
        # Capcity
        matrix[-1,2] = int(round(capacity))
        # Occupancy
        matrix[-1,3] = round(berth_occupancy,2)
        # Effective unloading capacity
        matrix[-1,4] = int(round(eff_unloading_cap))
        # Waiting factor
        matrix[-1,5] = round(waiting_factor,2)
        # Crane slots available
        matrix[-1,6] = round(slots_available)
        # Translate to dataframe
        df = pd.DataFrame(matrix, columns=['Year', 'Commodity demand', 'Capacity', 'Occupancy', 'Eff unloading capacity', 'Waiting factor', 'Available crane slots'])
        # Register under vessel class
        if 'info' in dir(berths[i]):
            if int(berths[i].info[-1:]['Year']) == year:
                berths[i].info = berths[i].info.iloc[:, ::-1]
                berths[i].info[-1:].update(df)
            else:
                berths[i].info = berths[i].info.append(df, sort=False)
        if 'info' not in dir(berths[i]):
            berths[i].info = df
                
        cranes_added = [int(np.sum(gantry_cranes_added)), int(np.sum(harbour_cranes_added)),
                        int(np.sum(mobile_cranes_added)), int(np.sum(screw_unloaders_added))]        
        
        # Evaluate how many berths and cranes haven been added
        for i in range(len(berths)):
            berths[i].delta = int(np.sum(berths_added))
        for i in range (4):
            for j in range (len(cranes[i])):
                cranes[i][j].delta = cranes_added[i]
                
        online = []
        offline = []
        for i in range(len(berths)):
            if berths[i].online_date <= year:
                online.append(1)
            if berths[i].online_date > year:
                offline.append(1)
        online_berths = int(np.sum(online))
        for i in range(len(berths)):
            berths[i].online = online_berths
            berths[i].offline = int(np.sum(offline))
                
    else:
        berths[0].delta = 0
        for i in range (4):
            for j in range (len(cranes[i])):
                cranes[i][j].delta = 0

    return berths, cranes


# ### Storage investment decision
# In this setup, the storage investment is triggered whenever the storage capacity equals 10% of yearly demand. Once triggered, the storage is expanded to accomodate 20% of yearly throughput

# In[4]:


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
                
    for i in range(2):
        for j in range(len(storage[i])):
            # Register berth characteristics under the berth instance
            matrix = np.zeros(shape=(1, 5))
            # Year
            matrix[-1,0] = int(round(year))
            # Commodity demand
            matrix[-1,1] = int(round(current_demand))
            # Storage
            if storage[i][j].online_date <= year:
                matrix[-1,2] = int(round(total_online_capacity))
            else:
                matrix[-1,2] = 0
            # Capacity
            if storage[i][j].online_date <= year:
                matrix[-1,3] = int(round(total_online_capacity/0.05))
            else:
                matrix[-1,3] = 0
            # Utilization
            if matrix[-1,3]:
                matrix[-1,4] = round(matrix[-1,1]/matrix[-1,3],2)
            else:
                matrix[-1,4] = 0
            # Translate to dataframe
            df = pd.DataFrame(matrix, columns=['Year', 'Commodity demand', 'Storage', 'Capacity', 'Utilization'])
            # Register under vessel class
            if 'info' in dir(storage[i][j]):
                storage[i][j].info = storage[i][j].info.append(df)
            if 'info' not in dir(storage[i]):
                storage[i][j].info = df
    
    return storage


# ### Loading station investment decision
# In this setup, it is assumed that the loading station has a utilisation rate of 60%. The loading station investment is triggered whenever the yearly loading capacity equals 80% of yearly demand, taking the utilisation rate into account. Once triggered, the loading rate is expanded to accomodate 120% of yearly throughput.

# In[5]:


def station_invest_decision(stations, trains, allowable_waiting_factor, commodities, timestep, year, operational_hours):
    
    # Calculate demand and resulting number of vessel calls
    demand = commodities[0].demand[len(commodities[0].historic) + timestep]
    trains.calls = int(np.ceil(demand / trains.call_size))
    
    # for each time step, check whether pending stations come online
    online = []
    offline = []
    for i in range(len(stations)):
        if stations[i].online_date <= year:
            online.append(1)
        if stations[i].online_date > year:
            offline.append(1)
    online_stations = int(np.sum(online))
    offline_stations = int(np.sum(offline))
            
    # Determine the unloading capacity of each berth (including upcoming stations)
    pending_berth_service_rate = []
    for i in range (len(stations)):
        pending_berth_service_rate.append(stations[i].production)

    # Traffic distribution according to ratio service rate of each station
    traffic_ratio = []
    if pending_berth_service_rate:
        for i in range (len(pending_berth_service_rate)):
            traffic_ratio.append(1/len(pending_berth_service_rate))
    else:
        traffic_ratio = 0
 
    # Determine total time that trains are at each berth
    pending_occupancy = []
    for i in range (len(pending_berth_service_rate)):            
        calls            = trains.calls / len(stations)
        service_time     = trains.call_size / stations[i].production
        prep_time        = trains.prep_time
        time_at_station  = service_time + prep_time
        cumulative_time  = time_at_station * calls
        pending_occupancy.append(cumulative_time / operational_hours)

    # Determine and register new berth characteristics                   
    for i in range (len(stations)):
        if i < len(pending_berth_service_rate):
            demand         = int(round(demand))
            capacity       = int(round(operational_hours * stations[i].production * trains.waitingfactor_to_occupancy(allowable_waiting_factor, len(pending_berth_service_rate))))
            occupancy      = round(pending_occupancy[i],2)
            loading_rate   = int(round(pending_berth_service_rate[i]))
            waiting_factor = round(trains.occupancy_to_waitingfactor(occupancy, len(stations)),2)
            n_stations     = int(round(len(pending_berth_service_rate)))
        else:
            demand         = int(round(demand))
            capacity       = 0
            occupancy      = 0
            loading_rate   = 0
            waiting_factor = 0
            n_stations     = int(round(len(pending_berth_service_rate)))

        # Register berth characteristics under the berth class
        matrix = np.zeros(shape=(1, 7))
        # Year
        matrix[-1,0] = int(round(year))
        # Commodity demand
        matrix[-1,1] = demand
        # Capacity
        matrix[-1,2] = capacity
        # Occupancy
        matrix[-1,3] = occupancy
        # Effective loading capacity
        matrix[-1,4] = loading_rate
        # Waiting factor
        matrix[-1,5] = waiting_factor
        # Number of stations
        matrix[-1,6] = n_stations
        # Translate to dataframe
        df = pd.DataFrame(matrix, columns=['Year', 'Commodity demand', 'Total yearly loading capacity', 'Occupancy', 'Loading capacity', 'Waiting factor', 'Nr of stations'])
        # Register under berth instance
        if 'info' in dir(stations[i]):
            if int(stations[i].info[-1:]['Year']) == year:
                stations[i].info[-1:].update(df)
            else:
                stations[i].info = stations[i].info.append(df, sort=False)
        if 'info' not in dir(stations[i]):
            stations[i].info = df  
            
    waiting_factors = []
    for i in range (len(stations)):
        waiting_factors.append(int(100*stations[i].info[-1:]['Waiting factor']))
    if waiting_factors:
        max_waiting_factor = max(waiting_factors)/100
            
    # for each time step, decide whether to invest in stations
    if len(stations) == 0 or max_waiting_factor > allowable_waiting_factor:
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
            
            # Determine the unloading capacity of each berth (including upcoming stations)
            pending_berth_service_rate = []
            for i in range (len(stations)):
                pending_berth_service_rate.append(stations[i].production)

            # Traffic distribution according to ratio service rate of each station
            traffic_ratio = []
            if pending_berth_service_rate:
                for i in range (len(pending_berth_service_rate)):
                    traffic_ratio.append(1/len(pending_berth_service_rate))

            # Determine total time that trains are at each berth
            pending_occupancy = []
            for i in range (len(pending_berth_service_rate)):            
                calls            = trains.calls / len(stations)
                service_time     = trains.call_size / stations[i].production
                prep_time        = trains.prep_time
                time_at_station  = service_time + prep_time
                cumulative_time  = time_at_station * calls
                pending_occupancy.append(cumulative_time / operational_hours)

            # Determine and register new berth characteristics                   
            for i in range (len(stations)):
                
                demand         = int(round(demand))
                capacity       = int(round(operational_hours * stations[i].production * trains.waitingfactor_to_occupancy(allowable_waiting_factor, len(pending_berth_service_rate))))
                occupancy      = round(pending_occupancy[i],2)
                loading_rate   = int(round(pending_berth_service_rate[i]))
                waiting_factor = round(trains.occupancy_to_waitingfactor(occupancy, len(stations)),2)
                n_stations     = int(round(len(pending_berth_service_rate)))

                # Register berth characteristics under the berth class
                matrix = np.zeros(shape=(1, 7))
                # Year
                matrix[-1,0] = int(round(year))
                # Commodity demand
                matrix[-1,1] = demand
                # Capacity
                matrix[-1,2] = capacity
                # Occupancy
                matrix[-1,3] = occupancy
                # Effective loading capacity
                matrix[-1,4] = loading_rate
                # Waiting factor
                matrix[-1,5] = waiting_factor
                # Number of stations
                matrix[-1,6] = n_stations
                # Translate to dataframe
                df = pd.DataFrame(matrix, columns=['Year', 'Commodity demand', 'Total yearly loading capacity', 'Occupancy', 'Loading capacity', 'Waiting factor', 'Nr of stations'])
                # Register under berth instance
                if 'info' in dir(stations[i]):
                    if int(stations[i].info[-1:]['Year']) == year:
                        stations[i].info[-1:].update(df)
                    else:
                        stations[i].info = stations[i].info.append(df, sort=False)
                if 'info' not in dir(stations[i]):
                    stations[i].info = df  

            waiting_factors = []
            for i in range (len(stations)):
                waiting_factors.append(int(100*stations[i].info[-1:]['Waiting factor']))
            if waiting_factors:
                max_waiting_factor = max(waiting_factors)/100

            # for each time step, decide whether to invest in stations
            if max_waiting_factor < allowable_waiting_factor:
                break
            
        # Evaluate how many stations have been added
        for i in range(len(stations)):
            stations[i].delta = np.sum(stations_added)
                
    else:
        for i in range(len(stations)):
            stations[i].delta = 0
    
    # Determine the unloading capacity of each online station
    online_berth_service_rate = []
    for i in range (online_stations):
        online_berth_service_rate.append(stations[i].production)

    # Traffic distribution according to ratio service rate of each station
    traffic_ratio = []
    if online_berth_service_rate:
        for i in range (len(online_berth_service_rate)):
            traffic_ratio.append(1/online_stations)
    else:
        traffic_ratio = 0
 
    # Determine total time that trains are at each berth
    online_occupancy = []
    for i in range (len(online_berth_service_rate)):            
        calls            = trains.calls / online_stations
        service_time     = trains.call_size / stations[i].production
        prep_time        = trains.prep_time
        time_at_station  = service_time + prep_time
        cumulative_time  = time_at_station * calls
        online_occupancy.append(cumulative_time / operational_hours)
    
    # Determine and register new berth characteristics                   
    for i in range (len(stations)):
        if i < online_stations:
            demand         = int(round(demand))
            capacity       = int(round(operational_hours * stations[i].production * trains.waitingfactor_to_occupancy(allowable_waiting_factor, online_stations)))
            occupancy      = round(online_occupancy[i],2)
            loading_rate   = int(round(online_berth_service_rate[i]))
            waiting_factor = round(trains.occupancy_to_waitingfactor(occupancy, online_stations),2)
            n_stations     = int(round(len(pending_berth_service_rate)))
        else:
            demand         = int(round(demand))
            capacity       = 0
            occupancy      = 0
            loading_rate   = 0
            waiting_factor = 0
            n_stations     = int(round(len(pending_berth_service_rate)))

        # Register berth characteristics under the berth class
        matrix = np.zeros(shape=(1, 7))
        # Year
        matrix[-1,0] = int(round(year))
        # Commodity demand
        matrix[-1,1] = demand
        # Capacity
        matrix[-1,2] = capacity
        # Occupancy
        matrix[-1,3] = occupancy
        # Effective loading capacity
        matrix[-1,4] = loading_rate
        # Waiting factor
        matrix[-1,5] = waiting_factor
        # Number of stations
        matrix[-1,6] = n_stations
        # Translate to dataframe
        df = pd.DataFrame(matrix, columns=['Year', 'Commodity demand', 'Total yearly loading capacity', 'Occupancy', 'Loading capacity', 'Waiting factor', 'Nr of stations'])
        # Register under berth instance
        if 'info' in dir(stations[i]):
            if int(stations[i].info[-1:]['Year']) == year:
                stations[i].info[-1:].update(df)
            else:
                stations[i].info = stations[i].info.append(df, sort=False)
        if 'info' not in dir(stations[i]):
            stations[i].info = df

    return stations, trains


# ### Conveyor investment decision
# #### Quay conveyor
# In this setup, the quay-side conveyor investment dicision is triggered whenever the the crane investment is triggered. The conveyor capacity is always sufficient to cope with the combined cranes' peak unloading capacity.

# In[6]:


def quay_conveyor_invest_decision(q_conveyors, berths, year, timestep, operational_hours):

    # For each time step, check whether pending assets come online
    
    online_capacity = []
    offline_capacity = []
    online_assets = []
    for i in range(len(q_conveyors)):
        if q_conveyors[i].online_date <= year:
            online_assets.append(1)
            online_capacity.append(q_conveyors[i].capacity)
        if q_conveyors[i].online_date > year:
            offline_capacity.append(q_conveyors[i].capacity)
    for i in range(len(q_conveyors)):
        q_conveyors[i].online = int(np.sum(online_capacity))
        q_conveyors[i].offline = int(np.sum(offline_capacity))
    online_assets = int(np.sum(online_assets))

    # for each time step, decide whether to invest in quay conveyors
    online = np.sum(online_capacity)
    pending = np.sum(offline_capacity)
    capacity = online + pending 
    berth_demands = []            
    for i in range(len(berths)):
        eff_unloading = int(berths[i].info[-1:]['Eff unloading capacity'])
        ratio = 2
        berth_demand = ratio * eff_unloading
        berth_demands.append(berth_demand)
    quay_demand = np.sum(berth_demands)
    
    if capacity < quay_demand:
        invest_decision = 'Invest in quay conveyors'
    else:
        invest_decision = 'Do not invest in quay conveyors'

    # if investments are needed, calculate how much extra capacity should be added
    if invest_decision == 'Invest in quay conveyors':
        # Calculate required capacity expansion
        q_conveyors.append(infra.conveyor(**infra.quay_conveyor_data))
        index = len(q_conveyors)-1
        capacity_steps = q_conveyors[index].capacity_steps
        shortcoming = quay_demand - capacity
        added_conveying_cap = int(np.ceil(shortcoming/capacity_steps)*capacity_steps)
        q_conveyors[index].purchase_date = year
        q_conveyors[index].online_date = year + q_conveyors[0].delivery_time
        q_conveyors[index].capacity = added_conveying_cap
        for i in range (len(q_conveyors)):
            q_conveyors[i].offline = added_conveying_cap
            q_conveyors[i].delta = added_conveying_cap
    
    if len(q_conveyors) != 0 and invest_decision == 'Do not invest in quay conveyors':
        q_conveyors[0].delta = 0
        
    for i in range(online_assets):    
        # Register berth characteristics under the berth instance
        matrix = np.zeros(shape=(1, 4))
        # Year
        matrix[-1,0] = int(round(year))
        # Quay demand
        berth_demands = []            
        for j in range(len(berths)):
            eff_unloading = int(berths[j].info[-1:]['Eff unloading capacity'])
            ratio = 2
            berth_demand = ratio * eff_unloading
            berth_demands.append(berth_demand)
        quay_demand = np.sum(berth_demands)
        matrix[-1,1] = int(round(quay_demand))
        # Capacity
        matrix[-1,2] = int(round(online))
        # Utilization
        if online:
            matrix[-1,3] = round(quay_demand/online,2)
        else:
            matrix[-1,3] = 0
        # Translate to dataframe
        df = pd.DataFrame(matrix, columns=['Year', 'Quay capacity demand', 'Capacity', 'Utilization'])
        # Register under station class
        if 'info' in dir(q_conveyors[i]):
            q_conveyors[i].info = q_conveyors[i].info.append(df)
        if 'info' not in dir(q_conveyors[i]):
            q_conveyors[i].info = df
    
    return q_conveyors


# #### 2.7.2 Hinterland conveyor
# In this setup, the hinterland conveyor investment dicision is triggered in order to always live up to loading station demand.

# In[7]:


def hinterland_conveyor_invest_decision(h_conveyors, stations, year, timestep, operational_hours):

    # For each time step, check whether pending assets come online
    online_capacity = []
    offline_capacity = []
    online_assets = []
    for i in range(len(h_conveyors)):
        if h_conveyors[i].online_date <= year:
            online_assets.append(1)
            online_capacity.append(h_conveyors[i].capacity)
        if h_conveyors[i].online_date > year:
            offline_capacity.append(h_conveyors[i].capacity)
    for i in range(len(h_conveyors)):
        h_conveyors[i].online = int(np.sum(online_capacity))
        h_conveyors[i].offline = int(np.sum(offline_capacity))
    online_assets = int(np.sum(online_assets))

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
    
    if len(h_conveyors) != 0 and invest_decision == 'Do not invest in hinterland conveyors':
        for i in range(len(h_conveyors)):
            h_conveyors[i].delta = 0
            
    for i in range(len(h_conveyors)):
        
        # Register berth characteristics under the berth instance
        matrix = np.zeros(shape=(1, 4))
        # Year
        matrix[-1,0] = int(round(year))
        # Station demand
        station_demand = []            
        for j in range(len(stations)):
            eff_unloading = int(stations[j].production)
            station_demand.append(eff_unloading)
        station_demand = np.sum(station_demand)
        matrix[-1,1] = int(round(station_demand))
        # Capacity
        matrix[-1,2] = int(round(online))
        # Utilization
        if online:
            matrix[-1,3] = round(station_demand/online,2)
        else:
            matrix[-1,3] = 0
        # Translate to dataframe
        df = pd.DataFrame(matrix, columns=['Year', 'Quay capacity demand', 'Capacity', 'Utilization'])
        # Register under station class
        if 'info' in dir(h_conveyors[i]):
            h_conveyors[i].info = h_conveyors[i].info.append(df)
        if 'info' not in dir(h_conveyors[i]):
            h_conveyors[i].info = df
    
    return h_conveyors

