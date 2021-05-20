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
             "unit_rate": 250_000_000, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019] 
             "mobilisation_min": 100_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.01,
             "crew_min": 1,
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
                  "mobilisation_min": 100_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.01,
                  "crew_min": 1,
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
                  "lifespan": 30,
                  "unit_rate": 20_000_000, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                  "mobilisation_min": 100_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.01,
                  "crew_min": 1,
                  "crew_for5": 1,
                  "insurance_perc": 0.01,
                  "storage_type": 'tank',
                  "consumption": 10, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                  "capacity": 38_500, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                   "losses": 0} 

"DBT"
storage_DBT_data = {"name": 'DBTTank_01',
                  "type": 'DBTTank',
                  "ownership": 'Terminal operator',
                  "delivery_time": 2, #[Abrahamse2021]
                  "lifespan": 30,
                  "unit_rate": 15_000_000, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                  "mobilisation_min": 100_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.01,
                  "crew_min": 1,
                  "crew_for5": 1,
                  "insurance_perc": 0.01,
                  "storage_type": 'tank',
                  "consumption": 1, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                  "capacity": 52_850, #[Lanphen2019, P 87], [HyChain Import Model Excel], [Ishimoto 2020], [IEA 2019]
                   "losses": 0} 


# *** Default inputs: H2 Reconversion class ***

"Liquid hydrogen"
h2retrieval_lh2_data = {"name": 'H2retrieval_LH2_01',
                  "type": 'HydrogenTank',
                  "ownership": 'Terminal operator',
                  "delivery_time": 2,
                  "lifespan": 20,
                  "unit_rate": 30_000_000, #59_000_000, #[Abrahamse 2021] 
                  "mobilisation_min": 200_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.015,
                  "crew_min": 3,
                  "crew_for5": 3,
                  "insurance_perc": 0.01,
                  "h2retrieval_type": 'tank',
                  "consumption": 600, #in kwh/ton H2#[Abrahamse 2021] 
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
             "crew_for5": 3,
             "insurance_perc": 0.01,
             "h2retrieval_type": 'tank',
             "consumption": 5890,#in kwh/ton H2 #[Abrahamse 2021] 
             "capacity": 221, #ton H2/hr #[Abrahamse 2021] 39 ton H2 / hr --> 221 ton NH3 / hr
             "losses": 1}  #%

"MCH"
h2retrieval_MCH_data = {"name": 'H2retrieval_MCH_01',
             "type": 'MCHTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2,
             "lifespan": 20,
             "unit_rate": 200_000_000, #335_000_000, #[Abrahamse 2021] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 3,
             "crew_for5": 3,
             "insurance_perc": 0.01,
             "h2retrieval_type": 'tank',
             "consumption": 9360,#in kwh/ton #[Abrahamse 2021] 
             "capacity": 742, #in ton H2/hr #[Abrahamse 2021] 46 ton H2 / hr --> 742 ton MCH / hr
             "losses": 10}  

"DBT"
h2retrieval_DBT_data = {"name": 'H2retrieval_DBT_01',
             "type": 'DBTTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2,
             "lifespan": 20,
             "unit_rate": 250_000_000, #[Abrahamse 2021] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 3,
             "crew_for5": 3,
             "insurance_perc": 0.01,
             "h2retrieval_type": 'tank',
             "consumption": 7360,#in kwh/ton #[Abrahamse 2021] 
             "capacity": 742, #in ton H2/hr #[Abrahamse 2021] 46 ton H2 / hr --> 742 ton MCH / hr
             "losses": 10}  


# *** Default inputs: H2 Conversion class ***

"Liquid hydrogen"
h2conversion_lh2_data = {"name": 'H2conversion_LH2_01',
                  "type": 'LH2Tank',
                  "ownership": 'Terminal operator',
                  "delivery_time": 2,
                  "lifespan": 20,
                  "unit_rate": 300_000_000,#439_000_000, #[Abrahamse 2019] 
                  "mobilisation_min": 200_000,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.015,
                  "crew_min": 3,
                  "crew_for5": 3,
                  "insurance_perc": 0.01,
                  "h2conversion_type": 'tank',
                  "consumption": 6100, #in kwh/ton #[Abrahamse 2021] 
                  "capacity": 30, #ton LH2/hr #[Abrahamse 2021] 
                  "losses": 0, 
                   "recycle_rate": 0,
                    "priceH2": 2.86, #€/kg
                   "sell_mat":  0, 
                     "sell_rate": 0}

