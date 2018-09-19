
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# # Import from notebook

# ### Import general port parameters
# This imports the 'General Port parameters' from the notebook so that they can be used for calculations within this package

# In[2]:


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


# ### Create notebook affiliated classes
# This creates the classes that are linked to data located within the notebook
# - Commodity characteristics at current timestep

# In[3]:


def import_notebook_classes():
    
    global commodities
    
    class commodity_class():
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.maize_demand   = maize.demand[timestep]
            self.soybean_demand = soybean.demand[timestep]
            self.wheat_demand   = wheat.demand[timestep]
            self.demand         = self.maize_demand + self.soybean_demand + self.wheat_demand
    commodities = commodity_class()
    
    return


# # Terminal Infrastructure classes

# ### Quay wall

# In[5]:


# create quay wall class
class quay_wall_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, mobilisation_min, mobilisation_perc, maintenance_perc, insurance_perc, 
                 length, depth, freeboard, Gijt_constant, Gijt_coefficient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.mobilisation_min     = mobilisation_min
        self.mobilisation_perc    = mobilisation_perc
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.length               = length
        self.depth                = depth
        self.freeboard            = freeboard
        self.Gijt_constant        = Gijt_constant
        self.Gijt_coefficient     = Gijt_coefficient

# Initial data set, data from Excel_input.xlsx
quay_data = {"ownership": 'Port authority', "delivery_time": 2, "lifespan": 50, "mobilisation_min": 2500000,
             "mobilisation_perc": 0.02, "maintenance_perc": 0.01, "insurance_perc": 0.01,"length": 400, "depth": 14,
             "freeboard": 4, "Gijt_constant": 757.20, "Gijt_coefficient": 1.2878} 


# In[6]:


