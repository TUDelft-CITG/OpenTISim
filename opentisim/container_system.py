# package(s) for data handling
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# opentisim package
from opentisim.container_objects import *
from opentisim import container_defaults


class System:
    def __init__(self, startyear=2020, lifecycle=20, stack_equipment='rs', laden_stack='rs',
                 operational_hours=7500, debug=False, elements=None,
                 crane_type_defaults=container_defaults.sts_crane_data,
                 allowable_berth_occupancy=0.6, laden_perc=0.80, reefer_perc=0.1, empty_perc=0.05, oog_perc=0.05, transhipment_ratio=0.60,
                 energy_price=0.17, fuel_price=1, land_price=0):
        # time inputs
        if elements is None:
            elements = []
        if elements is None:
            elements = []
        self.startyear = startyear
        self.lifecycle = lifecycle
        self.operational_hours = operational_hours

        # stack equipment parameters
        self.stack_equipment = stack_equipment
        self.laden_stack = laden_stack

        # provide intermediate outputs via print statements if debug = True
        self.debug = debug

        # collection of all terminal objects
        self.elements = elements

        # default values to use in case various types can be selected
        self.crane_type_defaults = crane_type_defaults

        # triggers for the various elements (berth, storage and station)
        self.allowable_berth_occupancy = allowable_berth_occupancy
        # self.allowable_dwelltime = allowable_dwelltime

        # container split
        self.laden_perc = laden_perc
        self.reefer_perc = reefer_perc
        self.empty_perc = empty_perc
        self.oog_perc = oog_perc

        # modal split
        self.transhipment_ratio = transhipment_ratio

        # fuel and electrical power price
        self.energy_price = energy_price
        self.fuel_price = fuel_price
        self.land_price = land_price

        # storage variables for revenue
        # self.revenues = []

    """ Simulation engine """

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

        " 1. for each year evaluate the demand of each commodity "
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_demand_commodity(year)

        " 2. for each year evaluate the various investment decisions "
        for year in range(self.startyear, self.startyear + self.lifecycle):
            if self.debug:
                print('')
                print('Below, the various investment decisions are evaluated for the year {}.'.format(year))
                print('')
                print('Simulate year: {}'.format(year))

            # estimate traffic from commodity scenarios
            fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS, total_calls, total_vol = self.calculate_vessel_calls(year)
            if self.debug:
                print('  Total vessel calls: {}'.format(total_calls))
                print('  Fully cellular calls: {}'.format(fully_cellular))
                print('  Panamax calls: {}'.format(panamax))
                print('  Panamax max calls: {}'.format(panamax_max))
                print('  Post Panamax I calls: {}'.format(post_panamax_I))
                print('  Post Panamax II calls: {}'.format(post_panamax_II))
                print('  New Panamax calls: {}'.format(new_panamax))
                print('  VLCS calls: {}'.format(VLCS))
                print('  ULCS calls: {}'.format(ULCS))
                print('  Total cargo volume: {}'.format(total_vol))

            self.berth_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)

            self.horizontal_transport_invest(year)

            self.laden_stack_invest(year)

            self.empty_stack_invest(year)

            self.oog_stack_invest(year)

            self.stack_equipment_invest(year)

            self.gate_invest(year)  # todo add barge_berth_invest(year)

            self.empty_handler_invest(year)

            self.general_services_invest(year)

        " 3. for each year calculate the general labour, fuel and energy costs (requires insight in realized demands) "
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_energy_cost(year)

        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_general_labour_cost(year)

        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_fuel_cost(year)

        " 4. for each year calculate the demurrage and overseas transport costs (requires insight in realized demands) "
        self.demurrage = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_demurrage_cost(year)

        self.overseas_transport = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_overseas_transport_costs(year)

        " 5.  for each year calculate terminal revenues "
        # self.revenues = []
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_revenue(year)

        " 6. collect all cash flows (capex, opex) (WACC = Weighted average cost of capital) "
        cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()

        " 7. calculate key numbers "
        # PV, capex_normal, opex_normal, labour_normal = self.NPV()
        # total_land_use = self.calculate_land_use(year)
        # land = total_land_use
        # labour = labour_normal[-1]
        # opex = opex_normal[-1]
        # capex_normal = np.nan_to_num(capex_normal)
        # capex = np.sum(capex_normal)
        #
        # data = {"equipment": self.stack_equipment,
        #         "cost_land": self.land_price,
        #         "cost_fuel": self.fuel_price,
        #         "cost_power": self.energy_price,
        #         "land": land,
        #         "labour": labour,
        #         "opex": opex,
        #         "capex": capex,
        #         "PV": PV}

        " 8. calculate PV's and aggregate to NPV "  # todo hier kun je varieeren welke kosten je wilt printen
        self.NPV()

        # PV, capex_normal, opex_normal, labour_normal = self.NPV()
        # return PV, data

    """ Revenue functions """
    # def calculate_revenue(self, year):
    #     """
    #     1. calculate the value of the total demand in year (demand * handling fee)
    #     2. calculate the maximum amount that can be handled (service capacity * operational hours)
    #     Terminal.revenues is the minimum of 1. and 2.
    #     """
    #     # implement a safetymarge
    #     quay_walls = len(self.find_elements(Quay_Wall))
    #     crane_cyclic = len(self.find_elements(Cyclic_Unloader))
    #     horizontal_transport = len(self.find_elements(Horizontal_Transport))
    #
    #     if quay_walls < 1  and (
    #             crane_cyclic > 1) and horizontal_transport<1:
    #         safety_factor = 0
    #     else:
    #         safety_factor = 1
    #
    #     # maize = Commodity(**container_defaults.maize_data)
    #     # wheat = Commodity(**container_defaults.wheat_data)
    #     # soybeans = Commodity(**container_defaults.soybean_data)
    #     #
    #     # maize_demand, wheat_demand, soybeans_demand = self.calculate_demand_commodity(year)
    #
    #     # gather volumes from each commodity, calculate how much revenue it would yield, and add
    #     revenues = 0
    #     for commodity in self.find_elements(Commodity):
    #         fee = commodity.handling_fee
    #         try:
    #             volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
    #             revenues += (volume * fee * safety_factor)
    #         except:
    #             pass
    #     if self.debug:
    #         print('     Revenues (demand): {}'.format(revenues))
    #
    #     fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS, total_calls, total_vol = self.calculate_vessel_calls(year)
    #     berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online= self.calculate_berth_occupancy(
    #         year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
    #
    #     # find the total service rate,
    #     service_rate = 0
    #     for element in self.find_elements(Cyclic_Unloader) :
    #         if year >= element.year_online:
    #             service_rate += element.effective_capacity * crane_occupancy_online
    #
    #     # find the rate between volume and throughput
    #     rate_throughput_volume = service_rate * self.operational_hours / total_vol
    #
    #     if self.debug:
    #         print('     Revenues (throughput): {}'.format(
    #             int(service_rate * self.operational_hours * fee * safety_factor)))
    #
    #     try:
    #         self.revenues.append(
    #             min(revenues * safety_factor, service_rate * self.operational_hours * fee * safety_factor))
    #     except:
    #         pass

    """ Operational expenditures """

    def calculate_energy_cost(self, year):  # todo add energy for new elements
        """
        The energy cost of all different element are calculated.
        1. At first find the consumption, capacity and working hours per element
        2. Find the total energy price to multiply the consumption with the energy price
        """

        sts_moves, stack_moves, empty_moves, tractor_moves = self.box_moves(year)
        energy_price = self.energy_price

        "STS crane energy costs"
        cranes = 0
        for element in self.elements:
            if isinstance(element, Cyclic_Unloader):
                if year >= element.year_online:
                    cranes += 1

        for element in self.find_elements(Cyclic_Unloader):
            if year >= element.year_online:
                sts_moves_per_element = sts_moves / cranes
                if element.consumption * sts_moves_per_element * energy_price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = \
                        element.consumption * sts_moves_per_element * energy_price
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        "Stack equipment energy costs"
        if self.stack_equipment == 'rmg':
            list_of_elements_Stack = self.find_elements(Stack_Equipment)
            equipment = 0
            for element in self.elements:
                if isinstance(element, Stack_Equipment):
                    if year >= element.year_online:
                        equipment += 1

            for element in list_of_elements_Stack:
                if year >= element.year_online:
                    moves = stack_moves / equipment
                    consumption = element.power_consumption
                    costs = energy_price
                    if consumption * costs * moves != np.inf:
                        element.df.loc[element.df['year'] == year, 'energy'] = consumption * costs * moves
                else:
                    element.df.loc[element.df['year'] == year, 'energy'] = 0

        "Reefer energy costs"
        stack_capacity_planned, stack_capacity_online, required_capacity, total_ground_slots, laden_stack_area, reefer_slots = self.laden_reefer_stack_capacity(year)

        stacks = 0
        for element in self.elements:
            if isinstance(element, Laden_Stack):
                if year >= element.year_online:
                    stacks += 1

        for element in self.find_elements(Laden_Stack):
            if year >= element.year_online:
                slots_per_stack = reefer_slots / stacks
                if slots_per_stack * element.reefers_present * energy_price * 24 * 365 != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = slots_per_stack * element.reefers_present \
                                                                           * energy_price * 24 * 365
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        "General power use"

        general = General_Services(**container_defaults.general_services_data)

        'lighting'
        quay_land_use = 0
        stack_land_use = 0
        empty_land_use = 0
        oog_land_use = 0
        gate_land_use = 0
        general_land_use = 0

        for element in self.elements:
            if isinstance(element, Quay_Wall):
                if year >= element.year_online:
                    quay_land_use += element.land_use
            if isinstance(element, Laden_Stack):
                if year >= element.year_online:
                    stack_land_use += element.land_use
            if isinstance(element, Empty_Stack):
                if year >= element.year_online:
                    empty_land_use += element.land_use
            if isinstance(element, OOG_Stack):
                if year >= element.year_online:
                    oog_land_use += element.land_use
            if isinstance(element, Gate):
                if year >= element.year_online:
                    gate_land_use += element.land_use
            if isinstance(element, General_Services):
                if year >= element.year_online:
                    general_land_use += element.land_use

        total_land_use = quay_land_use + stack_land_use + empty_land_use + oog_land_use + gate_land_use + general_land_use
        lighting = total_land_use * energy_price * general.lighting_consumption

        'office, gates, workshops'
        general_consumption = general.general_consumption * energy_price * self.operational_hours
        for element in self.find_elements(General_Services):
            if year >= element.year_online:
                if lighting + general_consumption != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = lighting + general_consumption
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

    def calculate_general_labour_cost(self, year):
        """ General labour """

        general = General_Services(**container_defaults.general_services_data)
        laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)
        throughput = laden_teu + reefer_teu + oog_teu + empty_teu
        labour = Labour(**container_defaults.labour_data)

        cranes = 0
        for element in self.elements:
            if isinstance(element, Cyclic_Unloader):
                if year >= element.year_online:
                    cranes += 1
        sts_cranes = cranes
        if sts_cranes != 0:
            crew_required = np.ceil(throughput / general.crew_required)

            # fixed labour
            total_fte_fixed = crew_required * (
                    general.ceo + general.secretary + general.administration + general.hr + general.commercial)
            fixed_labour = total_fte_fixed * labour.white_collar_salary

            # shift labour
            white_collar = crew_required * labour.daily_shifts * general.operations * labour.white_collar_salary
            blue_collar = crew_required * labour.daily_shifts * (general.engineering + general.security) * labour.blue_collar_salary

            shift_labour = white_collar + blue_collar

            # total labour
            list_of_elements_general = self.find_elements(General_Services)

            for element in list_of_elements_general:
                if year >= element.year_online:
                    if fixed_labour + shift_labour != np.inf:
                        element.df.loc[element.df['year'] == year, 'labour'] = fixed_labour + shift_labour
                else:
                    element.df.loc[element.df['year'] == year, 'labour'] = 0

    def calculate_fuel_cost(self, year):
        sts_moves, stack_moves, empty_moves, tractor_moves = self.box_moves(year)
        fuel_price = self.fuel_price

        # calculate empty handler fuel costs
        list_of_elements_ech = self.find_elements(Empty_Handler)
        equipment = 0
        for element in self.elements:
            if isinstance(element, Empty_Handler):
                if year >= element.year_online:
                    equipment += 1

        for element in list_of_elements_ech:
            if year >= element.year_online:
                moves = empty_moves / equipment
                consumption = element.fuel_consumption
                costs = fuel_price
                if consumption * costs * moves != np.inf:
                    element.df.loc[element.df['year'] == year, 'fuel'] = consumption * costs * moves
            else:
                element.df.loc[element.df['year'] == year, 'fuel'] = 0

        # calculate stack equipment fuel costs
        if self.stack_equipment == 'rtg' or self.stack_equipment == 'rs' or self.stack_equipment == 'sc':
            list_of_elements_Stack = self.find_elements(Stack_Equipment)
            equipment = 0
            for element in self.elements:
                if isinstance(element, Stack_Equipment):
                    if year >= element.year_online:
                        equipment += 1

            for element in list_of_elements_Stack:
                if year >= element.year_online:
                    moves = stack_moves / equipment
                    consumption = element.fuel_consumption
                    costs = fuel_price
                    if consumption * costs * moves != np.inf:
                        element.df.loc[element.df['year'] == year, 'fuel'] = consumption * costs * moves
                else:
                    element.df.loc[element.df['year'] == year, 'fuel'] = 0

        # calculate tractor fuel consumption
        list_of_elements_Tractor = self.find_elements(Horizontal_Transport)

        transport = 0
        for element in self.elements:
            if isinstance(element, Horizontal_Transport):
                if year >= element.year_online:
                    transport += 1

        for element in list_of_elements_Tractor:
            if year >= element.year_online:
                moves = tractor_moves / transport
                if element.fuel_consumption * moves * fuel_price != np.inf:
                    element.df.loc[element.df['year'] == year, 'fuel'] = \
                        element.fuel_consumption * moves * fuel_price

            else:
                element.df.loc[element.df['year'] == year, 'fuel'] = 0

    def calculate_demurrage_cost(self, year):

        """Find the demurrage cost per type of vessel and sum all demurrage cost"""

        fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls, total_calls, total_vol \
            = self.calculate_vessel_calls(year)

        factor, waiting_time_occupancy = self.waiting_time(year)

        # Find the service_rate per quay_wall to find the average service hours at the quay for a vessel
        quay_walls = len(self.find_elements(Quay_Wall))

        service_rate = 0
        for element in self.find_elements(Cyclic_Unloader):
            if year >= element.year_online:
                service_rate += element.effective_capacity / quay_walls

        # Find the demurrage cost per type of vessel
        if service_rate != 0:
            fully_cellular = Vessel(**container_defaults.fully_cellular_data)
            service_time_fully_cellular = fully_cellular.call_size / service_rate
            waiting_time_hours_fully_cellular = factor * service_time_fully_cellular
            port_time_fully_cellular = waiting_time_hours_fully_cellular + service_time_fully_cellular + fully_cellular.mooring_time
            penalty_time_fully_cellular = max(0, waiting_time_hours_fully_cellular - fully_cellular.all_turn_time)
            demurrage_time_fully_cellular = penalty_time_fully_cellular * fully_cellular_calls
            demurrage_cost_fully_cellular = demurrage_time_fully_cellular * fully_cellular.demurrage_rate

            panamax = Vessel(**container_defaults.panamax_data)
            service_time_panamax = panamax.call_size / service_rate
            waiting_time_hours_panamax = factor * service_time_panamax
            port_time_panamax = waiting_time_hours_panamax + service_time_panamax + panamax.mooring_time
            penalty_time_panamax = max(0, waiting_time_hours_panamax - panamax.all_turn_time)
            demurrage_time_panamax = penalty_time_panamax * panamax_calls
            demurrage_cost_panamax = demurrage_time_panamax * panamax.demurrage_rate

            panamax_max = Vessel(**container_defaults.panamax_max_data)
            service_time_panamax_max = panamax_max.call_size / service_rate
            waiting_time_hours_panamax_max = factor * service_time_panamax_max
            port_time_panamax_max = waiting_time_hours_panamax_max + service_time_panamax_max + panamax_max.mooring_time
            penalty_time_panamax_max = max(0, waiting_time_hours_panamax_max - panamax_max.all_turn_time)
            demurrage_time_panamax_max = penalty_time_panamax_max * panamax_max_calls
            demurrage_cost_panamax_max = demurrage_time_panamax_max * panamax_max.demurrage_rate

            post_panamax_I = Vessel(**container_defaults.post_panamax_I_data)
            service_time_post_panamax_I = post_panamax_I.call_size / service_rate
            waiting_time_hours_post_panamax_I = factor * service_time_post_panamax_I
            port_time_post_panamax_I = waiting_time_hours_post_panamax_I + service_time_post_panamax_I + post_panamax_I.mooring_time
            penalty_time_post_panamax_I = max(0, waiting_time_hours_post_panamax_I - post_panamax_I.all_turn_time)
            demurrage_time_post_panamax_I = penalty_time_post_panamax_I * post_panamax_I_calls
            demurrage_cost_post_panamax_I = demurrage_time_post_panamax_I * post_panamax_I.demurrage_rate

            post_panamax_II = Vessel(**container_defaults.post_panamax_II_data)
            service_time_post_panamax_II = post_panamax_II.call_size / service_rate
            waiting_time_hours_post_panamax_II = factor * service_time_post_panamax_II
            port_time_post_panamax_II = waiting_time_hours_post_panamax_II + service_time_post_panamax_II + post_panamax_II.mooring_time
            penalty_time_post_panamax_II = max(0, waiting_time_hours_post_panamax_II - post_panamax_II.all_turn_time)
            demurrage_time_post_panamax_II = penalty_time_post_panamax_II * post_panamax_II_calls
            demurrage_cost_post_panamax_II = demurrage_time_post_panamax_II * post_panamax_II.demurrage_rate

            new_panamax = Vessel(**container_defaults.new_panamax_data)
            service_time_new_panamax = new_panamax.call_size / service_rate
            waiting_time_hours_new_panamax = factor * service_time_new_panamax
            port_time_new_panamax = waiting_time_hours_new_panamax + service_time_new_panamax + new_panamax.mooring_time
            penalty_time_new_panamax = max(0, waiting_time_hours_new_panamax - new_panamax.all_turn_time)
            demurrage_time_new_panamax = penalty_time_new_panamax * new_panamax_calls
            demurrage_cost_new_panamax = demurrage_time_new_panamax * new_panamax.demurrage_rate

            VLCS = Vessel(**container_defaults.VLCS_data)
            service_time_VLCS = VLCS.call_size / service_rate
            waiting_time_hours_VLCS = factor * service_time_VLCS
            port_time_VLCS = waiting_time_hours_VLCS + service_time_VLCS + VLCS.mooring_time
            penalty_time_VLCS = max(0, waiting_time_hours_VLCS - VLCS.all_turn_time)
            demurrage_time_VLCS = penalty_time_VLCS * VLCS_calls
            demurrage_cost_VLCS = demurrage_time_VLCS * VLCS.demurrage_rate

            ULCS = Vessel(**container_defaults.ULCS_data)
            service_time_ULCS = ULCS.call_size / service_rate
            waiting_time_hours_ULCS = factor * service_time_ULCS
            port_time_ULCS = waiting_time_hours_ULCS + service_time_ULCS + ULCS.mooring_time
            penalty_time_ULCS = max(0, waiting_time_hours_ULCS - ULCS.all_turn_time)
            demurrage_time_ULCS = penalty_time_ULCS * ULCS_calls
            demurrage_cost_ULCS = demurrage_time_ULCS * ULCS.demurrage_rate

        else:
            demurrage_cost_fully_cellular = 0
            demurrage_cost_panamax = 0
            demurrage_cost_panamax_max = 0
            demurrage_cost_post_panamax_I = 0
            demurrage_cost_post_panamax_II = 0
            demurrage_cost_new_panamax = 0
            demurrage_cost_VLCS = 0
            demurrage_cost_ULCS = 0

        total_demurrage_cost = demurrage_cost_fully_cellular + demurrage_cost_panamax + demurrage_cost_panamax_max + \
                               demurrage_cost_post_panamax_I + demurrage_cost_post_panamax_II + demurrage_cost_new_panamax + \
                               demurrage_cost_VLCS + demurrage_cost_ULCS

        self.demurrage.append(total_demurrage_cost)

    # def calculate_indirect_costs(self, year):
    #     # todo fix this element, or remove it
    #     indirect = Indirect_Costs(**container_defaults.indirect_costs_data)
    #     cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()
    #     capex = cash_flows['capex'].values
    #     print(capex)
    #     if self.stack_equipment == 'rtg' or self.stack_equipment == 'rs' or self.stack_equipment == 'sc':
    #         electrical_works = indirect.electrical_works_fuel_terminal * capex
    #     elif self.stack_equipment == 'rmg' or self.stack_equipment == 'ertg':
    #         electrical_works = indirect.electrical_works_power_terminal * capex
    #
    #     miscellaneous = indirect.miscellaneous * capex
    #     preliminaries = indirect.preliminaries * capex
    #     engineering = indirect.engineering * capex
    #
    #     indirect_costs = capex + electrical_works + miscellaneous + preliminaries + engineering
    #     print(indirect_costs)
    #     # cash_flows['capex'].values = indirect_costs

    def calculate_overseas_transport_costs(self, year):
        """"
        The ocean transport depends on the ship type and the average overseas distance per ship type.
        1. At first find the calls per ship type.
        2. Find the total energy price to multiply the consumption with the energy price
        """

        fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS, total_calls, total_vol \
            = self.calculate_vessel_calls(year)

        def transport_costs(self):
            self.transport_costs = int(sum(self.average_distance_fully_cellular * self.starting_fee))

    """ Terminal investment functions """

    def berth_invest(self, year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS):  # QSC: berth occupancy

        """ Current strategy is to add berth if the berth_occupancy > allowable_berth_occupancy:
            - allowable_berth_occupancy = .40 # 40%
            - a berth needs: i) a quay and ii) cranes (min:1 and max: max_cranes)
            - berth occupancy depends on: i) total_calls and total_vol and ii) total_service_capacity as delivered by the cranes
            - adding quay and cranes decreases berth_occupancy_rate"""

        # report on the status of all berth elements
        self.report_element(Berth, year)
        self.report_element(Quay_Wall, year)
        self.report_element(Cyclic_Unloader, year)
        if self.debug:
            print('')
            print('  Start analysis:')

        # calculate berth occupancy
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
            year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
        factor, waiting_time_occupancy = self.waiting_time(year)

        if self.debug:
            print('     Berth occupancy planned (@ start of year): {}'.format(berth_occupancy_planned))
            print('     Berth occupancy online (@ start of year): {}'.format(berth_occupancy_online))
            print('     Crane occupancy planned (@ start of year): {}'.format(crane_occupancy_planned))
            print('     Crane occupancy online (@ start of year): {}'.format(crane_occupancy_online))
            print('     waiting time factor (@ start of year): {}'.format(factor))
            print('     waiting time occupancy (@ start of year): {}'.format(waiting_time_occupancy))

        # if the planned berth occupancy is higher than the allowable berth occupancy, add a berth when no crane slots are available
        while berth_occupancy_planned > self.allowable_berth_occupancy:
            if not (self.check_crane_slot_available()):
                if self.debug:
                    print('  *** add Berth to elements')
                berth = Berth(**container_defaults.berth_data)
                berth.year_online = year + berth.delivery_time
                self.elements.append(berth)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
                if self.debug:
                    print('     Berth occupancy planned (after adding berth): {}'.format(berth_occupancy_planned))
                    print('     Berth occupancy online (after adding berth): {}'.format(berth_occupancy_online))

            # check if a quay is needed
            berths = len(self.find_elements(Berth))
            quay_walls = len(self.find_elements(Quay_Wall))
            if berths > quay_walls:
                length_v = max(container_defaults.fully_cellular_data["LOA"],
                               container_defaults.panamax_data["LOA"],
                               container_defaults.panamax_max_data["LOA"],
                               container_defaults.post_panamax_I_data["LOA"],
                               container_defaults.post_panamax_II_data["LOA"],
                               container_defaults.new_panamax_data["LOA"],
                               container_defaults.VLCS_data["LOA"],
                               container_defaults.ULCS_data["LOA"])
                draught = max(container_defaults.fully_cellular_data["draught"],
                              container_defaults.panamax_data["draught"],
                              container_defaults.panamax_max_data["draught"],
                              container_defaults.post_panamax_I_data["draught"],
                              container_defaults.post_panamax_II_data["draught"],
                              container_defaults.new_panamax_data["draught"],
                              container_defaults.VLCS_data["draught"],
                              container_defaults.ULCS_data["draught"])

                # PIANC 2014 (see Ijzermans, 2019 - infrastructure.py line 107 - 111)
                # quay wall length
                if quay_walls == 0:
                    # length when next quay is n = 1
                    length = length_v + 2 * 15
                elif quay_walls == 1:
                    # length when next quay is n > 1
                    length = 1.1 * berths * (length_v + 15) - (length_v + 2 * 15)
                else:
                    length = 1.1 * berths * (length_v + 15) - 1.1 * (berths - 1) * (length_v + 15)

                # quay wall depth
                quay_wall = Quay_Wall(**container_defaults.quay_wall_data)
                depth = np.sum([draught, quay_wall.max_sinkage, quay_wall.wave_motion, quay_wall.safety_margin])
                self.quay_invest(year, length, depth)  # todo check

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
                if self.debug:
                    print('     Berth occupancy planned (after adding quay): {}'.format(berth_occupancy_planned))
                    print('     Berth occupancy online (after adding quay): {}'.format(berth_occupancy_online))

            # check if a crane is needed
            if self.check_crane_slot_available():
                self.crane_invest(year)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
                if self.debug:
                    print('     Berth occupancy planned (after adding crane): {}'.format(berth_occupancy_planned))
                    print('     Berth occupancy online (after adding crane): {}'.format(berth_occupancy_online))

    def quay_invest(self, year, length, depth):  # QSC: quay_per_berth

        """ Current strategy is to add quay as quay_per_berth < 1
            - adding quay will increase quay_per_berth
            - quay_wall.length must be long enough to accommodate largest expected vessel
            - quay_wall.depth must be deep enough to accommodate largest expected vessel
            - quay_wall.freeboard must be high enough to accommodate largest expected vessel"""

        if self.debug:
            print('  *** add Quay to elements')
        # add a Quay_Wall element

        quay_wall = Quay_Wall(**container_defaults.quay_wall_data)

        # capex
        unit_rate = int(quay_wall.Gijt_constant * (depth * 2 + quay_wall.freeboard) ** quay_wall.Gijt_coefficient)  # todo check haakjes, staat anders in rapport Wijnand
        mobilisation = int(max((length * unit_rate * quay_wall.mobilisation_perc), quay_wall.mobilisation_min))
        apron_pavement = length * quay_wall.apron_width * quay_wall.apron_pavement
        cost_of_land = length * quay_wall.apron_width * self.land_price
        quay_wall.capex = int(length * unit_rate + mobilisation + apron_pavement + cost_of_land)
        # quay_wall.capex = int(apron_pavement + cost_of_land)

        # - opex
        quay_wall.insurance = unit_rate * length * quay_wall.insurance_perc
        quay_wall.maintenance = unit_rate * length * quay_wall.maintenance_perc
        quay_wall.year_online = year + quay_wall.delivery_time

        # land use
        quay_wall.land_use = length * quay_wall.apron_width

        # add cash flow information to quay_wall object in a DataFrame
        quay_wall = self.add_cashflow_data_to_element(quay_wall)

        self.elements.append(quay_wall)

    def crane_invest(self, year):

        """ Current strategy is to add cranes as soon as a service trigger is achieved
            - find out how much service capacity is online
            - find out how much service capacity is planned
            - find out how much service capacity is needed
            - add service capacity until service_trigger is no longer exceeded"""

        if self.debug:
            print('  *** add STS crane to elements')
        # add unloader object
        if (self.crane_type_defaults["crane_type"] == 'Gantry crane' or
                self.crane_type_defaults["crane_type"] == 'Harbour crane' or
                self.crane_type_defaults["crane_type"] == 'STS crane' or
                self.crane_type_defaults["crane_type"] == 'Mobile crane'):
            crane = Cyclic_Unloader(**self.crane_type_defaults)

        # - capex
        unit_rate = crane.unit_rate
        mobilisation = unit_rate * crane.mobilisation_perc
        crane.capex = int(unit_rate + mobilisation)

        # - opex
        crane.insurance = unit_rate * crane.insurance_perc
        crane.maintenance = unit_rate * crane.maintenance_perc

        #   labour
        labour = Labour(**container_defaults.labour_data)
        crane.shift = ((crane.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))  # crew/crane/year
        crane.labour = crane.shift * labour.blue_collar_salary  # USD/crane/year

        # apply proper timing for the crane to come online (in the same year as the latest Quay_Wall)
        years_online = []
        for element in self.find_elements(Quay_Wall):
            years_online.append(element.year_online)
        crane.year_online = max([year + crane.delivery_time, max(years_online)])

        # add cash flow information to quay_wall object in a DataFrame
        crane = self.add_cashflow_data_to_element(crane)

        # add object to elements
        self.elements.append(crane)

    def horizontal_transport_invest(self, year):

        """ Current strategy is to add horizontal transport as soon as a service trigger is achieved
            - find out how much transport is online
            - find out how much transport is planned
            - find out how much transport is needed
            - add transport until service_trigger is no longer exceeded"""

        throughput_online = self.calculate_throughput(year)  # todo check
        cranes = 0
        transport = 0
        for element in self.elements:
            if isinstance(element, Cyclic_Unloader):
                if year >= element.year_online:
                    cranes += 1
            if isinstance(element, Horizontal_Transport):
                if year >= element.year_online:
                    transport += 1
        sts_cranes = cranes
        tractor_online = transport

        tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)

        if self.debug:
            # print('     Horizontal transport planned (@ start of year): {}'.format(tractor_planned))
            print('     Horizontal transport online (@ start of year): {}'.format(tractor_online))
            print('     Number of STS cranes (@start of year): {}'.format(sts_cranes))

        if self.stack_equipment != 'sc':

            while sts_cranes > (tractor_online // tractor.required):
                # add a tractor when not enough to serve number of STS cranes
                if self.debug:
                    print('  *** add tractor to elements')

                tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)

                # - capex
                unit_rate = tractor.unit_rate
                mobilisation = tractor.mobilisation
                tractor.capex = int(unit_rate + mobilisation)

                # - opex
                tractor.maintenance = unit_rate * tractor.maintenance_perc

                #   labour
                labour = Labour(**container_defaults.labour_data)
                tractor.shift = ((tractor.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))  # crew/tractor/year
                tractor.labour = tractor.shift * labour.blue_collar_salary  # USD/tractor/year

                if year == self.startyear:
                    tractor.year_online = year + tractor.delivery_time + 1
                else:
                    tractor.year_online = year + tractor.delivery_time

                # add cash flow information to tractor object in a DataFrame
                tractor = self.add_cashflow_data_to_element(tractor)

                self.elements.append(tractor)

                list_of_elements_tractor = self.find_elements(Horizontal_Transport)
                tractor_online = len(list_of_elements_tractor)

        return sts_cranes

    def empty_handler_invest(self, year):

        """ Current strategy is to add empty handlers as soon as a service trigger is achieved
            - find out how many empty handlers are online
            - find out how many empty handlers are planned
            - find out how many empty handlers are needed
            - add empty handlers until service_trigger is no longer exceeded"""

        list_of_elements_empty_handler = self.find_elements(Empty_Handler)
        list_of_elements_sts = self.find_elements(Cyclic_Unloader)
        sts_cranes = len(list_of_elements_sts)
        empty_handler_online = len(list_of_elements_empty_handler)

        empty_handler = Empty_Handler(**container_defaults.empty_handler_data)

        if self.debug:
            # print('     Horizontal transport planned (@ start of year): {}'.format(tractor_planned))
            print('     Empty handlers online (@ start of year): {}'.format(empty_handler_online))

        while sts_cranes > (empty_handler_online // empty_handler.required):
            # add a tractor when not enough to serve number of STS cranes
            if self.debug:
                print('  *** add tractor to elements')

            # - capex
            unit_rate = empty_handler.unit_rate
            mobilisation = empty_handler.mobilisation
            empty_handler.capex = int(unit_rate + mobilisation)

            # - opex
            empty_handler.maintenance = unit_rate * empty_handler.maintenance_perc

            #   labour
            labour = Labour(**container_defaults.labour_data)
            empty_handler.shift = ((empty_handler.crew * self.operational_hours) / (labour.shift_length * labour.annual_shifts))  # crew/empty_handler/year
            empty_handler.labour = empty_handler.shift * labour.blue_collar_salary  # USD/empty_handler/year

            if year == self.startyear:
                empty_handler.year_online = year + empty_handler.delivery_time + 1
            else:
                empty_handler.year_online = year + empty_handler.delivery_time

            # add cash flow information to tractor object in a DataFrame
            empty_handler = self.add_cashflow_data_to_element(empty_handler)

            self.elements.append(empty_handler)

            list_of_elements_empty_handler = self.find_elements(Empty_Handler)
            empty_handler_online = len(list_of_elements_empty_handler)

    def laden_stack_invest(self, year):

        """ Current strategy is to add laden stacks as soon as trigger is achieved
            - find out how much laden stack capacity is online
            - find out how much laden stack capacity is planned
            - find out how much laden stack capacity is needed
            - add stack capacity until service_trigger is no longer exceeded"""

        stack_capacity_planned, stack_capacity_online, required_capacity, total_ground_slots, laden_stack_area, reefer_slots = self.laden_reefer_stack_capacity(year)

        if self.debug:
            print('     Stack capacity planned (@ start of year): {}'.format(stack_capacity_planned))
            print('     Stack capacity online (@ start of year): {}'.format(stack_capacity_online))
            print('     Stack capacity required (@ start of year): {}'.format(required_capacity))
            print('     Total laden and reefer ground slots required (@ start of year): {}'.format(total_ground_slots))

        while required_capacity > stack_capacity_planned:
            if self.debug:
                print('  *** add laden stack to elements')

            if self.laden_stack == 'rtg':
                stack = Laden_Stack(**container_defaults.rtg_stack_data)
            elif self.laden_stack == 'rmg':
                stack = Laden_Stack(**container_defaults.rmg_stack_data)
            elif self.laden_stack == 'sc':
                stack = Laden_Stack(**container_defaults.sc_stack_data)
            elif self.laden_stack == 'rs':
                stack = Laden_Stack(**container_defaults.rs_stack_data)

            reefer_slots = (self.reefer_perc / self.laden_perc) * stack.capacity

            # - land use
            stack_ground_slots = stack.capacity / stack.height
            stack.land_use = (stack_ground_slots * stack.gross_tgs) * stack.area_factor

            # - capex
            area = stack.length * stack.width
            gross_tgs = stack.gross_tgs
            pavement = stack.pavement
            drainage = stack.drainage
            area_factor = stack.area_factor
            reefer_rack = reefer_slots * stack.reefer_rack
            mobilisation = stack.mobilisation
            cost_of_land = self.land_price
            stack.capex = int(
                (pavement + drainage + cost_of_land) * gross_tgs * area * area_factor + mobilisation + reefer_rack)

            # - opex
            stack.maintenance = int((pavement + drainage) * gross_tgs * area * area_factor * stack.maintenance_perc)

            if year == self.startyear:
                stack.year_online = year + stack.delivery_time + 1
            else:
                stack.year_online = year + stack.delivery_time

            # add cash flow information to quay_wall object in a DataFrame
            stack = self.add_cashflow_data_to_element(stack)

            self.elements.append(stack)

            stack_capacity_planned, stack_capacity_online, required_capacity, total_ground_slots, laden_stack_area, reefer_slots = self.laden_reefer_stack_capacity(year)

    def empty_stack_invest(self, year):

        """ Current strategy is to add stacks as soon as trigger is achieved
            - find out how much stack capacity is online
            - find out how much stack capacity is planned
            - find out how much stack capacity is needed
            - add stack capacity until service_trigger is no longer exceeded"""

        empty_capacity_planned, empty_capacity_online, empty_required_capacity, empty_ground_slots, empty_stack_area = self.empty_stack_capacity(year)

        if self.debug:
            print('     Empty stack capacity planned (@ start of year): {}'.format(empty_capacity_planned))
            print('     Empty stack capacity online (@ start of year): {}'.format(empty_capacity_online))
            print('     Empty stack capacity required (@ start of year): {}'.format(empty_required_capacity))
            print('     Empty ground slots required (@ start of year): {}'.format(empty_ground_slots))

        while empty_required_capacity > empty_capacity_planned:
            if self.debug:
                print('  *** add empty stack to elements')

            empty_stack = Empty_Stack(**container_defaults.empty_stack_data)

            # - land use
            stack_ground_slots = empty_stack.capacity / empty_stack.height
            empty_stack.land_use = (stack_ground_slots * empty_stack.gross_tgs) * empty_stack.area_factor

            # - capex
            area = empty_stack.length * empty_stack.width
            gross_tgs = empty_stack.gross_tgs
            pavement = empty_stack.pavement
            drainage = empty_stack.drainage
            area_factor = empty_stack.area_factor
            mobilisation = empty_stack.mobilisation
            cost_of_land = self.land_price
            empty_stack.capex = int(
                (pavement + drainage + cost_of_land) * gross_tgs * area * area_factor + mobilisation)

            # - opex
            empty_stack.maintenance = int(
                (pavement + drainage) * gross_tgs * area * area_factor * empty_stack.maintenance_perc)

            if year == self.startyear:
                empty_stack.year_online = year + empty_stack.delivery_time + 1
            else:
                empty_stack.year_online = year + empty_stack.delivery_time

            # add cash flow information to quay_wall object in a DataFrame
            empty_stack = self.add_cashflow_data_to_element(empty_stack)

            self.elements.append(empty_stack)

            empty_capacity_planned, empty_capacity_online, empty_required_capacity, empty_ground_slots, \
            empty_stack_area = self.empty_stack_capacity(
                year)

    def oog_stack_invest(self, year):  # out of gauge

        """ Current strategy is to add stacks as soon as trigger is achieved
            - find out how much OOG stack capacity is online
            - find out how much OOG stack capacity is planned
            - find out how much OOG stack capacity is needed
            - add stack capacity until service_trigger is no longer exceeded"""

        oog_capacity_planned, oog_capacity_online, oog_required_capacity = self.oog_stack_capacity(year)

        if self.debug:
            print('     OOG slots planned (@ start of year): {}'.format(oog_capacity_planned))
            print('     OOG slots online (@ start of year): {}'.format(oog_capacity_online))
            print('     OOG slots required (@ start of year): {}'.format(oog_required_capacity))

        while oog_required_capacity > oog_capacity_planned:
            if self.debug:
                print('  *** add OOG stack to elements')

            oog_stack = OOG_Stack(**container_defaults.oog_stack_data)

            # - capex
            area = oog_stack.length * oog_stack.width
            gross_tgs = oog_stack.gross_tgs
            pavement = oog_stack.pavement
            drainage = oog_stack.drainage
            area_factor = oog_stack.area_factor
            mobilisation = oog_stack.mobilisation
            cost_of_land = self.land_price
            oog_stack.capex = int((pavement + drainage + cost_of_land) * gross_tgs * area * area_factor + mobilisation)

            # - opex
            oog_stack.maintenance = int((pavement + drainage) * gross_tgs * area * area_factor * oog_stack.maintenance_perc)

            # - land use
            stack_ground_slots = oog_stack.capacity / oog_stack.height
            oog_stack.land_use = stack_ground_slots * oog_stack.gross_tgs

            if year == self.startyear:
                oog_stack.year_online = year + oog_stack.delivery_time + 1
            else:
                oog_stack.year_online = year + oog_stack.delivery_time

            # add cash flow information to quay_wall object in a DataFrame
            oog_stack = self.add_cashflow_data_to_element(oog_stack)

            self.elements.append(oog_stack)

            oog_capacity_planned, oog_capacity_online, oog_required_capacity = self.oog_stack_capacity(year)

    def stack_equipment_invest(self, year):

        """ Current strategy is to add stack equipment as soon as a service trigger is achieved
            - find out how much stack equipment is online
            - find out how much stack equipment is planned
            - find out how much stack equipment is needed
            - add equipment until service_trigger is no longer exceeded"""

        cranes = 0
        equipment = 0
        stack = 0
        for element in self.elements:
            if isinstance(element, Cyclic_Unloader):
                if year >= element.year_online:
                    cranes += 1
            if isinstance(element, Stack_Equipment):
                if year >= element.year_online:
                    equipment += 1
            if isinstance(element, Laden_Stack):
                if year >= element.year_online:
                    stack += 1

        sts_cranes = cranes
        stack_equipment_online = equipment

        if self.stack_equipment == 'rtg':
            stack_equipment = Stack_Equipment(**container_defaults.rtg_data)
        elif self.stack_equipment == 'rmg':
            stack_equipment = Stack_Equipment(**container_defaults.rmg_data)
        elif self.stack_equipment == 'sc':
            stack_equipment = Stack_Equipment(**container_defaults.sc_data)
        elif self.stack_equipment == 'rs':
            stack_equipment = Stack_Equipment(**container_defaults.rs_data)

        if self.debug:
            print('     Number of stack equipment online (@ start of year): {}'.format(stack_equipment_online))

        if (self.stack_equipment == 'rtg' or
                self.stack_equipment == 'sc' or
                self.stack_equipment == 'rs'):
            while sts_cranes > (stack_equipment_online // stack_equipment.required):

                # add stack equipment when not enough to serve number of STS cranes
                if self.debug:
                    print('  *** add stack equipment to elements')

                # - capex
                unit_rate = stack_equipment.unit_rate
                mobilisation = stack_equipment.mobilisation
                stack_equipment.capex = int(unit_rate + mobilisation)

                # - opex # todo calculate moves for energy costs
                stack_equipment.insurance = unit_rate * stack_equipment.insurance_perc
                stack_equipment.maintenance = unit_rate * stack_equipment.maintenance_perc

                #   labour
                labour = Labour(**container_defaults.labour_data)
                stack_equipment.shift = stack_equipment.crew * labour.daily_shifts  # todo check operational hours
                stack_equipment.labour = stack_equipment.shift * labour.blue_collar_salary

                if year == self.startyear:
                    stack_equipment.year_online = year + stack_equipment.delivery_time + 1
                else:
                    stack_equipment.year_online = year + stack_equipment.delivery_time

                # add cash flow information to tractor object in a DataFrame
                stack_equipment = self.add_cashflow_data_to_element(stack_equipment)

                self.elements.append(stack_equipment)

                list_of_elements_stack_equipment = self.find_elements(Stack_Equipment)
                stack_equipment_online = len(list_of_elements_stack_equipment)

        if self.stack_equipment == 'rmg':
            while stack > (stack_equipment_online * 0.5):

                # add stack equipment when not enough to serve number of STS cranes
                if self.debug:
                    print('  *** add stack equipment to elements')

                # - capex
                unit_rate = stack_equipment.unit_rate
                mobilisation = stack_equipment.mobilisation
                stack_equipment.capex = int(unit_rate + mobilisation)

                # - opex # todo calculate moves for energy costs
                stack_equipment.insurance = unit_rate * stack_equipment.insurance_perc
                stack_equipment.maintenance = unit_rate * stack_equipment.maintenance_perc

                #   labour
                labour = Labour(**container_defaults.labour_data)
                stack_equipment.shift = stack_equipment.crew * labour.daily_shifts  # todo check operational hours
                stack_equipment.labour = stack_equipment.shift * labour.blue_collar_salary

                if year == self.startyear:
                    stack_equipment.year_online = year + stack_equipment.delivery_time + 1
                else:
                    stack_equipment.year_online = year + stack_equipment.delivery_time

                # add cash flow information to tractor object in a DataFrame
                stack_equipment = self.add_cashflow_data_to_element(stack_equipment)

                self.elements.append(stack_equipment)

                list_of_elements_stack_equipment = self.find_elements(Stack_Equipment)
                stack_equipment_online = len(list_of_elements_stack_equipment)

    def gate_invest(self, year):  # todo check if a generic onshore berth is possible

        """ Current strategy is to add gates as soon as trigger is achieved
            - find out how much gate capacity is online
            - find out how much gate capacity is planned
            - find out how much gate capacity is needed
            - add gate capacity until service_trigger is no longer exceeded"""

        gate_capacity_planned, gate_capacity_online, service_rate_planned, total_design_gate_minutes = self.calculate_gate_minutes(year)

        if self.debug:
            print('     Gate capacity planned (@ start of year): {}'.format(gate_capacity_planned))
            print('     Gate capacity online (@ start of year): {}'.format(gate_capacity_online))
            print('     Gate service rate planned (@ start of year): {}'.format(service_rate_planned))
            print('     Gate lane minutes  (@ start of year): {}'.format(total_design_gate_minutes))

        while service_rate_planned > 1:
            if self.debug:
                print('  *** add gate to elements')

            gate = Gate(**container_defaults.gate_data)

            tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)

            # - land use
            gate.land_use = gate.area

            # - capex
            unit_rate = gate.unit_rate
            mobilisation = gate.mobilisation
            canopy = gate.canopy_costs * gate.area  # overkapping
            cost_of_land = self.land_price
            gate.capex = int(unit_rate + mobilisation + canopy + (cost_of_land * gate.area))

            # - opex
            gate.maintenance = unit_rate * gate.maintenance_perc

            #   labour
            labour = Labour(**container_defaults.labour_data)
            gate.shift = gate.crew * labour.daily_shifts  # todo check operational hours
            gate.labour = gate.shift * labour.blue_collar_salary

            if year == self.startyear:
                gate.year_online = year + gate.delivery_time + 1
            else:
                gate.year_online = year + gate.delivery_time

            # add cash flow information to tractor object in a DataFrame
            gate = self.add_cashflow_data_to_element(gate)

            self.elements.append(gate)

            gate_capacity_planned, gate_capacity_online, service_rate_planned, total_design_gate_minutes = self.calculate_gate_minutes(year)

    # def barge_berth_invest(self, year):  # todo check
    #
    #     """ Current strategy is to add barge berths as soon as trigger is achieved
    #         - find out how much barge berths capacity is online
    #         - find out how much barge berths capacity is planned
    #         - find out how much barge berths capacity is needed
    #         - add barge berths capacity until service_trigger is no longer exceeded"""
    #
    #     barge_berth_capacity_planned, barge_berth_capacity_online, service_rate_planned, total_design_barge_berth_minutes = self.calculate_barge_berth_minutes(year)
    #
    #     if self.debug:
    #         print('     Barge berth capacity planned (@ start of year): {}'.format(barge_berth_capacity_planned))
    #         print('     Barge berth capacity online (@ start of year): {}'.format(barge_berth_capacity_online))
    #         print('     Barge berth service rate planned (@ start of year): {}'.format(service_rate_planned))
    #         print('     Barge berth lane minutes  (@ start of year): {}'.format(total_design_barge_berth_minutes))
    #
    #     while service_rate_planned > 1:
    #         if self.debug:
    #             print('  *** add barge berth to elements')
    #
    #         barge_berth = Barge_Berth(**container_defaults.barge_berth_data)
    #
    #         tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)
    #
    #         # - land use
    #         barge_berth.land_use = barge_berth.area
    #
    #         # - capex
    #         unit_rate = barge_berth.unit_rate
    #         mobilisation = barge_berth.mobilisation
    #         canopy = barge_berth.canopy_costs * barge_berth.area
    #         cost_of_land = self.land_price
    #         barge_berth.capex = int(unit_rate + mobilisation + canopy + (cost_of_land * barge_berth.area))
    #
    #         # - opex
    #         barge_berth.maintenance = unit_rate * barge_berth.maintenance_perc
    #
    #         #   labour
    #         labour = Labour(**container_defaults.labour_data)
    #         barge_berth.shift = barge_berth.crew * labour.daily_shifts  # todo check operational hours
    #         barge_berth.labour = barge_berth.shift * labour.blue_collar_salary
    #
    #         if year == self.startyear:
    #             barge_berth.year_online = year + barge_berth.delivery_time + 1
    #         else:
    #             barge_berth.year_online = year + barge_berth.delivery_time
    #
    #         # add cash flow information to tractor object in a DataFrame
    #         barge_berth = self.add_cashflow_data_to_element(barge_berth)
    #
    #         self.elements.append(barge_berth)
    #
    #         barge_berth_capacity_planned, barge_berth_capacity_online, service_rate_planned, total_design_barge_berth_minutes = self.calculate_barge_berth_minutes(year)

    def general_services_invest(self, year):

        laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)
        throughput = laden_teu + reefer_teu + oog_teu + empty_teu
        cranes = 0
        general = 0
        for element in self.elements:
            if isinstance(element, Cyclic_Unloader):
                if year >= element.year_online:
                    cranes += 1
            if isinstance(element, General_Services):
                if year >= element.year_online:
                    general += 1
        sts_cranes = cranes

        general = General_Services(**container_defaults.general_services_data)

        quay_land_use = 0
        stack_land_use = 0
        empty_land_use = 0
        oog_land_use = 0
        gate_land_use = 0

        for element in self.elements:
            if isinstance(element, Quay_Wall):
                if year >= element.year_online:
                    quay_land_use += element.land_use
            if isinstance(element, Laden_Stack):
                if year >= element.year_online:
                    stack_land_use += element.land_use
            if isinstance(element, Empty_Stack):
                if year >= element.year_online:
                    empty_land_use += element.land_use
            if isinstance(element, OOG_Stack):
                if year >= element.year_online:
                    oog_land_use += element.land_use
            if isinstance(element, Gate):
                if year >= element.year_online:
                    gate_land_use += element.land_use

        total_land_use = (quay_land_use + stack_land_use + empty_land_use + oog_land_use + gate_land_use + general.office
                          + general.workshop + general.scanning_inspection_area + general.repair_building) * 0.0001

        if year == (self.startyear + 1):
            # add general services as soon as berth  is online
            if self.debug:
                print('  *** add general services to elements')

            # land use
            general.land_use = general.office + general.workshop + general.scanning_inspection_area \
                               + general.repair_building

            # - capex
            area = general.office + general.workshop + general.scanning_inspection_area + general.repair_building
            cost_of_land = self.land_price
            office = general.office * general.office_cost
            workshop = general.workshop * general.workshop_cost
            inspection = general.scanning_inspection_area * general.scanning_inspection_area_cost
            light = general.lighting_mast_cost * (total_land_use / general.lighting_mast_required)
            repair = general.repair_building * general.repair_building_cost
            basic = general.fuel_station_cost + general.firefight_cost + general.maintenance_tools_cost + general.terminal_operating_software_cost + general.electrical_station_cost
            general.capex = office + workshop + inspection + light + repair + basic + (area * cost_of_land)

            # - opex
            general.maintenance = general.capex * general.general_maintenance

            if year == self.startyear:
                general.year_online = year + general.delivery_time
            else:
                general.year_online = year + general.delivery_time

            # add cash flow information to tractor object in a DataFrame
            general = self.add_cashflow_data_to_element(general)

            self.elements.append(general)

    """ Financial analyses """

    def add_cashflow_elements(self):

        cash_flows = pd.DataFrame()

        # initialise cash_flows
        cash_flows['year'] = list(range(self.startyear, self.startyear + self.lifecycle))
        cash_flows['capex'] = 0
        cash_flows['maintenance'] = 0
        cash_flows['insurance'] = 0
        cash_flows['energy'] = 0
        cash_flows['labour'] = 0
        cash_flows['fuel'] = 0
        cash_flows['demurrage'] = 0
        cash_flows['overseas_transport'] = 0
        # cash_flows['revenues'] = self.revenues

        # add labour component for years where revenues are not zero
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
                                (1 + self.WACC_real()) ** (year - self.startyear))

        return cash_flows, cash_flows_WACC_real

    def add_cashflow_data_to_element(self, element):

        """Place cashflow data in element DataFrame"""

        # years
        years = list(range(self.startyear, self.startyear + self.lifecycle))

        # capex
        capex = element.capex

        # opex
        maintenance = element.maintenance
        insurance = element.insurance
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
        if labour:
            df.loc[df["year"] >= year_online, "labour"] = labour

        df.fillna(0, inplace=True)

        element.df = df

        return element

    def WACC_nom(self, Gearing=60, Re=.10, Rd=.30, Tc=.28):
        """Nominal cash flow is the true dollar amount of future revenues the company expects
        to receive and expenses it expects to pay out, including inflation.
        When all cashflows within the model are denoted in real terms and including inflation."""

        Gearing = Gearing
        Re = Re  # return on equity
        Rd = Rd  # return on debt
        Tc = Tc  # income tax
        E = 100 - Gearing
        D = Gearing

        WACC_nom = ((E / (E + D)) * Re + (D / (E + D)) * Rd) * (1 - Tc)

        return WACC_nom

    def WACC_real(self, inflation=0.02):
        """Real cash flow expresses a company's cash flow with adjustments for inflation.
        When all cash flows within the model are denoted in real terms and have been
        adjusted for inflation (no inflation has been taken into account),
        WACC_real should be used. WACC_real is computed by as follows:"""

        WACC_real = (self.WACC_nom() + 1) / (inflation + 1) - 1

        return WACC_real

    def NPV(self):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        "add cash flow information for each of the Terminal elements"
        cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()

        "prepare years, revenue, capex and opex real for plotting"
        years = cash_flows_WACC_real['year'].values
        # revenue = cash_flows_WACC_real['revenues'].values
        capex = cash_flows_WACC_real['capex'].values
        opex = cash_flows_WACC_real['insurance'].values \
               + cash_flows_WACC_real['maintenance'].values \
               + cash_flows_WACC_real['energy'].values \
               + cash_flows_WACC_real['demurrage'].values \
               + cash_flows_WACC_real['fuel'].values \
               + cash_flows_WACC_real['labour'].values  # + cash_flows_WACC_real['overseas_transport'].values
        opex = np.nan_to_num(opex)

        PV = - capex - opex
        print('PV: {}'.format(PV))

        print('NPV: {}'.format(np.sum(PV)))

        # return PV, capex_normal, opex_normal, labour_normal

    """ General functions """

    def find_elements(self, obj):
        """ Return elements of type objects part of self.elements """

        list_of_elements = []
        if self.elements != []:
            for element in self.elements:
                if isinstance(element, obj):
                    list_of_elements.append(element)

        return list_of_elements

    def calculate_vessel_calls(self, year):
        """Calculate volumes to be transported and the number of vessel calls (both per vessel type and in total) """

        # initialize values to be returned
        fully_cellular_vol = 0
        panamax_vol = 0
        panamax_max_vol = 0
        post_panamax_I_vol = 0
        post_panamax_II_vol = 0
        new_panamax_vol = 0
        VLCS_vol = 0
        ULCS_vol = 0
        total_vol = 0

        # gather volumes from each commodity scenario and calculate how much is transported with which vessel
        commodities = self.find_elements(Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                fully_cellular_vol += volume * commodity.fully_cellular_perc / 100
                panamax_vol += volume * commodity.panamax_perc / 100
                panamax_max_vol += volume * commodity.panamax_max_perc / 100
                post_panamax_I_vol += volume * commodity.post_panamax_I_perc / 100
                post_panamax_II_vol += volume * commodity.post_panamax_II_perc / 100
                new_panamax_vol += volume * commodity.new_panamax_perc / 100
                VLCS_vol += volume * commodity.VLCS_perc / 100
                ULCS_vol += volume * commodity.ULCS_perc / 100
                total_vol += volume
            except:
                pass

        # gather vessels and calculate the number of calls each vessel type needs to make
        vessels = self.find_elements(Vessel)
        for vessel in vessels:
            if vessel.type == 'Fully_Cellular':
                fully_cellular_calls = int(np.ceil(fully_cellular_vol / vessel.call_size))
            elif vessel.type == 'Panamax':
                panamax_calls = int(np.ceil(panamax_vol / vessel.call_size))
            elif vessel.type == 'Panamax_Max':
                panamax_max_calls = int(np.ceil(panamax_max_vol / vessel.call_size))
            elif vessel.type == 'Post_Panamax_I':
                post_panamax_I_calls = int(np.ceil(post_panamax_I_vol / vessel.call_size))
            elif vessel.type == 'Post_Panamax_II':
                post_panamax_II_calls = int(np.ceil(post_panamax_II_vol / vessel.call_size))
            elif vessel.type == 'New_Panamax':
                new_panamax_calls = int(np.ceil(new_panamax_vol / vessel.call_size))
            elif vessel.type == 'VLCS':
                VLCS_calls = int(np.ceil(VLCS_vol / vessel.call_size))
            elif vessel.type == 'ULCS':
                ULCS_calls = int(np.ceil(ULCS_vol / vessel.call_size))
        total_calls = np.sum([fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls])

        return fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls, post_panamax_II_calls, \
               new_panamax_calls, VLCS_calls, ULCS_calls, total_calls, total_vol

    def throughput_characteristics(self, year):

        """
        - Find all commodities and the modal split
        - Translate the total TEU/year to every container type throughput
        """

        """ Calculate the total throughput in TEU per year"""
        commodities = self.find_elements(Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        # throughput_online = self.calculate_throughput(year)
        # volume = throughput_online

        laden_teu = volume * self.laden_perc
        reefer_teu = volume * self.reefer_perc
        empty_teu = volume * self.empty_perc
        oog_teu = volume * self.oog_perc

        return laden_teu, reefer_teu, empty_teu, oog_teu

    def throughput_box(self, year):

        """
        - Find all commodities and the modal split
        - Translate the total containers/year to every container type throughput
        """

        """ Calculate the total throughput in containers per year """

        laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)

        laden = Container(**container_defaults.laden_container_data)
        reefer = Container(**container_defaults.reefer_container_data)
        empty = Container(**container_defaults.empty_container_data)
        oog = Container(**container_defaults.oog_container_data)

        laden_box = laden_teu / laden.teu_factor
        reefer_box = reefer_teu / reefer.teu_factor
        empty_box = empty_teu / empty.teu_factor
        oog_box = oog_teu / oog.teu_factor

        throughput_box = laden_box + reefer_box + empty_box + oog_box

        return laden_box, reefer_box, empty_box, oog_box, throughput_box

    def box_moves(self, year):
        """ Calculate the box moves as input for the power and fuel consumption """

        laden_box, reefer_box, empty_box, oog_box, throughput_box = self.throughput_box(year)

        # calculate STS moves
        """ STS cranes are responsible for the throughput (containers over the quay), 
        therefore the total number of boxes is the total number of box moves for STS cranes """

        sts_moves = throughput_box

        # calculate the number of tractor moves
        tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)
        tractor_moves = throughput_box * tractor.non_essential_moves

        # calculate the number of empty moves
        empty = Empty_Stack(**container_defaults.empty_stack_data)
        empty_moves = empty_box * empty.household * empty.digout

        # todo wellicht reefer and laden nog scheiden van elkaar in alles

        # calculate laden and reefer stack moves
        if self.laden_stack == 'rtg':
            stack = Laden_Stack(**container_defaults.rtg_stack_data)
        elif self.laden_stack == 'rmg':
            stack = Laden_Stack(**container_defaults.rmg_stack_data)
        elif self.laden_stack == 'sc':
            stack = Laden_Stack(**container_defaults.sc_stack_data)
        elif self.laden_stack == 'rs':
            stack = Laden_Stack(**container_defaults.rs_stack_data)

        digout_moves = (stack.height - 1) / 2  # JvBeemen

        ''''The number of moves per laden box moves differs for import and export (i/e) and for transhipment (t/s)'''
        moves_i_e = ((2 + stack.household + digout_moves) + ((2 + stack.household) * stack.digout_margin)) / 2
        moves_t_s = 0.5 * ((2 + stack.household) * stack.digout_margin)

        laden_reefer_box_t_s = (laden_box + reefer_box) * self.transhipment_ratio
        laden_reefer_box_i_e = (laden_box + reefer_box) - laden_reefer_box_t_s

        laden_reefer_moves_t_s = laden_reefer_box_t_s * moves_t_s
        laden_reefer_moves_i_e = laden_reefer_box_i_e * moves_i_e

        stack_moves = laden_reefer_moves_i_e + laden_reefer_moves_t_s

        return sts_moves, stack_moves, empty_moves, tractor_moves

    def calculate_land_use(self, year):

        quay_land_use = 0
        stack_land_use = 0
        empty_land_use = 0
        oog_land_use = 0
        gate_land_use = 0
        general_land_use = 0

        for element in self.elements:
            if isinstance(element, Quay_Wall):
                if year >= element.year_online:
                    quay_land_use += element.land_use
            if isinstance(element, Laden_Stack):
                if year >= element.year_online:
                    stack_land_use += element.land_use
            if isinstance(element, Empty_Stack):
                if year >= element.year_online:
                    empty_land_use += element.land_use
            if isinstance(element, OOG_Stack):
                if year >= element.year_online:
                    oog_land_use += element.land_use
            if isinstance(element, Gate):
                if year >= element.year_online:
                    gate_land_use += element.land_use
            if isinstance(element, General_Services):
                if year >= element.year_online:
                    general_land_use += element.land_use

        total_land_use = quay_land_use + stack_land_use + empty_land_use + oog_land_use + gate_land_use + general_land_use

        return total_land_use

    def laden_reefer_stack_capacity(self, year):

        """ Define the stack for laden containers and reefers """
        list_of_elements = self.find_elements(Laden_Stack)
        # find the total stack capacity

        stack_capacity_planned = 0
        stack_capacity_online = 0
        # required_capacity = 0

        for element in list_of_elements:
            stack_capacity_planned += element.capacity
            if year >= element.year_online:
                stack_capacity_online += element.capacity

        laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)

        ts = self.transhipment_ratio

        laden_teu = (laden_teu * ts * 0.5) + (laden_teu * (1 - ts))
        reefer_teu = (reefer_teu * ts * 0.5) + (reefer_teu * (1 - ts))

        laden = Container(**container_defaults.laden_container_data)
        reefer = Container(**container_defaults.reefer_container_data)
        stack = Laden_Stack(**container_defaults.rtg_stack_data)

        # define stack equipment
        if self.laden_stack == 'rtg':
            stack = Laden_Stack(**container_defaults.rtg_stack_data)
        elif self.laden_stack == 'rmg':
            stack = Laden_Stack(**container_defaults.rmg_stack_data)
        elif self.laden_stack == 'sc':
            stack = Laden_Stack(**container_defaults.sc_stack_data)
        elif self.laden_stack == 'rs':
            stack = Laden_Stack(**container_defaults.rs_stack_data)

        operational_days = self.operational_hours // 24

        laden_ground_slots = laden_teu * laden.peak_factor * laden.dwell_time / laden.stack_occupancy / stack.height / operational_days
        reefer_ground_slots = reefer_teu * reefer.peak_factor * reefer.dwell_time / reefer.stack_occupancy / \
                              stack.height / operational_days * stack.reefer_factor
        total_ground_slots = laden_ground_slots + reefer_ground_slots
        reefer_slots = reefer_ground_slots * stack.height

        required_capacity = (laden_ground_slots + reefer_ground_slots) * stack.height
        laden_stack_area = total_ground_slots * stack.area_factor

        return stack_capacity_planned, stack_capacity_online, required_capacity, total_ground_slots, laden_stack_area, reefer_slots

    def empty_stack_capacity(self, year):  # todo beschrijving empty stack

        list_of_elements = self.find_elements(Empty_Stack)
        # find the total stack capacity

        empty_capacity_planned = 0
        empty_capacity_online = 0
        # empty_required_capacity = 0

        for element in list_of_elements:
            empty_capacity_planned += element.capacity
            if year >= element.year_online:
                empty_capacity_online += element.capacity

        ts = self.transhipment_ratio

        laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)

        empty = Container(**container_defaults.empty_container_data)

        stack = Empty_Stack(**container_defaults.empty_stack_data)

        operational_days = self.operational_hours // 24
        empty_teu = (empty_teu * ts * 0.5) + (empty_teu * (1 - ts))
        empty_ground_slots = empty_teu * empty.peak_factor * empty.dwell_time / empty.stack_occupancy / stack.height / operational_days

        empty_required_capacity = empty_ground_slots * stack.height
        empty_stack_area = empty_ground_slots * stack.area_factor

        return empty_capacity_planned, empty_capacity_online, empty_required_capacity, empty_ground_slots, empty_stack_area

    def oog_stack_capacity(self, year):  # todo beschrijving oog stack

        list_of_elements = self.find_elements(OOG_Stack)
        # find the total stack capacity

        oog_capacity_planned = 0
        oog_capacity_online = 0
        # oog_required_capacity = 0

        for element in list_of_elements:
            oog_capacity_planned += element.capacity
            if year >= element.year_online:
                oog_capacity_online += element.capacity
        ts = self.transhipment_ratio

        laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)

        oog_teu = (oog_teu * ts * 0.5) + (oog_teu * (1 - ts))

        oog = Container(**container_defaults.oog_container_data)

        stack = OOG_Stack(**container_defaults.oog_stack_data)

        operational_days = self.operational_hours // 24

        oog_spots = oog_teu * oog.peak_factor * oog.dwell_time / oog.stack_occupancy / stack.height / operational_days / oog.teu_factor

        oog_required_capacity = oog_spots

        return oog_capacity_planned, oog_capacity_online, oog_required_capacity

    def calculate_berth_occupancy(self, year, fully_cellular_calls, panamax_calls, panamax_max_calls,
                                  post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls):
        """
        - Find all cranes and sum their effective_capacity to get service_capacity
        - Divide callsize_per_vessel by service_capacity and add mooring time to get total time at berth
        - Occupancy is total_time_at_berth divided by operational hours
        """

        # list all crane objects in system
        list_of_elements = self.find_elements(Cyclic_Unloader)
        list_of_elements_berth = self.find_elements(Berth)
        nr_berths = len(list_of_elements_berth)

        # list the number of berths online

        # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        service_rate_planned = 0
        service_rate_online = 0
        if list_of_elements != []:
            for element in list_of_elements:
                service_rate_planned += element.effective_capacity
                if year >= element.year_online:
                    service_rate_online += element.effective_capacity

            # estimate berth occupancy
            time_at_berth_fully_cellular_planned = fully_cellular_calls * (
                    (container_defaults.fully_cellular_data["call_size"] / service_rate_planned) + (
                    container_defaults.fully_cellular_data[
                        "mooring_time"] / nr_berths))
            time_at_berth_panamax_planned = panamax_calls * (
                    (container_defaults.panamax_data["call_size"] / service_rate_planned) + (
                    container_defaults.panamax_data[
                        "mooring_time"] / nr_berths))
            time_at_berth_panamax_max_planned = panamax_max_calls * (
                    (container_defaults.panamax_max_data["call_size"] / service_rate_planned) + (
                    container_defaults.panamax_max_data[
                        "mooring_time"] / nr_berths))
            time_at_berth_post_panamax_I_planned = post_panamax_I_calls * (
                    (container_defaults.post_panamax_I_data["call_size"] / service_rate_planned) + (
                    container_defaults.post_panamax_I_data[
                        "mooring_time"] / nr_berths))
            time_at_berth_post_panamax_II_planned = post_panamax_II_calls * (
                    (container_defaults.post_panamax_II_data["call_size"] / service_rate_planned) + (
                    container_defaults.post_panamax_II_data[
                        "mooring_time"] / nr_berths))
            time_at_berth_new_panamax_planned = new_panamax_calls * (
                    (container_defaults.new_panamax_data["call_size"] / service_rate_planned) + (
                    container_defaults.new_panamax_data[
                        "mooring_time"] / nr_berths))
            time_at_berth_VLCS_planned = VLCS_calls * (
                    (container_defaults.VLCS_data["call_size"] / service_rate_planned) + (
                    container_defaults.VLCS_data[
                        "mooring_time"] / nr_berths))
            time_at_berth_ULCS_planned = ULCS_calls * (
                    (container_defaults.ULCS_data["call_size"] / service_rate_planned) + (
                    container_defaults.ULCS_data[
                        "mooring_time"] / nr_berths))

            total_time_at_berth_planned = np.sum(
                [time_at_berth_fully_cellular_planned, time_at_berth_panamax_planned, time_at_berth_panamax_max_planned,
                 time_at_berth_post_panamax_I_planned, time_at_berth_post_panamax_II_planned,
                 time_at_berth_new_panamax_planned,
                 time_at_berth_VLCS_planned, time_at_berth_ULCS_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            berth_occupancy_planned = total_time_at_berth_planned / self.operational_hours

            # estimate crane occupancy
            time_at_crane_fully_cellular_planned = fully_cellular_calls * (
                (container_defaults.fully_cellular_data["call_size"] / service_rate_planned))
            time_at_crane_panamax_planned = panamax_calls * (
                (container_defaults.panamax_data["call_size"] / service_rate_planned))
            time_at_crane_panamax_max_planned = panamax_max_calls * (
                (container_defaults.panamax_max_data["call_size"] / service_rate_planned))
            time_at_crane_post_panamax_I_planned = post_panamax_I_calls * (
                (container_defaults.post_panamax_I_data["call_size"] / service_rate_planned))
            time_at_crane_post_panamax_II_planned = post_panamax_II_calls * (
                (container_defaults.post_panamax_II_data["call_size"] / service_rate_planned))
            time_at_crane_new_panamax_planned = new_panamax_calls * (
                (container_defaults.new_panamax_data["call_size"] / service_rate_planned))
            time_at_crane_VLCS_planned = VLCS_calls * (
                (container_defaults.VLCS_data["call_size"] / service_rate_planned))
            time_at_crane_ULCS_planned = ULCS_calls * (
                (container_defaults.ULCS_data["call_size"] / service_rate_planned))

            total_time_at_crane_planned = np.sum(
                [time_at_crane_fully_cellular_planned, time_at_crane_panamax_planned, time_at_crane_panamax_max_planned,
                 time_at_crane_post_panamax_I_planned, time_at_crane_post_panamax_II_planned,
                 time_at_crane_new_panamax_planned,
                 time_at_crane_VLCS_planned, time_at_crane_ULCS_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            crane_occupancy_planned = total_time_at_crane_planned / self.operational_hours

            if service_rate_online != 0:
                time_at_berth_fully_cellular_online = fully_cellular_calls * (
                        (container_defaults.fully_cellular_data["call_size"] / service_rate_online) +
                        container_defaults.fully_cellular_data[
                            "mooring_time"])
                time_at_berth_panamax_online = panamax_calls * (
                        (container_defaults.panamax_data["call_size"] / service_rate_online) + (
                        container_defaults.panamax_data[
                            "mooring_time"] / nr_berths))
                time_at_berth_panamax_max_online = panamax_max_calls * (
                        (container_defaults.panamax_max_data["call_size"] / service_rate_online) + (
                        container_defaults.panamax_max_data[
                            "mooring_time"] / nr_berths))
                time_at_berth_post_panamax_I_online = post_panamax_I_calls * (
                        (container_defaults.post_panamax_I_data["call_size"] / service_rate_online) + (
                        container_defaults.post_panamax_I_data[
                            "mooring_time"] / nr_berths))
                time_at_berth_post_panamax_II_online = post_panamax_II_calls * (
                        (container_defaults.post_panamax_II_data["call_size"] / service_rate_online) + (
                        container_defaults.post_panamax_II_data[
                            "mooring_time"] / nr_berths))
                time_at_berth_new_panamax_online = new_panamax_calls * (
                        (container_defaults.new_panamax_data["call_size"] / service_rate_online) + (
                        container_defaults.new_panamax_data[
                            "mooring_time"] / nr_berths))
                time_at_berth_VLCS_online = VLCS_calls * (
                        (container_defaults.VLCS_data["call_size"] / service_rate_online) + (
                        container_defaults.VLCS_data[
                            "mooring_time"] / nr_berths))
                time_at_berth_ULCS_online = ULCS_calls * (
                        (container_defaults.ULCS_data["call_size"] / service_rate_online) + (
                        container_defaults.ULCS_data[
                            "mooring_time"] / nr_berths))

                total_time_at_berth_online = np.sum(
                    [time_at_berth_fully_cellular_online, time_at_berth_panamax_online,
                     time_at_berth_panamax_max_online,
                     time_at_berth_post_panamax_I_online, time_at_berth_post_panamax_II_online,
                     time_at_berth_new_panamax_online,
                     time_at_berth_VLCS_online, time_at_berth_ULCS_online])

                # berth_occupancy is the total time at berth divided by the operational hours
                berth_occupancy_online = min([total_time_at_berth_online / self.operational_hours, 1])

                time_at_crane_fully_cellular_online = fully_cellular_calls * (
                    (container_defaults.fully_cellular_data["call_size"] / service_rate_online))
                time_at_crane_panamax_online = panamax_calls * (
                    (container_defaults.panamax_data["call_size"] / service_rate_online))
                time_at_crane_panamax_max_online = panamax_max_calls * (
                    (container_defaults.panamax_max_data["call_size"] / service_rate_online))
                time_at_crane_post_panamax_I_online = post_panamax_I_calls * (
                    (container_defaults.post_panamax_I_data["call_size"] / service_rate_online))
                time_at_crane_post_panamax_II_online = post_panamax_II_calls * (
                    (container_defaults.post_panamax_II_data["call_size"] / service_rate_online))
                time_at_crane_new_panamax_online = new_panamax_calls * (
                    (container_defaults.new_panamax_data["call_size"] / service_rate_online))
                time_at_crane_VLCS_online = VLCS_calls * (
                    (container_defaults.VLCS_data["call_size"] / service_rate_online))
                time_at_crane_ULCS_online = ULCS_calls * (
                    (container_defaults.ULCS_data["call_size"] / service_rate_online))

                total_time_at_crane_online = np.sum(
                    [time_at_crane_fully_cellular_online, time_at_crane_panamax_online,
                     time_at_crane_panamax_max_online,
                     time_at_crane_post_panamax_I_online, time_at_crane_post_panamax_II_online,
                     time_at_crane_new_panamax_online,
                     time_at_crane_VLCS_online, time_at_crane_ULCS_online])

                # berth_occupancy is the total time at berth divided by the operational hours
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

    def calculate_throughput(self, year):
        # list_of_elements = self.find_elements(Cyclic_Unloader)
        # list_of_elements_berth = self.find_elements(Berth)
        #
        # # list the number of berths online
        #
        # # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        # service_rate_planned = 0
        # service_rate_online = 0
        # if list_of_elements != []:
        #     for element in list_of_elements:
        #         service_rate_planned += element.effective_capacity
        #         if year >= element.year_online:
        #             service_rate_online += element.effective_capacity
        #
        # return service_rate_online, service_rate_planned

        # laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)
        # demand = laden_teu + reefer_teu + oog_teu + empty_teu

        commodities = self.find_elements(Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        demand = volume

        # find the total service rate and determine the capacity at the quay
        list_of_elements = self.find_elements(Cyclic_Unloader)
        # list_of_elements_berth = self.find_elements(Berth)
        quay_capacity_planned = 0
        quay_capacity_online = 0

        if list_of_elements != []:
            for element in list_of_elements:
                quay_capacity_planned += (
                        element.effective_capacity * self.operational_hours * self.allowable_berth_occupancy)
                if year >= element.year_online:
                    quay_capacity_online += (
                            element.effective_capacity * self.operational_hours * self.allowable_berth_occupancy)

        # # find the total laden capacity
        # list_of_elements = self.find_elements(Laden_Stack)
        # laden_capacity_planned = 0
        # laden_capacity_online = 0
        # if list_of_elements != []:
        #     for element in list_of_elements:
        #         laden_capacity_planned += element.capacity
        #         if year >= element.year_online:
        #             laden_capacity_online += element.capacity
        #
        # # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        # service_rate_planned = 0
        # service_rate_online = 0
        # # find the total empty capacity
        # list_of_elements = self.find_elements(Empty_Stack)
        # empty_capacity_planned = 0
        # empty_capacity_online = 0
        # if list_of_elements != []:
        #     for element in list_of_elements:
        #         service_rate_planned += element.effective_capacity
        #         empty_capacity_planned += element.capacity
        #         if year >= element.year_online:
        #             service_rate_online += element.effective_capacity
        #             empty_capacity_online += element.capacity
        #
        # # find the oog storage capacity
        # list_of_elements = self.find_elements(OOG_Stack)
        # oog_capacity_planned = 0
        # oog_capacity_online = 0
        # if list_of_elements != []:
        #     for element in list_of_elements:
        #         oog_capacity_planned += element.capacity
        #         if year >= element.year_online:
        #             oog_capacity_online += element.capacity
        #
        # storage_capacity_planned = laden_capacity_planned + empty_capacity_planned + oog_capacity_planned
        # storage_capacity_online = laden_capacity_online + empty_capacity_online + oog_capacity_online

        if quay_capacity_online is not 0:
            throughput_online = min(quay_capacity_online, demand)
        else:
            throughput_online = demand

        return throughput_online

    def calculate_gate_minutes(self, year):  # todo check barge berth

        """
        - Find all gates and sum their effective_capacity to get service_capacity
        - Calculate average entry and exit time to get total time at gate
        - Occupancy is total_minutes_at_gate per hour divided by 1 hour
        """

        # list all gate objects in system
        list_of_elements = self.find_elements(Gate)

        # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        capacity_planned = 0
        capacity_online = 0
        total_design_gate_minutes = 0
        if list_of_elements != []:
            for element in list_of_elements:
                capacity_planned += element.capacity
                if year >= element.year_online:
                    capacity_online += element.capacity

            # estimate time at gate lanes
            """ Get input: import box moves en export box moves, translate to design gate lanes per hour.
            Every gate is 60 minutes, which is the capacity. Dan is het gewoon while totaal is meer dan totale capacity gate toevoegen """

            """ Calculate the total throughput in TEU per year """
            laden_box, reefer_box, empty_box, oog_box, throughput_box = self.throughput_box(year)

            import_box_moves = (throughput_box * (
                    1 - self.transhipment_ratio)) * 0.5  # assume import / export is always 50/50
            export_box_moves = (throughput_box * (
                    1 - self.transhipment_ratio)) * 0.5  # assume import / export is always 50/50
            weeks_year = 52

            gate = Gate(**container_defaults.gate_data)

            design_exit_gate_minutes = import_box_moves * gate.truck_moves / weeks_year * gate.peak_factor * gate.peak_day * gate.peak_hour * \
                                       gate.exit_inspection_time * gate.design_capacity

            design_entry_gate_minutes = export_box_moves * gate.truck_moves / weeks_year * gate.peak_factor * gate.peak_day * gate.peak_hour * \
                                        gate.entry_inspection_time * gate.design_capacity

            total_design_gate_minutes = design_entry_gate_minutes + design_exit_gate_minutes

            service_rate_planend = total_design_gate_minutes / capacity_planned

        else:
            service_rate_planend = float("inf")

        return capacity_planned, capacity_online, service_rate_planend, total_design_gate_minutes

    def waiting_time(self, year):

        """
       - Import the berth occupancy of every year
       - Find the factor for the waiting time with the E2/E2/n queueing theory using 4th order polynomial regression
       - Waiting time is the factor times the crane occupancy
       """

        fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls, post_panamax_II_calls, \
        new_panamax_calls, VLCS_calls, ULCS_calls, total_calls, total_vol = self.calculate_vessel_calls(year)

        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
            self.calculate_berth_occupancy(year, fully_cellular_calls, panamax_calls, panamax_max_calls,
                                           post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, VLCS_calls,
                                           ULCS_calls)

        # find the different factors which are linked to the number of berths
        berths = len(self.find_elements(Berth))

        if berths == 1:
            factor = max(0, 79.726 * berth_occupancy_online ** 4 - 126.47 * berth_occupancy_online ** 3
                         + 70.660 * berth_occupancy_online ** 2 - 14.651 * berth_occupancy_online + 0.9218)
        elif berths == 2:
            factor = max(0, 29.825 * berth_occupancy_online ** 4 - 46.489 * berth_occupancy_online ** 3
                         + 25.656 * berth_occupancy_online ** 2 - 5.3517 * berth_occupancy_online + 0.3376)
        elif berths == 3:
            factor = max(0, 19.362 * berth_occupancy_online ** 4 - 30.388 * berth_occupancy_online ** 3
                         + 16.791 * berth_occupancy_online ** 2 - 3.5457 * berth_occupancy_online + 0.2253)
        elif berths == 4:
            factor = max(0, 17.334 * berth_occupancy_online ** 4 - 27.745 * berth_occupancy_online ** 3
                         + 15.432 * berth_occupancy_online ** 2 - 3.2725 * berth_occupancy_online + 0.2080)
        elif berths == 5:
            factor = max(0, 11.149 * berth_occupancy_online ** 4 - 17.339 * berth_occupancy_online ** 3
                         + 9.4010 * berth_occupancy_online ** 2 - 1.9687 * berth_occupancy_online + 0.1247)
        elif berths == 6:
            factor = max(0, 10.512 * berth_occupancy_online ** 4 - 16.390 * berth_occupancy_online ** 3
                         + 8.8292 * berth_occupancy_online ** 2 - 1.8368 * berth_occupancy_online + 0.1158)
        elif berths == 7:
            factor = max(0, 8.4371 * berth_occupancy_online ** 4 - 13.226 * berth_occupancy_online ** 3
                         + 7.1446 * berth_occupancy_online ** 2 - 1.4902 * berth_occupancy_online + 0.0941)
        else:
            # if there are no berths the occupancy is 'infinite' so a berth is certainly needed
            factor = float("inf")

        waiting_time_hours = factor * crane_occupancy_online * self.operational_hours / total_calls
        waiting_time_occupancy = waiting_time_hours * total_calls / self.operational_hours

        return factor, waiting_time_occupancy

    def check_crane_slot_available(self):
        list_of_elements = self.find_elements(Berth)
        slots = 0
        for element in list_of_elements:
            slots += element.max_cranes

        list_of_elements = self.find_elements(Cyclic_Unloader)

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

    """ Plotting functions """

    def terminal_elements_plot(self, width=0.10, alpha=0.7):
        """ Gather data from Terminal and plot which elements come online when """

        # collect elements to add to plot
        years = []
        berths = []
        cranes = []
        quays = []
        tractor = []
        stack = []
        stack_equipment = []
        gates = []
        empty_stack = []
        oog_stack = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            berths.append(0)
            quays.append(0)
            cranes.append(0)
            tractor.append(0)
            stack.append(0)
            stack_equipment.append(0)
            gates.append(0)
            empty_stack.append(0)
            oog_stack.append(0)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        berths[-1] += 1
                if isinstance(element, Quay_Wall):
                    if year >= element.year_online:
                        quays[-1] += 1
                if isinstance(element, Cyclic_Unloader):
                    if year >= element.year_online:
                        cranes[-1] += 1
                if isinstance(element, Laden_Stack):
                    if year >= element.year_online:
                        stack[-1] += 1
                if isinstance(element, Stack_Equipment):
                    if year >= element.year_online:
                        stack_equipment[-1] += 1
                if isinstance(element, Gate):
                    if year >= element.year_online:
                        gates[-1] += 1
                if isinstance(element, OOG_Stack):
                    if year >= element.year_online:
                        oog_stack[-1] += 1
                if isinstance(element, Empty_Stack):
                    if year >= element.year_online:
                        empty_stack[-1] += 1
                if isinstance(element, Horizontal_Transport):
                    if year >= element.year_online:
                        tractor[-1] += 1

        # scale elements on line
        tractor = [x / 10 for x in tractor]
        stack = [x / 10 for x in stack]
        stack_equipment = [x / 5 for x in stack_equipment]

        # generate plot
        fig, ax = plt.subplots(figsize=(16, 8))

        ax.bar([x + 0 * width for x in years], berths, width=width, alpha=alpha, label="berths")
        ax.bar([x + 1 * width for x in years], quays, width=width, alpha=alpha, label="quays")
        ax.bar([x + 2 * width for x in years], cranes, width=width, alpha=alpha, label="STS cranes")
        ax.bar([x + 3 * width for x in years], tractor, width=width, alpha=alpha, label="tractors (x 10)")
        ax.bar([x + 4 * width for x in years], stack, width=width, alpha=alpha, label="laden stacks (x 10)")
        ax.bar([x + 5 * width for x in years], empty_stack, width=width, alpha=alpha, label="empty stacks")
        ax.bar([x + 6 * width for x in years], oog_stack, width=width, alpha=alpha, label="oog stacks")
        ax.bar([x + 7 * width for x in years], stack_equipment, width=width, alpha=alpha, label="stack equipment (x 5)")
        ax.bar([x + 8 * width for x in years], gates, width=width, alpha=alpha, label="gates")

        ax.set_xlabel('Years')
        ax.set_ylabel('Elements on line [nr]')
        ax.set_title('Terminal elements online')
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='grey', linestyle='--', linewidth=0.5)
        ax.legend()

    def terminal_capacity_plot(self, width=0.25, alpha=0.4):  # todo check storages // edit ships
        """Gather data from Terminal and plot which elements come online when"""

        # get crane service capacity and storage capacity
        years = []
        cranes = []
        cranes_capacity = []
        # storages = []
        # storages_capacity = []

        for year in range(self.startyear, self.startyear + self.lifecycle):

            years.append(year)
            cranes.append(0)
            cranes_capacity.append(0)
            # storages.append(0)
            # storages_capacity.append(0)

            fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls, total_calls, \
            total_vol = self.calculate_vessel_calls(year)

            berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                year, fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls,
                post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls)

            for element in self.elements:
                if isinstance(element, Cyclic_Unloader):
                    # calculate cranes service capacity: effective_capacity * operational hours * berth_occupancy?
                    if year >= element.year_online:
                        cranes[-1] += 1
                        cranes_capacity[
                            -1] += element.effective_capacity * self.operational_hours * crane_occupancy_online
                # if isinstance(element, Storage):
                #     if year >= element.year_online:
                #         storages[-1] += 1
                #         storages_capacity[-1] += element.capacity * 365 / 18

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
        fig, ax = plt.subplots(figsize=(16, 5))

        ax.bar([x - 0.5 * width for x in years], cranes_capacity, width=width, alpha=alpha, label="cranes capacity",
               color='green')
        # ax.bar([x + 0.5 * width for x in years], storages_capacity, width=width, alpha=alpha, label="storages",
        #        color='green')
        ax.step(years, demand['demand'].values, label="demand", where='mid')

        ax.set_xlabel('Years')
        ax.set_ylabel('Throughput capacity [TEU/year]')
        ax.set_title('Terminal capacity online ({})'.format(self.crane_type_defaults['crane_type']))
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def land_use_plot(self, width=0.25, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # get land use
        years = []
        quay_land_use = []
        stack_land_use = []
        empty_land_use = []
        oog_land_use = []
        gate_land_use = []
        general_land_use = []

        for year in range(self.startyear, self.startyear + self.lifecycle):

            years.append(year)
            quay_land_use.append(0)
            stack_land_use.append(0)
            empty_land_use.append(0)
            oog_land_use.append(0)
            gate_land_use.append(0)
            general_land_use.append(0)

            for element in self.elements:
                if isinstance(element, Quay_Wall):
                    if year >= element.year_online:
                        quay_land_use[-1] += element.land_use
                if isinstance(element, Laden_Stack):
                    if year >= element.year_online:
                        stack_land_use[-1] += element.land_use
                if isinstance(element, Empty_Stack):
                    if year >= element.year_online:
                        empty_land_use[-1] += element.land_use
                if isinstance(element, OOG_Stack):
                    if year >= element.year_online:
                        oog_land_use[-1] += element.land_use
                if isinstance(element, Gate):
                    if year >= element.year_online:
                        gate_land_use[-1] += element.land_use
                if isinstance(element, General_Services):
                    if year >= element.year_online:
                        general_land_use[-1] += element.land_use

        quay_land_use = [x * 0.0001 for x in quay_land_use]
        stack_land_use = [x * 0.0001 for x in stack_land_use]
        empty_land_use = [x * 0.0001 for x in empty_land_use]
        oog_land_use = [x * 0.0001 for x in oog_land_use]
        gate_land_use = [x * 0.0001 for x in gate_land_use]
        general_land_use = [x * 0.0001 for x in general_land_use]

        quay_stack = np.add(quay_land_use, stack_land_use).tolist()
        quay_stack_empty = np.add(quay_stack, empty_land_use).tolist()
        quay_stack_empty_oog = np.add(quay_stack_empty, oog_land_use).tolist()
        quay_stack_empty_oog_gate = np.add(quay_stack_empty_oog, gate_land_use).tolist()

        # generate plot
        fig, ax = plt.subplots(figsize=(16, 8))

        ax.bar([x - 0.5 * width for x in years], quay_land_use, width=width, alpha=alpha, label="apron")
        ax.bar([x - 0.5 * width for x in years], stack_land_use, width=width, alpha=alpha,
               label="laden and reefer stack",
               bottom=quay_land_use)
        ax.bar([x - 0.5 * width for x in years], empty_land_use, width=width, alpha=alpha, label="empty stack",
               bottom=quay_stack)
        ax.bar([x - 0.5 * width for x in years], oog_land_use, width=width, alpha=alpha, label="oog stack",
               bottom=quay_stack_empty)
        ax.bar([x - 0.5 * width for x in years], gate_land_use, width=width, alpha=alpha, label="gate area",
               bottom=quay_stack_empty_oog)
        ax.bar([x - 0.5 * width for x in years], general_land_use, width=width, alpha=alpha,
               label="general service area",
               bottom=quay_stack_empty_oog_gate)

        ax.set_xlabel('Years')
        ax.set_ylabel('Land use [ha]')
        ax.set_title('Terminal land use ({})'.format(self.stack_equipment))
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def opex_plot(self, cash_flows):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        "prepare years, revenue, capex and opex for plotting"
        years = cash_flows['year'].values
        insurance = cash_flows['insurance'].values
        maintenance = cash_flows['maintenance'].values
        energy = cash_flows['energy'].values
        labour = cash_flows['labour'].values
        fuel = cash_flows['fuel'].values
        demurrage = cash_flows['demurrage'].values
        overseas_transport = cash_flows['overseas_transport'].values
        print(cash_flows)

        "generate plot"
        fig, ax = plt.subplots(figsize=(16, 6))

        ax.step(years, insurance, label='insurance', where='mid')
        ax.step(years, labour, label='labour', where='mid')
        ax.step(years, fuel, label='fuel', where='mid')
        ax.step(years, energy, label='energy', where='mid')
        ax.step(years, maintenance, label='maintenance', where='mid')
        ax.step(years, demurrage, label='demurrage', where='mid')
        ax.step(years, overseas_transport, label='overseas transport', where='mid')

        ax.set_xlabel('Years')
        ax.set_ylabel('Opex [ M $]')
        ax.set_title('Overview of Opex')
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def cashflow_plot(self, cash_flows, width=0.3, alpha=0.6):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        "prepare NPV"
        # NPV, capex_normal, opex_normal, labour_normal = self.NPV()
        # print(NPV)

        "prepare years, revenue, capex and opex for plotting"
        years = cash_flows['year'].values
        # revenue = self.revenues
        capex = cash_flows['capex'].values
        # opex = cash_flows['insurance'].values + + cash_flows['labour'].values + cash_flows['fuel'].values + cash_flows['energy'].values + cash_flows['maintenance'].values \
        #        + cash_flows['demurrage'].values

        # todo add overseas_transport
        opex = cash_flows['insurance'].values + + cash_flows['labour'].values + cash_flows['fuel'].values + cash_flows['energy'].values + cash_flows['maintenance'].values \
               + cash_flows['demurrage'].values + cash_flows['overseas_transport'].values

        "sum cash flows to get costs as a function of year"
        costs = []
        for year in years:
            costs.append(- cash_flows.loc[cash_flows['year'] == year]['capex'].item()
                         - cash_flows.loc[cash_flows['year'] == year]['insurance'].item()
                         - cash_flows.loc[cash_flows['year'] == year]['maintenance'].item()
                         - cash_flows.loc[cash_flows['year'] == year]['energy'].item()
                         - cash_flows.loc[cash_flows['year'] == year]['labour'].item()
                         - cash_flows.loc[cash_flows['year'] == year]['demurrage'].item()
                         - cash_flows.loc[cash_flows['year'] == year]['overseas_transport'].item())

        "cumulatively sum costs to get costs_cum"
        costs_cum = [None] * len(costs)
        for index, value in enumerate(costs):
            if index == 0:
                costs_cum[index] = 0
            else:
                costs_cum[index] = costs_cum[index - 1] + costs[index]

        "generate plot"
        fig, ax = plt.subplots(figsize=(16, 5))

        ax.bar([x - width for x in years], -opex, width=width, alpha=alpha, label="opex", color='lightblue')
        ax.bar(years, -capex, width=width, alpha=alpha, label="capex", color='green')
        # ax.bar([x + width for x in years], revenue, width=width, alpha=alpha, label="revenue", color='lightgreen')
        ax.step(years, costs, label='costs', where='mid')
        ax.step(years, costs_cum, label='costs_cum', where='mid')
        ax.set_xlabel('Years')
        ax.set_ylabel('Cashflow [1000 M $]')
        ax.set_title('Cash flow plot')
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()
