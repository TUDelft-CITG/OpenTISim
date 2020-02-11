"""Main generic object classes:

- 1. Quay_wall
- 2. Berth
- 3. Cyclic_Unloader
    - STS crane
- 4. Horizontal transport
    - Tractor trailer
- 5. Commodity
    - TEU
- 6. Containers
    - Laden
    - Reefer
    - Empty
    - OOG
- 7. Laden and reefer stack
    - RTG stack
    - RMG stack
    - SC stack
    - RS stack
- 8. Stack equipment
    - RTG
    - RMG
    - SC
    - RS
- 9. Empty stack
- 10. OOG stack
- 11. Gates
- 12. Empty handler
- 13. Vessel
- 14. Labour
- 15. Energy

#todo add sources here
"""

# package(s) for data handling
import pandas as pd

# *** Default inputs: Quay class ***

quay_wall_data = {"name": 'Quay_01',
                  "ownership": 'Port authority',
                  "delivery_time": 2,
                  "lifespan": 50,
                  "mobilisation_min": 2_500_000,
                  "mobilisation_perc": 0.02,
                  "maintenance_perc": 0.01,
                  "insurance_perc": 0.01,
                  "freeboard": 4,
                  "Gijt_constant_2": 2800,
                  "Gijt_constant": 757.20,
                  "Gijt_coefficient": 1.2878,
                  "max_sinkage": 0.5,
                  "wave_motion": 0.5,
                  "safety_margin": 0.5,
                  "apron_width": 65.5,
                  "apron_pavement": 125} # all values from Ijzermans, 2019, P 91


# *** Default inputs: Berth class ***

berth_data = {"name": 'Berth_01',
              "crane_type": 'Mobile cranes',
              "delivery_time": 1,
              "max_cranes": 4}  #STS cranes

# *** Default inputs: CyclicUnloader class ***

gantry_crane_data = {"name": 'Gantry_crane_01',
                     "ownership": 'Terminal operator',
                     "delivery_time": 1,
                     "lifespan": 40,
                     "unit_rate": 9_750_000,
                     "mobilisation_perc": 0.15,
                     "maintenance_perc": 0.02,
                     "consumption": 561,
                     "insurance_perc": 0.01,
                     "crew": 3,
                     "crane_type": 'Gantry crane',
                     "lifting_capacity": 50,
                     "hourly_cycles": 50,
                     "eff_fact": 0.50}  # all values from Ijzermans, 2019, P 100

harbour_crane_data = {"name": 'Harbour_crane_01',
                      "ownership": 'Terminal operator',
                      "delivery_time": 1,
                      "lifespan": 40,
                      "unit_rate": 7_880_000,
                      "mobilisation_perc": 0.15,
                      "maintenance_perc": 0.02,
                      "consumption": 210,
                      "insurance_perc": 0.01,
                      "crew": 3,
                      "crane_type": 'Harbour crane',
                      "lifting_capacity": 25,
                      "hourly_cycles": 40,
                      "eff_fact": 0.40}  # all values from Ijzermans, 2019, P 100

mobile_crane_data = {"name": 'Mobile_crane_01',
                     "ownership": 'Terminal operator',
                     "delivery_time": 1,
                     "lifespan": 40,
                     "unit_rate": 3_325_000,
                     "mobilisation_perc": 0.15,
                     "maintenance_perc": 0.02,
                     "consumption": 485,
                     "insurance_perc": 0.01,
                     "crew": 3,
                     "crane_type": 'Mobile crane',
                     "lifting_capacity": 30,
                     "hourly_cycles": 25,
                     "eff_fact": 0.35}  # all values from Ijzermans, 2019, P 100

