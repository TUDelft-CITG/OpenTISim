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
- 6. Commodity
    - Liquid hydrogen
    - Ammonia
    - MCH
- 7. Vessel
    - smallhydrogen
    - largehydrogen
    - smallammonia
    - largeammonia
    - Handysize
    - Panamax
    - VLCC
- 8. Labour
"""

from opentisim import hydrogen_mixins

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

# The generic H2retrieval class
# - LH2
# - NH3
# - MCH

H2retrieval = type('H2retrieval', (hydrogen_mixins.identifiable_properties_mixin,  # Give it a name
                           hydrogen_mixins.history_properties_mixin,  # Give it procurement history
                           hydrogen_mixins.h2retrieval_properties_mixin,
                           hydrogen_mixins.hascapex_properties_mixin,  # Give it capex info
                           hydrogen_mixins.hasopex_properties_mixin,  # Give it opex info
                           hydrogen_mixins.hasrevenue_properties_mixin,  # Give it revenue info
                           hydrogen_mixins.hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
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
