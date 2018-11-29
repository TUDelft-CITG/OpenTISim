
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# # Terminal Infrastructure classes

# ### Quay wall

# In[1]:


# create quay wall class
class quay_wall_properties_mixin(object):
    def __init__(self, t0_length, ownership, delivery_time, lifespan, mobilisation_min, mobilisation_perc, 
                 maintenance_perc, insurance_perc, length, depth, freeboard, Gijt_constant, Gijt_coefficient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.t0_length            = t0_length
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
quay_data = {"t0_length": 0, "ownership": 'Port authority', "delivery_time": 2, "lifespan": 50, "mobilisation_min": 2500000,
             "mobilisation_perc": 0.02, "maintenance_perc": 0.01, "insurance_perc": 0.01,"length": 400, "depth": 14,
             "freeboard": 4, "Gijt_constant": 757.20, "Gijt_coefficient": 1.2878} 


# In[2]:


# define quay wall class functions
class quay_wall_class(quay_wall_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[3]:


# create quay object
quay_object = quay_wall_class(**quay_data)


# ### Berths

# In[6]:


# create berth class
class berth_properties_mixin(object):
    def __init__(self, t0_quantity, crane_type, max_cranes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t0_quantity   = t0_quantity
        self.crane_type    = crane_type
        self.max_cranes    = max_cranes
        self.delivery_time = quay_object.delivery_time
        self.cranes_present = []
        
# Initial data set, data from Excel_input.xlsx
berth_data = {"t0_quantity": 0, "crane_type": 'Mobile cranes', "max_cranes": 3}


# In[ ]:


# define berth functions 
class berth_class(berth_properties_mixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def LOA_calc(self, vessels, timestep):
        handysize = vessels[0]
        handymax = vessels[1] 
        panamax = vessels[2]
        if panamax.calls[timestep] != 0:
            return panamax.LOA
        elif panamax.calls[timestep] == 0 and handymax.calls[timestep] != 0:
            return handymax.LOA
        else:
            return handysize.LOA

    def vessel_depth_calc(self, vessels, timestep):
        handysize = vessels[0]
        handymax = vessels[1] 
        panamax = vessels[2]
        if panamax.calls[timestep] != 0:
            return panamax.draft
        elif panamax.calls[timestep] == 0 and handymax.calls[timestep] != 0:
            return handymax.draft
        else:
            return handysize.draft

    def length_calc(self, max_LOA, berths):      
        if len(berths) == 1:
            return max_LOA + 15 + 15 
        else:
            return max_LOA + 15

    def depth_calc(self, max_draft):
        return max_draft + 1
    
    def remaining_calcs(self, berths, vessels, timestep):
        max_LOA   = berths[0].LOA_calc(vessels, timestep)          # Maximum vessel LOA
        max_draft = berths[0].vessel_depth_calc(vessels, timestep) # Maximum vessel draft
        self.length             = self.length_calc(max_LOA, berths)     # assign length of each berth
        self.depth              = self.depth_calc(max_draft)            # assign depth of each berth

    # Waiting time factor (E2/E2/n Erlang quing theory using 6th order polynomial regression)
    def occupancy_to_waitingfactor(self, occupancy, n_berths):
        x = [10, 20, 30, 40, 50, 60, 70, 80, 90]
        berth1 = [0.055555556,0.125, 0.214285714, 0.333333333, 0.5, 0.75, 1.1667, 2.0, 4.5] 
        berth2 = [0.0006, 0.0065, 0.0235, 0.0516, 0.1181, 0.2222, 0.4125, 0.83, 2.00]
        berth3 = [0,0.0011,0.0062,0.0205,0.0512,0.1103,0.2275,0.46,1.2]
        berth4 = [0,0.0002,0.0019,0.0085,0.0532,0.0639,0.1441,0.33,0.92]

        #Polynomial regression
        coefficients1 = np.polyfit(x, berth1, 6)
        coefficients2 = np.polyfit(x, berth2, 6)
        coefficients3 = np.polyfit(x, berth3, 6)
        coefficients4 = np.polyfit(x, berth4, 6)
        
        #Resulting continuous representation
        def berth1_trend(occupancy):
            return (coefficients1[0]*occupancy**6+coefficients1[1]*occupancy**5+coefficients1[2]*occupancy**4+
                    coefficients1[3]*occupancy**3+coefficients1[4]*occupancy**2+coefficients1[5]*occupancy+coefficients1[6])

        def berth2_trend(occupancy):
            return (coefficients2[0]*occupancy**6+coefficients2[1]*occupancy**5+coefficients2[2]*occupancy**4+
                    coefficients2[3]*occupancy**3+coefficients2[4]*occupancy**2+coefficients2[5]*occupancy+coefficients2[6])

        def berth3_trend(occupancy):
            return (coefficients3[0]*occupancy**6+coefficients3[1]*occupancy**5+coefficients3[2]*occupancy**4+
                    coefficients3[3]*occupancy**3+coefficients3[4]*occupancy**3+coefficients3[5]*occupancy+coefficients3[6])

        def berth4_trend(occupancy):
            return (coefficients4[0]*occupancy**6+coefficients4[1]*occupancy**5+coefficients4[2]*occupancy**4+
                    coefficients4[3]*occupancy**3+coefficients4[4]*occupancy**4+coefficients4[5]*occupancy+coefficients4[6])
        
        x = occupancy*100
        if n_berths == 1:
            return max(0, berth1_trend(x))
        if n_berths == 2:
            return max(0, berth2_trend(x))
        if n_berths == 3:
            return max(0, berth3_trend(x))
        if n_berths == 4:
            return max(0, berth4_trend(x))
        
    # Waiting time factor (E2/E2/n Erlang quing theory using 6th order polynomial regression)  
    def waitingfactor_to_occupancy(self, factor, n_berths):
        factor = factor * 100
        if n_berths == 1:
            return max(1,(19.462 * np.log(factor) - 25.505))/100
        if n_berths == 2:
            return max(1,(14.091 * np.log(factor) + 16.509))/100
        if n_berths == 3:
            return max(1,(12.625 * np.log(factor) + 30.298))/100
        if n_berths == 4:
            return max(1,(11.296 * np.log(factor) + 38.548))/100


# In[8]:


# create berth objects
berth_object = berth_class(**berth_data)


# ## Cranes (cyclic)

# In[9]:


# create cyclic unloader class **will ultimately be placed in package**
class cyclic_properties_mixin(object):
    def __init__(self, t0_quantity, ownership, delivery_time, lifespan, unit_rate, mobilisation_perc, maintenance_perc, 
                 insurance_perc, crew, crane_type, lifting_capacity, hourly_cycles, eff_fact, 
                 utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.t0_quantity          = t0_quantity
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation_perc    = mobilisation_perc
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.crew                 = crew
        self.crane_type           = crane_type
        self.lifting_capacity     = lifting_capacity
        self.hourly_cycles        = hourly_cycles
        self.eff_fact             = eff_fact
        self.utilisation          = utilisation
        self.payload              = int(0.70 * self.lifting_capacity)      #Source: Nemag
        self.peak_capacity        = int(self.payload * self.hourly_cycles) 
        self.effective_capacity   = int(eff_fact * self.peak_capacity)     #Source: TATA steel

# Initial data set, data from Excel_input.xlsx
gantry_crane_data   = {"t0_quantity":0, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 40, "unit_rate": 19500000,"mobilisation_perc": 0.15, 
                      "maintenance_perc": 0.02, "insurance_perc": 0.01, "crew": 3, 
                      "crane_type": 'Gantry crane', "lifting_capacity": 70, "hourly_cycles": 60, "eff_fact": 0.55,
                      "utilisation": 0.80}

harbour_crane_data = {"t0_quantity":0, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 40, "unit_rate": 14000000, "mobilisation_perc": 0.15, 
                      "maintenance_perc": 0.02, "insurance_perc": 0.01, "crew": 3, 
                      "crane_type": 'Harbour crane crane', "lifting_capacity": 40, "hourly_cycles": 40, "eff_fact": 0.55,
                      "utilisation": 0.80}

mobile_crane_data  = {"t0_quantity":0, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 20, "unit_rate": 3325000,"mobilisation_perc": 0.15, 
                      "maintenance_perc": 0.031,"insurance_perc": 0.01, "crew": 3, 
                      "crane_type": 'Mobile crane',"lifting_capacity": 60, "hourly_cycles": 30, "eff_fact": 0.55,
                      "utilisation": 0.80}


# In[10]:


# define cyclic unloader class functions **will ultimately be placed in package**
class cyclic_unloader(cyclic_properties_mixin): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.crane_type != 'Mobile crane':
            self.consumption = 0.3 * self.peak_capacity
        else:
            self.consumption = 485


# In[11]:


# create crane objects
gantry_crane_object  = cyclic_unloader(**gantry_crane_data)
harbour_crane_object = cyclic_unloader(**harbour_crane_data)
mobile_crane_object  = cyclic_unloader(**mobile_crane_data)  


# ## Cranes (continuous)

# In[12]:


# create continuous unloader class **will ultimately be placed in package**
class continuous_properties_mixin(object):
    def __init__(self, t0_quantity, ownership, delivery_time, lifespan, unit_rate, mobilisation_perc, maintenance_perc, 
                 insurance_perc, crew, crane_type, peak_capacity, eff_fact, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.t0_quantity          = t0_quantity
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation_perc    = mobilisation_perc
        self.mobilisation         = int(mobilisation_perc * unit_rate)
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.crew                 = crew
        self.crane_type           = crane_type
        self.peak_capacity        = peak_capacity
        self.eff_fact             = eff_fact
        self.effective_capacity   = eff_fact * peak_capacity
        self.utilisation          = utilisation

# Initial data set, data from Excel_input.xlsx
continuous_screw_data = {"t0_quantity": 0, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 30, "unit_rate": 6900000, "mobilisation_perc": 0.15, 
                         "maintenance_perc": 0.02, "insurance_perc": 0.01, "crew": 2,"crane_type": 'Screw unloader', 
                         "peak_capacity": 700, "eff_fact": 0.55, "utilisation": 0.80}


# In[13]:


# define continuous unloader class functions **will ultimately be placed in package**
class continuous_unloader(continuous_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[14]:


# create screw unloader objects
screw_unloader_object = continuous_unloader(**continuous_screw_data)
cranes_object = [gantry_crane_object, harbour_crane_object, mobile_crane_object, screw_unloader_object]


# ## Storage

# In[15]:


# create storage class **will ultimately be placed in package**
class storage_properties_mixin(object):
    def __init__(self, t0_capacity, ownership, delivery_time, lifespan, unit_rate, mobilisation_min, mobilisation_perc, 
                 maintenance_perc, crew, insurance_perc, storage_type, consumption, silo_capacity, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.t0_capacity          = t0_capacity
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation_min     = mobilisation_min
        self.mobilisation_perc    = mobilisation_perc
        self.maintenance_perc     = maintenance_perc
        self.crew                 = crew
        self.insurance_perc       = insurance_perc
        self.storage_type         = storage_type
        self.consumption          = consumption
        self.silo_capacity        = silo_capacity
        
# Initial data set, data from Excel_input.xlsx
silo_data      = {"t0_capacity": 0, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 30, "unit_rate": 60, 
                  "mobilisation_min": 200000, "mobilisation_perc": 0.003, "maintenance_perc": 0.02, "crew": 1, 
                  "insurance_perc": 0.01, "storage_type": 'Silos', "consumption": 0.002, "silo_capacity": 6000}
warehouse_data = {"t0_capacity": 0, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 30, "unit_rate": 140,
                  "mobilisation_min": 200000, "mobilisation_perc": 0.001, "maintenance_perc": 0.01, "crew": 3, 
                  "insurance_perc": 0.01, "storage_type": 'Warehouse', "consumption": 0.002, "silo_capacity": 'n/a'}


# In[16]:


# define storage class functions **will ultimately be placed in package**
class storage(storage_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[17]:


# create storage objects
silo_object = storage(**silo_data)
warehouse_object = storage(**warehouse_data)
storage_object = [silo_object, warehouse_object]


# ## Loading Station

# In[18]:


# create loading station class **will ultimately be placed in package**
class hinterland_station_properties_mixin(object):
    def __init__(self, t0_capacity, ownership, delivery_time, lifespan, unit_rate, mobilisation, maintenance_perc, 
                 insurance_perc, consumption, crew, utilisation, production, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.t0_capacity      = t0_capacity
        self.ownership        = ownership
        self.delivery_time    = delivery_time
        self.lifespan         = lifespan
        self.unit_rate        = unit_rate
        self.mobilisation     = mobilisation
        self.maintenance_perc = maintenance_perc
        self.insurance_perc   = insurance_perc
        self.consumption      = consumption
        self.crew             = crew
        self.utilisation      = utilisation
        self.production       = production
        
# Initial data set, data from Excel_input.xlsx
hinterland_station_data = {"t0_capacity": 0, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 15, "unit_rate": 800000, "mobilisation": 200000, 
                           "maintenance_perc": 0.02, "consumption": 100, "insurance_perc": 0.01, "crew": 2, "utilisation": 0.80, "production": 800}


# In[19]:


# define loading station class functions **will ultimately be placed in package**
class hinterland_station(hinterland_station_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[20]:


# create loading station objects
station_object = hinterland_station(**hinterland_station_data)


# ## Conveyors

# In[21]:


# create conveyor class **will ultimately be placed in package**
class conveyor_properties_mixin(object):
    def __init__(self, t0_capacity, length, ownership, delivery_time, lifespan, unit_rate, mobilisation, maintenance_perc, insurance_perc, 
                 consumption_constant, consumption_coefficient, crew, utilisation, capacity_steps, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.t0_capacity             = t0_capacity
        self.length                  = length
        self.ownership               = ownership
        self.delivery_time           = delivery_time
        self.lifespan                = lifespan
        self.unit_rate               = unit_rate
        self.mobilisation            = mobilisation
        self.maintenance_perc        = maintenance_perc
        self.insurance_perc          = insurance_perc
        self.consumption_constant    = consumption_constant
        self.consumption_coefficient = consumption_coefficient
        self.crew                    = crew
        self.utilisation             = utilisation
        self.capacity_steps          = capacity_steps

# Initial data set, data from Excel_input.xlsx
quay_conveyor_data = {"t0_capacity": 0, "length": 200, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 10, 
                      "unit_rate": 6, "mobilisation": 30000,"maintenance_perc": 0.10, "insurance_perc": 0.01, 
                      "consumption_constant": 81,"consumption_coefficient":0.08, "crew": 1, "utilisation": 0.80, 
                      "capacity_steps": 400}

hinterland_conveyor_data = {"t0_capacity": 0, "length": 200, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 10, "mobilisation": 30000, 
                            "unit_rate": 6, "maintenance_perc": 0.10, "insurance_perc": 0.01, "consumption_constant": 81, 
                            "consumption_coefficient":0.08, "crew": 1, "utilisation": 0.80, "capacity_steps": 400}


# In[22]:


# define conveyor class functions **will ultimately be placed in package**
class conveyor(conveyor_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[23]:


# create loading station objects
quay_conveyor_object = conveyor(**quay_conveyor_data)
hinterland_conveyor_object = conveyor(**hinterland_conveyor_data)

