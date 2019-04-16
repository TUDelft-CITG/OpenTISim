"""Main generic object classes:

- 1. Quay_wall
- 2. Berth
- 3. Cyclic_Unloader
    - STS crane
- 4. Conveyor
    - Hinterland conveyor
    - Quay conveyor
- 4. Horizontal transport
    - Tractor trailer
- 5. Containers
    - Laden
    - Reefer
    - Empty
    - OOG
- 5. Storage
    - Silo
    - Warehouse
- 6. Unloading_station
    - Hinterland station
- 7. Commodity
    - Maize
    - Soybean
    - Wheat
- 8. Vessel
    - Handysize
    - Handymax
    - Panamax
- 9. Labour

"""

from terminal_optimization import container_mixins

# The generic Quay_wall class
Quay_wall = type('Quay_wall', (container_mixins.identifiable_properties_mixin,  # Give it a name
                               container_mixins.quay_wall_properties_mixin,
                               container_mixins.history_properties_mixin,  # Give it procurement history
                               container_mixins.hascapex_properties_mixin,  # Give it capex info
                               container_mixins.hasopex_properties_mixin,  # Give it opex info
                               container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                               container_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
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

# The generic ContinuousUnloader class
# - Continuous_screw
Continuous_Unloader = type('Continuous_Unloader', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                                   container_mixins.history_properties_mixin,  # Give it procurement history
                                                   container_mixins.continuous_properties_mixin,
                                                   container_mixins.hascapex_properties_mixin,  # Give it capex info
                                                   container_mixins.hasopex_properties_mixin,  # Give it opex info
                                                   container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                                   container_mixins.hastriggers_properties_mixin),
                           # Give it investment triggers (lambda?)
                           {})  # The dictionary is empty because the site type is generic

# The generic Conveyor class
# - Quay_conveyor
# - Hinterland_conveyor
Conveyor_Quay = type('Conveyor_Quay', (container_mixins.identifiable_properties_mixin,  # Give it a name
                             container_mixins.history_properties_mixin,  # Give it procurement history
                             container_mixins.conveyor_properties_mixin,
                             container_mixins.hascapex_properties_mixin,  # Give it capex info
                             container_mixins.hasopex_properties_mixin,  # Give it opex info
                             container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             container_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

Conveyor_Hinter = type('Conveyor_Hinter', (container_mixins.identifiable_properties_mixin,  # Give it a name
                             container_mixins.history_properties_mixin,  # Give it procurement history
                             container_mixins.conveyor_properties_mixin,
                             container_mixins.hascapex_properties_mixin,  # Give it capex info
                             container_mixins.hasopex_properties_mixin,  # Give it opex info
                             container_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             container_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
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

# define loading station class functions **will ultimately be placed in package**
Unloading_station = type('Unloading_station', (container_mixins.identifiable_properties_mixin,  # Give it a name
                                               container_mixins.unloading_station_properties_mixin),
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

# The general Train class
Train = type('Train', (container_mixins.identifiable_properties_mixin,
                       container_mixins.train_properties_mixin),
             {})  # The dictionary is empty because the site type is generic
