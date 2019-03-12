# package for unique identifiers
import uuid

class identifiable_properties_mixin(object):
    """Something that has a name and id

    name: a name
    id: a unique id generated with uuid"""

    def __init__(self, name = [], id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.name = name
        # generate some id, in this case based on m
        self.id = id if id else str(uuid.uuid1())

class hascapex_properties_mixin(object):
    """Something has CAPEX

    capex: list with cost to be applied from investment year"""

    def __init__(self, capex = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.capex = capex
        
class hasopex_properties_mixin(object):
    """Something has OPEX

    opex: list with cost to be applied from investment year"""

    def __init__(self, labour = [], maintenance = [], energy = [], insurance = [], 
                 lease = [], demurrage = [], residual = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.labour = labour
        self.maintenance = maintenance
        self.energy = energy
        self.insurance = insurance
        self.lease = lease
        self.demurrage = demurrage
        self.residual = residual

class hasrevenue_properties_mixin(object):
    """Something has Revenue

    revenue: list with revenues to be applied from investment year"""

    def __init__(self, renevue = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.renevue = renevue        

class hastriggers_properties_mixin(object):
    """Something has InvestmentTriggers

    triggers: list with revenues to be applied from investment year"""

    def __init__(self, triggers = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.triggers = triggers        

class vessel_properties_mixin(object):
    def __init__(self, 
                 type, call_size, LOA, draft, beam, max_cranes, all_turn_time, mooring_time, demurrage, 
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.call_size = call_size 
        self.LOA = LOA
        self.draft = draft
        self.beam = beam
        self.max_cranes = max_cranes
        self.all_turn_time = all_turn_time
        self.mooring_time = mooring_time
        self.demurrage = demurrage

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
        
class berth_properties_mixin(object):
    def __init__(self, t0_quantity, crane_type, max_cranes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.t0_quantity   = t0_quantity
        self.crane_type    = crane_type
        self.max_cranes    = max_cranes
        self.delivery_time = quay_object.delivery_time
        self.cranes_present = []

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

