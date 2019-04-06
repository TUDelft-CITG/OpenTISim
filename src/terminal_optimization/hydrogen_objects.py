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

from terminal_optimization import hydrogen_mixins

# The generic Quay_wall class
Quay_wall = type('Quay_wall', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                               hydrogen_mixins.quay_wall_properties_mixin,
                               hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                               hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                               hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                               hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                               hydrogen_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                 {})  # The dictionary is empty because the site type is generic

# The generic Berth class
Berth = type('Berth', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                       hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                       hydrogen_mixins.berth_properties_mixin,
                       hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                       hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                       hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                       hydrogen_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
             {})  # The dictionary is empty because the site type is generic

# The generic Cyclic_Unloader class
# - Gantry_crane
# - Harbour_crane
# - Mobile_crane
Cyclic_Unloader = type('Cyclic_Unloader', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                                           hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                                           hydrogen_mixins.cyclic_properties_mixin,
                                           hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                                           hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                                           hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                           hydrogen_mixins.hastriggers_properties_mixin),
                       # Give it investment triggers (lambda?)
                       {})  # The dictionary is empty because the site type is generic

# The generic ContinuousUnloader class
# - Continuous_screw
Continuous_Unloader = type('Continuous_Unloader', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                                                   hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                                                   hydrogen_mixins.continuous_properties_mixin,
                                                   hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                                                   hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                                                   hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                                   hydrogen_mixins.hastriggers_properties_mixin),
                           # Give it investment triggers (lambda?)
                           {})  # The dictionary is empty because the site type is generic

# The generic Conveyor class
# - Quay_conveyor
# - Hinterland_conveyor
Conveyor_Quay = type('Conveyor_Quay', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                             hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                             hydrogen_mixins.conveyor_properties_mixin,
                             hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                             hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                             hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             hydrogen_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

Conveyor_Hinter = type('Conveyor_Hinter', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                             hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                             hydrogen_mixins.conveyor_properties_mixin,
                             hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                             hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                             hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             hydrogen_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

# The generic Storage class
# - Silo
# - Warehouse
Storage = type('Storage', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                           hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                           hydrogen_mixins.storage_properties_mixin,
                           hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                           hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                           hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                           hydrogen_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})  # The dictionary is empty because the site type is generic

# define loading station class functions **will ultimately be placed in package**
Unloading_station = type('Unloading_station', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                                               hydrogen_mixins.unloading_station_properties_mixin),
                         {})  # The dictionary is empty because the site type is generic

# The generic Commodity class
# - Maize
# - Soybean
# - Wheat
Commodity = type('Commodity', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                               hydrogen_mixins.commodity_properties_mixin,
                               hydrogen_mixins.hasscenario_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The general Vessel class
# - Handysize
# - Handymax
# - Panamax
Vessel = type('Vessel', (hydrogen_mixins.identifiable_properties_mixin,
                         hydrogen_mixins.vessel_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Labour class
Labour = type('Labour', (hydrogen_mixins.identifiable_properties_mixin,
                         hydrogen_mixins.labour_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Energy class
Energy = type('Energy', (hydrogen_mixins.identifiable_properties_mixin,
                         hydrogen_mixins.energy_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Train class
Train = type('Train', (hydrogen_mixins.identifiable_properties_mixin,
                       hydrogen_mixins.train_properties_mixin),
             {})  # The dictionary is empty because the site type is generic
