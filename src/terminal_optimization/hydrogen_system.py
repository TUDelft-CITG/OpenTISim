# package(s) for data handling
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# terminal_optimization package
from terminal_optimization.hydrogen_objects import *
from terminal_optimization import hydrogen_defaults

class System:
    def __init__(self, startyear=2019, lifecycle=20, operational_hours=5840, debug=False, elements=[],
                 commodity_type_defaults=hydrogen_defaults.commodity_lhydrogen_data, storage_type_defaults=
                 hydrogen_defaults.storage_lh2_data, h2retrieval_type_defaults=
                 hydrogen_defaults.h2retrieval_lh2_data, allowable_berth_occupancy=0.5, allowable_dwelltime=14 / 365,
                 h2retrieval_trigger = 0.5, allowable_station_occupancy=0.5):

        # time inputs
        self.startyear = startyear
        self.lifecycle = lifecycle
        self.operational_hours = operational_hours

        # provide intermediate outputs via print statements if debug = True
        self.debug = debug

        # collection of all terminal objects
        self.elements = elements

        # default values to use in selecting which commodity is imported
        self.commodity_type_defaults = commodity_type_defaults
        self.storage_type_defaults = storage_type_defaults
        self.h2retrieval_type_defaults = h2retrieval_type_defaults

        # triggers for the various elements (berth, storage and station)
        self.allowable_berth_occupancy = allowable_berth_occupancy
        self.allowable_dwelltime = allowable_dwelltime
        self.h2retrieval_trigger = h2retrieval_trigger
        self.allowable_station_occupancy = allowable_station_occupancy


        # storage variables for revenue
        self.revenues = []

    # *** Simulation engine

    def simulate(self):
        """ Terminal investment strategy simulation

        This method automatically generates investment decisions, parametrically derived from overall demand trends and
        a number of investment triggers.

        Based on:
        - Ijzermans, W., 2019. Terminal design optimization. Adaptive agribulk terminal planning
          in light of an uncertain future. Master's thesis. Delft University of Technology, Netherlands.
          URL: http://resolver.tudelft.nl/uuid:7ad9be30-7d0a-4ece-a7dc-eb861ae5df24.
        - Van Koningsveld, M. and J. P. M. Mulder. 2004. Sustainable Coastal Policy Developments in the
          Netherlands. A Systematic Approach Revealed. Journal of Coastal Research 20(2), pp. 375-385

        Apply frame of reference style decisions while stepping through each year of the terminal
        lifecycle and check if investment is needed (in light of strategic objective, operational objective,
        QSC, decision recipe, intervention method):

           1. for each year evaluate the demand of each commodity
           2. for each year evaluate the various investment decisions
           3. for each year calculate the energy costs (requires insight in realized demands)
           4. for each year calculate the demurrage costs (requires insight in realized demands)
           5. for each year calculate terminal revenues
           6. collect all cash flows (capex, opex, revenues)
           7. calculate PV's and aggregate to NPV

        """

        # # 1. for each year evaluate the demand of each commodity
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_demand_commodity(year)

        # 2. for each year evaluate the various investment decisions
        for year in range(self.startyear, self.startyear + self.lifecycle):
            """
            strategic objective: create a profitable enterprise (NPV > 0)
            operational objective: provide infrastructure of just sufficient quality
            """

            if self.debug:
                print('')
                print('Simulate year: {}'.format(year))

            # estimate traffic from commodity scenarios
            smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned, total_vol_planned = self.calculate_vessel_calls(year)

            if self.debug:
                print('  Total vessel calls: {}'.format(total_calls))
                print('     Small Hydrogen  calls: {}'.format(smallhydrogen_calls))
                print('     Large Hydrogen calls: {}'.format(largehydrogen_calls))
                print('     Small ammonia calls: {}'.format(smallammonia_calls))
                print('     Large ammonia calls: {}'.format(largeammonia_calls))
                print('     Handysize calls: {}'.format(handysize_calls))
                print('     Panamax calls: {}'.format(panamax_calls))
                print('     VLCC calls: {}'.format(vlcc_calls))
                print('  Total cargo volume: {}'.format(total_vol))

            self.berth_invest(year)

            self.pipeline_jetty_invest(year)

            self.storage_invest(year, self.storage_type_defaults)

            self.h2retrieval_invest(year, self.h2retrieval_type_defaults)

            self.unloading_station_invest(year)

            self.pipeline_hinter_invest(year, hydrogen_defaults.hinterland_pipeline_data)


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
            self.calculate_revenue(year)

        # 6. collect all cash flows (capex, opex, revenues)
        cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()

        # 7. calculate PV's and aggregate to NPV
        self.NPV()

    def calculate_revenue(self, year):
        """
        1. calculate the value of the total demand in year (demand * handling fee)
        2. calculate the maximum amount that can be handled (service capacity * operational hours)
        Terminal.revenues is the minimum of 1. and 2.
        """
        # todo: pakt nog niet goede fee bij throuhgput!
        # gather volumes from each commodity, calculate how much revenue it would yield, and add
        # for commodity in self.find_elements(Commodity):
        #     fee = commodity.handling_fee

        # commodity_type_defaults

        # commodity = Commodity(**hydrogen_defaults_commodity_data)
        list_of_elements = self.find_elements(Commodity)
        if list_of_elements != []:
            for element in list_of_elements:
                    fee = element.handling_fee

        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(year)
        if self.debug:
                print('     Revenues: {}'.format(int(throughput_online * fee)))

        try:
            self.revenues.append(throughput_online * fee)
        except:
            pass

    def calculate_energy_cost(self, year):
        """
        The energy cost of all different element are calculated.
        1. At first find the consumption, capacity and working hours per element
        2. Find the total energy price to multiply the consumption with the energy price
        """

        energy = Energy(**hydrogen_defaults.energy_data)
        smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned, total_vol_planned = self.calculate_vessel_calls(
            year)
        berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy(
            year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls,
            panamax_calls, vlcc_calls, smallhydrogen_calls_planned, largehydrogen_calls_planned,
            smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned,
            vlcc_calls_planned)

        station_occupancy_planned_demand, station_occupancy_planned_throughput, station_occupancy_online_demand, station_occupancy_online_throughput = self.calculate_station_occupancy(year)

        # calculate pipeline jetty energy
        list_of_elements_Pipelinejetty = self.find_elements(Pipeline_Jetty)

        for element in list_of_elements_Pipelinejetty:
            if year >= element.year_online:
                consumption = element.capacity * element.consumption_coefficient + element.consumption_constant
                hours = self.operational_hours * unloading_occupancy_online

                if consumption * hours * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * hours * energy.price

            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate storage energy
        list_of_elements_Storage = self.find_elements(Storage)

        for element in list_of_elements_Storage:
            if year >= element.year_online:
                consumption = element.consumption
                capacity = element.capacity
                hours = self.operational_hours

                if consumption * capacity * hours * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * capacity * hours * energy.price

            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate H2 retrieval energy
        list_of_elements_H2retrieval = self.find_elements(H2retrieval)

        # find the total throughput,
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(year)

        for element in list_of_elements_H2retrieval:
            if year >= element.year_online:
                consumption = element.consumption

                if consumption * throughput_online * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * throughput_online * energy.price
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate hinterland pipeline energy
        list_of_elements_hinter = self.find_elements(Pipeline_Hinter)

        for element in list_of_elements_hinter:
            if year >= element.year_online:
                consumption = element.capacity * element.consumption_coefficient + element.consumption_constant
                hours = self.operational_hours * station_occupancy_online_throughput

                if consumption * hours * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = consumption * hours * energy.price
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate hinterland station energy
        station_occupancy_planned_demand, station_occupancy_planned_throughput, station_occupancy_online_demand, station_occupancy_online_throughput = self.calculate_station_occupancy(year)

        list_of_elements_Station = self.find_elements(Unloading_station)

        for element in list_of_elements_Station:
            if year >= element.year_online:
                if element.consumption * self.operational_hours * station_occupancy_online_throughput * energy.price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'
                    ] = element.consumption * self.operational_hours * station_occupancy_online_throughput * energy.price
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

    def calculate_demurrage_cost(self, year):

        """Find the demurrage cost per type of vessel and sum all demurrage cost"""

        smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned,  total_vol_planned = self.calculate_vessel_calls(year)



        factor, waiting_time_occupancy = self.waiting_time(year)

        # Find the demurrage cost per type of vessel
        # if service_rate != 0:
        smallhydrogen = Vessel(**hydrogen_defaults.smallhydrogen_data)
        service_time_smallhydrogen = smallhydrogen.call_size / smallhydrogen.pump_capacity
        waiting_time_hours_smallhydrogen = factor * service_time_smallhydrogen
        penalty_time_smallhydrogen = max(0, waiting_time_hours_smallhydrogen - smallhydrogen.all_turn_time)
        demurrage_time_smallhydrogen = penalty_time_smallhydrogen * smallhydrogen_calls
        demurrage_cost_smallhydrogen = demurrage_time_smallhydrogen * smallhydrogen.demurrage_rate

        largehydrogen = Vessel(**hydrogen_defaults.largehydrogen_data)
        service_time_largehydrogen = largehydrogen.call_size / largehydrogen.pump_capacity
        waiting_time_hours_largehydrogen = factor * service_time_largehydrogen
        penalty_time_largehydrogen = max(0, waiting_time_hours_largehydrogen - largehydrogen.all_turn_time)
        demurrage_time_largehydrogen = penalty_time_largehydrogen * largehydrogen_calls
        demurrage_cost_largehydrogen = demurrage_time_largehydrogen * largehydrogen.demurrage_rate

        smallammonia = Vessel(**hydrogen_defaults.smallammonia_data)
        service_time_smallammonia = smallammonia.call_size / smallammonia.pump_capacity
        waiting_time_hours_smallammonia = factor * service_time_smallammonia
        penalty_time_smallammonia = max(0, waiting_time_hours_smallammonia - smallammonia.all_turn_time)
        demurrage_time_smallammonia = penalty_time_smallammonia * smallammonia_calls
        demurrage_cost_smallammonia = demurrage_time_smallammonia * smallammonia.demurrage_rate

        largeammonia = Vessel(**hydrogen_defaults.largeammonia_data)
        service_time_largeammonia = largeammonia.call_size / largeammonia.pump_capacity
        waiting_time_hours_largeammonia = factor * service_time_largeammonia
        penalty_time_largeammonia = max(0, waiting_time_hours_largeammonia - largeammonia.all_turn_time)
        demurrage_time_largeammonia = penalty_time_largeammonia * largeammonia_calls
        demurrage_cost_largeammonia = demurrage_time_largeammonia * largeammonia.demurrage_rate

        handysize = Vessel(**hydrogen_defaults.handysize_data)
        service_time_handysize = handysize.call_size / handysize.pump_capacity
        waiting_time_hours_handysize = factor * service_time_handysize
        penalty_time_handysize = max(0, waiting_time_hours_handysize - handysize.all_turn_time)
        demurrage_time_handysize = penalty_time_handysize * handysize_calls
        demurrage_cost_handysize = demurrage_time_handysize * handysize.demurrage_rate

        panamax = Vessel(**hydrogen_defaults.panamax_data)
        service_time_panamax = panamax.call_size / panamax.pump_capacity
        waiting_time_hours_panamax = factor * service_time_panamax
        penalty_time_panamax = max(0, waiting_time_hours_panamax - panamax.all_turn_time)
        demurrage_time_panamax = penalty_time_panamax * panamax_calls
        demurrage_cost_panamax = demurrage_time_panamax * panamax.demurrage_rate

        vlcc = Vessel(**hydrogen_defaults.vlcc_data)
        service_time_vlcc = vlcc.call_size / vlcc.pump_capacity
        waiting_time_hours_vlcc = factor * service_time_vlcc
        penalty_time_vlcc= max(0, waiting_time_hours_vlcc - vlcc.all_turn_time)
        demurrage_time_vlcc = penalty_time_vlcc * vlcc_calls
        demurrage_cost_vlcc = demurrage_time_vlcc * vlcc.demurrage_rate

        # vessel = Vessel(**hydrogen_defaults.vessel_data)
        # service_time_vessel = vessel.call_size / smallhydrogen.pump_capacity
        # waiting_time_hours_vessel = factor * service_time_vessel
        # penalty_time_vessel = max(0, waiting_time_hours_vessel - vessel.all_turn_time)
        # demurrage_time_vessel = penalty_time_vessel * vessel_calls
        # demurrage_cost_vessel = demurrage_time_vessel * vessel.demurrage_rate

        total_demurrage_cost = demurrage_cost_smallhydrogen + demurrage_cost_largehydrogen + demurrage_cost_smallammonia + demurrage_cost_largeammonia + demurrage_cost_handysize + demurrage_cost_panamax + demurrage_cost_vlcc

        self.demurrage.append(total_demurrage_cost)

    # *** Investment functions

    # todo: add reinvestment when lifetime is bigger than lifecycle

    def berth_invest(self, year):
        """
        Given the overall objectives of the terminal

        Decision recipe Berth:
        QSC: berth_occupancy
        Problem evaluation: there is a problem if the berth_occupancy > allowable_berth_occupancy
            - allowable_berth_occupancy = .40 # 40%
            - a berth needs:
               - a jetty
               - cranes (min:1 and max: max_cranes)
            - berth occupancy depends on:
                - total_calls and total_vol
                - total_service_capacity as delivered by the cranes
        Investment decisions: invest enough to make the berth_occupancy < allowable_berth_occupancy
            - adding jetty and cranes decreases berth_occupancy_rate
        """

        # report on the status of all berth elements

        self.report_element(Berth, year)
        self.report_element(Jetty, year)
        self.report_element(Pipeline_Jetty, year)
        self.report_element(Storage, year)
        self.report_element(H2retrieval, year)
        self.report_element(Pipeline_Hinter, year)
        self.report_element(Unloading_station, year)
        if self.debug:
            print('')
            print('  Start analysis:')

        # calculate berth occupancy
        smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned,  total_vol_planned = self.calculate_vessel_calls(year)

        berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy(
            year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls,
            panamax_calls, vlcc_calls, smallhydrogen_calls_planned, largehydrogen_calls_planned,
            smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned,
            vlcc_calls_planned)

        factor, waiting_time_occupancy = self.waiting_time(year)
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(year)

        if self.debug:
            print('     Berth occupancy planned (@ start of year): {}'.format(berth_occupancy_planned))
            print('     Berth occupancy online (@ start of year): {}'.format(berth_occupancy_online))
            print('     Unloading occupancy planned (@ start of year): {}'.format(unloading_occupancy_planned))
            print('     Unloading occupancy online (@ start of year): {}'.format(unloading_occupancy_online))
            print('     waiting time factor (@ start of year): {}'.format(factor))
            print('     waiting time occupancy (@ start of year): {}'.format(waiting_time_occupancy))
            print('     throughput online {}'.format(throughput_online))
            print('     throughput planned {}'.format(throughput_planned))


        while berth_occupancy_planned > self.allowable_berth_occupancy:

            if self.debug:
                    print('  *** add Berth to elements')
            berth = Berth(**hydrogen_defaults.berth_data)
            berth.year_online = year + berth.delivery_time
            self.elements.append(berth)

            berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy( year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls,  handysize_calls, panamax_calls, vlcc_calls, smallhydrogen_calls_planned,  largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned,   handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned)

            if self.debug:
                print('     Berth occupancy planned (after adding berth): {}'.format(berth_occupancy_planned))
                print('     Berth occupancy online (after adding berth): {}'.format(berth_occupancy_online))


            # check if a jetty is needed
            berths = len(self.find_elements(Berth))
            jettys = len(self.find_elements(Jetty))
            if berths > jettys:
                length_v = max(hydrogen_defaults.vlcc_data["LOA"], hydrogen_defaults.handysize_data["LOA"],
                               hydrogen_defaults.panamax_data["LOA"], hydrogen_defaults.smallhydrogen_data["LOA"],
                               hydrogen_defaults.largehydrogen_data["LOA"], hydrogen_defaults.smallammonia_data["LOA"],
                               hydrogen_defaults.largeammonia_data["LOA"] )  # average size
                draft = max(hydrogen_defaults.vlcc_data["draft"], hydrogen_defaults.handysize_data["draft"],
                               hydrogen_defaults.panamax_data["draft"], hydrogen_defaults.smallhydrogen_data["draft"],
                               hydrogen_defaults.largehydrogen_data["draft"], hydrogen_defaults.smallammonia_data["draft"],
                               hydrogen_defaults.largeammonia_data["draft"])
                width_v = max(hydrogen_defaults.vlcc_data["beam"], hydrogen_defaults.handysize_data["beam"],
                               hydrogen_defaults.panamax_data["beam"], hydrogen_defaults.smallhydrogen_data["beam"],
                               hydrogen_defaults.largehydrogen_data["beam"], hydrogen_defaults.smallammonia_data["beam"],
                               hydrogen_defaults.largeammonia_data["beam"])

                # Calculation of the length of a berth
                # apply PIANC 2014:
                if jettys == 0:
                    # - length when next jetty is n = 1
                    length = length_v + 2 * 15  # ref: PIANC 2014
                else:
                    if self.commodity_type_defaults==hydrogen_defaults.commodity_lhydrogen_data:
                        length = length_v + width_v + 2 * 15 + hydrogen_defaults.jetty_data["Safety_margin_LH2"]  # ref:LNG master planning - D. van Niekerk
                    else:
                        length = length_v + width_v + 2 * 15  # ref: Ports & Terminal, H ligteringen, H. Velsink p. 180

                # - width jetty head
                width = 4

                # - depth
                jetty = Jetty(**hydrogen_defaults.jetty_data)
                depth = np.sum([draft, jetty.max_sinkage, jetty.wave_motion, jetty.safety_margin])
                self.jetty_invest(year, length, depth, width)

                berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy(
                    year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls,
                    handysize_calls, panamax_calls, vlcc_calls, smallhydrogen_calls_planned,
                    largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned,
                    handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned)

                if self.debug:
                    print('     Berth occupancy planned (after adding jetty): {}'.format(berth_occupancy_planned))
                    print('     Berth occupancy online (after adding jetty): {}'.format(berth_occupancy_online))

            # # check if a crane is needed
            # if self.check_crane_slot_available():
            #     self.crane_invest(year)

            # # check if a storage is needed
            # if self.check_throughput_available(year):
            #     self.storage_invest(year)

    def jetty_invest(self, year, length, depth, width):
        """
        *** Decision recipe jetty: ***
        QSC: jetty_per_berth
        problem evaluation: there is a problem if the jetty_per_berth < 1
        investment decisions: invest enough to make the jetty_per_berth = 1
            - adding jetty will increase jetty_per_berth
            - jetty_wall.length must be long enough to accommodate largest expected vessel
            - jetty_wall.depth must be deep enough to accommodate largest expected vessel
            - jetty_wall.freeboard must be high enough to accommodate largest expected vessel
        """

        if self.debug:
            print('  *** add jetty to elements')
        # add a Jetty element
        jetty = Jetty(**hydrogen_defaults.jetty_data)

        # - capex
        unit_rate = int(jetty.Gijt_constant_jetty * (depth + jetty.freeboard)) #per m2
        mobilisation = int(max((length * width * unit_rate * jetty.mobilisation_perc), jetty.mobilisation_min))
        jetty.capex = int(length * width * unit_rate + mobilisation)

        # - opex
        jetty.insurance = unit_rate * length * width * jetty.insurance_perc
        jetty.maintenance = unit_rate * length * width * jetty.maintenance_perc
        jetty.year_online = year + jetty.delivery_time

        # residual
        jetty.assetvalue = (jetty.capex - mobilisation) * (1 - ((self.lifecycle + self.startyear - jetty.year_online) / jetty.lifespan))
        jetty.residual = max(jetty.assetvalue, 0)

        # add cash flow information to jetty object in a dataframe
        jetty = self.add_cashflow_data_to_element(jetty)

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
        list_of_elements = self.find_elements(Pipeline_Jetty)
        if list_of_elements != []:
            for element in list_of_elements:
                service_capacity += element.capacity
                if year >= element.year_online:
                    service_capacity_online += element.capacity

        #todo: max this, change this to general
        # max_vessel_Capacity_vessels = max([x.pump_capacity for x in self.find_elements(Vessel)])

        # find the total service rate,
        service_rate = 0
        years_online = []
        for element in self.find_elements(Jetty):
            service_rate += hydrogen_defaults.largehydrogen_data["pump_capacity"]
            years_online.append(element.year_online)

        # check if total planned capacity is smaller than target capacity, if so add a pipeline
        while service_capacity < service_rate:
            if self.debug:
                print('  *** add jetty pipeline to elements')
            pipeline_jetty = Pipeline_Jetty(**hydrogen_defaults.jetty_pipeline_data)

            # - capex
            unit_rate = pipeline_jetty.unit_rate_factor
            mobilisation = pipeline_jetty.mobilisation
            pipeline_jetty.capex = int(unit_rate + mobilisation)

            # - opex
            pipeline_jetty.insurance = unit_rate * pipeline_jetty.insurance_perc
            pipeline_jetty.maintenance = unit_rate * pipeline_jetty.maintenance_perc

            #   labour
            labour = Labour(**hydrogen_defaults.labour_data)
            pipeline_jetty.shift = (pipeline_jetty.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts)
            pipeline_jetty.labour = pipeline_jetty.shift * labour.operational_salary

            # there should always be a new jetty in the planning
            new_jetty_years = [x for x in years_online if x >= year]

            # find the maximum online year of pipeline_jetty or make it []
            if self.find_elements(Pipeline_Jetty) != []:
                max_pipeline_years = max([x.year_online for x in self.find_elements(Pipeline_Jetty)])
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

            # residual
            pipeline_jetty.assetvalue = unit_rate * (1 - (self.lifecycle + self.startyear - pipeline_jetty.year_online) / pipeline_jetty.lifespan)
            pipeline_jetty.residual = max(pipeline_jetty.assetvalue, 0)

            # add cash flow information to pipeline_jetty object in a dataframe
            pipeline_jetty = self.add_cashflow_data_to_element(pipeline_jetty)

            self.elements.append(pipeline_jetty)

            service_capacity += pipeline_jetty.capacity

        if self.debug:
            print('     a total of {} ton of pipeline_jetty service capacity is online; {} ton total planned'.format(
                service_capacity_online, service_capacity))

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
        list_of_elements = self.find_elements(Storage)
        if list_of_elements != []:
            for element in list_of_elements:
                if element.type == hydrogen_defaults_storage_data['type']:
                    storage_capacity += element.capacity
                    if year >= element.year_online:
                        storage_capacity_online += element.capacity

        if self.debug:
            print('     a total of {} ton of {} storage capacity is online; {} ton total planned'.format(
                storage_capacity_online, hydrogen_defaults_storage_data['type'], storage_capacity))

        # max_vessel_call_size = max([x.call_size for x in self.find_elements(Vessel)])
        max_vessel_call_size = hydrogen_defaults.largehydrogen_data["call_size"]

        Demand = []
        for commodity in self.find_elements(Commodity):
            try:
                Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        storage_capacity_dwelltime_demand = (Demand * self.allowable_dwelltime) * 1.1  # IJzerman p.26

        # find the total throughput
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(year)

        storage_capacity_dwelltime_throughput = (throughput_planned_storage * self.allowable_dwelltime) * 1.1  # IJzerman p.26

        # check if sufficient storage capacity is available
        # while storage_capacity < max_vessel_call_size and storage_capacity < storage_capacity_dwelltime_demand:

        while storage_capacity < storage_capacity_dwelltime_throughput or storage_capacity < max_vessel_call_size and storage_capacity < storage_capacity_dwelltime_demand:
            # if (self.check_throughput_available(year)):

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
            labour = Labour(**hydrogen_defaults.labour_data)
            storage.shift = ((storage.crew_for5 * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            storage.labour = storage.shift * labour.operational_salary

            if year == self.startyear:
                storage.year_online = year + storage.delivery_time +1
            else:
                storage.year_online = year + storage.delivery_time

            # residual
            storage.assetvalue = storage.unit_rate * (1 - ((self.lifecycle + self.startyear - storage.year_online) / storage.lifespan))
            storage.residual = max(storage.assetvalue, 0)

            # add cash flow information to storage object in a dataframe
            storage = self.add_cashflow_data_to_element(storage)

            self.elements.append(storage)

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

        plant_occupancy_planned, plant_occupancy_online, plant_occupancy_online_2, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(year)

        if self.debug:
            print('     Plant occupancy planned (@ start of year): {}'.format(plant_occupancy_planned))
            print('     Plant occupancy online (@ start of year): {}'.format(plant_occupancy_online))
            print('     Plant occupancy online (@ start of year): {}'.format(plant_occupancy_online_2))

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
            labour = Labour(**hydrogen_defaults.labour_data)
            h2retrieval.shift = ((h2retrieval.crew_for5 * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            h2retrieval.labour = h2retrieval.shift * labour.operational_salary

            jetty = Jetty(**hydrogen_defaults.jetty_data)

            if year == self.startyear + jetty.delivery_time:
                h2retrieval.year_online = year
            else:
                h2retrieval.year_online = year + h2retrieval.delivery_time

            # residual
            h2retrieval.assetvalue = h2retrieval.unit_rate * (
                        1 - (self.lifecycle + self.startyear - h2retrieval.year_online) / h2retrieval.lifespan)
            h2retrieval.residual = max(h2retrieval.assetvalue, 0)

            # add cash flow information to h2retrieval object in a dataframe
            h2retrieval = self.add_cashflow_data_to_element(h2retrieval)

            self.elements.append(h2retrieval)

            plant_occupancy_planned, plant_occupancy_online, plant_occupancy_online_2, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(year)

            if self.debug:
                print(
                    '     a total of {} ton of h2retrieval capacity is online; {} ton total planned'.format(
                        h2retrieval_capacity_online, h2retrieval_capacity_planned))

    def pipeline_hinter_invest(self, year, hydrogen_defaults_hinterland_pipeline_data):
        """current strategy is to add pipeline as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        # find the total service rate
        service_capacity = 0
        service_capacity_online_hinter = 0
        list_of_elements_pipeline = self.find_elements(Pipeline_Hinter)
        if list_of_elements_pipeline != []:
            for element in list_of_elements_pipeline:
                service_capacity += element.capacity
                if year >= element.year_online:
                    service_capacity_online_hinter += element.capacity

        # find the total service rate,
        service_rate = 0
        years_online = []
        for element in (self.find_elements(Unloading_station)):
            service_rate += element.service_rate
            years_online.append(element.year_online)

        # check if total planned length is smaller than target length, if so add a pipeline
        while service_rate > service_capacity:
            if self.debug:
                print('  *** add Hinter Pipeline to elements')

            pipeline_hinter = Pipeline_Hinter(**hydrogen_defaults_hinterland_pipeline_data)

            # - capex
            capacity = pipeline_hinter.capacity
            unit_rate = pipeline_hinter.unit_rate_factor * pipeline_hinter.length
            mobilisation = pipeline_hinter.mobilisation
            pipeline_hinter.capex = int(capacity * unit_rate + mobilisation)

            # - opex
            pipeline_hinter.insurance = capacity * unit_rate * pipeline_hinter.insurance_perc
            pipeline_hinter.maintenance = capacity * unit_rate * pipeline_hinter.maintenance_perc

            # - labour
            labour = Labour(**hydrogen_defaults.labour_data)
            pipeline_hinter.shift = (
                    (pipeline_hinter.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            pipeline_hinter.labour = pipeline_hinter.shift * labour.operational_salary

            if year == self.startyear:
                pipeline_hinter.year_online = year + pipeline_hinter.delivery_time +1
            else:
                pipeline_hinter.year_online = year + pipeline_hinter.delivery_time

            # residual
            pipeline_hinter.assetvalue = unit_rate * (
                    1 - (self.lifecycle + self.startyear - pipeline_hinter.year_online) / pipeline_hinter.lifespan)
            pipeline_hinter.residual = max(pipeline_hinter.assetvalue, 0)

            # add cash flow information to pipeline_hinter object in a dataframe
            pipeline_hinter = self.add_cashflow_data_to_element(pipeline_hinter)

            self.elements.append(pipeline_hinter)

            service_capacity += pipeline_hinter.capacity

        if self.debug:
            print(
                '     a total of {} ton of pipeline hinterland service capacity is online; {} ton total planned'.format(
                    service_capacity_online_hinter, service_capacity))

    def unloading_station_invest(self, year):
        """current strategy is to add unloading stations as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        station_occupancy_planned_demand, station_occupancy_planned_throughput, station_occupancy_online_demand, station_occupancy_online_throughput = self.calculate_station_occupancy(year)
        train_calls = self.train_call(year)

        while station_occupancy_planned_throughput > self.allowable_station_occupancy and station_occupancy_planned_demand > self.allowable_station_occupancy:
            # add a station when station occupancy is too high
            if self.debug:
                print('  *** add station to elements')

            station = Unloading_station(**hydrogen_defaults.hinterland_station_data)

            # - capex
            unit_rate = station.unit_rate
            mobilisation = station.mobilisation
            station.capex = int(unit_rate + mobilisation)

            # - opex
            station.insurance = unit_rate * station.insurance_perc
            station.maintenance = unit_rate * station.maintenance_perc

            # - labour
            labour = Labour(**hydrogen_defaults.labour_data)
            station.shift = ((station.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            station.labour = station.shift * labour.operational_salary

            # - Define online year
            if year == self.startyear:
                station.year_online = year + station.delivery_time + 1
            else:
                station.year_online = year + station.delivery_time

            # residual
            station.assetvalue = station.unit_rate * (1 - (self.lifecycle + self.startyear - station.year_online) / station.lifespan)
            station.residual = max(station.assetvalue, 0)

            # add cash flow information to station object in a dataframe
            station = self.add_cashflow_data_to_element(station)

            self.elements.append(station)

            station_occupancy_planned_demand, station_occupancy_planned_throughput, station_occupancy_online_demand, station_occupancy_online_throughput = self.calculate_station_occupancy(year)

    # *** Financial analyses

    def add_cashflow_elements(self):

        cash_flows = pd.DataFrame()
        labour = Labour(**hydrogen_defaults.labour_data)

        # initialise cash_flows
        cash_flows['year'] = list(range(self.startyear, self.startyear + self.lifecycle))
        cash_flows['capex'] = 0
        cash_flows['maintenance'] = 0
        cash_flows['insurance'] = 0
        cash_flows['energy'] = 0
        cash_flows['labour'] = 0
        cash_flows['residual'] = 0
        cash_flows['demurrage'] = self.demurrage
        cash_flows['revenues'] = self.revenues

        # add labour component for years were revenues are not zero
        cash_flows.loc[cash_flows[
                           'revenues'] != 0, 'labour'] = labour.international_staff * labour.international_salary + labour.local_staff * labour.local_salary

        for element in self.elements:
            if hasattr(element, 'df'):
                for column in cash_flows.columns:
                    if column in element.df.columns and column != "year":
                        cash_flows[column] += element.df[column]

        cash_flows.fillna(0)

        # calculate WACC real cashflows
        cash_flows_WACC_real = pd.DataFrame()
        cash_flows_WACC_real['year'] = cash_flows['year']
        for year in range(self.startyear, self.startyear + self.lifecycle):
            for column in cash_flows.columns:
                if column != "year":
                    cash_flows_WACC_real.loc[cash_flows_WACC_real['year'] == year, column] = \
                        cash_flows.loc[
                            cash_flows[
                                'year'] == year, column] / (
                                (1 + self.WACC_real()) ** (
                                year - self.startyear))

        return cash_flows, cash_flows_WACC_real

    def add_cashflow_data_to_element(self, element):

        """Place cashflow data in element dataframe"""

        # years
        years = list(range(self.startyear, self.startyear + self.lifecycle))

        # capex
        capex = element.capex

        # opex
        maintenance = element.maintenance
        insurance = element.insurance
        labour = element.labour
        residual = -1 * element.residual

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
        if labour:
            df.loc[df["year"] >= year_online, "labour"] = labour
        if residual:
            df.loc[df["year"] == self.startyear + self.lifecycle - 1, "residual"] = residual

        df.fillna(0, inplace=True)

        element.df = df

        return element

    def WACC_nominal(self, Gearing=60, Re=.10, Rd=.30, Tc=.28):
        """Nominal cash flow is the true dollar amount of future revenues the company expects
        to receive and expenses it expects to pay out, including inflation.
        When all cashflows within the model are denoted in real terms and including inflation."""

        Gearing = Gearing
        Re = Re  # return on equity
        Rd = Rd  # return on debt
        Tc = Tc  # income tax
        E = 100 - Gearing
        D = Gearing

        WACC_nominal = ((E / (E + D)) * Re + (D / (E + D)) * Rd) * (1 - Tc)

        return WACC_nominal

    def WACC_real(self, inflation=0.02):  # old: interest=0.0604
        """Real cash flow expresses a company's cash flow with adjustments for inflation.
        When all cashflows within the model are denoted in real terms and have been
        adjusted for inflation (no inlfation has been taken into account),
        WACC_real should be used. WACC_real is computed by as follows:"""

        WACC_real = (self.WACC_nominal() + 1) / (inflation + 1) - 1

        return WACC_real

    def NPV(self):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        # add cash flow information for each of the Terminal elements
        cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()

        # prepare years, revenue, capex and opex for plotting
        years = cash_flows_WACC_real['year'].values
        revenue = self.revenues
        capex = cash_flows_WACC_real['capex'].values
        opex = cash_flows_WACC_real['insurance'].values + \
               cash_flows_WACC_real['maintenance'].values + \
               cash_flows_WACC_real['energy'].values + \
               cash_flows_WACC_real['demurrage'].values + \
               cash_flows_WACC_real['residual'].values + \
               cash_flows_WACC_real['labour'].values

        PV = - capex - opex + revenue
        print('PV: {}'.format(PV))

        print('NPV: {}'.format(np.sum(PV)))

    # *** General functions

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
        smallhydrogen_vol = 0
        largehydrogen_vol = 0
        smallammonia_vol = 0
        largeammonia_vol = 0
        handysize_vol = 0
        panamax_vol = 0
        vlcc_vol = 0
        total_vol = 0
        smallhydrogen_vol_planned = 0
        largehydrogen_vol_planned  = 0
        smallammonia_vol_planned  = 0
        largeammonia_vol_planned  = 0
        handysize_vol_planned  = 0
        panamax_vol_planned  = 0
        vlcc_vol_planned  = 0
        total_vol_planned  = 0

        # gather volumes from each commodity scenario and calculate how much is transported with which vessel
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
            year)

        commodities = self.find_elements(Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                smallhydrogen_vol += volume/volume * throughput_online  * commodity.smallhydrogen_perc / 100
                largehydrogen_vol += volume/volume * throughput_online * commodity.largehydrogen_perc / 100
                smallammonia_vol += volume/volume * throughput_online * commodity.smallammonia_perc / 100
                largeammonia_vol += volume/volume * throughput_online * commodity.largeammonia_perc / 100
                handysize_vol += volume/volume * throughput_online * commodity.handysize_perc / 100
                panamax_vol += volume/volume * throughput_online * commodity.panamax_perc / 100
                vlcc_vol += volume/volume * throughput_online * commodity.vlcc_perc / 100
                total_vol += volume/volume * throughput_online
            except:
                pass

        # gather vessels and calculate the number of calls each vessel type needs to make
        vessels = self.find_elements(Vessel)
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
            [smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned,
             panamax_calls_planned, vlcc_calls_planned])

        return smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned, total_vol_planned

    def calculate_berth_occupancy(self, year,  smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls,\
        vlcc_calls, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, \
        largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned):
        """
        - Find all cranes and sum their effective_capacity to get service_capacity
        - Divide callsize_per_vessel by service_capacity and add mooring time to get total time at berth
        - Occupancy is total_time_at_berth divided by operational hours
        """

        # list all vessel objects in system
        list_of_elements = self.find_elements(Jetty)

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
                    (hydrogen_defaults.smallhydrogen_data["call_size"] / hydrogen_defaults.smallhydrogen_data["pump_capacity"]) +
                    hydrogen_defaults.smallhydrogen_data["mooring_time"])
            time_at_berth_largehydrogen_planned = largehydrogen_calls_planned * (
                    (hydrogen_defaults.largehydrogen_data["call_size"] / hydrogen_defaults.largehydrogen_data["pump_capacity"]) +
                    hydrogen_defaults.largehydrogen_data["mooring_time"])
            time_at_berth_smallammonia_planned = smallammonia_calls_planned * (
                    (hydrogen_defaults.smallammonia_data["call_size"] / hydrogen_defaults.smallammonia_data["pump_capacity"])  +
                    hydrogen_defaults.smallammonia_data["mooring_time"])
            time_at_berth_largeammonia_planned = largeammonia_calls_planned * (
                    (hydrogen_defaults.largeammonia_data["call_size"] / hydrogen_defaults.largeammonia_data["pump_capacity"]) +
                    hydrogen_defaults.largeammonia_data["mooring_time"])
            time_at_berth_handysize_planned = handysize_calls_planned * (
                    (hydrogen_defaults.handysize_data["call_size"] / hydrogen_defaults.handysize_data["pump_capacity"]) +
                    hydrogen_defaults.handysize_data["mooring_time"])
            time_at_berth_panamax_planned = panamax_calls_planned * (
                    (hydrogen_defaults.panamax_data["call_size"] / hydrogen_defaults.panamax_data["pump_capacity"]) +
                    hydrogen_defaults.panamax_data["mooring_time"])
            time_at_berth_vlcc_planned = vlcc_calls_planned * (
                    (hydrogen_defaults.vlcc_data["call_size"] / hydrogen_defaults.vlcc_data["pump_capacity"] ) +
                    hydrogen_defaults.vlcc_data["mooring_time"])
            total_time_at_berth_planned = np.sum(
                [time_at_berth_smallhydrogen_planned, time_at_berth_largehydrogen_planned, time_at_berth_smallammonia_planned, time_at_berth_largeammonia_planned, time_at_berth_handysize_planned, time_at_berth_panamax_planned, time_at_berth_vlcc_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            berth_occupancy_planned = total_time_at_berth_planned / (self.operational_hours * nr_of_jetty_planned)

            # estimate crane occupancy
            time_at_unloading_smallhydrogen_planned = smallhydrogen_calls * (hydrogen_defaults.smallhydrogen_data["call_size"] / hydrogen_defaults.smallhydrogen_data["pump_capacity"])
            time_at_unloading_largehydrogen_planned = largehydrogen_calls * (hydrogen_defaults.largehydrogen_data["call_size"] / hydrogen_defaults.largehydrogen_data["pump_capacity"])
            time_at_unloading_smallammonia_planned = smallammonia_calls * (hydrogen_defaults.smallammonia_data["call_size"] / hydrogen_defaults.smallammonia_data["pump_capacity"])
            time_at_unloading_largeammonia_planned = largeammonia_calls * (hydrogen_defaults.largeammonia_data["call_size"] / hydrogen_defaults.handysize_data["pump_capacity"])
            time_at_unloading_handysize_planned = handysize_calls * (hydrogen_defaults.handysize_data["call_size"] / hydrogen_defaults.largeammonia_data["pump_capacity"])
            time_at_unloading_panamax_planned = panamax_calls * (hydrogen_defaults.panamax_data["call_size"] / hydrogen_defaults.panamax_data["pump_capacity"])
            time_at_unloading_vlcc_planned = vlcc_calls * (hydrogen_defaults.vlcc_data["call_size"] / hydrogen_defaults.vlcc_data["pump_capacity"])

            total_time_at_unloading_planned = np.sum(
                [time_at_unloading_smallhydrogen_planned, time_at_unloading_largehydrogen_planned, time_at_unloading_smallammonia_planned, time_at_unloading_largeammonia_planned, time_at_unloading_handysize_planned, time_at_unloading_panamax_planned, time_at_unloading_vlcc_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            unloading_occupancy_planned = total_time_at_unloading_planned / (self.operational_hours * nr_of_jetty_planned)

            if nr_of_jetty_online != 0:
                time_at_berth_smallhydrogen_online = smallhydrogen_calls * (
                        (hydrogen_defaults.smallhydrogen_data["call_size"] / hydrogen_defaults.smallhydrogen_data["pump_capacity"]) +
                        hydrogen_defaults.smallhydrogen_data["mooring_time"])
                time_at_berth_largehydrogen_online = largehydrogen_calls * (
                        (hydrogen_defaults.largehydrogen_data["call_size"] / hydrogen_defaults.largehydrogen_data["pump_capacity"]) +
                        hydrogen_defaults.largehydrogen_data["mooring_time"])
                time_at_berth_smallammonia_online = smallammonia_calls * (
                        (hydrogen_defaults.smallammonia_data["call_size"] / hydrogen_defaults.smallammonia_data["pump_capacity"]) +
                        hydrogen_defaults.smallammonia_data["mooring_time"])
                time_at_berth_largeammonia_online = largeammonia_calls * (
                        (hydrogen_defaults.largeammonia_data["call_size"] / hydrogen_defaults.largeammonia_data["pump_capacity"]) +
                        hydrogen_defaults.largeammonia_data["mooring_time"])
                time_at_berth_handysize_online = handysize_calls * (
                        (hydrogen_defaults.handysize_data["call_size"] / hydrogen_defaults.handysize_data["pump_capacity"]) +
                        hydrogen_defaults.handysize_data["mooring_time"])
                time_at_berth_panamax_online = panamax_calls * (
                        (hydrogen_defaults.panamax_data["call_size"] / hydrogen_defaults.panamax_data["pump_capacity"]) +
                        hydrogen_defaults.panamax_data["mooring_time"])
                time_at_berth_vlcc_online = vlcc_calls * (
                        (hydrogen_defaults.vlcc_data["call_size"] / hydrogen_defaults.vlcc_data["pump_capacity"]) +
                        hydrogen_defaults.vlcc_data["mooring_time"])

                total_time_at_berth_online = np.sum(
                    [time_at_berth_smallhydrogen_online,time_at_berth_largehydrogen_online, time_at_berth_smallammonia_online, time_at_berth_largeammonia_online,time_at_berth_handysize_online, time_at_berth_panamax_online, time_at_berth_vlcc_online])

                # berth_occupancy is the total time at berth devided by the operational hours
                berth_occupancy_online = min([total_time_at_berth_online / (self.operational_hours * nr_of_jetty_online), 1])

                time_at_unloading_smallhydrogen_online = smallhydrogen_calls * (hydrogen_defaults.smallhydrogen_data["call_size"] / hydrogen_defaults.smallhydrogen_data["pump_capacity"])
                time_at_unloading_largehydrogen_online = largehydrogen_calls * (hydrogen_defaults.largehydrogen_data["call_size"] / hydrogen_defaults.largehydrogen_data["pump_capacity"])
                time_at_unloading_smallammonia_online = smallammonia_calls * (hydrogen_defaults.smallammonia_data["call_size"] / hydrogen_defaults.smallammonia_data["pump_capacity"])
                time_at_unloading_largeammonia_online = largeammonia_calls * (hydrogen_defaults.largeammonia_data["call_size"] / hydrogen_defaults.largeammonia_data["pump_capacity"])
                time_at_unloading_handysize_online = handysize_calls * (hydrogen_defaults.handysize_data["call_size"] / hydrogen_defaults.handysize_data["pump_capacity"])
                time_at_unloading_panamax_online = panamax_calls * (hydrogen_defaults.panamax_data["call_size"] / hydrogen_defaults.panamax_data["pump_capacity"])
                time_at_unloading_vlcc_online = vlcc_calls * (hydrogen_defaults.vlcc_data["call_size"] / hydrogen_defaults.vlcc_data["pump_capacity"])

                total_time_at_unloading_online = np.sum(
                    [time_at_unloading_smallhydrogen_online, time_at_unloading_largehydrogen_online, time_at_unloading_smallammonia_online, time_at_unloading_largeammonia_online, time_at_unloading_handysize_online, time_at_unloading_panamax_online, time_at_unloading_vlcc_online])

                # berth_occupancy is the total time at berth devided by the operational hours
                unloading_occupancy_online = min([total_time_at_unloading_online / (self.operational_hours * nr_of_jetty_online), 1])

            else:
                berth_occupancy_online = float("inf")
                unloading_occupancy_online = float("inf")

        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            berth_occupancy_planned = float("inf")
            berth_occupancy_online = float("inf")
            unloading_occupancy_planned = float("inf")
            unloading_occupancy_online = float("inf")

        return berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online

    def waiting_time(self, year):
        """
       - Import the berth occupancy of every year
       - Find the factor for the waiting time with the E2/E/n quing theory using 4th order polynomial regression
       - Waiting time is the factor times the crane occupancy
       """

        smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned,  total_vol_planned = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy(year, smallhydrogen_calls,     largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned,handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned)

        #find the different factors which are linked to the number of berths
        berths = len(self.find_elements(Berth))

        if berths == 1:
            factor = max(0,
                         79.726 * berth_occupancy_online ** 4 - 126.47 * berth_occupancy_online ** 3 + 70.660 * berth_occupancy_online ** 2 - 14.651 * berth_occupancy_online + 0.9218)
        elif berths == 2:
            factor = max(0,
                         29.825 * berth_occupancy_online ** 4 - 46.489 * berth_occupancy_online ** 3 + 25.656 * berth_occupancy_online ** 2 - 5.3517 * berth_occupancy_online + 0.3376)
        elif berths == 3:
            factor = max(0,
                         19.362 * berth_occupancy_online ** 4 - 30.388 * berth_occupancy_online ** 3 + 16.791 * berth_occupancy_online ** 2 - 3.5457 * berth_occupancy_online + 0.2253)
        elif berths == 4:
            factor = max(0,
                         17.334 * berth_occupancy_online ** 4 - 27.745 * berth_occupancy_online ** 3 + 15.432 * berth_occupancy_online ** 2 - 3.2725 * berth_occupancy_online + 0.2080)
        elif berths == 5:
            factor = max(0,
                         11.149 * berth_occupancy_online ** 4 - 17.339 * berth_occupancy_online ** 3 + 9.4010 * berth_occupancy_online ** 2 - 1.9687 * berth_occupancy_online + 0.1247)
        elif berths == 6:
            factor = max(0,
                         10.512 * berth_occupancy_online ** 4 - 16.390 * berth_occupancy_online ** 3 + 8.8292 * berth_occupancy_online ** 2 - 1.8368 * berth_occupancy_online + 0.1158)
        elif berths == 7:
            factor = max(0,
                         8.4371 * berth_occupancy_online ** 4 - 13.226 * berth_occupancy_online ** 3 + 7.1446 * berth_occupancy_online ** 2 - 1.4902 * berth_occupancy_online + 0.0941)
        else:
            # if there are no berths the occupancy is 'infinite' so a berth is certainly needed
            factor = float("inf")

        waiting_time_hours = factor * unloading_occupancy_online * self.operational_hours / total_calls
        waiting_time_occupancy = waiting_time_hours * total_calls / self.operational_hours

        return factor, waiting_time_occupancy

    def calculate_h2retrieval_occupancy(self, year):
        """
        - Find all stations and sum their service_rate to get service_capacity in TUE per hours
        - Divide the throughput by the service rate to get the total hours in a year
        - Occupancy is total_time_at_station divided by operational hours
        """
        # Find throughput
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station= self.throughput_elements(year)

        Demand = []
        for commodity in self.find_elements(Commodity):
            try:
                Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        # find the total service rate and determine the time at station
        h2retrieval_capacity_planned = 0
        h2retrieval_capacity_online = 0
        yearly_capacity = hydrogen_defaults.h2retrieval_lh2_data["capacity"] * self.operational_hours
        list_of_elements = self.find_elements(H2retrieval)
        if list_of_elements != []:
            for element in list_of_elements:
                h2retrieval_capacity_planned += yearly_capacity
                if year >= element.year_online:
                    h2retrieval_capacity_online += yearly_capacity

            # station_occupancy is the total time at station divided by the operational hours
            plant_occupancy_planned = Demand / h2retrieval_capacity_planned

            if h2retrieval_capacity_online != 0:
                time_at_plant_online = throughput_online / h2retrieval_capacity_online# element.capacity
                time_at_plant_online_2 = throughput_online / h2retrieval_capacity_online# element.capacity

                # station occupancy is the total time at station divided by the operational hours
                plant_occupancy_online = min([time_at_plant_online, 1])
                plant_occupancy_online_2 = min([time_at_plant_online_2, 1])
            else:
                plant_occupancy_online = float("inf")
                plant_occupancy_online_2 = float("inf")

        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            plant_occupancy_planned = float("inf")
            plant_occupancy_online = float("inf")
            plant_occupancy_online_2 = float("inf")

        return plant_occupancy_planned, plant_occupancy_online, plant_occupancy_online_2, h2retrieval_capacity_planned, h2retrieval_capacity_online

    def calculate_station_occupancy(self, year):
        """
        - Find all stations and sum their service_rate to get service_capacity in TUE per hours
        - Divide the throughput by the service rate to get the total hours in a year
        - Occupancy is total_time_at_station divided by operational hours
        """

        # Find demand
        Demand = []
        for commodity in self.find_elements(Commodity):
            try:
                Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station= self.throughput_elements(year)


        list_of_elements = self.find_elements(Unloading_station)
        # find the total service rate and determine the time at station

        service_rate_planned = 0
        service_rate_online = 0
        if list_of_elements != []:
            for element in list_of_elements:
                service_rate_planned += element.service_rate
                if year >= element.year_online:
                    service_rate_online += element.service_rate

            time_at_station_planned_demand = Demand / service_rate_planned  # element.service_rate
            time_at_station_planned_throughput = throughput_planned_station / service_rate_planned  # element.service_rate

            # station_occupancy is the total time at station divided by the operational hours
            station_occupancy_planned_demand = time_at_station_planned_demand / self.operational_hours
            station_occupancy_planned_throughput = time_at_station_planned_throughput / self.operational_hours

            if service_rate_online != 0:
                time_at_station_online_demand = Demand / service_rate_online  # element.capacity
                time_at_station_online_throughput = throughput_online / service_rate_online  # element.capacity

                # station occupancy is the total time at station divided by the operational hours
                station_occupancy_online_demand = min([time_at_station_online_demand / self.operational_hours, 1])
                station_occupancy_online_throughput = min([time_at_station_online_throughput / self.operational_hours, 1])
            else:
                station_occupancy_online_demand = float("inf")
                station_occupancy_online_throughput = float("inf")

        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            station_occupancy_planned_demand = float("inf")
            station_occupancy_planned_throughput = float("inf")
            station_occupancy_online_demand = float("inf")
            station_occupancy_online_throughput = float("inf")

        return station_occupancy_planned_demand, station_occupancy_planned_throughput, station_occupancy_online_demand, station_occupancy_online_throughput

    def throughput_elements(self,year):
        """
        - Find which elements are important and needs to be included
        - Find from each element the online capacity
        - Find where the lowest value is present, in the capacity or in the demand
        """

        #Find jetty capacity
        Jetty_cap_planned = 0
        Jetty_cap = 0
        for element in self.find_elements(Jetty):
            Jetty_cap_planned += ((hydrogen_defaults.smallhydrogen_data["pump_capacity"] +
                                 hydrogen_defaults.largehydrogen_data["pump_capacity"] +
                                 hydrogen_defaults.smallammonia_data["pump_capacity"] +
                                 hydrogen_defaults.largeammonia_data["pump_capacity"] +
                                 hydrogen_defaults.handysize_data["pump_capacity"] +
                                 hydrogen_defaults.panamax_data["pump_capacity"] +
                                 hydrogen_defaults.vlcc_data["pump_capacity"])/7 * self.operational_hours)
            if year >= element.year_online:
                Jetty_cap += ((hydrogen_defaults.smallhydrogen_data["pump_capacity"] +
                                 hydrogen_defaults.largehydrogen_data["pump_capacity"] +
                                 hydrogen_defaults.smallammonia_data["pump_capacity"] +
                                 hydrogen_defaults.largeammonia_data["pump_capacity"] +
                                 hydrogen_defaults.handysize_data["pump_capacity"] +
                                 hydrogen_defaults.panamax_data["pump_capacity"] +
                                 hydrogen_defaults.vlcc_data["pump_capacity"])/7 * self.operational_hours)

        # Find pipeline jetty capacity
        pipelineJ_capacity_planned = 0
        pipelineJ_capacity_online = 0
        list_of_elements = self.find_elements(Pipeline_Jetty)
        if list_of_elements != []:
            for element in list_of_elements:
                pipelineJ_capacity_planned += element.capacity * self.operational_hours
                if year >= element.year_online:
                    pipelineJ_capacity_online += element.capacity * self.operational_hours

        # Find storage capacity
        storage_capacity_planned = 0
        storage_capacity_online = 0
        list_of_elements = self.find_elements(Storage)
        if list_of_elements != []:
            for element in list_of_elements:
                storage_capacity_planned += element.capacity
                if year >= element.year_online:
                    storage_capacity_online += element.capacity

        storage_cap_planned = storage_capacity_planned / self.allowable_dwelltime / 1.1
        storage_cap_online = storage_capacity_online / self.allowable_dwelltime/ 1.1

        #Find H2retrieval capacity
        h2retrieval_capacity_planned = 0
        h2retrieval_capacity_online = 0
        yearly_capacity = hydrogen_defaults.h2retrieval_lh2_data["capacity"] * self.operational_hours
        list_of_elements = self.find_elements(H2retrieval)
        if list_of_elements != []:
            for element in list_of_elements:
                h2retrieval_capacity_planned += yearly_capacity
                if year >= element.year_online:
                    h2retrieval_capacity_online += yearly_capacity

        # Find pipeline hinter capacity
        pipelineh_capacity_planned = 0
        pipelineh_capacity_online = 0
        list_of_elements = self.find_elements(Pipeline_Hinter)
        if list_of_elements != []:
            for element in list_of_elements:
                pipelineh_capacity_planned += element.capacity * self.operational_hours
                if year >= element.year_online:
                    pipelineh_capacity_online += element.capacity * self.operational_hours

        #Find Station capacity
        list_of_elements = self.find_elements(Unloading_station)
        planned_station = 0
        online_station = 0
        if list_of_elements != []:
            for element in list_of_elements:
                planned_station += element.service_rate * self.operational_hours
                if year >= element.year_online:
                    online_station += element.service_rate * self.operational_hours

        #Find demand
        Demand = []
        for commodity in self.find_elements(Commodity):
            try:
                Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        # Find the possible and online throuhgput including all elements
        throughput_planned = min(Jetty_cap_planned, pipelineJ_capacity_planned, storage_cap_planned, h2retrieval_capacity_planned, pipelineh_capacity_planned, planned_station, Demand)
        throughput_online = min(online_station, h2retrieval_capacity_online, Jetty_cap, pipelineJ_capacity_online, pipelineh_capacity_online, storage_cap_online,  Demand)

        # Find from all elements the possible throughput if they were not there
        throughput_planned_jetty = min(pipelineJ_capacity_planned, storage_cap_planned, h2retrieval_capacity_planned, pipelineh_capacity_planned, planned_station, Demand)
        throughput_planned_pipej = min(Jetty_cap_planned, storage_cap_planned, h2retrieval_capacity_planned, pipelineh_capacity_planned, planned_station, Demand)
        throughput_planned_storage = min(Jetty_cap_planned, pipelineJ_capacity_planned, h2retrieval_capacity_planned, pipelineh_capacity_planned, planned_station, Demand)
        throughput_planned_h2retrieval = min(Jetty_cap_planned, pipelineJ_capacity_planned, storage_cap_planned, pipelineh_capacity_planned, planned_station, Demand)
        throughput_planned_pipeh = min(Jetty_cap_planned, pipelineJ_capacity_planned, storage_cap_planned, h2retrieval_capacity_planned, planned_station, Demand)
        throughput_planned_station = min(Jetty_cap_planned, pipelineJ_capacity_planned, storage_cap_planned, h2retrieval_capacity_planned, pipelineh_capacity_planned, Demand)

        return throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station

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

    def train_call(self, year):
        """Calculation of the train calls per year, this is calculated from:
        - find out how much throughput there is
        - find out how much cargo the train can transport
        - calculate the numbers of train calls"""

        station = Unloading_station(**hydrogen_defaults.hinterland_station_data)

        # - Trains calculated with the throughput
        smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls,\
        panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, \
        smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, \
        vlcc_calls_planned, total_calls_planned, total_vol_planned = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online, = self.calculate_berth_occupancy(year,  smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls,\
        vlcc_calls, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, \
        largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned)


        # find the total service rate,
        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station= self.throughput_elements(year)

        train_calls = throughput_online / station.call_size

        return train_calls

    def check_throughput_available(self, year):
        list_of_elements = self.find_elements(Storage)
        capacity = 0
        for element in list_of_elements:
            capacity += element.capacity

        throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(year)
        storage_capacity_dwelltime_throughput = (throughput_planned_storage * self.allowable_dwelltime) * 1.1  # IJzerman p.26

        # when there are more slots than installed cranes ...
        if capacity < storage_capacity_dwelltime_throughput:
            return True
        else:
            return False

    # *** plotting functions

    def terminal_elements_plot(self, width=0.1, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = []
        berths = []
        jettys = []
        pipelines_jetty = []
        storages = []
        h2retrievals = []
        pipelines_hinterland = []
        unloading_station = []
        throughputs_online = []


        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            berths.append(0)
            jettys.append(0)
            pipelines_jetty.append(0)
            storages.append(0)
            h2retrievals.append(0)
            pipelines_hinterland.append(0)
            unloading_station.append(0)
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
                if isinstance(element, Unloading_station):
                    if year >= element.year_online:
                        unloading_station[-1] += 1

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))

        ax1.bar([x + 0 * width for x in years], berths, width=width, alpha=alpha, label="Berths", color='#aec7e8', edgecolor='darkgrey')
        ax1.bar([x + 1 * width for x in years], jettys, width=width, alpha=alpha, label="Jettys", color='#c7c7c7', edgecolor='darkgrey')
        ax1.bar([x + 2 * width for x in years], pipelines_jetty, width=width, alpha=alpha, label="Pipelines jetty", color='#ffbb78', edgecolor='darkgrey')
        ax1.bar([x + 3 * width for x in years], storages, width=width, alpha=alpha, label="Storages", color='#9edae5', edgecolor='darkgrey')
        ax1.bar([x + 4 * width for x in years], h2retrievals, width=width, alpha=alpha, label="H2 retrievals", color='#DBDB8D', edgecolor='darkgrey')
        ax1.bar([x + 5 * width for x in years], pipelines_hinterland, width=width, alpha=alpha, label="Pipeline hinter", color='#c49c94', edgecolor='darkgrey')
        ax1.bar([x + 6 * width for x in years], unloading_station, width=width, alpha=alpha, label="Unloading station", color='grey', edgecolor='darkgrey')

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2024.6, color='k', linestyle='--')
        plt.axvline(x=2022.4, color='k', linestyle='--')

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

        #Adding the throughput
        years = []
        throughputs_online = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        #Making a second graph
        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput_online [t/y]", where='mid', color='#aec7e8')

        # added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.60, 'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.55, 0.60, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.60, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Elements on line [nr]')
        ax2.set_ylabel('Elements on line [nr]')
        ax1.set_title('Terminal elements online')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc = 'upper right')

    def demand_terminal_plot(self, width=0.1, alpha=0.6):
        # Adding the throughput
        years = []
        throughputs_online = []
        storage_capacity_online = []
        h2retrievals_capacity = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
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

        # Adding the throughput
        years = []
        throughputs_online = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                            throughputs_online[-1] = throughput_online

        #Making a second graph
        # ax2 = ax1.twinx()
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x + 0 * width for x in years], storage_capacity_online, width=width, alpha=alpha, label="Storage capacity", color='#9edae5', edgecolor='darkgrey')
        ax1.bar([x + 1 * width for x in years], h2retrievals_capacity, width=width, alpha=alpha, label="H2 retrieval capacity", color='#dbdb8d', edgecolor='darkgrey')


        ax1.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')
        ax1.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2024.6, color='k', linestyle='--')
        plt.axvline(x=2022.4, color='k', linestyle='--')

        # added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.60, 'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.55, 0.60, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.60, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Ton per annum')
        ax1.set_title('Demand vs Throughput')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def cashflow_plot(self, cash_flows, width=0.3, alpha=0.6):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        # prepare years, revenue, capex and opex for plotting
        years = cash_flows['year'].values
        revenue = self.revenues
        capex = cash_flows['capex'].values
        opex = cash_flows['insurance'].values + cash_flows['maintenance'].values + cash_flows['energy'].values + \
               cash_flows['labour'].values + cash_flows['demurrage'].values + cash_flows['residual'].values

        # sum cash flows to get profits as a function of year
        profits = []
        for year in years:
            profits.append(-cash_flows.loc[cash_flows['year'] == year]['capex'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['insurance'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['maintenance'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['energy'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['labour'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['demurrage'].item() +
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

        ax.bar([x - width for x in years], -opex, width=width, alpha=alpha, label="Opex", color='lightblue')
        ax.bar(years, -capex, width=width, alpha=alpha, label="Capex", color='red')
        ax.bar([x + width for x in years], revenue, width=width, alpha=alpha, label="Revenue", color='lightgreen')
        ax.step(years, profits, label='Profits', where='mid')
        ax.step(years, profits_cum, label='Profits_cum', where='mid')

        ax.set_xlabel('Years')
        ax.set_ylabel('Cashflow [000 M $]')
        ax.set_title('Cash flow plot')
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def terminal_occupancy_plot(self, width=0.3, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = []
        berths_occupancy = []
        waiting_factor = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            berths_occupancy.append(0)
            waiting_factor.append(0)

            smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned, total_vol_planned = self.calculate_vessel_calls(
                year)
            berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy(
                year, smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls,
                panamax_calls, vlcc_calls, smallhydrogen_calls_planned, largehydrogen_calls_planned,
                smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned,
                vlcc_calls_planned)

            factor, waiting_time_occupancy = self.waiting_time(year)

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
        demand['year'] = list(range(self.startyear, self.startyear + self.lifecycle))
        demand['demand'] = 0
        for commodity in self.find_elements(Commodity):
            try:
                for column in commodity.scenario_data.columns:
                    if column in commodity.scenario_data.columns and column != "year":
                        demand['demand'] += commodity.scenario_data[column]
            except:
                pass

        #Adding the throughput
        years = []
        throughputs_online = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

          # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x + 0 * width for x in years], berths_occupancy, width=width, alpha=alpha, label="Berth occupancy [-]", color='#aec7e8', edgecolor='darkgrey')
        # ax1.bar([x + 1 * width for x in years], waiting_factor, width=width, alpha=alpha, label="Berth occupancy [-]", color='grey', edgecolor='darkgrey')

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2024.3, color='k', linestyle='--')
        plt.axvline(x=2022.3, color='k', linestyle='--')

        # Adding a horizontal line which shows the allowable berth occupancy
        horiz_line_data = np.array([self.allowable_berth_occupancy for i in range(len(years))])
        plt.plot(years, horiz_line_data, 'r--', color='grey', label="Allowable berth occupancy [-]")

        for i, occ in enumerate(berths_occupancy):
            occ = occ if type(occ) != float else 0
            ax1.text(x = years[i] - 0.1, y = occ + 0.01, s = "{:04.2f}".format(occ), size=15)

        # for i, occ in enumerate(waiting_factor):
        #     occ = occ if type(occ) != float else 0
        #     ax1.text(x=years[i] - 0.1, y=occ + 0.01, s="{:04.2f}".format(occ), size=15)

        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        plt.ylim(0, 6000000)

        # added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.70, 'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.57, 0.70, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.70, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

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
        years = []
        plants_occupancy = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            plants_occupancy.append(0)

            plant_occupancy_planned, plant_occupancy_online, plant_occupancy_online_2, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(year)

            for element in self.elements:
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        plants_occupancy[-1] = plant_occupancy_online


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

        # Adding the throughput
        years = []
        throughputs_online = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x for x in years], plants_occupancy, width=width, alpha=alpha, label="Plant occupancy [-]", color='#aec7e8', edgecolor='darkgrey')

        for i, occ in enumerate(plants_occupancy):
            ax1.text(x=years[i], y=occ + 0.01, s="{:04.2f}".format(occ), size=15)

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2024.3, color='k', linestyle='--')
        plt.axvline(x=2022.3, color='k', linestyle='--')

        # Adding a horizontal line which shows the allowable plant occupancy
        horiz_line_data = np.array([self.h2retrieval_trigger for i in range(len(years))])
        plt.plot(years, horiz_line_data, 'r--', color='grey', label="Allowable plant occupancy [-]")

        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')

        # added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.70, 'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.57, 0.70, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.70, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Plant occupancy [-]')
        ax2.set_ylabel('Demand [t/y]')
        ax1.set_title('Plant occupancy')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def station_occupancy_plot(self, width=0.3, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = []
        stations_occupancy = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            stations_occupancy.append(0)

            station_occupancy_planned_demand, station_occupancy_planned_throughput, station_occupancy_online_demand, station_occupancy_online_throughput = self.calculate_station_occupancy(year)

            for element in self.elements:
                if isinstance(element, Unloading_station):
                    if year >= element.year_online:
                        stations_occupancy[-1] = station_occupancy_online_throughput

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

        # Adding the throughput
        years = []
        throughputs_online = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online
        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x for x in years], stations_occupancy, width=width, alpha=alpha, label="Station occupancy [-]",
                color='#aec7e8', edgecolor='darkgrey')

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2024.3, color='k', linestyle='--')
        plt.axvline(x=2022.3, color='k', linestyle='--')

        # Adding a horizontal line which shows the allowable plant occupancy
        horiz_line_data = np.array([self.allowable_station_occupancy for i in range(len(years))])
        plt.plot(years, horiz_line_data, 'r--', color='grey', label="Allowable station occupancy [-]")

        for i, occ in enumerate(stations_occupancy):
           ax1.text(x=years[i] - 0.1, y=occ + 0.01, s="{:04.2f}".format(occ), size=15)

        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        plt.ylim(0, 6000000)

        # added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.50, 'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.57, 0.50, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.50, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Station occupancy [-]')
        ax2.set_ylabel('Demand [t/y]')
        ax1.set_title('Station occupancy')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def Jetty_capacity_plot(self, width=0.3, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = []
        jettys = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            jettys.append(0)

            for element in self.elements:
                if isinstance(element, Jetty):
                    if year >= element.year_online:
                        jettys[-1] += 1

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

        # Adding the throughput
        years = []
        throughputs_online = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x for x in years], jettys, width=width, alpha=alpha, label="Jettys [nr]", color='#c7c7c7', edgecolor='darkgrey')

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2024.3, color='k', linestyle='--')
        plt.axvline(x=2022.3, color='k', linestyle='--')

        for i, occ in enumerate(jettys):
            occ = occ if type(occ) != float else 0
            ax1.text(x=years[i], y=occ + 0.02, s="{:01.0f}".format(occ), size=15)

        ax2 = ax1.twinx()
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        ax2.step(years, demand['demand'].values, label="Demand [t/y]", where='mid', color='#ff9896')

        # added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.60, 'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.57, 0.60, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.60, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

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
        years = []
        pipeline_jetty = []
        jettys = []
        pipeline_jetty_cap = []
        jettys_cap = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
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
            for element in self.find_elements(Jetty):
                if isinstance(element, Jetty):
                    if year >= element.year_online:
                        jettys_cap[-1] += hydrogen_defaults.largehydrogen_data["pump_capacity"]

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

        # Adding the throughput
        years = []
        throughputs_online = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x - 0.5 * width for x in years], jettys_cap, width=width, alpha=alpha, label="Jetty unloading capacity", color='#c7c7c7', edgecolor='darkgrey')
        ax1.bar([x + 0.5 * width for x in years], pipeline_jetty_cap, width=width, alpha=alpha,
                label="Pipeline Jetty - Storage capacity", color='#ffbb78', edgecolor='darkgrey')

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2024.3, color='k', linestyle='--')
        plt.axvline(x=2022.3, color='k', linestyle='--')

        # Plot second ax
        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, label="Demand", where='mid', color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        plt.ylim(0, 6000000)

        # added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.60, 'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.57, 0.60, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.60, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

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
        years = []
        storages = []
        storages_capacity = []

        for year in range(self.startyear, self.startyear + self.lifecycle):

            years.append(year)
            storages.append(0)
            storages_capacity.append(0)

            for element in self.elements:
                if isinstance(element, Storage):
                    if year >= element.year_online:
                        storages[-1] += 1
                        storages_capacity[-1] += element.capacity

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

        # Adding the throughput
        years = []
        throughputs_online = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x for x in years], storages, width=width, alpha=alpha, label="Storages", color='#9edae5', edgecolor='darkgrey')

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2024.3, color='k', linestyle='--')
        plt.axvline(x=2022.3, color='k', linestyle='--')

        for i, occ in enumerate(storages):
            occ = occ if type(occ) != float else 0
            ax1.text(x = years[i] - 0.05, y = occ + 0.2, s = "{:01.0f}".format(occ), size=15)

        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, label="Demand", where='mid',color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        ax2.step(years, storages_capacity, label="Storages capacity", where='mid', linestyle = '--',  color='steelblue')

        # added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.60, 'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.57, 0.60, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.60, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Storages [nr]')
        ax2.set_ylabel('Demand/Capacity [t/y]')
        ax1.set_title('Storage capacity')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def H2retrieval_capacity_plot(self, width=0.25, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # get crane service capacity and storage capacity
        years = []
        h2retrievals = []
        h2retrievals_capacity = []

        for year in range(self.startyear, self.startyear + self.lifecycle):

            years.append(year)
            h2retrievals.append(0)
            h2retrievals_capacity.append(0)

            for element in self.elements:
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        h2retrievals[-1] += 1
                        h2retrievals_capacity[-1] += element.capacity * self.operational_hours

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

        # Adding the throughput
        years = []
        throughputs_online = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            throughputs_online.append(0)

            throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh, throughput_planned_station = self.throughput_elements(
                year)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x for x in years], h2retrievals, width=width, alpha=alpha, label="H2 retrieval", color='#DBDB8D', edgecolor='darkgrey')

        #added vertical lines for mentioning the different phases
        plt.axvline(x=2024.3, color = 'k', linestyle = '--')
        plt.axvline(x=2022.3, color='k', linestyle='--')

        for i, occ in enumerate(h2retrievals):
            occ = occ if type(occ) != float else 0
            ax1.text(x = years[i] - 0.05, y = occ + 0.2, s = "{:01.0f}".format(occ), size=15)

        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, label="Demand", where='mid',color='#ff9896')
        ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
        ax2.step(years, h2retrievals_capacity, label="H2 retrieval capacity", where='mid', linestyle = '--',  color='darkgrey')

        #added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.60,'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.57, 0.60, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.60, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

        ax1.set_xlabel('Years')
        ax1.set_ylabel('H2 retrieval [nr]')
        ax2.set_ylabel('Demand/Capacity [t/y]')
        ax1.set_title('H2 retrieval capacity')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

    def Pipeline2_capacity_plot(self, width=0.2, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = []
        pipeline_hinterland = []
        loadingstations = []
        pipeline_hinterland_cap = []
        loadingstations_cap = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            pipeline_hinterland.append(0)
            loadingstations.append(0)
            pipeline_hinterland_cap.append(0)
            loadingstations_cap.append(0)

            for element in self.elements:
                if isinstance(element, Pipeline_Hinter):
                    if year >= element.year_online:
                        pipeline_hinterland[-1] += 1
            for element in self.elements:
                if isinstance(element, Unloading_station):
                    if year >= element.year_online:
                        loadingstations[-1] += 1

            for element in self.elements:
                if isinstance(element, Pipeline_Hinter):
                    if year >= element.year_online:
                        pipeline_hinterland_cap[-1] += element.capacity
            for element in self.elements:
                if isinstance(element, Unloading_station):
                    if year >= element.year_online:
                        loadingstations_cap[-1] += element.service_rate

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
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.bar([x - 0.5 * width for x in years], pipeline_hinterland, width=width, alpha=alpha,
                label="Number of pipeline H2 retrieval - Hinterland", color='#c49c94', edgecolor='darkgrey')
        ax1.bar([x + 0.5 * width for x in years], loadingstations, width=width, alpha=alpha,
                label="Number of hinterland station", color='grey', edgecolor='darkgrey')

        for i, occ in enumerate(pipeline_hinterland):
            occ = occ if type(occ) != float else 0
            ax1.text(x=years[i] - 0.25, y=occ + 0.05, s="{:01.0f}".format(occ), size=15)
        for i, occ in enumerate(loadingstations):
            occ = occ if type(occ) != float else 0
            ax1.text(x=years[i] + 0.15, y=occ + 0.05, s="{:01.0f}".format(occ), size=15)

        # added vertical lines for mentioning the different phases
        plt.axvline(x=2024.3, color='k', linestyle='--')
        plt.axvline(x=2022.3, color='k', linestyle='--')

        # Plot second ax
        ax2 = ax1.twinx()
        ax2.step(years, pipeline_hinterland_cap, label="Pipeline hinterland capacity", where='mid', linestyle = '--', color='#c49c94')
        ax2.step(years, loadingstations_cap, label="Loading station capacity", where='mid', linestyle = '--', color='darkgrey')

        # added boxes
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.30, 0.60, 'phase 1', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.57, 0.60, 'phase 2', transform=ax1.transAxes, fontsize=14, bbox=props)
        ax1.text(0.82, 0.60, 'phase 3', transform=ax1.transAxes, fontsize=14, bbox=props)

        ax1.set_xlabel('Years')
        ax1.set_ylabel('Nr of elements')
        ax2.set_ylabel('Capacity Pipeline & loading capacity station [t/h]')
        ax1.set_title('Capacity Pipeline & Station')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        fig.legend(loc=1)