sts_crane_data = {"name": 'STS_crane',
                  "ownership": 'Terminal operator',
                  "delivery_time": 1,
                  "lifespan": 40,
                  "unit_rate": 10_000_000,
                  "mobilisation_perc": 0.15,
                  "maintenance_perc": 0.02,
                  "consumption": 8,  # Peter Beamish
                  "insurance_perc": 0.01,
                  "crew": 5.5,  # todo is dit per shift?  #1.5 crane driver, 2 quay staff, 2 twistlock handler (per shift)
                  "crane_type": 'STS crane',
                  "lifting_capacity": 2.13,  # weighted average of TEU per lift
                  "hourly_cycles": 25,  # PIANC wg135
                  "eff_fact": 1}


# Default inputs: Horizontal Transport class ***

tractor_trailer_data = {"name": 'Tractor-trailer',
                        "type": 'tractor_trailer',
                        "ownership": 'Terminal operator',
                        "delivery_time": 0,
                        "lifespan": 10,
                        "mobilisation": 1_000,
                        "unit_rate": 85_000,
                        "maintenance_perc": 0.10,
                        "insurance_perc": 0.01,
                        "crew": 1,
                        "salary": 30_000,  # dummy
                        "utilisation": 0.80,
                        "fuel_consumption": 2,  # liter per box move
                        "productivity": 1,
                        "required": 5,
                        "non_essential_moves": 1.2}  # todo input value for tractor productivity

# *** Default inputs: Container class

laden_container_data = {"name": 'Laden container',
                        "type": 'laden_container',
                        "teu_factor": 1.55,
                        "dwell_time": 4,
                        "peak_factor": 1.2,
                        "stack_occupancy": 0.8}

reefer_container_data = {"name": 'Empty container',
                         "type": 'empty_container',
                         "teu_factor": 1.75,
                         "dwell_time": 4,
                         "peak_factor": 1.2,
                         "stack_occupancy": 0.8}

empty_container_data = {"name": 'Empty container',
                        "type": 'empty_container',
                        "teu_factor": 1.55,
                        "dwell_time": 10,
                        "peak_factor": 1.2,
                        "stack_occupancy": 0.7}

oog_container_data = {"name": 'OOG container',
                      "type": 'oog_container',
                      "teu_factor": 1.55,
                      "dwell_time": 5,
                      "peak_factor": 1.2,
                      "stack_occupancy": 0.9}

# *** Default inputs: Laden_Stack class

rtg_stack_data = {"name": 'RTG Stack',
                  "ownership": 'Terminal operator',
                  "delivery_time": 1,
                  "lifespan": 40,
                  "mobilisation": 25_000,
                  "maintenance_perc": 0.1,
                  "width": 6,  # TEU
                  "height": 5,  # TEU
                  "length": 30,  # TEU
                  "capacity": 900,  # TEU
                  "gross_tgs": 18,
                  "area_factor": 2.04,  # Based on grasshopper layout
                  "pavement": 200,  # DUMMY
                  "drainage": 50,  # DUMMY
                  "household": 0.1,  # moves
                  "digout_margin": 1.2,  # percentage
                  "reefer_factor": 2.33,  # RHDHV
                  "consumption": 4,  # kWh per active reefer
                  "reefer_rack": 3500,
                  "reefers_present": 0.5}  # per reefer spot


rmg_stack_data = {"name": 'RMG Stack',
                  "ownership": 'Terminal operator',
                  "delivery_time": 1,
                  "lifespan": 40,
                  "mobilisation": 50_000,
                  "maintenance_perc": 0.1,
                  "width": 6,  # TEU
                  "height": 5,  # TEU
                  "length": 40,  # TEU
                  "capacity": 1200,  # TEU
                  "gross_tgs": 18.67,
                  "area_factor": 2.79,  # Based on grasshopper layout
                  "pavement": 200,  # DUMMY
                  "drainage": 50,  # DUMMY
                  "household": 0.1,  # moves
                  "digout_margin": 1.2,  # percentage
                  "reefer_factor": 2.33,  # RHDHV
                  "consumption": 4,  # kWh per active reefer
                  "reefer_rack": 3500,
                  "reefers_present": 0.5}  # per reefer spot