"Ammonia"
h2conversion_nh3_data = {"name": 'H2conversion_NH3_01',
             "type": 'AmmoniaTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2,
             "lifespan": 20,
             "unit_rate": 362_000_000, #361_500_000, #[Abrahamse 2021] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 3,
             "crew_for5": 3,
             "insurance_perc": 0.01,
             "h2conversion_type": 'tank',
             "consumption": 640,#in kwh/ton #[Abrahamse 2021] 
             "capacity": 130, #ton NH3/hr #[Abrahamse 2021] 
             "losses": 1,
              "recycle_rate": 0,
              "priceH2": 2.86,
              "sell_mat": 0, 
             "sell_rate": 0}


"MCH"
h2conversion_MCH_data = {"name": 'H2conversion_MCH_01',
             "type": 'MCHTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2,
             "lifespan": 20,
             "unit_rate": 20_000_000, #[Abrahamse 2021] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 3,
             "crew_for5": 3,
             "insurance_perc": 0.01,
             "h2conversion_type": 'tank',
             "consumption": 20,#in kwh/ton #[Abrahamse 2021] 
             "capacity": 57, #in ton MCH/hr #[Abrahamse 2021] 
             "losses": 1,
             "recycle_rate": 97,
              "priceH2": 2.86, #€/kg  
             "sell_mat": 550, #500, #€/ton
             "sell_rate": 95}

"DBT"
h2conversion_DBT_data = {"name": 'H2conversion_DBT_01',
             "type": 'DBTTank',
             "ownership": 'Terminal operator',
             "delivery_time": 2,
             "lifespan": 20,
             "unit_rate": 15_000_000, #[Abrahamse 2021] 
             "mobilisation_min": 200_000,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 3,
             "crew_for5": 3,
             "insurance_perc": 0.01,
             "h2conversion_type": 'tank',
             "consumption": 20,#in kwh/ton #[Abrahamse 2021] 
             "capacity": 45, #in ton MCH/hr #[Abrahamse 2021] 
             "losses": 1,
             "recycle_rate": 99.9,
              "priceH2": 2.86, #€/kg  
             "sell_mat": 3100, 
             "sell_rate": 97.9}


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
            "Hcontent": 6.2,
            "material_price": 600, #€/ton
            "smallhydrogen_perc": 0,
            "largehydrogen_perc": 0,
            "smallammonia_perc": 0,
            "largeammonia_perc": 0,
            "handysize_perc": 30,
            "panamax_perc": 40,
            "vlcc_perc": 30,
            "historic_data": []}

commodity_DBT_data = {"name": 'DBT',
            "type": 'DBT',
            "handling_fee": 1000,
            "Hcontent": 6.0,
            "material_price": 3320, #€/ton
            "smallhydrogen_perc": 0,
            "largehydrogen_perc": 0,
            "smallammonia_perc": 0,
            "largeammonia_perc": 0,
            "handysize_perc": 0,
            "panamax_perc": 0,
            "vlcc_perc": 100,
            "historic_data": []}

