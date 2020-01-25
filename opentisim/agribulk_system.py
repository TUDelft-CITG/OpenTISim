# package(s) for data handling
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# opentisim package
from opentisim.agribulk_objects import *
from opentisim import agribulk_defaults
from opentisim import core

class System:
    """This class implements the 'complete supply chain' concept (Van Koningsveld et al, 2020) for agribulk terminals.
    The module allows variation of the type of quay crane used and the type of storage used. Terminal development is
    governed by three triggers: the allowable berth occupancy, the allowable dwell time and the allowable station
    occupancy."""
    def __init__(self, startyear=2019, lifecycle=20, operational_hours=5840, debug=False, elements=[],
                 crane_type_defaults=agribulk_defaults.mobile_crane_data,
                 storage_type_defaults=agribulk_defaults.silo_data,
                 allowable_berth_occupancy=0.4, allowable_dwelltime=18 / 365, allowable_station_occupancy=0.4):
        # time inputs
        self.startyear = startyear
        self.lifecycle = lifecycle
        self.operational_hours = operational_hours

        # provide intermediate outputs via print statements if debug = True
        self.debug = debug

        # collection of all terminal objects
        self.elements = elements

        # default values to use in case various types can be selected
        self.crane_type_defaults = crane_type_defaults
        self.storage_type_defaults = storage_type_defaults

        # triggers for the various elements (berth, storage and station)
        self.allowable_berth_occupancy = allowable_berth_occupancy
        self.allowable_dwelltime = allowable_dwelltime
        self.allowable_station_occupancy = allowable_station_occupancy

        # storage variables for revenue
        self.revenues = []

    # *** Overall terminal investment strategy for terminal class.
    def simulate(self):
        """The 'simulate' method implements the terminal investment strategy for this terminal class.

        This method automatically generates investment decisions, parametrically derived from overall demand trends and
        a number of investment triggers.

        Generic approaches based on:
        - Van Koningsveld, M. (Ed.), Verheij, H., Taneja, P. and De Vriend, H.J. (2020). Ports and Waterways.
          Navigating the changing world. TU Delft, Delft, The Netherlands.
        - Van Koningsveld, M. and J. P. M. Mulder. 2004. Sustainable Coastal Policy Developments in the
          Netherlands. A Systematic Approach Revealed. Journal of Coastal Research 20(2), pp. 375-385

        Specific application based on:
        - Ijzermans, W., 2019. Terminal design optimization. Adaptive agribulk terminal planning
          in light of an uncertain future. Master's thesis. Delft University of Technology, Netherlands.
          URL: http://resolver.tudelft.nl/uuid:7ad9be30-7d0a-4ece-a7dc-eb861ae5df24.

        The simulate method applies frame of reference style decisions while stepping through each year of the terminal
        lifecycle and check if investment is needed (in light of strategic objective, operational objective,
        QSC, decision recipe, intervention method):

           1. for each year estimate the anticipated vessel arrivals based on the expected demand
           2. for each year evaluate which investment are needed given the strategic and operational objectives
           3. for each year calculate the energy costs (requires insight in realized demands)
           4. for each year calculate the demurrage costs (requires insight in realized demands)
           5. for each year calculate terminal revenues (requires insight in realized demands)
           6. collect all cash flows (capex, opex, revenues)
           7. calculate PV's and aggregate to NPV

        """

        for year in range(self.startyear, self.startyear + self.lifecycle):
            """
            The simulate method is designed according to the following overall objectives for the terminal:
            - strategic objective: To maintain a profitable enterprise (NPV > 0) over the terminal lifecycle
            - operational objective: Annually invest in infrastructure upgrades when performance criteria are triggered
            """

            if self.debug:
                print('')
                print('### Simulate year: {} ############################'.format(year))

            # 1. for each year estimate the anticipated vessel arrivals based on the expected demand
            handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
            if self.debug:
                print('--- Cargo volume and vessel calls for {} ---------'.format(year))
                print('  Total cargo volume: {}'.format(total_vol))
                print('  Total vessel calls: {}'.format(total_calls))
                print('     Handysize calls: {}'.format(handysize))
                print('     Handymax calls: {}'.format(handymax))
                print('     Panamax calls: {}'.format(panamax))
                print('----------------------------------------------------')

            # 2. for each year evaluate which investment are needed given the strategic and operational objectives
            self.berth_invest(year, handysize, handymax, panamax)

            if self.debug:
                print('')
                print('$$$ Check quay conveyors (coupled with quay crane capacity) -----------')
            self.conveyor_quay_invest(year, agribulk_defaults.quay_conveyor_data)

            if self.debug:
                print('')
                print('$$$ Check storage (coupled with max call size and dwell time) ---------')
            self.storage_invest(year, self.storage_type_defaults)

            if self.debug:
                print('')
                print('$$$ Check hinterland conveyors (coupled with unloading stations) ------')
            self.conveyor_hinter_invest(year, agribulk_defaults.hinterland_conveyor_data)

            if self.debug:
                print('')
                print('$$$ Check unloading station (coupled with quay cranes) ----------------')
            self.unloading_station_invest(year)

        # 3. for each year calculate the energy costs (requires insight in realized demands)
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_energy_cost(year)

        # 4. for each year calculate the demurrage costs (requires insight in realized demands)
        self.demurrage = []
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_demurrage_cost(year)

        # 5. for each year calculate terminal revenues (requires insight in realized demands)
        self.revenues = []
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_revenue(year)

        # 6. collect all cash flows (capex, opex, revenues)
        # cash_flows, cash_flows_WACC_real = core.add_cashflow_elements(self)

        # 7. calculate PV's and aggregate to NPV
        core.NPV(self,  Labour(**agribulk_defaults.labour_data))

    # *** Individual investment methods for terminal elements
    def berth_invest(self, year, handysize, handymax, panamax):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and Mulder,
        2004) for the berth investments.

        Decision recipe Berth:
           QSC: berth_occupancy
           Benchmarking procedure: there is a problem if the estimated berth_occupancy > allowable_berth_occupancy
              - allowable_berth_occupancy = .40 # 40%
              - a berth needs:
                 - a quay
                 - cranes (min:1 and max: max_cranes)
              - berth occupancy depends on:
                 - total_calls, total_vol and time needed for mooring, unmooring
                 - total_service_capacity as delivered by the cranes
           Intervention procedure: invest enough to make the berth_occupancy < allowable_berth_occupancy
              - adding berths, quays and cranes decreases berth_occupancy_rate
        """

        # report on the status of all berth elements
        if self.debug:
            print('')
            print('--- Status terminal @ start of year ----------------')

        core.report_element(self, Berth, year)
        core.report_element(self, Quay_wall, year)
        core.report_element(self, Cyclic_Unloader, year)
        core.report_element(self, Continuous_Unloader, year)
        core.report_element(self, Conveyor_Quay, year)
        core.report_element(self, Storage, year)
        core.report_element(self, Conveyor_Hinter, year)
        core.report_element(self, Unloading_station, year)

        # calculate berth occupancy
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
            self.calculate_berth_occupancy(year, handysize, handymax, panamax)
        berths = len(core.find_elements(self, Berth))

        if berths != 0:
            waiting_factor = \
                core.occupancy_to_waitingfactor(occupancy=berth_occupancy_online, nr_of_servers_chk=berths, poly_order=6)
            total_calls = handysize + handymax + panamax

            waiting_time_hours = waiting_factor * crane_occupancy_online * self.operational_hours / total_calls
            waiting_time_occupancy = waiting_time_hours * total_calls / self.operational_hours

            # waiting_factor, waiting_time_occupancy = self.waiting_time(year)
        else:
            waiting_factor = np.inf
            waiting_time_hours = np.inf
            waiting_time_occupancy = np.inf

        if self.debug:
            print('     Berth occupancy online (@ start of year): {:.2f} (trigger level: {:.2f})'.format(berth_occupancy_online, self.allowable_berth_occupancy))
            print('     Berth occupancy planned (@ start of year): {:.2f} (trigger level: {:.2f})'.format(berth_occupancy_planned, self.allowable_berth_occupancy))
            print('     Crane occupancy online (@ start of year): {:.2f}'.format(crane_occupancy_online))
            print('     Crane occupancy planned (@ start of year): {:.2f}'.format(crane_occupancy_planned))
            print('     Waiting time occupancy (@ start of year): {:.2f}'.format(waiting_time_occupancy))
            print('     Waiting time factor (@ start of year): {:.2f}'.format(waiting_factor))

            print('')
            print('--- Start investment analysis ----------------------')
            print('')
            print('$$$ Check berth elements (coupled with berth occupancy) ---------------')

        core.report_element(self, Berth, year)
        core.report_element(self, Quay_wall, year)
        core.report_element(self, Cyclic_Unloader, year)

        while berth_occupancy_planned > self.allowable_berth_occupancy:

            # while planned berth occupancy is too large add a berth when no crane slots are available
            if not (self.check_crane_slot_available()):
                if self.debug:
                    print('  *** add Berth to elements')
                berth = Berth(**agribulk_defaults.berth_data)
                berth.year_online = year + berth.delivery_time
                self.elements.append(berth)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
                    self.calculate_berth_occupancy(year, handysize, handymax, panamax)
                if self.debug:
                    print('     Berth occupancy planned (after adding berth): {:.2f} (trigger level: {})'.format(berth_occupancy_planned, self.allowable_berth_occupancy))
                    # print('     Berth occupancy online (after adding berth): {}'.format(berth_occupancy_online))

            # while planned berth occupancy is too large add a berth if a quay is needed
            berths = len(core.find_elements(self, Berth))
            quay_walls = len(core.find_elements(self, Quay_wall))
            if berths > quay_walls:
                length_v = max(agribulk_defaults.handysize_data["LOA"],agribulk_defaults.handymax_data["LOA"],
                              agribulk_defaults.panamax_data["LOA"])  # average size
                draft = max(agribulk_defaults.handysize_data["draft"],agribulk_defaults.handymax_data["draft"],
                           agribulk_defaults.panamax_data["draft"])

                # apply PIANC 2014:
                # see Ijzermans, 2019 - infrastructure.py line 107 - 111
                if quay_walls == 0:
                    # - length when next quay is n = 1
                    length = length_v + 2 * 15  # ref: PIANC 2014
                elif quay_walls == 1:
                    # - length when next quay is n > 1
                    length = 1.1 * berths * (length_v + 15) - (length_v + 2 * 15)  # ref: PIANC 2014
                else:
                    length = 1.1 * berths * (length_v + 15) - 1.1 * (berths - 1) * (length_v + 15)

                # - depth
                quay_wall = Quay_wall(**agribulk_defaults.quay_wall_data)
                depth = np.sum([draft, quay_wall.max_sinkage, quay_wall.wave_motion, quay_wall.safety_margin])
                self.quay_invest(year, length, depth)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
                    self.calculate_berth_occupancy(year, handysize, handymax, panamax)
                if self.debug:
                    print('     Berth occupancy planned (after adding quay): {:.2f} (trigger level: {})'.format(berth_occupancy_planned, self.allowable_berth_occupancy))
                    # print('     Berth occupancy online (after adding quay): {}'.format(berth_occupancy_online))

            # while planned berth occupancy is too large add a crane if a crane is needed
            if self.check_crane_slot_available():
                self.crane_invest(year)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, handysize, handymax, panamax)
                if self.debug:
                    print('     Berth occupancy planned (after adding crane): {:.2f} (trigger level: {})'.format(berth_occupancy_planned, self.allowable_berth_occupancy))
                    # print('     Berth occupancy online (after adding crane): {}'.format(berth_occupancy_online))

    def quay_invest(self, year, length, depth):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and
        Mulder, 2004) for the quay investments.

        Decision recipe Quay:
           QSC: quay_per_berth
           Benchmarking procedure (triggered in self.berth_invest): there is a problem when
              the number of berths > the number of quays, but also while the planned berth occupancy is too large
           Intervention procedure: invest enough to make sure that each quay has a berth and the planned berth
              occupancy is below the max allowable berth occupancy
              - adding quay will increase quay_per_berth
              - quay_wall.length must be long enough to accommodate largest expected vessel
              - quay_wall.depth must be deep enough to accommodate largest expected vessel
              - quay_wall.freeboard must be high enough to accommodate largest expected vessel
        """

        if self.debug:
            print('  *** add Quay to elements')
        # add a Quay_wall element
        quay_wall = Quay_wall(**agribulk_defaults.quay_wall_data)

        # - capex
        unit_rate = int(quay_wall.Gijt_constant_2 * 2 * (depth + quay_wall.freeboard))
        mobilisation = int(max((length * unit_rate * quay_wall.mobilisation_perc), quay_wall.mobilisation_min))
        quay_wall.capex = int(length * unit_rate + mobilisation)

        # - opex
        quay_wall.insurance = unit_rate * length * quay_wall.insurance_perc
        quay_wall.maintenance = unit_rate * length * quay_wall.maintenance_perc
        quay_wall.year_online = year + quay_wall.delivery_time

        # add cash flow information to quay_wall object in a dataframe
        quay_wall = core.add_cashflow_data_to_element(self, quay_wall)

        self.elements.append(quay_wall)

    def crane_invest(self, year):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and
        Mulder, 2004) for the crane investments.

        Decision recipe Crane:
           QSC: berth_occupancy_planned
           Benchmarking procedure (triggered in self.berth_invest): there is a problem when the planned berth occupancy
              is larger than the max allowable berth occupancy
           Intervention procedure: invest until planned berth occupancy is below the max allowable berth occupancy
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
        crane.insurance = unit_rate * crane.insurance_perc
        crane.maintenance = unit_rate * crane.maintenance_perc

        # labour
        labour = Labour(**agribulk_defaults.labour_data)
        '''old formula --> crane.labour = crane.crew * self.operational_hours / labour.shift_length  '''
        crane.shift = ((crane.crew * self.operational_hours) / (
                labour.shift_length * labour.annual_shifts))
        crane.labour = crane.shift * labour.operational_salary

        # apply proper timing for the crane to come online (in the same year as the latest Quay_wall)
        years_online = []
        for element in core.find_elements(self, Quay_wall):
            years_online.append(element.year_online)
        crane.year_online = max([year + crane.delivery_time, max(years_online)])

        # add cash flow information to quay_wall object in a dataframe
        crane = core.add_cashflow_data_to_element(self, crane)

        # add object to elements
        self.elements.append(crane)

    def conveyor_quay_invest(self, year, agribulk_defaults_quay_conveyor_data):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and
        Mulder, 2004) for the quay conveyor investments.

        Operational objective: maintain a quay conveyor capacity that at least matches the quay crane capacity (so
        basically the quay conveyors follow what happens on the berth)

        Decision recipe quay conveyor:
           QSC: quay_conveyor_capacity planned
           Benchmarking procedure: there is a problem when the quay_conveyor_capacity_planned is smaller than the
           quay_crane_service_rate_planned
              For the quay conveyor investments the strategy is to at least match the quay crane processing capacity
           Intervention procedure: the intervention strategy is to add quay conveyors until the trigger is achieved
              - find out how much quay_conveyor_capacity is planned
              - find out how much quay_crane_service_rate is planned
              - add quay_conveyor_capacity until it matches quay_crane_service_rate
        """

        # find the total quay_conveyor capacity
        quay_conveyor_capacity_planned = 0
        quay_conveyor_capacity_online = 0
        list_of_elements = core.find_elements(self, Conveyor_Quay)
        if list_of_elements != []:
            for element in list_of_elements:
                quay_conveyor_capacity_planned += element.capacity_steps
                if year >= element.year_online:
                    quay_conveyor_capacity_online += element.capacity_steps

        if self.debug:
            print('     a total of {} ton of quay conveyor service capacity is online; {} ton still pending'.format(
                quay_conveyor_capacity_online, quay_conveyor_capacity_planned-quay_conveyor_capacity_online))

        # find the total quay crane service rate,
        quay_crane_service_rate_planned = 0
        years_online = []
        for element in (core.find_elements(self, Cyclic_Unloader) + core.find_elements(self, Continuous_Unloader)):
            quay_crane_service_rate_planned += element.peak_capacity
            years_online.append(element.year_online)

        # check if total planned capacity of the quay conveyor is smaller than planned capacity of the quay cranes,
        # if so add a conveyor
        while quay_conveyor_capacity_planned < quay_crane_service_rate_planned:
            if self.debug:
                print('  *** add Quay Conveyor to elements')
            conveyor_quay = Conveyor_Quay(**agribulk_defaults_quay_conveyor_data)

            # - capex
            capacity = conveyor_quay.capacity_steps
            unit_rate = conveyor_quay.unit_rate_factor * conveyor_quay.length
            mobilisation = conveyor_quay.mobilisation
            conveyor_quay.capex = int(capacity * unit_rate + mobilisation)

            # - opex
            conveyor_quay.insurance = capacity * unit_rate * conveyor_quay.insurance_perc
            conveyor_quay.maintenance = capacity * unit_rate * conveyor_quay.maintenance_perc

            #   labour
            labour = Labour(**agribulk_defaults.labour_data)
            conveyor_quay.shift = (
                    (conveyor_quay.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            conveyor_quay.labour = conveyor_quay.shift * labour.operational_salary

            # # apply proper timing for the crane to come online (in the same year as the latest Quay_wall)

            # there should always be a new crane in the planning
            new_crane_years = [x for x in years_online if x >= year]

            # find the maximum online year of Conveyor_Quay or make it []
            if core.find_elements(self, Conveyor_Quay) != []:
                max_conveyor_years = max([x.year_online for x in core.find_elements(self, Conveyor_Quay)])
            else:
                max_conveyor_years = []

            # decide what online year to use
            if max_conveyor_years == []:
                conveyor_quay.year_online = min(new_crane_years)
            elif max_conveyor_years < min(new_crane_years):
                conveyor_quay.year_online = min(new_crane_years)
            elif max_conveyor_years == min(new_crane_years):
                conveyor_quay.year_online = max(new_crane_years)
            elif max_conveyor_years > min(new_crane_years):
                conveyor_quay.year_online = max(new_crane_years)

            # add cash flow information to quay_wall object in a dataframe
            conveyor_quay = core.add_cashflow_data_to_element(self, conveyor_quay)

            self.elements.append(conveyor_quay)

            quay_conveyor_capacity_planned += conveyor_quay.capacity_steps

            if self.debug:
                print('     a total of {} ton of conveyor quay service capacity is online; {} ton still pending'.format(
                    quay_conveyor_capacity_online, quay_conveyor_capacity_planned-quay_conveyor_capacity_online))

    def storage_invest(self, year, agribulk_defaults_storage_data):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and
        Mulder, 2004) for the storage investments.

        Operational objective: maintain a storage capacity that is large enough to at least contain one time the largest
        vessel call size or that is large enough to accommodate a maximum allowable dwelltime.

        Decision recipe storage:
           QSC: storage_capacity
           Benchmarking procedure: there is a problem when the storage_capacity is too small to store one time the
           largest call size or when it is too small to allow for a predetermined max allowable dwell time
              The max allowable dwelltime is here determined as 5% of the annual demand, increased by 10% (PIANC, 2014)
           Intervention procedure: the intervention strategy is to add storage until the benchmarking trigger is
           achieved. The trigger is the max of one call size, or the volume derived from the dwelltime requirement.
        """

        # from all storage objects sum online capacity
        storage_capacity = 0
        storage_capacity_online = 0
        list_of_elements = core.find_elements(self, Storage)
        if list_of_elements != []:
            for element in list_of_elements:
                if element.type == agribulk_defaults_storage_data['type']:
                    storage_capacity += element.capacity
                    if year >= element.year_online:
                        storage_capacity_online += element.capacity

        if self.debug:
            print('     a total of {} ton of {} storage capacity is online; {} ton still pending'.format(
                storage_capacity_online, agribulk_defaults_storage_data['type'], storage_capacity-storage_capacity_online))

        handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
            self.calculate_berth_occupancy(year, handysize, handymax, panamax)

        # here an important bug was fixed! Previous code took the max call size of all vessesls,
        # but it needs to take the max call size of the vessels that actually arrive
        max_vessel_call_size = 0
        for vessel in core.find_elements(self, Vessel):
            if vessel.type=='Handysize' and handysize != 0:
                max_vessel_call_size = max(vessel.call_size, max_vessel_call_size)

            if vessel.type=='Handymax' and handymax != 0:
                max_vessel_call_size = max(vessel.call_size, max_vessel_call_size)

            if vessel.type=='Panamax' and panamax != 0:
                max_vessel_call_size = max(vessel.call_size, max_vessel_call_size)

        # find the total service rate,
        service_rate = 0
        for element in (core.find_elements(self, Cyclic_Unloader) + core.find_elements(self, Continuous_Unloader)):
            if year >= element.year_online:
                service_rate += element.effective_capacity * crane_occupancy_online

        commodities = core.find_elements(self, Commodity)
        if commodities != []:
            for commodity in commodities:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                storage_capacity_dwelltime = round((volume * 0.05) * 1.1)  # see IJzermans (2019) p.26

        # check if sufficient storage capacity is available
        while storage_capacity < max(max_vessel_call_size, storage_capacity_dwelltime):
            if self.debug:
                print('  *** add storage to elements')

            # add storage object
            storage = Storage(**agribulk_defaults_storage_data)

            # - capex
            storage.capex = storage.unit_rate * storage.capacity + storage.mobilisation_min

            # - opex
            storage.insurance = storage.unit_rate * storage.capacity * storage.insurance_perc
            storage.maintenance = storage.unit_rate * storage.capacity * storage.maintenance_perc

            #   labour**agribulk_defaults
            labour = Labour(**agribulk_defaults.labour_data)
            storage.shift = ((storage.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            storage.labour = storage.shift * labour.operational_salary

            if year == self.startyear:
                storage.year_online = year + storage.delivery_time + 1
            else:
                storage.year_online = year + storage.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            storage = core.add_cashflow_data_to_element(self, storage)

            self.elements.append(storage)

            storage_capacity += storage.capacity

            if self.debug:
                print('     a total of {} ton of {} storage capacity is online; {} ton still pending'.format(
                    storage_capacity_online, agribulk_defaults_storage_data['type'],
                    storage_capacity - storage_capacity_online))

    def unloading_station_invest(self, year):
        """The operational objective for the investment strategy for unloading stations is to have sufficient planned
        unloading stations to keep the station occupancy below a given threshold for the quay crane capacity planned.

        current strategy is to add unloading stations as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        station_occupancy_planned, station_occupancy_online = self.calculate_station_occupancy(year)
        train_calls = self.train_call(year)

        if self.debug:
            print('     Station occupancy planned (@ start of year): {:.2f}'.format(station_occupancy_planned))
            # print('     Station occupancy online (@ start of year): {:.2f}'.format(station_occupancy_online))
            print('     Number of trains (@start of year): {:.2f}'.format(train_calls))

        while station_occupancy_planned > self.allowable_station_occupancy:
            # add a station when station occupancy is too high
            if self.debug:
                print('  *** add unloading station to elements')

            station = Unloading_station(**agribulk_defaults.hinterland_station_data)

            # - capex
            unit_rate = station.unit_rate
            mobilisation = station.mobilisation
            station.capex = int(unit_rate + mobilisation)

            # - opex
            station.insurance = unit_rate * station.insurance_perc
            station.maintenance = unit_rate * station.maintenance_perc

            #   labour
            labour = Labour(**agribulk_defaults.labour_data)
            station.shift = ((station.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            station.labour = station.shift * labour.operational_salary

            if year == self.startyear:
                station.year_online = year + station.delivery_time + 1
            else:
                station.year_online = year + station.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            station = core.add_cashflow_data_to_element(self, station)

            self.elements.append(station)

            station_occupancy_planned, station_occupancy_online = self.calculate_station_occupancy(year)

    def conveyor_hinter_invest(self, year, agribulk_defaults_hinterland_conveyor_data):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and Mulder,
        2004) for the hinter conveyor investments.

        Operational objective: maintain a hinter conveyor capacity that at least matches the station unloading capacity
        (so basically the hinter conveyors follow what happens on the station)

        Decision recipe quay conveyor:
           QSC: hinter_conveyor_capacity planned
           Benchmarking procedure: there is a problem when the hinter_conveyor_capacity_planned is smaller than the
           station_service_rate_planned
              For the hinter conveyor investments the strategy is to at least match the unloading station capacity
           Intervention procedure: the intervention strategy is to add hinter conveyors until the trigger is achieved
              - find out how much hinter_conveyor_capacity is planned
              - find out how much station_service_rate_planned is planned
              - add hinter_conveyor_capacity until it matches station_service_rate_planned
        """

        # find the total service rate
        hinter_conveyor_capacity_planned = 0
        hinter_conveyor_capacity_online = 0
        list_of_elements_conveyor = core.find_elements(self, Conveyor_Hinter)
        if list_of_elements_conveyor != []:
            for element in list_of_elements_conveyor:
                hinter_conveyor_capacity_planned += element.capacity_steps
                if year >= element.year_online:
                    hinter_conveyor_capacity_online += element.capacity_steps

        if self.debug:
            print(
                '     a total of {} ton of hinterland conveyor service capacity is online; {} ton still pending'.format(
                    hinter_conveyor_capacity_online,
                    hinter_conveyor_capacity_planned - hinter_conveyor_capacity_online))

        # find the total station service rate planned,
        station_service_rate_planned = 0
        years_online = []
        for element in (core.find_elements(self, Unloading_station)):
            station_service_rate_planned += element.production
            years_online.append(element.year_online)

        # check if the hinter conveyor capacity (planned) at least matches the station unloading rate (planned)
        while hinter_conveyor_capacity_planned < station_service_rate_planned:
            if self.debug:
                print('  *** add Hinter Conveyor to elements')
            conveyor_hinter = Conveyor_Hinter(**agribulk_defaults_hinterland_conveyor_data)

            # - capex
            capacity = conveyor_hinter.capacity_steps
            unit_rate = conveyor_hinter.unit_rate_factor * conveyor_hinter.length
            mobilisation = conveyor_hinter.mobilisation
            conveyor_hinter.capex = int(capacity * unit_rate + mobilisation)

            # - opex
            conveyor_hinter.insurance = capacity * unit_rate * conveyor_hinter.insurance_perc
            conveyor_hinter.maintenance = capacity * unit_rate * conveyor_hinter.maintenance_perc

            # - labour
            labour = Labour(**agribulk_defaults.labour_data)
            conveyor_hinter.shift = (
                    (conveyor_hinter.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            conveyor_hinter.labour = conveyor_hinter.shift * labour.operational_salary

            # - online year
            conveyor_hinter.year_online = max(years_online)

            # add cash flow information to quay_wall object in a dataframe
            conveyor_hinter = core.add_cashflow_data_to_element(self, conveyor_hinter)

            self.elements.append(conveyor_hinter)

            hinter_conveyor_capacity_planned += conveyor_hinter.capacity_steps

            if self.debug:
                print(
                    '     a total of {} ton of hinterland conveyor service capacity is online; {} ton still pending'.format(
                        hinter_conveyor_capacity_online,
                        hinter_conveyor_capacity_planned - hinter_conveyor_capacity_online))

    # *** Energy costs, demurrage costs and revenue calculation methods
    def calculate_energy_cost(self, year):
        """
        1. calculate the value of the total demand in year (demand * handling fee)
        2. calculate the maximum amount that can be handled (service capacity * operational hours)
        Terminal.revenues is the minimum of 1. and 2.
        """

        energy = Energy(**agribulk_defaults.energy_data)
        handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
            year, handysize, handymax, panamax)
        station_occupancy_planned, station_occupancy_online = self.calculate_station_occupancy(year)

        # calculate crane energy
        list_of_elements_1 = core.find_elements(self, Cyclic_Unloader)
        list_of_elements_2 = core.find_elements(self, Continuous_Unloader)
        list_of_elements_Crane = list_of_elements_1 + list_of_elements_2

        for element in list_of_elements_Crane:
            if year >= element.year_online:
                consumption = element.consumption
                hours = self.operational_hours * crane_occupancy_online

                if consumption * hours * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * hours * energy.price

            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate Quay conveyor energy
        list_of_elements_quay = core.find_elements(self, Conveyor_Quay)

        for element in list_of_elements_quay:
            if year >= element.year_online:
                consumption = element.capacity_steps * element.consumption_coefficient + element.consumption_constant
                hours = self.operational_hours * crane_occupancy_online

                if consumption * hours * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * hours * energy.price

            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate storage energy
        list_of_elements_Storage = core.find_elements(self, Storage)

        for element in list_of_elements_Storage:
            if year >= element.year_online:
                consumption = element.consumption
                capacity = element.capacity
                hours = self.operational_hours

                if consumption * capacity * hours * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * capacity * hours * energy.price

            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate hinterland conveyor energy
        list_of_elements_hinter = core.find_elements(self, Conveyor_Hinter)

        for element in list_of_elements_hinter:
            if year >= element.year_online:
                consumption = element.capacity_steps * element.consumption_coefficient + element.consumption_constant
                hours = self.operational_hours * station_occupancy_online

                if consumption * hours * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * hours * energy.price

            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate hinterland station energy
        station_occupancy_planned, station_occupancy_online = self.calculate_station_occupancy(year)

        list_of_elements_Station = core.find_elements(self, Unloading_station)

        for element in list_of_elements_Station:
            if year >= element.year_online:

                if element.consumption * self.operational_hours * station_occupancy_online * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'
                    ] = element.consumption * self.operational_hours * station_occupancy_online * energy.price

            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

    def calculate_demurrage_cost(self, year):

        """Find the demurrage cost per type of vessel and sum all demurrage cost"""

        handysize_calls, handymax_calls, panamax_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
            self.calculate_berth_occupancy(year, handysize_calls, handymax_calls, panamax_calls)

        berths = len(core.find_elements(self, Berth))

        waiting_factor = \
            core.occupancy_to_waitingfactor(occupancy=berth_occupancy_online, nr_of_servers_chk=berths, poly_order=6)

        waiting_time_hours = waiting_factor * crane_occupancy_online * self.operational_hours / total_calls
        waiting_time_occupancy = waiting_time_hours * total_calls / self.operational_hours

        # Find the service_rate per quay_wall to find the average service hours at the quay for a vessel
        quay_walls = len(core.find_elements(self, Quay_wall))

        service_rate = 0
        for element in (core.find_elements(self, Cyclic_Unloader) + core.find_elements(self, Continuous_Unloader)):
            if year >= element.year_online:
                service_rate += element.effective_capacity / quay_walls

        # Find the demurrage cost per type of vessel
        if service_rate != 0:
            handymax = Vessel(**agribulk_defaults.handymax_data)
            service_time_handymax = handymax.call_size / service_rate
            waiting_time_hours_handymax = waiting_factor * service_time_handymax
            port_time_handymax = waiting_time_hours_handymax + service_time_handymax + handymax.mooring_time
            penalty_time_handymax = max(0, port_time_handymax - handymax.all_turn_time)
            demurrage_time_handymax = penalty_time_handymax * handymax_calls
            demurrage_cost_handymax = demurrage_time_handymax * handymax.demurrage_rate

            handysize = Vessel(**agribulk_defaults.handysize_data)
            service_time_handysize = handysize.call_size / service_rate
            waiting_time_hours_handysize = waiting_factor * service_time_handysize
            port_time_handysize = waiting_time_hours_handysize + service_time_handysize + handysize.mooring_time
            penalty_time_handysize = max(0, port_time_handysize - handysize.all_turn_time)
            demurrage_time_handysize = penalty_time_handysize * handysize_calls
            demurrage_cost_handysize = demurrage_time_handysize * handysize.demurrage_rate

            panamax = Vessel(**agribulk_defaults.panamax_data)
            service_time_panamax = panamax.call_size / service_rate
            waiting_time_hours_panamax = waiting_factor * service_time_panamax
            port_time_panamax = waiting_time_hours_panamax + service_time_panamax + panamax.mooring_time
            penalty_time_panamax = max(0, port_time_panamax - panamax.all_turn_time)
            demurrage_time_panamax = penalty_time_panamax * panamax_calls
            demurrage_cost_panamax = demurrage_time_panamax * panamax.demurrage_rate

        else:
            demurrage_cost_handymax = 0
            demurrage_cost_handysize = 0
            demurrage_cost_panamax = 0

        total_demurrage_cost = demurrage_cost_handymax + demurrage_cost_handysize + demurrage_cost_panamax

        self.demurrage.append(total_demurrage_cost)

    def calculate_revenue(self, year):
        """
        1. calculate the value of the total demand in year (demand * handling fee)
        2. calculate the maximum amount that can be handled (service capacity * operational hours)
        Terminal.revenues is the minimum of 1. and 2.
        """
        # implement a safety factor
        quay_walls = len(core.find_elements(self, Quay_wall))
        crane_cyclic = len(core.find_elements(self, Cyclic_Unloader))
        crane_continuous = len(core.find_elements(self, Continuous_Unloader))
        conveyor_quay = len(core.find_elements(self, Conveyor_Quay))
        storage = len(core.find_elements(self, Storage))
        conveyor_hinter = len(core.find_elements(self, Conveyor_Hinter))
        station = len(core.find_elements(self, Unloading_station))

        if quay_walls < 1 and conveyor_quay < 1 and (
                crane_cyclic > 1 or crane_continuous > 1) and storage < 1 and conveyor_hinter < 1 and station < 1:
            safety_factor = 0
        else:
            safety_factor = 1

        # gather volumes from each commodity, calculate how much revenue it would yield, and add
        revenues = 0
        for commodity in core.find_elements(self, Commodity):
            fee = commodity.handling_fee
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                revenues += (volume * fee * safety_factor)
            except:
                pass
        if self.debug:
            print('     Revenues (demand): {}'.format(revenues))

        handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
            year, handysize, handymax, panamax)

        # find the total service rate,
        service_rate = 0
        for element in (core.find_elements(self, Cyclic_Unloader) + core.find_elements(self, Continuous_Unloader)):
            if year >= element.year_online:
                service_rate += element.effective_capacity * crane_occupancy_online

        # find the rate between volume and throughput
        rate_throughput_volume = service_rate * self.operational_hours / total_vol

        if self.debug:
            print('     Revenues (throughput): {}'.format(
                int(service_rate * self.operational_hours * fee * safety_factor)))

        try:
            self.revenues.append(
                min(revenues * safety_factor, service_rate * self.operational_hours * fee * safety_factor))
        except:
            pass

    # *** General functions
    def calculate_vessel_calls(self, year=2019):
        """Calculate volumes to be transported and the number of vessel calls (both per vessel type and in total) """

        # intialize values to be returned
        handysize_vol = 0
        handymax_vol = 0
        panamax_vol = 0
        total_vol = 0

        # gather volumes from each commodity scenario and calculate how much is transported with which vessel
        commodities = core.find_elements(self, Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                handysize_vol += volume * commodity.handysize_perc / 100
                handymax_vol += volume * commodity.handymax_perc / 100
                panamax_vol += volume * commodity.panamax_perc / 100
                total_vol += volume
            except:
                pass

        # gather vessels and calculate the number of calls each vessel type needs to make
        vessels = core.find_elements(self, Vessel)
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
        list_of_elements_1 = core.find_elements(self, Cyclic_Unloader)
        list_of_elements_2 = core.find_elements(self, Continuous_Unloader)
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
                    (agribulk_defaults.handysize_data["call_size"] / service_rate_planned) +
                     agribulk_defaults.handysize_data["mooring_time"])
            time_at_berth_handymax_planned = handymax_calls * (
                    (agribulk_defaults.handymax_data["call_size"] / service_rate_planned) +
                     agribulk_defaults.handymax_data["mooring_time"])
            time_at_berth_panamax_planned = panamax_calls * (
                    (agribulk_defaults.panamax_data["call_size"] / service_rate_planned) +
                    agribulk_defaults.panamax_data["mooring_time"])

            total_time_at_berth_planned = np.sum(
                [time_at_berth_handysize_planned, time_at_berth_handymax_planned, time_at_berth_panamax_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            berth_occupancy_planned = total_time_at_berth_planned / self.operational_hours

            # estimate crane occupancy
            time_at_crane_handysize_planned = handysize_calls * (
                (agribulk_defaults.handysize_data["call_size"] / service_rate_planned))
            time_at_crane_handymax_planned = handymax_calls * (
                (agribulk_defaults.handymax_data["call_size"] / service_rate_planned))
            time_at_crane_panamax_planned = panamax_calls * (
                (agribulk_defaults.panamax_data["call_size"] / service_rate_planned))

            total_time_at_crane_planned = np.sum(
                [time_at_crane_handysize_planned, time_at_crane_handymax_planned, time_at_crane_panamax_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            crane_occupancy_planned = total_time_at_crane_planned / self.operational_hours

            if service_rate_online != 0:
                time_at_berth_handysize_online = handysize_calls * (
                        (agribulk_defaults.handysize_data["call_size"] / service_rate_online) +agribulk_defaults.handysize_data[
                    "mooring_time"])
                time_at_berth_handymax_online = handymax_calls * (
                        (agribulk_defaults.handymax_data["call_size"] / service_rate_online) +agribulk_defaults.handymax_data[
                    "mooring_time"])
                time_at_berth_panamax_online = panamax_calls * (
                        (agribulk_defaults.panamax_data["call_size"] / service_rate_online) +agribulk_defaults.panamax_data[
                    "mooring_time"])

                total_time_at_berth_online = np.sum(
                    [time_at_berth_handysize_online, time_at_berth_handymax_online, time_at_berth_panamax_online])

                # berth_occupancy is the total time at berth devided by the operational hours
                berth_occupancy_online = min([total_time_at_berth_online / self.operational_hours, 1])

                time_at_crane_handysize_online = handysize_calls * (
                    (agribulk_defaults.handysize_data["call_size"] / service_rate_online))
                time_at_crane_handymax_online = handymax_calls * (
                    (agribulk_defaults.handymax_data["call_size"] / service_rate_online))
                time_at_crane_panamax_online = panamax_calls * (
                    (agribulk_defaults.panamax_data["call_size"] / service_rate_online))

                total_time_at_crane_online = np.sum(
                    [time_at_crane_handysize_online, time_at_crane_handymax_online, time_at_crane_panamax_online])

                # berth_occupancy is the total time at berth devided by the operational hours
                crane_occupancy_online = min([total_time_at_crane_online / self.operational_hours, 1])

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
        """The station occupancy is calculated based on the service rate for the throughput of the online quay unloaders
        (effective capacity * occupancy). The unloading station should at least be able to handle the throughput by the
        online quay unloaders at a level that the station occupancy planned remains below the target occupancy level."""

        list_of_elements = core.find_elements(self, Unloading_station)

        # find the total service rate and determine the time at station
        service_rate_planned = 0
        service_rate_online = 0
        if list_of_elements != []:
            # find planned service rate and online service rate
            for element in list_of_elements:
                service_rate_planned += element.service_rate
                if year >= element.year_online:
                    service_rate_online += element.service_rate

            handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
            berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
                self.calculate_berth_occupancy(year, handysize, handymax, panamax)

            # find the service rate for the throughput of the online quay unloaders (effective capacity * occupancy)
            service_rate_throughput = 0
            for element in (core.find_elements(self, Cyclic_Unloader) + core.find_elements(self, Continuous_Unloader)):
                if year >= element.year_online:
                    service_rate_throughput += element.effective_capacity * crane_occupancy_online

            # determine time at stations planned (given the current throughput)
            if service_rate_planned != 0:
                time_at_station_planned = service_rate_throughput * self.operational_hours / service_rate_planned  # element.service_rate
                station_occupancy_planned = time_at_station_planned / self.operational_hours
            else:
                station_occupancy_planned = float("inf")

            # determine time at stations online (given the current throughput)
            if service_rate_online != 0:
                time_at_station_online = service_rate_throughput * self.operational_hours / service_rate_online  # element.capacity
                station_occupancy_online = time_at_station_online / self.operational_hours
            else:
                station_occupancy_online = float("inf")

        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            station_occupancy_planned = float("inf")
            station_occupancy_online = float("inf")

        return station_occupancy_planned, station_occupancy_online

    def check_crane_slot_available(self):
        list_of_elements = core.find_elements(self, Berth)
        slots = 0
        for element in list_of_elements:
            slots += element.max_cranes

        list_of_elements_1 = core.find_elements(self, Cyclic_Unloader)
        list_of_elements_2 = core.find_elements(self, Continuous_Unloader)
        list_of_elements = list_of_elements_1 + list_of_elements_2

        # when there are more slots than installed cranes ...
        if slots > len(list_of_elements):
            return True
        else:
            return False

    def train_call(self, year):
        """Calculation of the train calls per year, this is calculated from:
        - find out how much throughput there is
        - find out how much cargo the train can transport
        - calculate the numbers of train calls"""

        # create default station object (to get the train call size)
        station = Unloading_station(**agribulk_defaults.hinterland_station_data)

        # - Trains calculated with the throughput
        handysize, handymax, panamax, total_calls, total_vol = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
            self.calculate_berth_occupancy(year, handysize, handymax, panamax)

        service_rate_throughput_online = 0
        for element in (core.find_elements(self, Cyclic_Unloader) + core.find_elements(self, Continuous_Unloader)):
            if year >= element.year_online:
                service_rate_throughput_online += element.effective_capacity * crane_occupancy_online

        train_calls = service_rate_throughput_online * self.operational_hours / station.call_size

        return train_calls

    # *** Plotting functions
    def terminal_elements_plot(self, width=0.1, alpha=0.6, fontsize=20):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = []
        berths = []
        quays = []
        cranes = []
        conveyors_quay = []
        storages = []
        conveyors_hinterland = []
        unloading_station = []

        matplotlib.rcParams.update({'font.size': fontsize})

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            berths.append(0)
            quays.append(0)
            cranes.append(0)
            conveyors_quay.append(0)
            storages.append(0)
            conveyors_hinterland.append(0)
            unloading_station.append(0)

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
                if isinstance(element, Unloading_station):
                    if year >= element.year_online:
                        unloading_station[-1] += 1

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 12))
        ax1.grid(zorder=0, which='major', axis='both')

        colors = ['firebrick', 'darksalmon', 'sandybrown', 'darkkhaki', 'palegreen', 'lightseagreen', 'mediumpurple',
                  'mediumvioletred', 'lightgreen']
        offset = 3 * width

        ax1.bar([x - offset + 0 * width for x in years], berths, zorder=1, width=width, alpha=alpha, label="Berths", color=colors[0], edgecolor='darkgrey')
        ax1.bar([x - offset + 1 * width for x in years], quays, zorder=1, width=width, alpha=alpha, label="Quays", color=colors[1], edgecolor='darkgrey')
        ax1.bar([x - offset + 2 * width for x in years], cranes, zorder=1, width=width, alpha=alpha, label="Cranes", color=colors[2], edgecolor='darkgrey')
        ax1.bar([x - offset + 3 * width for x in years], conveyors_quay, zorder=1, width=width, alpha=alpha, label="Quay converyors", color=colors[3], edgecolor='darkgrey')
        ax1.bar([x - offset + 4 * width for x in years], storages, zorder=1, width=width, alpha=alpha, label="Storages", color=colors[4], edgecolor='darkgrey')
        ax1.bar([x - offset + 5 * width for x in years], conveyors_hinterland, zorder=1, width=width, alpha=alpha, label="Hinterland conveyors", color=colors[5], edgecolor='darkgrey')
        ax1.bar([x - offset + 6 * width for x in years], unloading_station, zorder=1, width=width, alpha=alpha, label="Unloading stations", color=colors[6], edgecolor='darkgrey')

        # added vertical lines for mentioning the different phases
        # plt.axvline(x=2025.6, color='k', linestyle='--')
        # plt.axvline(x=2023.4, color='k', linestyle='--')

        # get demand
        demand = pd.DataFrame()
        demand['year'] = list(range(self.startyear, self.startyear + self.lifecycle))
        demand['demand'] = 0
        for commodity in core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
            except:
                pass

        # #Adding the throughput
        # years = []
        # throughputs_online = []
        #
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     years.append(year)
        #     throughputs_online.append(0)
        #
        #     throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
        #         year)
        #
        #     for element in self.elements:
        #         if isinstance(element, Berth):
        #             if year >= element.year_online:
        #                 throughputs_online[-1] = throughput_online

        # Making a second graph
        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, zorder=2, label="Demand [t/y]", where='mid', color='blue')

        # ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')

        # added boxes
        # props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # # place a text box in upper left in axes coords
        # ax1.text(0.30, 0.60, 'phase 1', transform=ax1.transAxes, fontsize=18, bbox=props)
        # ax1.text(0.55, 0.60, 'phase 2', transform=ax1.transAxes, fontsize=18, bbox=props)
        # ax1.text(0.82, 0.60, 'phase 3', transform=ax1.transAxes, fontsize=18, bbox=props)

        # title and labels
        ax1.set_title('Terminal elements online', fontsize=fontsize)
        ax1.set_xlabel('Years', fontsize=fontsize)
        ax1.set_ylabel('Terminal elements on line [nr]', fontsize=fontsize)
        ax2.set_ylabel('Demand/throughput[t/y]', fontsize=fontsize)

        # ticks and tick labels
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels([int(x) for x in years], rotation='vertical', fontsize=fontsize)
        max_elements = max([max(berths), max(quays), max(cranes),
                            max(conveyors_quay), max(storages),
                            max(conveyors_hinterland), max(conveyors_hinterland)])
        ax1.set_yticks([x for x in range(0, max_elements + 1 + 2, 2)])
        ax1.set_yticklabels([int(x) for x in range(0, max_elements + 1 + 2, 2)], fontsize=fontsize)

        # print legend
        fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=4)
        fig.subplots_adjust(bottom=0.18)

    def terminal_capacity_plot(self, width=0.25, alpha=0.6, fontsize=20):
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
        for commodity in core.find_elements(self, Commodity):
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
        ax.step(years, demand['demand'].values, label="demand", where='mid')

        # title and labels
        ax.set_title('Terminal capacity online ({})'.format(self.crane_type_defaults['crane_type']), fontsize=fontsize)
        ax.set_xlabel('Years', fontsize=fontsize)
        ax.set_ylabel('Throughput capacity [tons/year]', fontsize=fontsize)

        # ticks and tick labels
        ax.set_xticks([x for x in years])
        ax.set_xticklabels([int(x) for x in years], rotation='vertical', fontsize=fontsize)
        ax.yaxis.set_tick_params(labelsize=fontsize)

        # print legend
        fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=4)
        fig.subplots_adjust(bottom=0.18)
