"""Main generic object classes:

- 1. Quay_wall
- 2. Berth
- 3. Cyclic_Unloader
    - STS crane
- 4. Horizontal transport
    - Tractor trailer
- 5. Commodity
    - TEU
- 6. Containers
    - Laden
    - Reefer
    - Empty
    - OOG
- 7. Laden and reefer stack
    - RTG stack
    - RMG stack
    - SC stack
    - RS stack
- 8. Stack equipment
    - RTG
    - RMG
    - SC
    - RS
- 9. Empty stack
- 10. OOG stack
- 11. Gates
- 12. Empty handler
- 13. Vessel
- 14. Labour
- 15. Energy
- 16. General
- 17. Indirect Costs
"""

from .container_mixins import *

# The generic Quay_wall class
Quay_wall = type('Quay_wall', (identifiable_properties_mixin,  # Give it a name
                               quay_wall_properties_mixin,
                               history_properties_mixin,  # Give it procurement history
                               hascapex_properties_mixin,  # Give it capex info
                               hasopex_properties_mixin,  # Give it opex info
                               hasrevenue_properties_mixin,  # Give it revenue info
                               hastriggers_properties_mixin,  # Give it investment triggers (lambda?)
                               hasland_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The generic Berth class
Berth = type('Berth', (identifiable_properties_mixin,  # Give it a name
                       history_properties_mixin,  # Give it procurement history
                       berth_properties_mixin,
                       hascapex_properties_mixin,  # Give it capex info
                       hasopex_properties_mixin,  # Give it opex info
                       hasrevenue_properties_mixin,  # Give it revenue info
                       hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
             {})  # The dictionary is empty because the site type is generic

# The generic Cyclic_Unloader class
# - Gantry_crane
# - Harbour_crane
# - Mobile_crane
Cyclic_Unloader = type('Cyclic_Unloader', (identifiable_properties_mixin,  # Give it a name
                                           history_properties_mixin,  # Give it procurement history
                                           cyclic_properties_mixin,
                                           hascapex_properties_mixin,  # Give it capex info
                                           hasopex_properties_mixin,  # Give it opex info
                                           hasrevenue_properties_mixin,  # Give it revenue info
                                           hastriggers_properties_mixin),
                       # Give it investment triggers (lambda?)
                       {})  # The dictionary is empty because the site type is generic

# The generic Horizontal transport class
# - Tractor trailer
Horizontal_Transport = type('Horizontal_Transport', (identifiable_properties_mixin,  # Give it a name
                                                       history_properties_mixin,  # Give it procurement history
                                                       transport_properties_mixin,
                                                       hascapex_properties_mixin,  # Give it capex info
                                                       hasopex_properties_mixin,  # Give it opex info
                                                       hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})

# The generic Commodity class
# - Container
Commodity = type('Commodity', (identifiable_properties_mixin,  # Give it a name
                               commodity_properties_mixin,
                               hasscenario_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

Container = type('Container', (identifiable_properties_mixin,  # Give it a name
                                container_properties_mixin),
               {})

# The generic laden and reefer stack class
# - RTG stack
# - RMG stack
# - SC stack
# - RS stack
Laden_Stack = type('Laden_Stack', (identifiable_properties_mixin,  # Give it a name
                               history_properties_mixin,
                               laden_stack_properties_mixin,
                               hasopex_properties_mixin,
                               hascapex_properties_mixin,  # Give it capex info
                               hastriggers_properties_mixin,  # Give it investment triggers
                               hasland_properties_mixin),
                 {})

# Empty_stack class
Empty_Stack = type('Empty_Stack', (identifiable_properties_mixin,  # Give it a name
                               history_properties_mixin,
                               empty_stack_properties_mixin,
                               hasopex_properties_mixin,
                               hascapex_properties_mixin,  # Give it capex info
                               hastriggers_properties_mixin,  # Give it investment triggers
                               hasland_properties_mixin),
                            {})

# OOG_stack class
OOG_Stack = type('OOG_Stack', (identifiable_properties_mixin,  # Give it a name
                               history_properties_mixin,
                               oog_stack_properties_mixin,
                               hasopex_properties_mixin,
                               hascapex_properties_mixin,  # Give it capex info
                               hastriggers_properties_mixin,  # Give it investment triggers
                               hasland_properties_mixin),
                {})

# The general Gates class
Gate = type('Gate', (identifiable_properties_mixin,  # Give it a name
                               history_properties_mixin,
                               gate_properties_mixin,
                               hascapex_properties_mixin,  # Give it capex info
                               hasopex_properties_mixin,  # Give it opex info
                               hastriggers_properties_mixin,  # Give it investment triggers
                               hasland_properties_mixin),
                    {})

# The generic stack equipment class
# - RTG
# - RMG
# - Straddle carrier
# - Reach stacker
Stack_Equipment = type('Stack_Equipment', (identifiable_properties_mixin,  # Give it a name
                               history_properties_mixin,
                               stack_equipment_properties_mixin,
                               hascapex_properties_mixin,  # Give it capex info
                               hasopex_properties_mixin,  # Give it opex info
                               hastriggers_properties_mixin),  # Give it investment triggers
                 {})

# The general Empty Container Handler (ECH) class
Empty_Handler = type('Empty_Handler', (identifiable_properties_mixin,  # Give it a name
                               history_properties_mixin,
                                empty_handler_properties_mixin,
                               hascapex_properties_mixin,  # Give it capex info
                               hasopex_properties_mixin,  # Give it opex info
                               hastriggers_properties_mixin),  # Give it investment triggers
                 {})

# The general Vessel class
# - Handysize
# - Handymax
# - Panamax
# - Super Post-Panamax
Vessel = type('Vessel', (identifiable_properties_mixin,
                         vessel_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Labour class
Labour = type('Labour', (identifiable_properties_mixin,
                         labour_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Energy class
Energy = type('Energy', (identifiable_properties_mixin,
                         energy_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general services class

General_Services = type('General_Services', (identifiable_properties_mixin,
                                             hasland_properties_mixin,
                                             hasopex_properties_mixin,
                                             hascapex_properties_mixin,
                                             general_services_mixin,
                                             history_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The indirect costs class
Indirect_Costs = type('Indirect Costs', (identifiable_properties_mixin,
                         indirect_costs_mixin),
              {})  # The dictionary is empty because the site type is generic

# The land costs class
Land_Price = type('Land Price', (identifiable_properties_mixin,
                         hascapex_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The land costs class
Land_Price = type('Land Price', (identifiable_properties_mixin,
                         hascapex_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

