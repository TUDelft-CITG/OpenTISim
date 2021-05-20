
# coding: utf-8

# In[ ]:



"""Tests for `opentisim` package."""

def test_liquidbulk_05_Berth_Jetty_Pipe():
	"""Test to see if for a given demand scenario and vessel mix the expected number of
	terminal elements are suggested if a Berth, Jetty and pipeline from the jetty to the terminal are build, check also the 	berth occupancy, waiting factor, throughput and costs - in this testcase the lifecycle is run in year-by-year stepping. 	Checks have been done for years 2023 and 2027.
	"""
	import pandas as pd
	import opentisim
	import numpy as np
    
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
	opentisim.liquidbulk.smallhydrogen_data['call_size'] = 10_345  #[Abrahamse 2021]
	opentisim.liquidbulk.smallhydrogen_data['LOA'] = 200 #[Lanphen 2019]
	opentisim.liquidbulk.smallhydrogen_data['all_turn_time'] = 20 #[Lanphen 2019]
	opentisim.liquidbulk.smallhydrogen_data['pump_capacity'] = 1_034.5 #[Abrahamse 2021]
	opentisim.liquidbulk.smallhydrogen_data['mooring_time'] = 3 #[Lanphen 2019]

	opentisim.liquidbulk.largehydrogen_data['call_size'] = 18_886 #[Abrahamse 2021]
	opentisim.liquidbulk.largehydrogen_data['LOA'] = 300  #[Lanphen 2019]
	opentisim.liquidbulk.largehydrogen_data['all_turn_time'] = 30 #[Lanphen 2019]
	opentisim.liquidbulk.largehydrogen_data['pump_capacity'] =  1888.6 #[Abrahamse 2021]
	opentisim.liquidbulk.largehydrogen_data['mooring_time'] = 3 #[Lanphen 2019]
    
    
	# jetty data
	opentisim.liquidbulk.jetty_data['delivery_time'] = 1 #Dr. ir. De Gijt and Ir. Quist, personal communication,[Lanphen2019]
	opentisim.liquidbulk.jetty_data['lifespan'] = 30 #Dr. ir. De Gijt and Ir. Quist, personal communication,[Lanphen2019]
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

	# pipeline data 
	opentisim.liquidbulk.jetty_pipeline_data['length'] = 600 #Gasunie & MTBS database [Stephanie2019]
	opentisim.liquidbulk.jetty_pipeline_data['delivery_time'] = 1  #Gasunie & MTBS database [Stephanie2019]
	opentisim.liquidbulk.jetty_pipeline_data['lifespan'] = 26  #Gasunie & MTBS database [Stephanie2019]
	opentisim.liquidbulk.jetty_pipeline_data['unit_rate_factor'] = 13_000  #Gasunie & MTBS database [Stephanie2019]
	opentisim.liquidbulk.jetty_pipeline_data['mobilisation'] = 30_000      #Gasunie & MTBS database [Stephanie2019]
	opentisim.liquidbulk.jetty_pipeline_data['maintenance_perc'] = 0.01 #[Stephanie2019]
	opentisim.liquidbulk.jetty_pipeline_data['insurance_perc'] = 0.01   #[Stephanie2019]
	opentisim.liquidbulk.jetty_pipeline_data['consumption_coefficient'] = 100  #Gasunie & MTBS database [Stephanie2019]
	opentisim.liquidbulk.jetty_pipeline_data['crew'] = 1     #Gasunie & MTBS database [Stephanie2019]
	opentisim.liquidbulk.jetty_pipeline_data['utilisation'] = 0.80  #Gasunie & MTBS database [Stephanie2019]
    
    
	# define terminal
	Terminal = opentisim.liquidbulk.System(
		startyear=startyear, #startyear of the model
		lifecycle=1, #lifecycle of the model looped through the years 
		elements=[lhydrogen] + vessels, #terminal elements at T = 0 
		operational_hours=16 * 365, #Example Wijnand (5840) 
		terminal_supply_chain={'berth_jetty','pipeline_jetty_-_terminal'}, #Choose what elements are on the terminal, other 		elements could be: 'storage', 'mch_2_h2_retrieval','pipeline_terminal_-_hinterland'},
		debug=False, #toggle: intermediate print statements
		commodity_type_defaults=opentisim.liquidbulk.commodity_lhydrogen_data,  # specify defaults: commodity
		storage_type_defaults=opentisim.liquidbulk.storage_lh2_data, # specify defaults: commodity storage
		kendall='E2/E2/n', #Queing theory (common users of the liquid bulk terminal a realistic queue is M/E2/n and for a       		dedicated shipping line is E2/E2/n (Monfort et al., 2011))
		allowable_waiting_service_time_ratio_berth=0.3,
		h2retrieval_type_defaults=opentisim.liquidbulk.h2retrieval_lh2_data, # specify defaults: commodity h2 retrieval
		allowable_berth_occupancy=0.5, # 0.5 Reasonable for liquid bulk (Monfort et al., 2011)
		allowable_dwelltime=14 / 365, 
		h2retrieval_trigger=1) 

	Terminal.modelframe = list(range(startyear, startyear + lifecycle))
	Terminal.revenues = []
	Terminal.demurrage = []
	# run simulation
	for year in years:
		Terminal.startyear = year
		Terminal.simulate()
        
	#Assert number of elements 
	assert len(Terminal.elements) == 14
	assert len(opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Pipeline_Jetty)) == 2

	#For different years check various things

	years = [2023, 2027]
	for index, year in enumerate(years): 

		jetty_pipelines = 0 
		#assert the number of jetties online and berths online 
		for element in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Pipeline_Jetty):
			if year >= element.year_online:
				jetty_pipelines += 1 

		#assert the throughput and demand
		Jetty_cap_planned = 0
		Jetty_cap = 0
        
		for commodity in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Commodity):
			if commodity.type == 'MCH': 
				pump1 = opentisim.liquidbulk.handysize_data["pump_capacity"]
				pump2 = opentisim.liquidbulk.panamax_data["pump_capacity"]
				pump3 = opentisim.liquidbulk.vlcc_data["pump_capacity"]
				pumpall = np.array([pump1, pump2, pump3])
				pumpall = pumpall[np.nonzero(pumpall)]
			elif commodity.type == 'Liquid hydrogen':
				pump1 = opentisim.liquidbulk.smallhydrogen_data["pump_capacity"]
				pump2 = opentisim.liquidbulk.largehydrogen_data["pump_capacity"]
				pump3 = 0
				pumpall = np.array([pump1, pump2, pump3])
				pumpall = pumpall[np.nonzero(pumpall)]
			else:
				pump1 = sopentisim.liquidbulk.mallammonia_data["pump_capacity"] 
				pump2 = opentisim.liquidbulk.largeammonia_data["pump_capacity"]
				pump3 = 0
				pumpall = np.array([pump1, pump2, pump33])
				pumpall = pumpall[np.nonzero(pumpall)]

		for element in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Jetty):
			Jetty_cap_planned += (sum(pumpall) / len(pumpall) * Terminal.operational_hours)
			if year >= element.year_online:
				Jetty_cap += (sum(pumpall) / len(pumpall) * Terminal.operational_hours)
		Jetty_cap = round(Jetty_cap) 
                
		# Find pipeline jetty capacity
		pipelineJ_capacity_planned = 0
		pipelineJ_capacity_online = 0
		list_of_elements = opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Pipeline_Jetty)
		if list_of_elements != []:
			for element in list_of_elements:
				pipelineJ_capacity_planned += (sum(pumpall) / len(pumpall) * Terminal.operational_hours) #element.capacity *    				self.operational_hours
				if year >= element.year_online:
					pipelineJ_capacity_online += (sum(pumpall) / len(pumpall) * Terminal.operational_hours)#element.capa
		pipelineJ_capacity_online = round(pipelineJ_capacity_online)                     
     
		Demand = []
		Commodity = opentisim.liquidbulk.Commodity(**opentisim.liquidbulk.commodity_lhydrogen_data)
		for commodity in opentisim.core.find_elements(Terminal, opentisim.liquidbulk.Commodity):
			try:
				Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
			except:
            #print('problem occurs at {}'.format(year))
				pass
            
		throughput_online, throughput_terminal_in ,throughput_online_jetty_in, throughput_online_stor_in,                   		throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,                  		throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in, Demand_jetty_in=   		Terminal.throughput_elements(year)

		#assert the costs 

		if index == 0: 
			assert jetty_pipelines == 1
			assert Jetty_cap == 8535452.0 
			assert pipelineJ_capacity_online == 8535452.0
			assert Demand == 2000000
			assert throughput_online == 2000000
		else:
			assert jetty_pipelines == 2
			assert Jetty_cap == 17070904.0
			assert pipelineJ_capacity_online == 17070904.0
			assert Demand == 4000000
			assert throughput_online == 4000000

