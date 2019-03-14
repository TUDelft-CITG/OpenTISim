import numpy as np
import pandas as pd
import babel.numbers 
import decimal

# 1 throughput

# Financial analysis needs the following classes:
# Based on an investment you get 1, 2.
# That in time leads to 3
# 1,2 and 3 need to be translated into 4, 5, 6, 7
#
# 1 capex
#   - investment
# 2 opex
#   - labour
#   - maintenance
#   - energy
#   - insurance
#   - lease
#   - demurrage
#   - residuals
# 3 revenue
# 4 cashflow
# 5 escalation (could be mixin property? HasEscalation)
# 6 WACC
# 7 NPV


# Terminal Throughput class
class throughput():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calculate(self, terminal, vessels, commodities, allowable_berth_occupancy, year, start_year, timestep, operational_hours):
        
        berths = terminal.berths
        cranes = terminal.cranes
        
        demand = []
        for i in range (3):
            demand.append(commodities[i].demand[timestep])
        demand = int(np.sum(demand))
        
        # Calculate current berth occupancy (without cranes that are due to come online)
        berth_service_rate = []
        for i in range (len(berths)):
            service_rate = []
            for j in range(4):
                for k in range(len(cranes[j])):
                    if cranes[j][k].online_date <= year and cranes[j][k].berth == i+1:
                        service_rate.append(cranes[j][k].effective_capacity * cranes[j][k].utilisation)                  
            berth_service_rate.append(np.sum(service_rate))
            berths[i].online_service_rate = int(np.sum(service_rate))
        total_service_rate = np.sum(berth_service_rate)
        
        cranes_online = [] 
        for i in range(4):
            for j in range(len(cranes[i])):
                if cranes[i][j].online_date <= year:
                    cranes_online.append(1)

        # Traffic distribution according to ratio service rate of each berth
        if total_service_rate != 0:
            traffic_ratio = []
            for i in range (len(berths)):
                if berth_service_rate[i] == 0:
                    traffic_ratio.append(0)
                    berths[i].traffic_ratio = traffic_ratio[0]
                else:
                    traffic_ratio.append(berth_service_rate[i]/total_service_rate)
                    berths[i].traffic_ratio = traffic_ratio[i]

            # Determine total time that vessels are at each berth
            occupancy = []
            for i in range (len(berths)):
                if traffic_ratio[i] == 0:
                    occupancy.append(0)
                    berths[i].occupancy = 0
                else:
                    berth_time = []
                    for j in range (3):
                        calls          = vessels[j].calls[timestep] * traffic_ratio[i]
                        service_time   = vessels[j].call_size / berth_service_rate[i]
                        mooring_time   = vessels[j].mooring_time
                        time_at_berth  = service_time + mooring_time
                        berth_time.append(time_at_berth * calls)
                    berth_time = np.sum(berth_time)
                    berths[i].occupancy = berth_time / operational_hours
                    occupancy.append(berth_time / operational_hours)              
                    
            # Determine maximum throughput (based on max allowable berth occupancy)
            capacity = []
            for i in range (len(berths)):
                if traffic_ratio[i] == 0:
                    capacity.append(0)
                else:
                    service_rate = berth_service_rate[i]
                    berth_occupancy = allowable_berth_occupancy
                    berth_throughput = service_rate * berth_occupancy * operational_hours
                    capacity.append(int(berth_throughput))

            quay_capacity        = int(np.sum(capacity))

            self.demand = demand
            self.capacity = quay_capacity
            self.throughput = int(min(demand, quay_capacity))
        
        else:
            self.demand = demand
            self.capacity = 0
            self.throughput = 0
            self.start_year = start_year

        return terminal

def throughput_calc(terminal, vessels,commodities, allowable_berth_occupancy, year, start_year, timestep, operational_hours):
    throughputs = terminal.throughputs
    throughputs.append(throughput_class())
    index = len(throughputs)-1
    throughputs[index].year = year
    terminal = throughputs[index].calc(terminal, vessels, commodities, allowable_berth_occupancy, year, start_year, timestep, operational_hours)
    terminal.throughputs = throughputs
    return terminal


# Business Logic classes
# create revenue class
class revenue_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

