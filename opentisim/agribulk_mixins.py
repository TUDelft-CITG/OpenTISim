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
- continuous_properties_mixin
- conveyor_properties_mixin
- storage_properties_mixin
- unloading_station_properties_mixin
- commodity_properties_mixin
- vessel_properties_mixin
- labour_properties_mixin
- hasscenario_properties_mixin

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
                 lease=[], demurrage=[], residual=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.labour = labour
        self.maintenance = maintenance
        self.energy = energy
        self.insurance = insurance
        self.lease = lease
        self.demurrage = demurrage
        self.residual = residual


class hasrevenue_properties_mixin(object):
    """Something has Revenue

    revenue: list with revenues to be applied from investment year"""

    def __init__(self, renevue=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.renevue = renevue


class hastriggers_properties_mixin(object):
    """Something has InvestmentTriggers

    triggers: list with revenues to be applied from investment year"""

    def __init__(self, triggers=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.triggers = triggers


class quay_wall_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, mobilisation_min, mobilisation_perc,
                 maintenance_perc, insurance_perc, freeboard, Gijt_constant_2, Gijt_constant, Gijt_coefficient, max_sinkage, wave_motion,
                 safety_margin, *args, **kwargs):
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
        self.Gijt_constant_2 = Gijt_constant_2
        self.Gijt_constant = Gijt_constant
        self.Gijt_coefficient = Gijt_coefficient
        self.max_sinkage = max_sinkage
        self.wave_motion = wave_motion
        self.safety_margin= safety_margin

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
        self.eff_fact = eff_fact
        self.payload = int(self.lifting_capacity * 0.7)  # Source: Nemag ((lifting_capacity - 2.4) / 1.4)
        self.peak_capacity = int(self.payload * self.hourly_cycles)
        self.effective_capacity = int(eff_fact * self.peak_capacity)  # Source: TATA steel


class continuous_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, unit_rate, mobilisation_perc, maintenance_perc,
                 consumption, insurance_perc, crew, crane_type, peak_capacity, eff_fact, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.unit_rate = unit_rate
        self.mobilisation_perc = mobilisation_perc
        self.mobilisation = int(mobilisation_perc * unit_rate)
        self.maintenance_perc = maintenance_perc
        self.consumption = consumption
        self.insurance_perc = insurance_perc
        self.crew = crew
        self.crane_type = crane_type
        self.peak_capacity = peak_capacity
        self.eff_fact = eff_fact
        self.effective_capacity = eff_fact * peak_capacity


class conveyor_properties_mixin(object):
    def __init__(self, type, length, ownership, delivery_time, lifespan, unit_rate_factor, mobilisation,
                 maintenance_perc, insurance_perc,
                 consumption_constant, consumption_coefficient, crew, utilisation, capacity_steps, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.length = length
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.unit_rate_factor = unit_rate_factor
        self.mobilisation = mobilisation
        self.maintenance_perc = maintenance_perc
        self.insurance_perc = insurance_perc
        self.consumption_constant = consumption_constant
        self.consumption_coefficient = consumption_coefficient
        self.crew = crew
        self.utilisation = utilisation
        self.capacity_steps = capacity_steps


class storage_properties_mixin(object):
    def __init__(self, type, ownership, delivery_time, lifespan, unit_rate, mobilisation_min, mobilisation_perc,
                 maintenance_perc, crew, insurance_perc, storage_type, consumption, capacity,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.unit_rate = unit_rate
        self.mobilisation_min = mobilisation_min
        self.mobilisation_perc = mobilisation_perc
        self.maintenance_perc = maintenance_perc
        self.crew = crew
        self.insurance_perc = insurance_perc
        self.storage_type = storage_type
        self.consumption = consumption
        self.capacity = capacity


class unloading_station_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, unit_rate, mobilisation, maintenance_perc,
                 insurance_perc, consumption, crew, production, wagon_payload, number_of_wagons, prep_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.unit_rate = unit_rate
        self.mobilisation = mobilisation
        self.maintenance_perc = maintenance_perc
        self.insurance_perc = insurance_perc
        self.consumption = consumption
        self.crew = crew
        self.production = production
        self.wagon_payload = wagon_payload
        self.number_of_wagons = number_of_wagons
        self.prep_time = prep_time
        self.call_size = int(self.wagon_payload * self.number_of_wagons)
        self.service_rate = int(self.call_size / (self.call_size/self.production + self.prep_time)) #TUE/hour, IJzermans 2019, P30

class commodity_properties_mixin(object):
    def __init__(self, handling_fee, handysize_perc, handymax_perc, panamax_perc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.handling_fee = handling_fee
        self.handysize_perc = handysize_perc
        self.handymax_perc = handymax_perc
        self.panamax_perc = panamax_perc


class vessel_properties_mixin(object):
    def __init__(self,
                 type, call_size, LOA, draft, beam, max_cranes, all_turn_time, mooring_time, demurrage_rate,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.call_size = call_size
        self.LOA = LOA
        self.draft = draft
        self.beam = beam
        self.max_cranes = max_cranes
        self.all_turn_time = all_turn_time
        self.mooring_time = mooring_time
        self.demurrage_rate = demurrage_rate


class labour_properties_mixin(object):
    def __init__(self, international_salary, international_staff, local_salary, local_staff, operational_salary,
                 shift_length, annual_shifts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.international_salary = international_salary
        self.international_staff = international_staff
        self.local_salary = local_salary
        self.local_staff = local_staff
        self.operational_salary = operational_salary
        self.shift_length = shift_length
        self.annual_shifts = annual_shifts


class energy_properties_mixin(object):
    def __init__(self, price, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = price

class train_properties_mixin(object):
    def __init__(self, wagon_payload, number_of_wagons, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.wagon_payload = wagon_payload
        self.number_of_wagons = number_of_wagons
        self.prep_time = 2
        self.call_size = wagon_payload * number_of_wagons
        self.call_log = []

class hasscenario_properties_mixin(object):
    """Something has a scenario

    historic_data: observed demand
    scenario_data: generated estimates of future demand"""

    def __init__(self, historic_data=[], scenario_data=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.historic_data = historic_data
        self.scenario_data = scenario_data

    def scenario_random(self, startyear=2019, lifecycle=20, rate=1.02, mu=0.01, sigma=0.065):
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

    def plot_demand(self, width=0.1, alpha=0.6):
        """generate a histogram of the demand data"""
        # generate plot
        fig, ax = plt.subplots(figsize=(20, 10))

        years = np.array([])

        try:
            ax.bar([x + 0 * width for x in self.historic_data['year'].values], self.historic_data['volume'].values,
                   width=width, alpha=alpha, label="historic data", color='blue', edgecolor='blue')
            years = self.historic_data['year'].values
        except:
            pass

        ax.bar([x + 0 * width for x in self.scenario_data['year'].values], self.scenario_data['volume'].values,
               width=width, alpha=alpha, label="scenario data", color='red', edgecolor='red')

        years = np.concatenate((years, self.scenario_data['year'].values))

        ax.set_xlabel('Years')
        ax.set_ylabel('Demand [tons]')
        ax.set_title('Demand: {}'.format(self.name))
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()
