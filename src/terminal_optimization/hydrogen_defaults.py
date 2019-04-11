"""Defaults for following objects:

- 1. Jetty
- 2. Berth
- 3. Unloader
    - Liquid hydrogen
    - Ammonia
    - MCH
- 4. Pipelines
    - jetty
    - hinterland
- 5. Storage
    - Liquid hydrogen
    - Ammonia
    - MCH
- 6. H2 retrieval
    - Ammonia
    - MCH
- 6. Unloading_station
    - Hinterland station
- 7. Commodity
    - Liquid hydrogen
    - Ammonia
    - MCH
- 8. Vessel
    - smallhydrogen
    - largehydrogen
    - smallammonia
    - largeammonia
    - Handysize
    - Panamax
    - VLCC
- 9. Labour

Default values are based on Claes 2018; Corbeau 2018; Daas 2018; Juha 2018;
Kranendonk 2018; Schutz 2018; Schuurmans 2018 and Verstegen 2018

"""

# package(s) for data handling
import pandas as pd

# *** Default inputs: Jetty class ***

jetty_data = {"name": 'Jetty_01',
                  "ownership": 'Port authority',
                  "delivery_time": 2,
                  "lifespan": 50,
                  "mobilisation_min": 2_500_000,
                  "mobilisation_perc": 0.02,
                  "maintenance_perc": 0.01,
                  "insurance_perc": 0.01,
                  "freeboard": 4,
                  "Gijt_constant_jetty": 1500,
                  "max_sinkage": 0.5,
                  "wave_motion": 0.5,
                  "safety_margin": 0.5} # all values from Ijzermans, 2019, P 91

# *** Default inputs: Berth class ***

berth_data = {"name": 'Berth_01',
              "crane_type": 'Mobile cranes',
              "delivery_time": 1,
              "max_cranes": 3}  # all values from Ijzermans, 2019, P 92


# *** Default inputs: Pipeline class ***

jetty_pipeline_data = {"name": 'jetty_pipeline_01',
                      "type": 'jetty_pipeline',
                      "length": 200,
                      "ownership": 'Terminal operator',
                      "delivery_time": 1,
                      "lifespan": 10,
                      "unit_rate_factor": 6,
                      "mobilisation": 30_000,
                      "maintenance_perc": 0.10,
                      "insurance_perc": 0.01,
                      "consumption_constant": 81,
                      "consumption_coefficient": 0.08,
                      "crew": 1,
                      "utilisation": 0.80,
                      "capacity": 4000} # all input values from Ijzermans, 2019, P 104

hinterland_pipeline_data = {"name": 'hinterland_pipeline_01',
                            "type": 'hinterland_pipeline',
                            "length": 400,
                            "ownership": 'Terminal operator',
                            "delivery_time": 1,
                            "lifespan": 10,
                            "mobilisation": 30_000,
                            "unit_rate_factor": 6,
                            "maintenance_perc": 0.10,
                            "insurance_perc": 0.01,
                            "consumption_constant": 81,
                            "consumption_coefficient": 0.08,
                            "crew": 1,
                            "utilisation": 0.80,
                            "capacity": 400} # all input values from Ijzermans, 2019, P 104


# *** Default inputs: Storage class ***

"Liquid hydrogen "

storage_lh2_data = {"name": 'HTank_01',
             "type": 'HydrogenTank',
             "ownership": 'Terminal operator',
             "delivery_time": 1,
             "lifespan": 20,
             "unit_rate": 800_000_000,
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.01,
             "crew_min": 3,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "storage_type": 'tank',
             "consumption": 0.1,
             "capacity": 60_000} # all input values from Ijzermans, 2019, P 102

"Ammonia"
storage_nh3_data = {"name": 'ATank_01',
                  "style": 'AmmoniaTank',
                  "ownership": 'Terminal operator',
                  "delivery_time": 1,
                  "lifespan": 20,
                  "unit_rate": 17_000_000,
                  "mobilisation_min": 200_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.01,
                  "crew_min": 3,
                  "crew_for5": 1,
                  "insurance_perc": 0.01,
                  "storage_type": 'tank',
                  "consumption": 0.1,
                  "capacity": 45_000}

"MCH"

# *** Default inputs: H2Convertion class ***




# *** Default inputs: Unloading_station class ***


hinterland_station_data = {"name": 'Hinterland_station_01',
                           "ownership": 'Terminal operator',
                           "delivery_time": 1,
                           "lifespan": 15,
                           "unit_rate": 800_000,
                           "mobilisation": 200_000,
                           "maintenance_perc": 0.02,
                           "consumption": 100,
                           "insurance_perc": 0.01,
                           "crew": 2,
                           "production": 800,
                           "wagon_payload" : 60,
                           "number_of_wagons": 60,
                           "prep_time": 2}

# *** Default inputs: Commodity class ***

