"""Basic properties mixins:

- identifiable_properties_mixin
- history_properties_mixin
- hascapex_properties_mixin
- hasopex_properties_mixin
- hasrevenue_properties_mixin
- hastriggers_properties_mixin
- jetty_properties_mixin
- berth_properties_mixin
- cyclic_properties_mixin
- continuous_properties_mixin
- pipeline_properties_mixin
- storage_properties_mixin
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
                 lease=[], demurrage=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.labour = labour
        self.maintenance = maintenance
        self.energy = energy
        self.insurance = insurance
        self.lease = lease
        self.demurrage = demurrage


class hasrevenue_properties_mixin(object):
    """Something has Revenue

    revenue: list with revenues to be applied from investment year"""

    def __init__(self, renevue=[], residual=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.renevue = renevue
        self.residual = residual


class hastriggers_properties_mixin(object):
    """Something has InvestmentTriggers

    triggers: list with revenues to be applied from investment year"""

    def __init__(self, triggers=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialization"""
        self.triggers = triggers


class jetty_properties_mixin(object):
    def __init__(self, ownership, delivery_time, lifespan, mobilisation_min, mobilisation_perc,
                 maintenance_perc, insurance_perc, Gijt_constant_jetty, jettywidth,jettylength, mooring_dolphins, catwalkwidth,catwalklength, Catwalk_rate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.ownership = ownership
        self.delivery_time = delivery_time
        self.lifespan = lifespan
        self.mobilisation_min = mobilisation_min
        self.mobilisation_perc = mobilisation_perc
        self.maintenance_perc = maintenance_perc
        self.insurance_perc = insurance_perc
        self.Gijt_constant_jetty = Gijt_constant_jetty
        self.jettywidth = jettywidth
        self.jettylength = jettylength
        self.mooring_dolphins= mooring_dolphins
        self.catwalkwidth = catwalkwidth
        self.catwalklength = catwalklength
        self.Catwalk_rate=Catwalk_rate



class berth_properties_mixin(object):
    def __init__(self, crane_type, delivery_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.crane_type = crane_type
        self.delivery_time = delivery_time

class pipeline_properties_mixin(object):
    def __init__(self, type, length, ownership, delivery_time, lifespan, unit_rate_factor, mobilisation,
                 maintenance_perc, insurance_perc, consumption_coefficient, crew, utilisation, capacity, losses, *args, **kwargs):
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
        self.consumption_coefficient = consumption_coefficient
        self.crew = crew
        self.utilisation = utilisation
        self.capacity = capacity
        self.losses = losses

class storage_properties_mixin(object):
    def __init__(self, type, ownership, delivery_time, lifespan, unit_rate, mobilisation_min, mobilisation_perc,
                 maintenance_perc, crew_min, crew_for5, insurance_perc, storage_type, consumption, capacity, losses, *args, **kwargs):
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
        self.crew_min = crew_min
        self.crew_for5 = crew_for5
        self.insurance_perc = insurance_perc
        self.storage_type = storage_type
        self.consumption = consumption
        self.capacity = capacity
        self.losses = losses

class h2retrieval_properties_mixin(object):
    def __init__(self, type, ownership, delivery_time, lifespan, unit_rate, mobilisation_min, mobilisation_perc,
                 maintenance_perc, crew_min, crew_for5, insurance_perc, h2retrieval_type, consumption, capacity, losses, *args, **kwargs):
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
        self.crew_min = crew_min
        self.crew_for5 = crew_for5
        self.insurance_perc = insurance_perc
        self.h2retrieval_type = h2retrieval_type
        self.consumption = consumption
        self.capacity = capacity
        self.losses = losses
        
class h2conversion_properties_mixin(object):
    def __init__(self, type, ownership, delivery_time, lifespan, unit_rate, mobilisation_min, mobilisation_perc,
                 maintenance_perc, crew_min, crew_for5, insurance_perc, h2conversion_type, consumption, capacity, losses, recycle_rate, priceH2,  *args, **kwargs):
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
        self.crew_min = crew_min
        self.crew_for5 = crew_for5
        self.insurance_perc = insurance_perc
        self.h2conversion_type = h2conversion_type
        self.consumption = consumption
        self.capacity = capacity
        self.losses = losses
        self.recycle_rate = recycle_rate
        self.priceH2 = priceH2

class commodity_properties_mixin(object):
    def __init__(self, type, handling_fee, Hcontent, material_price, smallhydrogen_perc, largehydrogen_perc, smallammonia_perc, largeammonia_perc,handysize_perc, panamax_perc, vlcc_perc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.type = type
        self.handling_fee = handling_fee
        self.Hcontent = Hcontent 
        self.material_price = material_price
        self.smallhydrogen_perc = smallhydrogen_perc
        self.largehydrogen_perc = largehydrogen_perc
        self.smallammonia_perc = smallammonia_perc
        self.largeammonia_perc = largeammonia_perc
        self.handysize_perc = handysize_perc
        self.panamax_perc = panamax_perc
        self.vlcc_perc = vlcc_perc


class vessel_properties_mixin(object):
    def __init__(self,
                 type, call_size, LOA, draft, beam, max_cranes, all_turn_time, pump_capacity, mooring_time, demurrage_rate,
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
        self.pump_capacity = pump_capacity
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

    def plot_demand(self,  width=0.1, alpha=0.6, fontsize=20):
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

        ax.set_xlabel('Years', fontsize=fontsize)
        ax.set_ylabel('Demand [tons]', fontsize=fontsize)
        ax.set_title('Demand: {}'.format(self.name), fontsize=fontsize)
        ax.set_xticks([x for x in years])
        ax.set_xticklabels([int(x) for x in years], rotation='vertical', fontsize=fontsize)
        ax.yaxis.set_tick_params(labelsize=fontsize)

        # print legend
        fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=5, fontsize=fontsize)
        fig.subplots_adjust(bottom=0.18)

