"""Tests for `opentisim` package."""

def test_containers_02_complete_lifecycle():
	"""Test to see if for a given demand scenario and vessel mix the expected number of
	terminal elements are suggested - in this testcase the entire lifecycle is run at once
	"""

	import numpy as np
	import pandas as pd

	import opentisim

	# basic inputs
	startyear = 2020
	lifecycle = 10
	years = list(range(startyear, startyear + lifecycle))

	# define demand scenario
	demand = []
	for year in years:
		if year < 2025:
			demand.append(2_460_000)
		else:
			demand.append(2_460_000)
	scenario_data = {'year': years, 'volume': demand}

	# modify container defaults according to case at hand
	# - specify modal split over calling vessels
	opentisim.containers.container_data['fully_cellular_perc'] = 0
	opentisim.containers.container_data['panamax_perc'] = 0
	opentisim.containers.container_data['panamax_max_perc'] = 0
	opentisim.containers.container_data['post_panamax_I_perc'] = 40
	opentisim.containers.container_data['post_panamax_II_perc'] = 0
	opentisim.containers.container_data['new_panamax_perc'] = 0
	opentisim.containers.container_data['VLCS_perc'] = 30
	opentisim.containers.container_data['ULCS_perc'] = 30

	# instantiate commodity object (add scenario_data) and add commodity object to 'demand' variable
	container = opentisim.containers.Commodity(**opentisim.containers.container_data)
	container.scenario_data = pd.DataFrame(data=scenario_data)

	# demand variable: contains info on cargo (to be added to Terminal.elements)
	demand = [container]

	# set default values
	opentisim.containers.post_panamax_I_data['LOA'] = 300
	opentisim.containers.post_panamax_I_data['draught'] = 13
	opentisim.containers.post_panamax_I_data['beam'] = 40
	opentisim.containers.post_panamax_I_data['mooring_time'] = 2
	opentisim.containers.post_panamax_I_data['call_size'] = 900

	opentisim.containers.VLCS_data['LOA'] = 397
	opentisim.containers.VLCS_data['draught'] = 15.5
	opentisim.containers.VLCS_data['beam'] = 56
	opentisim.containers.VLCS_data['mooring_time'] = 2
	opentisim.containers.VLCS_data['call_size'] = 2250

	opentisim.containers.ULCS_data['LOA'] = 400
	opentisim.containers.ULCS_data['draught'] = 16
	opentisim.containers.ULCS_data['beam'] = 59
	opentisim.containers.ULCS_data['mooring_time'] = 2
	opentisim.containers.ULCS_data['call_size'] = 3150

	# instantiate vessels
	fully_cellular = opentisim.containers.Vessel(**opentisim.containers.fully_cellular_data)
	panamax = opentisim.containers.Vessel(**opentisim.containers.panamax_data)
	panamax_max = opentisim.containers.Vessel(**opentisim.containers.panamax_max_data)
	post_panamax_I = opentisim.containers.Vessel(**opentisim.containers.post_panamax_I_data)
	post_panamax_II = opentisim.containers.Vessel(**opentisim.containers.post_panamax_II_data)
	new_panamax = opentisim.containers.Vessel(**opentisim.containers.new_panamax_data)
	VLCS = opentisim.containers.Vessel(**opentisim.containers.VLCS_data)
	ULCS = opentisim.containers.Vessel(**opentisim.containers.ULCS_data)

	# vessels variable: contains info on vessels (to be added to Terminal.elements)
	vessels = [fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, ULCS, VLCS]

	# set simulation details
	# Quay and crane data
	opentisim.containers.sts_crane_data['hourly_cycles'] = 30
	opentisim.containers.sts_crane_data['lifting_capacity'] = 2
	opentisim.containers.berth_data['max_cranes'] = 4
	opentisim.containers.quay_wall_data['apron_width'] = 82

	# Laden inputs
	opentisim.containers.laden_container_data['peak_factor'] = 1.2
	opentisim.containers.laden_container_data['dwell_time'] = 7.5  # days, PIANC (2014b) p 64 (5 - 10)
	opentisim.containers.laden_container_data['height'] = 4  # TEU
	opentisim.containers.laden_container_data['width'] = 45  # TEU
	opentisim.containers.laden_container_data['length'] = 20  # TEU
	opentisim.containers.laden_container_data['stack_ratio'] = 0.8
	opentisim.containers.laden_container_data[
		'stack_occupancy'] = 0.7  # acceptable occupancy rate (0.65 to 0.70), Quist and Wijdeven (2014), p 49

	# Reefer inputs
	opentisim.containers.reefer_container_data['peak_factor'] = 1.2
	opentisim.containers.reefer_container_data['dwell_time'] = 6.5  # days, PIANC (2014b) p 64 (5 - 10)
	opentisim.containers.reefer_container_data['width'] = 4  # TEU
	opentisim.containers.reefer_container_data['height'] = 22  # TEU
	opentisim.containers.reefer_container_data['length'] = 4  # TEU
	opentisim.containers.reefer_container_data['stack_ratio'] = 0.8
	opentisim.containers.reefer_container_data[
		'stack_occupancy'] = 0.7  # acceptable occupancy rate (0.65 to 0.70), Quist and Wijdeven (2014), p 49

	# Empties inputs
	opentisim.containers.empty_container_data['peak_factor'] = 1.2
	opentisim.containers.empty_container_data['dwell_time'] = 11  # days, PIANC (2014b) p 64 (5 - 10)
	opentisim.containers.empty_container_data['width'] = 6  # TEU
	opentisim.containers.empty_container_data['height'] = 35  # TEU
	opentisim.containers.empty_container_data['length'] = 24  # TEU
	opentisim.containers.empty_container_data['stack_ratio'] = 1
	opentisim.containers.empty_container_data[
		'stack_occupancy'] = 0.8  # acceptable occupancy rate (0.65 to 0.70), Quist and Wijdeven (2014), p 49

	# OOGs inputs
	opentisim.containers.oog_container_data['peak_factor'] = 1.2
	opentisim.containers.oog_container_data['dwell_time'] = 7  # days, PIANC (2014b) p 64 (5 - 10)
	opentisim.containers.oog_container_data['width'] = 1  # TEU
	opentisim.containers.oog_container_data['height'] = 10  # TEU
	opentisim.containers.oog_container_data['length'] = 10  # TEU
	opentisim.containers.oog_container_data['stack_ratio'] = 1
	opentisim.containers.oog_container_data[
		'stack_occupancy'] = 0.8  # acceptable occupancy rate (0.65 to 0.70), Quist and Wijdeven (2014), p 49
	# define terminal
	Terminal = opentisim.containers.System(
		terminal_name='Terminal 01',  # terminal name
		startyear=startyear,  # startyear
		lifecycle=lifecycle,  # number of simulation years
		elements=demand + vessels,  # terminal elements at T=0
		operational_hours=8592,  # operational hours (example Wijnand: 5840)
		debug=True,  # toggle: intermediate print statements
		crane_type_defaults=opentisim.containers.sts_crane_data,  # specify defaults: crane type to use
		kendall='E2/E2/n',
		allowable_waiting_service_time_ratio_berth=.1,
		import_perc=0.15, export_perc=0.16, transhipment_ratio=0.69,
		teu_factor=1.6, peak_factor=1.2,
		laden_perc=0.70, reefer_perc=0.10, empty_perc=0.19, oog_perc=0.01,
		laden_teu_factor=1.6, reefer_teu_factor=1.75, empty_teu_factor=1.55, oog_teu_factor=1.55,
		stack_equipment='sc',  # specify defaults: stack equipment to use
		laden_stack='sc')  # specify defaults: crane type to use

	# run simulation
	Terminal.modelframe = list(range(startyear, startyear + lifecycle))
	Terminal.revenues = []
	Terminal.demurrage = []
	# run simulation
	Terminal.simulate()

	# inspect results
	quay = opentisim.core.find_elements(Terminal, opentisim.containers.Quay_wall)

	assert len(opentisim.core.find_elements(Terminal, opentisim.containers.Quay_wall)) == 4
	assert np.sum([element.length for element in
				   opentisim.core.find_elements(Terminal, opentisim.containers.Quay_wall)]) == 1579.6646348823174
	assert np.mean([element.retaining_height for element in
					opentisim.core.find_elements(Terminal, opentisim.containers.Quay_wall)]) == 43.0
	assert np.mean(np.sum([element.length for element in
						   opentisim.core.find_elements(Terminal, opentisim.containers.Quay_wall)])) * quay[
			   0].apron_width == 129532.50006035002
	assert len(opentisim.core.find_elements(Terminal, opentisim.containers.Cyclic_Unloader)) == 14