"""Main generic object classes:

- 1. Quay_wall
- 2. Berth
- 3. Cyclic_Unloader
    - Gantry crane
    - Harbour crane
    - Mobile crane
     Continuous_Unloader
    - Continuous screw
- 4. Conveyor
    - Hinterland conveyor
    - Quay conveyor
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

from terminal_optimization import mixins

# The generic Quay_wall class
Quay_wall = type('Quay_wall', (mixins.identifiable_properties_mixin,  # Give it a name
                               mixins.quay_wall_properties_mixin,
                               mixins.history_properties_mixin,  # Give it procurement history
                               mixins.hascapex_properties_mixin,  # Give it capex info
                               mixins.hasopex_properties_mixin,  # Give it opex info
                               mixins.hasrevenue_properties_mixin,  # Give it revenue info
                               mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                 {})  # The dictionary is empty because the site type is generic

# The generic Berth class
Berth = type('Berth', (mixins.identifiable_properties_mixin,  # Give it a name
                       mixins.history_properties_mixin,  # Give it procurement history
                       mixins.berth_properties_mixin,
                       mixins.hascapex_properties_mixin,  # Give it capex info
                       mixins.hasopex_properties_mixin,  # Give it opex info
                       mixins.hasrevenue_properties_mixin,  # Give it revenue info
                       mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
             {})  # The dictionary is empty because the site type is generic

# The generic Cyclic_Unloader class
# - Gantry_crane
# - Harbour_crane
# - Mobile_crane
Cyclic_Unloader = type('Cyclic_Unloader', (mixins.identifiable_properties_mixin,  # Give it a name
                                           mixins.history_properties_mixin,  # Give it procurement history
                                           mixins.cyclic_properties_mixin,
                                           mixins.hascapex_properties_mixin,  # Give it capex info
                                           mixins.hasopex_properties_mixin,  # Give it opex info
                                           mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                           mixins.hastriggers_properties_mixin),
                       # Give it investment triggers (lambda?)
                       {})  # The dictionary is empty because the site type is generic

# The generic ContinuousUnloader class
# - Continuous_screw
Continuous_Unloader = type('Continuous_Unloader', (mixins.identifiable_properties_mixin,  # Give it a name
                                                   mixins.history_properties_mixin,  # Give it procurement history
                                                   mixins.continuous_properties_mixin,
                                                   mixins.hascapex_properties_mixin,  # Give it capex info
                                                   mixins.hasopex_properties_mixin,  # Give it opex info
                                                   mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                                   mixins.hastriggers_properties_mixin),
                           # Give it investment triggers (lambda?)
                           {})  # The dictionary is empty because the site type is generic

# The generic Conveyor class
# - Quay_conveyor
# - Hinterland_conveyor
Conveyor_Quay = type('Conveyor_Quay', (mixins.identifiable_properties_mixin,  # Give it a name
                             mixins.history_properties_mixin,  # Give it procurement history
                             mixins.conveyor_properties_mixin,
                             mixins.hascapex_properties_mixin,  # Give it capex info
                             mixins.hasopex_properties_mixin,  # Give it opex info
                             mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

Conveyor_Hinter = type('Conveyor_Hinter', (mixins.identifiable_properties_mixin,  # Give it a name
                             mixins.history_properties_mixin,  # Give it procurement history
                             mixins.conveyor_properties_mixin,
                             mixins.hascapex_properties_mixin,  # Give it capex info
                             mixins.hasopex_properties_mixin,  # Give it opex info
                             mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic


# todo: check if Unloader and Conveyor can be the same

# The generic Storage class
# - Silo
# - Warehouse
Storage = type('Storage', (mixins.identifiable_properties_mixin,  # Give it a name
                           mixins.history_properties_mixin,  # Give it procurement history
                           mixins.storage_properties_mixin,
                           mixins.hascapex_properties_mixin,  # Give it capex info
                           mixins.hasopex_properties_mixin,  # Give it opex info
                           mixins.hasrevenue_properties_mixin,  # Give it revenue info
                           mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})  # The dictionary is empty because the site type is generic

# define loading station class functions **will ultimately be placed in package**
Unloading_station = type('Unloading_station', (mixins.identifiable_properties_mixin,  # Give it a name
                                               mixins.unloading_station_properties_mixin),
                         {})  # The dictionary is empty because the site type is generic

# The generic Commodity class
# - Maize
# - Soybean
# - Wheat
Commodity = type('Commodity', (mixins.identifiable_properties_mixin,  # Give it a name
                               mixins.commodity_properties_mixin,
                               mixins.hasscenario_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The general Vessel class
# - Handysize
# - Handymax
# - Panamax
Vessel = type('Vessel', (mixins.identifiable_properties_mixin,
                         mixins.vessel_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Labour class
Labour = type('Labour', (mixins.identifiable_properties_mixin,
                         mixins.labour_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Energy class
Energy = type('Energy', (mixins.identifiable_properties_mixin,
                         mixins.energy_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Train class
Train = type('Train', (mixins.identifiable_properties_mixin,
                       mixins.train_properties_mixin),
             {})  # The dictionary is empty because the site type is generic
