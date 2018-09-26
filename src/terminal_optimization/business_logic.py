
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# # Terminal Throughput class

# In[2]:


class throughput_class():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, berths, cranes, operational_hours):
        
        # Throughput over the entire quay 
        if berths[0].online_quantity == 0:
            self.quay = 0
        else:
            quay_throughput = []
            for i in range (len(berths)):
                occupancy = berths[i].current_occupancy
                eff_unloading_rate = []
                for j in range (4):
                    for k in range (len(cranes[j])):
                        if cranes[j][k].berth == i+1:
                            eff_unloading_rate.append(cranes[j][k].effective_capacity * cranes[j][k].utilisation)
                online_eff_unloading_rate = np.sum(eff_unloading_rate)
                berths[i].throughput = online_eff_unloading_rate * occupancy
                quay_throughput.append(berths[i].throughput)
            self.quay = np.sum(quay_throughput) * operational_hours
            
        self.total = self.quay
        
        return 


# In[ ]:


def throughput_calc(throughputs, berths, cranes, year, timestep, operational_hours):
    throughputs.append(throughput_class())
    index = len(throughputs)-1
    throughputs[index].year = year
    throughputs[index].calc(berths, cranes, operational_hours)
    #print ('Terminal throughput (t/y):',throughputs[timestep].total)
    #print ()
    return throughputs


# # Business Logic classes
# ### Revenue

# In[2]:


# create revenue class
class revenue_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


# In[ ]:


# define revenue class functions 
class revenue_class(revenue_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self, commodities, throughputs, timestep):
        maize   = commodities[0]
        soybean = commodities[1]
        wheat   = commodities[2]
        
        maize_throughput   = min(maize.demand[timestep], throughputs[timestep].total)
        soybean_throughput = min(maize_throughput+soybean.demand[timestep], throughputs[timestep].total)
        wheat_throughput   = min(maize_throughput+soybean_throughput+wheat.demand[timestep], throughputs[timestep].total)

        self.maize   = int(maize_throughput   * maize.handling_fee)
        self.soybean = int(soybean_throughput * soybean.handling_fee)
        self.wheat   = int(wheat_throughput   * wheat.handling_fee)
        self.total   = int(self.maize + self.soybean + self.wheat)


# In[ ]:


def revenue_calc(revenues, commodities, throughputs, year, timestep):
    revenues.append(revenue_class())
    index = len(revenues)-1
    revenues[index].year = year
    revenues[index].calc(commodities, throughputs, timestep)
    #print ('Total revenue ($):', revenues[timestep].total)
    #print ()
    return revenues


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
    
    def calc(self, quays, cranes, storage, stations, q_conveyors, h_conveyors):
        
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


# In[ ]:


def capex_calc(capex, quays, cranes, storage, stations, q_conveyors, h_conveyors, year, timestep):
    capex.append(capex_class())
    index = len(capex)-1
    capex[index].year = year
    capex[index].calc(quays, cranes, storage, stations, q_conveyors, h_conveyors)
    #print ('Quay capex($)           ', capex[timestep].quay)
    #print ('Crane capex($)          ', capex[timestep].cranes)
    #print ('Storage capex($)        ', capex[timestep].storage)
    #print ('Conveyor capex($)       ', capex[timestep].conveyors)
    #print ('Loading station capex($)', capex[timestep].loading_stations)
    #print ('Total capex ($):        ', capex[timestep].total)
    #print ()
    return capex


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


# In[ ]:


# define labour class functions 
class labour_class(labour_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, cranes, storage, stations, q_conveyors, h_conveyors, operational_hours):
        
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
                storage_shifts.append(int(np.ceil(operational_hours * asset.crew / self.shift_length)))
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
        
        self.total = int(self.international_salary * self.international_staff + self.local_salary * self.local_staff +                           self.operational_salary   * self.operational_staff)


# In[ ]:


def labour_calc(labour, cranes, storage, stations, q_conveyors, h_conveyors, year, timestep, operational_hours):
    labour.append(labour_class(**labour_data))
    index = len(labour)-1
    labour[index].year = year
    labour[index].calc(cranes, storage, stations, q_conveyors, h_conveyors, operational_hours)
    #print ('International staff costs($):', labour[timestep].international_salary * labour[timestep].international_staff)
    #print ('Local staff costs($):        ', labour[timestep].local_salary         * labour[timestep].local_staff)
    #print ('Operational staff costs($):  ', labour[timestep].operational_salary   * labour[timestep].operational_staff)
    #print ('Total costs($):', labour[timestep].total)
    #print ()
    return labour


# ### Maintenance

# In[7]:


# create maintenance class 
class maintenance_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define maintenance class functions 
class maintenance_class(maintenance_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self, quays, cranes, storage, stations, q_conveyors, h_conveyors, year):
        
        # Maintenance costs associated with the quay
        quay_maintenance = []        
        for i in range(len(quays)):
            if quays[i].online_date <= year:
                unit_rate  = int(quays[i].Gijt_constant * (quays[i].depth*2 + quays[i].freeboard)**quays[i].Gijt_coefficient)
                length     = quays[i].length
                percentage = quays[i].maintenance_perc
                maintenance = unit_rate * length * percentage
                quay_maintenance.append(maintenance)
        self.quay = int(np.sum(quay_maintenance))
            
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
        
        self.total = int(self.quay + self.cranes + self.storage + self.loading_stations + self.conveyors)


# In[ ]:


def maintenance_calc(maintenance, quays, cranes, storage, stations, q_conveyors, h_conveyors, year, timestep):
    maintenance.append(maintenance_class())
    index = len(maintenance)-1
    maintenance[index].year = year
    maintenance[index].calc(quays, cranes, storage, stations, q_conveyors, h_conveyors, year)
    #print ('Quay maintenance costs($):    ', maintenance[timestep].quay)
    #print ('Crane maintenance costs($):   ', maintenance[timestep].cranes)
    #print ('Storage maintenance costs($): ', maintenance[timestep].storage)
    #print ('Conveyor maintenance costs($):', maintenance[timestep].conveyors)
    #print ('Total maintenance costs($):', maintenance[timestep].total)
    #print ()
    return maintenance


# ### Energy costs

# In[ ]:


# create energy consumption class 
class energy_properties_mixin(object):
    def __init__(self, price, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = price

# Initial data
energy_data = {"price": 0.10}


# In[ ]:


# define energy consumption class functions 
class energy_class(energy_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, berths, cranes, storage, stations, q_conveyors, h_conveyors, year, operational_hours):
            
        # Energy costs associated with the cranes
        crane_energy = []
        for i in range (4):
            for j in range (cranes[i][0].online_quantity):
                consumption = cranes[i][j].consumption
                occupancy = berths[i].current_occupancy
                utilisation = cranes[i][j].utilisation
                hours = operational_hours * occupancy * utilisation
                crane_energy.append(consumption * hours)
        self.cranes = int(np.sum(crane_energy) * self.price)
        
        # Energy costs associated with the storage
        storage_energy = []
        for i in range (2):
            consumption = storage[i][0].consumption
            capacity    = storage[i][0].online_capacity
            hours       = operational_hours
            storage_energy.append(consumption * capacity * hours)
        self.storage = int(np.sum(storage_energy) * self.price)
            
        # Energy costs associated with the loading stations
        station_energy = []
        consumption = stations[0].consumption
        capacity    = stations[0].online_capacity
        utilisation = stations[0].utilisation
        hours       = operational_hours * utilisation
        station_energy.append(consumption * capacity * hours)
        self.stations = int(np.sum(station_energy) * self.price)
        
        # Energy costs associated with the conveyors
        conveyor_energy = []
        
        for i in range(len(q_conveyors)):
            if not 'online_date' in dir(q_conveyors[i]):
                break
            if q_conveyors[i].online_date <= year:
                consumption = q_conveyors[i].capacity * q_conveyors[i].consumption_coefficient + q_conveyors[i].consumption_constant
                hours       = operational_hours * berths[0].current_occupancy
                usage       = consumption * hours
                conveyor_energy.append(usage)
        for i in range(len(h_conveyors)):
            if not 'online_date' in dir(h_conveyors[i]):
                break
            if h_conveyors[i].online_date <= year:
                consumption = h_conveyors[i].capacity * h_conveyors[i].consumption_coefficient + h_conveyors[i].consumption_constant
                hours       = operational_hours * stations[0].utilisation
                usage       = consumption * hours
                conveyor_energy.append(usage)
        self.conveyors = int(np.sum(conveyor_energy) * self.price)

        self.total = int(self.cranes + self.storage + self.stations + self.conveyors)


# In[ ]:


def energy_calc(energy, berths, cranes, storage, stations, q_conveyors, h_conveyors, year, operational_hours, timestep):
    energy.append(energy_class(**energy_data))
    index = len(energy)-1
    energy[index].year = year
    energy[index].calc(berths, cranes, storage, stations, q_conveyors, h_conveyors, year, operational_hours)
    #print ('Crane energy costs($):          ', energy[timestep].cranes)
    #print ('Storage energy costs($):        ', energy[timestep].storage)
    #print ('Loading station energy costs($):', energy[timestep].stations)
    #print ('Conveyor energy costs($):       ', energy[timestep].conveyors)
    #print ('Total energy costs($):', energy[timestep].total)
    #print ()
    return energy


# ### Insurance costs

# In[ ]:


# create insurance cost class 
class insurance_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define insurance cost class functions 
class insurance_class(insurance_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, quays, cranes, storage, stations, q_conveyors, h_conveyors, year):

        # Insurance costs associated with the quay
        quay_insurance = []        
        for i in range(len(quays)):
            if quays[i].online_date <= year:
                unit_rate  = int(quays[i].Gijt_constant * (quays[i].depth*2 + quays[i].freeboard)**quays[i].Gijt_coefficient)
                length     = quays[i].length
                percentage = quays[i].insurance_perc
                insurance  = unit_rate * length * percentage
                quay_insurance.append(insurance)
        self.quay = int(np.sum(quay_insurance))
        
        # Insurance costs associated with the cranes        
        crane_insurance = [] 
        for i in range (4):
            for j in range(cranes[i][0].online_quantity):
                unit_rate  = cranes[i][j].unit_rate
                percentage = cranes[i][j].insurance_perc
                insurance  = unit_rate * percentage
                crane_insurance.append(insurance)
        self.cranes = int(np.sum(quay_insurance))

        # Insurance costs associated with storage
        storage_insurance = [] 
        for i in range (2):
            for j in range(len(storage[i])):
                if not 'online_date' in dir(storage[i][j]):
                    break
                if storage[i][j].online_date <= year:
                    unit_rate  = storage[i][j].unit_rate
                    capacity   = storage[i][j].capacity
                    percentage = storage[i][j].insurance_perc
                    insurance  = unit_rate * capacity * percentage
                    storage_insurance.append(insurance)
        self.storage = int(np.sum(storage_insurance))
        
        # Insurance costs associated with loading stations
        station_insurance = [] 
        for i in range(len(stations)):
            if not 'online_date' in dir(storage[i]):
                break
            if storage[i].online_date <= year:
                unit_rate  = storage[i].unit_rate
                capacity   = storage[i].capacity
                percentage = storage[i].insurance_perc
                insurance  = unit_rate * capacity * percentage
                station_insurance.append(insurance)
        self.stations = int(np.sum(station_insurance))
        
        # Insurance costs associated with quay conveyors
        quay_conveyor_insurance = [] 
        for i in range(len(q_conveyors)):
            if not 'online_date' in dir(q_conveyors[i]):
                break
            if q_conveyors[i].online_date <= year:
                unit_rate  = q_conveyors[i].unit_rate * q_conveyors[i].length
                capacity   = q_conveyors[i].capacity
                percentage = q_conveyors[i].insurance_perc
                insurance  = unit_rate * capacity * percentage
                quay_conveyor_insurance.append(insurance)
                
        # Insurance costs associated with hinterland conveyors
        hinterland_conveyor_insurance = [] 
        for i in range(len(h_conveyors)):
            if not 'online_date' in dir(h_conveyors[i]):
                break
            if h_conveyors[i].online_date <= year:
                unit_rate  = h_conveyors[i].unit_rate * h_conveyors[i].length
                capacity   = h_conveyors[i].capacity
                percentage = h_conveyors[i].insurance_perc
                insurance  = unit_rate * capacity * percentage
                quay_conveyor_insurance.append(insurance)     
        self.conveyors = int(np.sum(quay_conveyor_insurance) + np.sum(hinterland_conveyor_insurance))
        
        self.total = int(self.quay + self.cranes + self.storage + self.stations + self.conveyors)


# In[ ]:


def insurance_calc(insurance, quays, cranes, storage, stations, q_conveyors, h_conveyors, year, timestep):
    insurance.append(insurance_class())
    index = len(insurance)-1
    insurance[index].year = year
    insurance[index].calc(quays, cranes, storage, stations, q_conveyors, h_conveyors, year)
    #print ('Total insurance costs($):', insurance[timestep].total)
    #print ()
    return insurance


# ### Lease costs

# In[5]:


# create energy consumption class 
class lease_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define lease cost class functions 
class lease_class(lease_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self):
        self.total = 0 


# In[ ]:


def lease_calc(lease, year, timestep):
    lease.append(lease_class())
    index = len(lease)-1
    lease[index].year = year
    lease[index].calc()
    #print ('Total lease costs($):', lease[timestep].total)
    #print ()
    return lease


# ### Demurrage costs

# In[ ]:


# create demurrage class
class demurrage_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define demurrage class functions 
class demurrage_class(demurrage_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
    def calc(self, berths, handysize, handymax, panamax, timestep):
        
        # Calculate berth unloading rate and occupancy
        service_rate = []
        occupancy = []
        for i in range (len(berths)):
            service_rate.append(berths[i].eff_unloading_rate)
            occupancy.append(berths[i].current_occupancy)
        service_rate = np.average(service_rate)
        occupancy    = np.average(occupancy)
        n_berths     = berths[0].online_quantity 
        
        if n_berths == 0:        
            self.handysize = 0
            self.handymax  = 0
            self.panamax   = 0
            self.total     = 0
            
        if n_berths != 0:  
            # Waiting time factor (E2/E/n quing theory using 4th order polynomial regression)
            if n_berths == 1:
                factor = max(0, 79.726* occupancy **4 - 126.47* occupancy **3 + 70.660* occupancy **2 - 14.651* occupancy + 0.9218)
            if n_berths == 2:
                factor = max(0, 29.825* occupancy **4 - 46.489* occupancy **3 + 25.656* occupancy **2 - 5.3517* occupancy + 0.3376)
            if n_berths == 3:
                factor = max(0, 19.362* occupancy **4 - 30.388* occupancy **3 + 16.791* occupancy **2 - 3.5457* occupancy + 0.2253)
            if n_berths == 4:
                factor = max(0, 17.334* occupancy **4 - 27.745* occupancy **3 + 15.432* occupancy **2 - 3.2725* occupancy + 0.2080)
            if n_berths == 5:
                factor = max(0, 11.149* occupancy **4 - 17.339* occupancy **3 + 9.4010* occupancy **2 - 1.9687* occupancy + 0.1247)
            if n_berths == 6:
                factor = max(0, 10.512* occupancy **4 - 16.390* occupancy **3 + 8.8292* occupancy **2 - 1.8368* occupancy + 0.1158)
            if n_berths == 7:
                factor = max(0, 8.4371* occupancy **4 - 13.226* occupancy **3 + 7.1446* occupancy **2 - 1.4902* occupancy + 0.0941)

            # Calculate total time at port
            costs = []
            vessels = [handysize, handymax, panamax]
            for i in range (3):
                service_time   = vessels[i].call_size/service_rate
                mooring_time   = vessels[i].mooring_time
                waiting_time   = factor * service_time
                berth_time     = service_time + mooring_time 
                port_time      = berth_time + waiting_time
                penalty_time   = max(0, port_time - vessels[i].all_turn_time)
                n_calls        = vessels[i].calls[timestep]
                demurrage_time = penalty_time * n_calls
                demurrage_cost = demurrage_time * vessels[i].demurrage_rate
                costs.append(demurrage_cost)

            self.handysize = costs[0]
            self.handymax  = costs[1]
            self.panamax   = costs[2]
            self.total     = np.sum(costs)


# In[ ]:


def demurrage_calc(demurrage, year, berths, handysize, handymax, panamax, timestep):
    demurrage.append(demurrage_class())
    index = len(demurrage)-1
    demurrage[index].year = year
    demurrage[index].calc(berths, handysize, handymax, panamax, timestep)
    #print ('Total demurrage costs($):', demurrage[timestep].total)
    #print ()
    return demurrage


# ### Residual values

# In[ ]:


# create residual value class 
class residual_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define residual value class functions 
class residual_class(residual_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, quays, cranes, storage, stations, q_conveyors, h_conveyors, year):
        # All assets are presumed to depreciate linearly
        
        # Residual value associated with the quay
        quay_residual = []        
        for i in range(len(quays)):
            if quays[i].online_date <= year:
                unit_rate  = int(quays[i].Gijt_constant * (quays[i].depth*2 + quays[i].freeboard)**quays[i].Gijt_coefficient)
                length     = quays[i].length
                ini_value  = unit_rate * length
                age        = year - quays[i].online_date
                depreciation_rate = 1/quays[i].lifespan
                current_value = ini_value * (1 - age * depreciation_rate)  
                quay_residual.append(current_value)
        self.quay = int(np.sum(quay_residual))
        
        # Current value associated with the cranes        
        cranes_residual = [] 
        for i in range (4):
            for j in range(cranes[i][0].online_quantity):
                ini_value  = cranes[i][j].unit_rate
                age        = year - cranes[i][j].online_date
                depreciation_rate = 1/cranes[i][j].lifespan
                current_value = ini_value * (1 - age * depreciation_rate)  
                cranes_residual.append(current_value)
        self.cranes = int(np.sum(cranes_residual))

        # Residual value associated with storage
        storage_residual = [] 
        for i in range (2):
            for j in range(len(storage[i])):
                if not 'online_date' in dir(storage[i][j]):
                    break
                if storage[i][j].online_date <= year:
                    unit_rate  = storage[i][j].unit_rate
                    capacity   = storage[i][j].capacity
                    ini_value  = unit_rate * capacity
                    age        = year - storage[i][j].online_date
                    depreciation_rate = 1/storage[i][j].lifespan
                    current_value = ini_value * (1 - age * depreciation_rate)  
                    storage_residual.append(current_value)
        self.storage = int(np.sum(storage_residual))
        
        # Residual value associated with loading stations
        station_residual = [] 
        for i in range(len(stations)):
            if not 'online_date' in dir(stations[i]):
                break
            if stations[i].online_date <= year:
                unit_rate  = stations[i].unit_rate
                capacity   = stations[i].capacity
                ini_value  = unit_rate * capacity
                age        = year - stations[i].online_date
                depreciation_rate = 1/stations[i].lifespan
                current_value = ini_value * (1 - age * depreciation_rate)  
                station_residual.append(current_value)
        self.stations = int(np.sum(station_residual))
        
        # Residual value associated with quay conveyors
        quay_conveyor_residual = [] 
        for i in range(len(q_conveyors)):
            if not 'online_date' in dir(q_conveyors[i]):
                break
            if q_conveyors[i].online_date <= year:
                unit_rate  = q_conveyors[i].unit_rate * q_conveyors[i].length
                capacity   = q_conveyors[i].capacity
                ini_value  = unit_rate * capacity
                age        = year - q_conveyors[i].online_date
                depreciation_rate = 1/q_conveyors[i].lifespan
                current_value = ini_value * (1 - age * depreciation_rate)  
                quay_conveyor_residual.append(current_value)
                
        # Residual value associated with hinterland conveyors
        hinterland_conveyor_residual = [] 
        for i in range(len(h_conveyors)):
            if not 'online_date' in dir(h_conveyors[i]):
                break
            if h_conveyors[i].online_date <= year:
                unit_rate  = h_conveyors[i].unit_rate * h_conveyors[i].length
                capacity   = h_conveyors[i].capacity
                ini_value  = unit_rate * capacity
                age        = year - h_conveyors[i].online_date
                depreciation_rate = 1/h_conveyors[i].lifespan
                current_value = ini_value * (1 - age * depreciation_rate)  
                hinterland_conveyor_residual.append(current_value)
        self.conveyors = int(np.sum(quay_conveyor_residual) + np.sum(hinterland_conveyor_residual))
        
        self.total = int(self.quay + self.cranes + self.storage + self.stations + self.conveyors)


# In[ ]:


def residual_calc(residuals, quays, cranes, storage, stations, q_conveyors, h_conveyors, assets, year, timestep):
    residuals.append(residual_class())
    index = len(residuals)-1
    residuals[index].year = year
    residuals[index].calc(quays, cranes, storage, stations, q_conveyors, h_conveyors, year)
    #print ('Total residual value ($)', residuals[timestep].total)
    #print ()
    return residuals


# ### Profits

# In[ ]:


# create profit class 
class profit_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define profit class functions 
class profit_class(profit_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, revenues, capex, labour, maintenance, energy, insurance, lease, demurrage, residuals, 
             window, timestep, year, start_year):
        
        self.revenues    = revenues[timestep].total
        self.capex       = capex[timestep].total       * -1
        self.labour      = labour[timestep].total      * -1
        self.maintenance = maintenance[timestep].total * -1
        self.energy      = energy[timestep].total      * -1
        self.insurance   = insurance[timestep].total   * -1
        self.lease       = lease[timestep].total       * -1
        self.demurrage   = demurrage[timestep].total   * -1
        if year == start_year + window: 
            self.residuals = residuals[timestep].total
        else:
            self.residuals = 0
            
        self.total = int(self.revenues + self.capex + self.labour + self.maintenance + self.energy + self.insurance +
                         self.lease + self.demurrage + self.residuals)


# In[ ]:


def profit_calc(profits, revenues, capex, labour, maintenance, energy, insurance, lease, demurrage, residuals, 
                window, timestep, year, start_year):
    profits.append(profit_class())
    index = len(profits)-1
    profits[index].year = year
    profits[index].calc(revenues, capex, labour, maintenance, energy, insurance, lease, demurrage, residuals, 
                        window, timestep, year, start_year)
    #print ('Total profit/loss ($)', profits[timestep].total)
    #print ()
    return profits


# ### OPEX

# In[1]:


# create opex class 
class opex_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define opex class functions 
class opex_class(opex_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, labour, maintenance, energy, insurance, lease, demurrage, timestep):
        
        self.labour      = labour[timestep].total      * -1
        self.maintenance = maintenance[timestep].total * -1
        self.energy      = energy[timestep].total      * -1
        self.insurance   = insurance[timestep].total   * -1
        self.lease       = lease[timestep].total       * -1
        self.demurrage   = demurrage[timestep].total   * -1
            
        self.total = int(self.labour + self.maintenance + self.energy + self.insurance + self.lease + self.demurrage)


# In[ ]:


def opex_calc(opex, labour, maintenance, energy, insurance, lease, demurrage, year, timestep):
    opex.append(opex_class())
    index = len(opex)-1
    opex[index].year = year
    opex[index].calc(labour, maintenance, energy, insurance, lease, demurrage, timestep)
    #print ('Total opex/loss ($)', opexs[timestep].total)
    #print ()
    return opex


# ### WACC

# In[ ]:


# create WACC class 
class WACC_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# In[ ]:


# define WACC class functions 
class WACC_class(WACC_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, assets):
        pass
        # All assets are presumed to depreciate linearly
        # Residual value associated with the quay


# ### Escalation
