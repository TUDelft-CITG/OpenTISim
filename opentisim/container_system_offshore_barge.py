# package(s) for data handling
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import babel.numbers
import decimal

# opentisim package
from opentisim.container_objects import *
from opentisim import container_defaults

class System:
    def __init__(self, startyear=2020, lifecycle=20, stack_equipment='rmg', laden_stack='rmg', offshore_onshore_ratio= 5/3,
                 operational_hours=7500, debug=False, elements=None,
                 offshore_distance=40, foreshore_slope=3.0, bathymetry_factor = 0.5, wave_height=3.0, tidal_range = 0.0, reclamation_height = 7.0,
                 barge_type='medium',
                 crane_type_defaults='STS crane', allowable_berth_occupancy=0.7, barge_perc=0.75,
                 laden_perc=0.80, reefer_perc=0.1, empty_perc=0.05, oog_perc=0.05, transhipment_ratio=0.0,
                 energy_price=0.17, fuel_price=1, land_price=0):

        # list of elements
        if elements is None:
            elements = []

        # time inputs
        self.startyear = startyear
        self.lifecycle = lifecycle
        self.operational_hours = operational_hours

        # stack equipment parameters
        self.stack_equipment = stack_equipment
        self.laden_stack = laden_stack
        self.offshore_onshore_ratio = offshore_onshore_ratio

        # provide intermediate outputs via print statements if debug = True
        self.debug = debug

        # collection of all terminal objects
        self.elements = elements

        # default values to use in case various types can be selected
        self.crane_type_defaults = crane_type_defaults
        self.barge_type = barge_type
        self.barge_perc = barge_perc

        # site specific conditions
        self.offshore_distance = offshore_distance
        self.foreshore_slope = foreshore_slope
        self.bathymetry_factor = bathymetry_factor
        self.wave_height = wave_height
        self.tidal_range = tidal_range
        self.reclamation_height = reclamation_height

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
           7. calculate cashflows and aggregate to NPV

        """

        " 1. for each year evaluate the demand of each commodity "
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_demand_commodity(year)

        " 2. for each year evaluate the various investment decisions "
        for year in range(self.startyear, self.startyear + self.lifecycle):
            if self.debug:
                print('')
                print('Offshore Port System - Barge Connection')
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

            # offshore
            self.berth_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
            self.access_channel_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
            self.reclamation_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
            self.revetment_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
            self.breakwater_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
            self.horizontal_transport_invest(year)
            self.laden_stack_invest(year)
            self.empty_stack_invest(year)
            self.oog_stack_invest(year)
            self.total_stack_capacity(year)
            self.stack_equipment_invest(year)
            self.gate_invest(year)
            self.offshore_barge_berth_invest(year)
            self.empty_handler_invest(year)
            self.general_services_invest(year)

            # connection offshore-onshore
            self.barge_invest(year)
            self.barge_channel_invest(year)

            # onshore
            self.onshore_barge_berth_invest(year)

        " 3. for each year calculate the general labour, fuel and energy costs (requires insight in realized demands) "
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_energy_cost(year)
            self.calculate_general_labour_cost(year)
            self.calculate_fuel_cost(year)

        " 4. for each year calculate the demurrage and ocean transport costs (requires insight in realized demands) "
        # self.demurrage = []
        #
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_demurrage_cost(year)

        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_ocean_transport_costs(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)

        " 5.  for each year calculate terminal revenues "
        # self.revenues = []
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_revenue(year)

        " 6. collect all cash flows (capex, opex) (WACC = Weighted average cost of capital) "
        cash_flows_df, cash_flows_WACC_real_df = self.add_cashflow_elements()

        " 7. calculate key numbers "

        # land use
        total_land_use = self.calculate_land_use(year)
        terminal_area = total_land_use

        # channel dimensions
        # ...

        " 8. calculate cashflows and aggregate to NPV "

        island_construction, coastal_protection_construction, structure_maintenance, off_terminal_capex, terminal_opex, capital_dredging, maintenance_dredging, \
            demurrage, barge_capex, barge_opex, cash_flows, cash_flows_df, cash_flows_WACC_real_df, NPV = self.net_present_value()

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
                    element.df.loc[element.df['Year'] == year, 'Energy'] = \
                        element.consumption * sts_moves_per_element * energy_price
            else:
                element.df.loc[element.df['Year'] == year, 'Energy'] = 0

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
                        element.df.loc[element.df['Year'] == year, 'Energy'] = consumption * costs * moves
                else:
                    element.df.loc[element.df['Year'] == year, 'Energy'] = 0

        "Reefer energy costs"
        stack_capacity_planned, stack_capacity_online, required_capacity, stack_ground_slots, laden_stack_area, reefer_slots = self.laden_reefer_stack_capacity(year)

        stacks = 0
        for element in self.elements:
            if isinstance(element, Laden_Stack):
                if year >= element.year_online:
                    stacks += 1

        for element in self.find_elements(Laden_Stack):
            if year >= element.year_online:
                slots_per_stack = reefer_slots / stacks
                if slots_per_stack * element.reefers_present * energy_price * 24 * 365 != np.inf:
                    element.df.loc[element.df['Year'] == year, 'Energy'] = slots_per_stack * element.reefers_present \
                                                                           * energy_price * 24 * 365
            else:
                element.df.loc[element.df['Year'] == year, 'Energy'] = 0

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
                    element.df.loc[element.df['Year'] == year, 'energy'] = lighting + general_consumption
            else:
                element.df.loc[element.df['Year'] == year, 'energy'] = 0

    def calculate_general_labour_cost(self, year):
        """ General labour """

        general = General_Services(**container_defaults.general_services_data)
        laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu = self.throughput_characteristics(year)
        labour = Labour(**container_defaults.labour_data)

        cranes = 0
        for element in self.elements:
            if isinstance(element, Cyclic_Unloader):
                if year >= element.year_online:
                    cranes += 1
        sts_cranes = cranes
        if sts_cranes != 0:
            crew_required = np.ceil(throughput_teu / general.crew_required)

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
                        element.df.loc[element.df['Year'] == year, 'Labour'] = fixed_labour + shift_labour
                else:
                    element.df.loc[element.df['Year'] == year, 'labour'] = 0

    def calculate_fuel_cost(self, year):
        sts_moves, stack_moves, empty_moves, tractor_moves = self.box_moves(year)
        fuel_price = self.fuel_price

        "calculate empty handler fuel costs"
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
                    element.df.loc[element.df['Year'] == year, 'Fuel'] = consumption * costs * moves
            else:
                element.df.loc[element.df['Year'] == year, 'Fuel'] = 0

        "calculate stack equipment fuel costs"
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
                        element.df.loc[element.df['Year'] == year, 'Fuel'] = consumption * costs * moves
                else:
                    element.df.loc[element.df['Year'] == year, 'Fuel'] = 0

        "calculate tractor fuel consumption"
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
                    element.df.loc[element.df['Year'] == year, 'Fuel'] = element.fuel_consumption * moves * fuel_price

            else:
                element.df.loc[element.df['Year'] == year, 'Fuel'] = 0

    def calculate_demurrage_cost(self, year):  # todo check Steph (Hydrogen Terminals)

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

    def calculate_ocean_transport_costs(self, year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS):

        """determine the ocean transport costs"""

        # load the annual throughput
        commodities = self.find_elements(Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass
        throughput = volume

        # gather vessels and calculate the transport costs of each vessel type
        vessels = self.find_elements(Vessel)
        for vessel in vessels:
            if fully_cellular > 0:
                vessel = Vessel(**container_defaults.fully_cellular_data)
                vessel.year_online = year + vessel.starting_time
                vessel.transport_costs = vessel.transport_costs * throughput / 2
            elif panamax > 0:
                vessel = Vessel(**container_defaults.panamax_data)
                vessel.year_online = year + vessel.starting_time
                vessel.transport_costs = vessel.transport_costs * throughput / 2
            elif panamax_max > 0:
                vessel = Vessel(**container_defaults.panamax_max_data)
                vessel.year_online = year + vessel.starting_time
                vessel.transport_costs = vessel.transport_costs * throughput / 2
            elif post_panamax_I > 0:
                vessel = Vessel(**container_defaults.post_panamax_I_data)
                vessel.year_online = year + vessel.starting_time
                vessel.transport_costs = vessel.transport_costs * throughput / 2
            elif post_panamax_II > 0:
                vessel = Vessel(**container_defaults.post_panamax_II_data)
                vessel.year_online = year + vessel.starting_time
                vessel.transport_costs = vessel.transport_costs * throughput / 2
            elif new_panamax > 0:
                vessel = Vessel(**container_defaults.new_panamax_data)
                vessel.year_online = year + vessel.starting_time
                vessel.transport_costs = vessel.transport_costs * throughput / 2
            elif VLCS > 0:
                vessel = Vessel(**container_defaults.VLCS_data)
                vessel.year_online = year + vessel.starting_time
                vessel.transport_costs = vessel.transport_costs * throughput / 2
            elif ULCS > 0:
                vessel = Vessel(**container_defaults.ULCS_data)
                vessel.year_online = year + vessel.starting_time
                vessel.transport_costs = vessel.transport_costs * throughput / 2

        # for vessel in vessels:
        #     if fully_cellular > 0:
        #         vessel = Vessel(**container_defaults.fully_cellular_data)
        #         vessel.year_online = year + vessel.starting_time
        #         vessel.transport_costs = vessel.avg_transport_costs * throughput / 2
        #     elif panamax > 0:
        #         vessel = Vessel(**container_defaults.panamax_data)
        #         vessel.year_online = year + vessel.starting_time
        #         vessel.transport_costs = vessel.avg_transport_costs * throughput / 2
        #     elif panamax_max > 0:
        #         vessel = Vessel(**container_defaults.panamax_max_data)
        #         vessel.year_online = year + vessel.starting_time
        #         vessel.transport_costs = vessel.avg_transport_costs * throughput / 2
        #     elif post_panamax_I > 0:
        #         vessel = Vessel(**container_defaults.post_panamax_I_data)
        #         vessel.year_online = year + vessel.starting_time
        #         vessel.transport_costs = vessel.avg_transport_costs * throughput / 2
        #     elif post_panamax_II > 0:
        #         vessel = Vessel(**container_defaults.post_panamax_II_data)
        #         vessel.year_online = year + vessel.starting_time
        #         vessel.transport_costs = vessel.avg_transport_costs * throughput / 2
        #     elif new_panamax > 0:
        #         vessel = Vessel(**container_defaults.new_panamax_data)
        #         vessel.year_online = year + vessel.starting_time
        #         vessel.transport_costs = vessel.avg_transport_costs * throughput / 2
        #     elif VLCS > 0:
        #         vessel = Vessel(**container_defaults.VLCS_data)
        #         vessel.year_online = year + vessel.starting_time
        #         vessel.transport_costs = vessel.avg_transport_costs * throughput / 2
        #     elif ULCS > 0:
        #         vessel = Vessel(**container_defaults.ULCS_data)
        #         vessel.year_online = year + vessel.starting_time
        #         vessel.transport_costs = vessel.avg_transport_costs * throughput / 2

        container_ship_costs = np.sum(vessel.transport_costs)

        list_of_elements_Vessel = self.find_elements(Vessel)

        # calibration
        print("container_ship_costs", f'{int(container_ship_costs):,}', "USD")

        return container_ship_costs

    """ Offshore Terminal investment functions """

    def berth_invest(self, year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS):

        """ Current strategy is to add berth if the berth_occupancy > allowable_berth_occupancy:
            - allowable_berth_occupancy is specified at System: def__init__()
            - a berth needs: i) a quay and ii) cranes (min: 1 and max: max_cranes)
            - berth occupancy depends on: i) total_calls and total_vol and ii) total_service_capacity as delivered by the cranes
            - adding cranes decreases berth_occupancy_rate """

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

        # factor, waiting_time_occupancy = self.waiting_time(year)

        if self.debug:
            print('     Berth occupancy planned (@ start of year): {}'.format(round(berth_occupancy_planned, 3)))
            print('     Berth occupancy online  (@ start of year): {}'.format(round(berth_occupancy_online, 3)))
            print('     Crane occupancy planned (@ start of year): {}'.format(round(crane_occupancy_planned, 3)))
            print('     Crane occupancy online  (@ start of year): {}'.format(round(crane_occupancy_online, 3)))
            # print('     Waiting time factor     (@ start of year): {}'.format(round(factor, 3)))
            # print('     Waiting time occupancy  (@ start of year): {}'.format(round(waiting_time_occupancy, 3)))
            print('')

        # if the planned berth occupancy is higher than the allowable berth occupancy, add a berth when no crane slots are available
        while berth_occupancy_planned > self.allowable_berth_occupancy:
            if not (self.check_crane_slot_available()):
                if self.debug:
                    print('  *** add Berth to elements')
                berth = Berth(**container_defaults.berth_data)
                berth.year_online = year + berth.delivery_time
                self.elements.append(berth)

                # berth occupancy after adding a berth
                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)

                if self.debug:
                    print('     Berth occupancy planned (after adding Berth): {}'.format(round(berth_occupancy_planned, 3)))
                    print('     Berth occupancy online  (after adding Berth): {}'.format(round(berth_occupancy_online, 3)))
                    print('')

            # check if a quay is needed
            berths = len(self.find_elements(Berth))
            quay_walls = len(self.find_elements(Quay_Wall))

            print('*** nr of berths:', berths)

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
                if quay_walls == 0:
                    quay_length = length_v + 2 * 15
                elif quay_walls == 1:
                    quay_length = 1.1 * berths * (length_v + 15) - (length_v + 2 * 15)
                else:
                    quay_length = 1.1 * berths * (length_v + 15) - 1.1 * (berths - 1) * (length_v + 15)

                # quay wall depth
                quay_wall = Quay_Wall(**container_defaults.quay_wall_data)
                quay_depth = np.sum([draught, self.tidal_range, quay_wall.max_sinkage, quay_wall.wave_motion, quay_wall.safety_margin])

                # calibration
                print("quay_length_in_func", f'{int(quay_length):,}', "m")
                print("quay_depth", f'{int(quay_depth):,}', "m")

                self.quay_invest(year, quay_length, quay_depth)

                # berth occupancy after adding a quay
                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
                if self.debug:
                    print('     Berth occupancy planned (after adding Quay): {}'.format(round(berth_occupancy_planned, 3)))
                    print('     Berth occupancy online  (after adding Quay): {}'.format(round(berth_occupancy_online, 3)))
                    print('')

            # check if a crane is needed
            if self.check_crane_slot_available():
                self.crane_invest(year)

                # berth occupancy after adding a Crane
                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                    year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)

                if self.debug:
                    print('     Berth occupancy planned (after adding Crane): {}'.format(round(berth_occupancy_planned, 3)))
                    print('     Berth occupancy online  (after adding Crane): {}'.format(round(berth_occupancy_online, 3)))
                    print('')

    def quay_invest(self, year, quay_length, quay_depth):

        """ Current strategy is to add quay as quay_per_berth < 1
            - adding quay will increase quay_per_berth
            - quay_wall.quay_length must be long enough to accommodate largest expected vessel
            - quay_wall.quay_depth must be deep enough to accommodate largest expected vessel
            - quay_wall.freeboard must be high enough to accommodate largest expected vessel"""

        if self.debug:
            print('  *** add Quay to elements')

        # add a Quay_Wall element
        quay_wall = Quay_Wall(**container_defaults.quay_wall_data)

        # capex
        unit_rate = int(quay_wall.Gijt_constant * (quay_depth * 2 + quay_wall.freeboard) ** quay_wall.Gijt_coefficient)  # todo check haakjes, staat anders in rapport Wijnand
        mobilisation = int(max((quay_length * unit_rate * quay_wall.mobilisation_perc), quay_wall.mobilisation_min))
        apron_pavement = quay_length * quay_wall.apron_width * quay_wall.apron_pavement
        cost_of_land = quay_length * quay_wall.apron_width * self.land_price
        quay_wall.off_terminal_capex = int(quay_length * unit_rate + mobilisation + apron_pavement + cost_of_land)

        # opex
        quay_wall.insurance = unit_rate * quay_length * quay_wall.insurance_perc
        quay_wall.maintenance = unit_rate * quay_length * quay_wall.maintenance_perc
        quay_wall.year_online = year + quay_wall.delivery_time

        # land use
        quay_wall.land_use = quay_length * quay_wall.apron_width

        # add cash flow information to quay_wall object in a DataFrame
        quay_wall = self.add_cashflow_data_to_element(quay_wall)

        self.elements.append(quay_wall)

    def offshore_barge_berth_invest(self, year):

        """ Current strategy is to add barge berths as soon as trigger is achieved
            - find out how much barge berths capacity is online
            - find out how much barge berths capacity is planned
            - find out how much barge berths capacity is needed
            - add barge berths capacity until service_trigger is no longer exceeded"""

        # # report on the status of all berth elements
        # print("")
        # print("Report barge berths/quays/cranes:")
        # self.report_element(Offshore_Barge_Berth, year)
        # self.report_element(Offshore_Barge_Quay_Wall, year)
        # self.report_element(Offshore_Barge_Crane, year)

        barge_berth_capacity_planned, barge_berth_capacity_online, service_rate_planned, design_barge_berth_capacity, \
            nom_crane_productivity, net_crane_productivity, net_berth_productivity = self.calculate_offshore_barge_berth(year)

        if self.debug:
            print('')
            print('     Offshore barge berth capacity planned     (@ start of year): {} [TEU/yr]'.format(round(barge_berth_capacity_planned, -1)))
            print('     Offshore barge berth capacity online      (@ start of year): {} [TEU/yr]'.format(round(barge_berth_capacity_online, -1)))
            print('     Offshore barge berth service rate planned (@ start of year): {} [-]'.format(round(service_rate_planned, 3)))
            print('     Offshore barge berth capacity required    (@ start of year): {} [TEU/yr]'.format(round(design_barge_berth_capacity, -1)))
            print('')

        while service_rate_planned > 1:
            if self.debug:
                print('  *** add Offshore Barge Berth to elements')

            offshore_barge_berth = Offshore_Barge_Berth(**container_defaults.barge_berth_data)
            offshore_barge_berth.year_online = year + offshore_barge_berth.delivery_time
            self.elements.append(offshore_barge_berth)

            # barge berth capacity after adding a barge berth
            barge_berth_capacity_planned, barge_berth_capacity_online, service_rate_planned, design_barge_berth_capacity, \
                nom_crane_productivity, net_crane_productivity, net_berth_productivity = self.calculate_offshore_barge_berth(year)

            if self.debug:
                print('     Offshore barge berth capacity planned (after adding Berth): {}'.format(round(barge_berth_capacity_planned, -1)), "TEU")
                print('     Offshore barge berth capacity online  (after adding Berth): {}'.format(round(barge_berth_capacity_online, -1)), "TEU")
                print('')

            # check if a quay is needed
            offshore_barge_berths = len(self.find_elements(Offshore_Barge_Berth))
            offshore_barge_quay_walls = len(self.find_elements(Offshore_Barge_Quay_Wall))

            print('*** nr of offshore barge berths:', offshore_barge_berths)
            print('*** nr of offshore barge quays: ', offshore_barge_quay_walls)

            if offshore_barge_berths > offshore_barge_quay_walls:
                length_barge = max(container_defaults.small_barge_data["LOA"],
                                   container_defaults.medium_barge_data["LOA"],
                                   container_defaults.large_barge_data["LOA"])
                draught = max(container_defaults.small_barge_data["draught"],
                              container_defaults.medium_barge_data["draught"],
                              container_defaults.large_barge_data["draught"])

                # barge quay length
                if offshore_barge_quay_walls == 0:
                    barge_quay_length = length_barge + 2 * 15
                elif offshore_barge_quay_walls == 1:
                    barge_quay_length = 1.1 * offshore_barge_berths * (length_barge + 15) - (length_barge + 2 * 15)
                else:
                    barge_quay_length = 1.1 * offshore_barge_berths * (length_barge + 15) - 1.1 * (offshore_barge_berths - 1) * (length_barge + 15)

                # barge quay wall depth (same defaults as Quay_Wall)
                quay_wall = Offshore_Barge_Quay_Wall(**container_defaults.quay_wall_data)
                barge_quay_depth = np.sum([draught, self.tidal_range, quay_wall.max_sinkage, quay_wall.wave_motion, quay_wall.safety_margin])

                # # calibration
                # print("barge_quay_length_in_func", f'{int(barge_quay_length):,}', "m")
                # print("barge_quay_depth", f'{int(barge_quay_depth):,}', "m")

                self.offshore_barge_quay_invest(year, barge_quay_length, barge_quay_depth)

                # barge berth capacity after adding a quay
                barge_berth_capacity_planned, barge_berth_capacity_online, service_rate_planned, design_barge_berth_capacity, \
                    nom_crane_productivity, net_crane_productivity, net_berth_productivity = self.calculate_offshore_barge_berth(year)

                if self.debug:
                    print('     Offshore barge berth capacity planned     (@ start of year): {} [TEU/yr]'.format(round(barge_berth_capacity_planned, 3)))
                    print('     Offshore barge berth capacity online      (@ start of year): {} [TEU/yr]'.format(round(barge_berth_capacity_online, 3)))
                    print('     Offshore barge berth service rate planned (@ start of year): {} [-]'.format(round(service_rate_planned, 3)))
                    print('     Offshore barge berth capacity required    (@ start of year): {} [TEU/yr]'.format(round(design_barge_berth_capacity, 3)))
                    print('')

        # calibration
        print("")
        print("Calibration Offshore Barge Berth")
        print("nom_crane_productivity", f'{round(nom_crane_productivity, 1):,}', "TEU/hr")
        print("net_crane_productivity", f'{round(net_crane_productivity, 1):,}', "TEU/hr")
        print("net_berth_productivity", f'{round(net_berth_productivity, 0):,}', "TEU/yr")
        print("")

    def offshore_barge_quay_invest(self, year, barge_quay_length, barge_quay_depth):

        """ Current strategy is to add quay as quay_per_berth < 1
            - adding quay will increase quay_per_berth
            - quay_wall.quay_length must be long enough to accommodate largest expected vessel
            - quay_wall.quay_depth must be deep enough to accommodate largest expected vessel
            - quay_wall.freeboard must be high enough to accommodate largest expected vessel"""

        if self.debug:
            print('  *** add Offshore Barge Quay to elements')

        # add a Quay_Wall element
        offshore_barge_quay_wall = Offshore_Barge_Quay_Wall(**container_defaults.quay_wall_data)

        # capex
        unit_rate = int(
            offshore_barge_quay_wall.Gijt_constant * (barge_quay_depth * 2 + offshore_barge_quay_wall.freeboard) ** offshore_barge_quay_wall.Gijt_coefficient)  # todo check haakjes, staat anders in rapport Wijnand
        mobilisation = int(max((barge_quay_length * unit_rate * offshore_barge_quay_wall.mobilisation_perc), offshore_barge_quay_wall.mobilisation_min))
        apron_pavement = barge_quay_length * offshore_barge_quay_wall.apron_width * offshore_barge_quay_wall.apron_pavement
        cost_of_land = barge_quay_length * offshore_barge_quay_wall.apron_width * self.land_price
        offshore_barge_quay_wall.off_terminal_capex = int(barge_quay_length * unit_rate + mobilisation + apron_pavement + cost_of_land)

        # opex
        offshore_barge_quay_wall.insurance = unit_rate * barge_quay_length * offshore_barge_quay_wall.insurance_perc
        offshore_barge_quay_wall.maintenance = unit_rate * barge_quay_length * offshore_barge_quay_wall.maintenance_perc
        offshore_barge_quay_wall.year_online = year + offshore_barge_quay_wall.delivery_time

        # land use
        offshore_barge_quay_wall.land_use = barge_quay_length * offshore_barge_quay_wall.apron_width

        # add cash flow information to quay_wall object in a DataFrame
        offshore_barge_quay_wall = self.add_cashflow_data_to_element(offshore_barge_quay_wall)

        self.elements.append(offshore_barge_quay_wall)

    def access_channel_invest(self, year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS):

        """ Current strategy is to ...."""  # todo add access channel invest

        vessels = self.find_elements(Vessel)
        for vessel in vessels:
            if fully_cellular > 0:
                vessel = Vessel(**container_defaults.fully_cellular_data)
                length = vessel.LOA
                draught = vessel.draught
                beam = vessel.beam
            elif panamax > 0:
                vessel = Vessel(**container_defaults.panamax_data)
                length = vessel.LOA
                draught = vessel.draught
                beam = vessel.beam
            elif panamax_max > 0:
                vessel = Vessel(**container_defaults.panamax_max_data)
                length = vessel.LOA
                draught = vessel.draught
                beam = vessel.beam
            elif post_panamax_I > 0:
                vessel = Vessel(**container_defaults.post_panamax_I_data)
                length = vessel.LOA
                draught = vessel.draught
                beam = vessel.beam
            elif post_panamax_II > 0:
                vessel = Vessel(**container_defaults.post_panamax_II_data)
                length = vessel.LOA
                draught = vessel.draught
                beam = vessel.beam
            elif new_panamax > 0:
                vessel = Vessel(**container_defaults.new_panamax_data)
                length = vessel.LOA
                draught = vessel.draught
                beam = vessel.beam
            elif VLCS > 0:
                vessel = Vessel(**container_defaults.VLCS_data)
                length = vessel.LOA
                draught = vessel.draught
                beam = vessel.beam
            elif ULCS > 0:
                vessel = Vessel(**container_defaults.ULCS_data)
                length = vessel.LOA
                draught = vessel.draught
                beam = vessel.beam

        # calibration
        print("length", length)
        print("draught", draught)
        print("beam", beam)

        # quay_length = self.berth_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
        quay_length = 1000
        print("quay_length", quay_length)

        access_channels = len(self.find_elements(Channel))

        if access_channels == 0:

            if self.debug:
                print('  *** add Access Channel to elements')

            # add an Access_Channel object
            access_channel = Channel(**container_defaults.channel_data)

            # dimensions access channel (According to PIANC 2014 for moderate conditions)
            width_standard = beam * 1.5
            width_cross_wind = beam * 0.4
            width_cross_current = beam * 0.7
            width_long_current = beam * 0.1
            width_wave_height = beam * 0.5
            width_aids_navigation = beam * 0.2
            width_bottom_surface = beam * 0.1
            width_depth_waterway = beam * 0.1
            width_bank_clearance = beam * 0.5
            width_passing = beam * 1.6
            channel_width = 2 * (width_standard + width_cross_wind + width_cross_current + width_long_current + width_wave_height +
                                 width_aids_navigation + width_bottom_surface + width_depth_waterway + width_bank_clearance) + width_passing


            wave_height = self.wave_height
            tidal_window = 0.0
            max_sinkage = 1.0
            wave_response = wave_height / 2
            net_underkeel_clearance = 0.5
            channel_depth = draught - tidal_window + max_sinkage + wave_response + net_underkeel_clearance

            offshore_distance = self.offshore_distance * 10**3
            channel_length_max = self.foreshore_slope * 10**3 * channel_depth
            channel_length = max(0, channel_length_max - offshore_distance)

            excavation_depth = max(0,(channel_length_max - offshore_distance) / (self.foreshore_slope * 10**3))

            channel_volume = self.bathymetry_factor * channel_width * excavation_depth * channel_length

            # dimensions turning circle
            turning_circle_diameter = length * 1.8  # Source: RHDHV
            turning_circle_volume = 1/4 * np.pi * turning_circle_diameter**2 * excavation_depth

            # dimensions berth pocket
            berth_pocket_width = beam * 2.0  # Source: RHDHV
            berth_pocket_volume = berth_pocket_width * excavation_depth * quay_length

            # total
            dredging_volume = channel_volume + turning_circle_volume + berth_pocket_volume

            # capex
            capital_dredging_rate = access_channel.capital_dredging_rate
            infill_dredging_rate = access_channel.infill_dredging_rate
            access_channel.capital_dredging = int((capital_dredging_rate + infill_dredging_rate) * dredging_volume)

            # opex
            maintenance_dredging_rate = access_channel.maintenance_dredging_rate
            access_channel.maintenance_dredging = maintenance_dredging_rate * dredging_volume * access_channel.maintenance_perc
            access_channel.year_online = year + access_channel.delivery_time

            # calibration
            print("channel_width", f'{int(channel_width):,}',"m")
            print("channel_depth", f'{int(channel_depth):,}', "m")
            print("channel_length", f'{int(channel_length):,}', "m")
            print("channel_volume", f'{int(round(channel_volume,-6)):,}', "m3")
            print("turning_circle_diameter", f'{int(turning_circle_diameter):,}', "m3")
            print("turning_circle_volume", f'{int(round(turning_circle_volume,-6)):,}', "m3")
            print("berth_pocket_width", f'{int(berth_pocket_width):,}', "m")
            print("berth_pocket_volume", f'{int(round(berth_pocket_volume,-6)):,}', "m3")
            print("dredging_volume", f'{int(round(dredging_volume,-6)):,}', "m3")
            print("")
            print("channel_length_max", f'{int(channel_length_max):,}', "m")
            print("excavation_depth", f'{int(excavation_depth):,}', "m")

            # add cash flow information to quay_wall object in a DataFrame
            access_channel = self.add_cashflow_data_to_element(access_channel)

            self.elements.append(access_channel)

            return channel_width, channel_depth, channel_length, channel_volume, turning_circle_volume, berth_pocket_volume, dredging_volume

    def reclamation_invest(self, year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS):

        """ Current strategy is to ...."""  # todo add strategy

        # quay_length = self.berth_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
        quay_length = 1000

        print("quay_length",quay_length)

        terminal_width = 50

        reclamations = len(self.find_elements(Reclamation))

        if reclamations == 0:

            if self.debug:
                print('  *** add Reclamation to elements')

            # add an Reclamation object
            reclamation = Reclamation(**container_defaults.reclamation_data)

            # dimensions island reclamation
            reclamation_length = quay_length       # meters
            reclamation_width = terminal_width     # meters
            reclamation_depth = 18                 # meters
            reclamation_area = reclamation_length * reclamation_width
            reclamation_volume = reclamation_area * reclamation_depth

            # capex
            reclamation_rate = reclamation.reclamation_rate * 10    # todo check
            reclamation.island_construction = int(reclamation_rate  * reclamation_volume)

            # opex
            reclamation_maintenance_rate = reclamation.reclamation_rate * reclamation.maintenance_perc
            reclamation.structure_maintenance = reclamation_maintenance_rate * reclamation_volume * reclamation.maintenance_perc
            reclamation.year_online = year + reclamation.delivery_time

            # calibration
            print("")
            print("Calibration Reclamation")
            print("reclamation_length", f'{int(round(reclamation_length,-1)):,}', "m")
            print("reclamation_width",  f'{int(round(reclamation_width, -1)):,}', "m")
            print("reclamation_area",   f'{int(round(reclamation_area,  -3)):,}', "m2")
            print("reclamation_volume", f'{int(round(reclamation_volume,-3)):,}', "m3")

            # add cash flow information to quay_wall object in a DataFrame
            reclamation = self.add_cashflow_data_to_element(reclamation)

            self.elements.append(reclamation)

            return reclamation_area, reclamation_volume

    def revetment_invest(self, year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS):

        """ Current strategy is to ...."""  # todo add strategy

        # quay_length = self.berth_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
        quay_length = 1000

        revetments = len(self.find_elements(Revetment))

        if revetments == 0:

            if self.debug:
                print('  *** add Revetment to elements')

            # add an Reclamation object
            revetment = Revetment(**container_defaults.revetment_data)

            # dimensions revetment
            revetment_length = quay_length * revetment.quay_length_rate  # meters

            # capex
            revetment_rate = revetment.revetment_rate
            revetment.coastal_protection_construction = int(revetment_rate * revetment_length)

            # opex
            revetment_maintenance_rate = revetment.revetment_rate * revetment.maintenance_perc
            revetment.coastal_protection_maintenance = int(revetment.coastal_protection_construction * revetment.maintenance_perc)
            revetment.year_online = year + revetment.delivery_time

            # calibration
            print("")
            print("Calibration Revetment")
            print("revetment_length", f'{int(round(revetment_length, -1)):,}', "m")

            # add cash flow information to quay_wall object in a DataFrame
            revetment = self.add_cashflow_data_to_element(revetment)

            self.elements.append(revetment)

            return revetment_length

    def breakwater_invest(self, year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS):

        """ Current strategy is to ...."""  # todo add strategy

        # quay_length = self.berth_invest(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax, VLCS, ULCS)
        quay_length = 1000

        breakwaters = len(self.find_elements(Breakwater))

        if breakwaters == 0:

            if self.debug:
                print('  *** add Breakwater to elements')

            # add an Reclamation object
            breakwater = Breakwater(**container_defaults.breakwater_data)

            # dimensions breakwater
            breakwater_length = quay_length * breakwater.quay_length_rate  # meters

            # capex
            breakwater_rate = breakwater.breakwater_rate
            breakwater.coastal_protection_construction = int(breakwater_rate * breakwater_length)

            # opex
            breakwater_maintenance_rate = breakwater.breakwater_rate * breakwater.maintenance_perc
            breakwater.structure_maintenance = int(breakwater.coastal_protection_construction * breakwater.maintenance_perc)
            breakwater.year_online = year + breakwater.delivery_time

            # calibration
            print("")
            print("Calibration Breakwater")
            print("breakwater_length", f'{int(round(breakwater_length, -1)):,}', "m")

            # add cash flow information to quay_wall object in a DataFrame
            breakwater = self.add_cashflow_data_to_element(breakwater)

            self.elements.append(breakwater)

            return breakwater_length

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

        # capex
        unit_rate = crane.unit_rate
        mobilisation = unit_rate * crane.mobilisation_perc
        crane.off_terminal_capex = int(unit_rate + mobilisation)

        # opex
        crane.insurance = unit_rate * crane.insurance_perc
        crane.maintenance = unit_rate * crane.maintenance_perc

        # labour
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
            print('     Horizontal Transport online (@ start of year): {}'.format(tractor_online))
            print('     Number of STS cranes        (@ start of year): {}'.format(sts_cranes))
            print('')

        if self.stack_equipment != 'sc':

            while sts_cranes > (tractor_online // tractor.required):
                # add a tractor when not enough to serve number of STS cranes
                if self.debug:
                    print('  *** add Tractor to elements')

                tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)

                # capex
                unit_rate = tractor.unit_rate
                mobilisation = tractor.mobilisation
                tractor.off_terminal_capex = int(unit_rate + mobilisation)

                # opex
                tractor.maintenance = unit_rate * tractor.maintenance_perc

                # labour
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
            print('     Empty Handlers online (@ start of year): {}'.format(empty_handler_online))
            print('')

        while sts_cranes > (empty_handler_online // empty_handler.required):

            # add a tractor when not enough to serve number of STS cranes
            if self.debug:
                print('  *** add Tractor to elements')

            # capex
            unit_rate = empty_handler.unit_rate
            mobilisation = empty_handler.mobilisation
            empty_handler.off_terminal_capex = int(unit_rate + mobilisation)

            # opex
            empty_handler.maintenance = unit_rate * empty_handler.maintenance_perc

            # labour
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

        stack_capacity_planned, stack_capacity_online, required_capacity, stack_ground_slots, laden_stack_area, reefer_slots = self.laden_reefer_stack_capacity(year)

        if self.debug:
            print('     Stack Capacity planned  (@ start of year): {}'.format(round(stack_capacity_planned)))
            print('     Stack Capacity online   (@ start of year): {}'.format(round(stack_capacity_online)))
            print('     Stack Capacity required (@ start of year): {}'.format(round(required_capacity)))
            print('     Laden and Reefer Ground Slots required (@ start of year): {}'.format(round(stack_ground_slots)))
            print('')

        while required_capacity > stack_capacity_planned:
            if self.debug:
                print('  *** add Laden Stack to elements')

            if self.laden_stack == 'rtg':
                stack = Laden_Stack(**container_defaults.rtg_stack_data)
            elif self.laden_stack == 'rmg':
                stack = Laden_Stack(**container_defaults.rmg_stack_data)
            elif self.laden_stack == 'sc':
                stack = Laden_Stack(**container_defaults.sc_stack_data)
            elif self.laden_stack == 'rs':
                stack = Laden_Stack(**container_defaults.rs_stack_data)

            reefer_slots = (self.reefer_perc / self.laden_perc) * stack.capacity

            # land use
            stack_ground_slots = stack.capacity / stack.height
            stack.storage_area = stack_ground_slots * stack.gross_tgs
            stack.land_use = stack.storage_area * stack.area_factor

            # capex
            area = stack.length * stack.width
            gross_tgs = stack.gross_tgs
            pavement = stack.pavement
            drainage = stack.drainage
            area_factor = stack.area_factor
            reefer_rack = reefer_slots * stack.reefer_rack
            mobilisation = stack.mobilisation
            cost_of_land = self.land_price
            stack.off_terminal_capex = int((pavement + drainage + cost_of_land) * gross_tgs * area * area_factor + mobilisation + reefer_rack)

            # opex
            stack.maintenance = int((pavement + drainage) * gross_tgs * area * area_factor * stack.maintenance_perc)

            if year == self.startyear:
                stack.year_online = year + stack.delivery_time + 1
            else:
                stack.year_online = year + stack.delivery_time

            # add cash flow information to quay_wall object in a DataFrame
            stack = self.add_cashflow_data_to_element(stack)

            self.elements.append(stack)

            stack_capacity_planned, stack_capacity_online, required_capacity, stack_ground_slots, laden_stack_area, reefer_slots = self.laden_reefer_stack_capacity(year)

    def empty_stack_invest(self, year):

        """ Current strategy is to add stacks as soon as trigger is achieved
            - find out how much stack capacity is online
            - find out how much stack capacity is planned
            - find out how much stack capacity is needed
            - add stack capacity until service_trigger is no longer exceeded"""

        empty_capacity_planned, empty_capacity_online, empty_required_capacity, empty_ground_slots, empty_stack_area = self.empty_stack_capacity(year)

        if self.debug:
            print('     Empty Stack capacity planned  (@ start of year): {}'.format(round(empty_capacity_planned)))
            print('     Empty Stack capacity online   (@ start of year): {}'.format(round(empty_capacity_online)))
            print('     Empty Stack capacity required (@ start of year): {}'.format(round(empty_required_capacity)))
            print('     Empty Ground Slots required   (@ start of year): {}'.format(round(empty_ground_slots)))
            print('')

        while empty_required_capacity > empty_capacity_planned:
            if self.debug:
                print('  *** add Empty Stack to elements')

            empty_stack = Empty_Stack(**container_defaults.empty_stack_data)

            # land use
            stack_ground_slots = empty_stack.capacity / empty_stack.height
            empty_stack.storage_area = stack_ground_slots * empty_stack.gross_tgs
            empty_stack.land_use = empty_stack.storage_area * empty_stack.area_factor

            # capex
            area = empty_stack.length * empty_stack.width
            gross_tgs = empty_stack.gross_tgs
            pavement = empty_stack.pavement
            drainage = empty_stack.drainage
            area_factor = empty_stack.area_factor
            mobilisation = empty_stack.mobilisation
            cost_of_land = self.land_price
            empty_stack.off_terminal_capex = int(
                (pavement + drainage + cost_of_land) * gross_tgs * area * area_factor + mobilisation)

            # opex
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
            print('     OOG Slots planned  (@ start of year): {}'.format(round(oog_capacity_planned)))
            print('     OOG Slots online   (@ start of year): {}'.format(round(oog_capacity_online)))
            print('     OOG Slots required (@ start of year): {}'.format(round(oog_required_capacity)))
            print('')

        while oog_required_capacity > oog_capacity_planned:
            if self.debug:
                print('  *** add OOG stack to elements')

            oog_stack = OOG_Stack(**container_defaults.oog_stack_data)

            # capex
            area = oog_stack.length * oog_stack.width
            gross_tgs = oog_stack.gross_tgs
            pavement = oog_stack.pavement
            drainage = oog_stack.drainage
            area_factor = oog_stack.area_factor
            mobilisation = oog_stack.mobilisation
            cost_of_land = self.land_price
            oog_stack.off_terminal_capex = int((pavement + drainage + cost_of_land) * gross_tgs * area * area_factor + mobilisation)

            # opex
            oog_stack.maintenance = int((pavement + drainage) * gross_tgs * area * area_factor * oog_stack.maintenance_perc)

            # land use
            stack_ground_slots = oog_stack.capacity / oog_stack.height
            oog_stack.storage_area = stack_ground_slots * oog_stack.gross_tgs
            oog_stack.land_use = oog_stack.storage_area * oog_stack.area_factor

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
            print('     Number of stack Equipment online (@ start of year): {}'.format(round(stack_equipment_online)))
            print('')

        if (self.stack_equipment == 'rtg' or
                self.stack_equipment == 'sc' or
                self.stack_equipment == 'rs'):
            while sts_cranes > (stack_equipment_online // stack_equipment.required):

                # add stack equipment when not enough to serve number of STS cranes
                if self.debug:
                    print('  *** add Stack Equipment to elements')

                # capex
                unit_rate = stack_equipment.unit_rate
                mobilisation = stack_equipment.mobilisation
                stack_equipment.off_terminal_capex = int(unit_rate + mobilisation)

                # opex# todo calculate moves for energy costs
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
                    print('  *** add Stack Equipment to elements')

                # capex
                unit_rate = stack_equipment.unit_rate
                mobilisation = stack_equipment.mobilisation
                stack_equipment.off_terminal_capex = int(unit_rate + mobilisation)

                # opex  todo calculate moves for energy costs
                stack_equipment.insurance = unit_rate * stack_equipment.insurance_perc
                stack_equipment.maintenance = unit_rate * stack_equipment.maintenance_perc

                # labour
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

    def gate_invest(self, year):

        """ Current strategy is to add gates as soon as trigger is achieved
            - find out how much gate capacity is online
            - find out how much gate capacity is planned
            - find out how much gate capacity is needed
            - add gate capacity until service_trigger is no longer exceeded"""

        gate_capacity_planned, gate_capacity_online, service_rate_planned, total_design_gate_minutes = self.calculate_gate_minutes(year)

        if self.debug:
            print('     Gate capacity planned     (@ start of year): {}'.format(round(gate_capacity_planned)))
            print('     Gate capacity online      (@ start of year): {}'.format(round(gate_capacity_online)))
            print('     Gate service rate planned (@ start of year): {}'.format(round(service_rate_planned, 3)))
            print('     Gate lane minutes         (@ start of year): {}'.format(round(total_design_gate_minutes)))
            print('')

        while service_rate_planned > 1:
            if self.debug:
                print('  *** add Gate to elements')

            gate = Gate(**container_defaults.gate_data)

            tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)

            # land use
            gate.land_use = gate.area

            # capex
            unit_rate = gate.unit_rate
            mobilisation = gate.mobilisation
            canopy = gate.canopy_costs * gate.area  # overkapping
            cost_of_land = self.land_price
            gate.off_terminal_capex = int(unit_rate + mobilisation + canopy + (cost_of_land * gate.area))

            # opex
            gate.maintenance = unit_rate * gate.maintenance_perc

            # labour
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

    def general_services_invest(self, year):

        laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu = self.throughput_characteristics(year)
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
                print('  *** add General Services to elements')

            # land use
            general.land_use = general.office + general.workshop + general.scanning_inspection_area \
                               + general.repair_building

            # capex
            area = general.office + general.workshop + general.scanning_inspection_area + general.repair_building
            cost_of_land = self.land_price
            office = general.office * general.office_cost
            workshop = general.workshop * general.workshop_cost
            inspection = general.scanning_inspection_area * general.scanning_inspection_area_cost
            light = general.lighting_mast_cost * (total_land_use / general.lighting_mast_required)
            repair = general.repair_building * general.repair_building_cost
            basic = general.fuel_station_cost + general.firefight_cost + general.maintenance_tools_cost + general.terminal_operating_software_cost + general.electrical_station_cost
            general.off_terminal_capex = office + workshop + inspection + light + repair + basic + (area * cost_of_land)

            # opex
            general.maintenance = general.off_terminal_capex * general.general_maintenance

            if year == self.startyear:
                general.year_online = year + general.delivery_time
            else:
                general.year_online = year + general.delivery_time

            # add cash flow information to tractor object in a DataFrame
            general = self.add_cashflow_data_to_element(general)

            self.elements.append(general)

    """ Onshore Terminal investment functions """

    def onshore_barge_berth_invest(self, year):

        """ Current strategy is to add barge berths as soon as trigger is achieved
            - find out how much barge berths capacity is online
            - find out how much barge berths capacity is planned
            - find out how much barge berths capacity is needed
            - add barge berths capacity until service_trigger is no longer exceeded"""

        barge_berth_capacity_planned, barge_berth_capacity_online, service_rate_planned, design_barge_berth_capacity, \
            nom_crane_productivity, net_crane_productivity, net_berth_productivity = self.calculate_onshore_barge_berth(year)

        if self.debug:
            print('')
            print('     Onshore barge berth capacity planned     (@ start of year): {} [TEU/yr]'.format(round(barge_berth_capacity_planned, -1)))
            print('     Onshore barge berth capacity online      (@ start of year): {} [TEU/yr]'.format(round(barge_berth_capacity_online, -1)))
            print('     Onshore barge berth service rate planned (@ start of year): {} [-]'.format(round(service_rate_planned, 3)))
            print('     Onshore barge berth capacity required    (@ start of year): {} [TEU/yr]'.format(round(design_barge_berth_capacity, -1)))
            print('')

        while service_rate_planned > 1:
            if self.debug:
                print('  *** add Onshore Barge Berth to elements')

            onshore_barge_berth = Onshore_Barge_Berth(**container_defaults.barge_berth_data)
            onshore_barge_berth.year_online = year + onshore_barge_berth.delivery_time
            self.elements.append(onshore_barge_berth)

            # barge berth capacity after adding a barge berth
            barge_berth_capacity_planned, barge_berth_capacity_online, service_rate_planned, design_barge_berth_capacity, \
                nom_crane_productivity, net_crane_productivity, net_berth_productivity = self.calculate_onshore_barge_berth(year)

            if self.debug:
                print('     Onshore barge berth capacity planned (after adding Berth): {}'.format(round(barge_berth_capacity_planned, -1)), "TEU")
                print('     Onshore barge berth capacity online  (after adding Berth): {}'.format(round(barge_berth_capacity_online, -1)), "TEU")
                print('')

            # check if a quay is needed
            onshore_barge_berths = len(self.find_elements(Onshore_Barge_Berth))
            onshore_barge_quay_walls = len(self.find_elements(Onshore_Barge_Quay_Wall))

            print('*** nr of onshore barge berths:', onshore_barge_berths)

            if onshore_barge_berths > onshore_barge_quay_walls:
                length_barge = max(container_defaults.small_barge_data["LOA"],
                                   container_defaults.medium_barge_data["LOA"],
                                   container_defaults.large_barge_data["LOA"])
                draught = max(container_defaults.small_barge_data["draught"],
                              container_defaults.medium_barge_data["draught"],
                              container_defaults.large_barge_data["draught"])

                # barge quay length
                if onshore_barge_quay_walls == 0:
                    barge_quay_length = length_barge + 2 * 15
                elif onshore_barge_quay_walls == 1:
                    barge_quay_length = 1.1 * onshore_barge_berths * (length_barge + 15) - (length_barge + 2 * 15)
                else:
                    barge_quay_length = 1.1 * onshore_barge_berths * (length_barge + 15) - 1.1 * (onshore_barge_berths - 1) * (length_barge + 15)

                # barge quay wall depth (same defaults as Quay_Wall)
                quay_wall = Onshore_Barge_Quay_Wall(**container_defaults.quay_wall_data)
                barge_quay_depth = np.sum([draught, self.tidal_range, quay_wall.max_sinkage, quay_wall.wave_motion, quay_wall.safety_margin])

                # # calibration
                # print("barge_quay_length_in_func", f'{int(barge_quay_length):,}', "m")
                # print("barge_quay_depth", f'{int(barge_quay_depth):,}', "m")

                self.onshore_barge_quay_invest(year, barge_quay_length, barge_quay_depth)

                # barge berth capacity after adding a quay
                barge_berth_capacity_planned, barge_berth_capacity_online, service_rate_planned, design_barge_berth_capacity, \
                    nom_crane_productivity, net_crane_productivity, net_berth_productivity = self.calculate_onshore_barge_berth(year)

                if self.debug:
                    print('     Onshore barge berth capacity planned     (@ start of year): {} [TEU/yr]'.format(round(barge_berth_capacity_planned, 3)))
                    print('     Onshore barge berth capacity online      (@ start of year): {} [TEU/yr]'.format(round(barge_berth_capacity_online, 3)))
                    print('     Onshore barge berth service rate planned (@ start of year): {} [-]'.format(round(service_rate_planned, 3)))
                    print('     Onshore barge berth capacity required    (@ start of year): {} [TEU/yr]'.format(round(design_barge_berth_capacity, 3)))
                    print('')

        print("onshore berth service rate planned", service_rate_planned)

        # calibration
        print("")
        print("Calibration Onshore Barge Berth")
        print("nom_crane_productivity", f'{round(nom_crane_productivity, 1):,}', "TEU/hr")
        print("net_crane_productivity", f'{round(net_crane_productivity, 1):,}', "TEU/hr")
        print("net_berth_productivity", f'{round(net_berth_productivity, 0):,}', "TEU/yr")
        print("")

    def onshore_barge_quay_invest(self, year, barge_quay_length, barge_quay_depth):

        """ Current strategy is to add quay as quay_per_berth < 1
            - adding quay will increase quay_per_berth
            - quay_wall.quay_length must be long enough to accommodate largest expected vessel
            - quay_wall.quay_depth must be deep enough to accommodate largest expected vessel
            - quay_wall.freeboard must be high enough to accommodate largest expected vessel"""

        if self.debug:
            print('  *** add Onshore Barge Quay to elements')

        # add a Onshore Barge Quay Wall element
        onshore_barge_quay_wall = Onshore_Barge_Quay_Wall(**container_defaults.quay_wall_data)

        # capex
        unit_rate = int(
            onshore_barge_quay_wall.Gijt_constant * (barge_quay_depth * 2 + onshore_barge_quay_wall.freeboard) ** onshore_barge_quay_wall.Gijt_coefficient)  # todo check haakjes, staat anders in rapport Wijnand
        mobilisation = int(max((barge_quay_length * unit_rate * onshore_barge_quay_wall.mobilisation_perc), onshore_barge_quay_wall.mobilisation_min))
        apron_pavement = barge_quay_length * onshore_barge_quay_wall.apron_width * onshore_barge_quay_wall.apron_pavement
        cost_of_land = barge_quay_length * onshore_barge_quay_wall.apron_width * self.land_price
        onshore_barge_quay_wall.off_terminal_capex = int(barge_quay_length * unit_rate + mobilisation + apron_pavement + cost_of_land)

        # opex
        onshore_barge_quay_wall.insurance = unit_rate * barge_quay_length * onshore_barge_quay_wall.insurance_perc
        onshore_barge_quay_wall.maintenance = unit_rate * barge_quay_length * onshore_barge_quay_wall.maintenance_perc
        onshore_barge_quay_wall.year_online = year + onshore_barge_quay_wall.delivery_time

        # land use
        onshore_barge_quay_wall.land_use = barge_quay_length * onshore_barge_quay_wall.apron_width

        # add cash flow information to quay_wall object in a DataFrame
        onshore_barge_quay_wall = self.add_cashflow_data_to_element(onshore_barge_quay_wall)

        self.elements.append(onshore_barge_quay_wall)

    """ Terminal connection investment functions """

    def barge_invest(self, year):

        """ Current strategy is to ...."""  # todo add barge invest

        barge_capacity_planned, barge_capacity_online, required_barge_capacity = self.calculate_barge_capacity(year)

        if self.debug:
            print('     Barge Capacity planned  (@ start of year): {}'.format(round(barge_capacity_planned)))
            print('     Barge Capacity online   (@ start of year): {}'.format(round(barge_capacity_online)))
            print('     Barge Capacity required (@ start of year): {}'.format(round(required_barge_capacity)))
            print('')

        while required_barge_capacity > barge_capacity_planned:  # todo check
            if self.debug:
                print('  *** add Barge to elements')

            # add a Barge object
            if self.barge_type == 'Small_Barge':
                barge = Barge(**container_defaults.small_barge_data)
            elif self.barge_type == 'Medium_Barge':
                barge = Barge(**container_defaults.medium_barge_data)
            elif self.barge_type == 'Large_Barge':
                barge = Barge(**container_defaults.large_barge_data)

            barge = Barge(**container_defaults.medium_barge_data)

            trips = 150  # todo edit
            barge_capacity = barge.call_size * trips
            required_nr_barges = int(required_barge_capacity / barge_capacity)

            barges_online = len(self.find_elements(Barge))

            # capex
            unit_rate = barge.unit_rate
            nr_barges = barges_online
            barge.barge_capex = int(nr_barges * unit_rate)

            # opex
            barge.barge_opex = barge.barge_capex * barge.operations_perc

            if year == self.startyear:
                barge.year_online = year + barge.delivery_time + 1
            else:
                barge.year_online = year + barge.delivery_time

            # add cash flow information to barge object in a DataFrame
            barge = self.add_cashflow_data_to_element(barge)

            self.elements.append(barge)

            list_of_elements_barge = self.find_elements(Barge)
            barges_online = len(list_of_elements_barge)
            print("barges_online", barges_online)

            barge_capacity_planned, barge_capacity_online, required_barge_capacity = self.calculate_barge_capacity(year)

    def barge_channel_invest(self, year):

        """ Current strategy is to ...."""  # todo add access channel invest

        barges = self.find_elements(Barge)

        for barge in barges:
            if barge.type == 'small':
                length = barge.LOA
                draught = barge.draught
                beam = barge.beam
            elif barge.type == 'medium':
                length = barge.LOA
                draught = barge.draught
                beam = barge.beam
            elif barge.type == 'large':
                length = barge.LOA
                draught = barge.draught
                beam = barge.beam

        # calibration
        print("length", length)
        print("draught", draught)
        print("beam", beam)

        barge_channels = len(self.find_elements(Barge_Channel))

        if barge_channels == 0:

            if self.debug:
                print('  *** add Barge Channel to elements')

            # add an Access_Channel object
            barge_channel = Barge_Channel(**container_defaults.channel_data)

            # dimensions barge channel (According to PIANC 2014 for moderate conditions)
            width_standard = beam * 1.5
            width_cross_wind = beam * 0.4
            width_cross_current = beam * 0.7
            width_long_current = beam * 0.1
            width_wave_height = beam * 0.5
            width_aids_navigation = beam * 0.2
            width_bottom_surface = beam * 0.1
            width_depth_waterway = beam * 0.1
            width_bank_clearance = beam * 0.5
            width_passing = beam * 1.6
            barge_channel_width = 2 * (width_standard + width_cross_wind + width_cross_current + width_long_current + width_wave_height +
                                   width_aids_navigation + width_bottom_surface + width_depth_waterway + width_bank_clearance) + width_passing

            wave_height = self.wave_height
            tidal_window = 0.0
            max_sinkage = 1.0
            wave_response = wave_height / 2
            net_underkeel_clearance = 0.5
            barge_channel_depth = draught - tidal_window + max_sinkage + wave_response + net_underkeel_clearance

            barge_channel_length = self.foreshore_slope * 10**3 * barge_channel_depth

            barge_channel_volume = 1/2 * barge_channel_width * barge_channel_depth * barge_channel_length

            # dimensions turning circle
            barge_turning_circle_diameter = length * 1.8  # Source: RHDHV
            barge_turning_circle_depth = barge_channel_depth
            barge_turning_circle_volume = 1/4 * np.pi * barge_turning_circle_diameter**2 * barge_turning_circle_depth

            # dimensions berth pocket
            barge_quay_length =  1130.0  # todo edit
            barge_berth_pocket_width = beam * 2.0  # Source: RHDHV
            barge_berth_pocket_depth = barge_channel_depth
            barge_berth_pocket_volume = barge_berth_pocket_width * barge_berth_pocket_depth * barge_quay_length

            # total
            barge_dredging_volume = barge_channel_volume + barge_turning_circle_volume + barge_berth_pocket_volume

            # capex
            capital_dredging_rate = barge_channel.capital_dredging_rate
            infill_dredging_rate = barge_channel.infill_dredging_rate
            barge_channel.capital_dredging = int((capital_dredging_rate + infill_dredging_rate) * barge_dredging_volume)

            # opex
            maintenance_dredging_rate = barge_channel.maintenance_dredging_rate
            barge_channel.maintenance_dredging = maintenance_dredging_rate * barge_dredging_volume * barge_channel.maintenance_perc
            barge_channel.year_online = year + barge_channel.delivery_time

            # calibration
            print("")
            print("Calibration Barge Channel")
            print("barge_channel_width", f'{int(barge_channel_width):,}',"m")
            print("barge_channel_depth", f'{int(barge_channel_depth):,}', "m")
            print("barge_channel_length", f'{int(barge_channel_length):,}', "m")
            print("barge_channel_volume", f'{int(barge_channel_volume):,}', "m3")
            print("barge_turning_circle_diameter", f'{int(barge_turning_circle_diameter):,}', "m")
            print("barge_turning_circle_volume", f'{int(barge_turning_circle_volume):,}', "m3")
            print("barge_berth_pocket_width", f'{int(barge_berth_pocket_width):,}', "m")
            print("barge_berth_pocket_volume", f'{int(barge_berth_pocket_volume):,}', "m3")
            print("barge_dredging_volume", f'{int(barge_dredging_volume):,}', "m3")

            # add cash flow information to quay_wall object in a DataFrame
            barge_channel = self.add_cashflow_data_to_element(barge_channel)

            self.elements.append(barge_channel)

            return barge_channel_width, barge_channel_depth, barge_channel_length, barge_channel_volume, barge_turning_circle_volume, barge_berth_pocket_volume, barge_dredging_volume

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
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()  # The total amount of annualy transported TEU
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

    def calculate_barge_capacity(self, year):

        """ Define the barges """
        list_of_elements = self.find_elements(Barge)

        # find the total barge capacity
        barge_capacity_planned = 0
        barge_capacity_online = 0

        trips = 150  # todo edit

        for element in list_of_elements:
            barge_capacity_planned += element.call_size * trips
            if year >= element.year_online:
                barge_capacity_online += element.call_size * trips

        laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu = self.throughput_characteristics(year)

        transhipment_ratio = self.transhipment_ratio
        barge_perc = self.barge_perc

        onshore_barge_throughput = (throughput_teu * transhipment_ratio * 0.5) + (throughput_teu * (1 - transhipment_ratio)) * barge_perc
        offshore_barge_throughput = (throughput_teu * transhipment_ratio * 0.5) + (throughput_teu * (1 - transhipment_ratio))

        required_barge_capacity = onshore_barge_throughput

        return barge_capacity_planned, barge_capacity_online, required_barge_capacity

    def throughput_characteristics(self, year):

        """ Calculate the total throughput in TEU per year
        - Find all commodities and the modal split
        - Translate the total TEU/year to every container type throughput
        """

        commodities = self.find_elements(Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        laden_teu = volume * self.laden_perc
        reefer_teu = volume * self.reefer_perc
        empty_teu = volume * self.empty_perc
        oog_teu = volume * self.oog_perc

        throughput_teu = laden_teu + reefer_teu + empty_teu + oog_teu

        return laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu

    def throughput_box(self, year):

        """ Calculate the total throughput in containers per year
        - Find all commodities and the modal split
        - Translate the total containers/year to every container type throughput
        """

        laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu = self.throughput_characteristics(year)

        laden = Container(**container_defaults.laden_container_data)
        reefer = Container(**container_defaults.reefer_container_data)
        empty = Container(**container_defaults.empty_container_data)
        oog = Container(**container_defaults.oog_container_data)

        laden_box = round(laden_teu / laden.teu_factor)
        reefer_box = round(reefer_teu / reefer.teu_factor)
        empty_box = round(empty_teu / empty.teu_factor)
        oog_box = round(oog_teu / oog.teu_factor)

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
        tractor_moves = round(throughput_box * tractor.non_essential_moves)

        # calculate the number of empty moves
        empty = Empty_Stack(**container_defaults.empty_stack_data)
        empty_moves = round(empty_box * empty.household * empty.digout)   # nr. of empty box moves

        # calculate laden and reefer stack moves
        if self.laden_stack == 'rtg':
            stack = Laden_Stack(**container_defaults.rtg_stack_data)
        elif self.laden_stack == 'rmg':
            stack = Laden_Stack(**container_defaults.rmg_stack_data)
        elif self.laden_stack == 'sc':
            stack = Laden_Stack(**container_defaults.sc_stack_data)
        elif self.laden_stack == 'rs':
            stack = Laden_Stack(**container_defaults.rs_stack_data)

        digout_moves = (stack.height - 1) / 2  # source: JvBeemen

        # The number of moves per laden box moves differs for import and export (i/e) and for transhipment (ts)
        moves_i_e = ((2 + stack.household + digout_moves) + ((2 + stack.household) * stack.digout_margin)) / 2
        moves_ts = 0.5 * ((2 + stack.household) * stack.digout_margin)

        laden_reefer_box_ts = (laden_box + reefer_box) * self.transhipment_ratio
        laden_reefer_box_i_e = (laden_box + reefer_box) - laden_reefer_box_ts

        laden_reefer_moves_ts = laden_reefer_box_ts * moves_ts
        laden_reefer_moves_i_e = laden_reefer_box_i_e * moves_i_e

        stack_moves = laden_reefer_moves_i_e + laden_reefer_moves_ts

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

        laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu = self.throughput_characteristics(year)

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
        reefer_ground_slots = (reefer_teu * reefer.peak_factor * reefer.dwell_time / reefer.stack_occupancy /
                               stack.height / operational_days * stack.reefer_factor)
        stack_ground_slots = laden_ground_slots + reefer_ground_slots
        reefer_slots = reefer_ground_slots * stack.height

        required_capacity = (laden_ground_slots + reefer_ground_slots) * stack.height
        laden_stack_area = stack_ground_slots * stack.area_factor

        return stack_capacity_planned, stack_capacity_online, required_capacity, stack_ground_slots, laden_stack_area, reefer_slots

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

        laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu = self.throughput_characteristics(year)

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

        laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu = self.throughput_characteristics(year)

        oog_teu = (oog_teu * ts * 0.5) + (oog_teu * (1 - ts))

        oog = Container(**container_defaults.oog_container_data)

        stack = OOG_Stack(**container_defaults.oog_stack_data)

        operational_days = self.operational_hours // 24

        oog_spots = oog_teu * oog.peak_factor * oog.dwell_time / oog.stack_occupancy / stack.height / operational_days / oog.teu_factor

        oog_required_capacity = oog_spots

        return oog_capacity_planned, oog_capacity_online, oog_required_capacity

    def total_stack_capacity(self, year):
        stack_capacity_planned, stack_capacity_online, stack_required_capacity, stack_ground_slots, laden_stack_area, reefer_slots = self.laden_reefer_stack_capacity(year)
        empty_capacity_planned, empty_capacity_online, empty_required_capacity, empty_ground_slots, empty_stack_area = self.empty_stack_capacity(year)
        oog_capacity_planned, oog_capacity_online, oog_required_capacity = self.oog_stack_capacity(year)

        total_ground_slots = stack_ground_slots + empty_ground_slots
        total_required_capacity = stack_required_capacity + empty_required_capacity + oog_required_capacity

        # calibration
        print('     Total Ground Slots required (@ start of year): ', f'{int(total_ground_slots):,}', "TEU")
        print('     Total Stack capacity required (@ start of year): ', f'{int(total_required_capacity):,}', "TEU" )
        print('')

        return total_ground_slots, total_required_capacity

    def calculate_berth_occupancy(self, year, fully_cellular_calls, panamax_calls, panamax_max_calls,
                                  post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls):
        """
        - Find all cranes and sum their effective_capacity to get service_capacity
        - Divide callsize_per_vessel by service_capacity and add mooring time to get total time at berth
        - Occupancy is total_time_at_berth divided by operational hours
        """

        # list all crane objects in system
        list_of_elements_cranes = self.find_elements(Cyclic_Unloader)

        # list the number of berths online
        list_of_elements_berths = self.find_elements(Berth)
        nr_berths = len(list_of_elements_berths)

        # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        service_rate_planned = 0
        service_rate_online = 0
        if list_of_elements_cranes != []:
            for element in list_of_elements_cranes:
                service_rate_planned += element.effective_capacity  # TEU/hr
                if year >= element.year_online:
                    service_rate_online += element.effective_capacity

            "estimate berth occupancy"
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
            # print('Post Panamax II, time at berth', round(time_at_berth_post_panamax_II_planned), 'hr')

            time_at_berth_new_panamax_planned = new_panamax_calls * (
                    (container_defaults.new_panamax_data["call_size"] / service_rate_planned) + (
                    container_defaults.new_panamax_data[
                        "mooring_time"] / nr_berths))
            # print('New Panamax, time at berth', round(time_at_berth_new_panamax_planned), 'hr')

            time_at_berth_VLCS_planned = VLCS_calls * (
                    (container_defaults.VLCS_data["call_size"] / service_rate_planned) + (
                    container_defaults.VLCS_data[
                        "mooring_time"] / nr_berths))

            time_at_berth_ULCS_planned = ULCS_calls * (
                    (container_defaults.ULCS_data["call_size"] / service_rate_planned) + (
                    container_defaults.ULCS_data[
                        "mooring_time"] / nr_berths))

            total_time_at_berth_planned = round(np.sum(
                [time_at_berth_fully_cellular_planned,
                 time_at_berth_panamax_planned,
                 time_at_berth_panamax_max_planned,
                 time_at_berth_post_panamax_I_planned,
                 time_at_berth_post_panamax_II_planned,
                 time_at_berth_new_panamax_planned,
                 time_at_berth_VLCS_planned,
                 time_at_berth_ULCS_planned]))
            # print('   > Total time at berth (planned) is', total_time_at_berth_planned, 'h /', self.operational_hours, 'oh')

            "berth_occupancy is the total time at berth divided by the operational hours"
            berth_occupancy_planned = total_time_at_berth_planned / self.operational_hours
            # print('Berth occupancy planned', round(berth_occupancy_planned *100 ,2), '%')

            "estimate crane occupancy"
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

            total_time_at_crane_planned = round(np.sum(
                [time_at_crane_fully_cellular_planned, time_at_crane_panamax_planned, time_at_crane_panamax_max_planned,
                 time_at_crane_post_panamax_I_planned, time_at_crane_post_panamax_II_planned,
                 time_at_crane_new_panamax_planned,
                 time_at_crane_VLCS_planned, time_at_crane_ULCS_planned]))
            # print('total time at crane planned: ', total_time_at_crane_planned)

            "berth_occupancy is the total time at berth divided by the operational hours"
            crane_occupancy_planned = total_time_at_crane_planned / self.operational_hours

            if service_rate_online != 0:
                time_at_berth_fully_cellular_online = fully_cellular_calls * (
                        (container_defaults.fully_cellular_data["call_size"] / service_rate_online) +
                        container_defaults.fully_cellular_data["mooring_time"])
                time_at_berth_panamax_online = panamax_calls * (
                        (container_defaults.panamax_data["call_size"] / service_rate_online) + (
                        container_defaults.panamax_data["mooring_time"] / nr_berths))
                time_at_berth_panamax_max_online = panamax_max_calls * (
                        (container_defaults.panamax_max_data["call_size"] / service_rate_online) + (
                        container_defaults.panamax_max_data["mooring_time"] / nr_berths))
                time_at_berth_post_panamax_I_online = post_panamax_I_calls * (
                        (container_defaults.post_panamax_I_data["call_size"] / service_rate_online) + (
                        container_defaults.post_panamax_I_data["mooring_time"] / nr_berths))
                time_at_berth_post_panamax_II_online = post_panamax_II_calls * (
                        (container_defaults.post_panamax_II_data["call_size"] / service_rate_online) + (
                        container_defaults.post_panamax_II_data["mooring_time"] / nr_berths))
                time_at_berth_new_panamax_online = new_panamax_calls * (
                        (container_defaults.new_panamax_data["call_size"] / service_rate_online) + (
                        container_defaults.new_panamax_data["mooring_time"] / nr_berths))
                time_at_berth_VLCS_online = VLCS_calls * (
                        (container_defaults.VLCS_data["call_size"] / service_rate_online) + (
                        container_defaults.VLCS_data["mooring_time"] / nr_berths))
                time_at_berth_ULCS_online = ULCS_calls * (
                        (container_defaults.ULCS_data["call_size"] / service_rate_online) + (
                        container_defaults.ULCS_data["mooring_time"] / nr_berths))

                total_time_at_berth_online = round(np.sum(
                    [time_at_berth_fully_cellular_online,
                     time_at_berth_panamax_online,
                     time_at_berth_panamax_max_online,
                     time_at_berth_post_panamax_I_online,
                     time_at_berth_post_panamax_II_online,
                     time_at_berth_new_panamax_online,
                     time_at_berth_VLCS_online,
                     time_at_berth_ULCS_online]))
                # print('   > Total time at berth (online) is', total_time_at_berth_online, 'h /', self.operational_hours, 'oh')

                "berth_occupancy is the total time at berth divided by the operational hours"
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

                "berth_occupancy is the total time at berth divided by the operational hours"
                crane_occupancy_online = min([total_time_at_crane_online / self.operational_hours, 1])

            else:
                berth_occupancy_online = float("inf")
                crane_occupancy_online = float("inf")

        else:
            "if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed"
            berth_occupancy_planned = float("inf")
            berth_occupancy_online  = float("inf")
            crane_occupancy_planned = float("inf")
            crane_occupancy_online  = float("inf")

        return berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online

    def calculate_throughput(self, year):

        commodities = self.find_elements(Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        demand = volume

        "find the total service rate and determine the capacity at the quay"
        list_of_elements_cranes = self.find_elements(Cyclic_Unloader)
        list_of_elements_berths = self.find_elements(Berth)
        quay_capacity_planned = 0
        quay_capacity_online = 0

        if list_of_elements_cranes != []:
            for element in list_of_elements_cranes:
                quay_capacity_planned += (element.effective_capacity * self.operational_hours * self.allowable_berth_occupancy)

                if year >= element.year_online:
                    quay_capacity_online += (element.effective_capacity * self.operational_hours * self.allowable_berth_occupancy)

        print('   > Quay capacity planned', int(quay_capacity_planned), 'TEU per year')

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

        print('   > Throughput online', int(throughput_online), 'TEU per year')

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
            """ Get input: import box moves and export box moves, translate to design gate lanes per hour.
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

            service_rate_planned = total_design_gate_minutes / capacity_planned

        else:
            service_rate_planned = float("inf")

        return capacity_planned, capacity_online, service_rate_planned, total_design_gate_minutes

    def calculate_offshore_barge_berth(self, year):

        """
        - Find all berths and sum their effective_capacity to get service_capacity
        - Calculate average entry and exit time to get total time at gate
        - Occupancy is total_minutes_at_gate per hour divided by 1 hour
        """

        # load teu factor
        laden = Container(**container_defaults.laden_container_data)
        teu_factor = laden.teu_factor

        # determine the berth productivity
        offshore_barge_berth = Offshore_Barge_Berth(**container_defaults.barge_berth_data)

        nom_crane_productivity = offshore_barge_berth.nom_crane_productivity                                                    # in moves per hour
        nom_crane_productivity = nom_crane_productivity * teu_factor                                                            # in TEU per hour
        net_crane_productivity = nom_crane_productivity * offshore_barge_berth.utilisation * offshore_barge_berth.efficiency    # in TEU per hour

        net_berth_productivity = net_crane_productivity * offshore_barge_berth.crane_per_berth                                  # in TEU per hour
        net_berth_productivity = net_berth_productivity * self.operational_hours * offshore_barge_berth.handling_time_ratio + offshore_barge_berth.peak_factor  # in TEU per year

        # list all gate objects in system
        list_of_elements = self.find_elements(Offshore_Barge_Berth)

        # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        capacity_planned = 0
        capacity_online = 0
        capacity_required = 0
        if list_of_elements != []:
            for element in list_of_elements:
                capacity_planned += net_berth_productivity
                if year >= element.year_online:
                    capacity_online += net_berth_productivity

            """ Calculate the total throughput in TEU per year """
            laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu = self.throughput_characteristics(year)

            capacity_required = throughput_teu

            service_rate_planned = capacity_required / capacity_planned

        else:
            service_rate_planned = float("inf")

        return capacity_planned, capacity_online, service_rate_planned, capacity_required, nom_crane_productivity, net_crane_productivity, net_berth_productivity

    def calculate_onshore_barge_berth(self, year):

        """
        - Find all berths and sum their effective_capacity to get service_capacity
        - Calculate average entry and exit time to get total time at gate
        - Occupancy is total_minutes_at_gate per hour divided by 1 hour
        """

        # load teu factor
        laden = Container(**container_defaults.laden_container_data)
        teu_factor = laden.teu_factor

        # determine the berth productivity
        onshore_barge_berth = Onshore_Barge_Berth(**container_defaults.barge_berth_data)

        nom_crane_productivity = onshore_barge_berth.nom_crane_productivity                                                   # in moves per hour
        nom_crane_productivity = nom_crane_productivity * teu_factor                                                          # in TEU per hour
        net_crane_productivity = nom_crane_productivity * onshore_barge_berth.utilisation * onshore_barge_berth.efficiency    # in TEU per hour

        net_berth_productivity = net_crane_productivity * onshore_barge_berth.crane_per_berth                                 # in TEU per hour
        net_berth_productivity = net_berth_productivity * self.operational_hours * onshore_barge_berth.handling_time_ratio + onshore_barge_berth.peak_factor  # in TEU per year

        # list all gate objects in system
        list_of_elements = self.find_elements(Onshore_Barge_Berth)
        # print("nr_onshore_barge_berths", len(list_of_elements))

        # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        capacity_planned = 0
        capacity_online = 0
        capacity_required = 0
        if list_of_elements != []:
            for element in list_of_elements:
                capacity_planned += net_berth_productivity
                if year >= element.year_online:
                    capacity_online += net_berth_productivity

            """ Calculate the total throughput in TEU per year """
            laden_teu, reefer_teu, empty_teu, oog_teu, throughput_teu = self.throughput_characteristics(year)

            capacity_required = throughput_teu * self.barge_perc

            service_rate_planned = capacity_required / capacity_planned

        else:
            service_rate_planned = float("inf")

        return capacity_planned, capacity_online, service_rate_planned, capacity_required, nom_crane_productivity, net_crane_productivity, net_berth_productivity

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
                                           post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls)

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

        # print('   > The factor is', factor)
        # print('   > The waiting time occupancy is', waiting_time_occupancy)

        return factor, waiting_time_occupancy

    def check_crane_slot_available(self):
        list_of_elements = self.find_elements(Berth)
        slots = 0
        for element in list_of_elements:
            slots += element.max_cranes

        list_of_elements = self.find_elements(Cyclic_Unloader)

        # when there are more slots than installed cranes
        if slots > len(list_of_elements):
            return True
        else:
            return False

    # def check_barge_crane_slot_available(self):
    #     list_of_elements = self.find_elements(Offshore_Barge_Berth)
    #     slots = 0
    #     for element in list_of_elements:
    #         slots += element.crane_per_berth
    #
    #     list_of_elements = self.find_elements(Barge_Crane)
    #
    #     # when there are more slots than installed cranes
    #     if slots > len(list_of_elements):
    #         return True
    #     else:
    #         return False
    #
    #     print("barge crane slot available is checked")

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

    """ Financial analyses """

    def add_cashflow_elements(self):

        """Create cashflow element DataFrame"""

        # capex_cash_flows_df = pd.DataFrame()
        # opex_cash_flows_df = pd.DataFrame()

        """initialise cash flows"""
        cash_flows_df = pd.DataFrame()

        cash_flows_df['Year'] = list(range(self.startyear, self.startyear + self.lifecycle))

        # island
        cash_flows_df['Reclamation'] = 0
        cash_flows_df['Coastal Protection'] = 0
        cash_flows_df['Coastal Structures Maintenance'] = 0

        # terminal
        cash_flows_df['Offshore Terminal Capex'] = 0
        cash_flows_df['Offshore Maintenance'] = 0
        cash_flows_df['Offshore Insurance'] = 0
        cash_flows_df['Offshore Energy'] = 0
        cash_flows_df['Offshore Labour'] = 0
        cash_flows_df['Offshore Fuel'] = 0
        cash_flows_df['Offshore Terminal Opex'] = 0

        cash_flows_df['Onshore Terminal Capex'] = 0
        cash_flows_df['Onshore Maintenance'] = 0
        cash_flows_df['Onshore Insurance'] = 0
        cash_flows_df['Onshore Energy'] = 0
        cash_flows_df['Onshore Labour'] = 0
        cash_flows_df['Onshore Fuel'] = 0
        cash_flows_df['Onshore Terminal Opex'] = 0

        # transport
        cash_flows_df['Ocean Transport'] = 0
        # cash_flows_df['Demurrage'] = 0
        cash_flows_df['Barge Capex'] = 0
        cash_flows_df['Barge Opex'] = 0

        # offshore connection
        cash_flows_df['Capital Dredging'] = 0
        cash_flows_df['Maintenance Dredging'] = 0

        for element in self.elements:
            if hasattr(element, 'df'):
                for column in cash_flows_df.columns:
                    if column in element.df.columns and column != "Year":
                        cash_flows_df[column] += element.df[column]

        cash_flows_df = cash_flows_df.fillna(0)

        # calculate WACC real cashflows
        cash_flows_WACC_real_df = pd.DataFrame()
        cash_flows_WACC_real_df['Year'] = cash_flows_df['Year']

        for year in range(self.startyear, self.startyear + self.lifecycle):
            for column in cash_flows_df.columns:
                if column != "Year":
                    cash_flows_WACC_real_df.loc[cash_flows_WACC_real_df['Year'] == year, column] = (
                            cash_flows_df.loc[cash_flows_df['Year'] == year, column] / ((1 + self.WACC_real()) ** (year - self.startyear)))

        return cash_flows_df, cash_flows_WACC_real_df

    def add_cashflow_data_to_element(self, element):

        """Place cashflow data in element DataFrame"""

        # years
        years = list(range(self.startyear, self.startyear + self.lifecycle))

        # island
        island_construction = element.island_construction
        coastal_protection_construction = element.coastal_protection_construction
        structure_maintenance = element.structure_maintenance

        # terminal
        off_terminal_capex = element.off_terminal_capex
        maintenance = element.maintenance
        insurance = element.insurance
        energy = element.energy
        fuel = element.fuel
        labour = element.labour

        # offshore connection
        capital_dredging = element.capital_dredging
        maintenance_dredging = element.maintenance_dredging

        # transport
        # demurrage = element.demurrage
        # ocean_transport = element.ocean_transport
        barge_capex = element.barge_capex
        barge_opex = element.barge_opex

        # year online
        year_online = element.year_online
        year_delivery = element.delivery_time

        df = pd.DataFrame()

        # years
        df["Year"] = years

        # island
        if island_construction:
            if year_delivery > 1:
                df.loc[df["Year"] == year_online - 2, "Reclamation"] = 0.4 * island_construction
                df.loc[df["Year"] == year_online - 1, "Reclamation"] = 0.6 * island_construction
            else:
                df.loc[df["Year"] == year_online - 1, "Reclamation"] = island_construction

        if coastal_protection_construction:
            if year_delivery > 1:
                df.loc[df["Year"] == year_online - 2, "Coastal Protection"] = 0.4 * coastal_protection_construction
                df.loc[df["Year"] == year_online - 1, "Coastal Protection"] = 0.6 * coastal_protection_construction
            else:
                df.loc[df["Year"] == year_online - 1, "Coastal Protection"] = coastal_protection_construction

        if structure_maintenance:
            df.loc[df["Year"] >= year_online, "Coastal Structures Maintenance"] = structure_maintenance

        # terminals
        if off_terminal_capex:
            if year_delivery > 1:
                df.loc[df["Year"] == year_online - 2, "Offshore Terminal Capex"] = 0.6 * off_terminal_capex
                df.loc[df["Year"] == year_online - 1, "Offshore Terminal Capex"] = 0.4 * off_terminal_capex
                df.loc[df["Year"] == year_online - 2, "Onshore Terminal Capex"] = 0.6 * off_terminal_capex * self.offshore_onshore_ratio
                df.loc[df["Year"] == year_online - 1, "Onshore Terminal Capex"] = 0.4 * off_terminal_capex * self.offshore_onshore_ratio
            else:
                df.loc[df["Year"] == year_online - 1, "Offshore Terminal Capex"] = off_terminal_capex
                df.loc[df["Year"] == year_online - 1, "Onshore Terminal Capex"] = off_terminal_capex * self.offshore_onshore_ratio

        if maintenance:
            df.loc[df["Year"] >= year_online, "Offshore Maintenance"] = maintenance
            df.loc[df["Year"] >= year_online, "Onshore Maintenance"] = maintenance * self.offshore_onshore_ratio
        if insurance:
            df.loc[df["Year"] >= year_online, "Offshore Insurance"] = insurance
            df.loc[df["Year"] >= year_online, "Onshore Insurance"] = insurance * self.offshore_onshore_ratio
        if energy:
            df.loc[df["Year"] >= year_online, "Offshore Energy"] = energy
            df.loc[df["Year"] >= year_online, "Onshore Energy"] = energy * self.offshore_onshore_ratio
        if fuel:
            df.loc[df["Year"] >= year_online, "Offshore Fuel"] = fuel
            df.loc[df["Year"] >= year_online, "Onshore Fuel"] = fuel * self.offshore_onshore_ratio
        if labour:
            df.loc[df["Year"] >= year_online, "Offshore Labour"] = labour
            df.loc[df["Year"] >= year_online, "Onshore Labour"] = labour * self.offshore_onshore_ratio

        # channel
        if capital_dredging:
            if year_delivery > 1:
                df.loc[df["Year"] == year_online - 2, "Capital Dredging"] = capital_dredging * 0.5
                df.loc[df["Year"] == year_online - 1, "Capital Dredging"] = capital_dredging * 0.5
            else:
                df.loc[df["Year"] == year_online - 1, "Capital Dredging"] = capital_dredging

        if maintenance_dredging:
            df.loc[df["Year"] >= year_online, "Maintenance Dredging"] = maintenance_dredging

        # container ships
        # if ocean_transport:
        #     df.loc[df["Year"] >= year_online, "Ocean Transport"] = ocean_transport
        # if demurrage:
        #     df.loc[df["Year"] >= year_online, "Demurrage"] = demurrage

        # barges
        if barge_capex:
            df.loc[df["Year"] == year_online - 1, "Barge Capex"] = barge_capex
        if barge_opex:
            df.loc[df["Year"] >= year_online, "Barge Opex"] = barge_opex

        df.fillna(0, inplace=True)

        element.df = df

        print("df", df.head())

        return element

        print('element', element)

    def overview_dataframes(self):

        # overview cash flow
        capex_cash_flows_df['Offshore Terminal'] = 0
        capex_cash_flows_df['Onshore Terminal'] = 0
        capex_cash_flows_df['Capital Dredging'] = 0
        capex_cash_flows_df['Barges'] = 0
        capex_cash_flows_df['Total'] = 0

        opex_cash_flows_df['Ocean Transport'] = 0
        opex_cash_flows_df['Offshore Terminal'] = 0
        opex_cash_flows_df['Onshore Terminal'] = 0
        opex_cash_flows_df['Maintenance Dredging'] = 0
        opex_cash_flows_df['Barge Operations'] = 0
        opex_cash_flows_df['Total'] = 0

    def WACC_nom(self, Gearing=60, Re=.135, Rd=.08, Tc=.20):
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

    def net_present_value(self):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        "add cash flow information for each of the Terminal elements"
        cash_flows_df, cash_flows_WACC_real_df = self.add_cashflow_elements()

        "prepare years, revenue, capex and opex real for plotting"
        years = cash_flows_WACC_real_df['Year'].values

        # island
        island_construction = cash_flows_WACC_real_df['Reclamation'].values
        coastal_protection_construction = cash_flows_WACC_real_df['Coastal Protection'].values
        structure_maintenance = cash_flows_WACC_real_df['Coastal Structures Maintenance'].values

        # terminal
        off_terminal_capex = cash_flows_WACC_real_df['Offshore Terminal Capex'].values
        off_terminal_opex = (cash_flows_WACC_real_df['Offshore Maintenance'].values
                         + cash_flows_WACC_real_df['Offshore Insurance'].values
                         + cash_flows_WACC_real_df['Offshore Energy'].values
                         + cash_flows_WACC_real_df['Offshore Fuel'].values
                         + cash_flows_WACC_real_df['Offshore Labour'].values)
        off_terminal_opex = np.nan_to_num(off_terminal_opex)
        cash_flows_WACC_real_df['Offshore Terminal Opex'] = off_terminal_opex

        # channel
        capital_dredging = cash_flows_WACC_real_df['Capital Dredging'].values
        maintenance_dredging = cash_flows_WACC_real_df['Maintenance Dredging'].values

        # container ships
        ocean_transport = cash_flows_WACC_real_df['Ocean Transport'].values
        # demurrage = cash_flows_WACC_real_df['Demurrage'].values

        # barges
        barge_capex = cash_flows_WACC_real_df['Barge Capex'].values
        barge_opex = cash_flows_WACC_real_df['Barge Opex'].values

        cash_flows = - (island_construction + coastal_protection_construction + structure_maintenance +
                        off_terminal_capex + off_terminal_opex + capital_dredging + maintenance_dredging + barge_capex + barge_opex)
        cash_flows_WACC_real_df['Total'] = - cash_flows

        NPV = np.sum(cash_flows)

        return island_construction, coastal_protection_construction, structure_maintenance, off_terminal_capex, off_terminal_opex, \
               capital_dredging, maintenance_dredging, ocean_transport, barge_capex, barge_opex, cash_flows, cash_flows_df, cash_flows_WACC_real_df, NPV

    """ Plotting functions """

    def terminal_elements_plot(self, width=0.10, alpha=0.6):
        """ Gather data from Terminal and plot which elements come online when """

        "get demand"
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

        "collect elements to add to plot"
        years = []
        OGV_berths = []
        cranes = []
        quays = []
        tractor = []
        laden_stack = []
        empty_stack = []
        oog_stack = []
        stack_equipment = []
        gates = []
        offshore_barge_berths = []
        onshore_barge_berths = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            OGV_berths.append(0)
            quays.append(0)
            cranes.append(0)
            tractor.append(0)
            laden_stack.append(0)
            empty_stack.append(0)
            oog_stack.append(0)
            stack_equipment.append(0)
            gates.append(0)
            offshore_barge_berths.append(0)
            onshore_barge_berths.append(0)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        OGV_berths[-1] += 1
                if isinstance(element, Quay_Wall):
                    if year >= element.year_online:
                        quays[-1] += 1
                if isinstance(element, Cyclic_Unloader):
                    if year >= element.year_online:
                        cranes[-1] += 1
                if isinstance(element, Horizontal_Transport):
                    if year >= element.year_online:
                        tractor[-1] += 1
                if isinstance(element, Laden_Stack):
                    if year >= element.year_online:
                        laden_stack[-1] += 1
                if isinstance(element, Empty_Stack):
                    if year >= element.year_online:
                        empty_stack[-1] += 1
                if isinstance(element, OOG_Stack):
                    if year >= element.year_online:
                        oog_stack[-1] += 1
                if isinstance(element, Stack_Equipment):
                    if year >= element.year_online:
                        stack_equipment[-1] += 1
                if isinstance(element, Gate):
                    if year >= element.year_online:
                        gates[-1] += 1
                if isinstance(element, Offshore_Barge_Berth):
                    if year >= element.year_online:
                        offshore_barge_berths[-1] += 1
                if isinstance(element, Onshore_Barge_Berth):
                    if year >= element.year_online:
                        onshore_barge_berths[-1] += 1

        "scale elements"
        tractor = [x / 5 for x in tractor]
        stack_equipment = [x / 5 for x in stack_equipment]

        "generate plot"
        fig, (ax1, ax2) = plt.subplots(2, figsize=(16, 12))

        "offshore plot"
        ax1.bar([x - 3.5 * width for x in years], OGV_berths, width=width, alpha=alpha, label="OGV berths")
        ax1.bar([x - 2.5 * width for x in years], cranes, width=width, alpha=alpha, label="STS cranes")
        ax1.bar([x - 1.5 * width for x in years], tractor, width=width, alpha=alpha, label="Tractors (x 5)")
        ax1.bar([x - 0.5 * width for x in years], stack_equipment, width=width, alpha=alpha, label="Stack equipment (x 5)")
        ax1.bar([x + 0.5 * width for x in years], laden_stack, width=width, alpha=alpha, label="Laden stacks (1200 TEU)")
        ax1.bar([x + 1.5 * width for x in years], empty_stack, width=width, alpha=alpha, label="Empty stacks (480 TEU)")
        ax1.bar([x + 2.5 * width for x in years], oog_stack, width=width, alpha=alpha, label="OOG stacks (100 TEU)")
        ax1.bar([x + 3.5 * width for x in years], offshore_barge_berths, width=width, alpha=alpha, label="Barge berths")

        ax1.set_xlabel('Years', fontsize='large')
        ax1.set_ylabel('Elements [nr]', fontsize='large')
        ax1.set_title('Offshore Terminal (equipment: RMG)', fontsize='x-large')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        ax1.set_axisbelow(True)
        ax1.yaxis.grid(color='grey', linestyle='--', linewidth=0.5)

        ax3 = ax1.twinx()
        ax3.set_ylabel('Demand [TEU]', fontsize='large')
        ax3.step(years, demand['demand'].values, where='mid', color='tab:gray', label='Demand')
        ax3.grid(False, which='major')

        if self.lifecycle == 10:
            ax1.legend(loc='lower left', fancybox=True, shadow=False, framealpha=1.0,
                       fontsize='large', title="Offshore terminal elements", title_fontsize='large')
            ax1.set_yticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18])
            ax3.set_ylim(0, 1_530_000)
            ax3.set_yticks([0, 500_000, 1_000_000, 1_500_000])
            ax3.legend(loc='upper left', fancybox=True, shadow=False, framealpha=1.0,
                       fontsize='large')
        if self.lifecycle == 20:
            ax1.legend(loc='upper left', fancybox=True, shadow=False, framealpha=1.0,
                       fontsize='large', title="Offshore terminal elements", title_fontsize='large')

            ax3.set_ylim(0, 2_030_000)
            ax3.set_yticks([0, 500_000, 1_000_000, 1_500_000, 2_000_000])
            ax3.legend(loc='upper left', fancybox=True, shadow=False, framealpha=1.0,
                       fontsize='large', bbox_to_anchor=(0.2, 1.0))

        fig.tight_layout()

        "onshore plot"
        ax2.bar([x - 3.5 * width for x in years], onshore_barge_berths, width=width, alpha=alpha, label="Barge berths")
        ax2.bar([x - 2.5 * width for x in years], cranes,               width=width, alpha=alpha, label="Barge cranes")
        ax2.bar([x - 1.5 * width for x in years], tractor,              width=width, alpha=alpha, label="Tractors (x 5)")
        ax2.bar([x - 0.5 * width for x in years], stack_equipment,      width=width, alpha=alpha, label="Stack equipment (x 5)")
        ax2.bar([x + 0.5 * width for x in years], laden_stack,          width=width, alpha=alpha, label="Laden stacks (1200 TEU)")
        ax2.bar([x + 1.5 * width for x in years], empty_stack,          width=width, alpha=alpha, label="Empty stacks (480 TEU)")
        ax2.bar([x + 2.5 * width for x in years], oog_stack,            width=width, alpha=alpha, label="OOG stacks (100 TEU)")
        ax2.bar([x + 3.5 * width for x in years], gates,                width=width, alpha=alpha, label="Lanes")

        # ax2.set_xlabel('Years', fontsize='large')
        ax2.set_ylabel('Elements [nr]', fontsize='large')
        ax2.set_title('Onshore Terminal (equipment: RMG)',fontsize='x-large')
        ax2.set_xticks([x for x in years])
        ax2.set_xticklabels(years, fontsize='large')
        ax2.set_axisbelow(True)
        ax2.yaxis.grid(color='grey', linestyle='--', linewidth=0.5)
        ax2.legend(loc='upper left', fancybox=True, shadow=True, framealpha=0.0,
                   fontsize='large', title="Onshore terminal elements", title_fontsize='large')

        ax3 = ax2.twinx()
        ax3.set_ylabel('Demand [TEU]', fontsize='large')
        ax3.set_ylim(0, 2_030_000)
        ax3.step(years, demand['demand'].values, where='mid', color='tab:gray', label='Demand')
        ax3.grid(False, which='major')
        ax3.set_yticks([0, 500_000, 1_000_000, 1_500_000, 2_000_000])

        if self.lifecycle == 10:
            ax2.legend(loc='lower left', fancybox=True, shadow=True, framealpha=1.0,
                       fontsize='large', title="Onshore terminal elements", title_fontsize='large')
            ax2.set_yticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18])
            ax3.set_ylim(0, 1_530_000)
            ax3.set_yticks([0, 500_000, 1_000_000, 1_500_000])
            ax3.legend(loc='upper left', fancybox=True, shadow=True, framealpha=1.0,
                       fontsize='large')
        if self.lifecycle == 20:
            ax2.legend(loc='upper left', fancybox=True, shadow=True, framealpha=1.0,
                       fontsize='large', title="Onshore terminal elements", title_fontsize='large')

            ax3.set_ylim(0, 2_030_000)
            ax3.set_yticks([0, 500_000, 1_000_000, 1_500_000, 2_000_000])
            ax3.legend(loc='upper left', fancybox=True, shadow=True, framealpha=1.0,
                       fontsize='large', bbox_to_anchor=(0.2, 1.0))
        fig.tight_layout()

        plt.setp(ax1.patches, linewidth=0)
        plt.setp(ax2.patches, linewidth=0)
        plt.setp(ax3.patches, linewidth=0)

        ax1.grid(False, which='major')
        ax2.grid(False, which='major')

    def terminal_capacity_plot(self, width=0.25, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        "get crane service capacity"
        years = []
        cranes = []
        cranes_capacity = []

        for year in range(self.startyear, self.startyear + self.lifecycle):

            years.append(year)
            cranes.append(0)
            cranes_capacity.append(0)

            fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls, total_calls, \
            total_vol = self.calculate_vessel_calls(year)

            berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = self.calculate_berth_occupancy(
                year, fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls,
                post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls)

            for element in self.elements:
                if isinstance(element, Cyclic_Unloader):
                    if year >= element.year_online:
                        cranes[-1] += 1
                        cranes_capacity[-1] += element.effective_capacity * self.operational_hours * crane_occupancy_online

        "get demand"
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

        def generate_terminal_capacity_plot():
            fig, (ax1, ax2) = plt.subplots(2, figsize=(16, 10))

            ax1.bar(years, cranes_capacity, width=width, alpha=alpha, label="OGV Berth Capacity")
            ax1.step(years, demand['demand'].values, where='mid', label='Demand', color='tab:gray')

            # ax1.set_xlabel('Years')
            ax1.set_ylabel('Throughput capacity [TEU/year]', fontsize='large')
            ax1.set_title('Offshore Terminal', fontsize='large')
            ax1.set_xticks([x for x in years])
            ax1.set_xticklabels(years)
            ax1.legend()
            ax2.bar(years, cranes_capacity, width=width, alpha=alpha, label="Barge Berth Capacity")
            ax2.step(years, demand['demand'].values, where='mid', label='Demand', color='tab:grey')

            ax2.set_xlabel('Years', fontsize='large')
            ax2.set_ylabel('Throughput capacity [TEU/year]', fontsize='large')
            ax2.set_title('Onshore Terminal', fontsize='large')
            ax2.set_xticks([x for x in years])
            ax2.set_xticklabels(years)
            ax2.legend()

            plt.setp(ax1.patches, linewidth=0)
            plt.setp(ax2.patches, linewidth=0)

            ax1.grid(False, which='major')
            ax2.grid(False, which='major')
        generate_terminal_capacity_plot()

    def terminal_land_use_plot(self, width=0.25, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        "get land use"
        years = []
        OGV_quay_land_use = []
        stack_land_use = []
        empty_land_use = []
        oog_land_use = []
        gate_land_use = []
        offshore_barge_land_use = []
        onshore_barge_land_use = []
        general_land_use = []

        "get demand"
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

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            OGV_quay_land_use.append(0)
            stack_land_use.append(0)
            empty_land_use.append(0)
            oog_land_use.append(0)
            gate_land_use.append(0)
            offshore_barge_land_use.append(0)
            onshore_barge_land_use.append(0)
            general_land_use.append(0)

            for element in self.elements:
                if isinstance(element, Quay_Wall):
                    if year >= element.year_online:
                        OGV_quay_land_use[-1] += element.land_use
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
                if isinstance(element, Offshore_Barge_Quay_Wall):
                    if year >= element.year_online:
                        offshore_barge_land_use[-1] += element.land_use
                if isinstance(element, Onshore_Barge_Quay_Wall):
                    if year >= element.year_online:
                        onshore_barge_land_use[-1] += element.land_use
                if isinstance(element, General_Services):
                    if year >= element.year_online:
                        general_land_use[-1] += element.land_use

        def land_use_df():
            offshore_total_land_use = [OGV_quay_land_use, stack_land_use, empty_land_use, oog_land_use, offshore_barge_land_use, general_land_use]
            offshore_total_land_use = sum(map(np.array, offshore_total_land_use)) / 10000
            convert_ha = 10_000
            stack_land_use_ha = np.divide(stack_land_use, convert_ha)
            oog_land_use_ha = np.divide(oog_land_use, convert_ha)
            empty_land_use_ha = np.divide(empty_land_use, convert_ha)
            storage_land_use_ha = sum(map(np.array, [stack_land_use_ha, oog_land_use_ha, empty_land_use_ha]))
            land_use_df = pd.DataFrame(list(zip(years, stack_land_use_ha, oog_land_use_ha, empty_land_use_ha, storage_land_use_ha, offshore_total_land_use)),
                                       columns=['Year', 'Laden stack (ha)', 'OOG stack (ha)', 'Empty stack (ha)', 'Total storage (ha)', 'Total land use (ha)'])
            land_use_df.set_index('Year', inplace=True)
            display(land_use_df)
        land_use_df()

        OGV_quay_land_use = [x * 0.0001 for x in OGV_quay_land_use]
        stack_land_use = [x * 0.0001 for x in stack_land_use]
        empty_land_use = [x * 0.0001 for x in empty_land_use]
        oog_land_use = [x * 0.0001 for x in oog_land_use]
        gate_land_use = [x * 0.0001 for x in gate_land_use]
        offshore_barge_land_use = [x * 0.0001 for x in offshore_barge_land_use]
        onshore_barge_land_use = [x * 0.0001 for x in onshore_barge_land_use]
        general_land_use = [x * 0.0001 for x in general_land_use]

        # offshore
        off_quay_stack  = np.add(OGV_quay_land_use, stack_land_use).tolist()
        off_quay_empty  = np.add(off_quay_stack, empty_land_use).tolist()
        off_quay_oog    = np.add(off_quay_empty, oog_land_use).tolist()
        off_quay_barge  = np.add(off_quay_oog, offshore_barge_land_use).tolist()

        # onshore
        on_quay_stack = np.add(onshore_barge_land_use, stack_land_use).tolist()
        on_quay_empty = np.add(on_quay_stack, empty_land_use).tolist()
        on_quay_oog   = np.add(on_quay_empty, oog_land_use).tolist()
        on_quay_gate  = np.add(on_quay_oog, gate_land_use).tolist()
        on_quay_barge = np.add(on_quay_oog, offshore_barge_land_use).tolist()

        def generate_land_use_plot():
            fig, (ax1, ax2) = plt.subplots(2, figsize=(16, 12))

            'offshore'
            ax1.bar(years, OGV_quay_land_use,       width=width, alpha=alpha, label="OGV Apron")
            ax1.bar(years, stack_land_use,          width=width, alpha=alpha, label="Laden and Reefer Stack", bottom=OGV_quay_land_use)
            ax1.bar(years, empty_land_use,          width=width, alpha=alpha, label="Empty Stack",            bottom=off_quay_stack)
            ax1.bar(years, oog_land_use,            width=width, alpha=alpha, label="OOG Stack",              bottom=off_quay_empty)
            ax1.bar(years, offshore_barge_land_use, width=width, alpha=alpha, label="Barge Area",             bottom=off_quay_oog)
            ax1.bar(years, general_land_use,        width=width, alpha=alpha, label="General Service Area",   bottom=off_quay_barge)

            # ax1.set_xlabel('Years', fontsize='large')
            ax1.set_ylabel('Land use [ha]', fontsize='large')
            ax1.set_title('Offshore Terminal', fontsize='large')
            ax1.set_xticks([x for x in years])
            ax1.set_xticklabels(years, fontsize='large')
            ax1.legend(loc='lower left', fontsize='large')

            'onshore'
            ax2.bar(years, onshore_barge_land_use, width=width, alpha=alpha, label="Barge Apron")
            ax2.bar(years, stack_land_use,         width=width, alpha=alpha, label="Laden and Reefer Stack", bottom=onshore_barge_land_use)
            ax2.bar(years, empty_land_use,         width=width, alpha=alpha, label="Empty Stack",            bottom=on_quay_stack)
            ax2.bar(years, oog_land_use,           width=width, alpha=alpha, label="OOG Stack",              bottom=on_quay_empty)
            ax2.bar(years, gate_land_use,          width=width, alpha=alpha, label="Gate Area",              bottom=on_quay_oog)
            ax2.bar(years, general_land_use,       width=width, alpha=alpha, label="General Service Area",   bottom=on_quay_gate)

            ax2.set_xlabel('Years', fontsize='large')
            ax2.set_ylabel('Land use [ha]', fontsize='large')
            ax2.set_title('Onshore Terminal', fontsize='large')
            ax2.set_xticks([x for x in years])
            ax2.set_xticklabels(years, fontsize='large')
            ax2.legend(loc='lower left', fontsize='large')

            ax3 = ax1.twinx()
            ax3.step(years, demand['demand'].values, where='mid', color='tab:gray', label='Demand')
            ax3.set_ylabel('Demand [TEU]', fontsize='large')
            ax3.set_ylim(0, )

            ax3 = ax2.twinx()
            ax3.step(years, demand['demand'].values, where='mid', color='tab:gray', label='Demand')
            ax3.set_ylabel('Demand [TEU]', fontsize='large')
            ax3.set_ylim(0, )

            fig.tight_layout()

            plt.setp(ax1.patches, linewidth=0)
            plt.setp(ax2.patches, linewidth=0)
            plt.setp(ax3.patches, linewidth=0)

            ax1.grid(False, which='major')
            ax2.grid(False, which='major')
            ax3.grid(False, which='major')
        generate_land_use_plot()

    def storage_area_plot(self, width=0.25, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # get storage area
        years = []
        stack_storage_area = []
        empty_storage_area = []
        oog_storage_area = []

        for year in range(self.startyear, self.startyear + self.lifecycle):

            years.append(year)
            stack_storage_area.append(0)
            empty_storage_area.append(0)
            oog_storage_area.append(0)

            for element in self.elements:
                if isinstance(element, Laden_Stack):
                    if year >= element.year_online:
                        stack_storage_area[-1] += element.storage_area
                if isinstance(element, Empty_Stack):
                    if year >= element.year_online:
                        empty_storage_area[-1] += element.storage_area
                if isinstance(element, OOG_Stack):
                    if year >= element.year_online:
                        oog_storage_area[-1] += element.storage_area

        "total storage area"
        total_storage_area = [stack_storage_area, empty_storage_area, oog_storage_area]
        total_storage_area = sum(map(np.array, total_storage_area))/1000
        storage_area_df = pd.DataFrame(list(zip(years, total_storage_area)), columns = ['Year', 'Storage Area'])
        storage_area_df.set_index('Year')

        stack_storage_area = [x * 0.001 for x in stack_storage_area]
        empty_storage_area = [x * 0.001 for x in empty_storage_area]
        oog_storage_area = [x * 0.001 for x in oog_storage_area]

        stack_empty = np.add(stack_storage_area, empty_storage_area).tolist()
        stack_empty_storage = np.add(empty_storage_area, oog_storage_area).tolist()

        def generate_storage_area_plot():
            fig, (ax1, ax2) = plt.subplots(2, figsize=(16, 12))

            ax1.bar(years, stack_storage_area, width=width, alpha=alpha, label="Laden and Reefer Stack", bottom=None)
            ax1.bar(years, empty_storage_area, width=width, alpha=alpha, label="Empty Stack", bottom=stack_storage_area)
            ax1.bar(years, oog_storage_area, width=width, alpha=alpha, label="OOG Stack", bottom=stack_empty)

            ax1.step(years, total_storage_area, where='mid', label='Storage Area', color='tab:gray')

            # ax1.set_xlabel('Years')
            ax1.set_ylabel('Storage Area [TEU]')
            ax1.set_title('Onshore Storage Area')
            ax1.set_xticks([x for x in years])
            ax1.set_xticklabels(years)
            ax1.legend()

            ax2.bar(years, stack_storage_area, width=width, alpha=alpha, label="Laden and Reefer Stack", bottom=None)
            ax2.bar(years, empty_storage_area, width=width, alpha=alpha, label="Empty Stack", bottom=stack_storage_area)
            ax2.bar(years, oog_storage_area, width=width, alpha=alpha, label="OOG Stack", bottom=stack_empty)

            ax2.step(years, total_storage_area, where='mid', color='tab:gray')

            ax2.set_xlabel('Years')
            ax2.set_ylabel('Storage Area [TEU]')
            ax2.set_title('Onshore Storage Area')
            ax2.set_xticks([x for x in years])
            ax2.set_xticklabels(years)
            ax2.legend()

            plt.setp(ax1.patches, linewidth=0)
            plt.setp(ax2.patches, linewidth=0)
        generate_storage_area_plot()

    def terminal_opex_plot(self, cash_flows_df):

        """Gather data from Terminal elements and combine into a cash flow plot"""

        "prepare years, revenue, capex and opex for plotting"
        years = cash_flows_df['Year'].values
        off_maintenance = cash_flows_df['Offshore Maintenance'].values
        off_insurance = cash_flows_df['Offshore Insurance'].values
        off_energy = cash_flows_df['Offshore Energy'].values
        off_fuel = cash_flows_df['Offshore Fuel'].values
        off_labour = cash_flows_df['Offshore Labour'].values

        on_maintenance = cash_flows_df['Offshore Maintenance'].values * self.offshore_onshore_ratio
        on_insurance = cash_flows_df['Offshore Insurance'].values * self.offshore_onshore_ratio
        on_energy = cash_flows_df['Offshore Energy'].values* self.offshore_onshore_ratio
        on_fuel = cash_flows_df['Offshore Fuel'].values* self.offshore_onshore_ratio
        on_labour = cash_flows_df['Offshore Labour'].values* self.offshore_onshore_ratio

        "generate plot"
        fig, (ax1, ax2) = plt.subplots(2, figsize=(16, 12))
        ax1.step(years, off_maintenance, label='Maintenance', where='mid')
        ax1.step(years, off_insurance, label='Insurance', where='mid')
        ax1.step(years, off_energy, label='Energy', where='mid')
        ax1.step(years, off_fuel, label='Fuel', where='mid')
        ax1.step(years, off_labour, label='Labour', where='mid')
        ax1.set_xlabel('Years')
        ax1.set_ylabel('Opex [M US$]')
        ax1.set_title('Opex Onshore Terminal')
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        # ax1.set_yticks(np.arange(0, 1000 * 10^6, 100 * 10^6))
        ax1.legend()

        ax2.step(years, on_maintenance, label='Maintenance', where='mid')
        ax2.step(years, on_insurance, label='Insurance', where='mid')
        ax2.step(years, on_energy, label='Energy', where='mid')
        ax2.step(years, on_fuel, label='Fuel', where='mid')
        ax2.step(years, on_labour, label='Labour', where='mid')
        ax2.set_xlabel('Years')
        ax2.set_ylabel('Opex [M US$]')
        ax2.set_title('Opex Offshore Terminal')
        ax2.set_xticks([x for x in years])
        ax2.set_xticklabels(years)
        ax2.legend()

        plt.setp(ax1.patches, linewidth=0)
        plt.setp(ax2.patches, linewidth=0)

    def element_cashflow_plot(self):
        island_construction, coastal_protection_construction, offshore_maintenance, off_terminal_capex, terminal_opex, capital_dredging, maintenance_dredging, \
        ocean_transport, barge_capex, barge_opex, cash_flows, cash_flows_df, cash_flows_WACC_real_df, NPV = self.net_present_value()

        """Gather data from Terminal elements and combine into a barplot"""

        element = ["Reclamation", "Coastal Protection", "Island maint.",
                   "Terminal Capex", "Terminal Opex", "Capital Dredging", "Maintenance Dredging",
                   "Ocean Transport", "Barge Investment", "Barge Operartions"]

        costs = []
        costs.append(np.sum(island_construction))
        costs.append(np.sum(coastal_protection_construction))
        costs.append(np.sum(offshore_maintenance))
        costs.append(np.sum(off_terminal_capex))
        costs.append(np.sum(terminal_opex))
        costs.append(np.sum(capital_dredging))
        costs.append(np.sum(maintenance_dredging))
        costs.append(np.sum(ocean_transport))
        costs.append(np.sum(barge_capex))
        costs.append(np.sum(barge_opex))

        df = pd.DataFrame()
        df["Element"] = element
        df["Costs"] = costs
        # df["RHDHV"] = [1.1 * 9.643031e+08, 6.335749e+08, 1.1 * 5.148727e+08, 2.969801e+08, 1.1 * 2.444650e+08, 1.168661e+08, 1.044354e+08, 1.1 * 8.169944e+07, 1.711446e+07, 0.000000e+00]

        df = df.sort_values(by=["Costs"], ascending=False)

        print("list of elements")
        print(df)

        "generate plot"
        fig, ax = plt.subplots(figsize=(16, 8))
        ax = sns.barplot(x = df.Element, y = df.Costs, palette = "Blues_d")

    def cashflow_plot(self, cash_flows_df, width=0.3, alpha=0.6):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        # New-Panamax transport costs
        if self.lifecycle == 10:
            ocean_transport = [0, 0, 559_000_000, 559_000_000, 559_000_000, 743_470_000, 743_470_000, 743_470_000, 743_470_000, 743_470_000]
        if self.lifecycle == 20:
            ocean_transport = [0, 0, 559_000_000, 559_000_000, 559_000_000, 743_470_000, 743_470_000, 743_470_000, 743_470_000, 743_470_000,
                               933_530_000, 933_530_000, 933_530_000, 933_530_000, 933_530_000, 1_118_000_000, 1_118_000_000, 1_118_000_000, 1_118_000_000, 1_118_000_000]

        data = {'Ocean Transport': ocean_transport,
                }
        manual_df = pd.DataFrame(data)

        "prepare years, revenue, capex and opex for plotting"
        years = cash_flows_df['Year'].values

        # island
        island_construction = cash_flows_df['Reclamation'].values
        coastal_protection_construction = cash_flows_df['Coastal Protection'].values
        structure_maintenance = cash_flows_df['Coastal Structures Maintenance'].values

        # terminal
        off_terminal_capex = cash_flows_df['Offshore Terminal Capex'].values
        off_terminal_opex = (cash_flows_df['Offshore Maintenance'].values
                             + cash_flows_df['Offshore Insurance'].values
                             + cash_flows_df['Offshore Energy'].values
                             + cash_flows_df['Offshore Fuel'].values
                             + cash_flows_df['Offshore Labour'].values)
        off_terminal_opex = np.nan_to_num(off_terminal_opex)

        on_terminal_capex =cash_flows_df['Onshore Terminal Capex'].values
        on_terminal_opex = (cash_flows_df['Onshore Maintenance'].values
                             + cash_flows_df['Onshore Insurance'].values
                             + cash_flows_df['Onshore Energy'].values
                             + cash_flows_df['Onshore Fuel'].values
                             + cash_flows_df['Onshore Labour'].values)

        # channel
        capital_dredging = cash_flows_df['Capital Dredging'].values
        maintenance_dredging = cash_flows_df['Maintenance Dredging'].values

        # transport
        barge_capex = cash_flows_df['Barge Capex'].values
        barge_opex = cash_flows_df['Barge Opex'].values
        ocean_transport = manual_df['Ocean Transport'].values

        "sum cash flows to get costs as a function of year"
        costs = (- island_construction - coastal_protection_construction - structure_maintenance
                 - off_terminal_capex - off_terminal_opex - on_terminal_capex - on_terminal_opex
                 - capital_dredging - maintenance_dredging - barge_capex - barge_opex - ocean_transport)
        costs_cum = np.cumsum(costs)

        "generate plot"
        fig, ax2 = plt.subplots(figsize=(16, 8))

        capex_terminals = off_terminal_capex + on_terminal_capex
        capex_dredging = capex_terminals + capital_dredging
        capex_barges = capex_dredging + barge_capex
        capex_island = capex_barges + island_construction

        opex_terminals = off_terminal_opex + on_terminal_opex
        opex_dredging = opex_terminals + maintenance_dredging
        opex_barges = opex_dredging + barge_opex
        opex_OGV = opex_barges + structure_maintenance

        bar1 = ax2.bar([x + 0.5 * width for x in years], - off_terminal_capex, width=width, color='tab:blue', alpha=1.0, bottom = None, label="Offshore Terminal")
        bar2 = ax2.bar([x + 0.5 * width for x in years], - on_terminal_capex, width=width, color='tab:blue', alpha=0.9, bottom= - off_terminal_capex, label="Onshore Terminal")
        bar3 = ax2.bar([x + 0.5 * width for x in years], - capital_dredging, width=width, color='tab:blue', alpha=0.8, bottom = - capex_terminals, label="Capital Dredging")
        bar4 = ax2.bar([x + 0.5 * width for x in years], - barge_capex, width=width, color='tab:blue', alpha=0.6, bottom = - capex_dredging, label="Barges")
        bar5 = ax2.bar([x + 0.5 * width for x in years], - island_construction, width=width, color='tab:blue', alpha=0.4, bottom = - capex_barges, label="Reclamation")
        bar6 = ax2.bar([x + 0.5 * width for x in years], - coastal_protection_construction, width=width, color='tab:blue', alpha=0.3, bottom = - capex_island, label="Coastal Protection")

        bar7 = ax2.bar([x - 0.5 * width for x in years], - off_terminal_opex, width=width, color='darkcyan', alpha=1.0, bottom = None, label="Offshore Terminal")
        bar8 = ax2.bar([x - 0.5 * width for x in years], - on_terminal_opex, width=width, color='darkcyan', alpha=0.8, bottom = - off_terminal_opex, label="Offshore Terminal")
        bar9 = ax2.bar([x - 0.5 * width for x in years], - maintenance_dredging, width=width, color='darkcyan', alpha=0.6, bottom = - opex_terminals, label="Maintenance Dredging")
        bar10 = ax2.bar([x - 0.5 * width for x in years], - barge_opex, width=width, color='darkcyan', alpha=0.4, bottom = - opex_dredging, label="Barge Operations")
        bar11 = ax2.bar([x - 0.5 * width for x in years], - structure_maintenance, width=width, color='darkcyan', alpha=0.2, bottom= - opex_barges, label="Coastal Structure Maintenance")
        bar12 = ax2.bar([x - 0.5 * width for x in years], - ocean_transport, width=width, color='darkcyan', alpha=0.15, bottom= - opex_OGV, label="Ocean Transport")

        plot1, = ax2.step(years, costs, label="Annual Costs", where='mid', linestyle='-', color='tab:red', alpha=0.6, zorder=2)
        # plot2, = ax2.step(years, costs_cum, label="Cumulative Costs", where='mid', linestyle='-.', color='tab:red', alpha=0.8, zorder=3)
        # plot3 = ax2.axhline(y = costs_cum[len(costs_cum)-1], label="PV of the costs", color='tab:red', linestyle='--', alpha=1.0, zorder=4)

        ax2.set_xlabel('Years')
        ax2.set_ylabel('Cashflow [M US$]')
        ax2.set_title('Cash flow plot')

        ax2.set_yticks([0,-1000000000,-2000000000,-3000000000,-4000000000,-5000000000,-6000000000])
        ax2.set_yticklabels(["$ 0M","$ -1,000M","$ -2,000M","$ -3,000M","$ -4,000M", "$ -5,000M", "$-6,000M"])
        ax2.set_yticks([0,-1000000000,-2000000000,-3000000000,])
        ax2.set_yticklabels(["$ 0M","$ -1,000M","$ -2,000M","$ -3,000M"])

        ax2.xaxis.tick_top()
        ax2.set_xticks([x for x in years])
        ax2.set_xticklabels(years)

        # first_leg = ax2.legend(handles=[plot1,plot2,plot3],
        #                         loc='upper right', bbox_to_anchor=(1.0, 0.30), fancybox=True, shadow=True, framealpha = 1.0, fontsize='large',
        #                         title="Cost-estimation",title_fontsize='large')
        first_leg = ax2.legend(handles=[plot1,],
                                loc='upper right', bbox_to_anchor=(1.0, 0.275), fancybox=True, shadow=True, framealpha = 1.0, fontsize='large',
                                title="Cost-estimation",title_fontsize='large')
        add_first_leg = plt.gca().add_artist(first_leg)

        second_leg = ax2.legend(handles=[bar1,bar2,bar3,bar4,bar5,bar6],
                                loc='upper right', bbox_to_anchor=(1.0, 0.9), fancybox=True, shadow=True, framealpha = 1.0, fontsize='large',
                                title="Capex",title_fontsize='large')
        add_second_leg = plt.gca().add_artist(second_leg)

        ax2.legend(handles=[bar7,bar8,bar9,bar10,bar11,bar12],
                   loc='upper right', bbox_to_anchor=(1.0, 0.625), fancybox=True, shadow=True, framealpha = 1.0, fontsize='large',
                   title="Opex", title_fontsize ='large')

        # ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, framealpha = 1.0, ncol=5, fontsize='large')

        plt.setp(ax2.patches, linewidth=0)
        ax2.grid(False, which='major')

    def ex_cashflow_plot(self, cash_flows_df, width=0.3, alpha=0.6):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        "add manually"
        if self.lifecycle == 10:
            # example capex
            capital_dredging = [1000000, 600000, 0, 0, 0, 600000, 0, 0, 0, 0]
            terminal_construction = [1000000, 800000, 0, 0, 0, 1000000, 0, 0, 0, 0]

            # example opex
            terminal_operations =   [0, 0, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000]
            container_ships =       [0, 0, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000]
            barges =                [0, 0, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000]
            maintenance_dredging =  [0, 0, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000]

        if self.lifecycle == 20:
            # example capex
            capital_dredging = [1000000, 600000, 0, 0, 0, 600000, 0, 0, 0, 0, 600000, 0, 0, 0, 0, 600000, 0, 0, 0, 0]
            terminal_construction = [1000000, 800000, 0, 0, 0, 1000000, 0, 0, 0, 0, 1000000, 0, 0, 0, 0, 1000000, 0, 0, 0, 0]

            # example opex
            terminal_operations = [0, 0, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000]
            container_ships = [0, 0, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000, 180000]
            barges = [0, 0, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000]
            maintenance_dredging = [0, 0, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000, 120000]

        data = {'Capital Dredging': capital_dredging,
                'Terminal Construction': terminal_construction,
                'Terminal Operations': terminal_operations,
                'Container Ships': container_ships,
                'Barges': barges,
                'Maintenance Dredging': maintenance_dredging,
               }
        example_df = pd.DataFrame(data)
        # print(example_df)

        "prepare years, revenue, capex and opex for plotting"
        years = cash_flows_df['Year'].values
        capital_dredging = example_df['Capital Dredging'].values
        terminal_construction = example_df['Terminal Construction'].values
        terminal_operations = example_df['Terminal Operations'].values
        container_ships = example_df['Container Ships'].values
        barges = example_df['Barges'].values
        maintenance_dredging = example_df['Maintenance Dredging'].values

        "sum cash flows to get costs as a function of year"
        costs = (- capital_dredging - terminal_construction                                 # capex
                 - terminal_operations - container_ships - barges - maintenance_dredging)   # opex
        costs_cum = np.cumsum(costs)

        opex_1 = - terminal_operations
        opex_2 = - terminal_operations - container_ships
        opex_3 = - terminal_operations - container_ships - barges

        "generate plot"
        fig, ax2 = plt.subplots(figsize=(16, 8))

        bar1 = ax2.bar([x - 0.5 * width for x in years], - capital_dredging, width=width, color='tab:blue', alpha=1.0, bottom=None, label="Capital Dredging")
        bar2 = ax2.bar([x - 0.5 * width for x in years], - terminal_construction, width=width, color='tab:blue', alpha=0.8, bottom=-capital_dredging, label="Terminal Construction")

        bar3 = ax2.bar([x + 0.5 * width for x in years], - terminal_operations, width=width, color='darkcyan', alpha=1.0, bottom=None, label="Terminal Operations")
        bar4 = ax2.bar([x + 0.5 * width for x in years], - container_ships, width=width, color='darkcyan', alpha=0.8, bottom=opex_1, label="Container Ship Operations")
        bar5 = ax2.bar([x + 0.5 * width for x in years], - barges, width=width, color='darkcyan', alpha=0.6, bottom=opex_2, label="Barge Operations")
        bar6 = ax2.bar([x + 0.5 * width for x in years], - maintenance_dredging, width=width, color='darkcyan', alpha=0.4, bottom=opex_3, label="Maintenance Dredging")

        plot1, = ax2.step(years, costs, label="Annual Costs", where='mid', linestyle='-', color='tab:red', alpha=0.6, zorder=2)
        # plot2, = ax2.step(years, costs_cum, label="Cumulative Costs", where='mid', linestyle='-.', color='tab:red', alpha=0.8, zorder=3)
        # plot3 = ax2.axhline(y = costs_cum[len(costs_cum)-1], label="PV of the costs", color='tab:red', linestyle='--', alpha=1.0, zorder=4)

        ax2.set_xlabel('Years', fontsize='large')
        ax2.set_ylabel('Annual costs [USD]', fontsize='large')
        ax2.set_title('Capex and Opex plot', fontsize='large')

        ax2.set_yticks([0,-1000000,-2000000,-3000000,-4000000,-5000000,-6000000,-7000000,-8000000,-9000000,-10000000])
        ax2.set_yticklabels(["$ 0M","$ -1M","$ -2M","$ -3M","$ -4M", "$ -5M", "$-6M", "$-7M", "$-8M", "$-9M", "$-10M"])

        ax2.xaxis.tick_top()
        ax2.set_xticks([x for x in years])
        ax2.set_xticklabels(years)

        # first_leg = ax2.legend(handles=[plot1,plot2,plot3],
        #                         loc='upper right', bbox_to_anchor=(1.0, 0.35), fancybox=True, shadow=True, framealpha = 1.0, fontsize='large',
        #                         title="Cost-estimation",title_fontsize='large')
        first_leg = ax2.legend(handles=[plot1,],
                                loc='upper right', bbox_to_anchor=(1.0, 0.35), fancybox=True, shadow=True, framealpha = 1.0, fontsize='large',
                                title="Cost-estimation",title_fontsize='large')
        add_first_leg = plt.gca().add_artist(first_leg)

        second_leg = ax2.legend(handles=[bar1,bar2],
                                loc='upper right', bbox_to_anchor=(1.0, 0.8), fancybox=True, shadow=True, framealpha = 1.0, fontsize='large',
                                title="Capex",title_fontsize='large')
        add_second_leg = plt.gca().add_artist(second_leg)

        ax2.legend(handles=[bar3,bar4,bar5,bar6],
                   loc='upper right', bbox_to_anchor=(1.0, 0.625), fancybox=True, shadow=True, framealpha = 1.0, fontsize='large',
                   title="Opex", title_fontsize ='large')

        plt.setp(ax2.patches, linewidth=0)
        ax2.grid(False, which='major')