# define revenue class functions 
class revenue_class(revenue_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self, commodities, throughputs, timestep):
        maize   = commodities[0]
        soybean = commodities[1]
        wheat   = commodities[2]
        
        maize_throughput   = min(maize.demand[timestep], throughputs[timestep].capacity)
        soybean_throughput = min(maize_throughput+soybean.demand[timestep], throughputs[timestep].capacity)
        wheat_throughput   = min(maize_throughput+soybean_throughput+wheat.demand[timestep], throughputs[timestep].capacity)

        self.maize   = int(maize_throughput   * maize.handling_fee)
        self.soybean = int(soybean_throughput * soybean.handling_fee)
        self.wheat   = int(wheat_throughput   * wheat.handling_fee)
        self.total   = int(self.maize + self.soybean + self.wheat)

def revenue_calc(revenues, throughputs, commodities, year, timestep):
    revenues.append(revenue_class())
    index = len(revenues)-1
    revenues[index].year = year
    revenues[index].calc(commodities, throughputs, timestep)
    return revenues

### Capex
# create capex class
class capex_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# define capex class functions 
class capex_class(capex_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self, terminal):
        
        quays = terminal.quays
        cranes = terminal.cranes
        storage = terminal.storage
        stations = terminal.stations
        q_conveyors = terminal.quay_conveyors
        h_conveyors = terminal.hinterland_conveyors 
        
        # Capex associated with the quay wall
        if len(quays) != 0 and quays[0].delta != 0:
            quay         = quays[len(quays)-1]
            delta        = quay.delta
            unit_rate    = int(quay.Gijt_constant * (quay.depth*2 + quay.freeboard)**quay.Gijt_coefficient)
            mobilisation = int(max((delta * unit_rate * quay.mobilisation_perc), quay.mobilisation_min))
            self.quay    = int(delta * unit_rate + mobilisation)
            terminal.quays[len(quays)-1].value = unit_rate * delta
        else:
            self.quay = 0
        
        # Capex associated with the gantry cranes
        if len(cranes[0]) != 0 and cranes[0][0].delta != 0:
            crane        = terminal.cranes[0][0]
            delta        = crane.delta
            unit_rate    = crane.unit_rate
            mobilisation = delta * unit_rate * crane.mobilisation_perc
            self.gantry_cranes = int(delta * unit_rate + mobilisation)
        else:
            self.gantry_cranes = 0
        
        # Capex associated with the harbour cranes
        if len(cranes[1]) != 0 and cranes[1][0].delta != 0:
            crane        = terminal.cranes[1][0]
            delta        = crane.delta
            unit_rate  = crane.unit_rate
            mobilisation = delta * unit_rate * crane.mobilisation_perc
            self.harbour_cranes = int(delta * unit_rate + mobilisation)
        else:
            self.harbour_cranes = 0
        
        # Capex associated with the mobile harbour cranes
        if len(cranes[2]) != 0 and cranes[2][0].delta != 0:
            crane        = terminal.cranes[2][0]
            delta        = crane.delta
            unit_rate    = crane.unit_rate
            mobilisation = delta * unit_rate * crane.mobilisation_perc
            self.mobile_cranes = int(delta * unit_rate + mobilisation) 
        else:
            self.mobile_cranes = 0
        
        # Capex associated with the screw unloaders
        if len(cranes[3]) != 0 and cranes[3][0].delta != 0:
            crane        = terminal.cranes[3][0]
            delta        = crane.delta
            unit_rate    = crane.unit_rate
            mobilisation = delta * unit_rate * crane.mobilisation_perc
            self.screw_unloaders = int(delta * unit_rate + mobilisation)
        else:
            self.screw_unloaders = 0
        
        # Capex associated with the silos
        if len(storage[0]) != 0 and storage[0][0].delta != 0:
            silo         = terminal.storage[0][0]
            delta        = silo.delta
            unit_rate    = silo.unit_rate
            mobilisation = delta * unit_rate * silo.mobilisation_perc
            self.silos   = int(delta * unit_rate + mobilisation)
            terminal.storage[0][len(storage[0])-1].value = unit_rate * delta
        else:
            self.silos = 0
        
        # Capex associated with the warehouses
        if len(storage[1]) != 0 and storage[0][0].delta != 0:
            asset        = terminal.storage[1][0]
            delta        = asset.delta
            unit_rate    = asset.unit_rate
            mobilisation = delta * unit_rate * asset.mobilisation_perc
            self.warehouses = int(delta * unit_rate + mobilisation)
            terminal.storage[1][len(storage[1])-1].value = unit_rate * delta
        else:
            self.warehouses = 0
        
        # Capex associated with the hinterland loading stations
        if len(stations) != 0 and stations[0].delta != 0:
            station      = terminal.stations[0]
            delta        = station.delta
            unit_rate    = station.unit_rate
            mobilisation = station.mobilisation
            self.loading_stations = delta * unit_rate + mobilisation
            terminal.stations[len(stations)-1].value = unit_rate * delta
        else:
            self.loading_stations = 0
        
        # Capex associated with the conveyors connecting the quay to the storage
        if len(q_conveyors) != 0 and q_conveyors[0].delta != 0:
            conveyor     = terminal.quay_conveyors[0]
            delta        = conveyor.delta
            unit_rate    = 6.0 * conveyor.length
            mobilisation = conveyor.mobilisation
            self.quay_conveyors = int(delta * unit_rate + mobilisation)
            terminal.quay_conveyors[len(q_conveyors)-1].value = unit_rate * delta
        else:
            self.quay_conveyors = 0
        
        # Capex associated with the conveyors connecting the storage with the loading stations
        if len(h_conveyors) != 0 and h_conveyors[0].delta != 0:
            conveyor     = terminal.hinterland_conveyors[0]
            delta        = conveyor.delta
            unit_rate    = 6.0 * conveyor.length
            mobilisation = conveyor.mobilisation
            self.hinterland_conveyors = int(delta * unit_rate + mobilisation)
            terminal.hinterland_conveyors[len(h_conveyors)-1].value = unit_rate * delta
        else:
            self.hinterland_conveyors = 0
        
        # Combining all capex data
        self.total     = -1*int(self.quay + self.gantry_cranes + self.harbour_cranes + self.mobile_cranes +                             self.screw_unloaders + self.silos + self.warehouses + self.loading_stations +                             self.quay_conveyors + self.hinterland_conveyors)
        self.cranes    = -1*int(self.gantry_cranes + self.harbour_cranes + self.mobile_cranes + self.screw_unloaders)
        self.storage   = -1*int(self.silos + self.warehouses)
        self.conveyors = -1*int(self.quay_conveyors + self.hinterland_conveyors)

