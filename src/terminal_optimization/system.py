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
    def __init__(self, startyear=2019, lifecycle=20, operational_hours=4680, debug=False, elements=[],
                 crane_type_defaults=defaults.mobile_crane_data, storage_type_defaults=defaults.silo_data):
        # time inputs
        self.startyear = startyear
        self.lifecycle = lifecycle
        self.operational_hours = operational_hours
        self.debug = debug
        # status terminal @ T=startyear
        self.elements = elements

        # default values for crane type to use
        self.crane_type_defaults = crane_type_defaults
        self.storage_type_defaults = storage_type_defaults

        # storage variables for revenue
        self.revenues = []

    # *** Simulation engine

    def simulate(self):
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

        # before the start of each simulation set revenues to []
        self.revenues = []

        # 1. step through investment decisions
        for year in range(self.startyear, self.startyear + self.lifecycle):
            """
            strategic objective: create a profitable enterprise (NPV > 0)
            operational objective: provide infrastructure of just sufficient quality
            """

            if self.debug:
                print('')
                print('Simulate year: {}'.format(year))

            # estimate traffic from commodity scenarios
            handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
            if self.debug:
                print('  Total vessel calls: {}'.format(total_calls))
                print('     Handysize calls: {}'.format(handysize))
                print('     Handymax calls: {}'.format(handymax))
                print('     Panamax calls: {}'.format(panamax))
                print('  Total cargo volume: {}'.format(total_vol))

            allowable_berth_occupancy = .4  # is 40 %
            self.berth_invest(year, allowable_berth_occupancy, handysize, handymax, panamax)

            self.calculate_revenue(year)
            # NB: quay_conveyor, storage, hinterland_conveyor and unloading_station follow from berth
            self.conveyor_quay_invest(year, defaults.quay_conveyor_data)
            #
            self.storage_invest(year, self.storage_type_defaults)
            #
            self.conveyor_hinter_invest(year, defaults.hinterland_conveyor_data)

            self.unloading_station_invest(year)
            #
            # # self.calculate_train_calls(year)

        # 2. collect cash flows

        # 3. collect revenues

        # 4. calculate profits

        # 5. apply WACC to cashflows and revenues

        # 6. aggregate to NPV

    def calculate_revenue(self, year):
        """
        1. calculate the value of the total demand in year (demand * handling fee)
        2. calculate the maximum amount that can be handled (service capacity * operational hours)
        Terminal.revenues is the minimum of 1. and 2.
        """

        # gather volumes from each commodity, calculate how much revenue it would yield, and add
        revenues = 0
        for commodity in self.find_elements(Commodity):
            fee = commodity.handling_fee
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                revenues += (volume * fee)
            except:
                pass
        if self.debug:
            print('     Revenues (demand): {}'.format(revenues))

        handysize_calls, handymax_calls, panamax_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
            year, handysize_calls,
            handymax_calls,
            panamax_calls)

        # find the total service rate,
        service_rate = 0
        for element in (self.find_elements(Cyclic_Unloader) + self.find_elements(Continuous_Unloader)):
            if year >= element.year_online:
                service_rate += element.effective_capacity * crane_occupancy_online

        if self.debug:
            print('     Revenues (throughput): {}'.format(int(service_rate * self.operational_hours * fee)))

        try:
            self.revenues.append(min(revenues, service_rate * self.operational_hours * fee))
        except:
            pass

        # todo: now one fee is used for all commodities. This still needs attention

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
        self.report_element(Conveyor_Quay, year)
        self.report_element(Storage, year)
        self.report_element(Conveyor_Hinter, year)
        self.report_element(Unloading_station, year)
        if self.debug:
            print('')
            print('  Start analysis:')

        # calculate berth occupancy
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
            year, handysize, handymax, panamax)
        if self.debug:
            print('     Berth occupancy planned (@ start of year): {}'.format(berth_occupancy_planned))
            print('     Berth occupancy online (@ start of year): {}'.format(berth_occupancy_online))

        while berth_occupancy_planned > allowable_berth_occupancy:

            # add a berth when no crane slots are available
            if not (self.check_crane_slot_available()):
                if self.debug:
                    print('  *** add Berth to elements')
                berth = Berth(**defaults.berth_data)
                berth.year_online = year + berth.delivery_time
                self.elements.append(berth)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, handysize, handymax, panamax)
                if self.debug:
                    print('     Berth occupancy planned (after adding berth): {}'.format(berth_occupancy_planned))
                    print('     Berth occupancy online (after adding berth): {}'.format(berth_occupancy_online))

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
                # todo: these are hard coded values, consider to move to vessel defaults
                depth = np.sum([draft, max_sinkage, wave_motion, safety_margin])
                self.quay_invest(year, length, depth)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, handysize,
                    handymax, panamax)
                if self.debug:
                    print('     Berth occupancy planned (after adding quay): {}'.format(berth_occupancy_planned))
                    print('     Berth occupancy online (after adding quay): {}'.format(berth_occupancy_online))

            # check if a crane is needed
            if self.check_crane_slot_available():
                self.crane_invest(year, berth_occupancy_online)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, handysize,
                    handymax, panamax)
                if self.debug:
                    print('     Berth occupancy planned (after adding crane): {}'.format(berth_occupancy_planned))
                    print('     Berth occupancy online (after adding crane): {}'.format(berth_occupancy_online))
                    print('     Crane occupancy planned (after adding crane): {}'.format(crane_occupancy_planned))
                    print('     Crane occupancy online (after adding crane): {}'.format(crane_occupancy_online))

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

        if self.debug:
            print('  *** add Quay to elements')
        # add a Quay_wall element

        quay_wall = Quay_wall(**defaults.quay_wall_data)

        # - capex
        unit_rate = int(
            quay_wall.Gijt_constant * (depth * 2 + quay_wall.freeboard) ** quay_wall.Gijt_coefficient)
        mobilisation = int(max((length * unit_rate * quay_wall.mobilisation_perc), quay_wall.mobilisation_min))
        quay_wall.capex = int(length * unit_rate + mobilisation)

        # todo: review the formulas

        # - opex
        quay_wall.insurance = quay_wall.capex * quay_wall.insurance_perc
        quay_wall.maintenance = quay_wall.capex * quay_wall.maintenance_perc
        quay_wall.year_online = year + quay_wall.delivery_time

        # add cash flow information to quay_wall object in a dataframe
        quay_wall = self.add_cashflow_data_to_element(quay_wall)

        self.elements.append(quay_wall)

    def crane_invest(self, year, berth_occupancy_online):
        """current strategy is to add cranes as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """
        if self.debug:
            print('  *** add Harbour crane to elements')
        # add unloader object
        if (self.crane_type_defaults["crane_type"] == 'Gantry crane' or
                self.crane_type_defaults["crane_type"] == 'Harbour crane' or
                self.crane_type_defaults["crane_type"] == 'Mobile crane'):
            crane = Cyclic_Unloader(**self.crane_type_defaults)
        elif self.crane_type_defaults["crane_type"] == 'Screw unloader':
            crane = Continuous_Unloader(**self.crane_type_defaults)

        # - capex
        unit_rate = crane.unit_rate
        mobilisation = unit_rate * crane.mobilisation_perc
        crane.capex = int(unit_rate + mobilisation)

        # - opex
        crane.insurance = crane.capex * crane.insurance_perc
        crane.maintenance = crane.capex * crane.maintenance_perc

        # Occupancy related to the effective capacity. The unloader has also time needed for trimming,
        # cleaning and switching holds. Therefore the capacity decreases, but also the running hours decrease
        # in which case the energy costs decreases.

        #   energy
        energy = Energy(**defaults.energy_data)
        handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
            year, handysize, handymax, panamax)

        # this is needed because at greenfield startup occupancy is still inf
        if berth_occupancy_online == np.inf:
            berth_occupancy_online = 0.4
            crane_occupancy_online = 0.4

        consumption = crane.consumption
        hours = self.operational_hours * crane_occupancy_online
        crane.energy = consumption * hours * energy.price
        # todo: the energy costs needs to be calculated every year and not only in year 1 and than take this number for the
        #  whole period (that is what at the moment happens)

        #   labour
        labour = Labour(**defaults.labour_data)
        '''old formula --> crane.labour = crane.crew * self.operational_hours / labour.shift_length  '''
        crane.shift = ((crane.crew * self.operational_hours) / (
                labour.shift_length * labour.annual_shifts))
        crane.labour = crane.shift * labour.operational_salary

        # apply proper timing for the crane to come online (in the same year as the latest Quay_wall)
        years_online = []
        for element in self.find_elements(Quay_wall):
            years_online.append(element.year_online)
        crane.year_online = max([year + crane.delivery_time, max(years_online) - 1 + crane.delivery_time])

        # add cash flow information to quay_wall object in a dataframe
        crane = self.add_cashflow_data_to_element(crane)

        # add object to elements
        self.elements.append(crane)

    def conveyor_quay_invest(self, year, defaults_quay_conveyor_data):
        """current strategy is to add conveyors as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        # list all crane objects in system
        list_of_elements_1 = self.find_elements(Cyclic_Unloader)
        list_of_elements_2 = self.find_elements(Continuous_Unloader)
        list_of_elements_Crane = list_of_elements_1 + list_of_elements_2

        # find the total service rate
        if list_of_elements_Crane != []:
            service_peakcapacity_cranes = 0
            for element in list_of_elements_Crane:
                service_peakcapacity_cranes += element.peak_capacity

        # list all conveyor objects in system
        list_of_elements = self.find_elements(Conveyor_Quay)

        # find the total service rate
        service_capacity = 0
        service_capacity_online = 0
        if list_of_elements != []:
            for element in list_of_elements:
                if element.type == defaults_quay_conveyor_data['type']:
                    service_capacity += element.capacity_steps
                    if year >= element.year_online:
                        service_capacity_online += element.capacity_steps

        if self.debug:
            print('     a total of {} ton of {} conveyor service capacity is online; {} ton total planned'.format(
                service_capacity_online,
                defaults_quay_conveyor_data['type'],
                service_capacity))

        # check if total planned length is smaller than target length, if so add a quay
        while service_capacity < service_peakcapacity_cranes:
            # todo: this way conveyors are added until conveyor service capacity is at least the crane capacity
            if self.debug:
                print('  *** add Conveyor to elements')
            conveyor = Conveyor_Quay(**defaults_quay_conveyor_data)

            # - capex
            capacity = conveyor.capacity_steps
            unit_rate = conveyor.unit_rate_factor * conveyor.length
            mobilisation = conveyor.mobilisation
            conveyor.capex = int(capacity * unit_rate + mobilisation)

            # - opex
            conveyor.insurance = conveyor.capex * conveyor.insurance_perc
            conveyor.maintenance = conveyor.capex * conveyor.maintenance_perc

            #   energy
            energy = Energy(**defaults.energy_data)
            handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
            berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                year, handysize, handymax,
                panamax)

            # this is needed because at greenfield startup occupancy is still inf
            if berth_occupancy_online == np.inf:
                berth_occupancy_online = 0.4
            # todo: the berht occupancy is not yet well defined (it does not calculate every year a new berth occupancy)

            consumption = conveyor.capacity_steps * conveyor.consumption_coefficient + conveyor.consumption_constant
            hours = self.operational_hours * berth_occupancy_online
            conveyor.energy = consumption * hours * energy.price

            # year online

            years_online = []
            for element in list_of_elements_Crane:
                years_online.append(element.year_online)
            conveyor.year_online = element.year_online - 1 + conveyor.delivery_time
            # todo: the year_online is not yet complete, it does not follow directly the movements of the cranes

            # add cash flow information to quay_wall object in a dataframe
            conveyor.quay = self.add_cashflow_data_to_element(conveyor)

            self.elements.append(conveyor.quay)

            service_capacity += conveyor.capacity_steps

        if self.debug:
            print('     a total of {} ton of conveyor quay service capacity is online; {} ton total planned'.format(
                service_capacity_online,
                service_capacity))

    def storage_invest(self, year, defaults_storage_data):
        """current strategy is to add storage as long as target storage is not yet achieved
        - find out how much storage is online
        - find out how much storage is planned
        - find out how much storage is needed
        - add storage until target is reached
        """

        # from all Conveyor objects sum online capacity
        storage_capacity = 0
        storage_capacity_online = 0
        list_of_elements = self.find_elements(Storage)
        if list_of_elements != []:
            for element in list_of_elements:
                if element.type == defaults_storage_data['type']:
                    storage_capacity += element.capacity
                    if year >= element.year_online:
                        storage_capacity_online += element.capacity

        if self.debug:
            print('     a total of {} ton of {} storage capacity is online; {} ton total planned'.format(
                storage_capacity_online,
                defaults_storage_data['type'],
                storage_capacity))

        handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)

        max_vessel_call_size = max([x.call_size for x in self.find_elements(Vessel)])
        storage_capacity_dwelltime = (total_vol * 0.05) * 1.1

        # check if sufficient storage capacity is available
        while storage_capacity < max_vessel_call_size or storage_capacity < storage_capacity_dwelltime:
            # todo: added the option that minimum storage size is at least as big as the largest vessel's call_size
            # todo: find a way to add dwell time
            if self.debug:
                print('  *** add storage to elements')

            # add storage object
            storage = Storage(**defaults_storage_data)

            # - capex
            storage.capex = storage.unit_rate * storage.capacity + storage.mobilisation_min

            # - opex
            storage.insurance = storage.capex * storage.insurance_perc
            storage.maintenance = storage.capex * storage.maintenance_perc

            # energy
            energy = Energy(**defaults.energy_data)
            consumption = storage.consumption
            capacity = storage.capacity * storage.occupancy
            hours = self.operational_hours
            storage.energy = consumption * capacity * hours * energy.price

            if year == self.startyear:
                storage.year_online = year + storage.delivery_time + 1
            else:
                storage.year_online = year + storage.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            storage = self.add_cashflow_data_to_element(storage)

            self.elements.append(storage)

            storage_capacity += storage.capacity

            if self.debug:
                print(
                    '      a total of {} ton of storage capacity is online; {} ton total planned'.format(
                        storage_capacity_online,
                        storage_capacity))

    def conveyor_hinter_invest(self, year, defaults_hinterland_conveyor_data):
        """current strategy is to add conveyors as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        # # find unloading capacity of the unloading station
        # list_of_elements_Unloading = self.find_elements(Unloading_station)
        #
        # # find the total service rate
        # if list_of_elements_Unloading != []:
        #     service_capacity_unloading = 0
        #     for element in list_of_elements_Unloading:
        #         service_capacity_unloading += element.peak_capacity
        #
        # # list all conveyor objects in system
        # list_of_elements = self.find_elements(Conveyor_Hinter)
        #
        # # find the total service rate
        # service_capacity = 0
        # service_capacity_online = 0
        # if list_of_elements != []:
        #     for element in list_of_elements:
        #         if element.type == defaults_hinterland_conveyor_data['type']:
        #             service_capacity += element.capacity_steps
        #             if year >= element.year_online:
        #                 service_capacity_online += element.capacity_steps
        #
        # if self.debug:
        #     print('     a total of {} ton of {} conveyor hinterland service capacity is online; {} ton total planned'.format(
        #         service_capacity_online,
        #         defaults_hinterland_conveyor_data['type'],
        #         service_capacity))
        #
        # # check if total planned length is smaller than target length, if so add a quay
        # while service_capacity < service_capacity_unloading:
        #     # todo: this way conveyors are added until conveyor service capacity is at least the crane capacity
        #     if self.debug:
        #         print('add Conveyor to elements')
        #     conveyor = Conveyor_Hinter(**defaults_hinterland_conveyor_data)
        #
        #     # - capex
        #     capacity = conveyor.capacity_steps
        #     unit_rate = conveyor.unit_rate_factor * conveyor.length
        #     mobilisation = conveyor.mobilisation
        #     conveyor.capex = int(capacity * unit_rate + mobilisation)
        #
        #     # - opex
        #     conveyor.insurance = conveyor.capex * conveyor.insurance_perc
        #     conveyor.maintenance = conveyor.capex * conveyor.maintenance_perc
        #
        #     #   energy
        #     energy = Energy(**defaults.energy_data)
        #     consumption = conveyor.capacity_steps * conveyor.consumption_coefficient + conveyor.consumption_constant
        #     hours = self.operational_hours #* occupancy station #todo: the station occupancy is not yet defined
        #     conveyor.energy = consumption * hours * energy.price
        #
        #     # year online
        #     years_online = []
        #     for element in list_of_elements_Unloading:
        #         years_online.append(element.year_online)
        #     conveyor.year_online = element.year_online - 1 + conveyor.delivery_time
        #     #todo: the year_online is not yet complete, it does not follow directly the movements of the cranes
        #
        #     # add cash flow information to quay_wall object in a dataframe
        #     conveyor.hinter = self.add_cashflow_data_to_element(conveyor)
        #
        #     self.elements.append(conveyor.hinter)
        #
        #     service_capacity += conveyor.capacity_steps
        #
        # if self.debug:
        #     print('     a total of {} ton of conveyor hinterland service capacity is online; {} ton total planned'.format(
        #         service_capacity_online,
        #         service_capacity))

    def unloading_station_invest(self, year):
        """current strategy is to add unloading stations as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        station_occupancy_planned, station_occupancy_online = self.calculate_station_occupancy(year)
        if self.debug:
            print('     Station occupancy planned (@ start of year): {}'.format(station_occupancy_planned))
            print('     Station occupancy online (@ start of year): {}'.format(station_occupancy_online))

        allowable_station_occupancy = .4  # is 40 %

        while station_occupancy_planned > allowable_station_occupancy:
            # add a station when station occupancy is too high
            if self.debug:
                print('  *** add station to elements')

            station = Unloading_station(**defaults.hinterland_station_data)
            station.year_online = year + station.delivery_time

            # - capex
            unit_rate = station.unit_rate
            mobilisation = station.mobilisation
            station.capex = int(unit_rate + mobilisation)

            # - opex
            station.insurance = station.capex * station.insurance_perc
            station.maintenance = station.capex * station.maintenance_perc
            station.labour = 0

            energy = Energy(**defaults.energy_data)
            if station_occupancy_online == np.inf:
                station.energy = 0
            else:
                station.energy = station.consumption * self.operational_hours * station_occupancy_online * energy.price

            station.year_online = year + station.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            station = self.add_cashflow_data_to_element(station)

            self.elements.append(station)

            station_occupancy_planned, station_occupancy_online = self.calculate_station_occupancy(year)
            print('    station_occupancy_planned: {}'.format(station_occupancy_planned))
            # service_capacity += station.production
            # print(station_occupancy_planned)
            # print(station_occupancy_online)
            #
        # if self.debug:
        #     print('     a total of {} ton of conveyor service capacity is online; {} ton total planned'.format(
        #         service_capacity_online,
        #         service_capacity))

    # *** Financial analyses

    def capex(self):
        pass

    def opex(self):
        pass

    def revenues(self):
        pass

    def profits(self):
        pass

    def terminal_elements_plot(self, width=0.15, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = []
        berths = []
        cranes = []
        quays = []
        conveyors_quay = []
        storages = []
        conveyors_hinterland = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            berths.append(0)
            quays.append(0)
            cranes.append(0)
            conveyors_quay.append(0)
            storages.append(0)
            conveyors_hinterland.append(0)
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
                if isinstance(element, Conveyor_Quay):
                    if year >= element.year_online:
                        conveyors_quay[-1] += 1
                if isinstance(element, Storage):
                    if year >= element.year_online:
                        storages[-1] += 1
                if isinstance(element, Conveyor_Hinter):
                    if year >= element.year_online:
                        conveyors_hinterland[-1] += 1

        # generate plot
        fig, ax = plt.subplots(figsize=(20, 10))

        ax.bar([x + 0 * width for x in years], berths, width=width, alpha=alpha, label="berths", color='coral',
               edgecolor='crimson')
        ax.bar([x + 1 * width for x in years], quays, width=width, alpha=alpha, label="quays", color='orchid',
               edgecolor='purple')
        ax.bar([x + 2 * width for x in years], cranes, width=width, alpha=alpha, label="cranes", color='lightblue',
               edgecolor='blue')
        ax.bar([x + 3 * width for x in years], conveyors_quay, width=width, alpha=alpha, label="conveyors quay",
               color='lightgreen', edgecolor='green')
        ax.bar([x + 4 * width for x in years], storages, width=width, alpha=alpha, label="storages", color='orange',
               edgecolor='orangered')
        ax.bar([x + 5 * width for x in years], conveyors_hinterland, width=width, alpha=alpha, label="conveyors hinter",
               color='grey', edgecolor='black')
        ax.set_xlabel('Years')
        ax.set_ylabel('Elements on line [nr]')
        ax.set_title('Terminal elements online ({})'.format(self.crane_type_defaults['crane_type']))
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def terminal_capacity_plot(self, width=0.25, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # get crane service capacity and storage capacity
        years = []
        cranes = []
        cranes_capacity = []
        storages = []
        storages_capacity = []

        for year in range(self.startyear, self.startyear + self.lifecycle):

            years.append(year)
            cranes.append(0)
            cranes_capacity.append(0)
            storages.append(0)
            storages_capacity.append(0)

            handysize_calls, handymax_calls, panamax_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
            berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                year, handysize_calls, handymax_calls, panamax_calls)

            for element in self.elements:
                if isinstance(element, Cyclic_Unloader) | isinstance(element, Continuous_Unloader):
                    # calculate cranes service capacity: effective_capacity * operational hours * berth_occupancy?
                    if year >= element.year_online:
                        cranes[-1] += 1
                        cranes_capacity[
                            -1] += element.effective_capacity * self.operational_hours * crane_occupancy_online
                if isinstance(element, Storage):
                    if year >= element.year_online:
                        storages[-1] += 1
                        storages_capacity[-1] += element.capacity * 365 / 18

        # get demand
        demand = pd.DataFrame()
        demand['year'] = list(range(self.startyear, self.startyear + self.lifecycle))
        demand['demand'] = 0
        for commodity in self.find_elements(Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
            except:
                pass
        # generate plot
        fig, ax = plt.subplots(figsize=(20, 10))

        ax.bar([x - 0.5 * width for x in years], cranes_capacity, width=width, alpha=alpha, label="cranes capacity",
               color='red')
        # ax.bar([x + 0.5 * width for x in years], storages_capacity, width=width, alpha=alpha, label="storages",
        #        color='green')
        ax.step(years, demand['demand'].values, label="demand", where='mid')

        ax.set_xlabel('Years')
        ax.set_ylabel('Throughput capacity [tons/year]')
        ax.set_title('Terminal capacity online ({})'.format(self.crane_type_defaults['crane_type']))
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def cashflow_plot(self, width=0.3, alpha=0.6):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        # add cash flow information for each of the Terminal elements
        cash_flows = self.add_cashflow_elements()

        # prepare years, revenue, capex and opex for plotting
        years = cash_flows['year'].values
        revenue = self.revenues
        capex = cash_flows['capex'].values
        opex = cash_flows['insurance'].values + cash_flows['maintenance'].values + cash_flows['energy'].values + \
               cash_flows['labour'].values
        # todo: check if we need to add land lease as a opex (for terminal operator) or revenue (for a port operator)

        # sum cash flows to get profits as a function of year
        profits = []
        for year in years:
            profits.append(-cash_flows.loc[cash_flows['year'] == year]['capex'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['insurance'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['maintenance'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['energy'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['labour'].item() +
                           revenue[cash_flows.loc[cash_flows['year'] == year].index.item()])

        # cumulatively sum profits to get profits_cum
        profits_cum = [None] * len(profits)
        for index, value in enumerate(profits):
            if index == 0:
                profits_cum[index] = 0
            else:
                profits_cum[index] = profits_cum[index - 1] + profits[index]

        # generate plot
        fig, ax = plt.subplots(figsize=(16, 7))

        ax.bar([x - width for x in years], -opex, width=width, alpha=alpha, label="opex", color='lightblue')
        ax.bar(years, -capex, width=width, alpha=alpha, label="capex", color='red')
        ax.bar([x + width for x in years], revenue, width=width, alpha=alpha, label="revenue", color='lightgreen')
        ax.step(years, profits, label='profits', where='mid')
        ax.step(years, profits_cum, label='profits_cum', where='mid')

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
        """Gather data from Terminal elements and combine into a cash flow plot"""

        # add cash flow information for each of the Terminal elements
        cash_flows = self.add_cashflow_elements()

        # prepare years, revenue, capex and opex for plotting
        years = cash_flows['year'].values
        revenue = self.revenues
        capex = cash_flows['capex'].values
        opex = cash_flows['insurance'].values + cash_flows['maintenance'].values + cash_flows['energy'].values + \
               cash_flows['labour'].values

        PV = - capex - opex + revenue
        print('PV: {}'.format(PV))

        print('NPV: {}'.format(np.sum(PV)))

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
        cash_flows['revenues'] = self.revenues

        for element in self.elements:
            if hasattr(element, 'df'):
                for column in cash_flows.columns:
                    if column in element.df.columns and column != "year":
                        cash_flows[column] += element.df[column]

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
            df.loc[df["year"] == year_online - 2, "capex"] = 0.6 * capex
            df.loc[df["year"] == year_online - 1, "capex"] = 0.4 * capex
        else:
            df.loc[df["year"] == year_online - 1, "capex"] = capex

        # opex
        if maintenance:
            df.loc[df["year"] >= year_online, "maintenance"] = maintenance
        if insurance:
            df.loc[df["year"] >= year_online, "insurance"] = insurance
        if energy:
            df.loc[df["year"] >= year_online, "energy"] = energy
        if labour:
            df.loc[df["year"] >= year_online, "labour"] = labour

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
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                handysize_vol += volume * commodity.handysize_perc / 100
                handymax_vol += volume * commodity.handymax_perc / 100
                panamax_vol += volume * commodity.panamax_perc / 100
                total_vol += volume
            except:
                pass

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

    def calculate_berth_occupancy(self, year, handysize_calls, handymax_calls, panamax_calls):
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
        service_rate_planned = 0
        service_rate_online = 0
        if list_of_elements != []:
            for element in list_of_elements:
                service_rate_planned += element.effective_capacity
                if year >= element.year_online:
                    service_rate_online += element.effective_capacity

            # estimate berth occupancy
            time_at_berth_handysize_planned = handysize_calls * (
                    (defaults.handysize_data["call_size"] / service_rate_planned) + defaults.handysize_data[
                "mooring_time"])
            time_at_berth_handymax_planned = handymax_calls * (
                    (defaults.handymax_data["call_size"] / service_rate_planned) + defaults.handymax_data[
                "mooring_time"])
            time_at_berth_panamax_planned = panamax_calls * (
                    (defaults.panamax_data["call_size"] / service_rate_planned) + defaults.panamax_data["mooring_time"])

            total_time_at_berth_planned = np.sum(
                [time_at_berth_handysize_planned, time_at_berth_handymax_planned, time_at_berth_panamax_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            berth_occupancy_planned = total_time_at_berth_planned / self.operational_hours

            # estimate crane occupancy
            time_at_crane_handysize_planned = handysize_calls * (
                (defaults.handysize_data["call_size"] / service_rate_planned))
            time_at_crane_handymax_planned = handymax_calls * (
                (defaults.handymax_data["call_size"] / service_rate_planned))
            time_at_crane_panamax_planned = panamax_calls * (
                (defaults.panamax_data["call_size"] / service_rate_planned))

            total_time_at_crane_planned = np.sum(
                [time_at_crane_handysize_planned, time_at_crane_handymax_planned, time_at_crane_panamax_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            crane_occupancy_planned = total_time_at_crane_planned / self.operational_hours

            if service_rate_online != 0:
                time_at_berth_handysize_online = handysize_calls * (
                        (defaults.handysize_data["call_size"] / service_rate_online) + defaults.handysize_data[
                    "mooring_time"])
                time_at_berth_handymax_online = handymax_calls * (
                        (defaults.handymax_data["call_size"] / service_rate_online) + defaults.handymax_data[
                    "mooring_time"])
                time_at_berth_panamax_online = panamax_calls * (
                        (defaults.panamax_data["call_size"] / service_rate_online) + defaults.panamax_data[
                    "mooring_time"])

                total_time_at_berth_online = np.sum(
                    [time_at_berth_handysize_online, time_at_berth_handymax_online, time_at_berth_panamax_online])

                # berth_occupancy is the total time at berth devided by the operational hours
                berth_occupancy_online = min([total_time_at_berth_online / self.operational_hours, 1])

                handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
                time_at_crane = total_vol / (service_rate_online * len(list_of_elements))

                # time_at_crane_handysize_online = handysize_calls * (
                #     (defaults.handysize_data["call_size"] / service_rate_online))
                # time_at_crane_handymax_online = handymax_calls * (
                #     (defaults.handymax_data["call_size"] / service_rate_online))
                # time_at_crane_panamax_online = panamax_calls * (
                #     (defaults.panamax_data["call_size"] / service_rate_online))

                # total_time_at_crane_online = np.sum([time_at_crane_handysize_online, time_at_crane_handymax_online, time_at_crane_panamax_online])

                # berth_occupancy is the total time at berth devided by the operational hours
                #crane_occupancy_online = min([total_time_at_crane_online / self.operational_hours, 1])

                crane_occupancy_online = min([time_at_crane / self.operational_hours, 1])

            else:
                berth_occupancy_online = float("inf")
                crane_occupancy_online = float("inf")

        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            berth_occupancy_planned = float("inf")
            berth_occupancy_online = float("inf")
            crane_occupancy_planned = float("inf")
            crane_occupancy_online = float("inf")

        return berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online

    def calculate_station_occupancy(self, year):
        """
        - Find all cranes and sum their effective_capacity to get service_capacity
        - Divide callsize_per_vessel by service_capacity and add mooring time to get total time at berth
        - Occupancy is total_time_at_berth divided by operational hours
        """

        list_of_elements = self.find_elements(Unloading_station)
        # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)

        service_rate_planned = 0
        service_rate_online = 0
        if list_of_elements != []:
            for element in list_of_elements:
                service_rate_planned += element.capacity
                if year >= element.year_online:
                    service_rate_online += element.capacity

            time_at_station_planned = total_vol / service_rate_planned  # element.capacity

            # station_occupancy is the total time at station divided by the operational hours
            station_occupancy_planned = time_at_station_planned / self.operational_hours

            if service_rate_online != 0:
                time_at_station_online = total_vol / service_rate_online  # element.capacity

                # station occupancy is the total time at berth divided by the operational hours
                station_occupancy_online = min([time_at_station_online / self.operational_hours, 1])
            else:
                station_occupancy_online = float("inf")

        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            station_occupancy_planned = float("inf")
            station_occupancy_online = float("inf")

        return station_occupancy_planned, station_occupancy_online

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

        if self.debug:
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