# *** Default inputs: Sea Vessel class ***

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
                  "demurrage_rate": 600, 
                  "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 253_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0, 
                  "maintenance_perc": 0.015,
                  "crew_min": 20,
                  "crew_for5": 20,
                  "insurance_perc": 0.01,
                  "losses": 0.3, 
                  "utilization":5840, 
                  "avspeed": 25, 
                  "consumption": 275, 
                  "ship_weight": 31501,
                   "DWT": 84580,
                   "gamma":0.9, 
                  "fuelprice": 556}

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
                  "demurrage_rate": 700,
                  "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 334_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0, 
                  "maintenance_perc": 0.015,
                  "crew_min": 20,
                  "crew_for5": 20,
                  "insurance_perc": 0.01,
                  "losses": 0.3, 
                  "utilization":5840, 
                  "avspeed": 25, 
                  "consumption": 275, 
                  "ship_weight": 48008,
                   "DWT": 128900,
                   "gamma":0.9,  
                  "fuelprice": 556}

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
                 "demurrage_rate": 750,
                 "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 41_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0, 
                  "maintenance_perc": 0.015,
                  "crew_min": 20,
                  "crew_for5": 20,
                  "insurance_perc": 0.01,
                  "losses": 0.5, 
                  "utilization":5840, 
                  "avspeed": 25, 
                  "consumption": 275, 
                  "ship_weight": 7261,
                  "DWT": 19182,
                  "gamma":0.9,  
                  "fuelprice": 556}

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
                 "demurrage_rate": 750,
                 "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 82_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0, 
                  "maintenance_perc": 0.015,
                  "crew_min": 20,
                  "crew_for5": 20,
                  "insurance_perc": 0.01,
                  "losses": 0.5, 
                  "utilization":5840, 
                  "avspeed": 25, 
                  "consumption": 275, 
                  "ship_weight": 19128,
                  "DWT": 50534,
                  "gamma":0.9,  
                  "fuelprice": 556}
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
                  "demurrage_rate": 600,
                  "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 38_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0, 
                  "maintenance_perc": 0.015,
                  "crew_min": 20,
                  "crew_for5": 20,
                  "insurance_perc": 0.01,
                  "losses": 0, 
                  "utilization":5840, 
                  "avspeed": 25, 
                  "consumption": 275, 
                  "ship_weight": 11050,
                  "DWT": 78322,
                  "gamma":0.9,  
                  "fuelprice": 556}

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
                "demurrage_rate": 730,
                "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 59_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0, 
                  "maintenance_perc": 0.015,
                  "crew_min": 20,
                  "crew_for5": 20,
                  "insurance_perc": 0.01,
                  "losses": 0, 
                  "utilization":5840, 
                  "avspeed": 25, 
                  "consumption": 275, 
                  "ship_weight": 17044,
                  "DWT": 120802,
                  "gamma":0.9,  
                  "fuelprice": 556}

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
             "demurrage_rate": 1000,
             "delivery_time": 2, 
              "lifespan": 20,
              "unit_rate": 127_000_000, 
              "mobilisation_min": 0, 
              "mobilisation_perc":0, 
              "maintenance_perc": 0.015,
              "crew_min": 20,
              "crew_for5": 20,
              "insurance_perc": 0.01,
              "losses": 0, 
              "utilization":5840, 
              "avspeed": 25, 
              "consumption": 275, 
              "ship_weight": 37432,
              "DWT": 265311,
              "gamma":0.9,  
              "fuelprice": 556}

vlcc_data_DBT = {"name": 'VLCC_DBT',
             "type": 'VLCC_DBT',
             "call_size": 275_000, #[Abrahamse 2021]
             "LOA": 300,
             "draft": 18.5,
             "beam": 55,
             "max_cranes": 3,
             "all_turn_time": 40,
             "pump_capacity": 27_500, #[Abrahamse 2021]
             "mooring_time": 3,
             "demurrage_rate": 1000,
             "delivery_time": 2, 
              "lifespan": 20,
              "unit_rate": 127_000_000, 
              "mobilisation_min": 0, 
              "mobilisation_perc":0, 
              "maintenance_perc": 0.015,
              "crew_min": 20,
              "crew_for5": 20,
              "insurance_perc": 0.01,
              "losses": 0, 
              "utilization":5840, 
              "avspeed": 25, 
              "consumption": 275, 
              "ship_weight": 37432,
              "DWT": 265311,
              "gamma":0.9,  
              "fuelprice": 556}


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
               "price": 0.12}

# *** Default inputs: Barge class ***

"Liquid hydrogen:"