def capex_calc(terminal, year, timestep):
    capex = terminal.capex
    capex.append(capex_class())
    index = len(capex)-1
    capex[index].year = year
    capex[index].calc(terminal)
    return capex


### Labour
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

# define labour class functions 
class labour_class(labour_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, terminal, operational_hours):
        
        cranes = terminal.cranes
        storage = terminal.storage
        stations = terminal.stations
        q_conveyors = terminal.quay_conveyors
        h_conveyors = terminal.hinterland_conveyors 
        
        # Number of shifts associated with the cranes (3 crew per crane)
        crane_shifts = []
        for i in range (4):
            for j in range(len(cranes[i])):
                crane_shifts.append(int(np.ceil(cranes[i][j].crew * operational_hours / self.shift_length)))
        crane_shifts = np.sum(crane_shifts)
        
        # Number of shifts associated with the storage
        storage_shifts = []
        for i in range (2):
            for j in range(len(storage[i])):
                storage_shifts.append(int(np.ceil(operational_hours * storage[i][0].crew / self.shift_length)))
        storage_shifts = np.sum(storage_shifts)
        
        # Number of shifts associated with the loading stations (always 2)
        station_shifts = []
        for i in range(len(stations)):
            station_shifts.append(np.ceil(operational_hours * stations[i].crew / self.shift_length))
        station_shifts = np.sum(station_shifts)    

        # Number of shifts associated with the conveyors (always 1 for the quay and 1 for the hinterland conveyor)
        q_conveyor_shifts, h_conveyor_shifts = [], []
        for i in range(len(q_conveyors)):
            q_conveyor_shifts.append(np.ceil(operational_hours * q_conveyors[0].crew / self.shift_length))
        for i in range(len(h_conveyors)):
            h_conveyor_shifts.append(np.ceil(operational_hours * h_conveyors[0].crew / self.shift_length))
        conveyor_shifts = np.sum(q_conveyor_shifts) + np.sum(h_conveyor_shifts)
        
        self.total_shifts = crane_shifts + storage_shifts + station_shifts + conveyor_shifts
        self.operational_staff = self.total_shifts/self.annual_shifts
        
        self.total = int(self.international_salary * self.international_staff + self.local_salary * self.local_staff +                           self.operational_salary   * self.operational_staff)

