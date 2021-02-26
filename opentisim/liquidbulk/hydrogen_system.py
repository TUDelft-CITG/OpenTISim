# package(s) for data handling
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .hydrogen_defaults import *
from .hydrogen_objects import *
import opentisim


# todo: consider renaming this class to Terminal (seems more appropriate)
class System:
    """This class implements the 'complete supply chain' concept (Van Koningsveld et al, 2021) for liquid bulk
    terminals. The module allows variation of the commodity type, the storage type and the h2retrieval type.
    Terminal development is governed by three triggers: the allowable waiting time as factor of service time,
    the allowable dwell time and an h2retrieval trigger."""

    def __init__(self, startyear=2020, lifecycle=10, operational_hours=5840, debug=False, elements=[],
                 terminal_supply_chain={'berth_jetty', 'pipeline_jetty_-_terminal', 'storage',
                                        'pipeline_terminal_-_hinterland'},
                 commodity_type_defaults=commodity_ammonia_data,
                 storage_type_defaults=storage_nh3_data,
                 kendall='E2/E2/n',
                 allowable_waiting_service_time_ratio_berth=0.5,
                 h2retrieval_type_defaults=h2retrieval_nh3_data,
                 allowable_berth_occupancy=0.5, allowable_dwelltime=14 / 365, h2retrieval_trigger=1):
        # time inputs
        self.years = []
        self.startyear = startyear
        self.lifecycle = lifecycle
        self.operational_hours = operational_hours
        self.terminal_supply_chain = terminal_supply_chain

        # provide intermediate outputs via print statements if debug = True
        self.debug = debug

        # collection of all terminal objects
        self.elements = elements

        # default values to use in selecting which commodity is imported
        self.commodity_type_defaults = commodity_type_defaults
        self.storage_type_defaults = storage_type_defaults
        self.h2retrieval_type_defaults = h2retrieval_type_defaults

        # triggers for the various elements (berth, storage and h2retrieval)
        self.kendall = kendall
        self.allowable_waiting_service_time_ratio_berth = allowable_waiting_service_time_ratio_berth
        self.allowable_berth_occupancy = allowable_berth_occupancy
        self.allowable_dwelltime = allowable_dwelltime
        self.h2retrieval_trigger = h2retrieval_trigger

        # storage variables for revenue
        self.revenues = []

    # *** Overall terminal investment strategy for terminal class.
    def simulate(self):
        """The 'simulate' method implements the terminal investment strategy for this terminal class.

        This method automatically generates investment decisions, parametrically derived from overall demand trends and
        a number of investment triggers.

        Generic approaches based on:
        - Van Koningsveld, M. (Ed.), Verheij, H., Taneja, P. and De Vriend, H.J. (2021). Ports and Waterways.
          Navigating the changing world. TU Delft, Delft, The Netherlands.
        - Van Koningsveld, M. and J. P. M. Mulder. 2004. Sustainable Coastal Policy Developments in the
          Netherlands. A Systematic Approach Revealed. Journal of Coastal Research 20(2), pp. 375-385

        Specific application based on:
        - Stephanie Lanphen, 2019. Hydrogen import terminal. Elaborating the supply chains of a hydrogen import
          terminal, and its corresponding investment decisions. MSc thesis. Delft University of Technology,
          Civil Engineering and Geosciences, Hydraulic Engineering - Ports and Waterways. Delft, the Netherlands

        The simulate method applies frame of reference style decisions while stepping through each year of the terminal
        lifecycle and check if investment is needed (in light of strategic objective, operational objective,
        QSC, decision recipe, intervention method):

           1. for each year estimate the anticipated vessel arrivals based on the expected demand and vessel mix
           2. for each year evaluate which investment are needed given the strategic and operational objectives
           3. for each year calculate the energy costs (requires insight in realized demands)
           4. for each year calculate the demurrage costs (requires insight in realized demands)
           5. for each year calculate terminal revenues (requires insight in realized demands)
           6. for each year calculate the throughput (requires insight in realized demands)
           7. collect all cash flows (capex, opex, revenues)
           8. calculate PV's and aggregate to NPV

        """

        for year in range(self.startyear, self.startyear + self.lifecycle):
            """
            The simulate method is designed according to the following overall objectives for the terminal:
            - strategic objective: To achieve a competitive terminal operation over the terminal lifecycle
            - operational objective: Annually invest in infrastructure upgrades when performance criteria are triggered
            """
            self.years.append(year)
            if self.debug:
                print('')
                print('### Simulate year: {} ############################'.format(year))

            # 1. for each year estimate the anticipated vessel arrivals based on the expected demand
            smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, \
            handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, \
            smallhydrogen_calls_planned, largehydrogen_calls_planned, \
            smallammonia_calls_planned, largeammonia_calls_planned, \
            handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, \
            total_calls_planned, total_vol_planned = self.calculate_vessel_calls(year)

            commodities = opentisim.core.find_elements(self, Commodity)
            for commodity in commodities:
                try:
                    volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                except:
                    pass

            if self.debug:
                print('--- Cargo volume and vessel calls for {} ---------'.format(year))
                print('  Total demand volume: {}'.format(volume))
                print('  Total actual throughput volume: {}'.format(total_vol))
                print('  Total actual vessel calls: {}'.format(total_calls))
                print('     Small Hydrogen calls: {}'.format(smallhydrogen_calls))
                print('     Large Hydrogen calls: {}'.format(largehydrogen_calls))
                print('     Small ammonia calls: {}'.format(smallammonia_calls))
                print('     Large ammonia calls: {}'.format(largeammonia_calls))
                print('     Handysize calls: {}'.format(handysize_calls))
                print('     Panamax calls: {}'.format(panamax_calls))
                print('     VLCC calls: {}'.format(vlcc_calls))
                print('----------------------------------------------------')

            # 2. for each year evaluate which investment are needed given the strategic and operational objectives
            if 'berth_jetty' in self.terminal_supply_chain:
                self.berth_invest(year)

            if 'pipeline_jetty_-_terminal' in self.terminal_supply_chain:
                if self.debug:
                    print('')
                    print('$$$ Check pipeline jetty ---------------------------')
                self.pipeline_jetty_invest(year)

            if 'storage' in self.terminal_supply_chain:
                if self.debug:
                    print('')
                    print('$$$ Check storage ----------------------------------')
                self.storage_invest(year, self.storage_type_defaults)

            if 'mch_2_h2_retrieval' in self.terminal_supply_chain:
                if self.debug:
                    print('')
                    print('$$$ Check H2 retrieval plants ----------------------')
                self.h2retrieval_invest(year, self.h2retrieval_type_defaults)

            if 'pipeline_terminal_-_hinterland' in self.terminal_supply_chain:
                if self.debug:
                    print('')
                    print('$$$ Check pipeline hinterland ----------------------')
                self.pipeline_hinter_invest(year)

        # 3. for each year calculate the energy costs (requires insight in realized demands)
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_energy_cost(year)

        # 4. for each year calculate the demurrage costs (requires insight in realized demands)
        self.demurrage = []
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_demurrage_cost(year)

        # 5.  for each year calculate terminal revenues
        self.revenues = []
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_revenue(year, self.commodity_type_defaults)

        # 6. for each year calculate the throughput (requires insight in realized demands)
        self.throughputonline = []
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.throughput_elements(year)

        # # 7. collect all cash flows (capex, opex, revenues)
        # cash_flows, cash_flows_WACC_nominal = self.add_cashflow_elements()

        # 8. calculate PV's and aggregate to NPV
        opentisim.core.NPV(self, Labour(**labour_data))

    # *** Individual investment methods for terminal elements
    def berth_invest(self, year):
        """
        Given the overall objectives of the terminal

        Decision recipe Berth:
        QSC: waiting_factor
        Problem evaluation: there is a problem if the waiting_factor > allowable_waiting_service_time_ratio_berth
            - allowable_berth_occupancy = .50 # 50%
            - a berth needs:
               - a jetty
            - berth occupancy depends on:
                - total_calls and total_vol
                - total_service_capacity as delivered by the vessels
        Investment decisions: invest enough to make the waiting_factor < allowable_waiting_service_time_ratio_berth
            - adding jettys decreases waiting_factor
        """

        # report on the status of all berth elements
        if self.debug:
            print('')
            print('--- Status terminal @ start of year ----------------')

        opentisim.core.report_element(self, Berth, year)
        opentisim.core.report_element(self, Jetty, year)
        opentisim.core.report_element(self, Pipeline_Jetty, year)
        opentisim.core.report_element(self, Storage, year)
        opentisim.core.report_element(self, H2retrieval, year)
        opentisim.core.report_element(self, Pipeline_Hinter, year)

        # calculate vessel calls
        # todo: store output in a class, rather than all these individual items
        smallhydrogen_calls, largehydrogen_calls, \
        smallammonia_calls, largeammonia_calls, \
        handysize_calls, panamax_calls, vlcc_calls, \
        total_calls, total_vol, \
        smallhydrogen_calls_planned, largehydrogen_calls_planned, \
        smallammonia_calls_planned, largeammonia_calls_planned, \
        handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, \
        total_calls_planned, total_vol_planned = self.calculate_vessel_calls(year)

        # calculate berth occupancy
        berth_occupancy_planned, berth_occupancy_online, \
        unloading_occupancy_planned, unloading_occupancy_online = \
            self.calculate_berth_occupancy(
                year,
                smallhydrogen_calls, largehydrogen_calls,
                smallammonia_calls, largeammonia_calls,
                handysize_calls, panamax_calls, vlcc_calls,
                smallhydrogen_calls_planned, largehydrogen_calls_planned,
                smallammonia_calls_planned, largeammonia_calls_planned,
                handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned)

        # calculate throughput
        throughput_online, throughput_planned, \
        throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, \
        throughput_planned_h2retrieval, throughput_planned_pipeh = \
            self.throughput_elements(year)

        # calculate waiting_factor
        berths = len(opentisim.core.find_elements(self, Berth))
        if berths != 0:
            waiting_factor = \
                opentisim.core.occupancy_to_waitingfactor(utilisation=berth_occupancy_planned,
                                                          nr_of_servers_to_chk=berths, kendall=self.kendall)
        else:
            waiting_factor = np.inf

        if self.debug:
            # print('     Berth occupancy planned (@ start of year): {:.2f} (trigger level: {:.2f})'.format(
            #     berth_occupancy_planned, self.allowable_berth_occupancy))
            print('     Unloading occupancy planned (@ start of year): {:.2f}'.format(unloading_occupancy_planned))
            print('     waiting time as factor of service time (@ start of year): {:.2f}'.format(waiting_factor))
            print('     throughput planned {:.2f}'.format(throughput_planned))

            print('')
            print('--- Start investment analysis ----------------------')
            print('')
            print('$$$ Check berth elements ---------------------------')

        opentisim.core.report_element(self, Berth, year)
        opentisim.core.report_element(self, Jetty, year)
        opentisim.core.report_element(self, Pipeline_Jetty, year)

        while waiting_factor > self.allowable_waiting_service_time_ratio_berth:

            # while planned berth occupancy is too large add a berth when no crane slots are available
            # NB: this setup makes sense here since there can be only one jetty per berth (compare containers)
            if self.debug:
                print('  *** add Berth to elements')
            berth = Berth(**berth_data)
            berth.year_online = year + berth.delivery_time
            self.elements.append(berth)

            # commented out: checking occupancy after adding a berth makes no sense in this setup
            # berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = \
            #     self.calculate_berth_occupancy(year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls,
            #                                    largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls,
            #                                    smallhydrogen_calls_planned, largehydrogen_calls_planned,
            #                                    smallammonia_calls_planned, largeammonia_calls_planned,
            #                                    handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned)
            #
            # print(berth_occupancy_planned)
            #
            # waiting_factor = opentisim.core.occupancy_to_waitingfactor(utilisation=berth_occupancy_planned,
            #                                               nr_of_servers_to_chk=berths, kendall=self.kendall)

            if self.debug:
                # print('     Berth occupancy planned (after adding berth): {:.2f} (trigger level: {:.2f})'.format(
                #     berth_occupancy_planned, self.allowable_berth_occupancy))
                print('     Waiting time as factor of service time (after adding berth): {:.2f} (trigger level: {:.2f})'.format(waiting_factor,
                                                                                                     self.allowable_waiting_service_time_ratio_berth))

                # print('     Berth occupancy planned (after adding berth): {:.2f}'.format(berth_occupancy_planned))
                # print('     Berth occupancy online (after adding berth): {}'.format(berth_occupancy_online))

            # while planned berth occupancy is too large add a berth if a jetty is needed
            berths = len(opentisim.core.find_elements(self, Berth))
            jettys = len(opentisim.core.find_elements(self, Jetty))

            # todo: check and add reference (check Lanphen (2019)?)
            if berths > jettys:
                length_max = max(vlcc_data["LOA"], handysize_data["LOA"],
                                 panamax_data["LOA"], smallhydrogen_data["LOA"],
                                 largehydrogen_data["LOA"], smallammonia_data["LOA"],
                                 largeammonia_data["LOA"])  # maximum of all vessels
                length_min = min(vlcc_data["LOA"], handysize_data["LOA"],
                                 panamax_data["LOA"], smallhydrogen_data["LOA"],
                                 largehydrogen_data["LOA"], smallammonia_data["LOA"],
                                 largeammonia_data["LOA"])  # maximum of all vessels
                if length_max - length_min > 100:
                    nrofdolphins = 8
                else:
                    nrofdolphins = 6

                # activate jetty_invest
                self.jetty_invest(year, nrofdolphins)

                # recheck occupancies and waiting factors (while loop will exit if condition is met)
                berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy(
                    year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls,
                    handysize_calls, panamax_calls, vlcc_calls, smallhydrogen_calls_planned,
                    largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned,
                    handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned)

                waiting_factor = opentisim.core.occupancy_to_waitingfactor(utilisation=berth_occupancy_planned,
                                                              nr_of_servers_to_chk=berths, kendall=self.kendall)

                if self.debug:
                    # print('     Berth occupancy planned (after adding jetty): {:.2f} (trigger level: {:.2f})'.format(
                    #     berth_occupancy_planned, self.allowable_berth_occupancy))
                    print('     Waiting time as factor of service time (after adding jetty): {:.2f} (trigger level: {:.2f})'.format(waiting_factor,
                                                                                                     self.allowable_waiting_service_time_ratio_berth))

    def jetty_invest(self, year, nrofdolphins):
        """
        *** Decision recipe jetty (NB: triggered in berth_invest): ***
        QSC: jettys, berths
        problem evaluation: there is a problem if the berths > jettys
        investment decisions: invest until not(berths > jettys)
            - adding jetty will increase jettys
        """

        if self.debug:
            print('  *** add jetty to elements')
        # add a Jetty element
        jetty = Jetty(**jetty_data)

        # - capex
        unit_rate = int((nrofdolphins * jetty.mooring_dolphins) + (jetty.Gijt_constant_jetty * jetty.jettywidth *
                                                                   jetty.jettylength) + (jetty.Catwalk_rate *
                                                                                         jetty.catwalklength * jetty.catwalkwidth))
        mobilisation = int(max((unit_rate * jetty.mobilisation_perc), jetty.mobilisation_min))
        jetty.capex = int(unit_rate + mobilisation)

        # - opex
        jetty.insurance = unit_rate * jetty.insurance_perc
        jetty.maintenance = unit_rate * jetty.maintenance_perc
        jetty.year_online = year + jetty.delivery_time

        # residual
        jetty.assetvalue = (unit_rate) * (1 - ((self.lifecycle + self.startyear - jetty.year_online) / jetty.lifespan))
        jetty.residual = max(jetty.assetvalue, 0)

        # add cash flow information to jetty object in a dataframe
        jetty = opentisim.core.add_cashflow_data_to_element(self, jetty)

        self.elements.append(jetty)

    def pipeline_jetty_invest(self, year):
        """current strategy is to add pipeline as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        # find the total service rate
        service_capacity = 0
        service_capacity_online = 0
        list_of_elements = opentisim.core.find_elements(self, Pipeline_Jetty)
        if list_of_elements != []:
            for element in list_of_elements:
                service_capacity += element.capacity
                if year >= element.year_online:
                    service_capacity_online += element.capacity

        # find the year online,
        years_online = []
        for element in opentisim.core.find_elements(self, Jetty):
            years_online.append(element.year_online)

        # # check if total planned capacity is smaller than target capacity, if so add a pipeline
        pipelines = len(opentisim.core.find_elements(self, Pipeline_Jetty))
        jettys = len(opentisim.core.find_elements(self, Jetty))
        if jettys > pipelines:
            if self.debug:
                print('  *** add jetty pipeline to elements')
            pipeline_jetty = Pipeline_Jetty(**jetty_pipeline_data)

            # - capex
            unit_rate = pipeline_jetty.unit_rate_factor * pipeline_jetty.length
            mobilisation = pipeline_jetty.mobilisation
            pipeline_jetty.capex = int(unit_rate + mobilisation)

            # - opex
            pipeline_jetty.insurance = unit_rate * pipeline_jetty.insurance_perc
            pipeline_jetty.maintenance = unit_rate * pipeline_jetty.maintenance_perc

            #   labour
            labour = Labour(**labour_data)
            pipeline_jetty.shift = (pipeline_jetty.crew * self.operational_hours) / (
                        labour.shift_length * labour.annual_shifts)
            pipeline_jetty.labour = pipeline_jetty.shift * labour.operational_salary

            # # find the total service rate,
            service_rate = 0
            years_online = []
            for element in opentisim.core.find_elements(self, Jetty):
                service_rate += largehydrogen_data["pump_capacity"]
                years_online.append(element.year_online)

            # there should always be a new jetty in the planning
            new_jetty_years = [x for x in years_online if x >= year]

            # find the maximum online year of pipeline_jetty or make it []
            if opentisim.core.find_elements(self, Pipeline_Jetty) != []:
                max_pipeline_years = max([x.year_online for x in opentisim.core.find_elements(self, Pipeline_Jetty)])
            else:
                max_pipeline_years = []

            # decide what online year to use
            if max_pipeline_years == []:
                pipeline_jetty.year_online = min(new_jetty_years)
            elif max_pipeline_years < min(new_jetty_years):
                pipeline_jetty.year_online = min(new_jetty_years)
            elif max_pipeline_years == min(new_jetty_years):
                pipeline_jetty.year_online = max(new_jetty_years)
            elif max_pipeline_years > min(new_jetty_years):
                pipeline_jetty.year_online = max(new_jetty_years)

            # pipeline_jetty.year_online = year
            # residual
            pipeline_jetty.assetvalue = unit_rate * (
                        1 - (self.lifecycle + self.startyear - pipeline_jetty.year_online) / pipeline_jetty.lifespan)
            pipeline_jetty.residual = max(pipeline_jetty.assetvalue, 0)

            # add cash flow information to pipeline_jetty object in a dataframe
            pipeline_jetty = opentisim.core.add_cashflow_data_to_element(self, pipeline_jetty)

            self.elements.append(pipeline_jetty)

    def storage_invest(self, year, hydrogen_defaults_storage_data):
        """current strategy is to add storage as long as target storage is not yet achieved
        - find out how much storage is online
        - find out how much storage is planned
        - find out how much storage is needed
        - add storage until target is reached
        """

        # from all storage objects sum online capacity
        storage_capacity = 0
        storage_capacity_online = 0
        list_of_elements = opentisim.core.find_elements(self, Storage)
        if list_of_elements != []:
            for element in list_of_elements:
                #                 storage_capacity += element.capacity
                #                 if year >= element.year_online:
                #                     storage_capacity_online += element.capacity
                if element.type == hydrogen_defaults_storage_data['type']:
                    storage_capacity += element.capacity
                    if year >= element.year_online:
                        storage_capacity_online += element.capacity

        if self.debug:
            print('     a total of {} ton of {} storage capacity is online; {} ton total planned'.format(
                storage_capacity_online, hydrogen_defaults_storage_data['type'], storage_capacity))

        # max_vessel_call_size = max([x.call_size for x in opentisim.core.find_elements(self, Vessel)])
        max_vessel_call_size = largeammonia_data["call_size"]

        Demand = []
        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        storage_capacity_dwelltime_demand = (Demand * self.allowable_dwelltime) * 1.1  # IJzerman p.26

        # find the total throughput
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
            year)

        # print('troughput planned storage',throughput_planned_storage, 'in year', year )
        storage_capacity_dwelltime_throughput = (
                                                            throughput_planned_storage * self.allowable_dwelltime) * 1.1  # IJzerman p.26
        #  or
        # check if sufficient storage capacity is available
        while storage_capacity < max_vessel_call_size or (
                storage_capacity < storage_capacity_dwelltime_demand and storage_capacity < storage_capacity_dwelltime_throughput):
            if self.debug:
                print('  *** add storage to elements')

            # add storage object
            storage = Storage(**hydrogen_defaults_storage_data)

            # - capex
            storage.capex = storage.unit_rate + storage.mobilisation_min

            # - opex
            storage.insurance = storage.unit_rate * storage.insurance_perc
            storage.maintenance = storage.unit_rate * storage.maintenance_perc

            #   labour**hydrogen_defaults
            labour = Labour(**labour_data)
            storage.shift = (
                        (storage.crew_for5 * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            storage.labour = storage.shift * labour.operational_salary

            jettys = opentisim.core.find_elements(self, opentisim.liquidbulk.Jetty)
            jetty_year_online = 0
            for jetty in jettys:
                jetty_year_online = np.max([jetty_year_online, jetty.year_online])

            storage.year_online = np.max([jetty_year_online, year + storage.delivery_time])
            # # elif year == self.startyear + 1:
            # # storage.year_online = year + 1
            #
            # # todo: make startyear altijd
            # if self.lifecycle > 1:
            #     if year == self.startyear:
            #         storage.year_online = year + jetty.delivery_time
            #     # elif year == self.startyear + 1:
            #     # storage.year_online = year + 1
            #     elif year == self.startyear + jetty.delivery_time:
            #         storage.year_online = year
            #     else:
            #         storage.year_online = year + storage.delivery_time
            #
            # elif self.lifecycle == 1:
            #     if self.startyear == self.years[0]:
            #         storage.year_online = year + jetty.delivery_time
            #         # elif self.startyear == self.years[1]:
            #         # storage.year_online = year + 1
            #     elif self.startyear == self.years[jetty.delivery_time]:
            #         storage.year_online = year
            #     else:
            #         storage.year_online = year + storage.delivery_time

            # #reinvestment
            # if year == storage.year_online + storage.lifespan:

            # residual
            storage.assetvalue = storage.unit_rate * (
                        1 - ((self.lifecycle + self.startyear - storage.year_online) / storage.lifespan))
            storage.residual = max(storage.assetvalue, 0)

            # add cash flow information to storage object in a dataframe
            storage = opentisim.core.add_cashflow_data_to_element(self, storage)

            self.elements.append(storage)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
                year)

            storage_capacity_dwelltime_throughput = (throughput_planned_storage * self.allowable_dwelltime) * 1.1

            storage_capacity += storage.capacity

            if self.debug:
                print('     a total of {} ton of {} storage capacity is online; {} ton total planned'.format(
                    storage_capacity_online, hydrogen_defaults_storage_data['type'], storage_capacity))

    def h2retrieval_invest(self, year, hydrogen_defaults_h2retrieval_data):
        """current strategy is to add h2 retrieval as long as target h2 retrieval is not yet achieved
        - find out how much h2 retrieval is online
        - find out how much h2 retrieval is planned
        - find out how much h2 retrieval is needed
        - add h2 retrieval until target is reached
        """

        plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(
            year, hydrogen_defaults_h2retrieval_data)

        if self.debug:
            print('     Plant occupancy planned (@ start of year): {:.2f}'.format(plant_occupancy_planned))
            print('     Plant occupancy online (@ start of year): {:.2f}'.format(plant_occupancy_online))

        # check if sufficient h2retrieval capacity is available
        while plant_occupancy_planned > self.h2retrieval_trigger:

            if self.debug:
                print('  *** add h2retrieval to elements')

            # add h2retrieval object
            h2retrieval = H2retrieval(**hydrogen_defaults_h2retrieval_data)

            # - capex
            h2retrieval.capex = h2retrieval.unit_rate + h2retrieval.mobilisation_min

            # - opex
            h2retrieval.insurance = h2retrieval.unit_rate * h2retrieval.insurance_perc
            h2retrieval.maintenance = h2retrieval.unit_rate * h2retrieval.maintenance_perc

            #   labour**hydrogen_defaults
            labour = Labour(**labour_data)
            h2retrieval.shift = (
                        (h2retrieval.crew_for5 * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            h2retrieval.labour = h2retrieval.shift * labour.operational_salary

            jetty = Jetty(**jetty_data)

            if year == self.startyear + jetty.delivery_time:
                h2retrieval.year_online = year
            else:
                h2retrieval.year_online = year + h2retrieval.delivery_time

            # residual
            h2retrieval.assetvalue = h2retrieval.unit_rate * (
                    1 - (self.lifecycle + self.startyear - h2retrieval.year_online) / h2retrieval.lifespan)
            h2retrieval.residual = max(h2retrieval.assetvalue, 0)

            # add cash flow information to h2retrieval object in a dataframe
            h2retrieval = opentisim.core.add_cashflow_data_to_element(self, h2retrieval)

            self.elements.append(h2retrieval)

            plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(
                year, hydrogen_defaults_h2retrieval_data)

            if self.debug:
                print(
                    '     a total of {} ton of h2retrieval capacity is online; {} ton total planned'.format(
                        h2retrieval_capacity_online, h2retrieval_capacity_planned))

    def pipeline_hinter_invest(self, year):
        """current strategy is to add pipeline as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        # find the total service rate
        service_capacity = 0
        service_capacity_online_hinter = 0
        list_of_elements_pipeline = opentisim.core.find_elements(self, Pipeline_Hinter)
        if list_of_elements_pipeline != []:
            for element in list_of_elements_pipeline:
                service_capacity += element.capacity
                if year >= element.year_online:
                    service_capacity_online_hinter += element.capacity

        # find the total service rate,
        service_rate = 0
        years_online = []
        for element in (opentisim.core.find_elements(self, H2retrieval)):
            service_rate += element.capacity
            years_online.append(element.year_online)

        # check if total planned length is smaller than target length, if so add a pipeline
        while service_rate > service_capacity:
            if self.debug:
                print('  *** add Hinter Pipeline to elements')

            pipeline_hinter = Pipeline_Hinter(**hinterland_pipeline_data)

            # - capex
            capacity = pipeline_hinter.capacity
            unit_rate = pipeline_hinter.unit_rate_factor * pipeline_hinter.length
            mobilisation = pipeline_hinter.mobilisation
            pipeline_hinter.capex = int(unit_rate + mobilisation)

            # - opex
            pipeline_hinter.insurance = unit_rate * pipeline_hinter.insurance_perc
            pipeline_hinter.maintenance = unit_rate * pipeline_hinter.maintenance_perc

            # - labour
            labour = Labour(**labour_data)
            pipeline_hinter.shift = (
                    (pipeline_hinter.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            pipeline_hinter.labour = pipeline_hinter.shift * labour.operational_salary

            if year == self.startyear:
                pipeline_hinter.year_online = year + pipeline_hinter.delivery_time + 1
            else:
                pipeline_hinter.year_online = year + pipeline_hinter.delivery_time

            # residual
            pipeline_hinter.assetvalue = unit_rate * (
                    1 - (self.lifecycle + self.startyear - pipeline_hinter.year_online) / pipeline_hinter.lifespan)
            pipeline_hinter.residual = max(pipeline_hinter.assetvalue, 0)

            # add cash flow information to pipeline_hinter object in a dataframe
            pipeline_hinter = opentisim.core.add_cashflow_data_to_element(self, pipeline_hinter)

            self.elements.append(pipeline_hinter)

            service_capacity += pipeline_hinter.capacity

        if self.debug:
            print(
                '     a total of {} ton of pipeline hinterland service capacity is online; {} ton total planned'.format(
                    service_capacity_online_hinter, service_capacity))

    # *** Energy costs, demurrage costs and revenue calculation methods
    def calculate_energy_cost(self, year):
        """
        The energy cost of all different element are calculated.
        1. At first find the consumption, capacity and working hours per element
        2. Find the total energy price to multiply the consumption with the energy price
        """

        energy = Energy(**energy_data)
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
            year)

        # calculate pipeline jetty energy
        list_of_elements_Pipelinejetty = opentisim.core.find_elements(self, Pipeline_Jetty)

        pipelinesj = 0
        for element in list_of_elements_Pipelinejetty:
            if year >= element.year_online:
                pipelinesj += 1
                consumption = throughput_online / pipelinesj * element.consumption_coefficient

                if consumption * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * energy.price

            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate storage energy
        list_of_elements_Storage = opentisim.core.find_elements(self, Storage)
        max_vessel_call_size = largeammonia_data["call_size"]
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
            year)
        storage_capacity_dwelltime_throughput = (throughput_online * self.allowable_dwelltime) * 1.1

        for element in list_of_elements_Storage:
            if year >= element.year_online:
                consumption = element.consumption
                hours = self.operational_hours
                capacity = max(max_vessel_call_size, storage_capacity_dwelltime_throughput)

                if consumption * capacity * hours * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * capacity * energy.price

            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate H2 retrieval energy
        list_of_elements_H2retrieval = opentisim.core.find_elements(self, H2retrieval)

        # find the total throughput,
        # throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(year)
        hydrogen_defaults_h2retrieval_data = self.h2retrieval_type_defaults
        plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(
            year, hydrogen_defaults_h2retrieval_data)

        for element in list_of_elements_H2retrieval:
            if year >= element.year_online:
                consumption = element.consumption
                capacity = element.capacity * self.operational_hours

                if consumption * throughput_online * energy.price != np.inf:
                    element.df.loc[element.df[
                                       'year'] == year, 'energy'] = consumption * plant_occupancy_online * capacity * energy.price
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate hinterland pipeline energy
        list_of_elements_hinter = opentisim.core.find_elements(self, Pipeline_Hinter)

        plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(
            year, hydrogen_defaults_h2retrieval_data)

        pipelines = 0
        for element in list_of_elements_hinter:
            if year >= element.year_online:
                pipelines += 1
                consumption = element.consumption_coefficient

                if consumption * energy.price != np.inf:
                    element.df.loc[element.df[
                                       'year'] == year, 'energy'] = consumption * throughput_online / pipelines * energy.price
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

    def calculate_demurrage_cost(self, year):
        """Find the demurrage cost per type of vessel and sum all demurrage cost"""

        smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned, total_vol_planned = self.calculate_vessel_calls(
            year)
        berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy(
            year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls,
            panamax_calls, vlcc_calls, smallhydrogen_calls_planned, largehydrogen_calls_planned,
            smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned,
            vlcc_calls_planned)

        berths = len(opentisim.core.find_elements(self, Berth))

        waiting_factor = opentisim.core.occupancy_to_waitingfactor(utilisation=berth_occupancy_online,
                                                                   nr_of_servers_to_chk=berths, kendall=self.kendall)

        # waiting_time_hours = waiting_factor * unloading_occupancy_online * self.operational_hours / total_calls

        # Find the demurrage cost per type of vessel
        # if service_rate != 0:
        smallhydrogen = Vessel(**smallhydrogen_data)
        service_time_smallhydrogen = smallhydrogen.call_size / smallhydrogen.pump_capacity
        waiting_time_hours_smallhydrogen = waiting_factor * service_time_smallhydrogen
        penalty_time_smallhydrogen = max(0, waiting_time_hours_smallhydrogen - smallhydrogen.all_turn_time)
        demurrage_time_smallhydrogen = penalty_time_smallhydrogen * smallhydrogen_calls
        demurrage_cost_smallhydrogen = demurrage_time_smallhydrogen * smallhydrogen.demurrage_rate

        largehydrogen = Vessel(**largehydrogen_data)
        service_time_largehydrogen = largehydrogen.call_size / largehydrogen.pump_capacity
        waiting_time_hours_largehydrogen = waiting_factor * service_time_largehydrogen
        penalty_time_largehydrogen = max(0, waiting_time_hours_largehydrogen - largehydrogen.all_turn_time)
        demurrage_time_largehydrogen = penalty_time_largehydrogen * largehydrogen_calls
        demurrage_cost_largehydrogen = demurrage_time_largehydrogen * largehydrogen.demurrage_rate

        smallammonia = Vessel(**smallammonia_data)
        service_time_smallammonia = smallammonia.call_size / smallammonia.pump_capacity
        waiting_time_hours_smallammonia = waiting_factor * service_time_smallammonia
        penalty_time_smallammonia = max(0, waiting_time_hours_smallammonia - smallammonia.all_turn_time)
        demurrage_time_smallammonia = penalty_time_smallammonia * smallammonia_calls
        demurrage_cost_smallammonia = demurrage_time_smallammonia * smallammonia.demurrage_rate

        largeammonia = Vessel(**largeammonia_data)
        service_time_largeammonia = largeammonia.call_size / largeammonia.pump_capacity
        waiting_time_hours_largeammonia = waiting_factor * service_time_largeammonia
        penalty_time_largeammonia = max(0, waiting_time_hours_largeammonia - largeammonia.all_turn_time)
        demurrage_time_largeammonia = penalty_time_largeammonia * largeammonia_calls
        demurrage_cost_largeammonia = demurrage_time_largeammonia * largeammonia.demurrage_rate

        handysize = Vessel(**handysize_data)
        service_time_handysize = handysize.call_size / handysize.pump_capacity
        waiting_time_hours_handysize = waiting_factor * service_time_handysize
        penalty_time_handysize = max(0, waiting_time_hours_handysize - handysize.all_turn_time)
        demurrage_time_handysize = penalty_time_handysize * handysize_calls
        demurrage_cost_handysize = demurrage_time_handysize * handysize.demurrage_rate

        panamax = Vessel(**panamax_data)
        service_time_panamax = panamax.call_size / panamax.pump_capacity
        waiting_time_hours_panamax = waiting_factor * service_time_panamax
        penalty_time_panamax = max(0, waiting_time_hours_panamax - panamax.all_turn_time)
        demurrage_time_panamax = penalty_time_panamax * panamax_calls
        demurrage_cost_panamax = demurrage_time_panamax * panamax.demurrage_rate

        vlcc = Vessel(**vlcc_data)
        service_time_vlcc = vlcc.call_size / vlcc.pump_capacity
        waiting_time_hours_vlcc = waiting_factor * service_time_vlcc
        penalty_time_vlcc = max(0, waiting_time_hours_vlcc - vlcc.all_turn_time)
        demurrage_time_vlcc = penalty_time_vlcc * vlcc_calls
        demurrage_cost_vlcc = demurrage_time_vlcc * vlcc.demurrage_rate

        total_demurrage_cost = demurrage_cost_smallhydrogen + demurrage_cost_largehydrogen + demurrage_cost_smallammonia + demurrage_cost_largeammonia + demurrage_cost_handysize + demurrage_cost_panamax + demurrage_cost_vlcc

        self.demurrage.append(total_demurrage_cost)

    def calculate_revenue(self, year, hydrogen_defaults_commodity_data):
        """
        1. calculate the value of the total throughput in year (throughput * handling fee)
        """

        # gather the fee from the selected commodity
        commodity = Commodity(**hydrogen_defaults_commodity_data)
        fee = commodity.handling_fee

        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
            year)
        if self.debug:
            print('     Revenues: {}'.format(int(throughput_online * fee)))

        try:
            self.revenues.append(throughput_online * fee)
        except:
            pass

    # *** General functions
    def calculate_vessel_calls(self, year=2019):
        """Calculate volumes to be transported and the number of vessel calls (both per vessel type and in total) """

        # intialize values to be returned
        smallhydrogen_vol = 0
        largehydrogen_vol = 0
        smallammonia_vol = 0
        largeammonia_vol = 0
        handysize_vol = 0
        panamax_vol = 0
        vlcc_vol = 0
        total_vol = 0
        smallhydrogen_vol_planned = 0
        largehydrogen_vol_planned = 0
        smallammonia_vol_planned = 0
        largeammonia_vol_planned = 0
        handysize_vol_planned = 0
        panamax_vol_planned = 0
        vlcc_vol_planned = 0
        total_vol_planned = 0

        # gather volumes from each commodity scenario and calculate how much is transported with which vessel
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
            year)

        commodities = opentisim.core.find_elements(self, Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                smallhydrogen_vol += volume / volume * throughput_online * commodity.smallhydrogen_perc / 100
                largehydrogen_vol += volume / volume * throughput_online * commodity.largehydrogen_perc / 100
                smallammonia_vol += volume / volume * throughput_online * commodity.smallammonia_perc / 100
                largeammonia_vol += volume / volume * throughput_online * commodity.largeammonia_perc / 100
                handysize_vol += volume / volume * throughput_online * commodity.handysize_perc / 100
                panamax_vol += volume / volume * throughput_online * commodity.panamax_perc / 100
                vlcc_vol += volume / volume * throughput_online * commodity.vlcc_perc / 100
                total_vol += volume / volume * throughput_online
            except:
                pass

        # gather vessels and calculate the number of calls each vessel type needs to make
        vessels = opentisim.core.find_elements(self, Vessel)
        for vessel in vessels:
            if vessel.type == 'Smallhydrogen':
                smallhydrogen_calls = int(np.ceil(smallhydrogen_vol / vessel.call_size))
            elif vessel.type == 'Largehydrogen':
                largehydrogen_calls = int(np.ceil(largehydrogen_vol / vessel.call_size))
            elif vessel.type == 'Smallammonia':
                smallammonia_calls = int(np.ceil(smallammonia_vol / vessel.call_size))
            elif vessel.type == 'Largeammonia':
                largeammonia_calls = int(np.ceil(largeammonia_vol / vessel.call_size))
            elif vessel.type == 'Handysize':
                handysize_calls = int(np.ceil(handysize_vol / vessel.call_size))
            elif vessel.type == 'Panamax':
                panamax_calls = int(np.ceil(panamax_vol / vessel.call_size))
            elif vessel.type == 'VLCC':
                vlcc_calls = int(np.ceil(vlcc_vol / vessel.call_size))
        total_calls = np.sum(
            [smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls,
             panamax_calls, vlcc_calls])

        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                smallhydrogen_vol_planned += volume * commodity.smallhydrogen_perc / 100
                largehydrogen_vol_planned += volume * commodity.largehydrogen_perc / 100
                smallammonia_vol_planned += volume * commodity.smallammonia_perc / 100
                largeammonia_vol_planned += volume * commodity.largeammonia_perc / 100
                handysize_vol_planned += volume * commodity.handysize_perc / 100
                panamax_vol_planned += volume * commodity.panamax_perc / 100
                vlcc_vol_planned += volume * commodity.vlcc_perc / 100
                total_vol_planned += volume
            except:
                pass

        for vessel in vessels:
            if vessel.type == 'Smallhydrogen':
                smallhydrogen_calls_planned = int(np.ceil(smallhydrogen_vol_planned / vessel.call_size))
            elif vessel.type == 'Largehydrogen':
                largehydrogen_calls_planned = int(np.ceil(largehydrogen_vol_planned / vessel.call_size))
            elif vessel.type == 'Smallammonia':
                smallammonia_calls_planned = int(np.ceil(smallammonia_vol_planned / vessel.call_size))
            elif vessel.type == 'Largeammonia':
                largeammonia_calls_planned = int(np.ceil(largeammonia_vol_planned / vessel.call_size))
            elif vessel.type == 'Handysize':
                handysize_calls_planned = int(np.ceil(handysize_vol_planned / vessel.call_size))
            elif vessel.type == 'Panamax':
                panamax_calls_planned = int(np.ceil(panamax_vol_planned / vessel.call_size))
            elif vessel.type == 'VLCC':
                vlcc_calls_planned = int(np.ceil(vlcc_vol_planned / vessel.call_size))
        total_calls_planned = np.sum(
            [smallhydrogen_calls_planned, largehydrogen_calls_planned,
             smallammonia_calls_planned, largeammonia_calls_planned,
             handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned])

        return smallhydrogen_calls, largehydrogen_calls, \
               smallammonia_calls, largeammonia_calls, \
               handysize_calls, panamax_calls, vlcc_calls, \
               total_calls, total_vol, \
               smallhydrogen_calls_planned, largehydrogen_calls_planned, \
               smallammonia_calls_planned, largeammonia_calls_planned, \
               handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, \
               total_calls_planned, total_vol_planned

    def calculate_berth_occupancy(self, year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls,
                                  largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls,
                                  smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned,
                                  largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned,
                                  vlcc_calls_planned):
        """- Find all cranes and sum their effective_capacity to get service_capacity
        - Divide callsize_per_vessel by service_capacity and add mooring time to get total time at berth
        - Occupancy is total_time_at_berth divided by operational hours
        """

        # list all vessel objects in system
        list_of_elements = opentisim.core.find_elements(self, Jetty)

        # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        nr_of_jetty_planned = 0
        nr_of_jetty_online = 0
        if list_of_elements != []:
            for element in list_of_elements:
                nr_of_jetty_planned += 1
                if year >= element.year_online:
                    nr_of_jetty_online += 1

            # estimate berth occupancy
            time_at_berth_smallhydrogen_planned = smallhydrogen_calls_planned * (
                    (smallhydrogen_data["call_size"] / smallhydrogen_data["pump_capacity"]) +
                    smallhydrogen_data["mooring_time"])
            time_at_berth_largehydrogen_planned = largehydrogen_calls_planned * (
                    (largehydrogen_data["call_size"] / largehydrogen_data["pump_capacity"]) +
                    largehydrogen_data["mooring_time"])
            time_at_berth_smallammonia_planned = smallammonia_calls_planned * (
                    (smallammonia_data["call_size"] / smallammonia_data["pump_capacity"]) +
                    smallammonia_data["mooring_time"])
            time_at_berth_largeammonia_planned = largeammonia_calls_planned * (
                    (largeammonia_data["call_size"] / largeammonia_data["pump_capacity"]) +
                    largeammonia_data["mooring_time"])
            time_at_berth_handysize_planned = handysize_calls_planned * (
                    (handysize_data["call_size"] / handysize_data["pump_capacity"]) +
                    handysize_data["mooring_time"])
            time_at_berth_panamax_planned = panamax_calls_planned * (
                    (panamax_data["call_size"] / panamax_data["pump_capacity"]) +
                    panamax_data["mooring_time"])
            time_at_berth_vlcc_planned = vlcc_calls_planned * (
                    (vlcc_data["call_size"] / vlcc_data["pump_capacity"]) +
                    vlcc_data["mooring_time"])

            total_time_at_berth_planned = np.sum(
                [time_at_berth_smallhydrogen_planned, time_at_berth_largehydrogen_planned,
                 time_at_berth_smallammonia_planned, time_at_berth_largeammonia_planned,
                 time_at_berth_handysize_planned, time_at_berth_panamax_planned, time_at_berth_vlcc_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            berth_occupancy_planned = total_time_at_berth_planned / (self.operational_hours * nr_of_jetty_planned)

            # estimate crane occupancy
            time_at_unloading_smallhydrogen_planned = smallhydrogen_calls * (
                        smallhydrogen_data["call_size"] / smallhydrogen_data["pump_capacity"])
            time_at_unloading_largehydrogen_planned = largehydrogen_calls * (
                        largehydrogen_data["call_size"] / largehydrogen_data["pump_capacity"])
            time_at_unloading_smallammonia_planned = smallammonia_calls * (
                        smallammonia_data["call_size"] / smallammonia_data["pump_capacity"])
            time_at_unloading_largeammonia_planned = largeammonia_calls * (
                        largeammonia_data["call_size"] / handysize_data["pump_capacity"])
            time_at_unloading_handysize_planned = handysize_calls * (
                        handysize_data["call_size"] / largeammonia_data["pump_capacity"])
            time_at_unloading_panamax_planned = panamax_calls * (
                        panamax_data["call_size"] / panamax_data["pump_capacity"])
            time_at_unloading_vlcc_planned = vlcc_calls * (vlcc_data["call_size"] / vlcc_data["pump_capacity"])

            total_time_at_unloading_planned = np.sum(
                [time_at_unloading_smallhydrogen_planned, time_at_unloading_largehydrogen_planned,
                 time_at_unloading_smallammonia_planned, time_at_unloading_largeammonia_planned,
                 time_at_unloading_handysize_planned, time_at_unloading_panamax_planned,
                 time_at_unloading_vlcc_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            unloading_occupancy_planned = total_time_at_unloading_planned / (
                        self.operational_hours * nr_of_jetty_planned)

            if nr_of_jetty_online != 0:
                time_at_berth_smallhydrogen_online = smallhydrogen_calls * (
                        (smallhydrogen_data["call_size"] / smallhydrogen_data["pump_capacity"]) +
                        smallhydrogen_data["mooring_time"])
                time_at_berth_largehydrogen_online = largehydrogen_calls * (
                        (largehydrogen_data["call_size"] / largehydrogen_data["pump_capacity"]) +
                        largehydrogen_data["mooring_time"])
                time_at_berth_smallammonia_online = smallammonia_calls * (
                        (smallammonia_data["call_size"] / smallammonia_data["pump_capacity"]) +
                        smallammonia_data["mooring_time"])
                time_at_berth_largeammonia_online = largeammonia_calls * (
                        (largeammonia_data["call_size"] / largeammonia_data["pump_capacity"]) +
                        largeammonia_data["mooring_time"])
                time_at_berth_handysize_online = handysize_calls * (
                        (handysize_data["call_size"] / handysize_data["pump_capacity"]) +
                        handysize_data["mooring_time"])
                time_at_berth_panamax_online = panamax_calls * (
                        (panamax_data["call_size"] / panamax_data["pump_capacity"]) +
                        panamax_data["mooring_time"])
                time_at_berth_vlcc_online = vlcc_calls * (
                        (vlcc_data["call_size"] / vlcc_data["pump_capacity"]) +
                        vlcc_data["mooring_time"])

                total_time_at_berth_online = np.sum(
                    [time_at_berth_smallhydrogen_online, time_at_berth_largehydrogen_online,
                     time_at_berth_smallammonia_online, time_at_berth_largeammonia_online,
                     time_at_berth_handysize_online, time_at_berth_panamax_online, time_at_berth_vlcc_online])

                # berth_occupancy is the total time at berth devided by the operational hours
                berth_occupancy_online = min(
                    [total_time_at_berth_online / (self.operational_hours * nr_of_jetty_online), 1])

                time_at_unloading_smallhydrogen_online = smallhydrogen_calls * (
                            smallhydrogen_data["call_size"] / smallhydrogen_data["pump_capacity"])
                time_at_unloading_largehydrogen_online = largehydrogen_calls * (
                            largehydrogen_data["call_size"] / largehydrogen_data["pump_capacity"])
                time_at_unloading_smallammonia_online = smallammonia_calls * (
                            smallammonia_data["call_size"] / smallammonia_data["pump_capacity"])
                time_at_unloading_largeammonia_online = largeammonia_calls * (
                            largeammonia_data["call_size"] / largeammonia_data["pump_capacity"])
                time_at_unloading_handysize_online = handysize_calls * (
                            handysize_data["call_size"] / handysize_data["pump_capacity"])
                time_at_unloading_panamax_online = panamax_calls * (
                            panamax_data["call_size"] / panamax_data["pump_capacity"])
                time_at_unloading_vlcc_online = vlcc_calls * (vlcc_data["call_size"] / vlcc_data["pump_capacity"])

                total_time_at_unloading_online = np.sum(
                    [time_at_unloading_smallhydrogen_online, time_at_unloading_largehydrogen_online,
                     time_at_unloading_smallammonia_online, time_at_unloading_largeammonia_online,
                     time_at_unloading_handysize_online, time_at_unloading_panamax_online,
                     time_at_unloading_vlcc_online])

                # berth_occupancy is the total time at berth devided by the operational hours
                unloading_occupancy_online = min(
                    [total_time_at_unloading_online / (self.operational_hours * nr_of_jetty_online), 1])

            else:
                berth_occupancy_online = float("inf")
                unloading_occupancy_online = float("inf")

        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            berth_occupancy_planned = float("inf")
            berth_occupancy_online = float("inf")
            unloading_occupancy_planned = float("inf")
            unloading_occupancy_online = float("inf")

        return berth_occupancy_planned, berth_occupancy_online, \
               unloading_occupancy_planned, unloading_occupancy_online

    def calculate_h2retrieval_occupancy(self, year, hydrogen_defaults_h2retrieval_data):
        """
        - Divide the throughput by the service rate to get the total hours in a year
        - Occupancy is total_time_at_h2retrieval divided by operational hours
        """
        # Find throughput
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
            year)

        Demand = []
        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        # find the total service rate and determine the time at h2retrieval
        h2retrieval_capacity_planned = 0
        h2retrieval_capacity_online = 0

        h2retrieval = H2retrieval(**hydrogen_defaults_h2retrieval_data)
        capacity = h2retrieval.capacity

        yearly_capacity = capacity * self.operational_hours

        list_of_elements = opentisim.core.find_elements(self, H2retrieval)
        if list_of_elements != []:
            for element in list_of_elements:
                h2retrieval_capacity_planned += yearly_capacity
                if year >= element.year_online:
                    h2retrieval_capacity_online += yearly_capacity

            # h2retrieval_occupancy is the total time at h2retrieval divided by the operational hours
            plant_occupancy_planned = Demand / h2retrieval_capacity_planned

            if h2retrieval_capacity_online != 0:
                time_at_plant_online = throughput_online / h2retrieval_capacity_online  # element.capacity

                # h2retrieval occupancy is the total time at h2retrieval divided by the operational hours
                plant_occupancy_online = min([time_at_plant_online, 1])
            else:
                plant_occupancy_online = float("inf")

        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            plant_occupancy_planned = float("inf")
            plant_occupancy_online = float("inf")

        return plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online

    def throughput_elements(self, year):
        """
        - Find which elements are important and needs to be included
        - Find from each element the online capacity
        - Find where the lowest value is present, in the capacity or in the demand
        """

        # Find jetty capacity
        Jetty_cap_planned = 0
        Jetty_cap = 0
        for element in opentisim.core.find_elements(self, Jetty):
            Jetty_cap_planned += ((smallhydrogen_data["pump_capacity"] +
                                   largehydrogen_data["pump_capacity"] +
                                   smallammonia_data["pump_capacity"] +
                                   largeammonia_data["pump_capacity"] +
                                   handysize_data["pump_capacity"] +
                                   panamax_data["pump_capacity"] +
                                   vlcc_data["pump_capacity"]) / 7 * self.operational_hours)
            if year >= element.year_online:
                Jetty_cap += ((smallhydrogen_data["pump_capacity"] +
                               largehydrogen_data["pump_capacity"] +
                               smallammonia_data["pump_capacity"] +
                               largeammonia_data["pump_capacity"] +
                               handysize_data["pump_capacity"] +
                               panamax_data["pump_capacity"] +
                               vlcc_data["pump_capacity"]) / 7 * self.operational_hours)

        # Find pipeline jetty capacity
        pipelineJ_capacity_planned = 0
        pipelineJ_capacity_online = 0
        list_of_elements = opentisim.core.find_elements(self, Pipeline_Jetty)
        if list_of_elements != []:
            for element in list_of_elements:
                pipelineJ_capacity_planned += element.capacity * self.operational_hours
                if year >= element.year_online:
                    pipelineJ_capacity_online += element.capacity * self.operational_hours

        # Find storage capacity
        storage_capacity_planned = 0
        storage_capacity_online = 0
        list_of_elements = opentisim.core.find_elements(self, Storage)
        if list_of_elements != []:
            for element in list_of_elements:
                storage_capacity_planned += element.capacity
                if year >= element.year_online:
                    storage_capacity_online += element.capacity

        storage_cap_planned = storage_capacity_planned / self.allowable_dwelltime / 1.1
        storage_cap_online = storage_capacity_online / self.allowable_dwelltime / 1.1

        # Find H2retrieval capacity
        h2retrieval_capacity_planned = 0
        h2retrieval_capacity_online = 0
        list_of_elements = opentisim.core.find_elements(self, H2retrieval)
        if list_of_elements != []:
            for element in list_of_elements:
                h2retrieval_capacity_planned += element.capacity * self.operational_hours
                if year >= element.year_online:
                    h2retrieval_capacity_online += element.capacity * self.operational_hours

        # Find pipeline hinter capacity
        pipelineh_capacity_planned = 0
        pipelineh_capacity_online = 0
        list_of_elements = opentisim.core.find_elements(self, Pipeline_Hinter)
        if list_of_elements != []:
            for element in list_of_elements:
                pipelineh_capacity_planned += element.capacity * self.operational_hours
                if year >= element.year_online:
                    pipelineh_capacity_online += element.capacity * self.operational_hours

        # Find demand
        Demand = []
        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                print('problem occurs at {}'.format(year))
                pass

        # Find the possible and online throuhgput including all elements
        throughput_planned = min(Jetty_cap_planned, pipelineJ_capacity_planned, storage_cap_planned,
                                 h2retrieval_capacity_planned, pipelineh_capacity_planned, Demand)
        throughput_online = min(h2retrieval_capacity_online, Jetty_cap, pipelineJ_capacity_online,
                                pipelineh_capacity_online, storage_cap_online, Demand)

        # Find from all elements the possible throughput if they were not there
        throughput_planned_jetty = min(pipelineJ_capacity_planned, storage_cap_planned, h2retrieval_capacity_planned,
                                       pipelineh_capacity_planned, Demand)
        throughput_planned_pipej = min(Jetty_cap_planned, storage_cap_planned, h2retrieval_capacity_planned,
                                       pipelineh_capacity_planned, Demand)
        throughput_planned_storage = min(Jetty_cap_planned, pipelineJ_capacity_planned, h2retrieval_capacity_planned,
                                         pipelineh_capacity_planned, Demand)
        throughput_planned_h2retrieval = min(Jetty_cap_planned, pipelineJ_capacity_planned, storage_cap_planned,
                                             pipelineh_capacity_planned, Demand)
        throughput_planned_pipeh = min(Jetty_cap_planned, pipelineJ_capacity_planned, storage_cap_planned,
                                       h2retrieval_capacity_planned, Demand)

        return throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh
        self.throughput.append(throughput_online)

    def check_throughput_available(self, year):
        list_of_elements = opentisim.core.find_elements(self, Storage)
        capacity = 0
        for element in list_of_elements:
            capacity += element.capacity

        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
            year)
        storage_capacity_dwelltime_throughput = (
                                                            throughput_planned_storage * self.allowable_dwelltime) * 1.1  # IJzerman p.26

        # when there are more slots than installed cranes ...
        if capacity < storage_capacity_dwelltime_throughput:
            return True
        else:
            return False

    # *** Plotting functions
    def terminal_elements_plot(self, width=0.1, alpha=0.6, fontsize=20):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = self.years
        berths = []
        jettys = []
        pipelines_jetty = []
        storages = []
        h2retrievals = []
        pipelines_hinterland = []
        throughputs_online = []

        # matplotlib.rcParams.update({'font.size': 18})

        for year in self.years:
            #         years.append(year)
            berths.append(0)
            jettys.append(0)
            pipelines_jetty.append(0)
            storages.append(0)
            h2retrievals.append(0)
            pipelines_hinterland.append(0)
            throughputs_online.append(0)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        berths[-1] += 1
                if isinstance(element, Jetty):
                    if year >= element.year_online:
                        jettys[-1] += 1
                if isinstance(element, Pipeline_Jetty):
                    if year >= element.year_online:
                        pipelines_jetty[-1] += 1
                if isinstance(element, Storage):
                    if year >= element.year_online:
                        storages[-1] += 1
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        h2retrievals[-1] += 1
                if isinstance(element, Pipeline_Hinter):
                    if year >= element.year_online:
                        pipelines_hinterland[-1] += 1

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))

        ax1.bar([x + 0 * width for x in years], berths, width=width, alpha=alpha, label="Berths", color='#aec7e8',
                edgecolor='darkgrey')
        ax1.bar([x + 1 * width for x in years], jettys, width=width, alpha=alpha, label="Jettys", color='#c7c7c7',
                edgecolor='darkgrey')
        ax1.bar([x + 2 * width for x in years], pipelines_jetty, width=width, alpha=alpha, label="Pipelines jetty",
                color='#ffbb78', edgecolor='darkgrey')
        ax1.bar([x + 3 * width for x in years], storages, width=width, alpha=alpha, label="Storages", color='#9edae5',
                edgecolor='darkgrey')
        ax1.bar([x + 4 * width for x in years], h2retrievals, width=width, alpha=alpha, label="H2 retrievals",
                color='#DBDB8D', edgecolor='darkgrey')
        ax1.bar([x + 5 * width for x in years], pipelines_hinterland, width=width, alpha=alpha, label="Pipeline hinter",
                color='#c49c94', edgecolor='darkgrey')

        # added vertical lines for mentioning the different phases
        # plt.axvline(x=2025.6, color='k', linestyle='--')
        # plt.axvline(x=2023.4, color='k', linestyle='--')

        # get demand
        demand = pd.DataFrame()
        demand['year'] = self.years
        demand['demand'] = 0

        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
                    elif column in commodity.scenario_data.columns and column != "volume":
                        demand['year'] = commodity.scenario_data[column]
            except:
                demand['demand'] += 0
                demand['year'] += 0
                pass

        # Adding the throughput
        # years = []
        throughputs_online = []
        for year in self.years:
            # years.append(year)
            throughputs_online.append(0)
            try:
                throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
                    year)
            except:
                throughput_online = 0
                pass

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # Making a second graph
        ax2 = ax1.twinx()

        dem = demand['year'].values[~np.isnan(demand['year'].values)]
        values = demand['demand'].values[~np.isnan(demand['demand'].values)]
        # print(dem, values)
        ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')

        # ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')

        # title and labels
        ax1.set_title('Terminal elements online', fontsize=fontsize)
        ax1.set_xlabel('Years', fontsize=fontsize)
        ax1.set_ylabel('Elements on line [nr]', fontsize=fontsize)
        ax2.set_ylabel('Demand/throughput[t/y]', fontsize=fontsize)

        # ticks and tick labels
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels([int(x) for x in years], rotation='vertical', fontsize=fontsize)
        max_elements = max([max(berths), max(jettys), max(pipelines_jetty),
                            max(storages), max(h2retrievals),
                            max(pipelines_hinterland)])

        ax1.set_yticks([x for x in range(0, max_elements + 1 + 2, 2)])
        ax1.set_yticklabels([int(x) for x in range(0, max_elements + 1 + 2, 2)], fontsize=fontsize)

        # print legend
        fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=4, fontsize=fontsize)
        fig.subplots_adjust(bottom=0.2)

    def demand_terminal_plot(self, width=0.1, alpha=0.6):
        # Adding the throughput
        years = self.years
        throughputs_online = []
        storage_capacity_online = []
        h2retrievals_capacity = []

        for year in self.years:
            # years.append(year)
            throughputs_online.append(0)
            storage_capacity_online.append(0)
            h2retrievals_capacity.append(0)

            # Find storage capacity
            for element in self.elements:
                if isinstance(element, Storage):
                    if year >= element.year_online:
                        storage_capacity_online[-1] += element.capacity / self.allowable_dwelltime / 1.1

            for element in self.elements:
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        h2retrievals_capacity[-1] += element.capacity * self.operational_hours

            # for element in self.elements:
            #     if isinstance(element, Jetty):
            #         if year >= element.year_online:
            #             jettys_capacity[-1] += element.capacity * self.operational_hours

        # get demand
        demand = pd.DataFrame()
        demand['year'] = self.years
        demand['demand'] = 0

        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
                    elif column in commodity.scenario_data.columns and column != "volume":
                        demand['year'] = commodity.scenario_data[column]
            except:
                demand['demand'] += 0
                demand['year'] += 0
                pass

        # Adding the throughput
        # years = []
        throughputs_online = []

        for year in self.years:
            # years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # Making a second graph
        # ax2 = ax1.twinx()
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x + 0 * width for x in years], storage_capacity_online, width=width, alpha=alpha,
                label="Storage capacity", color='#9edae5', edgecolor='darkgrey')
        ax1.bar([x + 1 * width for x in years], h2retrievals_capacity, width=width, alpha=alpha,
                label="H2 retrieval capacity", color='#dbdb8d', edgecolor='darkgrey')

        ax1.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')
        ax1.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Ton per annum')
        ax1.set_title('Demand vs Throughput')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def terminal_occupancy_plot(self, width=0.3, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        #         for year in self.years:
        #         #years.append(year)
        #         plants_occupancy.append(0)
        #         hydrogen_defaults_h2retrieval_data = self.h2retrieval_type_defaults
        #         try:

        #             plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(year, hydrogen_defaults_h2retrieval_data)
        #         except:
        #             plant_occupancy = 0

        #         for element in self.elements:
        #             if isinstance(element, H2retrieval):
        #                 if year >= element.year_online:
        #                     plants_occupancy[-1] = plant_occupancy_online

        # collect elements to add to plot
        # years = []
        years = self.years
        berths_occupancy = []
        waiting_factor = []

        for year in self.years:
            berths_occupancy.append(0)
            waiting_factor.append(0)
            try:

                smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned, total_vol_planned = self.calculate_vessel_calls(
                    year)
                berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy(
                    year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls,
                    handysize_calls,
                    panamax_calls, vlcc_calls, smallhydrogen_calls_planned, largehydrogen_calls_planned,
                    smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned,
                    panamax_calls_planned,
                    vlcc_calls_planned)

            except:
                berth_occupancy_online = 0

            berths = len(opentisim.core.find_elements(self, Berth))

            factor = opentisim.core.occupancy_to_waitingfactor(utilisation=berth_occupancy_online,
                                                               nr_of_servers_to_chk=berths, kendall=self.kendall)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        berths_occupancy[-1] = berth_occupancy_online

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        waiting_factor[-1] = factor

        # get demand
        demand = pd.DataFrame()
        demand['year'] = self.years
        demand['demand'] = 0

        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
                    elif column in commodity.scenario_data.columns and column != "volume":
                        demand['year'] = commodity.scenario_data[column]
            except:
                demand['demand'] += 0
                demand['year'] += 0
                pass

        # Adding the throughput
        # years = []
        throughputs_online = []
        for year in self.years:
            # years.append(year)
            throughputs_online.append(0)
            try:
                throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
                    year)
            except:
                throughput_online = 0
                pass

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x + 0 * width for x in years], berths_occupancy, width=width, alpha=alpha, label="Berth occupancy [-]",
                color='#aec7e8', edgecolor='darkgrey')
        # ax1.bar([x + 1 * width for x in years], waiting_factor, width=width, alpha=alpha, label="Berth occupancy [-]", color='grey', edgecolor='darkgrey')

        # Adding a horizontal line which shows the allowable berth occupancy
        horiz_line_data = np.array([self.allowable_berth_occupancy for i in range(len(years))])
        plt.plot(years, horiz_line_data, 'r--', color='grey', label="Allowable berth occupancy [-]")

        for i, occ in enumerate(berths_occupancy):
            occ = occ if type(occ) != float else 0
            ax1.text(x=years[i] - 0.1, y=occ + 0.01, s="{:04.2f}".format(occ), size=15)

        # for i, occ in enumerate(waiting_factor):
        #     occ = occ if type(occ) != float else 0
        #     ax1.text(x=years[i] - 0.1, y=occ + 0.01, s="{:04.2f}".format(occ), size=15)

        ax2 = ax1.twinx()

        dem = demand['year'].values[~np.isnan(demand['year'].values)]
        values = demand['demand'].values[~np.isnan(demand['demand'].values)]
        # print(dem, values)
        ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')

        # ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        plt.ylim(0, 6000000)

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Berth occupancy [-]')
        ax2.set_ylabel('Demand [t/y]')
        ax1.set_title('Berth occupancy')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def plant_occupancy_plot(self, width=0.3, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = self.years
        plants_occupancy = []

        for year in self.years:
            # years.append(year)
            plants_occupancy.append(0)
            hydrogen_defaults_h2retrieval_data = self.h2retrieval_type_defaults
            try:

                plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(
                    year, hydrogen_defaults_h2retrieval_data)
            except:
                plant_occupancy = 0

            for element in self.elements:
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        plants_occupancy[-1] = plant_occupancy_online

        #     # get demand
        demand = pd.DataFrame()
        demand['year'] = self.years
        demand['demand'] = 0

        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
                    elif column in commodity.scenario_data.columns and column != "volume":
                        demand['year'] = commodity.scenario_data[column]
            except:
                demand['demand'] += 0
                demand['year'] += 0
                pass

        # Adding the throughput
        # years = []
        throughputs_online = []
        for year in self.years:
            # years.append(year)
            throughputs_online.append(0)
            try:
                throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
                    year)
            except:
                throughput_online = 0
                pass

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x for x in years], plants_occupancy, width=width, alpha=alpha, label="Plant occupancy [-]",
                color='#aec7e8', edgecolor='darkgrey')

        for i, occ in enumerate(plants_occupancy):
            ax1.text(x=years[i], y=occ + 0.01, s="{:04.2f}".format(occ), size=15)

        # Adding a horizontal line which shows the allowable plant occupancy
        horiz_line_data = np.array([self.h2retrieval_trigger for i in range(len(years))])
        plt.plot(years, horiz_line_data, 'r--', color='grey', label="Allowable plant occupancy [-]")

        ax2 = ax1.twinx()

        dem = demand['year'].values[~np.isnan(demand['year'].values)]
        values = demand['demand'].values[~np.isnan(demand['demand'].values)]
        # print(dem, values)
        ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')

        # ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')
        # ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Plant occupancy [-]')
        ax2.set_ylabel('Demand [t/y]')
        ax1.set_title('Plant occupancy')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def Jetty_capacity_plot(self, width=0.3, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = self.years
        jettys = []

        # list number of jetties per year
        for year in self.years:  # range(years[0], years[-1]+1):
            # years.append(year)
            jettys.append(0)

            for element in self.elements:
                if isinstance(element, Jetty):
                    if year >= element.year_online:
                        jettys[-1] += 1

        # list demands per year
        # demand is now not working properly, because historical demand is not logged in Terminal
        demand = pd.DataFrame()
        demand['year'] = self.years
        demand['demand'] = 0

        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
                    elif column in commodity.scenario_data.columns and column != "volume":
                        demand['year'] = commodity.scenario_data[column]
            except:
                demand['demand'] += 0
                demand['year'] += 0
                pass

        # list throughputs_online per year
        throughputs_online = []
        for year in self.years:
            # years.append(year)
            throughputs_online.append(0)
            try:
                throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
                    year)
            except:
                throughput_online = 0
                pass

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x for x in years], jettys, width=width, alpha=alpha, label="Jettys [nr]", color='#c7c7c7',
                edgecolor='darkgrey')

        for i, occ in enumerate(jettys):
            occ = occ if type(occ) != float else 0
            ax1.text(x=years[i], y=occ + 0.02, s="{:01.0f}".format(occ), size=15)

        ax2 = ax1.twinx()
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')

        dem = demand['year'].values[~np.isnan(demand['year'].values)]
        values = demand['demand'].values[~np.isnan(demand['demand'].values)]
        # print(dem, values)
        ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')

        #     ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Elements on line [nr]')
        ax2.set_ylabel('Demand [t/y]')
        ax1.set_title('Jettys')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def Pipeline1_capacity_plot(self, width=0.2, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = self.years
        pipeline_jetty = []
        jettys = []
        pipeline_jetty_cap = []
        jettys_cap = []

        for year in self.years:
            # years.append(year)
            pipeline_jetty.append(0)
            jettys.append(0)
            pipeline_jetty_cap.append(0)
            jettys_cap.append(0)

            for element in self.elements:
                if isinstance(element, Pipeline_Jetty):
                    if year >= element.year_online:
                        pipeline_jetty[-1] += 1
            for element in self.elements:
                if isinstance(element, Jetty):
                    if year >= element.year_online:
                        jettys[-1] += 1

            for element in self.elements:
                if isinstance(element, Pipeline_Jetty):
                    if year >= element.year_online:
                        pipeline_jetty_cap[-1] += element.capacity
            for element in opentisim.core.find_elements(self, Jetty):
                if isinstance(element, Jetty):
                    if year >= element.year_online:
                        jettys_cap[-1] += largeammonia_data["pump_capacity"]

        # get demand
        demand = pd.DataFrame()
        demand['year'] = self.years
        demand['demand'] = 0

        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
                    elif column in commodity.scenario_data.columns and column != "volume":
                        demand['year'] = commodity.scenario_data[column]
            except:
                demand['demand'] += 0
                demand['year'] += 0
                pass

        # Adding the throughput
        # years = []
        throughputs_online = []
        for year in self.years:
            # years.append(year)
            throughputs_online.append(0)
            try:
                throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
                    year)
            except:
                throughput_online = 0
                pass

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x - 0.5 * width for x in years], jettys_cap, width=width, alpha=alpha,
                label="Jetty unloading capacity", color='#c7c7c7', edgecolor='darkgrey')
        ax1.bar([x + 0.5 * width for x in years], pipeline_jetty_cap, width=width, alpha=alpha,
                label="Pipeline Jetty - Storage capacity", color='#ffbb78', edgecolor='darkgrey')

        # Plot second ax
        ax2 = ax1.twinx()

        dem = demand['year'].values[~np.isnan(demand['year'].values)]
        values = demand['demand'].values[~np.isnan(demand['demand'].values)]
        # print(dem, values)
        ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')

        # ax2.step(years, demand['demand'].values, label="Demand", where='mid', color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        plt.ylim(0, 6000000)

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Unloading capacity Jetty & capacity Pipeline [t/h]')
        ax2.set_ylabel('Demand [t/y]')
        ax1.set_title('Capacity Jetty & Pipeline')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def Storage_capacity_plot(self, width=0.25, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # get crane service capacity and storage capacity
        years = self.years
        storages = []
        storages_capacity = []

        for year in self.years:
            # years.append(year)
            storages.append(0)
            storages_capacity.append(0)

            for element in self.elements:
                if isinstance(element, Storage):
                    if year >= element.year_online:
                        storages[-1] += 1
                        storages_capacity[-1] += element.capacity

        # get demand
        demand = pd.DataFrame()
        demand['year'] = self.years
        demand['demand'] = 0

        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
                    elif column in commodity.scenario_data.columns and column != "volume":
                        demand['year'] = commodity.scenario_data[column]
            except:
                demand['demand'] += 0
                demand['year'] += 0
                pass

        # Adding the throughput
        throughputs_online = []
        for year in self.years:
            # years.append(year)
            throughputs_online.append(0)
            try:
                throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
                    year)
            except:
                throughput_online = 0
                pass

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x for x in years], storages, width=width, alpha=alpha, label="Storages", color='#9edae5',
                edgecolor='darkgrey')

        for i, occ in enumerate(storages):
            occ = occ if type(occ) != float else 0
            ax1.text(x=years[i] - 0.05, y=occ + 0.2, s="{:01.0f}".format(occ), size=15)

        ax2 = ax1.twinx()

        dem = demand['year'].values[~np.isnan(demand['year'].values)]
        values = demand['demand'].values[~np.isnan(demand['demand'].values)]
        # print(dem, values)
        ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')

        # ax2.step(years, demand['demand'].values, label="Demand", where='mid',color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        ax2.step(years, storages_capacity, label="Storages capacity", where='mid', linestyle='--', color='steelblue')

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Storages [nr]')
        ax2.set_ylabel('Demand/Capacity [t/y]')
        ax1.set_title('Storage capacity')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def H2_capacity_plot(self, width=0.3, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = self.years
        h2retrievals = []
        h2retrievals_capacity = []

        for year in self.years:
            # years.append(year)
            h2retrievals.append(0)
            h2retrievals_capacity.append(0)

            for element in self.elements:
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        h2retrievals[-1] += 1
                        h2retrievals_capacity[-1] += element.capacity * self.operational_hours

        demand = pd.DataFrame()
        demand['year'] = self.years
        demand['demand'] = 0

        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
                    elif column in commodity.scenario_data.columns and column != "volume":
                        demand['year'] = commodity.scenario_data[column]
            except:
                demand['demand'] += 0
                demand['year'] += 0
                pass

        throughputs_online = []
        for year in self.years:
            # years.append(year)
            throughputs_online.append(0)
            try:
                throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(
                    year)
            except:
                throughput_online = 0
                pass

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x for x in years], h2retrievals, width=width, alpha=alpha, label="H2retrieval [nr]", color='#c7c7c7',
                edgecolor='darkgrey')

        for i, occ in enumerate(h2retrievals):
            occ = occ if type(occ) != float else 0
            ax1.text(x=years[i], y=occ + 0.02, s="{:01.0f}".format(occ), size=15)

        ax2 = ax1.twinx()
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        ax2.step(years, h2retrievals_capacity, label="H2 retrieval capacity", where='mid', linestyle='--',
                 color='darkgrey')

        dem = demand['year'].values[~np.isnan(demand['year'].values)]
        values = demand['demand'].values[~np.isnan(demand['demand'].values)]
        # print(dem, values)
        ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')
        #     ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Elements on line [nr]')
        ax2.set_ylabel('Demand [t/y]')
        ax1.set_title('H2retrievals')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def Pipeline2_capacity_plot(self, width=0.2, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = self.years
        pipeline_hinterland = []
        h2retrievals = []
        pipeline_hinterland_cap = []
        h2retrieval_cap = []

        for year in self.years:
            years.append(year)
            pipeline_hinterland.append(0)
            h2retrievals.append(0)
            pipeline_hinterland_cap.append(0)
            h2retrieval_cap.append(0)

            for element in self.elements:
                if isinstance(element, Pipeline_Hinter):
                    if year >= element.year_online:
                        pipeline_hinterland[-1] += 1
            for element in self.elements:
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        h2retrievals[-1] += 1

            for element in self.elements:
                if isinstance(element, Pipeline_Hinter):
                    if year >= element.year_online:
                        pipeline_hinterland_cap[-1] += element.capacity
            for element in self.elements:
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        h2retrieval_cap[-1] += element.capacity

        # get demand
        demand = pd.DataFrame()
        demand['year'] = self.years
        demand['demand'] = 0

        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
                    elif column in commodity.scenario_data.columns and column != "volume":
                        demand['year'] = commodity.scenario_data[column]
            except:
                demand['demand'] += 0
                demand['year'] += 0
                pass

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x - 0.5 * width for x in years], pipeline_hinterland, width=width, alpha=alpha,
                label="Number of pipeline H2 retrieval - Hinterland", color='#c49c94', edgecolor='darkgrey')
        ax1.bar([x + 0.5 * width for x in years], h2retrievals, width=width, alpha=alpha,
                label="Number of H2 retrievals", color='#DBDB8D', edgecolor='darkgrey')

        for i, occ in enumerate(pipeline_hinterland):
            occ = occ if type(occ) != float else 0
            ax1.text(x=years[i] - 0.25, y=occ + 0.05, s="{:01.0f}".format(occ), size=15)
        for i, occ in enumerate(h2retrievals):
            occ = occ if type(occ) != float else 0
            ax1.text(x=years[i] + 0.15, y=occ + 0.05, s="{:01.0f}".format(occ), size=15)

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2025.3, color='k', linestyle='--')
        plt.axvline(x=2023.3, color='k', linestyle='--')

        # Plot second ax
        ax2 = ax1.twinx()
        ax2.step(years, pipeline_hinterland_cap, label="Pipeline hinterland capacity", where='mid', linestyle='--',
                 color='#c49c94')
        ax2.step(years, h2retrieval_cap, label="H2 retrieval capacity", where='mid', linestyle='--', color='darkgrey')

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Nr of elements')
        ax2.set_ylabel('Capacity Pipeline & loading capacity H2 retrieval [t/h]')
        ax1.set_title('Capacity Pipeline & H2 retrieval')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)
