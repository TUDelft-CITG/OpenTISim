"""Tests for `opentisim` package."""

def test_liquidbulk_02():
	"""Test to see if for a given demand scenario and vessel mix the expected number of
	terminal elements are suggested
	"""

	import pandas as pd
	import opentisim

	# basic inputs
	startyear = 2019
	lifecycle = 10
	years = list(range(startyear, startyear + lifecycle))

	# define demand scenario
	demand = []
	for year in years:
		if year < 2024:
			demand.append(1_000_000)
		else:
			demand.append(2_000_000)
	scenario_data = {'year': years, 'volume': demand}

	# no historic data
	opentisim.liquidbulk.commodity_lhydrogen_data['historic_data'] = []

	# instantiate demand
	lhydrogen = opentisim.liquidbulk.Commodity(**opentisim.liquidbulk.commodity_lhydrogen_data)
	lhydrogen.scenario_data = pd.DataFrame(data=scenario_data)

	# instantiate vessels
	Smallhydrogen = opentisim.liquidbulk.Vessel(**opentisim.liquidbulk.smallhydrogen_data)
	Largehydrogen = opentisim.liquidbulk.Vessel(**opentisim.liquidbulk.largehydrogen_data)
	Smallammonia = opentisim.liquidbulk.Vessel(**opentisim.liquidbulk.smallammonia_data)
	Largeammonia = opentisim.liquidbulk.Vessel(**opentisim.liquidbulk.largeammonia_data)
	Handysize = opentisim.liquidbulk.Vessel(**opentisim.liquidbulk.handysize_data)
	Panamax = opentisim.liquidbulk.Vessel(**opentisim.liquidbulk.panamax_data)
	VLCC = opentisim.liquidbulk.Vessel(**opentisim.liquidbulk.vlcc_data)

	vessels = [Smallhydrogen, Largehydrogen, Smallammonia, Largeammonia, Handysize, Panamax, VLCC]

	# define terminal
	Terminal = opentisim.liquidbulk.System(
		startyear=startyear,
		lifecycle=lifecycle,
		elements=[lhydrogen] + vessels,
		operational_hours=16 * 365,
		terminal_supply_chain={'berth_jetty', 'pipeline_jetty_-_terminal', 'storage', 'mch_2_h2_retrieval',
							   'pipeline_terminal_-_hinterland'},
		debug=True,
		commodity_type_defaults=opentisim.liquidbulk.commodity_ammonia_data,
		storage_type_defaults=opentisim.liquidbulk.storage_nh3_data,
		h2retrieval_type_defaults=opentisim.liquidbulk.h2retrieval_nh3_data)

	# run simulation
	Terminal.simulate()

	# we expect a total of 22 elements in Terminal.elements
	assert len(Terminal.elements) == 22
