# package(s) for data handling
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Used for making the graph to visualize our problem
import networkx as nx

# terminal_optimization package
from terminal_optimization.objects import *
from terminal_optimization import defaults


class System:
    def __init__(self, startyear=2019, lifecycle=20, operational_hours=4680, elements=[],
                 crane_type_defaults=defaults.mobile_crane_data):
        # time inputs
        self.startyear = startyear
        self.lifecycle = lifecycle
        self.operational_hours = operational_hours
        self.revenues = []

        # status terminal @ T=startyear
        self.elements = elements
        self.crane_type_defaults = crane_type_defaults

    # *** Simulation engine

    def simulate(self, startyear=2019, lifecycle=20):
        """ Terminal design optimization

        Based on:
        - Ijzermans, W., 2019. Terminal design optimization. Adaptive agribulk terminal planning
          in light of an uncertain future. Master's thesis. Delft University of Technology, Netherlands.
          URL: http://resolver.tudelft.nl/uuid:7ad9be30-7d0a-4ece-a7dc-eb861ae5df24.
        - Van Koningsveld, M. and J. P. M. Mulder. 2004. Sustainable Coastal Policy Developments in the
          Netherlands. A Systematic Approach Revealed. Journal of Coastal Research 20(2), pp. 375-385

        Apply frame of reference style decisions while stepping through each year of the terminal
        lifecycle and check if investment is needed (in light of strategic objective, operational objective,
        QSC, decision recipe, intervention method):
        1. step through investment decisions
        2. collect cash flows
        3. collect revenues
        4. calculate profits
        5. apply WACC to cashflows and revenues
        6. aggregate to NPV

        """
        # todo:
        # 1. step through investment decisions
        for year in range(startyear, startyear + lifecycle):
            """
            strategic objective: create a profitable enterprise (NPV > 0)
            operational objective: provide infrastructure of just sufficient quality
            """
            print('')
            print('Simulate year: {}'.format(year))

            # estimate traffic from commodity scenarios
            handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
            print('  Total vessel calls: {}'.format(total_calls))
            print('     Handysize calls: {}'.format(handysize))
            print('     Handymax calls: {}'.format(handymax))
            print('     Panamax calls: {}'.format(panamax))
            print('  Total cargo volume: {}'.format(total_vol))

            allowable_berth_occupancy = .4  # is 40 %
            self.berth_invest(year, allowable_berth_occupancy, handysize, handymax, panamax)

            self.calculate_revenue(year)
            # NB: quay_conveyor, storage, hinterland_conveyor and unloading_station follow from berth
            # self.conveyor_invest(year, 1000)
            #
            # self.storage_invest(year, 10000)
            #
            # self.conveyor_invest(year, 1000)
            #
            # # self.calculate_train_calls(year)
            # self.unloading_station_invest(year, 1000)

        # 2. collect cash flows

        # 3. collect revenues

        # 4. calculate profits

        # 5. apply WACC to cashflows and revenues

        # 6. aggregate to NPV

    def calculate_revenue(self, year):

        # intialize values to be returned
        revenues = 0

        # gather volumes from each commodity scenario and calculate how much is transported with which vessel
        for commodity in self.find_elements(Commodity):
            volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            fee = commodity.handling_fee

            revenues += (volume * fee)
            print(revenues)

        self.revenues.append(revenues)

    # *** Investment functions

    def berth_invest(self, year, allowable_berth_occupancy, handysize, handymax, panamax):
        """
        Given the overall objectives of the terminal

        Decision recipe Berth:
        QSC: berth_occupancy
        Problem evaluation: there is a problem if the berth_occupancy > allowable_berth_occupancy
            - allowable_berth_occupancy = .40 # 40%
            - a berth needs:
               - a quay
               - cranes (min:1 and max: max_cranes)
            - berth occupancy depends on:
                - total_calls and total_vol
                - total_service_capacity as delivered by the cranes
        Investment decisions: invest enough to make the berth_occupancy < allowable_berth_occupancy
            - adding quay and cranes decreases berth_occupancy_rate
        """

        # report on the status of all berth elements
        berths_online, berths = self.report_element(Berth, year)
        self.report_element(Quay_wall, year)
        self.report_element(Cyclic_Unloader, year)
        self.report_element(Continuous_Unloader, year)
        print('')
        print('  Start analysis:')

        # calculate berth occupancy
        berth_occupancy = self.calculate_berth_occupancy(handysize, handymax, panamax)
        print('     Berth occupancy (@ start of year): {}'.format(berth_occupancy))

        while berth_occupancy > allowable_berth_occupancy:

            # add a berth when no crane slots are available
            if not (self.check_crane_slot_available()):
                print('  *** add Berth to elements')
                berth = Berth(**defaults.berth_data)
                berth.year_online = year + berth.delivery_time
                self.elements.append(berth)

                berth_occupancy = self.calculate_berth_occupancy(handysize, handymax,
                                                                 panamax)
                print('     Berth occupancy (after adding berth): {}'.format(berth_occupancy))

            # check if a quay is needed
            berths = len(self.find_elements(Berth))
            quay_walls = len(self.find_elements(Quay_wall))
            if berths > quay_walls:
                length = max(defaults.handysize_data["LOA"], defaults.handymax_data["LOA"],
                             defaults.panamax_data["LOA"])  # average size
                draft = max(defaults.handysize_data["draft"], defaults.handymax_data["draft"],
                            defaults.panamax_data["draft"])
                # apply PIANC 2014:
                # see Ijzermans, 2019 - infrastructure.py line 107 - 111
                if quay_walls == 0:
                    # - length when next quay is n = 1
                    length = length + 2 * 15
                else:
                    # - length when next quay is n > 1
                    length = length + 15
                #   length = 1.1 * berths *( length + 15)
                # todo: checken of length goed gedefinieerd is

                # - depth
                max_sinkage = 0.5
                wave_motion = 0.5
                safety_margin = 0.5
                depth = np.sum([draft, max_sinkage, wave_motion, safety_margin])
                self.quay_invest(year, length, depth)

                berth_occupancy = self.calculate_berth_occupancy(handysize, handymax, panamax)
                print('     Berth occupancy (after adding quay): {}'.format(berth_occupancy))

            # check if a crane is needed
            if self.check_crane_slot_available():
                self.crane_invest(year)

                berth_occupancy = self.calculate_berth_occupancy(handysize, handymax, panamax)
                print('     Berth occupancy (after adding crane): {}'.format(berth_occupancy))

    def quay_invest(self, year, length, depth):
        """
        *** Decision recipe Quay: ***
        QSC: quay_per_berth
        problem evaluation: there is a problem if the quay_per_berth < 1
        investment decisions: invest enough to make the quay_per_berth = 1
            - adding quay will increase quay_per_berth
            - quay_wall.length must be long enough to accommodate largest expected vessel
            - quay_wall.depth must be deep enough to accommodate largest expected vessel
            - quay_wall.freeboard must be high enough to accommodate largest expected vessel
        """

        print('  *** add Quay to elements')
        quay_wall = Quay_wall(**defaults.quay_wall_data)

        # - capex
        unit_rate = int(
            quay_wall.Gijt_constant * (depth * 2 + quay_wall.freeboard) ** quay_wall.Gijt_coefficient)

        mobilisation = int(max((length * unit_rate * quay_wall.mobilisation_perc), quay_wall.mobilisation_min))
        quay_wall.capex = int(length * unit_rate + mobilisation)

        # unit_rate = int(quay_wall.Gijt_constant * (2* (depth + quay_wall.freeboard)) ** quay_wall.Gijt_coefficient
        # quay_wall.capex = int(unit_rate * (2*(depth + quay_wall.freeboard)+width) * length  + mobilisation)

        # todo: review the formulas

        # - opex
        quay_wall.insurance = quay_wall.capex * quay_wall.insurance_perc
        quay_wall.maintenance = quay_wall.capex * quay_wall.maintenance_perc
        quay_wall.year_online = year + quay_wall.delivery_time

        # add cash flow information to quay_wall object in a dataframe
        quay_wall = self.add_cashflow_data_to_element(quay_wall)

        self.elements.append(quay_wall)

    def crane_invest(self, year):
        """current strategy is to add cranes as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        print('  *** add Harbour crane to elements')
        if (self.crane_type_defaults["crane_type"] == 'Gantry crane' or
                self.crane_type_defaults["crane_type"] == 'Harbour crane' or
                self.crane_type_defaults["crane_type"] == 'Mobile crane'):
            crane = Cyclic_Unloader(**self.crane_type_defaults)
        elif self.crane_type_defaults["crane_type"] == 'Screw unloader':
            crane = Continuous_Unloader(**self.crane_type_defaults)

        # - capex
        # todo: figure out what is meant with delta in this case
        # delta: number of unloaders aquisitioned in current year
        # delta = cranes

        delta = 1
        unit_rate = crane.unit_rate
        mobilisation = delta * unit_rate * crane.mobilisation_perc
        crane.capex = int(delta * unit_rate + mobilisation)

        # - opex
        crane.insurance = crane.capex * crane.insurance_perc
        crane.maintenance = crane.capex * crane.maintenance_perc

        # Occupancy related to the effective capacity. The unloader has also time needed for trimming, cleaning and switching holds.
        # Therefor the capacity decreases, but also the running hours decrease in which in the energy costs decreases.

        occupancy = 0.5  # (effective capacity)
        consumption = crane.consumption
        hours = self.operational_hours * occupancy
        crane.energy = consumption * hours

        labour = Labour(**defaults.labour_data)

        '''old formula --> crane.labour = crane.crew * self.operational_hours / labour.shift_length  '''
        crane.labour = crane.crew * self.operational_hours / (
                labour.shift_length * labour.annual_shifts) * labour.operational_salary

        # apply proper timing for the crane to come online
        years_online = []
        for element in self.find_elements(Quay_wall):
            years_online.append(element.year_online)
        crane.year_online = max([year + crane.delivery_time, max(years_online) - 1 + crane.delivery_time])

        # add cash flow information to quay_wall object in a dataframe
        crane = self.add_cashflow_data_to_element(crane)
        self.elements.append(crane)

        # service_capacity += crane.lifting_capacity * crane.hourly_cycles * crane.eff_fact * self.operational_hours
        #
        # print('a total of {} ton of crane service capacity is online; {} ton total planned'.format(
        #     service_capacity_online,
        #     service_capacity))

    def storage_invest(self, year, storage_trigger):
        """current strategy is to add storage as long as target storage is not yet achieved
        - find out how much storage is online
        - find out how much storage is planned
        - find out how much storage is needed
        - add storage until target is reached
        """

        # from all Quay objects sum online length
        storage = 0
        storage_online = 0
        list_of_elements = self.find_elements(Storage)
        if list_of_elements != []:
            for element in list_of_elements:
                storage += element.capacity
                if year >= element.year_online:
                    storage_online += element.capacity

        print('a total of {} ton of storage capacity is online; {} ton total planned'.format(storage_online, storage))

        # check if total planned length is smaller than target length, if so add a quay
        while storage < storage_trigger:
            print('add Storage to elements')
            silo = Storage(**defaults.silo_data)

            # - capex
            silo.capex = silo.unit_rate * silo.capacity + silo.mobilisation_min

            # - opex
            silo.insurance = silo.capex * silo.insurance_perc
            silo.maintenance = silo.capex * silo.maintenance_perc
            silo.energy = silo.consumption * silo.capacity * self.operational_hours

            occupancy = 0.8  # todo: Figure out occupancy
            consumption = silo.consumption
            capacity = silo.capacity
            hours = self.operational_hours
            silo.energy = consumption * capacity * hours

            silo.year_online = year + silo.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            silo = self.add_cashflow_data_to_element(silo)

            self.elements.append(silo)

            storage += silo.capacity

        print('a total of {} ton of storage capacity is online; {} ton total planned'.format(storage_online, storage))

    def conveyor_invest(self, year, service_capacity_trigger):
        """current strategy is to add conveyors as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        # from all Conveyor objects sum online capacity
        service_capacity = 0
        service_capacity_online = 0
        list_of_elements = self.find_elements(Conveyor)
        if list_of_elements != []:
            for element in list_of_elements:
                service_capacity += element.capacity_steps
                if year >= element.year_online:
                    service_capacity_online += element.capacity_steps
        # todo: understand conveyors capacity formulation

        print('a total of {} ton of conveyor service capacity is online; {} ton total planned'.format(
            service_capacity_online,
            service_capacity))

        # check if total planned length is smaller than target length, if so add a quay
        while service_capacity < service_capacity_trigger:
            print('add Conveyor to elements')
            conveyor = Conveyor(**defaults.quay_conveyor_data)

            # - capex
            delta = conveyor.capacity_steps
            unit_rate = 6.0 * conveyor.length
            mobilisation = conveyor.mobilisation
            conveyor.capex = int(delta * unit_rate + mobilisation)

            # - opex
            conveyor.insurance = conveyor.capex * conveyor.insurance_perc
            conveyor.maintenance = conveyor.capex * conveyor.maintenance_perc
            occupancy = 0.8  # todo: Figure out occupancy
            consumption = conveyor.capacity_steps * conveyor.consumption_coefficient + conveyor.consumption_constant
            hours = self.operational_hours * occupancy
            conveyor.energy = consumption * hours

            conveyor.year_online = year + conveyor.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            conveyor = self.add_cashflow_data_to_element(conveyor)

            self.elements.append(conveyor)

            service_capacity += conveyor.capacity_steps

        print('a total of {} ton of conveyor service capacity is online; {} ton total planned'.format(
            service_capacity_online,
            service_capacity))

    def unloading_station_invest(self, year, service_capacity_trigger):
        """current strategy is to add unloading stations as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        # from all Conveyor objects sum online capacity
        service_capacity = 0
        service_capacity_online = 0
        list_of_elements = self.find_elements(Unloading_station)
        if list_of_elements != []:
            for element in list_of_elements:
                service_capacity += element.production
                if year >= element.year_online:
                    service_capacity_online += element.production
        # todo: understand conveyors capacity formulation

        print('a total of {} ton of conveyor service capacity is online; {} ton total planned'.format(
            service_capacity_online,
            service_capacity))

        # check if total planned length is smaller than target length, if so add a quay
        while service_capacity < service_capacity_trigger:
            print('add Unloading_station to elements')
            hinterland_station = Unloading_station(**defaults.hinterland_station_data)

            # - capex
            delta = hinterland_station.production
            unit_rate = hinterland_station.unit_rate
            mobilisation = hinterland_station.mobilisation
            hinterland_station.capex = int(delta * unit_rate + mobilisation)

            # - opex
            hinterland_station.insurance = hinterland_station.capex * hinterland_station.insurance_perc
            hinterland_station.maintenance = hinterland_station.capex * hinterland_station.maintenance_perc
            hinterland_station.energy = hinterland_station.consumption * hinterland_station.production * self.operational_hours

            hinterland_station.year_online = year + hinterland_station.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            hinterland_station = self.add_cashflow_data_to_element(hinterland_station)

            self.elements.append(hinterland_station)

            service_capacity += hinterland_station.production

        print('a total of {} ton of conveyor service capacity is online; {} ton total planned'.format(
            service_capacity_online,
            service_capacity))

    # *** Financial analyses

    def capex(self):
        pass

    def opex(self):
        pass

    def revenues(self):
        pass

    def profits(self):
        pass

    def terminal_elements_plot(self, width=0.3, alpha=0.6):

        # collect elements to add to plot
        years = []
        berths = []
        cranes = []
        quays = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            berths.append(0)
            quays.append(0)
            cranes.append(0)
            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        berths[-1] += 1
                if isinstance(element, Quay_wall):
                    if year >= element.year_online:
                        quays[-1] += 1
                if isinstance(element, Cyclic_Unloader) | isinstance(element, Continuous_Unloader):
                    if year >= element.year_online:
                        cranes[-1] += 1

        # generate plot
        fig, ax = plt.subplots(figsize=(16, 7))

        ax.bar([x - width for x in years], berths, width=width, alpha=alpha, label="berths", color='pink')
        ax.bar(years, quays, width=width, alpha=alpha, label="quays", color='red')
        ax.bar([x + width for x in years], cranes, width=width, alpha=alpha, label="cranes", color='lightblue')

        ax.set_xlabel('Years')
        ax.set_ylabel('Elements on line [nr]')
        ax.set_title('Terminal elements online ({})'.format(self.crane_type_defaults['crane_type']))
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def cashflow_plot(self, cash_flows, width=0.3, alpha=0.6):

        # todo: extract from self.elements years, revenue, capex and opex
        years = cash_flows['year'].values
        revenue = self.revenues
        capex = cash_flows['capex'].values
        opex = cash_flows['insurance'].values + cash_flows['maintenance'].values + cash_flows['energy'].values + \
               cash_flows['labour'].values

        # generate plot
        fig, ax = plt.subplots(figsize=(16, 7))

        ax.bar([x - width for x in years], revenue, width=width, alpha=alpha, label="revenue", color='pink')
        ax.bar(years, -capex, width=width, alpha=alpha, label="capex", color='red')
        ax.bar([x + width for x in years], -opex, width=width, alpha=alpha, label="opex", color='lightblue')
        ax.set_xlabel('Years')
        ax.set_ylabel('Cashflow [000 M $]')
        ax.set_title('Cash flow plot')
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def WACC_nominal(self, Gearing=60, Re=.10, Rd=.30, Tc=.28):
        """Nominal cash flow is the true dollar amount of future revenues the company expects
        to receive and expenses it expects to pay out, without any adjustments for inflation.
        When all cashflows within the model are denoted in real terms and have been
        adjusted for inflation. The real WACC is computed by as follows:"""

        Gearing = Gearing
        Re = Re  # return on equity
        Rd = Rd  # return on debt
        Tc = Tc  # income tax
        E = 100 - Gearing
        D = Gearing

        WACC_nominal = ((E / (E + D)) * Re + (D / (E + D)) * Rd) * (1 - Tc)

        return WACC_nominal

    def WACC_real(self, interest=0.0604):
        """Real cash flow expresses a company's cash flow with adjustments for inflation.
        When all cashflows within the model are denoted in real terms and have been
        adjusted for inflation, WACC_real should be used. WACC_real is computed by as follows:"""

        WACC_real = (self.WACC_nominal() + 1) / (interest + 1) - 1

        return WACC_real

    def NPV(self):
        pass

    # *** General functions

    def add_cashflow_elements(self):

        cash_flows = pd.DataFrame()

        # initialise cash_flows
        cash_flows['year'] = list(range(self.startyear, self.startyear + self.lifecycle))
        cash_flows['capex'] = 0
        cash_flows['maintenance'] = 0
        cash_flows['insurance'] = 0
        cash_flows['energy'] = 0
        cash_flows['labour'] = 0
        cash_flows['revenues'] = 0

        for element in self.elements:
            if hasattr(element, 'df'):
                for column in cash_flows.columns:
                    if column in element.df.columns and column != "year":
                        cash_flows[column] += element.df[column]

        # cash_flows['revenues'] += self.revenues
        cash_flows.fillna(0)

        return cash_flows

    def add_cashflow_data_to_element(self, element):

        """Place cashflow data in element dataframe"""

        # years
        years = list(range(self.startyear, self.startyear + self.lifecycle))

        # capex
        capex = element.capex

        # opex
        maintenance = element.maintenance
        insurance = element.insurance
        energy = element.energy
        labour = element.labour

        # year online
        year_online = element.year_online
        year_delivery = element.delivery_time

        df = pd.DataFrame()

        # years
        df["year"] = years

        # capex
        if year_delivery > 1:
            df.loc[df["year"] == year_online - 1, "capex"] = 0.6 * capex
            df.loc[df["year"] == year_online, "capex"] = 0.4 * capex
        else:
            df.loc[df["year"] == year_online, "capex"] = capex

        # opex
        if maintenance:
            df.loc[df["year"] > year_online, "maintenance"] = maintenance
        if insurance:
            df.loc[df["year"] > year_online, "insurance"] = insurance
        if energy:
            df.loc[df["year"] > year_online, "energy"] = energy
        if labour:
            df.loc[df["year"] > year_online, "labour"] = labour

        df.fillna(0, inplace=True)

        element.df = df

        return element

    def find_elements(self, obj):
        """return elements of type obj part of self.elements"""

        list_of_elements = []
        if self.elements != []:
            for element in self.elements:
                if isinstance(element, obj):
                    list_of_elements.append(element)

        return list_of_elements

    def calculate_vessel_calls(self, year=2019):
        """Calculate volumes to be transported and the number of vessel calls (both per vessel type and in total) """

        # intialize values to be returned
        handysize_vol = 0
        handymax_vol = 0
        panamax_vol = 0
        total_vol = 0

        # gather volumes from each commodity scenario and calculate how much is transported with which vessel
        commodities = self.find_elements(Commodity)
        for commodity in commodities:
            # todo: check what commodity.utilisation means (Wijnands multiplies by utilisation).
            #  see page 48 of wijnands report
            volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            handysize_vol += volume * commodity.handysize_perc / 100
            handymax_vol += volume * commodity.handymax_perc / 100
            panamax_vol += volume * commodity.panamax_perc / 100
            total_vol += volume

        # gather vessels and calculate the number of calls each vessel type needs to make
        vessels = self.find_elements(Vessel)
        for vessel in vessels:
            if vessel.type == 'Handysize':
                handysize_calls = int(np.ceil(handysize_vol / vessel.call_size))
            elif vessel.type == 'Handymax':
                handymax_calls = int(np.ceil(handymax_vol / vessel.call_size))
            elif vessel.type == 'Panamax':
                panamax_calls = int(np.ceil(panamax_vol / vessel.call_size))
        total_calls = np.sum([handysize_calls, handymax_calls, panamax_calls])

        return handysize_calls, handymax_calls, panamax_calls, total_calls, total_vol

    def calculate_berth_occupancy(self, handysize, handymax, panamax):
        """
        - Find all cranes and sum their effective_capacity to get service_capacity
        - Divide callsize_per_vessel by service_capacity and add mooring time to get total time at berth
        - Occupancy is total_time_at_berth divided by operational hours
        """

        # list all crane objects in system
        list_of_elements_1 = self.find_elements(Cyclic_Unloader)
        list_of_elements_2 = self.find_elements(Continuous_Unloader)
        list_of_elements = list_of_elements_1 + list_of_elements_2

        # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        if list_of_elements != []:
            service_rate = 0
            for element in list_of_elements:
                service_rate += element.effective_capacity

            time_at_berth_handysize = handysize * (
                    (defaults.handysize_data["call_size"] / service_rate) + defaults.handysize_data["mooring_time"])
            time_at_berth_handymax = handymax * (
                    (defaults.handymax_data["call_size"] / service_rate) + defaults.handymax_data["mooring_time"])
            time_at_berth_panamax = panamax * (
                    (defaults.panamax_data["call_size"] / service_rate) + defaults.panamax_data["mooring_time"])

            total_time_at_berth = np.sum([time_at_berth_handysize, time_at_berth_handymax, time_at_berth_panamax])

            # berth_occupancy is the total time at berth devided by the operational hours
            berth_occupancy = total_time_at_berth / self.operational_hours
        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            berth_occupancy = float("inf")

        return berth_occupancy

    def check_crane_slot_available(self):
        list_of_elements = self.find_elements(Berth)
        slots = 0
        for element in list_of_elements:
            slots += element.max_cranes

        list_of_elements_1 = self.find_elements(Cyclic_Unloader)
        list_of_elements_2 = self.find_elements(Continuous_Unloader)
        list_of_elements = list_of_elements_1 + list_of_elements_2

        # when there are more slots than installed cranes ...
        if slots > len(list_of_elements):
            return True
        else:
            return False

    def report_element(self, Element, year):
        elements = 0
        elements_online = 0
        element_name = []
        list_of_elements = self.find_elements(Element)
        if list_of_elements != []:
            for element in list_of_elements:
                element_name = element.name
                elements += 1
                if year >= element.year_online:
                    elements_online += 1

        print('     a total of {} {} is online; {} total planned'.format(elements_online, element_name, elements))

        return elements_online, elements

    def supply_chain(self, nodes, edges):
        """Create a supply chain of example objects:
        the graph contains all available paths the cargo can take to travel through the terminal
        each path needs at least 1 of each of the indicated objects to make a navigable route
        if terminal elements do not make up a graph with a full path through no revenue can be obtained
        """

        # create a graph
        FG = nx.DiGraph()

        labels = {}
        for node in nodes:
            labels[node.name] = (node.name, node.name)
            FG.add_node(node.name, Object=node)

        for edge in edges:
            FG.add_edge(edge[0].name, edge[1].name, weight=1)

        self.supply_graph = FG

        # inspect all paths
        self.supply_chains = list([p for p in nx.all_shortest_paths(FG, nodes[0].name, nodes[-1].name)])

    def plot_system(self):

        nx.draw_kamada_kawai(self.supply_graph, with_labels=True)