hydrogen_barge_data = {"name": 'hydrogenbarge_1',
                  "type": 'hydrogenbarge',
                  "call_size": 710, #[Abrahamse 2021] ton LH2
                  "delivery_time": 1, 
                  "lifespan": 20,
                  "unit_rate": 40_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0.003, 
                  "maintenance_perc": 0.015,
                  "crew_min": 2,
                  "crew_for5": 2,
                  "insurance_perc": 0.01,
                  "losses": 0.3, 
                  "utilization":5840, 
                  "avspeed": 13, #km/h
                  "consumption": 275, 
                  "ship_weight": 1500,
                  "loadingtime": 48, #h
                  "unloadingtime": 48, #h 
                  "uncertainty":1.2, 
                  "fuelprice": 1.20} #€/liter


"Ammonia:"


ammonia_barge_data = {"name": 'ammoniabarge_1',
                 "type": 'ammoniabarge',
                 "call_size": 6826, #[Abrahamse 2021] ton NH3
                 "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 20_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0.003, 
                  "maintenance_perc": 0.015,
                  "crew_min": 2,
                  "crew_for5": 2,
                  "insurance_perc": 0.01,
                  "losses": 0.08, 
                  "utilization":5840, 
                  "avspeed": 13, 
                  "consumption": 275, 
                  "ship_weight": 4400,
                  "loadingtime": 48, #h
                  "unloadingtime": 48, #h 
                  "uncertainty":1.2, 
                  "fuelprice": 1.20} #€/liter


"MCH:"
MCH_barge_data = {"name": 'MCHbarge_1',
                  "type": 'MCHbarge',
                  "call_size": 7700, #[Abrahamse 2021] ton MCH
                  "delivery_time": 1, 
                  "lifespan": 20,
                  "unit_rate": 11_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0.003, 
                  "maintenance_perc": 0.015,
                  "crew_min": 2,
                  "crew_for5": 2,
                  "insurance_perc": 0.01,
                  "losses": 0, 
                  "utilization":5840, 
                  "avspeed": 13, 
                  "consumption": 275, 
                  "ship_weight": 2300,
                  "loadingtime": 48, #h
                  "unloadingtime": 48, #h 
                  "uncertainty":1.2, 
                  "fuelprice": 1.20} #€/liter

"DBT:"
DBT_barge_data = {"name": 'DBTbarge_1',
                  "type": 'DBTbarge',
                  "call_size": 10570, #[Abrahamse 2021] ton MCH
                  "delivery_time": 1, 
                  "lifespan": 20,
                  "unit_rate": 11_000_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0.003, 
                  "maintenance_perc": 0.015,
                  "crew_min": 2,
                  "crew_for5": 2,
                  "insurance_perc": 0.01,
                  "losses": 0, 
                  "utilization":5840, 
                  "avspeed": 13, 
                  "consumption": 275, 
                  "ship_weight": 2300,
                  "loadingtime": 48, #h
                  "unloadingtime": 48, #h 
                  "uncertainty":1.2, 
                  "fuelprice": 1.20} #€/liter


# *** Default inputs: Train class ***

"Liquid hydrogen:"


hydrogen_train_data = {"name": 'hydrogentrain_1',
                  "type": 'hydrogentrain',
                  "call_size": 325, #[Abrahamse 2021] ton LH2
                  "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 27_370_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0.003, 
                  "maintenance_perc": 0.015,
                  "crew_min": 2,
                  "crew_for5": 2,
                  "insurance_perc": 0.01,
                  "losses": 0.3, 
                  "utilization":5840, 
                  "avspeed": 45, #km/h
                  "consumption": 203, 
                  "train_weight": 2100,
                  "loadingtime":24, #h
                  "unloadingtime": 24, #h 
                  "uncertainty":1.2, 
                  "fuelprice": 1.20} #€/liter


"Ammonia:"
       
ammonia_train_data = {"name": 'ammoniatrain_1',
                 "type": 'ammoniatrain',
                 "call_size": 3105, #[Abrahamse 2021] ton NH3
                 "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 18_270_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0.003, 
                  "maintenance_perc": 0.015,
                  "crew_min": 2,
                  "crew_for5": 2,
                  "insurance_perc": 0.01,
                  "losses": 0.08, 
                  "utilization":5840, 
                  "avspeed": 45, 
                  "consumption": 203, 
                  "train_weight": 2100,
                  "loadingtime": 24, #h
                  "unloadingtime": 24, #h 
                  "uncertainty":1.2, 
                  "fuelprice": 1.20} #€/liter


