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
- 8. Stack equipment
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

from opentisim import container_mixins

# The generic OGV_Quay_wall class
Quay_Wall = type('OGV_Quay_Wall', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                   container_mixins.quay_wall_properties_mixin,
                                   container_mixins.history_properties_mixin,       # Give it procurement history
                                   container_mixins.hascapex_properties_mixin,      # Give it capex info
                                   container_mixins.hasopex_properties_mixin,       # Give it opex info
                                   container_mixins.hasrevenue_properties_mixin,    # Give it revenue info
                                   container_mixins.hastriggers_properties_mixin,   # Give it investment triggers
                                   container_mixins.hasland_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The generic Barge_Quay_wall class
Offshore_Barge_Quay_Wall = type('Offshore Barge Quay Wall', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                                             container_mixins.quay_wall_properties_mixin,
                                                             container_mixins.history_properties_mixin,       # Give it procurement history
                                                             container_mixins.hascapex_properties_mixin,      # Give it capex info
                                                             container_mixins.hasopex_properties_mixin,       # Give it opex info
                                                             container_mixins.hasrevenue_properties_mixin,    # Give it revenue info
                                                             container_mixins.hastriggers_properties_mixin,   # Give it investment triggers
                                                             container_mixins.hasland_properties_mixin),
                                {})  # The dictionary is empty because the site type is generic

# The generic Barge_Quay_wall class
Onshore_Barge_Quay_Wall = type('Onshore Barge Quay Wall', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                                           container_mixins.quay_wall_properties_mixin,
                                                           container_mixins.history_properties_mixin,       # Give it procurement history
                                                           container_mixins.hascapex_properties_mixin,      # Give it capex info
                                                           container_mixins.hasopex_properties_mixin,       # Give it opex info
                                                           container_mixins.hasrevenue_properties_mixin,    # Give it revenue info
                                                           container_mixins.hastriggers_properties_mixin,   # Give it investment triggers
                                                           container_mixins.hasland_properties_mixin),
                               {})  # The dictionary is empty because the site type is generic

# The generic OGV Berth class
Berth = type('Berth', (container_mixins.identifiable_properties_mixin,                  # Give it a name
                       container_mixins.history_properties_mixin,                       # Give it procurement history
                       container_mixins.berth_properties_mixin,                         # Give it berth properties
                       container_mixins.hascapex_properties_mixin,                      # Give it capex info
                       container_mixins.hasopex_properties_mixin,                       # Give it opex info
                       container_mixins.hasrevenue_properties_mixin,                    # Give it revenue info
                       container_mixins.hastriggers_properties_mixin),                  # Give it investment triggers
             {})  # The dictionary is empty because the site type is generic

# The general Barge Berth class
Offshore_Barge_Berth = type('Offshore Barge Berth', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                                     container_mixins.history_properties_mixin,
                                                     container_mixins.barge_berth_properties_mixin,
                                                     container_mixins.hascapex_properties_mixin,  # Give it capex info
                                                     container_mixins.hasopex_properties_mixin,  # Give it opex info
                                                     container_mixins.hastriggers_properties_mixin,  # Give it investment triggers
                                                     container_mixins.hasland_properties_mixin),
                            {})  # The dictionary is empty because the site type is generic

# The general Onshore Barge Berth class
Onshore_Barge_Berth = type('Onshore Barge Berth', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                                   container_mixins.history_properties_mixin,
                                                   container_mixins.barge_berth_properties_mixin,
                                                   container_mixins.hascapex_properties_mixin,  # Give it capex info
                                                   container_mixins.hasopex_properties_mixin,  # Give it opex info
                                                   container_mixins.hastriggers_properties_mixin,  # Give it investment triggers
                                                   container_mixins.hasland_properties_mixin),
                           {})  # The dictionary is empty because the site type is generic

# The generic Channel class
Channel = type('Channel', (container_mixins.identifiable_properties_mixin,              # Give it a name
                           container_mixins.history_properties_mixin,                   # Give it procurement history
                           container_mixins.channel_properties_mixin,                   # Give it channel properties
                           container_mixins.hascapex_properties_mixin,                  # Give it capex info
                           container_mixins.hasopex_properties_mixin,                   # Give it opex info
                           container_mixins.hastriggers_properties_mixin),              # Give it investment triggers
               {})  # The dictionary is empty because the site type is generic

# The generic Channel class
Barge_Channel = type('Barge_Channel', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                       container_mixins.history_properties_mixin,       # Give it procurement history
                                       container_mixins.channel_properties_mixin,       # Give it channel properties
                                       container_mixins.hascapex_properties_mixin,      # Give it capex info
                                       container_mixins.hasopex_properties_mixin,       # Give it opex info
                                       container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
               {})  # The dictionary is empty because the site type is generic

