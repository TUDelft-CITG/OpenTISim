
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# # Business Logic classes
# ### Revenue

# In[2]:


# create revenue class
class revenue_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


# In[3]:


# define revenue class functions 
class revenue_class(revenue_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self, maize, soybean, wheat, terminal_throughput, timestep):
        maize_throughput   = min(maize.demand[timestep], terminal_throughput)
        soybean_throughput = min(maize_throughput+soybean.demand[timestep], terminal_throughput)
        wheat_throughput   = min(maize_throughput+soybean_throughput+wheat.demand[timestep], terminal_throughput)

        self.maize   = int(maize_throughput   * maize.handling_fee)
        self.soybean = int(soybean_throughput * soybean.handling_fee)
        self.wheat   = int(wheat_throughput   * wheat.handling_fee)
        self.total   = int(self.maize + self.soybean + self.wheat)


# ### Capex

# In[4]:


# create capex class
class capex_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define capex class functions 
class capex_class(capex_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self, assets):
        
        quays       = assets[0]
        cranes      = assets[1]
        storage     = assets[2]
        stations    = assets[3]
        q_conveyors = assets[4]
        h_conveyors = assets[5]
        
        # Capex associated with the quay wall
        if quays[0].delta != 0:
            quay         = quays[0] 
            delta        = quay.delta
            unit_rate    = int(quay.Gijt_constant * (quay.depth*2 + quay.freeboard)**quay.Gijt_coefficient)
            mobilisation = int(max((delta * unit_rate * quay.mobilisation_perc), quay.mobilisation_min))
            self.quay    = delta * unit_rate + mobilisation
        else:
            self.quay = 0
        
        # Capex associated with the gantry cranes
        if cranes[0][0].delta != 0:
            crane        = cranes[0][0]
            delta        = crane.delta
            unit_rate    = crane.unit_rate
            mobilisation = delta * unit_rate * crane.mobilisation_perc
            self.gantry_cranes = delta * unit_rate + mobilisation
        else:
            self.gantry_cranes = 0
        
        # Capex associated with the harbour cranes
        if cranes[1][0].delta != 0:
            crane        = cranes[1][0]
            delta        = crane.delta
            unit_rate  = crane.unit_rate
            mobilisation = delta * unit_rate * crane.mobilisation_perc
            self.harbour_cranes = delta * unit_rate + mobilisation
        else:
            self.harbour_cranes = 0
        
        # Capex associated with the mobile harbour cranes
        if cranes[2][0].delta != 0:
            crane        = cranes[2][0]
            delta        = crane.delta
            unit_rate    = crane.unit_rate
            mobilisation = delta * unit_rate * crane.mobilisation_perc
            self.mobile_cranes = delta * unit_rate + mobilisation 
        else:
            self.mobile_cranes = 0
        
        # Capex associated with the screw unloaders
        if cranes[3][0].delta != 0:
            crane        = cranes[3][0]
            delta        = crane.delta
            unit_rate    = crane.unit_rate
            mobilisation = delta * unit_rate * crane.mobilisation_perc
            self.screw_unloaders = delta * unit_rate + mobilisation
        else:
            self.screw_unloaders = 0
        
        # Capex associated with the silos
        if storage[0][0].delta != 0:
            asset        = storage[0][0]
            delta        = asset.delta
            unit_rate    = asset.unit_rate
            mobilisation = delta * unit_rate * asset.mobilisation_perc
            self.silos   = delta * unit_rate + mobilisation
        else:
            self.silos = 0
        
        # Capex associated with the warehouses
        if storage[0][0].delta != 0:
            asset        = storage[1][0]
            delta        = asset.delta
            unit_rate    = asset.unit_rate
            mobilisation = delta * unit_rate * asset.mobilisation_perc
            self.warehouses = delta * unit_rate + mobilisation
        else:
            self.warehouses = 0
        
        # Capex associated with the hinterland laoding stations
        if stations[0].delta != 0:
            station      = stations[0]
            delta        = station.delta
            unit_rate    = station.unit_rate
            mobilisation = station.mobilisation
            self.loading_stations = delta * unit_rate + mobilisation
        else:
            self.loading_stations = 0
        
        # Capex associated with the conveyors connecting the quay to the storage
        if q_conveyors[0].delta != 0:
            conveyor     = q_conveyors[0]
            delta        = conveyor.delta
            unit_rate    = 6.0 * conveyor.length
            mobilisation = conveyor.mobilisation
            self.quay_conveyors = delta * unit_rate + mobilisation
        else:
            self.quay_conveyors = 0
        
        # Capex associated with the conveyors connecting the storage with the loading stations
        if h_conveyors[0].delta != 0:
            conveyor     = h_conveyors[0]
            delta        = conveyor.delta
            unit_rate    = 6.0 * conveyor.length
            mobilisation = conveyor.mobilisation
            self.hinterland_conveyors = delta * unit_rate + mobilisation
        else:
            self.hinterland_conveyors = 0
        
        # Combining all capex data
        self.total     = int(self.quay + self.gantry_cranes + self.harbour_cranes + self.mobile_cranes +                             self.screw_unloaders + self.silos + self.warehouses + self.loading_stations +                             self.quay_conveyors + self.hinterland_conveyors)
        self.cranes    = int(self.gantry_cranes + self.harbour_cranes + self.mobile_cranes + self.screw_unloaders)
        self.storage   = int(self.silos + self.warehouses)
        self.conveyors = int(self.quay_conveyors + self.hinterland_conveyors)


