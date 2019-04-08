"""Main generic object classes:

Defaults for following objects:
- 1. Jetty
- 2. Berth
- 3. Unloader
    - Liquid hydrogen
    - Ammonia
    - MCH
- 4. Pipelines
    - jetty
    - hinterland
- 5. Storage
    - Liquid hydrogen
    - Ammonia
    - MCH
- 6. H2 retrieval
    - Ammonia
    - MCH
- 6. Unloading_station
    - Hinterland station
- 7. Commodity
    - Liquid hydrogen
    - Ammonia
    - MCH
- 8. Vessel
    - smallhydrogen
    - largehydrogen
    - smallammonia
    - largeammonia
    - Handysize
    - Panamax
    - VLCC
- 9. Labour
"""

from terminal_optimization import hydrogen_mixins

# The generic jetty class
Jetty = type('Jetty', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                               hydrogen_mixins.jetty_properties_mixin,
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

# # The generic Cyclic_Unloader class
# # - Gantry_crane
# # - Harbour_crane
# # - Mobile_crane
# Cyclic_Unloader = type('Cyclic_Unloader', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
#                                            hydrogen_mixins.history_properties_mixin,  # Give it procurement history
#                                            hydrogen_mixins.cyclic_properties_mixin,
#                                            hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
#                                            hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
#                                            hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
#                                            hydrogen_mixins.hastriggers_properties_mixin),
#                        # Give it investment triggers (lambda?)
#                        {})  # The dictionary is empty because the site type is generic
#
# # The generic ContinuousUnloader class
# # - Continuous_screw
# Continuous_Unloader = type('Continuous_Unloader', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
#                                                    hydrogen_mixins.history_properties_mixin,  # Give it procurement history
#                                                    hydrogen_mixins.continuous_properties_mixin,
#                                                    hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
#                                                    hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
#                                                    hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
#                                                    hydrogen_mixins.hastriggers_properties_mixin),
#                            # Give it investment triggers (lambda?)
#                            {})  # The dictionary is empty because the site type is generic

# The generic Conveyor class
# - Quay_conveyor
# - Hinterland_conveyor
Pipeline_Jetty = type('Pipeline_Jetty', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                             hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                             hydrogen_mixins.pipeline_properties_mixin,
                             hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                             hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                             hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             hydrogen_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

Pipeline_Hinter = type('Pipeline_Hinter', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                             hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                             hydrogen_mixins.pipeline_properties_mixin,
                             hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                             hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                             hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                             hydrogen_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

# The generic Storage class
# - LH2
# - NH3
# - MCH
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
# - Liquid hydrogen
# - Ammonia
# - MCH
Commodity = type('Commodity', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                               hydrogen_mixins.commodity_properties_mixin,
                               hydrogen_mixins.hasscenario_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The general Vessel class
# - smallhydrogen
# - largehydrogen
# - smallammonia
# - largeammonia
# - Handysize
# - Panamax
# - VLCC
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
