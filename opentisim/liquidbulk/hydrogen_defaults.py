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
- 6. Commodity
    - Liquid hydrogen
    - Ammonia
    - MCH
- 7. Vessel
    - smallhydrogen
    - largehydrogen
    - smallammonia
    - largeammonia
    - Handysize
    - Panamax
    - VLCC
- 8. Labour

Default values are based on Claes 2018; Corbeau 2018; Daas 2018; Juha 2018;
Kranendonk 2018; Schutz 2018; Schuurmans 2018 and Verstegen 2018

"""

# package(s) for data handling
import pandas as pd


# *** Default inputs: Jetty class ***

jetty_data = {"name": 'Jetty_01',
                  "ownership": 'Port authority',
                  "delivery_time": 2, ##[Abrahamse2021]
                  "lifespan": 30, #[Lanphen 2019, P 84]
                  "mobilisation_min": 1_000_000, #equipment (+0 for import terminal and +1_000_000 for export terminal) [Lanphen 2019, P 84]
                  "mobilisation_perc": 0.02, 
                  "maintenance_perc": 0.01,
                  "insurance_perc": 0.01,
                  "Gijt_constant_jetty": 2000, #based on personal communation with de Gijt [Lanphen 2019, P 84]
                  "jettywidth": 16, #based on personal communation with de Gijt [Lanphen 2019, P 84]
                  "jettylength": 30, #based on personal communation with de Gijt [Lanphen 2019, P 84]
                  "mooring_dolphins":250_000, #based on personal communcation with Quist [Lanphen 2019, P 84]
                  "catwalkwidth": 5, #based on personal communcation with Quist [Lanphen 2019, P 84]
                  "catwalklength":100, #based on personal communcation with Quist [Lanphen 2019, P 84]
                  "Catwalk_rate": 1000, #based on personal communcation with Quist [Lanphen2019, P 84]
                            } 

# *** Default inputs: Berth class ***

berth_data = {"name": 'Berth_01',
              "crane_type": 'Mobile cranes',
              "delivery_time": 2}  # #[Abrahamse2021]


# *** Default inputs: Pipeline class ***

jetty_pipeline_data = {"name": 'jetty_pipeline_01',
                      "type": 'jetty_pipeline',
                      "length": 600, #[Lanphen2019, P 86]
                      "ownership": 'Terminal operator',
                      "delivery_time": 1,
                      "lifespan": 26,
                      "unit_rate_factor": 13_000, #[Lanphen2019, P 86]
                      "mobilisation": 30_000,
                      "maintenance_perc": 0.01,
                      "insurance_perc": 0.01,
                      "consumption_coefficient": 100, # [Lanphen2019, P 86]
                      "crew": 1,
                      "utilisation": 0.80,
                      "capacity": 1, 
                      "losses": 0} # Calculated in the hydrogen_system.py (the same as capacity of 1 jetty) 

hinterland_pipeline_data = {"name": 'hinterland_pipeline_01',
                            "type": 'hinterland_pipeline',
                            "length": 400,
                            "ownership": 'Terminal operator',
                            "delivery_time": 1,
                            "lifespan": 26,
                            "mobilisation": 30_000,
                            "unit_rate_factor": 1_500, #193_000
                            "maintenance_perc": 0.01,
                            "insurance_perc": 0.01,
                            "consumption_coefficient": 80, #in kwh/ton
                            "crew": 1,
                            "utilisation": 0.80,
                            "capacity": 685, #4000 ton/hr
                             "losses": 0} 


# *** Default inputs: Storage class ***

"Liquid hydrogen"

storage_lh2_data = {"name": 'HTank_01',
             "type": 'HydrogenTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2, #[Abrahamse2021]
             "lifespan": 30,
             "unit_rate": 350_000_000, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.01,
             "crew_min": 3,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "storage_type": 'tank',
             "consumption": 610, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019] 
             "capacity": 3_550, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019] 
               "losses": 0.06} #%/d 

# [Ishimoto 2020] = Large-scale production and transport of hydrogen from Norway to Europe and Japan: Value chain analysis and comparison of liquid hydrogen and ammonia as energy (Ishimoto, Y., Voldsund, M., Nekså, P., Roussanaly, S., Berstad, D., Gardarsdottir, S. O.)

# [IEA 2019] = The Future of Hydrogen (Assumptions and Data Appendix) 

"Ammonia"
storage_nh3_data = {"name": 'ATank_01',
                  "type": 'AmmoniaTank',
                  "ownership": 'Terminal operator',
                  "delivery_time": 2,#[Abrahamse2021]
                  "lifespan": 30,
                  "unit_rate": 55_000_000, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                  "mobilisation_min": 200_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.01,
                  "crew_min": 3,
                  "crew_for5": 1,
                  "insurance_perc": 0.01,
                  "storage_type": 'tank',
                  "consumption": 100, #in kwh/ton #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                  "capacity": 34_130,#[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                    "losses": 0.03} #%/d

"MCH"
storage_MCH_data = {"name": 'MCHTank_01',
                  "type": 'MCHTank',
                  "ownership": 'Terminal operator',
                  "delivery_time": 2, #[Abrahamse2021]
                  "lifespan": 50,
                  "unit_rate": 32_000_000, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                  "mobilisation_min": 200_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.01,
                  "crew_min": 3,
                  "crew_for5": 1,
                  "insurance_perc": 0.01,
                  "storage_type": 'tank',
                  "consumption": 10, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                  "capacity": 38_500, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                   "losses": 0} 


# *** Default inputs: H2 Reconversion class ***

"Liquid hydrogen"
h2retrieval_lh2_data = {"name": 'H2retrieval_LH2_01',
                  "type": 'HydrogenTank',
                  "ownership": 'Terminal operator',
                  "delivery_time": 2,
                  "lifespan": 20,
                  "unit_rate": 59_000_000, #[Abrahamse 2021] 
                  "mobilisation_min": 200_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.015,
                  "crew_min": 3,
                  "crew_for5": 1,
                  "insurance_perc": 0.01,
                  "h2retrieval_type": 'tank',
                  "consumption": 600, #in kwh/ton #[Abrahamse 2021] 
                  "capacity": 137, #ton H2/hr #[Abrahamse 2021] 137 ton H2 /hr --> 137 ton LH2 / hr
                  "losses": 0 } 

"Ammonia"
h2retrieval_nh3_data = {"name": 'H2retrieval_NH3_01',
             "type": 'AmmoniaTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2,
             "lifespan": 20,
             "unit_rate": 225_000_000, #[Abrahamse 2021] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 3,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "h2retrieval_type": 'tank',
             "consumption": 5889,#in kwh/ton #[Abrahamse 2021] 
             "capacity": 221, #ton H2/hr #[Abrahamse 2021] 39 ton H2 / hr --> 221 ton NH3 / hr
             "losses": 1}  #%

"MCH"
h2retrieval_MCH_data = {"name": 'H2retrieval_MCH_01',
             "type": 'MCHTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2,
             "lifespan": 20,
             "unit_rate": 335_000_000, #[Abrahamse 2021] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 3,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "h2retrieval_type": 'tank',
             "consumption": 9360,#in kwh/ton #[Abrahamse 2021] 
             "capacity": 742, #in ton H2/hr #[Abrahamse 2021] 46 ton H2 / hr --> 742 ton MCH / hr
             "losses": 10}  


# *** Default inputs: H2 Conversion class ***

"Liquid hydrogen"
h2conversion_lh2_data = {"name": 'H2conversion_LH2_01',
                  "type": 'LH2Tank',
                  "ownership": 'Terminal operator',
                  "delivery_time": 2,
                  "lifespan": 20,
                  "unit_rate": 439_000_000, #[Abrahamse 2019] 
                  "mobilisation_min": 200_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.015,
                  "crew_min": 3,
                  "crew_for5": 1,
                  "insurance_perc": 0.01,
                  "h2conversion_type": 'tank',
                  "consumption": 6400, #in kwh/ton #[Abrahamse 2021] 
                  "capacity": 30, #ton LH2/hr #[Abrahamse 2021] 
                  "losses": 0, 
                   "recycle_rate": 0,
                    "priceH2": 2.70} #€/kg

"Ammonia"
h2conversion_nh3_data = {"name": 'H2conversion_NH3_01',
             "type": 'AmmoniaTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2,
             "lifespan": 20,
             "unit_rate": 361_500_000, #[Abrahamse 2021] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 3,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "h2conversion_type": 'tank',
             "consumption": 640,#in kwh/ton #[Abrahamse 2021] 
             "capacity": 130, #ton NH3/hr #[Abrahamse 2021] 
             "losses": 1,
              "recycle_rate": 0,
              "priceH2": 2.70}  #%#€/kg

"MCH"
h2conversion_MCH_data = {"name": 'H2conversion_MCH_01',
             "type": 'MCHTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2,
             "lifespan": 20,
             "unit_rate": 48_000_000, #[Abrahamse 2021] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 3,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "h2conversion_type": 'tank',
             "consumption": 300,#in kwh/ton #[Abrahamse 2021] 
             "capacity": 45, #in ton MCH/hr #[Abrahamse 2021] 
             "losses": 1,
             "recycle_rate": 97,
              "priceH2": 2.70} #€/kg  



# *** Default inputs: Commodity class ***

commodity_lhydrogen_data = {"name": 'Liquid hydrogen',
                            "type": 'Liquid hydrogen',
                  "handling_fee": 490,
                   "Hcontent": 100, 
                   "material_price": 0,
                  "smallhydrogen_perc": 30,
                  "largehydrogen_perc": 70,
                  "smallammonia_perc": 0,
                  "largeammonia_perc": 0,
                  "handysize_perc": 0,
                  "panamax_perc": 0,
                  "vlcc_perc": 0,
                  "historic_data": []}

commodity_ammonia_data = {"name": 'Ammonia',
                "type": 'Ammonia',
                "handling_fee": 150,
                "Hcontent": 17.65,
                "material_price": 27, #€/ton
                "smallhydrogen_perc": 0,
                "largehydrogen_perc": 0,
                "smallammonia_perc": 40,
                "largeammonia_perc": 60,
                "handysize_perc": 0,
                "panamax_perc": 0,
                "vlcc_perc": 0,
                "historic_data": []}

commodity_MCH_data = {"name": 'MCH',
            "type": 'MCH',
            "handling_fee": 1000,
            "Hcontent": 5.7,
            "material_price": 350, #€/ton
            "smallhydrogen_perc": 0,
            "largehydrogen_perc": 0,
            "smallammonia_perc": 0,
            "largeammonia_perc": 0,
            "handysize_perc": 30,
            "panamax_perc": 40,
            "vlcc_perc": 30,
            "historic_data": []}

# *** Default inputs: Vessel class ***

"Liquid hydrogen:"

smallhydrogen_data = {"name": 'smallhydrogen_1',
                  "type": 'Smallhydrogen',
                  "call_size": 10_345, #[Abrahamse 2021]
                  "LOA": 200,
                  "draft": 10,
                  "beam": 24,
                  "max_cranes": 3,
                  "all_turn_time": 20,
                  "pump_capacity": 1_034.5, #[Abrahamse 2021]
                  "mooring_time": 3,
                  "demurrage_rate": 600}

largehydrogen_data = {"name": 'largehydrogen_1',
                  "type": 'Largehydrogen',
                  "call_size": 18_886, #[Abrahamse 2021]
                  "LOA": 300,
                  "draft": 12,
                  "beam": 43,
                  "max_cranes": 3,
                  "all_turn_time": 30,
                  "pump_capacity": 1888.6, #[Abrahamse 2021]
                  "mooring_time": 3,
                  "demurrage_rate": 700}

"Ammonia:"

smallammonia_data = {"name": 'smallammonia_1',
                 "type": 'Smallammonia',
                 "call_size": 14_062, #[Abrahamse 2021]
                 "LOA": 170,
                 "draft": 9.5,
                 "beam": 22,
                 "max_cranes": 2,
                 "all_turn_time": 24,
                 "pump_capacity": 1406.2, #[Abrahamse 2021]
                 "mooring_time": 3,
                 "demurrage_rate": 750}

largeammonia_data = {"name": 'largeammonia_1',
                 "type": 'Largeammonia',
                 "call_size": 56110, #[Abrahamse 2021]
                 "LOA": 230,
                 "draft": 11,
                 "beam": 40,
                 "max_cranes": 2,
                 "all_turn_time": 24,
                 "pump_capacity": 5661, #[Abrahamse 2021]
                 "mooring_time": 3, 
                 "demurrage_rate": 750}

"MCH:"
handysize_data = {"name": 'Handysize_1',
                  "type": 'Handysize',
                  "call_size": 35_000, #[Abrahamse 2021]
                  "LOA": 130,
                  "draft": 10,
                  "beam": 24,
                  "max_cranes": 2,
                  "all_turn_time": 24,
                  "pump_capacity": 3_500, #[Abrahamse 2021]
                  "mooring_time": 3,
                  "demurrage_rate": 600}

panamax_data = {"name": 'Panamax_1',
                "type": 'Panamax',
                "call_size": 65_000, #[Abrahamse 2021]
                "LOA": 220,
                "draft": 13,
                "beam": 32.2,
                "max_cranes": 3,
                "all_turn_time": 36,
                "pump_capacity": 6_500, #[Abrahamse 2021]
                "mooring_time": 3,
                "demurrage_rate": 730}

vlcc_data = {"name": 'VLCC_1',
             "type": 'VLCC',
             "call_size": 200_000, #[Abrahamse 2021]
             "LOA": 300,
             "draft": 18.5,
             "beam": 55,
             "max_cranes": 3,
             "all_turn_time": 40,
             "pump_capacity": 20_000, #[Abrahamse 2021]
             "mooring_time": 3,
             "demurrage_rate": 1000}


# *** Default inputs: Labour class ***

labour_data = {"name": 'Labour',
               "international_salary": 105_000,
               "international_staff": 4,
               "local_salary": 18_850,
               "local_staff": 10,
               "operational_salary": 46_000,
               "shift_length": 8,
               "annual_shifts": 200}

# *** Default inputs: Energy class ***

energy_data = {"name": 'Energy',
               "price": 0.09}