# ### Labour

# In[5]:


# create labour class 
class labour_properties_mixin(object):
    def __init__(self, international_salary, international_staff, local_salary, local_staff, operational_salary, 
                 shift_length, annual_shifts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.international_salary = international_salary
        self.international_staff = international_staff
        self.local_salary = local_salary
        self.local_staff = local_staff
        self.operational_salary = operational_salary
        self.shift_length = shift_length
        self.annual_shifts = annual_shifts

labour_data =  {"international_salary": 105000, "international_staff": 4, "local_salary": 18850, "local_staff": 10, 
                "operational_salary": 16750, "shift_length": 6.5, "annual_shifts": 200}


# In[6]:


# define labour class functions 
class labour_class(labour_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def calc(self, assets):
        cranes      = assets[1]
        storage     = assets[2]
        stations    = assets[3]
        q_conveyors = assets[4]
        h_conveyors = assets[5]
        
        # Number of shifts associated with the cranes (3 crew per crane)
        crane_shifts = []
        for i in range (4):
            crane = cranes[i][0]
            if crane.online_quantity != 0:
                crane_shifts.append(int(np.ceil(crane.online_quantity * operational_hours * crane.crew / self.shift_length)))
        crane_shifts = np.sum(crane_shifts)
        
        # Number of shifts associated with the storage (0.00002 or 0.0004 per tonne depending on storage type)
        storage_shifts = []
        for i in range (2):
            asset = storage[i][0]
            if asset.online_capacity != 0:
                storage_shifts.append(int(np.ceil(asset.online_capacity * operational_hours * asset.crew / self.shift_length)))
        storage_shifts = np.sum(storage_shifts)
        
        # Number of shifts associated with the loading stations (always 2)
        station_shifts = []
        station = stations[0]
        if station.online_capacity != 0:
            station_shifts = int(np.ceil(operational_hours * asset.crew / self.shift_length))
        else:
            station_shifts = 0
        
        # Number of shifts associated with the conveyors (always 1 for the quay and 1 for the hinterland conveyor)
        conveyor = q_conveyors[0]
        if conveyor.online_capacity != 0:
            q_conveyor_shifts = int(np.ceil(operational_hours * conveyor.crew / self.shift_length))
        else:
            q_conveyor_shifts = 0
        conveyor = h_conveyors[0]
        if conveyor.online_capacity != 0:
            h_conveyor_shifts = int(np.ceil(operational_hours * conveyor.crew / self.shift_length))
        else:
            h_conveyor_shifts = 0
        conveyor_shifts = q_conveyor_shifts + h_conveyor_shifts
        
        self.total_shifts = crane_shifts + storage_shifts + station_shifts + conveyor_shifts
        self.operational_staff = self.total_shifts/self.annual_shifts
        
        self.total_costs = int(self.international_salary * self.international_staff + self.local_salary * self.local_staff +                           self.operational_salary   * self.operational_staff)


# ### Maintenance

# In[7]:


# create maintenance class **will ultimately be placed in package**
class maintenance_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define maintenance class functions **will ultimately be placed in package**
class maintenance_class(maintenance_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self, assets):
        quays       = assets[0]
        cranes      = assets[1]
        storage     = assets[2]
        stations    = assets[3]
        q_conveyors = assets[4]
        h_conveyors = assets[5]
        
        # Maintenance costs associated with the quay
        quay = quays[0]
        if quay.online_length != 0:
            unit_rate = int(quay.Gijt_constant * (quay.depth*2 + quay.freeboard)**quay.Gijt_coefficient)
            maintenance = quay.online_length * unit_rate * quay.maintenance_perc
            self.quay = int(maintenance)
        else:
            self.quay = 0
            
        # Maintenance costs associated with the cranes
        crane_maintenance = []
        for i in range (4):
            crane = cranes[i][0]
            if crane.online_quantity != 0:
                unit_rate = crane.unit_rate
                maintenance = crane.online_quantity * unit_rate * crane.maintenance_perc
                crane_maintenance.append(maintenance)
        self.cranes = int(np.sum(crane_maintenance))

        # Maintenance costs associated with the storage
        storage_maintenance = []
        for i in range (2):
            asset = storage[i][0]
            if asset.online_capacity != 0:
                unit_rate = asset.unit_rate
                maintenance = asset.online_capacity * unit_rate * asset.maintenance_perc
                storage_maintenance.append(maintenance)
        self.storage = int(np.sum(storage_maintenance))
        
        # Maintenance costs associated with the loading stations
        station = stations[0]
        if station.online_capacity != 0:
            unit_rate = station.unit_rate
            maintenance = station.online_capacity * unit_rate * station.maintenance_perc
            self.loading_stations = int(maintenance)
        else:
            self.loading_stations = 0
            
        # Maintenance costs associated with the quay conveyors
        conveyor = q_conveyors[0]
        if conveyor.online_capacity != 0:
            unit_rate = 6.0 * conveyor.length
            maintenance = conveyor.online_capacity * unit_rate * conveyor.maintenance_perc
            quay_conveyor_maintenance = maintenance
        else:
            quay_conveyor_maintenance = 0
            
        # Maintenance costs associated with the hinterland conveyors
        conveyor = h_conveyors[0]
        if conveyor.online_capacity != 0:
            unit_rate = 6.0 * conveyor.length
            maintenance = conveyor.online_capacity * unit_rate * conveyor.maintenance_perc
            hinterland_conveyor_maintenance = maintenance
        else:
            hinterland_conveyor_maintenance = 0
            
        # Maintenance costs associated with all conveyors combined
        self.conveyors = int(quay_conveyor_maintenance + hinterland_conveyor_maintenance)
        
        self.total_costs = int(self.quay + self.cranes + self.storage + self.loading_stations + self.conveyors)


# ### Energy costs

# In[ ]:


# create energy consumption class **will ultimately be placed in package**
class energy_properties_mixin(object):
    def __init__(self, price, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = price

# Initial data
energy_data = {"price": 0.10}


# In[ ]:


# define energy consumption class functions **will ultimately be placed in package**
class energy_class(energy_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, assets):
        cranes      = assets[1]
        storage     = assets[2]
        stations    = assets[3]
        q_conveyors = assets[4]
        h_conveyors = assets[5]
            
        # Energy costs associated with the cranes
        crane_energy = []
        for i in range (4):
            if i != 2:
                consumption = 0.3 * self.peak_capacity
            else:
                consumption = 485
            for j in range (cranes[i][0].quantity):
                crane_energy.append(consumption * operational_hours * cranes[i][0].utilisation)
        crane_energy = np.sum(crane_energy)

#####################################################################################################
# Continue tommorrow 
#####################################################################################################

        # Energy costs associated with the storage
        storage_energy = []
        for i in range (2):
            asset = storage[i][0]
            if asset.online_capacity != 0:
                unit_rate = asset.unit_rate
                energy = asset.online_capacity * unit_rate * asset.energy_perc
                storage_energy.append(energy)
        self.storage = int(np.sum(storage_energy))
        
        # Energy costs associated with the loading stations
        station = stations[0]
        if station.online_capacity != 0:
            unit_rate = station.unit_rate
            energy = station.online_capacity * unit_rate * station.energy_perc
            self.loading_stations = int(energy)
        else:
            self.loading_stations = 0
            
        # Energy costs associated with the quay conveyors
        conveyor = q_conveyors[0]
        if conveyor.online_capacity != 0:
            unit_rate = 6.0 * conveyor.length
            energy = conveyor.online_capacity * unit_rate * conveyor.energy_perc
            quay_conveyor_energy = energy
        else:
            quay_conveyor_energy = 0
            
        # Energy costs associated with the hinterland conveyors
        conveyor = h_conveyors[0]
        if conveyor.online_capacity != 0:
            unit_rate = 6.0 * conveyor.length
            energy = conveyor.online_capacity * unit_rate * conveyor.energy_perc
            hinterland_conveyor_energy = energy
        else:
            hinterland_conveyor_energy = 0
            
        # Energy costs associated with all conveyors combined
        self.conveyors = int(quay_conveyor_energy + hinterland_conveyor_energy)
        
        self.total_costs = int(self.quay + self.cranes + self.storage + self.loading_stations + self.conveyors)
        
        
        
        
        
    
    def individual_calc(self, asset):
        if "consumption_calc" in dir(asset) != False:
            asset.consumption_calc()
            return asset.consumption
        else:
            return 0
            
    def calc(self):
        self.quay                = self.individual_calc(quay)
        self.gantry_cranes       = self.individual_calc(gantry_cranes)
        self.harbour_cranes      = self.individual_calc(harbour_cranes)
        self.mobile_cranes       = self.individual_calc(mobile_cranes)
        self.screw_unloaders     = self.individual_calc(screw_unloaders)
        self.conveyor_quay       = self.individual_calc(conveyor_quay)
        self.conveyor_hinterland = self.individual_calc(conveyor_hinterland)
        self.silos               = self.individual_calc(silos)
        self.warehouse           = self.individual_calc(warehouse)
        self.loading_station     = self.individual_calc(loading_station)
        
        self.consumption = int(self.quay + self.gantry_cranes + self.harbour_cranes + self.mobile_cranes + self.screw_unloaders +                               self.conveyor_quay + self.conveyor_hinterland + self.silos + self.warehouse + self.loading_station)
        self.total = int(self.consumption * self.price)


# # Demurrage costs

# In[ ]:


# create demurrage class **will ultimately be placed in package**
class demurrage_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define demurrage class functions **will ultimately be placed in package**
class demurrage_class(demurrage_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def individual_calc(self, vessel_type):
        vessel_type.berth_time_calc()
        return int(max(vessel_type.port_time - vessel_type.all_turn_time, 0) * vessel_type.demurrage_rate)
       
    def calc(self):
        self.handysize = self.individual_calc(handysize)
        self.handymax  = self.individual_calc(handymax)
        self.panamax   = self.individual_calc(panamax)


# In[ ]:


def business_logic_objects(start_year, window):
    
    revenues = []
    capex = []
    labour = []
    maintenance = []
    energy = []
    demurrage = []
    
    for i in range (window):
        
        revenues.append(revenue_class())
        revenues[i].index = start_year + i
        
        capex.append(capex_class())
        capex[i].index = start_year + i
        
        labour.append(labour_class(**labour_data))
        labour[i].index = start_year + i
        
        maintenance.append(maintenance_class())
        maintenance[i].index = start_year + i
        
        energy.append(energy_class(**energy_data))
        energy[i].index = start_year + i
        
        demurrage.append(demurrage_class())
        demurrage[i].index = start_year + i
        
    return [revenues, capex, labour, maintenance, energy, demurrage]

