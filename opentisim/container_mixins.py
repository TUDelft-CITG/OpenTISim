"""Basic properties mixins:

- identifiable_properties_mixin
- history_properties_mixin
- hascapex_properties_mixin
- hasopex_properties_mixin
- hasrevenue_properties_mixin
- hastriggers_properties_mixin
- quay_wall_properties_mixin
- berth_properties_mixin
- cyclic_properties_mixin
- transport_properties_mixin
- container_properties_mixin
- laden_stack_properties_mixin
- empty_stack_properties_mixin
- oog_stack_properties_mixin
- stack_equipment_properties_mixin
- gate_properties_mixin
- empty_handler_properties_mixin
- commodity_properties_mixin
- vessel_properties_mixin
- labour_properties_mixin
- hasscenario_properties_mixin
- general_services_mixin
- indirect_costs_mixin
- land_price_mixin

"""

# package for unique identifiers
import uuid

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


class identifiable_properties_mixin(object):
    """Something that has a name and id

    name: a name
    id: a unique id generated with uuid"""

    def __init__(self, name=[], id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.name = name
        # generate some id, in this case based on m
        self.id = id if id else str(uuid.uuid1())


class history_properties_mixin(object):
    """Something that has a purchase history

    purchase_date: year in which the decision was made to add another element
    online_date: year by which the elements starts to perform"""

    def __init__(self, year_purchase=[], year_online=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.year_purchase = year_purchase
        self.year_online = year_online


class hascapex_properties_mixin(object):
    """Something has CAPEX

    capex: list with cost to be applied from investment year"""

    def __init__(self, capex=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.capex = capex


class hasopex_properties_mixin(object):
    """Something has OPEX

    opex: list with cost to be applied from investment year"""

    def __init__(self, labour=[], maintenance=[], energy=[], insurance=[],
                 lease=[], demurrage=[], residual=[], fuel=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.labour = labour
        self.maintenance = maintenance
        self.energy = energy
        self.insurance = insurance
        self.lease = lease
        self.demurrage = demurrage
        self.residual = residual
        self.fuel = fuel


class hasrevenue_properties_mixin(object):
    """Something has Revenue

    revenue: list with revenues to be applied from investment year"""

    def __init__(self, renevue=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.renevue = renevue


class hasland_properties_mixin(object):
    """Something has land use [m^2]

    land_use: list with land use to be applied from investment year"""

    def __init__(self, land_use=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.land_use = land_use


class hastriggers_properties_mixin(object):
    """Something has InvestmentTriggers

    triggers: list with revenues to be applied from investment year"""

    def __init__(self, triggers=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.triggers = triggers


class quay_wall_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, mobilisation_min, mobilisation_perc,
                 maintenance_perc, insurance_perc, freeboard, Gijt_constant, Gijt_coefficient, max_sinkage, wave_motion,
                 safety_margin, apron_width, apron_pavement, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.mobilisation_min = mobilisation_min
        self.mobilisation_perc = mobilisation_perc
        self.maintenance_perc = maintenance_perc
        self.insurance_perc = insurance_perc
        self.freeboard = freeboard
        self.Gijt_constant = Gijt_constant
        self.Gijt_coefficient = Gijt_coefficient
        self.max_sinkage = max_sinkage
        self.wave_motion = wave_motion
        self.safety_margin = safety_margin
        self.apron_width = apron_width
        self.apron_pavement = apron_pavement


class berth_properties_mixin(object):
    def __init__(self, crane_type, max_cranes, delivery_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.crane_type = crane_type
        self.max_cranes = max_cranes
        self.delivery_time = delivery_time


class cyclic_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, unit_rate, mobilisation_perc, maintenance_perc,
                 consumption, insurance_perc, crew, crane_type, lifting_capacity, hourly_cycles, eff_fact,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.unit_rate = unit_rate
        self.mobilisation_perc = mobilisation_perc
        self.maintenance_perc = maintenance_perc
        self.consumption = consumption
        self.insurance_perc = insurance_perc
        self.crew = crew
        self.crane_type = crane_type
        self.lifting_capacity = lifting_capacity
        self.hourly_cycles = hourly_cycles
        self.eff_fact = eff_fact  # effectiveness factor
        self.payload = self.lifting_capacity * 1.0  # for lashing
        self.peak_capacity = self.payload * self.hourly_cycles
        self.effective_capacity = int(eff_fact * self.peak_capacity) # TEU/hr


class transport_properties_mixin(object):
    def __init__(self, type, ownership, delivery_time, lifespan, unit_rate, mobilisation,
                 maintenance_perc, insurance_perc,
                 crew, salary, utilisation, fuel_consumption, productivity, required, non_essential_moves, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.unit_rate = unit_rate
        self.mobilisation = mobilisation
        self.maintenance_perc = maintenance_perc
        self.insurance_perc = insurance_perc
        self.crew = crew
        self.salary = salary
        self.utilisation = utilisation
        self.fuel_consumption = fuel_consumption
        self.productivity = productivity
        self.required = required
        self.non_essential_moves = non_essential_moves


class container_properties_mixin(object):
    def __init__(self, type, teu_factor, dwell_time, peak_factor, stack_occupancy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.teu_factor = teu_factor
        self.dwell_time = dwell_time
        self.peak_factor = peak_factor
        self.stack_occupancy = stack_occupancy


class laden_stack_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, mobilisation, maintenance_perc, width, height,
                 length, capacity, gross_tgs, area_factor, pavement, drainage, household, digout_margin,
                 reefer_factor, consumption, reefer_rack, reefers_present, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.mobilisation = mobilisation
        self.maintenance_perc = maintenance_perc
        self.width = width
        self.height = height
        self.length = length
        self.capacity = capacity
        self.gross_tgs = gross_tgs
        self.area_factor = area_factor
        self.pavement = pavement
        self.drainage = drainage
        self.household = household
        self.digout_margin = digout_margin
        self.reefer_factor = reefer_factor
        self.consumption = consumption
        self.reefer_rack = reefer_rack
        self.reefers_present = reefers_present


class empty_stack_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, mobilisation, maintenance_perc, width, height,
                 length, capacity, gross_tgs, area_factor, pavement, drainage, household, digout, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.mobilisation = mobilisation
        self.maintenance_perc = maintenance_perc
        self.width = width
        self.height = height
        self.length = length
        self.capacity = capacity
        self.gross_tgs = gross_tgs
        self.area_factor = area_factor
        self.pavement = pavement
        self.drainage = drainage
        self.household = household
        self.digout = digout


class oog_stack_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, mobilisation, maintenance_perc, width, height,
                 length, capacity, gross_tgs, area_factor, pavement, drainage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.mobilisation = mobilisation
        self.maintenance_perc = maintenance_perc
        self.width = width
        self.height = height
        self.length = length
        self.capacity = capacity
        self.gross_tgs = gross_tgs
        self.area_factor = area_factor
        self.pavement = pavement
        self.drainage = drainage


class stack_equipment_properties_mixin(object):
    def __init__(self, type, ownership, delivery_time, lifespan, unit_rate, mobilisation, maintenance_perc, insurance_perc, crew,
                 salary, required, fuel_consumption, power_consumption, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.unit_rate = unit_rate
        self.mobilisation = mobilisation
        self.maintenance_perc = maintenance_perc
        self.insurance_perc = insurance_perc
        self.crew = crew
        self.salary = salary
        self.required = required
        self.fuel_consumption = fuel_consumption
        self.power_consumption = power_consumption


class gate_properties_mixin(object):
    def __init__(self, type, ownership, delivery_time, lifespan, unit_rate, mobilisation, maintenance_perc, crew,
                 salary, canopy_costs, area, staff_gates, service_gates, design_capacity, exit_inspection_time, entry_inspection_time,
                 peak_hour, peak_day, peak_factor, truck_moves, operating_days, capacity, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.unit_rate = unit_rate
        self.mobilisation = mobilisation
        self.maintenance_perc = maintenance_perc
        self.crew = crew
        self.salary = salary
        self.canopy_costs = canopy_costs
        self.area = area
        self.staff_gates = staff_gates
        self.service_gates = service_gates
        self.design_capacity = design_capacity
        self.exit_inspection_time = exit_inspection_time
        self.entry_inspection_time = entry_inspection_time
        self.peak_hour = peak_hour
        self.peak_day = peak_day
        self.peak_factor = peak_factor
        self.truck_moves = truck_moves
        self.operating_days = operating_days
        self.capacity = capacity


class empty_handler_properties_mixin(object):
    def __init__(self, type, ownership, delivery_time, lifespan, unit_rate, mobilisation,
                 maintenance_perc, crew, salary, fuel_consumption, required, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.unit_rate = unit_rate
        self.mobilisation = mobilisation
        self.maintenance_perc = maintenance_perc
        self.crew = crew
        self.salary = salary
        self.fuel_consumption = fuel_consumption
        self.required = required


class commodity_properties_mixin(object):
    def __init__(self, handling_fee, fully_cellular_perc, panamax_perc, panamax_max_perc, post_panamax_I_perc,
                 post_panamax_II_perc, new_panamax_perc, VLCS_perc, ULCS_perc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.handling_fee = handling_fee
        self.fully_cellular_perc = fully_cellular_perc
        self.panamax_perc = panamax_perc
        self.panamax_max_perc = panamax_max_perc
        self.post_panamax_I_perc = post_panamax_I_perc
        self.post_panamax_II_perc = post_panamax_II_perc
        self.new_panamax_perc = new_panamax_perc
        self.VLCS_perc = VLCS_perc
        self.ULCS_perc = ULCS_perc


class vessel_properties_mixin(object):
    def __init__(self,
                 type, call_size, LOA, draught, beam, max_cranes, all_turn_time,
                 mooring_time, demurrage_rate, starting_fee, variable_fee, avg_overseas_distance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.call_size = call_size
        self.LOA = LOA
        self.draught = draught
        self.beam = beam
        self.max_cranes = max_cranes
        self.all_turn_time = all_turn_time
        self.mooring_time = mooring_time
        self.demurrage_rate = demurrage_rate
        self.starting_fee = starting_fee
        self.variable_fee = variable_fee
        self.avg_overseas_distance = avg_overseas_distance


class labour_properties_mixin(object):
    def __init__(self, international_salary, international_staff, local_salary, local_staff, operational_salary,
                 shift_length, annual_shifts, daily_shifts, blue_collar_salary, white_collar_salary, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.international_salary = international_salary
        self.international_staff = international_staff
        self.local_salary = local_salary
        self.local_staff = local_staff
        self.operational_salary = operational_salary
        self.shift_length = shift_length
        self.annual_shifts = annual_shifts
        self.daily_shifts = daily_shifts
        self.blue_collar_salary = blue_collar_salary
        self.white_collar_salary = white_collar_salary


class energy_properties_mixin(object):
    def __init__(self, price, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = price


class hasscenario_properties_mixin(object):
    """Something has a scenario

    historic_data: observed demand
    scenario_data: generated estimates of future demand"""

    def __init__(self, historic_data=[], scenario_data=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.historic_data = historic_data
        self.scenario_data = scenario_data

    def scenario_random(self, startyear=2020, lifecycle=20, rate=1.02, mu=0.01, sigma=0.065):
        """trend generated from random growth rate increments"""
        # package(s) used for probability
        years = range(startyear, startyear + lifecycle)
        volume = self.historic_data[self.historic_data.year == startyear - 1].volume.item()

        volumes = []
        for year in years:
            change = np.random.normal(mu, sigma, 1)
            new_rate = rate + change
            volume = volume * new_rate
            volumes.append(np.int(volume))

        scenario_data = {'year': years, 'volume': volumes}

        self.scenario_data = pd.DataFrame(data=scenario_data)

    def plot_demand(self):
        plt.figure(figsize=(10, 7.5))

        try:
            plt.plot(self.historic_data['year'], self.historic_data['volume'], 'o:r')
        except:
            pass
        plt.plot(self.scenario_data['year'], self.scenario_data['volume'], 'o:b')
        plt.xlabel('Time [years]')
        plt.ylabel('Demand ' + self.name + ' [TEU]')
        plt.title('Demand ' + self.name)


class general_services_mixin(object):
    def __init__(self,
                 type, office, office_cost, workshop, workshop_cost, fuel_station_cost, scanning_inspection_area,
                 scanning_inspection_area_cost, lighting_mast_required, lighting_mast_cost, firefight_cost,
                 maintenance_tools_cost, terminal_operating_software_cost, electrical_station_cost, repair_building, repair_building_cost,
                 ceo, secretary, administration, hr, commercial, operations, engineering, security, general_maintenance,
                 crew_required, delivery_time, lighting_consumption, general_consumption, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.office = office
        self.office_cost = office_cost
        self.workshop = workshop
        self.workshop_cost = workshop_cost
        self.fuel_station_cost = fuel_station_cost
        self.scanning_inspection_area = scanning_inspection_area
        self.scanning_inspection_area_cost = scanning_inspection_area_cost
        self.lighting_mast_required = lighting_mast_required
        self.lighting_mast_cost = lighting_mast_cost
        self.firefight_cost = firefight_cost
        self.maintenance_tools_cost = maintenance_tools_cost
        self.terminal_operating_software_cost = terminal_operating_software_cost
        self.electrical_station_cost = electrical_station_cost
        self.repair_building = repair_building
        self.repair_building_cost = repair_building_cost
        self.ceo = ceo
        self.secretary = secretary
        self.administration = administration
        self.hr = hr
        self.commercial = commercial
        self.operations = operations
        self.engineering = engineering
        self.security = security
        self.general_maintenance = general_maintenance
        self.crew_required = crew_required
        self.delivery_time = delivery_time
        self.lighting_consumption = lighting_consumption
        self.general_consumption = general_consumption


class indirect_costs_mixin(object):
    def __init__(self, preliminaries, engineering, miscellaneous, electrical_works_fuel_terminal,
                 electrical_works_power_terminal, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.preliminaries = preliminaries
        self.engineering = engineering
        self.miscellaneous = miscellaneous
        self.electrical_works_fuel_terminal = electrical_works_fuel_terminal
        self.electrical_works_power_terminal = electrical_works_power_terminal


class land_price_mixin(object):
    def __init__(self, price, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = price
