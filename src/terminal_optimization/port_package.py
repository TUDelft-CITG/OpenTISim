
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# In[2]:


def import_notebook():
    year              = parameters.year
    operational_hours = parameters.operational_hours


# # Terminal Infrastructure

# ## Quay wall

# In[3]:


# create quay wall class **will ultimately be placed in package**
class quay_wall_properties_mixin(object):
    def __init__(self, ownership, lifespan, mobilisation_min, mobilisation_perc, maintenance_perc, insurance_perc, length, depth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.lifespan             = lifespan
        self.mobilisation_min     = mobilisation_min
        self.mobilisation_perc    = mobilisation_perc
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.length               = length
        self.depth                = depth

# Initial data set, data from Excel_input.xlsx
quay_data = {"ownership": 'Port authority', "lifespan": 50, "mobilisation_min": 2500000,
             "mobilisation_perc": 0.02, "maintenance_perc": 0.01, "insurance_perc": 0.01,"length": 400, "depth": 14} 


# In[4]:


# define quay wall class functions **will ultimately be placed in package**
class quay_wall(quay_wall_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def unit_rate_calc(self):
        self.unit_rate = 757.20 * (self.depth+5)**1.2878 # van Gijt (2010)
    
    def original_value_calc(self):
        self.original_value = int(self.length * self.unit_rate)
        
    def mobilisation_calc(self):
        self.mobilisation = int(max((self.delta * self.unit_rate * self.mobilisation_perc), self.mobilisation_min))
        
    def maintenance_calc(self):
        self.maintenance = int(self.original_value * self.maintenance_perc)
        
    def insurance_calc(self):
        self.insurance = int(self.original_value * self.insurance_perc)


# In[5]:


# create objects **will ultimately be placed in notebook**
quay = quay_wall(**quay_data)


# ## Berths

# In[6]:


# create berth class
class berth_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[7]:


# define berth functions 
class berths(berth_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# ## Cranes (cyclic)

# In[8]:


# create cyclic unloader class **will ultimately be placed in package**
class cyclic_properties_mixin(object):
    def __init__(self, ownership, lifespan, unit_rate, mobilisation_perc, maintenance_perc, insurance_perc, consumption, crew, unloader_type, lifting_capacity, hourly_cycles, eff_fact, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
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
gantry_data        = {"ownership": 'Terminal operator', "lifespan": 40, "unit_rate": 19500000,"mobilisation_perc": 0.15, 
                      "maintenance_perc": 0.02, "insurance_perc": 0.01,"consumption": 0, "crew": 3, 
                      "unloader_type": 'Gantry crane', "lifting_capacity": 70, "hourly_cycles": 60, "eff_fact": 0.55,
                      "utilisation": 0.80}

harbour_crane_data = {"ownership": 'Terminal operator', "lifespan": 40, "unit_rate": 14000000, "mobilisation_perc": 0.15, 
                      "maintenance_perc": 0.02, "insurance_perc": 0.01,"consumption": 0, "crew": 3, 
                      "unloader_type": 'Harbour crane crane', "lifting_capacity": 40, "hourly_cycles": 40, "eff_fact": 0.55,
                      "utilisation": 0.80}

mobile_crane_data  = {"ownership": 'Terminal operator', "lifespan": 20, "unit_rate": 3325000,"mobilisation_perc": 0.15, 
                      "maintenance_perc": 0.031,"insurance_perc": 0.01,"consumption": 485, "crew": 3, 
                      "unloader_type": 'Mobile crane',"lifting_capacity": 60, "hourly_cycles": 30, "eff_fact": 0.55,
                      "utilisation": 0.80}


# In[9]:


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


# In[10]:


# create objects **will ultimately be placed in notebook**
gantry_cranes   = cyclic_unloader(**gantry_data)
harbour_cranes  = cyclic_unloader(**harbour_crane_data)  
mobile_cranes   = cyclic_unloader(**mobile_crane_data) 


# ## Cranes (continuous)

# In[11]:


# create continuous unloader class **will ultimately be placed in package**
class continuous_properties_mixin(object):
    def __init__(self, ownership, lifespan, unit_rate, mobilisation_perc, maintenance_perc, insurance_perc, crew, unloader_type, peak_capacity, eff_fact, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
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
        self.utilisation          = utilisation

# Initial data set, data from Excel_input.xlsx
continuous_screw_data = {"ownership": 'Terminal operator', "lifespan": 30, "unit_rate": 6900000, "mobilisation_perc": 0.15, 
                         "maintenance_perc": 0.02, "insurance_perc": 0.01, "crew": 2,"unloader_type": 'Screw unloader', 
                         "peak_capacity": 700, "eff_fact": 0.55, "utilisation": 0.80}


# In[12]:


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


# In[13]:


# create objects **will ultimately be placed in notebook**
screw_unloaders = continuous_unloader(**continuous_screw_data)


# ## Conveyors

# In[14]:


# create conveyor class **will ultimately be placed in package**
class conveyor_properties_mixin(object):
    def __init__(self, ownership, lifespan, mobilisation, maintenance_perc, insurance_perc, crew, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.lifespan             = lifespan
        self.mobilisation         = mobilisation
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.crew                 = crew
        self.utilisation          = utilisation

# Initial data set, data from Excel_input.xlsx
conveyor_data = {"ownership": 'Terminal operator', "lifespan": 10, "mobilisation": 30000, 
                 "maintenance_perc": 0.10, "insurance_perc": 0.01, "crew": 0.5, "utilisation": 0.80}


# In[15]:


# define conveyor class functions **will ultimately be placed in package**
class conveyor(conveyor_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def capacity_calc(self):
        self.capacity = int(np.ceil((gantry_cranes.peak_capacity   * gantry_cranes.quantity +                                     harbour_cranes.peak_capacity  * harbour_cranes.quantity +                                     mobile_cranes.peak_capacity   * mobile_cranes.quantity +                                     screw_unloaders.peak_capacity * screw_unloaders.quantity)/400)*400)
    
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
        
    def delta_calc(self):
        self.delta = int(np.ceil((gantry_cranes.peak_capacity   * gantry_cranes.delta  +                                  harbour_cranes.peak_capacity  * harbour_cranes.delta +                                  mobile_cranes.peak_capacity   * mobile_cranes.delta  +                                  screw_unloaders.peak_capacity * screw_unloaders.delta)/400)*400)


# In[16]:


# create objects **will ultimately be placed in notebook**
conveyor_quay       = conveyor(**conveyor_data)
conveyor_hinterland = conveyor(**conveyor_data)

conveyor_quay.length       = 500
conveyor_hinterland.length = 500


# ## Storage

# In[17]:


# create storage class **will ultimately be placed in package**
class storage_properties_mixin(object):
    def __init__(self, ownership, lifespan, unit_rate, mobilisation_min, mobilisation_perc, maintenance_perc, insurance_perc, storage_type, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation_min     = mobilisation_min
        self.mobilisation_perc    = mobilisation_perc
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.storage_type         = storage_type
        self.utilisation          = utilisation
        
# Initial data set, data from Excel_input.xlsx
silo_data      = {"ownership": 'Terminal operator', "lifespan": 30, "unit_rate": 60, 
                  "mobilisation_min": 200000, "mobilisation_perc": 0.02, "maintenance_perc": 0.02, 
                  "insurance_perc": 0.01, "storage_type": 'Silos', "utilisation": 0.80}
warehouse_data = {"ownership": 'Terminal operator', "lifespan": 30, "unit_rate": 140,
                  "mobilisation_min": 200000, "mobilisation_perc": 0.02, "maintenance_perc": 0.01, 
                  "insurance_perc": 0.01, "storage_type": 'Warehouse', "utilisation": 0.80}


# In[18]:


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


# In[19]:


# create objects **will ultimately be placed in notebook**     
silos     = storage(**silo_data)
warehouse = storage(**warehouse_data)


# ## Loading Station

# In[20]:


# create loading station class **will ultimately be placed in package**
class hinterland_station_properties_mixin(object):
    def __init__(self, ownership, lifespan, unit_rate, mobilisation, maintenance_perc, insurance_perc, crew, utilisation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership            = ownership
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation         = mobilisation
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.crew                 = crew
        self.utilisation          = utilisation
        
# Initial data set, data from Excel_input.xlsx
hinterland_station_data = {"ownership": 'Terminal operator', "lifespan": 15, "unit_rate": 4000, "mobilisation": 100000, 
                           "maintenance_perc": 0.02, "insurance_perc": 0.01, "crew": 2, "utilisation": 0.80}


# In[21]:


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


# In[22]:


# create objects **will ultimately be placed in notebook**
loading_station = hinterland_station(**hinterland_station_data)


# # Business Logic

# ## Revenue calc

# In[23]:


# create revenue class **will ultimately be placed in package**
class revenue_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


# In[24]:


# define revenue class functions **will ultimately be placed in package**
class revenue_class(revenue_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self):
        self.maize   = int(maize.throughput   * maize.handling_fee)
        self.soybean = int(soybean.throughput * soybean.handling_fee)
        self.wheat   = int(wheat.throughput   * wheat.handling_fee)
        self.total   = int(self.maize + self.soybean + self.wheat)


# In[25]:


# create objects **will ultimately be placed in notebook**
revenue = revenue_class()


# ## Capex calc

# In[26]:


# create capex class **will ultimately be placed in package**
class capex_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[27]:


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


# In[28]:


# create objects **will ultimately be placed in notebook**
capex = capex_class()


# ## Labour calc

# In[29]:


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


# In[30]:


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


# In[31]:


# create objects **will ultimately be placed in notebook**
labour = labour_class(**labour_data)


# ## Maintenance calc

# In[32]:


# create maintenance class **will ultimately be placed in package**
class maintenance_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[33]:


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


# In[34]:


# create objects **will ultimately be placed in notebook**
maintenance = maintenance_class()


# ## Energy consumption calc

# In[35]:


# create energy consumption class **will ultimately be placed in package**
class energy_properties_mixin(object):
    def __init__(self, price, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = price

# Initial data
energy_data = {"price": 0.10}


# In[36]:


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


# In[37]:


# create objects **will ultimately be placed in notebook**
energy = energy_class(**energy_data)


# ## Demurrage calc

# In[38]:


# create demurrage class **will ultimately be placed in package**
class demurrage_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[39]:


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


# In[40]:


# create objects **will ultimately be placed in notebook**
demurrage = demurrage_class()


# In[41]:


# [Test] demurrage 

#demurrage.calc()
#demurrage.__dict__


# ## Residual value calc

# ## Lease calc

# ## WACC calc

# ## Escalation calc

# ## Profit calc

# ## NPV calc

# # Simulation
