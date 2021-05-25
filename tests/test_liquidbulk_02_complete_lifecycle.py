"""Tests for `opentisim` package."""

def test_liquidbulk_02_complete_lifecycle():
	"""Test to see if for a given demand scenario and vessel mix the expected number of
	terminal elements are suggested - in this testcase the entire lifecycle is run at once
	"""

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
			demand.append(2_000_000)
		else:
			demand.append(4_000_000)
	scenario_data = {'year': years, 'volume': demand}

	# instantiate a commodity objects
	opentisim.liquidbulk.commodity_lhydrogen_data['smallhydrogen_perc'] = 50
	opentisim.liquidbulk.commodity_lhydrogen_data['largehydrogen_perc'] = 50

	# instantiate a commodity objects
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
		terminal_supply_chain={'berth_jetty', 'pipeline_jetty_-_terminal', 'storage', 'h2_retrieval'},
							   #'pipeline_terminal_-_hinterland'},
		debug=True,
		commodity_type_defaults=opentisim.liquidbulk.commodity_lhydrogen_data,
		storage_type_defaults=opentisim.liquidbulk.storage_lh2_data,
		kendall='E2/E2/n',
		allowable_waiting_service_time_ratio_berth=0.3,
		h2retrieval_type_defaults=opentisim.liquidbulk.h2retrieval_lh2_data,
		allowable_dwelltime=14 / 365)

	Terminal.modelframe = list(range(startyear, startyear + lifecycle))
	Terminal.revenues = []
	Terminal.demurrage = []
	# run simulation
	Terminal.simulate()

	# we expect a total of 33 elements in Terminal.elements
	assert len(Terminal.elements) == 67
