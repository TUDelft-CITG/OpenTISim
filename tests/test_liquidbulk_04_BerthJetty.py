
# coding: utf-8

# In[ ]:


"""Tests for `opentisim` package."""

def test_liquidbulk_04_Berth_Jetty():
	"""Test to see if for a given demand scenario and vessel mix the expected number of
	terminal elements are suggested if only a Berth and Jetty are build, check also the berth occupancy, waiting factor, 
	    throughput and costs - in this testcase the lifecycle is run in year-by-year stepping. Checks have been done for years  	2023 and 2027.
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

	# set simulation details
    
	# commodity data (liquid hydrogen)
	opentisim.liquidbulk.commodity_lhydrogen_data['handling_fee'] = 490 

	# vessel data (liquid hydrogen)
	opentisim.liquidbulk.smallhydrogen_data['call_size'] = 10_000 
	opentisim.liquidbulk.smallhydrogen_data['LOA'] = 200 
	opentisim.liquidbulk.smallhydrogen_data['all_turn_time'] = 20 
	opentisim.liquidbulk.smallhydrogen_data['pump_capacity'] = 1_000
	opentisim.liquidbulk.smallhydrogen_data['mooring_time'] = 3 
	opentisim.liquidbulk.smallhydrogen_data['demurrage_rate'] = 600    
    
	opentisim.liquidbulk.largehydrogen_data['call_size'] = 30_000 
	opentisim.liquidbulk.largehydrogen_data['LOA'] = 300  
	opentisim.liquidbulk.largehydrogen_data['all_turn_time'] = 30 
	opentisim.liquidbulk.largehydrogen_data['pump_capacity'] = 3_000
	opentisim.liquidbulk.largehydrogen_data['mooring_time'] = 3 
	opentisim.liquidbulk.largehydrogen_data['demurrage_rate'] = 700 
    
	# jetty data
	opentisim.liquidbulk.jetty_data['delivery_time'] = 2 #Dr. ir. De Gijt and Ir. Quist, personal communication,[Lanphen2019]
	opentisim.liquidbulk.jetty_data['lifespan'] = 50 #Dr. ir. De Gijt and Ir. Quist, personal communication,[Lanphen2019]
	opentisim.liquidbulk.jetty_data['mobilisation_min'] = 1_000_000 #Dr. ir. De Gijt and Ir. Quist, personal communication,     	[Lanphen2019]
	opentisim.liquidbulk.jetty_data['mobilisation_perc'] = 0.02 #[Lanphen2019]
	opentisim.liquidbulk.jetty_data['maintenance_perc'] = 0.01 #1% of CAPEX [Lanphen2019]
	opentisim.liquidbulk.jetty_data['insurance_perc'] = 0.01 #1% of CAPEX [Lanphen2019]
	opentisim.liquidbulk.jetty_data['Gijt_constant_jetty'] = 2000 #Dr. ir. De Gijt, personal communication, [Lanphen 2019]
	opentisim.liquidbulk.jetty_data['jettywidth'] = 16 #Dr. ir. De Gijt, personal communication, [Lanphen 2019]
	opentisim.liquidbulk.jetty_data['jettylength'] = 30 #Dr. ir. De Gijt, personal communication, [Lanphen 2019]
	opentisim.liquidbulk.jetty_data['mooring_dolphins'] = 250_000 #Ir. Quist, personal communication, [Lanphen 2019]
	opentisim.liquidbulk.jetty_data['catwalkwidth'] = 5 #Ir. Quist, personal communication, [Lanphen 2019]
	opentisim.liquidbulk.jetty_data['catwalklength'] = 100 #Ir. Quist, personal communication, [Lanphen 2019]
	opentisim.liquidbulk.jetty_data['Catwalk_rate'] = 1000 #Ir. Quist, personal communication, [Lanphen 2019]
    
	# berth data   
	opentisim.liquidbulk.berth_data['delivery_time'] = 1 #Dr. ir. De Gijt and Ir. Quist, personal communication,[Lanphen2019]
      
	# define terminal
	Terminal = opentisim.liquidbulk.System(
		startyear=startyear, #startyear of the model
		lifecycle=1, #lifecycle of the model looped through the years 
		elements=[lhydrogen] + vessels, #terminal elements at T = 0 
		operational_hours=16 * 365, #Example Wijnand (5840) 
		terminal_supply_chain={'berth_jetty'}, #Choose what elements are on the terminal, other elements could be:              		'pipeline_jetty_-_terminal', 'storage', 'mch_2_h2_retrieval','pipeline_terminal_-_hinterland'},
		debug=False, #toggle: intermediate print statements
		commodity_type_defaults=opentisim.liquidbulk.commodity_lhydrogen_data,  # specify defaults: commodity
		storage_type_defaults=opentisim.liquidbulk.storage_lh2_data, # specify defaults: commodity storage
		kendall='E2/E2/n', #Queing theory (common users of the liquid bulk terminal a realistic queue is M/E2/n and for a       		dedicated shipping line is E2/E2/n (Monfort et al., 2011))
		allowable_waiting_service_time_ratio_berth=0.3,
		h2retrieval_type_defaults=opentisim.liquidbulk.h2retrieval_lh2_data, # specify defaults: commodity h2 retrieval
		allowable_berth_occupancy=0.5, # 0.5 Reasonable for liquid bulk (Monfort et al., 2011)
		allowable_dwelltime=14 / 365, 
		h2retrieval_trigger=1) 

	# run simulation
	for year in years:
		Terminal.startyear = year
		Terminal.simulate()
        

	#Assert number of elements 
	assert len(Terminal.elements) == 12
	assert len(opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Berth)) == 2
	assert len(opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Jetty)) == 2

	#For different years check various things

	years = [2023, 2027]
	for index, year in enumerate(years): 
		berths = 0
		jetties = 0 
		#assert the number of jetties online and berths online 
		for element in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Berth):
			if year >= element.year_online:
				berths += 1 

		for element in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Jetty):
			if year >= element.year_online:
				jetties += 1 

		#assert the berth occupancy and the waiting factor 

		smallhydrogen_calls, largehydrogen_calls,smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls,        		vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned,                           		smallammonia_calls_planned,largeammonia_calls_planned,handysize_calls_planned, panamax_calls_planned,                   		vlcc_calls_planned, total_calls_planned, total_vol_planned = Terminal.calculate_vessel_calls(year)

		berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online =              		Terminal.calculate_berth_occupancy(year, smallhydrogen_calls, largehydrogen_calls,                                      		smallammonia_calls,largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls,smallhydrogen_calls_planned,          		largehydrogen_calls_planned, smallammonia_calls_planned,largeammonia_calls_planned, handysize_calls_planned,            		panamax_calls_planned, vlcc_calls_planned)
            
		WF = opentisim.core.occupancy_to_waitingfactor(utilisation=berth_occupancy_planned, nr_of_servers_to_chk=berths,    		kendall=Terminal.kendall)

		berth_occupancy_online = round(berth_occupancy_online,3)
		WF = round(WF,3)

		#assert the throughput and demand

		Jetty_cap_planned = 0
		Jetty_cap = 0
		for element in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Jetty):
			Jetty_cap_planned += ((opentisim.liquidbulk.smallhydrogen_data["pump_capacity"]                                     			+opentisim.liquidbulk.largehydrogen_data["pump_capacity"] + opentisim.liquidbulk.smallammonia_data["pump_capacity"] 			+opentisim.liquidbulk.largeammonia_data["pump_capacity"] + opentisim.liquidbulk.handysize_data["pump_capacity"] +   			opentisim.liquidbulk.panamax_data["pump_capacity"] + opentisim.liquidbulk.vlcc_data["pump_capacity"]) / 7 *         			Terminal.operational_hours)
            
			if year >= element.year_online:
				Jetty_cap += ((opentisim.liquidbulk.smallhydrogen_data["pump_capacity"] +                                   				opentisim.liquidbulk.largehydrogen_data["pump_capacity"] +                                                      				opentisim.liquidbulk.smallammonia_data["pump_capacity"] +                                                   				opentisim.liquidbulk.largeammonia_data["pump_capacity"] + opentisim.liquidbulk.handysize_data["pump_capacity"]  				+ opentisim.liquidbulk.panamax_data["pump_capacity"] + opentisim.liquidbulk.vlcc_data["pump_capacity"]) / 7 *   				Terminal.operational_hours)
                
		Jetty_cap = round(Jetty_cap)  
        
		Demand = []
		Commodity = opentisim.liquidbulk.Commodity(**opentisim.liquidbulk.commodity_lhydrogen_data)
		for commodity in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Commodity):
			try:
				Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
			except:
            #print('problem occurs at {}'.format(year))
				pass
            
		throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage,  		throughput_planned_h2retrieval, throughput_planned_pipeh = Terminal.throughput_elements(year)

		#assert the costs 

		if index == 0: 
			assert berths == 1
			assert jetties == 1
			assert berth_occupancy_online == 0.298
			assert WF == 0.038
			assert Jetty_cap == 34622857 
			assert Demand == 2000000
			assert throughput_online == 2000000
		else:
			assert berths == 2
			assert jetties == 2 
			assert berth_occupancy_online == 0.297
			assert WF == 0.023
			assert Jetty_cap == 69245714
			assert Demand == 4000000
			assert throughput_online == 4000000

