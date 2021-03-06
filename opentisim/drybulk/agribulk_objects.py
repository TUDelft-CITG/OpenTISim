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

from opentisim import agribulk_mixins

# The generic Quay_wall class
Quay_wall = type('Quay_wall', (agribulk_mixins.identifiable_properties_mixin,  # Give it a name
                               agribulk_mixins.quay_wall_properties_mixin,
                               agribulk_mixins.history_properties_mixin,  # Give it procurement history
                               agribulk_mixins.hascapex_properties_mixin,  # Give it capex info
                               agribulk_mixins.hasopex_properties_mixin,  # Give it opex info
                               agribulk_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                               agribulk_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                 {})  # The dictionary is empty because the site type is generic

# The generic Berth class
Berth = type('Berth', (agribulk_mixins.identifiable_properties_mixin,  # Give it a name
                       agribulk_mixins.history_properties_mixin,  # Give it procurement history
                       agribulk_mixins.berth_properties_mixin,
                       agribulk_mixins.hascapex_properties_mixin,  # Give it capex info
                       agribulk_mixins.hasopex_properties_mixin,  # Give it opex info
                       agribulk_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                       agribulk_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
             {})  # The dictionary is empty because the site type is generic

# The generic Cyclic_Unloader class
# - Gantry_crane
# - Harbour_crane
# - Mobile_crane
Cyclic_Unloader = type('Cyclic_Unloader', (agribulk_mixins.identifiable_properties_mixin,  # Give it a name
                                           agribulk_mixins.history_properties_mixin,  # Give it procurement history
                                           agribulk_mixins.cyclic_properties_mixin,
                                           agribulk_mixins.hascapex_properties_mixin,  # Give it capex info
                                           agribulk_mixins.hasopex_properties_mixin,  # Give it opex info
                                           agribulk_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                           agribulk_mixins.hastriggers_properties_mixin),
                       # Give it investment triggers (lambda?)
                       {})  # The dictionary is empty because the site type is generic

# The generic ContinuousUnloader class
# - Continuous_screw
Continuous_Unloader = type('Continuous_Unloader', (agribulk_mixins.identifiable_properties_mixin,  # Give it a name
                                                   agribulk_mixins.history_properties_mixin,  # Give it procurement history
                                                   agribulk_mixins.continuous_properties_mixin,
                                                   agribulk_mixins.hascapex_properties_mixin,  # Give it capex info
                                                   agribulk_mixins.hasopex_properties_mixin,  # Give it opex info
                                                   agribulk_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                                                   agribulk_mixins.hastriggers_properties_mixin),
                           # Give it investment triggers (lambda?)
                           {})  # The dictionary is empty because the site type is generic

# The generic Conveyor class
# - Quay_conveyor
# - Hinterland_conveyor
Conveyor_Quay = type('Conveyor_Quay', (agribulk_mixins.identifiable_properties_mixin,  # Give it a name
                             agribulk_mixins.history_properties_mixin,  # Give it procurement history
                             agribulk_mixins.conveyor_properties_mixin,
                             agribulk_mixins.hascapex_properties_mixin,  # Give it capex info
                             agribulk_mixins.hasopex_properties_mixin,  # Give it opex info
                             agribulk_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             agribulk_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

Conveyor_Hinter = type('Conveyor_Hinter', (agribulk_mixins.identifiable_properties_mixin,  # Give it a name
                             agribulk_mixins.history_properties_mixin,  # Give it procurement history
                             agribulk_mixins.conveyor_properties_mixin,
                             agribulk_mixins.hascapex_properties_mixin,  # Give it capex info
                             agribulk_mixins.hasopex_properties_mixin,  # Give it opex info
                             agribulk_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             agribulk_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

# The generic Storage class
# - Silo
# - Warehouse
Storage = type('Storage', (agribulk_mixins.identifiable_properties_mixin,  # Give it a name
                           agribulk_mixins.history_properties_mixin,  # Give it procurement history
                           agribulk_mixins.storage_properties_mixin,
                           agribulk_mixins.hascapex_properties_mixin,  # Give it capex info
                           agribulk_mixins.hasopex_properties_mixin,  # Give it opex info
                           agribulk_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                           agribulk_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})  # The dictionary is empty because the site type is generic

# define loading station class functions **will ultimately be placed in package**
Unloading_station = type('Unloading_station', (agribulk_mixins.identifiable_properties_mixin,  # Give it a name
                                               agribulk_mixins.unloading_station_properties_mixin),
                         {})  # The dictionary is empty because the site type is generic

# The generic Commodity class
# - Maize
# - Soybean
# - Wheat
Commodity = type('Commodity', (agribulk_mixins.identifiable_properties_mixin,  # Give it a name
                               agribulk_mixins.commodity_properties_mixin,
                               agribulk_mixins.hasscenario_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The general Vessel class
# - Handysize
# - Handymax
# - Panamax
Vessel = type('Vessel', (agribulk_mixins.identifiable_properties_mixin,
                         agribulk_mixins.vessel_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Labour class
Labour = type('Labour', (agribulk_mixins.identifiable_properties_mixin,
                         agribulk_mixins.labour_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Energy class
Energy = type('Energy', (agribulk_mixins.identifiable_properties_mixin,
                         agribulk_mixins.energy_properties_mixin),
              {})  # The dictionary is empty because the site type is generic

# The general Train class
Train = type('Train', (agribulk_mixins.identifiable_properties_mixin,
                       agribulk_mixins.train_properties_mixin),
             {})  # The dictionary is empty because the site type is generic