def labour_calc(terminal, year, timestep, operational_hours):
    labour = terminal.labour
    labour.append(labour_class(**labour_data))
    index = len(labour)-1
    labour[index].year = year
    labour[index].calc(terminal, operational_hours)
    return labour


# ### Maintenance
# create maintenance class 
class maintenance_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# define maintenance class functions 
class maintenance_class(maintenance_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def calc(self, terminal, year):
        
        quays = terminal.quays
        cranes = terminal.cranes
        storage = terminal.storage
        stations = terminal.stations
        q_conveyors = terminal.quay_conveyors
        h_conveyors = terminal.hinterland_conveyors 
        
        # Maintenance costs associated with the quay
        quay_maintenance = []        
        for i in range(len(quays)):
            if quays[i].online_date <= year:
                value      = quays[i].value
                percentage = quays[i].maintenance_perc
                maintenance = value * percentage
                quay_maintenance.append(maintenance)
                quays[i].maintenance_costs = maintenance
        self.quay = int(np.sum(quay_maintenance))
            
        # Maintenance costs associated with the cranes
        crane_maintenance = []
        for i in range (4):
            for j in range(len(cranes[i])):
                unit_rate = cranes[i][j].unit_rate
                maintenance = unit_rate * cranes[i][j].maintenance_perc
                crane_maintenance.append(maintenance)
                cranes[i][j].maintenance_costs = maintenance
        self.cranes = int(np.sum(crane_maintenance))

        # Maintenance costs associated with the storage
        storage_maintenance = []
        for i in range (2):
            for j in range (len(storage[i])):
                maintenance = storage[i][j].value * storage[i][j].maintenance_perc
                storage_maintenance.append(maintenance)
                storage[i][j].maintenance_costs = maintenance
        self.storage = int(np.sum(storage_maintenance))
        
        # Maintenance costs associated with the loading stations
        station_maintenance = []
        for i in range(len(stations)):
            maintenance = stations[i].value * stations[i].maintenance_perc
            stations[i].maintenance_costs = maintenance
        self.loading_stations = int(np.sum(station_maintenance))
            
        # Maintenance costs associated with the quay conveyors
        quay_conveyor_maintenance = []
        for i in range (len(q_conveyors)):
            maintenance = q_conveyors[i].value * q_conveyors[i].maintenance_perc
            quay_conveyor_maintenance.append(maintenance)
            q_conveyors[i].maintenance = maintenance
        quay_conveyor_maintenance = np.sum(quay_conveyor_maintenance)
            
        # Maintenance costs associated with the hinterland conveyors
        hinterland_conveyor_maintenance = []
        for i in range (len(h_conveyors)):
            maintenance = h_conveyors[i].value * h_conveyors[i].maintenance_perc
            h_conveyors[i].maintenance = maintenance
            hinterland_conveyor_maintenance = maintenance
        hinterland_conveyor_maintenance = np.sum(hinterland_conveyor_maintenance)
            
        # Maintenance costs associated with all conveyors combined
        self.conveyors = int(quay_conveyor_maintenance + hinterland_conveyor_maintenance)
        
        self.total = int(self.quay + self.cranes + self.storage + self.loading_stations + self.conveyors)

def maintenance_calc(terminal, year, timestep):
    maintenance = terminal.maintenance
    maintenance.append(maintenance_class())
    index = len(maintenance)-1
    maintenance[index].year = year
    maintenance[index].calc(terminal, year)
    return maintenance


# ### Energy costs
# create energy consumption class 
class energy_properties_mixin(object):
    def __init__(self, price, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = price

# Initial data
energy_data = {"price": 0.10}

# define energy consumption class functions 
class energy_class(energy_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, terminal, year, operational_hours):
            
        cranes = terminal.cranes
        berths = terminal.berths
        storage = terminal.storage
        stations = terminal.stations
        q_conveyors = terminal.quay_conveyors
        h_conveyors = terminal.hinterland_conveyors    
            
        # Energy costs associated with the cranes
        crane_energy = []
        for i in range (4):
            for j in range (len(cranes[i])):
                if cranes[i][j].online_date <= year and 'occupancy' in dir(cranes[i][j]):
                    consumption = cranes[i][j].consumption
                    occupancy = berths[0].occupancy
                    hours = operational_hours * occupancy
                    crane_energy.append(consumption * hours)
        self.cranes = int(np.sum(crane_energy) * self.price)
        
        # Energy costs associated with the storage
        storage_energy = []
        for i in range (2):
            for j in range(len(storage[i])):
                if storage[i][j].online_date <= year:
                    consumption = storage[i][j].consumption
                    capacity    = storage[i][j].capacity
                    hours       = operational_hours
                    storage_energy.append(consumption * capacity * hours)
        self.storage = int(np.sum(storage_energy) * self.price)
            
        # Energy costs associated with the loading stations
        station_energy = []
        for i in range(len(stations)):
            if stations[i].online_date <= year:
                consumption = stations[i].consumption
                capacity    = stations[i].capacity
                utilisation = stations[i].utilisation
                hours       = operational_hours * utilisation
                station_energy.append(consumption * capacity * hours)
        self.stations = int(np.sum(station_energy) * self.price)
        
        # Energy costs associated with the conveyors
        conveyor_energy = []
        if 'occupancy' in dir(berths[0]):
            berth_occupancy = []
            for i in range (len(berths)):
                berth_occupancy.append(berths[i].occupancy)
                occupancy = np.average(berth_occupancy)
        for i in range(len(q_conveyors)):
            if q_conveyors[i].online_date <= year and 'occupancy' in dir(berths[0]):
                consumption = q_conveyors[i].capacity * q_conveyors[i].consumption_coefficient + q_conveyors[i].consumption_constant
                hours       = operational_hours * occupancy
                usage       = consumption * hours
                conveyor_energy.append(usage)
        for i in range(len(h_conveyors)):
            if h_conveyors[i].online_date <= year:
                consumption = h_conveyors[i].capacity * h_conveyors[i].consumption_coefficient + h_conveyors[i].consumption_constant
                hours       = operational_hours * stations[0].utilisation
                usage       = consumption * hours
                conveyor_energy.append(usage)
        self.conveyors = int(np.sum(conveyor_energy) * self.price)

        self.total = int(self.cranes + self.storage + self.stations + self.conveyors)

def energy_calc(terminal, year, operational_hours, timestep):
    energy = terminal.energy
    energy.append(energy_class(**energy_data))
    index = len(energy)-1
    energy[index].year = year
    energy[index].calc(terminal, year, operational_hours)
    return energy


# ### Insurance costs
# create insurance cost class 
class insurance_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# define insurance cost class functions 
class insurance_class(insurance_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, terminal, year):
        
        quays = terminal.quays
        cranes = terminal.cranes
        storage = terminal.storage
        stations = terminal.stations
        q_conveyors = terminal.quay_conveyors
        h_conveyors = terminal.hinterland_conveyors   

        # Insurance costs associated with the quay
        quay_insurance = []        
        for i in range(len(quays)):
            if quays[i].online_date <= year:
                unit_rate  = int(quays[i].Gijt_constant * (quays[i].depth*2 + quays[i].freeboard)**quays[i].Gijt_coefficient)
                length     = quays[i].length
                percentage = quays[i].insurance_perc
                insurance  = unit_rate * length * percentage
                quay_insurance.append(insurance)
                quays[i].insurance_costs = insurance
        self.quay = int(np.sum(quay_insurance))
        
        # Insurance costs associated with the cranes        
        crane_insurance = [] 
        for i in range (4):
            for j in range(len(cranes[i])):
                unit_rate  = cranes[i][j].unit_rate
                percentage = cranes[i][j].insurance_perc
                insurance  = unit_rate * percentage
                crane_insurance.append(insurance)
                cranes[i][j].insurance_costs = insurance
        self.cranes = int(np.sum(quay_insurance))

        # Insurance costs associated with storage
        storage_insurance = [] 
        for i in range (2):
            for j in range(len(storage[i])):
                if storage[i][j].online_date <= year:
                    unit_rate  = storage[i][j].unit_rate
                    capacity   = storage[i][j].capacity
                    percentage = storage[i][j].insurance_perc
                    insurance  = unit_rate * capacity * percentage
                    storage_insurance.append(insurance)
                    storage[i][j].insurance_costs = insurance
        self.storage = int(np.sum(storage_insurance))
        
        # Insurance costs associated with loading stations
        station_insurance = [] 
        for i in range(len(stations)):
            if stations[i].online_date <= year:
                unit_rate  = stations[i].unit_rate
                capacity   = stations[i].capacity
                percentage = stations[i].insurance_perc
                insurance  = unit_rate * capacity * percentage
                station_insurance.append(insurance)
                stations[i].insurance_costs = insurance
        self.stations = int(np.sum(station_insurance))
        
        # Insurance costs associated with quay conveyors
        quay_conveyor_insurance = [] 
        for i in range(len(q_conveyors)):
            if q_conveyors[i].online_date <= year:
                unit_rate  = q_conveyors[i].unit_rate * q_conveyors[i].length
                capacity   = q_conveyors[i].capacity
                percentage = q_conveyors[i].insurance_perc
                insurance  = unit_rate * capacity * percentage
                q_conveyors[i].insurance_costs = insurance
                quay_conveyor_insurance.append(insurance)
                
        # Insurance costs associated with hinterland conveyors
        hinterland_conveyor_insurance = [] 
        for i in range(len(h_conveyors)):
            if h_conveyors[i].online_date <= year:
                unit_rate  = h_conveyors[i].unit_rate * h_conveyors[i].length
                capacity   = h_conveyors[i].capacity
                percentage = h_conveyors[i].insurance_perc
                insurance  = unit_rate * capacity * percentage
                quay_conveyor_insurance.append(insurance)
                h_conveyors[i].insurance_costs = insurance
        self.conveyors = int(np.sum(quay_conveyor_insurance) + np.sum(hinterland_conveyor_insurance))
        
        self.total = int(self.quay + self.cranes + self.storage + self.stations + self.conveyors)

def insurance_calc(terminal, year, timestep):
    insurance = terminal.insurance
    insurance.append(insurance_class())
    index = len(insurance)-1
    insurance[index].year = year
    insurance[index].calc(terminal, year)
    return insurance


# ### Lease costs
# create energy consumption class 
class lease_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# define lease cost class functions 
class lease_class(lease_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self):
        self.total = 0 

def lease_calc(terminal, year, timestep):
    lease = terminal.lease
    lease.append(lease_class())
    index = len(lease)-1
    lease[index].year = year
    lease[index].calc()
    return lease


# ### Demurrage costs
# create demurrage class
class demurrage_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# define demurrage class functions 
class demurrage_class(demurrage_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
    def calc(self, berths, vessels, timestep):
        
        if berths[0].online == 0:
            self.total = 0
        else:
            # Calculate berth unloading rate and occupancy
            online = berths[0].online
            costs = []
            for i in range (online):
                occupancy     = berths[i].occupancy
                service_rate  = berths[i].online_service_rate 
                traffic_ratio = berths[i].traffic_ratio
                
                # Waiting time factor (E2/E/n quing theory using 4th order polynomial regression)
                if online == 1:
                    factor = max(0, 79.726* occupancy **4 - 126.47* occupancy **3 + 70.660* occupancy **2 - 14.651* occupancy + 0.9218)
                if online == 2:
                    factor = max(0, 29.825* occupancy **4 - 46.489* occupancy **3 + 25.656* occupancy **2 - 5.3517* occupancy + 0.3376)
                if online == 3:
                    factor = max(0, 19.362* occupancy **4 - 30.388* occupancy **3 + 16.791* occupancy **2 - 3.5457* occupancy + 0.2253)
                if online == 4:
                    factor = max(0, 17.334* occupancy **4 - 27.745* occupancy **3 + 15.432* occupancy **2 - 3.2725* occupancy + 0.2080)
                if online == 5:
                    factor = max(0, 11.149* occupancy **4 - 17.339* occupancy **3 + 9.4010* occupancy **2 - 1.9687* occupancy + 0.1247)
                if online == 6:
                    factor = max(0, 10.512* occupancy **4 - 16.390* occupancy **3 + 8.8292* occupancy **2 - 1.8368* occupancy + 0.1158)
                if online == 7:
                    factor = max(0, 8.4371* occupancy **4 - 13.226* occupancy **3 + 7.1446* occupancy **2 - 1.4902* occupancy + 0.0941)

                # Calculate total time at port
                vessel_specific_costs = []
                for j in range (3):
                    service_time   = vessels[j].call_size/service_rate
                    mooring_time   = vessels[j].mooring_time
                    waiting_time   = factor * service_time
                    berth_time     = service_time + mooring_time 
                    port_time      = berth_time + waiting_time
                    penalty_time   = max(0, port_time - vessels[j].all_turn_time)
                    n_calls        = vessels[j].calls[timestep] * traffic_ratio
                    demurrage_time = penalty_time * n_calls
                    demurrage_cost = demurrage_time * vessels[j].demurrage_rate
                    vessel_specific_costs.append(demurrage_cost)
                    costs.append(np.sum(vessel_specific_costs))

            self.total = np.sum(costs)

def demurrage_calc(demurrage, berths, vessels, year, timestep):
    demurrage.append(demurrage_class())
    index = len(demurrage)-1
    demurrage[index].year = year
    demurrage[index].calc(berths, vessels, timestep)
    return demurrage


# ### Residual values
# create residual value class 
class residual_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# define residual value class functions 
class residual_class(residual_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, terminal, year):
        
        # All assets are presumed to depreciate linearly
        quays = terminal.quays
        cranes = terminal.cranes
        storage = terminal.storage
        stations = terminal.stations
        q_conveyors = terminal.quay_conveyors
        h_conveyors = terminal.hinterland_conveyors    
        
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
            for j in range(len(cranes[i])):
                if not 'online_date' in dir(cranes[i][j]):
                    break
                if cranes[i][j].online_date <= year:
                    ini_value = cranes[i][j].unit_rate
                    age = year - cranes[i][j].online_date
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

def residual_calc(terminal, year, timestep):
    residuals = terminal.residuals
    residuals.append(residual_class())
    index = len(residuals)-1
    residuals[index].year = year
    residuals[index].calc(terminal, year)
    return residuals


# ### Profits
# create profit class 
class profit_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# define profit class functions 
class profit_class(profit_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, terminal, window, timestep, year, start_year):
        
        profits, revenues, capex, labour, maintenance, energy, insurance, lease, demurrage, residuals = terminal.profits, terminal.revenues, terminal.capex, terminal.labour, terminal.maintenance, terminal.energy, terminal.insurance, terminal.lease, terminal.demurrage, terminal.residuals
        self.revenues    = revenues[timestep].total
        self.capex       = capex[timestep].total
        self.labour      = labour[timestep].total      * -1
        self.maintenance = maintenance[timestep].total * -1
        self.energy      = energy[timestep].total      * -1
        self.insurance   = insurance[timestep].total   * -1
        self.lease       = lease[timestep].total       * -1
        self.demurrage   = demurrage[timestep].total   * -1
        if year == start_year + window - 1:
            #self.residuals = 0
            self.residuals = residuals[timestep].total
        else:
            self.residuals = 0
            
        self.total = int(self.revenues + self.capex + self.labour + self.maintenance + self.energy + self.insurance +
                         self.lease + self.demurrage + self.residuals)

def profit_calc(terminal, window, timestep, year, start_year):
    profits = terminal.profits
    profits.append(profit_class())
    index = len(profits)-1
    profits[index].year = year
    profits[index].calc(terminal, window, timestep, year, start_year)
    return profits


# ### OPEX
# create opex class 
class opex_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# define opex class functions 
class opex_class(opex_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def calc(self, terminal, timestep):
        
        labour, maintenance, energy, insurance, lease, demurrage = terminal.labour, terminal.maintenance, terminal.energy, terminal.insurance, terminal.lease, terminal.demurrage
        
        self.labour      = labour[timestep].total      * -1
        self.maintenance = maintenance[timestep].total * -1
        self.energy      = energy[timestep].total      * -1
        self.insurance   = insurance[timestep].total   * -1
        self.lease       = lease[timestep].total       * -1
        self.demurrage   = demurrage[timestep].total   * -1
            
        self.total = int(self.labour + self.maintenance + self.energy + self.insurance + self.lease + self.demurrage)

def opex_calc(terminal, year, timestep):
    opex = terminal.opex
    opex.append(opex_class())
    index = len(opex)-1
    opex[index].year = year
    opex[index].calc(terminal, timestep)
    return opex


# ### Combining all cashflow 

def cashflow_calc(terminal, simulation_window, start_year):

    flows = np.zeros(shape=(simulation_window, 15))
    profits, revenues, capex, opex, labour, maintenance, energy, insurance, lease, demurrage, residuals = terminal.profits, terminal.revenues, terminal.capex, terminal.opex, terminal.labour, terminal.maintenance, terminal.energy, terminal.insurance, terminal.lease, terminal.demurrage, terminal.residuals

    ############################################################################################################
    # For each year, register the corresponding cashflow 
    ############################################################################################################
    
    for t in range (simulation_window):
        
        # Years (Column 0)
        year = t + start_year 
        flows[t,0] = year

        # Profits (Column 1)
        flows[t,1] = profits[t].total

        # Revenues (Column 2)
        flows[t,2] = revenues[t].total

        # Capex (Column 3)
        flows[t,3] = capex[t].total

        # Opex (Column 4)
        flows[t,4] = opex[t].total

        # Labour costs (Column 5)
        flows[t,5] = labour[t].total

        # Maintenance costs (Column 6)
        flows[t,6] = maintenance[t].total

        # Energy costs (Column 7)
        flows[t,7] = energy[t].total

        # Insurance costs (Column 8)
        flows[t,8] = insurance[t].total

        # Lease costs (Column 9)
        flows[t,9] = lease[t].total

        # Demurrage costs (Column 10)
        flows[t,10] = demurrage[t].total

        # Residual asset value (Column 11)
        flows[t,11] = residuals[t].total
        
        # WACC depreciated profits
        flows[t,12] = terminal.WACC_cashflows.profits[t]
        
        if t != 0:
            # Compounded profit
            flows[t-1,13] = sum(flows[0:t,1])

            # Compounded profit (present value)
            flows[t-1,14] = sum(flows[0:t,12])
            
        if t == simulation_window-1:
            # Compounded profit
            flows[t,13] = sum(flows[0:t+1,1])

            # Compounded profit (present value)
            flows[t,14] = sum(flows[0:t+1,12])

    cashflows = pd.DataFrame(flows, columns=['Year', 'Profits', 'Revenues', 'Capex', 'Opex', 'Labour costs', 
                                             'Maintenance costs', 'Energy costs', 'Insurance costs', 'Lease costs', 
                                             'Demurrage costs','Residual asset value', 'Profits (discounted)', 
                                             'Compounded profit', 'Compounded profit (discounted)'])
    cashflows = cashflows.astype(int)
    
    return cashflows


# ### Escalation
# create WACC class 
class escalation_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# define escalation class functions 
class escalation_class(escalation_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    #def calc(self, window):


# create WACC class 
class WACC_properties_mixin(object):
    def __init__(self, real_WACC, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_WACC = real_WACC
        
WACC_data = {"real_WACC": 0.09}

# define WACC class functions 
class WACC_class(WACC_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def profits_calc(self, overruled_WACC, profits, window, start_year):
        
        WACC = []
        years = []
        profits_WACC = []
        
        for i in range (window):
            WACC.append(1/((1+overruled_WACC)**(i)))
            years.append(start_year + i)
            profit = profits[i].total
            profits_WACC.append(profit * WACC[i])

        self.WACC = WACC
        self.profits = profits_WACC
        self.years = years
        
        return 

def WACC_calc(WACC, profits, window, start_year):
    WACC_cashflows = WACC_class(**WACC_data)
    WACC_cashflows.profits_calc(WACC, profits, window, start_year)
    return WACC_cashflows


# ### NPV
def NPV_calc(WACC_cashflows):
    profits = WACC_cashflows.profits
    NPV = int(np.sum(profits))
    #NPV = '${:0,.0f}'.format(NPV)
    return NPV
