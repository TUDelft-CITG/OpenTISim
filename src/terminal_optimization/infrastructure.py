import numpy as np
import pandas as pd


# # Terminal Infrastructure classes
# ### Quay wall

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

# define quay wall class functions
class quay_wall_class(quay_wall_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# create quay object
quay_object = quay_wall_class(**quay_data)

# ### Berths
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

# create berth objects
berth_object = berth_class(**berth_data)

# ## Cranes (cyclic)
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

# define cyclic unloader class functions **will ultimately be placed in package**
class cyclic_unloader(cyclic_properties_mixin): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.crane_type != 'Mobile crane':
            self.consumption = 0.3 * self.peak_capacity
        else:
            self.consumption = 485

# create crane objects
gantry_crane_object  = cyclic_unloader(**gantry_crane_data)
harbour_crane_object = cyclic_unloader(**harbour_crane_data)
mobile_crane_object  = cyclic_unloader(**mobile_crane_data)  

# ## Cranes (continuous)
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

# define continuous unloader class functions **will ultimately be placed in package**
class continuous_unloader(continuous_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# create screw unloader objects
screw_unloader_object = continuous_unloader(**continuous_screw_data)
cranes_object = [gantry_crane_object, harbour_crane_object, mobile_crane_object, screw_unloader_object]

# ## Storage
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

# define storage class functions **will ultimately be placed in package**
class storage(storage_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# create storage objects
silo_object = storage(**silo_data)
warehouse_object = storage(**warehouse_data)
storage_object = [silo_object, warehouse_object]

# ## Loading Station
# create loading station class **will ultimately be placed in package**
class hinterland_station_properties_mixin(object):
    def __init__(self, t0_capacity, ownership, delivery_time, lifespan, unit_rate, mobilisation, maintenance_perc, 
                 insurance_perc, consumption, crew, utilisation, capacity_steps, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.t0_capacity          = t0_capacity
        self.ownership            = ownership
        self.delivery_time        = delivery_time
        self.lifespan             = lifespan
        self.unit_rate            = unit_rate
        self.mobilisation         = mobilisation
        self.maintenance_perc     = maintenance_perc
        self.insurance_perc       = insurance_perc
        self.consumption          = consumption
        self.crew                 = crew
        self.utilisation          = utilisation
        self.capacity_steps       = capacity_steps
        
# Initial data set, data from Excel_input.xlsx
hinterland_station_data = {"t0_capacity": 0, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 15, "unit_rate": 4000, "mobilisation": 100000, 
                           "maintenance_perc": 0.02, "consumption": 0.25, "insurance_perc": 0.01, "crew": 2, "utilisation": 0.80, "capacity_steps": 300}

# define loading station class functions **will ultimately be placed in package**
class hinterland_station(hinterland_station_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# create loading station objects
station_object = hinterland_station(**hinterland_station_data)


# ## Conveyors
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
quay_conveyor_data = {"t0_capacity": 0, "length": 500, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 10, 
                      "unit_rate": 6, "mobilisation": 30000,"maintenance_perc": 0.10, "insurance_perc": 0.01, 
                      "consumption_constant": 81,"consumption_coefficient":0.08, "crew": 1, "utilisation": 0.80, 
                      "capacity_steps": 400}

hinterland_conveyor_data = {"t0_capacity": 0, "length": 500, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 10, "mobilisation": 30000, 
                            "unit_rate": 6, "maintenance_perc": 0.10, "insurance_perc": 0.01, "consumption_constant": 81, 
                            "consumption_coefficient":0.08, "crew": 1, "utilisation": 0.80, "capacity_steps": 400}

# define conveyor class functions **will ultimately be placed in package**
class conveyor(conveyor_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# create loading station objects
quay_conveyor_object = conveyor(**quay_conveyor_data)
hinterland_conveyor_object = conveyor(**hinterland_conveyor_data)