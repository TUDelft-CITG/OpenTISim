
# coding: utf-8

# In[5]:


import numpy as np
import terminal_optimization.infrastructure as infra


# In[ ]:


def terminal():
    
    #########################################
    # Import terminal infrastructure objects
    #########################################
    
    # Quay
    quay_object = infra.quay_wall_class(**infra.quay_data)
    berth_object = infra.berth_class(**infra.berth_data)
    
    # Cranes
    gantry_crane_object  = infra.cyclic_unloader(**infra.gantry_crane_data)
    harbour_crane_object = infra.cyclic_unloader(**infra.harbour_crane_data)
    mobile_crane_object  = infra.cyclic_unloader(**infra.mobile_crane_data)  
    screw_unloader_object = infra.continuous_unloader(**infra.continuous_screw_data)
    
    # Storage
    silo_object = infra.storage(**infra.silo_data)
    warehouse_object = infra.storage(**infra.warehouse_data)
    
    #Loading stations
    station_object = infra.hinterland_station(**infra.hinterland_station_data)
    
    # Conveyors
    quay_conveyor_object = infra.conveyor(**infra.quay_conveyor_data)
    hinterland_conveyor_object = infra.conveyor(**infra.hinterland_conveyor_data)
    
    #########################################
    # Assign existing infrastructure   
    #########################################
    
    terminal.quays, terminal.berths, terminal.cranes, terminal.storage, terminal.stations = [], [], ([],[],[],[]), ([],[]), []
    terminal.quay_conveyors, terminal.hinterland_conveyors = [], [] 

    # Quay
    if quay_object.t0_length != 0:
        terminal.quays.append(quay_object)   
    if berth_object.t0_quantity != 0:
        for i in range (berth_object.t0_quantity):
            terminal.berths.append(berth_object)
    
    # Cranes
    if gantry_crane_object.t0_quantity != 0:
        for i in range (gantry_crane_object.t0_quantity):
            terminal.cranes[0].append(gantry_crane_object)        
    if harbour_crane_object.t0_quantity != 0:
        for i in range (harbour_crane_object.t0_quantity):
            terminal.cranes[1].append(harbour_crane_object)      
    if mobile_crane_object.t0_quantity != 0:
        for i in range (mobile_crane_object.t0_quantity):
            terminal.cranes[2].append(mobile_crane_object)     
    if screw_unloader_object.t0_quantity != 0:
        for i in range (screw_unloader_object.t0_quantity):
            terminal.cranes[3].append(screw_unloader_object)
    
    # Storage
    if silo_object.t0_capacity != 0:
        terminal.storage[0].append(silo_object)
        terminal.storage[0][0].capacity = silo_object.t0_capacity
    if warehouse_object.t0_capacity != 0:
        terminal.storage[1].append(warehouse_object)
        terminal.storage[1][0].capacity = warehouse_object.t0_capacity
    
    # Loading stations
    if station_object.t0_capacity != 0:
        terminal.stations.append(station_object)
        terminal.stations[0].capacity = station_object.t0_capacity
    
    # Conveyors
    if quay_conveyor_object.t0_capacity != 0:
        terminal.quay_conveyors.append(quay_conveyor_object)
        terminal.quay_conveyors[0].capacity = quay_conveyor_object.t0_capacity  
    if hinterland_conveyor_object.t0_capacity != 0:
        terminal.hinterland_conveyors.append(hinterland_conveyor_object)
        terminal.hinterland_conveyors[0].capacity = hinterland_conveyor_object.t0_capacity
        
    #########################################
    # Assign empty cashflow list
    #########################################
    
    terminal.throughputs, terminal.revenues, terminal.capex, terminal.labour, terminal.maintenance = [], [], [], [], []
    terminal.energy, terminal.insurance, terminal.lease, terminal.demurrage, terminal.residuals = [], [], [], [], []
    terminal.profits, terminal.opex = [], []
        
    return terminal