"MCH:"


MCH_train_data = {"name": 'MCHtrain_1',
                  "type": 'MCHtrain',
                  "call_size": 3505, #[Abrahamse 2021] ton MCH
                  "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 15_120_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0.003, 
                  "maintenance_perc": 0.015,
                  "crew_min": 2,
                  "crew_for5": 2,
                  "insurance_perc": 0.01,
                  "losses": 0, 
                  "utilization":5840, 
                  "avspeed": 45, 
                  "consumption": 203, 
                  "train_weight": 2300,
                  "loadingtime": 24, #h
                  "unloadingtime": 24, #h 
                  "uncertainty":1.2, 
                  "fuelprice": 1.20} #€/liter

"DBT:"


DBT_train_data = {"name": 'DBTtrain_1',
                  "type": 'DBTtrain',
                  "call_size": 4810, #[Abrahamse 2021] ton MCH
                  "delivery_time": 2, 
                  "lifespan": 20,
                  "unit_rate": 15_120_000, 
                  "mobilisation_min": 0, 
                  "mobilisation_perc":0.003, 
                  "maintenance_perc": 0.015,
                  "crew_min": 2,
                  "crew_for5": 2,
                  "insurance_perc": 0.01,
                  "losses": 0, 
                  "utilization":5840, 
                  "avspeed": 45, 
                  "consumption": 203, 
                  "train_weight": 2300,
                  "loadingtime": 24, #h
                  "unloadingtime": 24, #h 
                  "uncertainty":1.2, 
                  "fuelprice": 1.20} #€/liter


# *** Default inputs: Truck class ***

"Liquid hydrogen"
truck_lh2_data = {"name": 'truck_LH2_01',
                  "type": 'HydrogenTruck',
                  "ownership": 'End use',
                  "delivery_time": 0,
                  "lifespan": 12,
                  "unit_rate": 747_500, #depends on diesel, electric or hydrogen truck --> now hydrogen 
                  "mobilisation_min": 0,
                  "mobilisation_perc": 0.003,
                  "maintenance_perc": 0.015,
                  "crew_min": 1,
                  "crew_for5": 1,
                  "insurance_perc": 0.01,
                  "truck_type": 'truck',
                  "consumption": 0.1, #in L/km for diesel, kWh/km for electric, in kgH2/km for hydrogen --> now hydrogen 
                  "capacity": 3.1, #in ton/hr --> ton H2
                  "utilization": 2400, #h/year 
                  "avspeed": 50, #km/h
                  "loadingtime": 3, #h
                  "unloadingtime": 3, #h 
                  "uncertainty": 1.5, 
                  "losses": 0.3, 
                 "fuelprice":0.40} #in €/km --> now hydrogen 

"Ammonia"
truck_nh3_data = {"name": 'truck_NH3_01',
             "type": 'AmmoniaTruck',
             "ownership": 'End use',
             "delivery_time": 0,
             "lifespan": 12,
             "unit_rate": 560_000, #depends on diesel, electric or hydrogen truck --> now hydrogen 
             "mobilisation_min": 0,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 1,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "truck_type": 'truck',
             "consumption": 0.1,#in L/km for diesel, kWh/km for electric, in kgH2/km for hydrogen --> now hydrogen 
             "capacity": 16.7,   # ton NH3 per trip 
             "utilization": 5840, #h/year 
            "avspeed": 50, #km/h
            "loadingtime": 1.5, #h
            "unloadingtime": 1.5, #h 
            "uncertainty": 1.5, 
                  "losses": 0.08, 
                 "fuelprice":0.40} #in €/km --> now hydrogen 

