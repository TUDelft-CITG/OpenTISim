from terminal_optimization import mixins

# The generic berth class
Berth = type('Berth', (mixins.identifiable_properties_mixin,      # Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.berth_properties_mixin,
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
            {})                         # The dictionary is empty because the site type is generic

# The generic crane class
Crane = type('Crane', (mixins.identifiable_properties_mixin,      # Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.cyclic_properties_mixin,
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
            {})                         # The dictionary is empty because the site type is generic

# The generic storage class
Storage = type('Storage', (mixins.identifiable_properties_mixin,  # Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.storage_properties_mixin,
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
            {})                         # The dictionary is empty because the site type is generic

# The generic quay class
Quay = type('Quay', (mixins.identifiable_properties_mixin,        # Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.quay_wall_properties_mixin,
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
            {})                         # The dictionary is empty because the site type is generic

# The generic conveyor class
Conveyor = type('Conveyor', (mixins.identifiable_properties_mixin,# Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.conveyor_properties_mixin,
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
                {})                         # The dictionary is empty because the site type is generic