# define quay wall class functions
class quay_wall_class(quay_wall_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def unit_rate_calc(self):
        self.unit_rate = int(self.Gijt_constant * (self.depth*2 + self.freeboard)**self.Gijt_coefficient) # van Gijt (2010)
    
    def original_value_calc(self):
        self.original_value = int(self.length * self.unit_rate)
        
    def mobilisation_calc(self):
        self.mobilisation = int(max((self.delta * self.unit_rate * self.mobilisation_perc), self.mobilisation_min))
        
    def maintenance_calc(self):
        self.maintenance = int(self.original_value * self.maintenance_perc)
        
    def insurance_calc(self):
        self.insurance = int(self.original_value * self.insurance_perc)


# In[7]:


# create quay object
quay = quay_wall_class(**quay_data)


# ### Berths

# In[8]:


# create berth class
class berth_properties_mixin(object):
    def __init__(self, crane_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crane_config  = crane_config
        self.delivery_time = quay.delivery_time
        
# Initial data set, data from Excel_input.xlsx
berth_data = {"crane_config": 'maximum'}


# In[16]:


# define berth functions 
class berth_class(berth_properties_mixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def LOA_calc(self):
        if panamax.calls[timestep] != 0:
            return panamax.LOA
        elif panamax.calls[timestep] == 0 and handymax.calls[timestep] != 0:
            return handymax.LOA
        else:
            return handysize.LOA

    def vessel_depth_calc(self):
        if panamax.calls[timestep] != 0:
            return panamax.draft
        elif panamax.calls[timestep] == 0 and handymax.calls[timestep] != 0:
            return handymax.draft
        else:
            return handysize.draft

    def length_calc(self, max_LOA, i):      
        if i == 0:
            return max_LOA + 15 + 15 
        else:
            return max_LOA + 15

    def depth_calc(self, max_draft):
        return max_draft + 1
        
    def cranes_calc(self):
        if self.crane_config == 'maximum': 
            if panamax.calls[timestep] != 0:
                self.n_cranes = panamax.max_cranes
            elif panamax.calls[timestep] == 0 and handymax.calls[timestep] != 0:
                self.n_cranes = handymax.max_cranes
            else:
                self.n_cranes = handysize.max_cranes
        
    def eff_unloading_rate_calc(self):
        if self.crane_type == 'Gantry cranes':
            return gantry_cranes[0].effective_capacity * self.n_cranes
        if self.crane_type == 'Harbour cranes':
            return harbour_cranes[0].effective_capacity * self.n_cranes
        if self.crane_type == 'Mobile cranes':
            return mobile_cranes[0].effective_capacity * self.n_cranes
        if self.crane_type == 'Screw unloaders':
            return screw_unloaders[0].effective_capacity * self.n_cranes
        
    def peak_unloading_rate_calc(self):
        if self.crane_type == 'Gantry cranes':
            return gantry_cranes[0].peak_capacity * self.n_cranes
        if self.crane_type == 'Harbour cranes':
            return harbour_cranes[0].peak_capacity * self.n_cranes
        if self.crane_type == 'Mobile cranes':
            return mobile_cranes[0].peak_capacity * self.n_cranes
        if self.crane_type == 'Screw unloaders':
            return screw_unloaders[0].peak_capacity * self.n_cranes
    
    def occupancy_calc(self, quantity):
        self.cranes_calc()
        unloading_rate = self.eff_unloading_rate_calc()
        handysize.berth_time_calc(unloading_rate)
        handymax.berth_time_calc(unloading_rate)
        panamax.berth_time_calc(unloading_rate)
        berth_time = (handysize.berth_time * handysize.calls[timestep] +                      handymax.berth_time  * handymax.calls[timestep] +                      panamax.berth_time   * panamax.calls[timestep]) / quantity       
        return berth_time / (operational_hours)    
    
    def remaining_calcs(self):
        max_LOA   = berths[0].LOA_calc()                          # Maximum vessel LOA
        max_draft = berths[0].vessel_depth_calc()                 # Maximum vessel draft
        n_cranes  = berths[0].cranes_calc()                       # Number of cranes per vessel
        self.cranes_calc()
        self.length             = self.length_calc(max_LOA, i)    # assign length of each berth
        self.depth              = self.depth_calc(max_draft)      # assign depth of each berth
        self.eff_unloading_rate = self.eff_unloading_rate_calc()  # effective unloading rate of each berth
        self.eff_unloading_rate = self.peak_unloading_rate_calc() # peak unloading rate of each berth
        
    @classmethod
    def online_quantity_calc(cls, quantity):
        cls.online_quantity = quantity
        
    @classmethod
    def pending_quantity_calc(cls, quantity):
        cls.pending_quantity = quantity


# In[ ]:


#@classmethod
def remaining_calcs(clc):
    max_LOA   = berths[0].LOA_calc()                    # Maximum vessel LOA
    max_draft = berths[0].vessel_depth_calc()           # Maximum vessel draft
    n_cranes  = berths[0].cranes_calc()                 # Number of cranes per vessel

    for i in range (berths[0].quantity):
        berths[i].cranes_calc()
        berths[i].length             = berths[i].length_calc(max_LOA, i)            # assign length of each berth
        berths[i].depth              = berths[i].depth_calc(max_draft)              # assign depth of each berth
        berths[i].eff_unloading_rate = berths[i].eff_unloading_rate_calc()  # effective unloading rate of each berth
        berths[i].eff_unloading_rate = berths[i].peak_unloading_rate_calc() # peak unloading rate of each berth


# In[4]:


# create berth objects
berths = []
for i in range (5):
    berths.append(berth_class(**berth_data))
    berths[i].index = i


# ## Cranes (cyclic)

# In[12]:


# create cyclic unloader class **will ultimately be placed in package**
class cyclic_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, unit_rate, mobilisation_perc, maintenance_perc, insurance_perc, consumption, crew, unloader_type, lifting_capacity, hourly_cycles, eff_fact, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation_perc    = mobilisation_perc
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.consumption          = consumption
        self.crew                 = crew
        self.unloader_type        = unloader_type
        self.lifting_capacity     = lifting_capacity
        self.hourly_cycles        = hourly_cycles
        self.eff_fact             = eff_fact
        self.utilisation          = utilisation
        self.payload              = int(0.70 * self.lifting_capacity)      #Source: Nemag
        self.peak_capacity        = int(self.payload * self.hourly_cycles) 
        self.effective_capacity   = int(eff_fact * self.peak_capacity)     #Source: TATA steel

# Initial data set, data from Excel_input.xlsx
gantry_crane_data        = {"ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 40, "unit_rate": 19500000,"mobilisation_perc": 0.15, 
                      "maintenance_perc": 0.02, "insurance_perc": 0.01,"consumption": 0, "crew": 3, 
                      "unloader_type": 'Gantry crane', "lifting_capacity": 70, "hourly_cycles": 60, "eff_fact": 0.55,
                      "utilisation": 0.80}

harbour_crane_data = {"ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 40, "unit_rate": 14000000, "mobilisation_perc": 0.15, 
                      "maintenance_perc": 0.02, "insurance_perc": 0.01,"consumption": 0, "crew": 3, 
                      "unloader_type": 'Harbour crane crane', "lifting_capacity": 40, "hourly_cycles": 40, "eff_fact": 0.55,
                      "utilisation": 0.80}

mobile_crane_data  = {"ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 20, "unit_rate": 3325000,"mobilisation_perc": 0.15, 
                      "maintenance_perc": 0.031,"insurance_perc": 0.01,"consumption": 485, "crew": 3, 
                      "unloader_type": 'Mobile crane',"lifting_capacity": 60, "hourly_cycles": 30, "eff_fact": 0.55,
                      "utilisation": 0.80}


# In[13]:


# define cyclic unloader class functions **will ultimately be placed in package**
class cyclic_unloader(cyclic_properties_mixin): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def total_capacity_calc(self):
        self.total_peak_capacity = int(self.quantity * self.peak_capacity)
        self.total_eff_capacity  = int(self.total_peak_capacity * self.eff_fact)
    
    def original_value_calc(self):
        self.original_value = int(self.quantity * self.unit_rate) 
        
    def lease_calc(self):
        if self.unloader_type == 'Mobile crane':
            self.lease = int(self.original_value * 0.10)
        else:
            return
            
    def mobilisation_calc(self):
        self.mobilisation = int(self.delta * self.unit_rate * self.mobilisation_perc)
        
    def maintenance_calc(self):
        self.maintenance = int(self.original_value * self.maintenance_perc)
        
    def insurance_calc(self):
        self.insurance = int(self.original_value * self.insurance_perc)
        
    def consumption_calc(self):
        if self.unloader_type != 'Mobile crane':
            self.consumption = int(0.3 * operational_hours * self.utilisation * self.quantity * self.peak_capacity)
        if self.unloader_type == 'Mobile crane':
            self.consumption = int(485 * operational_hours * self.utilisation * self.quantity)
        
    def shifts_calc(self):
        self.shifts = int(np.ceil(self.quantity * operational_hours * self.crew / labour.shift_length))
        
    def quantity_calc(self, quantity, crane_type):
        if crane_type == 'Gantry crane':
            for i in range (quantity):
                cranes[0][i].quantity = quantity
        elif crane_type == 'Harbour crane':
            for i in range (quantity):
                cranes[1][i].quantity = quantity
        elif crane_type == 'Mobile crane':
            for i in range (quantity):
                cranes[2][i].quantity = quantity


# In[5]:


# create crane objects
gantry_cranes  = []
harbour_cranes = []
mobile_cranes  = []

for i in range (10):
    gantry_cranes.append(cyclic_unloader(**gantry_crane_data))
    gantry_cranes[i].index = i

    harbour_cranes.append(cyclic_unloader(**harbour_crane_data))
    harbour_cranes[i].index = i
    
    mobile_cranes.append(cyclic_unloader(**mobile_crane_data))
    mobile_cranes[i].index = i    


# ## Cranes (continuous)

# In[15]:


# create continuous unloader class **will ultimately be placed in package**
class continuous_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, unit_rate, mobilisation_perc, maintenance_perc, insurance_perc, crew, unloader_type, peak_capacity, eff_fact, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation_perc    = mobilisation_perc
        self.mobilisation         = int(mobilisation_perc * unit_rate)
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.crew                 = crew
        self.unloader_type        = unloader_type
        self.peak_capacity        = peak_capacity
        self.eff_fact             = eff_fact
        self.effective_capacity   = eff_fact * peak_capacity
        self.utilisation          = utilisation

# Initial data set, data from Excel_input.xlsx
continuous_screw_data = {"ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 30, "unit_rate": 6900000, "mobilisation_perc": 0.15, 
                         "maintenance_perc": 0.02, "insurance_perc": 0.01, "crew": 2,"unloader_type": 'Screw unloader', 
                         "peak_capacity": 700, "eff_fact": 0.55, "utilisation": 0.80}


# In[16]:


# define continuous unloader class functions **will ultimately be placed in package**
class continuous_unloader(continuous_properties_mixin):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def total_capacity_calc(self):
        self.total_peak_capacity = int(self.quantity * self.peak_capacity)
        self.total_eff_capacity  = int(self.total_peak_capacity * self.eff_fact)
    
    def original_value_calc(self):
        self.original_value = int(self.quantity * self.unit_rate) 
        
    def mobilisation_calc(self):
        self.mobilisation = int(self.delta * self.unit_rate * self.mobilisation_perc)
        
    def maintenance_calc(self):
        self.maintenance = int(self.original_value * self.maintenance_perc)
        
    def insurance_calc(self):
        self.insurance = int(self.original_value * self.insurance_perc)
        
    def consumption_calc(self):
        self.consumption = int(0.52 * operational_hours * self.utilisation * self.quantity * self.peak_capacity)
        
    def shifts_calc(self):
        self.shifts = int(np.ceil(self.quantity * operational_hours * self.crew / labour.shift_length))
        
    def quantity_calc(self, quantity, crane_type):
        if crane_type == 'Screw unloader':
            for i in range (quantity):
                cranes[3][i].quantity = quantity


# In[7]:


# create screw unloader objects 
screw_unloaders  = []

for i in range (10):
    screw_unloaders.append(continuous_unloader(**continuous_screw_data))
    screw_unloaders[i].index = i
    
cranes = [gantry_cranes, harbour_cranes, mobile_cranes, screw_unloaders]


# ## Conveyors

# In[18]:


# create conveyor class **will ultimately be placed in package**
class conveyor_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, mobilisation, maintenance_perc, insurance_perc, crew, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.mobilisation         = mobilisation
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.crew                 = crew
        self.utilisation          = utilisation

# Initial data set, data from Excel_input.xlsx
conveyor_data = {"ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 10, "mobilisation": 30000, 
                 "maintenance_perc": 0.10, "insurance_perc": 0.01, "crew": 0.5, "utilisation": 0.80}


# In[19]:


# define conveyor class functions **will ultimately be placed in package**
class conveyor(conveyor_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def unit_rate_calc(self):
        self.unit_rate = int(6.0 * self.length)
    
    def original_value_calc(self):
        self.original_value = int(self.capacity * self.unit_rate) 
        
    def maintenance_calc(self):
        self.maintenance = int(self.original_value * self.maintenance_perc)
        
    def insurance_calc(self):
        self.insurance = int(self.original_value * self.insurance_perc)
        
    def consumption_calc(self):
        self.consumption = int(0.08 * operational_hours * self.utilisation * self.capacity)
        
    def shifts_calc(self):
        self.shifts = int(np.ceil(operational_hours * self.crew / labour.shift_length))
        
    def quantity_calc(self, quantity, conveyor_group):
        if conveyor_group == 'Quay':
            for i in range (quantity):
                q_conveyors[i].quantity = quantity
        else:
            for i in range (quantity):
                h_conveyors[i].quantity = quantity
    
    def overall_capacity_calc(self, capacity, quantity, conveyor_group):
        if conveyor_group == 'Quay':
            for i in range (quantity):
                q_conveyors[i].overall_capacity = capacity
        else:
            for i in range (quantity):
                h_conveyors[i].overall_capacity = capacity


# In[20]:


# create loading station objects
q_conveyors = []
h_conveyors = []

for i in range (5):
    q_conveyors.append(conveyor(**conveyor_data))
    q_conveyors[i].index = i
    
    h_conveyors.append(conveyor(**conveyor_data))
    h_conveyors[i].index = i


# ## Storage

# In[21]:


# create storage class **will ultimately be placed in package**
class storage_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, unit_rate, mobilisation_min, mobilisation_perc, maintenance_perc, insurance_perc, storage_type, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation_min     = mobilisation_min
        self.mobilisation_perc    = mobilisation_perc
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.storage_type         = storage_type
        self.utilisation          = utilisation
        
# Initial data set, data from Excel_input.xlsx
silo_data      = {"ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 30, "unit_rate": 60, 
                  "mobilisation_min": 200000, "mobilisation_perc": 0.02, "maintenance_perc": 0.02, 
                  "insurance_perc": 0.01, "storage_type": 'Silos', "utilisation": 0.80}
warehouse_data = {"ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 30, "unit_rate": 140,
                  "mobilisation_min": 200000, "mobilisation_perc": 0.02, "maintenance_perc": 0.01, 
                  "insurance_perc": 0.01, "storage_type": 'Warehouse', "utilisation": 0.80}


# In[22]:


# define storage class functions **will ultimately be placed in package**
class storage(storage_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  
    
    def original_value_calc(self):
        self.original_value = int(self.capacity * self.unit_rate) 
    
    def mobilisation_calc(self):
        self.mobilisation = int(max((self.delta * self.unit_rate * self.mobilisation_perc), self.mobilisation_min))
        
    def maintenance_calc(self):
        self.maintenance = int(self.original_value * self.maintenance_perc)
        
    def insurance_calc(self):
        self.insurance = int(self.original_value * self.insurance_perc)
        
    def consumption_calc(self):
        if self.storage_type == 'Silos':
            self.consumption = int(0.003 * self.capacity * operational_hours)
        if self.storage_type == 'Warehouse':
            self.consumption = int(0.001 * self.capacity * operational_hours)
        
    def shifts_calc(self):
        if self.storage_type == 'Silos':
            self.crew = 0.00002 * self.capacity  # 2 people per 100.000t of storage
        if self.storage_type == 'Warehouse':
            self.crew = 0.00004 * self.capacity  # 4 people per 100.000t of storage
        self.shifts = int(np.ceil(operational_hours * self.crew / labour.shift_length))
        
    def quantity_calc(self, quantity, storage_type):
        if storage_type == 'Silos':
            for i in range (quantity):
                storage[0][i].quantity = quantity
        else:
            for i in range (quantity):
                storage[1][i].quantity = quantity
    
    def overall_capacity_calc(self, capacity, quantity, storage_type):
        if storage_type == 'Silos':
            for i in range (quantity):
                storage[0][i].overall_capacity = capacity
        else:
            for i in range (quantity):
                storage[1][i].overall_capacity = capacity


# In[23]:


# create storage objects
silos = []
warehouses = []

for i in range (5):
    silos.append(storage(**silo_data))
    warehouses.append(storage(**warehouse_data))
    silos[i].index = i
    warehouses[i].index = i
    
storage = [silos, warehouses]


# ## Loading Station

# In[24]:


# create loading station class **will ultimately be placed in package**
class hinterland_station_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, unit_rate, mobilisation, maintenance_perc, insurance_perc, crew, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation         = mobilisation
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.crew                 = crew
        self.utilisation          = utilisation
        
# Initial data set, data from Excel_input.xlsx
hinterland_station_data = {"ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 15, "unit_rate": 4000, "mobilisation": 100000, 
                           "maintenance_perc": 0.02, "insurance_perc": 0.01, "crew": 2, "utilisation": 0.80}


# In[25]:


# define loading station class functions **will ultimately be placed in package**
class hinterland_station(hinterland_station_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def capacity_calc(self):
        self.capacity = 0    
    
    def original_value_calc(self):
        self.original_value = int(self.capacity * self.unit_rate) 
        
    def maintenance_calc(self):
        self.maintenance = int(self.original_value * self.maintenance_perc)
        
    def insurance_calc(self):
        self.insurance = int(self.original_value * self.insurance_perc)
        
    def consumption_calc(self):
        self.consumption = int(0.75 * operational_hours * self.utilisation * self.capacity)
        
    def shifts_calc(self):
        self.shifts = int(np.ceil(operational_hours * self.crew / labour.shift_length))
    
    def capacity_calc(self, capacity):
        self.capacity = capacity
        
    @classmethod
    def overall_capacity_calc(cls, capacity):
        cls.overall_capacity = capacity
        
    @classmethod
    def quantity_calc(cls, quantity):
        cls.quantity = quantity


# In[26]:


# create loading station objects
stations = []
for i in range (5):
    stations.append(hinterland_station(**hinterland_station_data))
    stations[i].index = i


# # Business Logic

# ## Revenue calc

# In[27]:


# create revenue class **will ultimately be placed in package**
class revenue_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


# In[28]:


# define revenue class functions **will ultimately be placed in package**
class revenue_class(revenue_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self):
        self.maize   = int(maize.throughput   * maize.handling_fee)
        self.soybean = int(soybean.throughput * soybean.handling_fee)
        self.wheat   = int(wheat.throughput   * wheat.handling_fee)
        self.total   = int(self.maize + self.soybean + self.wheat)


# In[29]:


# create objects **will ultimately be placed in notebook**
revenue = revenue_class()


# ## Capex calc

# In[30]:


# create capex class **will ultimately be placed in package**
class capex_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[31]:


# define capex class functions **will ultimately be placed in package**
class capex_class(capex_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)    
        
    def individual_calc(self, asset):
        if asset.delta != 0:
            if "unit_rate_calc" in dir(asset) != False:
                asset.unit_rate_calc()
            if "mobilisation_calc" in dir(asset) != False:
                asset.mobilisation_calc()
            return int(asset.delta * asset.unit_rate + asset.mobilisation)
        if asset.delta == 0: 
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
        
        self.total = int(self.quay + self.gantry_cranes + self.harbour_cranes + self.mobile_cranes + self.screw_unloaders +                     self.conveyor_quay + self.conveyor_hinterland + self.silos + self.warehouse + self.loading_station)


# In[32]:


# create objects **will ultimately be placed in notebook**
capex = capex_class()


# ## Labour calc

# In[33]:


# create labour class **will ultimately be placed in package**
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


# In[34]:


# define labour class functions **will ultimately be placed in package**
class labour_class(labour_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def individual_calc(self, asset):
        if "shifts_calc" in dir(asset) != False:
            asset.shifts_calc()
            return int(np.ceil(asset.shifts / self.annual_shifts))
        else:
            return 0
            
    def calc(self):
        self.staff_quay                = self.individual_calc(quay)
        self.staff_gantry_cranes       = self.individual_calc(gantry_cranes)
        self.staff_harbour_cranes      = self.individual_calc(harbour_cranes)
        self.staff_mobile_cranes       = self.individual_calc(mobile_cranes)
        self.staff_screw_unloaders     = self.individual_calc(screw_unloaders)
        self.staff_conveyor_quay       = self.individual_calc(conveyor_quay)
        self.staff_conveyor_hinterland = self.individual_calc(conveyor_hinterland)
        self.staff_silos               = self.individual_calc(silos)
        self.staff_warehouse           = self.individual_calc(warehouse)
        self.staff_loading_station     = self.individual_calc(loading_station)
        
        self.operational_staff = int(self.staff_quay + self.staff_gantry_cranes + self.staff_harbour_cranes + 
                                     self.staff_mobile_cranes + self.staff_screw_unloaders + self.staff_conveyor_quay +\
                                     self.staff_conveyor_hinterland + self.staff_silos + self.staff_warehouse +\
                                     self.staff_loading_station)
        
        self.total = self.international_salary * self.international_staff + self.local_salary * self.local_staff +                     self.operational_salary   * self.operational_staff


# In[35]:


# create objects **will ultimately be placed in notebook**
labour = labour_class(**labour_data)


# ## Maintenance calc

# In[36]:


# create maintenance class **will ultimately be placed in package**
class maintenance_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[37]:


# define maintenance class functions **will ultimately be placed in package**
class maintenance_class(maintenance_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def individual_calc(self, asset):
        if "unit_rate_calc" in dir(asset) != False:
            asset.unit_rate_calc()
        if "original_value_calc" in dir(asset) != False:
            asset.original_value_calc()
        if "maintenance_calc" in dir(asset) != False:
            asset.maintenance_calc()
            return asset.maintenance
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
        
        self.total = int(self.quay + self.gantry_cranes + self.harbour_cranes + self.mobile_cranes + self.screw_unloaders +                     self.conveyor_quay + self.conveyor_hinterland + self.silos + self.warehouse + self.loading_station)


# In[38]:


# create objects **will ultimately be placed in notebook**
maintenance = maintenance_class()


# ## Energy consumption calc

# In[39]:


# create energy consumption class **will ultimately be placed in package**
class energy_properties_mixin(object):
    def __init__(self, price, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = price

# Initial data
energy_data = {"price": 0.10}


# In[40]:


# define energy consumption class functions **will ultimately be placed in package**
class energy_class(energy_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
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


# In[41]:


# create objects **will ultimately be placed in notebook**
energy = energy_class(**energy_data)


# ## Demurrage calc

# In[42]:


# create demurrage class **will ultimately be placed in package**
class demurrage_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[43]:


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


# In[44]:


# create objects **will ultimately be placed in notebook**
demurrage = demurrage_class()


# In[45]:


# [Test] demurrage 

#demurrage.calc()
#demurrage.__dict__


# ## Residual value calc

# ## Lease calc

# ## WACC calc

# ## Escalation calc

# ## Profit calc

# ## NPV calc

# # Apply triggers
