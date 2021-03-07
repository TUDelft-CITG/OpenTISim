
# coding: utf-8

# In[ ]:


# coding: utf-8

# In[ ]:


"""Tests for `opentisim` package."""

def test_liquidbulk_07_Berth_Jetty_Pipe_Plant():
	"""Test to see if for a given demand scenario and vessel mix the expected number of
	terminal elements are suggested if only a Berth and Jetty are build, check also the berth occupancy, waiting factor, 
	    throughput and costs - in this testcase the lifecycle is run in year-by-year stepping
	"""
	import pandas as pd
	import opentisim
	#from opentisim.liquidbulk.hydrogen_defaults import *
	#from opentisim.liquidbulk.hydrogen_objects import *
    
	# basic inputs
	startyear = 2020
	lifecycle = 10
	years = list(range(startyear, startyear + lifecycle))
	#Berth = opentisim.liquidbulk.Berth(**opentisim.liquidbulk.berth_data)
	#Jetty = opentisim.liquidbulk.Jetty(**opentisim.liquidbulk.jetty_data)

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
		lifecycle=1,
		elements=[lhydrogen] + vessels,
		operational_hours=16 * 365,
		terminal_supply_chain={'berth_jetty','pipeline_jetty_-_terminal','mch_2_h2_retrieval'},
                           #'pipeline_terminal_-_hinterland'},
		debug=False,
		commodity_type_defaults=opentisim.liquidbulk.commodity_lhydrogen_data,
		storage_type_defaults=opentisim.liquidbulk.storage_lh2_data,
		kendall='E2/E2/n',
		allowable_waiting_service_time_ratio_berth=0.3,
		h2retrieval_type_defaults=opentisim.liquidbulk.h2retrieval_lh2_data)

	# run simulation
	for year in years:
		Terminal.startyear = year
		Terminal.simulate()
        

	#Assert number of elements 
	assert len(Terminal.elements) == 19
	assert len(opentisim.core.find_elements(Terminal, opentisim.liquidbulk.H2retrieval)) == 5

	#For different years check various things

	years = [2023, 2027]
	for index, year in enumerate(years): 
		plants = 0
		#assert the number of jetties online and berths online 
		for element in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.H2retrieval):
			if year >= element.year_online:
				plants += 1 

		#assert the throughput and demand

		Jetty_cap_planned = 0
		Jetty_cap = 0
		for element in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Jetty):
			Jetty_cap_planned += ((opentisim.liquidbulk.smallhydrogen_data["pump_capacity"]                                     			+opentisim.liquidbulk.largehydrogen_data["pump_capacity"] + opentisim.liquidbulk.smallammonia_data["pump_capacity"] 			+opentisim.liquidbulk.largeammonia_data["pump_capacity"] + opentisim.liquidbulk.handysize_data["pump_capacity"] +   			opentisim.liquidbulk.panamax_data["pump_capacity"] + opentisim.liquidbulk.vlcc_data["pump_capacity"]) / 7 *         			Terminal.operational_hours)
            
			if year >= element.year_online:
				Jetty_cap += ((opentisim.liquidbulk.smallhydrogen_data["pump_capacity"] +                                   				opentisim.liquidbulk.largehydrogen_data["pump_capacity"] +                                                      				opentisim.liquidbulk.smallammonia_data["pump_capacity"] +                                                   				opentisim.liquidbulk.largeammonia_data["pump_capacity"] + opentisim.liquidbulk.handysize_data["pump_capacity"]  				+ opentisim.liquidbulk.panamax_data["pump_capacity"] + opentisim.liquidbulk.vlcc_data["pump_capacity"]) / 7 *   				Terminal.operational_hours)
                
		Jetty_cap = round(Jetty_cap)  
        
		pipelineJ_capacity_planned = 0
		pipelineJ_capacity_online = 0
		list_of_elements = opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Pipeline_Jetty)
		if list_of_elements != []:
			for element in list_of_elements:
				pipelineJ_capacity_planned += element.capacity * Terminal.operational_hours
				if year >= element.year_online:
					pipelineJ_capacity_online += element.capacity * Terminal.operational_hours
        
		pipelineJ_capacity_online = round(pipelineJ_capacity_online)
        
		Demand = []
		Commodity = opentisim.liquidbulk.Commodity(**opentisim.liquidbulk.commodity_lhydrogen_data)
		for commodity in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Commodity):
			try:
				Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
			except:
            #print('problem occurs at {}'.format(year))
				pass
            
            
        # Find plant capacity
		h2retrieval_capacity_planned = 0
		h2retrieval_capacity_online = 0
		list_of_elements = opentisim.core.find_elements(Terminal, opentisim.liquidbulk.H2retrieval)
		if list_of_elements != []:
			for element in list_of_elements:
				h2retrieval_capacity_planned += element.capacity * Terminal.operational_hours
				if year >= element.year_online:
					h2retrieval_capacity_online += element.capacity * Terminal.operational_hours


		h2retrieval_capacity_planned = round(h2retrieval_capacity_planned)
		h2retrieval_capacity_online = round(h2retrieval_capacity_online)

		plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online= Terminal.calculate_h2retrieval_occupancy( year, opentisim.liquidbulk.h2retrieval_lh2_data) 
		plant_occupancy_online = round(plant_occupancy_online,2)
		throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage,  		throughput_planned_h2retrieval, throughput_planned_pipeh = Terminal.throughput_elements(year)

		#assert the costs 

		if index == 0: 
			assert plants == 3
			assert Jetty_cap == 34622857
			assert pipelineJ_capacity_online == 23360000
			assert Demand == 2000000
			assert h2retrieval_capacity_online == 2400240
			assert throughput_online == 2000000
			assert plant_occupancy_online == 0.83
		else:
			assert plants == 5
			assert Jetty_cap == 69245714
			assert pipelineJ_capacity_online == 46720000 
			assert Demand == 4000000
			assert h2retrieval_capacity_online == 4000400
			assert throughput_online == 4000000
			assert plant_occupancy_online == 1.0

