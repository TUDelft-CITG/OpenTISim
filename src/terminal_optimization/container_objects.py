"""Main generic object classes:

- 1. Quay_wall
- 2. Berth
- 3. Cyclic_Unloader
    - STS crane
- 4. Horizontal transport
    - Tractor trailer
- 5. Containers
    - Laden
    - Reefer
    - Empty
    - OOG
- 6. Laden and reefer stack
    - RTG stack
    - RMG stack
    - SC stack
    - RS stack
- 7. Stack equipment
    - RTG
    - RMG
    - SC
    - RS
-8. Other stacks
    - OOG stack
    - Empty stack
- 9. Gates
- 8. Vessel
    - Panamax
- 9. Labour
-

"""

from terminal_optimization import container_mixins

# The generic Quay_wall class
Quay_wall = type('Quay_wall', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.quay_wall_properties_mixin,
                               container_mixins.history_properties_mixin,  # Give it procurement history
                               container_mixins.hascapex_properties_mixin,  # Give it capex info
                               container_mixins.hasopex_properties_mixin,  # Give it opex info
                               container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                               container_mixins.hastriggers_properties_mixin,  # Give it investment triggers (lambda?)
                               container_mixins.hasland_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The generic Berth class
Berth = type('Berth', (container_mixins.identifiable_properties_mixin,  # Give it a name
                       container_mixins.history_properties_mixin,  # Give it procurement history
                       container_mixins.berth_properties_mixin,
                       container_mixins.hascapex_properties_mixin,  # Give it capex info
                       container_mixins.hasopex_properties_mixin,  # Give it opex info
                       container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                       container_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
             {})  # The dictionary is empty because the site type is generic

# The generic Cyclic_Unloader class
# - Gantry_crane
# - Harbour_crane
# - Mobile_crane
Cyclic_Unloader = type('Cyclic_Unloader', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                           container_mixins.history_properties_mixin,  # Give it procurement history
                                           container_mixins.cyclic_properties_mixin,
                                           container_mixins.hascapex_properties_mixin,  # Give it capex info
                                           container_mixins.hasopex_properties_mixin,  # Give it opex info
                                           container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                           container_mixins.hastriggers_properties_mixin),
                       # Give it investment triggers (lambda?)
                       {})  # The dictionary is empty because the site type is generic

# The generic Horizontal transport class
# - Tractor trailer
Horizontal_Transport = type('Horizontal_Transport', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                                       container_mixins.history_properties_mixin,  # Give it procurement history
                                                       container_mixins.transport_properties_mixin,
                                                       container_mixins.hascapex_properties_mixin,  # Give it capex info
                                                       container_mixins.hasopex_properties_mixin,  # Give it opex info
                                                       container_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})


Container = type('Container', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                container_mixins.container_properties_mixin),
               {})

# The generic laden and reefer stack class
# - RTG stack
# - RMG stack
# - SC stack
# - RS stack

Laden_Stack = type('Laden_Stack', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.history_properties_mixin,
                                container_mixins.laden_stack_properties_mixin,
                                container_mixins.hasopex_properties_mixin,
                               container_mixins.hascapex_properties_mixin,  # Give it capex info
                               container_mixins.hastriggers_properties_mixin,  # Give it investment triggers
                                container_mixins.hasland_properties_mixin),
                 {})

# The generic stack equipment class
# - RTG
# - RMG
# - Straddle carrier
# - Reach stacker


Stack_Equipment = type('Stack_Equipment', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.history_properties_mixin,
                                container_mixins.stack_equipment_properties_mixin,
                               container_mixins.hascapex_properties_mixin,  # Give it capex info
                               container_mixins.hasopex_properties_mixin,  # Give it opex info
                               container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
                 {})



# Empty_stack class

Empty_Stack = type('Empty_Stack', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.history_properties_mixin,
                                container_mixins.empty_stack_properties_mixin,
                                container_mixins.hasopex_properties_mixin,
                               container_mixins.hascapex_properties_mixin,  # Give it capex info
                               container_mixins.hastriggers_properties_mixin,  # Give it investment triggers
                                container_mixins.hasland_properties_mixin),
                            {})

# OOG_stack class

OOG_Stack = type('Empty_Stack', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.history_properties_mixin,
                                container_mixins.oog_stack_properties_mixin,
                                container_mixins.hasopex_properties_mixin,
                               container_mixins.hascapex_properties_mixin,  # Give it capex info
                               container_mixins.hastriggers_properties_mixin,  # Give it investment triggers
                                 container_mixins.hasland_properties_mixin),
                {})


# The generic Storage class
# - Silo
# - Warehouse

Storage = type('Storage', (container_mixins.identifiable_properties_mixin,  # Give it a name
                           container_mixins.history_properties_mixin,  # Give it procurement history
                           container_mixins.storage_properties_mixin,
                           container_mixins.hascapex_properties_mixin,  # Give it capex info
                           container_mixins.hasopex_properties_mixin,  # Give it opex info
                           container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                           container_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})  # The dictionary is empty because the site type is generic


# The generic Commodity class
# - Maize
# - Soybean
# - Wheat
# - Laden
Commodity = type('Commodity', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.commodity_properties_mixin,
                               container_mixins.hasscenario_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The general Vessel class
# - Handysize
# - Handymax
# - Panamax
# - Super Post-Panamax
Vessel = type('Vessel', (container_mixins.identifiable_properties_mixin,
                         container_mixins.vessel_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Labour class
Labour = type('Labour', (container_mixins.identifiable_properties_mixin,
                         container_mixins.labour_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Energy class
Energy = type('Energy', (container_mixins.identifiable_properties_mixin,
                         container_mixins.energy_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Gates class
Gate = type('Gate', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.history_properties_mixin,
                                container_mixins.gate_properties_mixin,
                               container_mixins.hascapex_properties_mixin,  # Give it capex info
                               container_mixins.hasopex_properties_mixin,  # Give it opex info
                               container_mixins.hastriggers_properties_mixin,  # Give it investment triggers
                                container_mixins.hasland_properties_mixin),
                    {})

# The general Empty Container Handler (ECH) class

Empty_Handler = type('Empty_Handler', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.history_properties_mixin,
                                container_mixins.empty_handler_properties_mixin,
                               container_mixins.hascapex_properties_mixin,  # Give it capex info
                               container_mixins.hasopex_properties_mixin,  # Give it opex info
                               container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
                 {})





# The general Train class
Train = type('Train', (container_mixins.identifiable_properties_mixin,
                       container_mixins.train_properties_mixin),
             {})  # The dictionary is empty because the site type is generic