lhydrogen_data = {"name": 'Liquid hydrogen',
                  "handling_fee": 9.8,
                  "smallhydrogen_perc": 30,
                  "largehydrogen_perc": 70,
                  "smallammonia_perc": 0,
                  "largeammonia_perc": 0,
                  "handysize_perc": 0,
                  "panamax_perc": 0,
                  "vlcc_perc": 0,
                  "historic_data": pd.DataFrame(data={'year': [2014, 2015, 2016, 2017, 2018],
                                                  'volume': [1_000_000, 1_100_000, 1_250_000, 1_400_000, 1_500_000]})}

ammonia_data = {"name": 'Ammonia',
                "handling_fee": 9.8,
                "smallhydrogen_perc": 0,
                "largehydrogen_perc": 0,
                "smallammonia_perc": 40,
                "largeammonia_perc": 60,
                "handysize_perc": 0,
                "panamax_perc": 0,
                "vlcc_perc": 0,
                "historic_data": pd.DataFrame(data={'year': [2014, 2015, 2016, 2017, 2018],
                                                'volume': [1_000_000, 1_100_000, 1_250_000, 1_400_000, 1_500_000]})}
MCH_data = {"name": 'MCH',
            "handling_fee": 9.8,
            "smallhydrogen_perc": 0,
            "largehydrogen_perc": 0,
            "smallammonia_perc": 0,
            "largeammonia_perc": 0,
            "handysize_perc": 30,
            "panamax_perc": 40,
            "vlcc_perc": 30,
            "historic_data": pd.DataFrame(data={'year': [2014, 2015, 2016, 2017, 2018],
                                                  'volume': [1_000_000, 1_100_000, 1_250_000, 1_400_000, 1_500_000]})}

# *** Default inputs: Vessel class ***

"Liquid hydrogen:"

smallhydrogen_data = {"name": 'smallhydrogen_1',
                  "type": 'Smallhydrogen',
                  "call_size": 10_000,
                  "LOA": 200,
                  "draft": 10,
                  "beam": 24,
                  "max_cranes": 3,
                  "all_turn_time": 20,
                  "pump_capacity": 1_000,
                  "mooring_time": 3,
                  "demurrage_rate": 600}

largehydrogen_data = {"name": 'largehydrogen_1',
                  "type": 'Largehydrogen',
                  "call_size": 30_000,
                  "LOA": 300,
                  "draft": 12,
                  "beam": 43,
                  "max_cranes": 3,
                  "all_turn_time": 30,
                  "pump_capacity": 3_000,
                  "mooring_time": 3,
                  "demurrage_rate": 700}

"Ammonia:"

smallammonia_data = {"name": 'smallammonia_1',
                 "type": 'Smallammonia',
                 "call_size": 20_000,
                 "LOA": 170,
                 "draft": 9.5,
                 "beam": 22,
                 "max_cranes": 2,
                 "all_turn_time": 24,
                 "pump_capacity": 2_000,
                 "mooring_time": 3,
                 "demurrage_rate": 750}

largeammonia_data = {"name": 'largeammonia_1',
                 "type": 'Largeammonia',
                 "call_size": 55_000,
                 "LOA": 230,
                 "draft": 11,
                 "beam": 40,
                 "max_cranes": 2,
                 "all_turn_time": 24,
                 "pump_capacity": 5_500,
                 "mooring_time": 3,
                 "demurrage_rate": 750}

"MCH:"
handysize_data = {"name": 'Handysize_1',
                  "type": 'Handysize',
                  "call_size": 35_000,
                  "LOA": 130,
                  "draft": 10,
                  "beam": 24,
                  "max_cranes": 2,
                  "all_turn_time": 24,
                  "pump_capacity": 3_500,
                  "mooring_time": 3,
                  "demurrage_rate": 600}

panamax_data = {"name": 'Panamax_1',
                "type": 'Panamax',
                "call_size": 65_000,
                "LOA": 220,
                "draft": 13,
                "beam": 32.2,
                "max_cranes": 3,
                "all_turn_time": 36,
                "pump_capacity": 6_500,
                "mooring_time": 3,
                "demurrage_rate": 730}

vlcc_data = {"name": 'VLCC_1',
             "type": 'VLCC',
             "call_size": 200_000,
             "LOA": 300,
             "draft": 18.5,
             "beam": 55,
             "max_cranes": 3,
             "all_turn_time": 40,
             "pump_capacity": 20_000,
             "mooring_time": 3,
             "demurrage_rate": 1000}


# *** Default inputs: Labour class ***

labour_data = {"name": 'Labour',
               "international_salary": 105_000,
               "international_staff": 4,
               "local_salary": 18_850,
               "local_staff": 10,
               "operational_salary": 16_750,
               "shift_length": 6.5,
               "annual_shifts": 200}

# *** Default inputs: Energy class ***

energy_data = {"name": 'Energy',
               "price": 0.10}

# *** Default inputs: Train class ***

train_data = {"wagon_payload": 60,
              "number_of_wagons": 60}
