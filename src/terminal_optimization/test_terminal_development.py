from terminal_optimization import objects
from terminal_optimization import defaults
from terminal_optimization import system

# instantiate a commodity object
maize = objects.Commodity(**defaults.maize_data)
wheat = objects.Commodity(**defaults.wheat_data)
soybeans = objects.Commodity(**defaults.soybean_data)

# create a future througput scenario
maize.scenario_random()
wheat.scenario_random()
soybeans.scenario_random()
cargo = [maize, wheat, soybeans]

# instantiate vessels
handysize = objects.Vessel(**defaults.handysize_data)
handymax = objects.Vessel(**defaults.handymax_data)
panamax = objects.Vessel(**defaults.panamax_data)
vessels = [handysize, handymax, panamax]

# instantiate System object
Terminal = system.System(elements=cargo + vessels)

# start parametric terminal development
Terminal.simulate()

if False:
    for element in Terminal.elements:
        print("")
        print(element.name)
        print("")
        print(element.__dict__)
