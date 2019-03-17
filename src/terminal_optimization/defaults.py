"""Defaults for following objects:

- 1. Quay_wall
- 2. Berth
- 3. Cyclic_Unloader
    - Gantry crane
    - Harbour crane
    - Mobile crane
     Continuous_Unloader
    - Continuous screw
- 4. Conveyor
    - Hinterland conveyor
    - Quay conveyor
- 5. Storage
    - Silo
    - Warehouse
- 6. Unloading_station
    - Hinterland station
- 7. Commodity
    - Maize
    - Soybean
    - Wheat
- 8. Vessel
    - Handysize
    - Handymax
    - Panamax
- 9. Labour

Default values are based on Claes 2018; Corbeau 2018; Daas 2018; Juha 2018;
Kranendonk 2018; Schutz 2018; Schuurmans 2018 and Verstegen 2018

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
                  "Gijt_constant": 757.20,
                  "Gijt_coefficient": 1.2878,
                  "length": 400,  # should probably be calculated
                  "depth": 14}  # should probably be calculated

# *** Default inputs: Berth class ***

berth_data = {"name": 'Berth_01',
              "crane_type": 'Mobile cranes',
              "delivery_time": 1,
              "max_cranes": 3}
# todo: check delivery time of berth
# todo: check if indeed at t = 0 it takes 1 year to get a berth online and 2 years to get a quay online

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
                     "eff_fact": 0.50}

harbour_crane_data = {"name": 'Harbour_crane_01',
                      "ownership": 'Terminal operator',
                      "delivery_time": 1,
                      "lifespan": 40,
                      "unit_rate": 10_500_000,
                      "mobilisation_perc": 0.15,
                      "maintenance_perc": 0.02,
                      "consumption": 210,
                      "insurance_perc": 0.01,
                      "crew": 3,
                      "crane_type": 'Harbour crane',
                      "lifting_capacity": 40,
                      "hourly_cycles": 40,
                      "eff_fact": 0.40}

mobile_crane_data = {"name": 'Mobile_crane_01',
                     "ownership": 'Terminal operator',
                     "delivery_time": 1,
                     "lifespan": 20,
                     "unit_rate": 3_325_000,
                     "mobilisation_perc": 0.15,
                     "maintenance_perc": 0.031,
                     "consumption": 310,
                     "insurance_perc": 0.01,
                     "crew": 3,
                     "crane_type": 'Mobile crane',
                     "lifting_capacity": 30,
                     "hourly_cycles": 25,
                     "eff_fact": 0.35}

# *** Default inputs: ContinuousUnloader class ***


continuous_screw_data = {"name": 'Continuous_loader_01',
                         "ownership": 'Terminal operator',
                         "delivery_time": 1,
                         "lifespan": 30,
                         "unit_rate": 6_900_000,
                         "mobilisation_perc": 0.15,
                         "maintenance_perc": 0.02,
                         "consumption": 364,
                         "insurance_perc": 0.01,
                         "crew": 2,
                         "crane_type": 'Screw unloader',
                         "peak_capacity": 700,
                         "eff_fact": 0.55}

# *** Default inputs: Conveyor class ***

quay_conveyor_data = {"name": 'Quay_conveyor_01',
                      "length": 500,
                      "ownership": 'Terminal operator',
                      "delivery_time": 1,
                      "lifespan": 10,
                      "unit_rate": 6,
                      "mobilisation": 30_000,
                      "maintenance_perc": 0.10,
                      "insurance_perc": 0.01,
                      "consumption_constant": 81,
                      "consumption_coefficient": 0.08,
                      "crew": 1,
                      "utilisation": 0.80,
                      "capacity_steps": 400}

hinterland_conveyor_data = {"name": 'Hinterland_conveyor_01',
                            "length": 500,
                            "ownership": 'Terminal operator',
                            "delivery_time": 1,
                            "lifespan": 10,
                            "mobilisation": 30_000,
                            "unit_rate": 6,
                            "maintenance_perc": 0.10,
                            "insurance_perc": 0.01,
                            "consumption_constant": 81,
                            "consumption_coefficient": 0.08,
                            "crew": 1,
                            "utilisation": 0.80,
                            "capacity_steps": 400}

# *** Default inputs: Storage class ***

silo_data = {"name": 'Silo_01',
             "ownership": 'Terminal operator',
             "delivery_time": 1,
             "lifespan": 30,
             "unit_rate": 60,
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.02,
             "crew": 1,
             "insurance_perc": 0.01,
             "storage_type": 'Silos',
             "consumption": 0.002,
             "capacity": 5_000}

warehouse_data = {"name": 'Warehouse_01',
                  "ownership": 'Terminal operator',
                  "delivery_time": 1,
                  "lifespan": 30,
                  "unit_rate": 140,
                  "mobilisation_min": 200_000,
                  "mobilisation_perc": 0.001,
                  "maintenance_perc": 0.01,
                  "crew": 3,
                  "insurance_perc": 0.01,
                  "storage_type": 'Warehouse',
                  "consumption": 0.002,
                  "silo_capacity": 'n/a'}

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
                           "production": 800}

# *** Default inputs: Commodity class ***

maize_data = {"name": 'Maize',
              "handling_fee": 3,
              "handysize_perc": 50,
              "handymax_perc": 50,
              "panamax_perc": 0,
              "historic_data": pd.DataFrame(data={'year': [2014, 2015, 2016, 2017, 2018],
                                                  'volume': [1_000_000, 1_100_000, 1_250_000, 1_400_000, 1_500_000]})}

soybean_data = {"name": 'Soybeans',
                "handling_fee": 3,
                "handysize_perc": 50,
                "handymax_perc": 50,
                "panamax_perc": 0,
                "historic_data": pd.DataFrame(data={'year': [2014, 2015, 2016, 2017, 2018],
                                                    'volume': [1_000_000, 1_100_000, 1_250_000, 1_400_000, 1_500_000]})}

wheat_data = {"name": 'Wheat',
              "handling_fee": 3,
              "handysize_perc": 0,
              "handymax_perc": 0,
              "panamax_perc": 100,
              "historic_data": pd.DataFrame(data={'year': [2014, 2015, 2016, 2017, 2018],
                                                  'volume': [1_000_000, 1_100_000, 1_250_000, 1_400_000, 1_500_000]})}

# *** Default inputs: Vessel class ***

handysize_data = {"name": 'Handysize_1',
                  "type": 'Handysize',
                  "call_size": 35_000,
                  "LOA": 130,
                  "draft": 10,
                  "beam": 24,
                  "max_cranes": 2,
                  "all_turn_time": 24,
                  "mooring_time": 3,
                  "demurrage_rate": 600}

handymax_data = {"name": 'Handymax_1',
                 "type": 'Handymax',
                 "call_size": 50_000,
                 "LOA": 180,
                 "draft": 11.5,
                 "beam": 28,
                 "max_cranes": 2,
                 "all_turn_time": 24,
                 "mooring_time": 3,
                 "demurrage_rate": 750}

panamax_data = {"name": 'Panamax_1',
                "type": 'Panamax',
                "call_size": 65_000,
                "LOA": 220,
                "draft": 13,
                "beam": 32.2,
                "max_cranes": 3,
                "all_turn_time": 36,
                "mooring_time": 3,
                "demurrage_rate": 730}

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
