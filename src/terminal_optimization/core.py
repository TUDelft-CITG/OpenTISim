# create vessel class
class vessel_properties_mixin(object):
    def __init__(self, 
                 vessel_type, call_size, LOA, draft, beam, max_cranes, all_turn_time, mooring_time, demurrage, 
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.vessel_type = vessel_type
        self.call_size = call_size 
        self.LOA = LOA
        self.draft = draft
        self.beam = beam
        self.max_cranes = max_cranes
        self.all_turn_time = all_turn_time
        self.mooring_time = mooring_time
        self.demurrage = demurrage

# create loader class
class cyclic_properties_mixin(object):
    def __init__(self, unloader_type, lifting_capacity, hourly_cycles, eff_fact, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.unloader_type      = unloader_type
        self.lifting_capacity   = lifting_capacity
        self.hourly_cycles      = hourly_cycles
        self.eff_fact           = eff_fact 
        self.payload            = 0.70 * self.lifting_capacity      #Source: Nemag
        self.peak_capacity      = self.payload * self.hourly_cycles #Or as direct input 
        self.effective_capacity = eff_fact * self.peak_capacity     #Source: TATA steel

# create loader class
class continuous_properties_mixin(object):
    def __init__(self, unloader_type, peak_capacity, eff_fact, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.unloader_type      = unloader_type
        self.peak_capacity      = peak_capacity
        self.eff_fact           = eff_fact 
        self.rated_capacity     = 0.70 * self.peak_capacity      #Source: Nemag
        self.effective_capacity = eff_fact * self.peak_capacity     #Source: TATA steel
        
test_variable = 100