"MCH"
truck_MCH_data = {"name": 'truck_MCH_01',
             "type": 'MCHTruck',
             "ownership": 'End use',
             "delivery_time": 0,
             "lifespan": 12,
             "unit_rate": 535_000, #depends on diesel, electric or hydrogen truck --> now hydrogen 
             "mobilisation_min": 0,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 1,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "truck_type": 'truck',
             "consumption": 0.1,##in L/km for diesel, kWh/km for electric, in kgH2/km for hydrogen --> now hydrogen 
             "capacity": 34,  #in ton/hr --> ton MCH
             "utilization": 5840, #h/year 
            "avspeed": 50, #km/h
            "loadingtime": 3, #h #doubled because LOHCs need to be loaded on 
            "unloadingtime": 3, #h #doubled because LOHCs need to be loaded on 
            "uncertainty": 1.5, 
                  "losses": 0, 
                 "fuelprice":0.40} #in €/km --> now hydrogen 

"DBT"
truck_DBT_data = {"name": 'truck_DBT_01',
             "type": 'DBTTruck',
             "ownership": 'End use',
             "delivery_time": 0,
             "lifespan": 12,
             "unit_rate": 535_000, #depends on diesel, electric or hydrogen truck --> now hydrogen 
             "mobilisation_min": 0,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 1,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "truck_type": 'truck',
             "consumption": 0.1,##in L/km for diesel, kWh/km for electric, in kgH2/km for hydrogen --> now hydrogen 
             "capacity": 46,  #in ton/hr --> ton MCH
             "utilization": 5840, #h/year 
            "avspeed": 50, #km/h
            "loadingtime": 3, #h #doubled because LOHCs need to be loaded on 
            "unloadingtime": 3, #h #doubled because LOHCs need to be loaded on 
            "uncertainty": 1.5, 
                  "losses": 0, 
                 "fuelprice":0.40} #in €/km --> now hydrogen 

"Gaseous Hydrogen"
truck_CGH2_data = {"name": 'truck_CGH2_01',
             "type": 'CGH2Truck',
             "ownership": 'End use',
             "delivery_time": 0,
             "lifespan": 12,
             "unit_rate": 725_000, #depends on diesel, electric or hydrogen truck --> now hydrogen 
             "mobilisation_min": 0,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 1,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "truck_type": 'truck',
             "consumption": 0.1,##in L/km for diesel, kWh/km for electric, in kgH2/km for hydrogen --> now hydrogen 
             "capacity": 0.86,  #in ton/hr --> ton
            "utilization": 5840, #h/year 
            "avspeed": 50, #km/h
            "loadingtime": 1.5, #h
            "unloadingtime": 1.5, #h 
            "uncertainty": 1.5 , #lies higher for hydrogen trucks because it takes longer to reload 
                   "losses": 0, 
                  "fuelprice":0.40} #in €/km --> now hydrogen 

# *** Default inputs: Pipelines ***

"Gaseous Hydrogen"
pipe_CGH2_data = {"name": 'pipe_CGH2_01',
             "type": 'CGH2Pipe',
             "ownership": 'End use',
             "delivery_time": 3,
             "lifespan": 40,
             "mobilisation_min": 0,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 2,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "pipe_type": 'pipe',
            "utilization": 8760, #h/year 
            "speed": 15, #
            "losses": 0.75, #0.5, 
             "unit_rate_com": 3_400_000,
             "delivery_time_com": 1, 
             "lifespan_com": 20, 
             "crew_min_com": 1, 
             "consumption_com": 0.24, 
              "pressure_com": 100, 
              "capacity_com": 250, 
              "losses_com": 0.5, 
                 "rho": 5.7}

"Ammonia"
pipe_nh3_data = {"name": 'pipe_nh3_01',
             "type": 'nh3Pipe',
             "ownership": 'End use',
             "delivery_time": 3,
             "lifespan": 40,
             "mobilisation_min": 0,
             "mobilisation_perc": 0.003,
             "maintenance_perc": 0.015,
             "crew_min": 2,
             "crew_for5": 1,
             "insurance_perc": 0.01,
             "pipe_type": 'pipe',
            "utilization": 8760, #h/year 
            "speed": 2, #
            "losses": 0.75, #0.5, 
             "unit_rate_com": 3_400_000,#50_000_000, 
             "delivery_time_com": 1, 
             "lifespan_com": 20, 
             "crew_min_com": 1, 
             "consumption_com": 0.24, 
              "pressure_com": 100, 
              "capacity_com": 250, 
              "losses_com": 0.5, 
                "rho": 682}


