import numpy as np
import terminal_optimization.infrastructure as infra

# create profit class 
class terminal_properties_mixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class terminal(terminal_properties_mixin):
    def __init__(self, project_WACC, allowable_berth_occupancy, allowable_waiting_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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

        self.quays, self.berths, self.cranes, self.storage, self.stations = [], [], ([],[],[],[]), ([],[]), []
        self.quay_conveyors, self.hinterland_conveyors = [], [] 

        # Quay
        if quay_object.t0_length != 0:
            self.quays.append(quay_object)
            self.quays[0].online_date = start_year
            self.quays[0].online_length = quay_object.t0_length
            self.quays[0].pending_length = 0

        # Berths
        if berth_object.t0_quantity != 0:
            for i in range (berth_object.t0_quantity):
                self.berths.append(berth_object)
                self.berths[i].online_date = start_year
                self.berths[i].online_quantity = berth_object.t0_quantity
                self.berths[i].pending_quantity = 0

        # Cranes
        if gantry_crane_object.t0_quantity != 0:
            for i in range (gantry_crane_object.t0_quantity):
                self.cranes[0].append(gantry_crane_object)
                self.cranes[0][i].online_date = start_year
                self.cranes[0][i].online_quantity = gantry_crane_object.t0_quantity
                self.cranes[0][i].pending_quantity = 0
                self.cranes[0][i].berth = 1
        if harbour_crane_object.t0_quantity != 0:
            for i in range (harbour_crane_object.t0_quantity):
                self.cranes[1].append(harbour_crane_object)
                self.cranes[1][i].online_date = start_year
                self.cranes[1][i].online_quantity = harbour_crane_object.t0_quantity
                self.cranes[1][i].pending_quantity = 0
                self.cranes[1][i].berth = 1
        if mobile_crane_object.t0_quantity != 0:
            for i in range (mobile_crane_object.t0_quantity):
                self.cranes[2].append(mobile_crane_object)
                self.cranes[2][i].online_date = start_year
                self.cranes[2][i].online_quantity = mobile_crane_object.t0_quantity
                self.cranes[2][i].pending_quantity = 0
                self.cranes[2][i].berth = 1
        if screw_unloader_object.t0_quantity != 0:
            for i in range (screw_unloader_object.t0_quantity):
                self.cranes[3].append(screw_unloader_object)
                self.cranes[3][i].online_date = start_year
                self.cranes[3][i].online_quantity = screw_unloader_object.t0_quantity
                self.cranes[3][i].pending_quantity = 0
                self.cranes[3][i].berth = 1

        # Storage
        if silo_object.t0_capacity != 0:
            self.storage[0].append(silo_object)
            self.storage[0][0].online_date = start_year
            self.storage[0][0].capacity = silo_object.t0_capacity
            self.storage[0][0].online_capacity = silo_object.t0_capacity
            self.storage[0][0].pending_capacity = 0
        if warehouse_object.t0_capacity != 0:
            self.storage[1].append(warehouse_object)
            self.storage[1][0].online_date = start_year
            self.storage[1][0].capacity = warehouse_object.t0_capacity
            self.storage[1][0].online_capacity = warehouse_object.t0_capacity
            self.storage[1][0].pending_capacity = 0

        # Loading stations
        if station_object.t0_capacity != 0:
            self.stations.append(station_object)
            self.stations[0].online_date = start_year
            self.stations[0].capacity = station_object.t0_capacity
            self.stations[0].online_capacity = station_object.t0_capacity
            self.stations[0].pending_capacity = 0

        # Conveyors
        if quay_conveyor_object.t0_capacity != 0:
            self.quay_conveyors.append(quay_conveyor_object)
            self.quay_conveyors[0].online_date = start_year
            self.quay_conveyors[0].capacity = quay_conveyor_object.t0_capacity
            self.quay_conveyors[0].online_capacity = quay_conveyors.t0_capacity
            self.quay_conveyors[0].pending_capacity = 0
        if hinterland_conveyor_object.t0_capacity != 0:
            self.hinterland_conveyors.append(hinterland_conveyor_object)
            self.hinterland_conveyors[0].online_date = start_year
            self.hinterland_conveyors[0].capacity = hinterland_conveyor_object.t0_capacity
            self.hinterland_conveyors[0].online_capacity = hinterland_conveyors.t0_capacity
            self.hinterland_conveyors[0].pending_capacity = 0

        #########################################
        # Assign empty cashflow list
        #########################################

        self.throughputs, self.revenues, self.capex, self.labour, self.maintenance = [], [], [], [], []
        self.energy, self.insurance, self.lease, self.demurrage, self.residuals = [], [], [], [], []
        self.profits, self.opex = [], []
        
        #########################################
        # Assign iteration variables
        #########################################
    
        self.project_WACC = project_WACC
        self.allowable_berth_occupancy = allowable_berth_occupancy
        self.allowable_waiting_time = allowable_waiting_time