sc_stack_data = {"name": 'SC Stack',
                 "ownership": 'Terminal operator',
                 "delivery_time": 1,
                 "lifespan": 40,
                 "mobilisation": 50_000,
                 "maintenance_perc": 0.1,
                 "width": 48,  # TEU
                 "height": 4,  # TEU
                 "length": 20,  # TEU
                 "capacity": 3840,  # TEU
                 "gross_tgs": 26.46,
                 "area_factor": 1.45,  # Based on grasshopper layout
                 "pavement": 200,  # DUMMY
                 "drainage": 50,  # DUMMY
                 "household": 0.1,  # moves
                 "digout_margin": 1.2,  # percentage
                 "reefer_factor": 2.33,  # RHDHV
                 "consumption": 4,  # kWh per active reefer
                 "reefer_rack": 3500,
                 "reefers_present": 0.5}  # per reefer spot

rs_stack_data = {"name": 'RS Stack',
                 "ownership": 'Terminal operator',
                 "delivery_time": 1,
                 "lifespan": 40,
                 "mobilisation": 10_000,
                 "maintenance_perc": 0.1,
                 "width": 4,  # TEU
                 "height": 4,  # TEU
                 "length": 20,  # TEU
                 "capacity": 320,  # TEU
                 "gross_tgs": 18,
                 "area_factor": 3.23,  # Based on grasshopper layout
                 "pavement": 200,  # DUMMY
                 "drainage": 50,  # DUMMY
                 "household": 0.1,  # moves
                 "digout_margin": 1.2,  # percentage
                 "reefer_factor": 2.33,  # RHDHV
                 "consumption": 4,  # kWh per active reefer
                 "reefer_rack": 3500,
                 "reefers_present": 0.5}  # per reefer spot


# #*** Default inputs: Reefer data
# reefer_rack_data = {"reefer_factor":2.33,  # RHDHV
#                  "consumption":4,  # kWh per active reefer
#                  "reefer_rack": 3500}  # per reefer spot



# *** Default inputs: Other_Stack class

empty_stack_data = {"name": 'Empty Stack',
                    "ownership": 'Terminal operator',
                    "delivery_time": 1,
                    "lifespan": 40,
                    "mobilisation": 25_000,
                    "maintenance_perc": 0.1,
                    "width": 8,  # TEU
                    "height": 6,  # TEU
                    "length": 10,  # TEU
                    "capacity": 480,  # TEU
                    "gross_tgs": 18,
                    "area_factor": 2.04,  # Based on grasshopper layout
                    "pavement": 200,  # DUMMY
                    "drainage": 50,
                    "household": 1.05,
                    "digout": 1.05}  # DUMMY

oog_stack_data = {"name": 'OOG Stack',
                  "ownership": 'Terminal operator',
                  "delivery_time": 1,
                  "lifespan": 40,
                  "mobilisation": 25_000,
                  "maintenance_perc": 0.1,
                  "width": 10,  # TEU
                  "height": 1,  # TEU
                  "length": 10,  # TEU
                  "capacity": 100,  # TEU
                  "gross_tgs": 64,
                  "area_factor": 1.05,  # Based on grasshopper layout
                  "pavement": 200,  # DUMMY
                  "drainage": 50}  # DUMMY

# *** Default inputs: Stack_Equipment class
#RTG # todo add eRTG

rtg_data = {"name": 'RTG',
            "type": 'rtg',
            "ownership": 'Terminal operator',
            "delivery_time": 0,
            "lifespan": 10,
            "unit_rate": 1_400_000,
            "mobilisation": 5000,
            "maintenance_perc": 0.1,  # dummy
            "insurance_perc": 0,
            "crew": 1,  # dummy
            "salary": 50_000,  # dummy
            "required": 3,
            "fuel_consumption": 1,  # dummy
            "power_consumption": 0
            }