# The generic Bridge class
Bridge = type('Bridge', (container_mixins.identifiable_properties_mixin,                # Give it a name
                         container_mixins.history_properties_mixin,                     # Give it procurement history
                         container_mixins.bridge_properties_mixin,                      # Give it bridge properties
                         container_mixins.hascapex_properties_mixin,                    # Give it capex info
                         container_mixins.hasopex_properties_mixin,                     # Give it opex info
                         container_mixins.hastriggers_properties_mixin),                # Give it investment triggers
              {})  # The dictionary is empty because the site type is generic

# The generic Channel class
Reclamation = type('Reclamation', (container_mixins.identifiable_properties_mixin,      # Give it a name
                                   container_mixins.history_properties_mixin,           # Give it procurement history
                                   container_mixins.reclamation_properties_mixin,       # Give it reclamation properties
                                   container_mixins.hascapex_properties_mixin,          # Give it capex info
                                   container_mixins.hasopex_properties_mixin,           # Give it opex info
                                   container_mixins.hastriggers_properties_mixin),      # Give it investment triggers
                     {})  # The dictionary is empty because the site type is generic

# The generic Channel class
Revetment = type('Revetment', (container_mixins.identifiable_properties_mixin,          # Give it a name
                               container_mixins.history_properties_mixin,               # Give it procurement history
                               container_mixins.revetment_properties_mixin,             # Give it revetment properties
                               container_mixins.hascapex_properties_mixin,              # Give it capex info
                               container_mixins.hasopex_properties_mixin,               # Give it opex info
                               container_mixins.hastriggers_properties_mixin),          # Give it investment triggers
                 {})  # The dictionary is empty because the site type is generic

# The generic Channel class
Breakwater = type('Breakwater', (container_mixins.identifiable_properties_mixin,        # Give it a name
                                 container_mixins.history_properties_mixin,             # Give it procurement history
                                 container_mixins.breakwater_properties_mixin,          # Give it breakwater properties
                                 container_mixins.hascapex_properties_mixin,            # Give it capex info
                                 container_mixins.hasopex_properties_mixin,             # Give it opex info
                                 container_mixins.hastriggers_properties_mixin),        # Give it investment triggers
                  {})  # The dictionary is empty because the site type is generic

