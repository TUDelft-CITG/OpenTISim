from terminal_optimization import objects
from terminal_optimization import defaults

maize = objects.Commodity(**defaults.maize_data)
wheat = objects.Commodity(**defaults.wheat_data)
soybeans = objects.Commodity(**defaults.soybean_data)

maize.scenario_random()

print(maize.historic_data)

print(maize.scenario_data)

if False:
    print(maize.__dict__)