#RMG
rmg_data = {"name": 'RMG',
            "type": 'rmg',
            "ownership": 'Terminal operator',
            "delivery_time": 0,
            "lifespan": 10,
            "unit_rate": 2_500_000,
            "mobilisation": 5000,
            "maintenance_perc": 0.1,  # dummy
            "insurance_perc": 0,
            "crew": 0,  # dummy
            "salary": 50_000,  # dummy
            "required": 1,  # one per stack
            "fuel_consumption": 0,  # dummy
            "power_consumption": 15  # kWh/box move
            }

#Straddle carrier #
sc_data = {"name": 'Straddle carrier',
            "type": 'sc',
            "ownership": 'Terminal operator',
            "delivery_time": 0,
            "lifespan": 10,
            "unit_rate": 2_000_000,  # dummy
            "mobilisation": 5000,
            "maintenance_perc": 0.1,  # dummy
            "insurance_perc": 0,
            "crew": 0,  # dummy
            "salary": 50_000,  # dummy
            "required": 5,
            "fuel_consumption": 0,  # dummy
            "power_consumption": 30
            }

#Reach stacker
rs_data = {"name": 'Reach stacker',
            "type": 'rs',
            "ownership": 'Terminal operator',
            "delivery_time": 0,
            "lifespan": 10,
            "unit_rate": 500_000,
            "mobilisation": 5000,
            "maintenance_perc": 0.1,  # dummy
            "insurance_perc": 0,
            "crew": 2,  # dummy
            "salary": 50_000,  # dummy
            "required": 4,
            "fuel_consumption": 1,  # dummy
            "power_consumption": 0
            }



# *** Default inputs: Gate class ***

gate_data = {"name": 'Gate',
             "type": 'gate',
             "ownership":  "Terminal operator",
             "delivery_time": 1,
             "lifespan": 15,
             "unit_rate": 30_000,
             "mobilisation": 5000,
             "maintenance_perc": 0.02,
             "crew": 2,
             "salary": 30_000,  # dummy
             "canopy_costs": 250,  # USD/m2 dummy
             "area": 288.75,  # PIANC WG135
             "staff_gates": 1,
             "service_gates": 1,
             "design_capacity": 0.98,
             "exit_inspection_time": 2,  # min #dummy
             "entry_inspection_time": 2,  # min #dummy
             "peak_hour": 0.25,  # dummy
             "peak_day": 0.1,  # dummy
             "peak_factor": 1.2,
             "truck_moves": 0.75,
             "operating_days": 6,
             "capacity": 60}

# *** Default inputs: ECH class***

empty_handler_data = {"name": 'Empty Handler',
                      "type": 'empty_handler',
                      "ownership":  "Terminal operator",
                      "delivery_time": 1,
                      "lifespan": 15,
                      "unit_rate": 500_000,
                      "mobilisation": 5000,
                      "maintenance_perc": 0.02,
                      "crew": 1,
                      "salary": 35_000,  # dummy
                      "fuel_consumption": 1.5,
                      "required": 5}


# *** Default inputs: Commodity class ***

container_data = {"name": 'Laden',
                "handling_fee": 150,
                "handysize_perc": 0,
                "handymax_perc": 0,
                "panamax_perc": 100,
                "historic_data": pd.DataFrame(data={'year': [2014, 2015, 2016, 2017, 2018],
                                                    'volume': [1_000_000, 1_100_000, 1_250_000, 1_400_000, 1_500_000]})}


# *** Default inputs: Vessel class ***

feeder_800_data = {"name": 'Feeder_800_1',  # https://products.damen.com/en/ranges/container-feeder
                   "type": 'Feeder_800',
                   "call_size": 803,  # TEU
                   "tonnage": 0,  # todo: verify
                   "LOA": 140.64,  # m
                   "beam": 21.8,  # m
                   "draft": 7.33,  # m
                   # "speedmax": 17,  # kts
                   "max_cranes": 1,  # todo: verify
                   "all_turn_time": 31,  # todo: verify
                   "mooring_time": 6,  # todo: verify
                   "demurrage_rate": 730}  # todo: verify