# The generic Barge class
Barge = type('Barge', (container_mixins.identifiable_properties_mixin,  # Give it a name
                       container_mixins.history_properties_mixin,       # Give it procurement history
                       container_mixins.barge_properties_mixin,         # Give it barge properties
                       container_mixins.hascapex_properties_mixin,      # Give it capex info
                       container_mixins.hasopex_properties_mixin,       # Give it opex info
                       container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
             {})  # The dictionary is empty because the site type is generic

# The generic Channel class
Truck = type('Truck', (container_mixins.identifiable_properties_mixin,  # Give it a name
                       container_mixins.history_properties_mixin,       # Give it procurement history
                       container_mixins.truck_properties_mixin,         # Give it truck properties
                       container_mixins.hascapex_properties_mixin,      # Give it capex info
                       container_mixins.hasopex_properties_mixin,       # Give it opex info
                       container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
             {})  # The dictionary is empty because the site type is generic

# The generic Cyclic_Unloader class
Cyclic_Unloader = type('Cyclic_Unloader', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                           container_mixins.history_properties_mixin,  # Give it procurement history
                                           container_mixins.cyclic_properties_mixin,
                                           container_mixins.hascapex_properties_mixin,  # Give it capex info
                                           container_mixins.hasopex_properties_mixin,  # Give it opex info
                                           container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                           container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
                       {})  # The dictionary is empty because the site type is generic

# The generic Offshore Barge Crane class
Offshore_Barge_Crane = type('Offshore_Barge_Crane', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                                     container_mixins.history_properties_mixin,  # Give it procurement history
                                                     container_mixins.barge_crane_properties_mixin,
                                                     container_mixins.hascapex_properties_mixin,  # Give it capex info
                                                     container_mixins.hasopex_properties_mixin,  # Give it opex info
                                                     container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                                     container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
                           {})  # The dictionary is empty because the site type is generic

# The generic Onshore Barge Crane class
Onshore_Barge_Crane = type('Onshore_Barge_Crane', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                                   container_mixins.history_properties_mixin,  # Give it procurement history
                                                   container_mixins.barge_crane_properties_mixin,
                                                   container_mixins.hascapex_properties_mixin,  # Give it capex info
                                                   container_mixins.hasopex_properties_mixin,  # Give it opex info
                                                   container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                                   container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
                           {})  # The dictionary is empty because the site type is generic

# The generic Horizontal transport class
Horizontal_Transport = type('Horizontal_Transport', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                                     container_mixins.history_properties_mixin,  # Give it procurement history
                                                     container_mixins.transport_properties_mixin,
                                                     container_mixins.hascapex_properties_mixin,  # Give it capex info
                                                     container_mixins.hasopex_properties_mixin,  # Give it opex info
                                                     container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
                            {})  # The dictionary is empty because the site type is generic

# The generic Commodity class
Commodity = type('Commodity', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.commodity_properties_mixin,
                               container_mixins.hasscenario_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The generic container class
Container = type('Container', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.container_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The generic laden and reefer stack class
Laden_Stack = type('Laden_Stack', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                   container_mixins.history_properties_mixin,
                                   container_mixins.laden_stack_properties_mixin,
                                   container_mixins.hasopex_properties_mixin,
                                   container_mixins.hascapex_properties_mixin,  # Give it capex info
                                   container_mixins.hastriggers_properties_mixin,  # Give it investment triggers
                                   container_mixins.hasland_properties_mixin),
                   {})  # The dictionary is empty because the site type is generic

# The generic stack equipment class
Stack_Equipment = type('Stack_Equipment', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                           container_mixins.history_properties_mixin,
                                           container_mixins.stack_equipment_properties_mixin,
                                           container_mixins.hascapex_properties_mixin,  # Give it capex info
                                           container_mixins.hasopex_properties_mixin,  # Give it opex info
                                           container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
                       {})  # The dictionary is empty because the site type is generic

# Empty_stack class
Empty_Stack = type('Empty_Stack', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                   container_mixins.history_properties_mixin,
                                   container_mixins.empty_stack_properties_mixin,
                                   container_mixins.hasopex_properties_mixin,
                                   container_mixins.hascapex_properties_mixin,  # Give it capex info
                                   container_mixins.hastriggers_properties_mixin,  # Give it investment triggers
                                   container_mixins.hasland_properties_mixin),
                   {})  # The dictionary is empty because the site type is generic

# OOG_stack class
OOG_Stack = type('Empty_Stack', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                 container_mixins.history_properties_mixin,
                                 container_mixins.oog_stack_properties_mixin,
                                 container_mixins.hasopex_properties_mixin,
                                 container_mixins.hascapex_properties_mixin,  # Give it capex info
                                 container_mixins.hastriggers_properties_mixin,  # Give it investment triggers
                                 container_mixins.hasland_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The general Gates class
Gate = type('Gate', (container_mixins.identifiable_properties_mixin,    # Give it a name
                     container_mixins.history_properties_mixin,
                     container_mixins.gate_properties_mixin,
                     container_mixins.hascapex_properties_mixin,        # Give it capex info
                     container_mixins.hasopex_properties_mixin,         # Give it opex info
                     container_mixins.hastriggers_properties_mixin,     # Give it investment triggers
                     container_mixins.hasland_properties_mixin),
            {})  # The dictionary is empty because the site type is generic

# The general Empty Container Handler (ECH) class
Empty_Handler = type('Empty_Handler', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                       container_mixins.history_properties_mixin,
                                       container_mixins.empty_handler_properties_mixin,
                                       container_mixins.hascapex_properties_mixin,  # Give it capex info
                                       container_mixins.hasopex_properties_mixin,  # Give it opex info
                                       container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
                     {})  # The dictionary is empty because the site type is generic

# The general Vessel class
Vessel = type('Vessel', (container_mixins.identifiable_properties_mixin,
                         container_mixins.history_properties_mixin,
                         container_mixins.vessel_properties_mixin,
                         container_mixins.hascapex_properties_mixin,  # Give it capex info
                         container_mixins.hasopex_properties_mixin,  # Give it opex info
                         container_mixins.hastriggers_properties_mixin),  # Give it investment triggers
              {})  # The dictionary is empty because the site type is generic

# The general Labour class
Labour = type('Labour', (container_mixins.identifiable_properties_mixin,
                         container_mixins.labour_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Energy class
Energy = type('Energy', (container_mixins.identifiable_properties_mixin,
                         container_mixins.energy_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general services class
General_Services = type('General_Services', (container_mixins.identifiable_properties_mixin,
                                             container_mixins.hasland_properties_mixin,
                                             container_mixins.hasopex_properties_mixin,
                                             container_mixins.hascapex_properties_mixin,
                                             container_mixins.general_services_mixin,
                                             container_mixins.history_properties_mixin),
                        {})  # The dictionary is empty because the site type is generic

# The indirect costs class
Indirect_Costs = type('Indirect Costs', (container_mixins.identifiable_properties_mixin,
                                         container_mixins.indirect_costs_mixin),
                      {})  # The dictionary is empty because the site type is generic

# The land costs class
Land_Price = type('Land Price', (container_mixins.identifiable_properties_mixin,
                                 container_mixins.hascapex_properties_mixin),
                  {})  # The dictionary is empty because the site type is generic
