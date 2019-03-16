from terminal_optimization import objects
from terminal_optimization import defaults

print('')
print('*** Test general Quay_wall class')
print('')

print('test Quay_wall: quay wall')
print(defaults.quay_wall_data)
quay_wall01 = objects.Quay_wall(**defaults.quay_wall_data)
print(quay_wall01.__dict__)

print('')
print('*** Test general Berth class')
print('')

print('test Berth: berth')
print(defaults.berth_data)
berth = objects.Berth(**defaults.berth_data)
print(berth.__dict__)

print('')
print('*** Test general Cyclic_Unloader class')
print('')

print('test Cyclic_Unloader: gantry crane')
print(defaults.gantry_crane_data)
unloader_01 = objects.Cyclic_Unloader(**defaults.gantry_crane_data)
print(unloader_01.__dict__)

print('test Cyclic_Unloader: harbour crane')
print(defaults.harbour_crane_data)
unloader_02 = objects.Cyclic_Unloader(**defaults.harbour_crane_data)
print(unloader_02.__dict__)

print('test Cyclic_Unloader: mobile crane')
print(defaults.mobile_crane_data)
unloader_03 = objects.Cyclic_Unloader(**defaults.mobile_crane_data)
print(unloader_03.__dict__)

print('')
print('*** Test general Continuous_Unloader class')
print('')

print('test Continuous_Unloader: continuous screw')
print(defaults.continuous_screw_data)
unloader_04 = objects.Continuous_Unloader(**defaults.continuous_screw_data)
print(unloader_04.__dict__)

print('')
print('*** Test general Conveyor class')
print('')

print('test Conveyor: quay conveyor')
print(defaults.quay_conveyor_data)
conveyor_01 = objects.Conveyor(**defaults.quay_conveyor_data)
print(conveyor_01.__dict__)

print('test Conveyor: hinterland conveyor')
print(defaults.hinterland_conveyor_data)
conveyor_02 = objects.Conveyor(**defaults.hinterland_conveyor_data)
print(conveyor_02.__dict__)

print('')
print('*** Test general Unloading_station class')
print('')

print('test Unloading_station: hinterland station')
print(defaults.hinterland_station_data)
hinterland_station_01 = objects.Unloading_station(**defaults.hinterland_station_data)
print(hinterland_station_01.__dict__)

print('')
print('*** Test general Commodity class')
print('')

print('test Commodity: wheat')
print(defaults.wheat_data)
wheat = objects.Commodity(**defaults.wheat_data)
print(wheat.__dict__)

print('test Commodity: maize')
print(defaults.maize_data)
maize = objects.Commodity(**defaults.maize_data)
print(maize.__dict__)

print('test Commodity: soybean')
print(defaults.soybean_data)
soybean = objects.Commodity(**defaults.soybean_data)
print(soybean.__dict__)

print('')
print('*** Test general Vessel class')
print('')

print('test Vessel: handysize')
print(defaults.handysize_data)
handysize = objects.Vessel(**defaults.handysize_data)
print(handysize.__dict__)

print('test Vessel: handymax')
print(defaults.handymax_data)
handymax = objects.Vessel(**defaults.handymax_data)
print(handymax.__dict__)

print('test Vessel: panamax')
print(defaults.panamax_data)
panamax = objects.Vessel(**defaults.panamax_data)
print(panamax.__dict__)

print('')
print('*** Test general Labour class')
print('')

print('test Labour: labour')
print(defaults.labour_data)
labour = objects.Labour(**defaults.labour_data)
print(labour.__dict__)

print('')
print('*** Test general Energy class')
print('')

print('test Energy: energy')
print(defaults.energy_data)
energy = objects.Energy(**defaults.energy_data)
print(energy.__dict__)