feeder_900_data = {"name": 'Feeder_900_1',  # https://products.damen.com/en/ranges/container-feeder
                   "type": 'Feeder_900',
                   "call_size": 888,  # TEU
                   "tonnage": 0,  # todo: verify
                   "LOA": 150.17,  # m
                   "beam": 21.8,  # m
                   "draft": 7.2,  # m
                   # "speedmax": 17,  # kts
                   "max_cranes": 1,  # todo: verify
                   "all_turn_time": 31,  # todo: verify
                   "mooring_time": 6,  # todo: verify
                   "demurrage_rate": 730}  # todo: verify

feeder_1100_data = {"name": 'Feeder_1100_1',  # https://products.damen.com/en/ranges/container-feeder
                    "type": 'Feeder_1100',
                    "call_size": 1719,  # TEU
                    "tonnage": 0,  # todo: verify
                    "LOA": 148.8,  # m
                    "beam": 25.5,  # m
                    "draft": 8.5,  # m
                    # "speedmax": 15,  # kts
                    "max_cranes": 1,  # todo: verify
                    "all_turn_time": 31,  # todo: verify
                    "mooring_time": 6,  # todo: verify
                    "demurrage_rate": 730}  # todo: verify

feeder_1700_data = {"name": 'Feeder_1700_1',  # https://products.damen.com/en/ranges/container-feeder
                    "type": 'Feeder_1700',
                    "call_size": 1740,  # TEU
                    "tonnage": 0,  # todo: verify
                    "LOA": 172,  # m
                    "beam": 28.8,  # m
                    "draft": 8.5,  # m
                    # "speedmax": 18,  # kts
                    "max_cranes": 2,  # todo: verify
                    "all_turn_time": 31,  # todo: verify
                    "mooring_time": 6,  # todo: verify
                    "demurrage_rate": 730}  # todo: verify

feeder_2500_data = {"name": 'Feeder_2500_1',  # https://products.damen.com/en/ranges/container-feeder
                    "type": 'Feeder_2500',
                    "call_size": 2500,  # TEU
                    "tonnage": 0,  # todo: verify
                    "LOA": 195,  # m
                    "beam": 32.2,  # m
                    "draft": 9.5,  # m
                    # "speedmax": 19,  # kts
                    "max_cranes": 2,  # todo: verify
                    "all_turn_time": 31,  # todo: verify
                    "mooring_time": 6,  # todo: verify
                    "demurrage_rate": 730}  # todo: verify

panamax_data = {"name": 'Panamax_1',  # https://en.wikipedia.org/wiki/Container_ship
                "type": 'Panamax',
                "call_size": 5_100,  # TEU
                # "tonnage": 53_500,  # DWT
                "LOA": 294.13,  # m
                "beam": 32.31,  # m
                "draft": 12.04,  # m
                # "speedmax": 20,  # kts - https://transportgeography.org/?page_id=5955
                "max_cranes": 4,  # STS cranes
                "all_turn_time": 31,  # UNCTAD geeft deze waarde voor container schepen
                "mooring_time": 6,  # berthing + deberthing time
                "demurrage_rate": 730}

neopanamax_data = {"name": 'Neopanamax_1',  # https://en.wikipedia.org/wiki/Container_ship
                   "type": 'Neopanamax',
                   "call_size": 14_500,  # TEU
                   # "tonnage": 120_000,  # DWT
                   "LOA": 366,  # m
                   "beam": 49,  # m
                   "draft": 15.2,  # m
                   # "speedmax": 20,  # kts - https://transportgeography.org/?page_id=5955
                   "max_cranes": 4,  # STS cranes
                   "all_turn_time": 31,  # UNCTAD geeft deze waarde voor container schepen
                   "mooring_time": 6,  # berthing + deberthing time
                   "demurrage_rate": 730}

