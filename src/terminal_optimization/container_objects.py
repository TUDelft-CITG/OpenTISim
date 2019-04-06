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

from terminal_optimization import container_mixins

# The generic Quay_wall class
Quay_wall = type('Quay_wall', (containers_mixins.identifiable_properties_mixin,  # Give it a name
                               containers_mixins.quay_wall_properties_mixin,
                               containers_mixins.history_properties_mixin,  # Give it procurement history
                               containers_mixins.hascapex_properties_mixin,  # Give it capex info
                               containers_mixins.hasopex_properties_mixin,  # Give it opex info
                               containers_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                               containers_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                 {})  # The dictionary is empty because the site type is generic

# The generic Berth class
Berth = type('Berth', (containers_mixins.identifiable_properties_mixin,  # Give it a name
                       containers_mixins.history_properties_mixin,  # Give it procurement history
                       containers_mixins.berth_properties_mixin,
                       containers_mixins.hascapex_properties_mixin,  # Give it capex info
                       containers_mixins.hasopex_properties_mixin,  # Give it opex info
                       containers_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                       containers_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
             {})  # The dictionary is empty because the site type is generic

# The generic Cyclic_Unloader class
# - Gantry_crane
# - Harbour_crane
# - Mobile_crane
Cyclic_Unloader = type('Cyclic_Unloader', (containers_mixins.identifiable_properties_mixin,  # Give it a name
                                           containers_mixins.history_properties_mixin,  # Give it procurement history
                                           containers_mixins.cyclic_properties_mixin,
                                           containers_mixins.hascapex_properties_mixin,  # Give it capex info
                                           containers_mixins.hasopex_properties_mixin,  # Give it opex info
                                           containers_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                           containers_mixins.hastriggers_properties_mixin),
                       # Give it investment triggers (lambda?)
                       {})  # The dictionary is empty because the site type is generic

# The generic ContinuousUnloader class
# - Continuous_screw
Continuous_Unloader = type('Continuous_Unloader', (containers_mixins.identifiable_properties_mixin,  # Give it a name
                                                   containers_mixins.history_properties_mixin,  # Give it procurement history
                                                   containers_mixins.continuous_properties_mixin,
                                                   containers_mixins.hascapex_properties_mixin,  # Give it capex info
                                                   containers_mixins.hasopex_properties_mixin,  # Give it opex info
                                                   containers_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                                   containers_mixins.hastriggers_properties_mixin),
                           # Give it investment triggers (lambda?)
                           {})  # The dictionary is empty because the site type is generic

# The generic Conveyor class
# - Quay_conveyor
# - Hinterland_conveyor
Conveyor_Quay = type('Conveyor_Quay', (containers_mixins.identifiable_properties_mixin,  # Give it a name
                             containers_mixins.history_properties_mixin,  # Give it procurement history
                             containers_mixins.conveyor_properties_mixin,
                             containers_mixins.hascapex_properties_mixin,  # Give it capex info
                             containers_mixins.hasopex_properties_mixin,  # Give it opex info
                             containers_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             containers_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

Conveyor_Hinter = type('Conveyor_Hinter', (containers_mixins.identifiable_properties_mixin,  # Give it a name
                             containers_mixins.history_properties_mixin,  # Give it procurement history
                             containers_mixins.conveyor_properties_mixin,
                             containers_mixins.hascapex_properties_mixin,  # Give it capex info
                             containers_mixins.hasopex_properties_mixin,  # Give it opex info
                             containers_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             containers_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

# The generic Storage class
# - Silo
# - Warehouse
Storage = type('Storage', (containers_mixins.identifiable_properties_mixin,  # Give it a name
                           containers_mixins.history_properties_mixin,  # Give it procurement history
                           containers_mixins.storage_properties_mixin,
                           containers_mixins.hascapex_properties_mixin,  # Give it capex info
                           containers_mixins.hasopex_properties_mixin,  # Give it opex info
                           containers_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                           containers_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})  # The dictionary is empty because the site type is generic

# define loading station class functions **will ultimately be placed in package**
Unloading_station = type('Unloading_station', (containers_mixins.identifiable_properties_mixin,  # Give it a name
                                               containers_mixins.unloading_station_properties_mixin),
                         {})  # The dictionary is empty because the site type is generic

# The generic Commodity class
# - Maize
# - Soybean
# - Wheat
Commodity = type('Commodity', (containers_mixins.identifiable_properties_mixin,  # Give it a name
                               containers_mixins.commodity_properties_mixin,
                               containers_mixins.hasscenario_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The general Vessel class
# - Handysize
# - Handymax
# - Panamax
Vessel = type('Vessel', (containers_mixins.identifiable_properties_mixin,
                         containers_mixins.vessel_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Labour class
Labour = type('Labour', (containers_mixins.identifiable_properties_mixin,
                         containers_mixins.labour_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Energy class
Energy = type('Energy', (containers_mixins.identifiable_properties_mixin,
                         containers_mixins.energy_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Train class
Train = type('Train', (containers_mixins.identifiable_properties_mixin,
                       containers_mixins.train_properties_mixin),
             {})  # The dictionary is empty because the site type is generic
