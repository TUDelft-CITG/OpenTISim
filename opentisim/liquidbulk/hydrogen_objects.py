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

from .hydrogen_mixins import *

# The generic jetty class
Jetty = type('Jetty', (identifiable_properties_mixin,  # Give it a name
                       jetty_properties_mixin,
                       history_properties_mixin,  # Give it procurement history
                       hascapex_properties_mixin,  # Give it capex info
                       hasopex_properties_mixin,  # Give it opex info
                       hasrevenue_properties_mixin,  # Give it revenue info
                       hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
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


# The generic Conveyor class
# - Quay_conveyor
# - Hinterland_conveyor
Pipeline_Jetty = type('Pipeline_Jetty', (identifiable_properties_mixin,  # Give it a name
                             history_properties_mixin,  # Give it procurement history
                             pipeline_properties_mixin,
                             hascapex_properties_mixin,  # Give it capex info
                             hasopex_properties_mixin,  # Give it opex info
                             hasrevenue_properties_mixin,  # Give it revenue info
                             hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

Pipeline_Hinter = type('Pipeline_Hinter', (identifiable_properties_mixin,  # Give it a name
                             history_properties_mixin,  # Give it procurement history
                             pipeline_properties_mixin,
                             hascapex_properties_mixin,  # Give it capex info
                             hasopex_properties_mixin,  # Give it opex info
                             hasrevenue_properties_mixin,  # Give it revenue info
                             hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
                {})  # The dictionary is empty because the site type is generic

# The generic Storage class
# - LH2
# - NH3
# - MCH
Storage = type('Storage', (identifiable_properties_mixin,  # Give it a name
                           history_properties_mixin,  # Give it procurement history
                           storage_properties_mixin,
                           hascapex_properties_mixin,  # Give it capex info
                           hasopex_properties_mixin,  # Give it opex info
                           hasrevenue_properties_mixin,  # Give it revenue info
                           hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})  # The dictionary is empty because the site type is generic

# The generic H2retrieval class
# - LH2
# - NH3
# - MCH

H2retrieval = type('H2retrieval', (identifiable_properties_mixin,  # Give it a name
                           history_properties_mixin,  # Give it procurement history
                           h2retrieval_properties_mixin,
                           hascapex_properties_mixin,  # Give it capex info
                           hasopex_properties_mixin,  # Give it opex info
                           hasrevenue_properties_mixin,  # Give it revenue info
                           hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})  # The dictionary is empty because the site type is generic

H2conversion = type('H2conversion', (identifiable_properties_mixin,  # Give it a name
                           history_properties_mixin,  # Give it procurement history
                           h2conversion_properties_mixin,
                           hascapex_properties_mixin,  # Give it capex info
                           hasopex_properties_mixin,  # Give it opex info
                           hasrevenue_properties_mixin,  # Give it revenue info
                           hastriggers_properties_mixin),  # Give it investment triggers (lambda?)
               {})  # The dictionary is empty because the site type is generic

# The generic Commodity class
# - Liquid hydrogen
# - Ammonia
# - MCH
Commodity = type('Commodity', (identifiable_properties_mixin,  # Give it a name
                               commodity_properties_mixin,
                               hasscenario_properties_mixin),
                 {})  # The dictionary is empty because the site type is generic

# The general Vessel class
# - smallhydrogen
# - largehydrogen
# - smallammonia
# - largeammonia
# - Handysize
# - Panamax
# - VLCC
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

# The general Train class
Train = type('Train', (identifiable_properties_mixin,
                       train_properties_mixin),
             {})  # The dictionary is empty because the site type is generic