ulcv_data = {"name": 'ULCV_1',  # https://en.wikipedia.org/wiki/Container_ship
                "type": 'ULCV',
                "call_size": 20_000,  # TEU
                "tonnage": 120_000,  # DWT
                "LOA": 366,  # m
                "beam": 49,  # m
                "draft": 15.2,  # m
                # "speedmax": 20,  # kts - https://transportgeography.org/?page_id=5955
                "max_cranes": 4,  # STS cranes
                "all_turn_time": 31,  # UNCTAD geeft deze waarde voor container schepen
                "mooring_time": 6,  # berthing + deberthing time
                "demurrage_rate": 730}


handysize_data = {"name": 'Handysize_1',
                  "type": 'Handysize',
                  "call_size": 35_000,
                  "LOA": 130,
                  "draft": 10,
                  "beam": 24,
                  # "speedmax": 20,  # kts - https://transportgeography.org/?page_id=5955
                  "max_cranes": 2,
                  "all_turn_time": 24,
                  "mooring_time": 3,
                  "demurrage_rate": 600}

handymax_data = {"name": 'Handymax_1',
                 "type": 'Handymax',
                 "call_size": 55_000,
                 "LOA": 180,
                 "draft": 11.5,
                 "beam": 28,
                 # "speedmax": 20,  # kts - https://transportgeography.org/?page_id=5955
                 "max_cranes": 2,
                 "all_turn_time": 24,
                 "mooring_time": 3,
                 "demurrage_rate": 750}


# *** Default inputs: Labour class ***

labour_data = {"name": 'Labour',
               "international_salary": 105_000,
               "international_staff": 4,
               "local_salary": 18_850,
               "local_staff": 10,
               "operational_salary": 16_750,
               "shift_length": 6.5,
               "annual_shifts": 200,
               "daily_shifts": 5,
               "blue_collar_salary": 25_000,
               "white_collar_salary": 35_000}

# *** Default inputs: Energy class ***

energy_data = {"name": 'Energy',
               "price": 0.10}

# *** Default inputs: General_Services class ***

general_services_data = {"name": 'General_Services"',
                         "type": 'general_services',
                         "office": 2400,
                         "office_cost": 1500,
                         "workshop": 2400,
                         "workshop_cost": 1000,
                         "fuel_station_cost": 500_000,
                         "scanning_inspection_area": 2700,
                         "scanning_inspection_area_cost": 1000,
                         "lighting_mast_required": 1.2,  #masts per ha
                         "lighting_mast_cost": 30_000,
                         "firefight_cost": 2_000_000,
                         "maintenance_tools_cost": 10_000_000,
                         "terminal_operating_software_cost": 10_000_000,
                         "electrical_station_cost": 2_000_000,
                         "repair_building": 100,
                         "repair_building_cost": 1000,
                         "ceo": 1,  # FTE per 500 k TEU
                         "secretary": 1,  # FTE per 500 k TEU
                         "administration": 3,  # FTE per 500 k TEU
                         "hr": 2,  # FTE per 500 k TEU
                         "commercial": 1,  # FTE per 500 k TEU
                         "operations": 4,  # FTE/shirt per 500 k TEU
                         "engineering": 2,  # FTE/shift per 500 k TEU
                         "security": 2,  # FTE/shift per 500 k TEU
                         "general_maintenance": 0.015,
                         "crew_required": 500_000,  # for each 500_k TEU an additional crew team is added
                         "delivery_time": 1,
                         "lighting_consumption": 1,
                         "general_consumption": 1000}

indirect_costs_data = {"name": 'Indirect_Costs',
               "preliminaries": 0.15,
               "engineering": 0.05,
               "miscellaneous": 0.15,
               "electrical_works_fuel_terminal": 0.12,
               "electrical_works_power_terminal": 0.15}