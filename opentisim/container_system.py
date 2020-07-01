# package(s) for data handling
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


# opentisim package
from opentisim.container_objects import *
from opentisim import container_layout

from opentisim import container_defaults
from opentisim import core

class System:
    """This class implements the 'complete supply chain' concept (Van Koningsveld et al, 2020) for container terminals.

    The module allows variation of the type of quay crane used and the type of quay crane used and the type of stack
    equipment used.

    Terminal development is governed by the following triggers:
    - the allowable waiting time as a factor of service time at the berth, and
    - the distribution ratios (adding up to 1) for:
        - ladens
        - empties
        - reefers
        - out of gauges
    - the transhipment ratio
    """

    def __init__(self, terminal_name='Terminal', startyear=2019, lifecycle=20, operational_hours=(365-7)*24, debug=False,
                 elements=[],
                 crane_type_defaults=container_defaults.sts_crane_data,
                 stack_equipment='rs', laden_stack='rs',
                 allowable_waiting_service_time_ratio_berth=0.1, allowable_berth_occupancy=0.6, kendall='E2/E2/n',
                 laden_perc=0.80, reefer_perc=0.1, empty_perc=0.05, oog_perc=0.05,
                 laden_teu_factor=1.6, reefer_teu_factor=1.75, empty_teu_factor=1.55, oog_teu_factor=1.55,
                 import_perc=0.15, export_perc=0.16, transhipment_ratio=0.69,
                 teu_factor=1.6, peak_factor=1.3,
                 energy_price=0.17, fuel_price=1, land_price=0,
                 space_boundary = False, prim_yard_only = False, block_configuration = False, coords = []):
        # identity
        self.terminal_name = terminal_name

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
        self.stack_equipment = stack_equipment
        self.laden_stack = laden_stack

        # triggers for the various elements (berth, storage and station)
        self.allowable_waiting_service_time_ratio_berth = allowable_waiting_service_time_ratio_berth
        self.allowable_berth_occupancy = allowable_berth_occupancy
        self.kendall = kendall

        # container split
        self.laden_perc = laden_perc
        self.reefer_perc = reefer_perc
        self.empty_perc = empty_perc
        self.oog_perc = oog_perc
        self.laden_teu_factor = laden_teu_factor
        self.reefer_teu_factor = reefer_teu_factor
        self.empty_teu_factor = empty_teu_factor
        self.oog_teu_factor = oog_teu_factor

        # modal split
        self.import_perc = import_perc
        self.export_perc = export_perc
        self.transhipment_ratio = transhipment_ratio
        self.teu_factor = teu_factor
        self.peak_factor = peak_factor

        # fuel and electrical power price
        self.energy_price = energy_price
        self.fuel_price = fuel_price
        self.land_price = land_price

        # terminal space boundary and coordinates
        self.space_boundary = space_boundary
        self.prim_yard_only = prim_yard_only
        self.block_configuration = block_configuration
        self.coords = coords

        # storage variables for revenue
        # self.revenues = []

        # input testing: throughput type percentages should add up to 1
        np.testing.assert_equal(self.laden_perc + self.reefer_perc + self.empty_perc + self.oog_perc, 1,
                                'error: throughput type fractions should add up to 1')
        np.testing.assert_equal(self.import_perc + self.export_perc + self.transhipment_ratio, 1,
                                'error: import, export and transhipment should add up to 1')

    # *** Overall terminal investment strategy for terminal class.
    def simulate(self):
        """The 'simulate' method implements the terminal investment strategy for this terminal class.

        This method automatically generates investment decisions, parametrically derived from overall demand trends and
        a number of investment triggers.

        Generic approaches based on:
        - Quist, P. and Wijdeven, B., 2014. Ports & Terminals Hand-out. Chapter 7 Container terminals. CIE4330/CIE5306
        - PIANC. 2014. Master plans for the development of existing ports. MarCom - Report 158, PIANC
        - PIANC. 2014b. Design principles for small and medium marine containter terminals. MarCom - Report 135, PIANC
        - Van Koningsveld, M. (Ed.), Verheij, H., Taneja, P. and De Vriend, H.J. (2020). Ports and Waterways.
          Navigating the changing world. TU Delft, Delft, The Netherlands.
        - Van Koningsveld, M. and J. P. M. Mulder. 2004. Sustainable Coastal Policy Developments in the
          Netherlands. A Systematic Approach Revealed. Journal of Coastal Research 20(2), pp. 375-385

        Specific application based on (modifications have been applied where deemed an improvement):
        - Koster, P.H.F., 2019. Concept level container terminal design. Investigating the consequences of accelerating
          the concept design phase by modelling the automatable tasks. Master's thesis. Delft University of Technology,
          Netherlands. URL: http://resolver.tudelft.nl/uuid:131133bf-9021-4d67-afcb-233bd8302ce0.
        - Stam, H.W.B., 2020. Offshore-Onshore Port Systems. A framework for the financial evaluation of offshore
          container terminals. Master's thesis. Delft University of Technology, Netherlands.

        The simulate method applies frame of reference style decisions while stepping through each year of the terminal
        lifecycle and check if investment is needed (in light of strategic objective, operational objective,
        QSC, decision recipe, intervention method):

           1. for each year estimate the anticipated vessel arrivals based on the expected demand
           2. for each year evaluate which investment are needed given the strategic and operational objectives
           3. for each year calculate the energy costs (requires insight in realized demands)
           4. for each year calculate the demurrage costs (requires insight in realized demands)
           5. for each year calculate terminal revenues (requires insight in realized demands)
           6. collect all cash flows (capex, opex, [revenues])
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

            # Step 1: Estimate annual throughput
            commodities = core.find_elements(self, Commodity)
            for commodity in commodities:
                # The total amount of annualy transported TEU
                total_vol = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()

            if self.debug:
                print('--- Cargo volume for {} ------------------------'.format(year))
                print('  Total cargo volume: {}'.format(total_vol))
                print('----------------------------------------------------')

            # Step 2: Estimate fleet composition and number of trips
            fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls, post_panamax_II_calls, \
                new_panamax_calls, VLCS_calls, ULCS_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
            if self.debug:
                print('--- Vessel calls for {} ------------------------'.format(year))
                print('  Total vessel calls: {}'.format(total_calls))
                print('     Fully cellular calls: {}'.format(fully_cellular_calls))
                print('     Panamax calls: {}'.format(panamax_calls))
                print('     Panamax max calls: {}'.format(panamax_max_calls))
                print('     Post Panamax I calls: {}'.format(post_panamax_I_calls))
                print('     Post Panamax II calls: {}'.format(post_panamax_II_calls))
                print('     New Panamax calls: {}'.format(new_panamax_calls))
                print('     VLCS calls: {}'.format(VLCS_calls))
                print('     ULCS calls: {}'.format(ULCS_calls))
                print('----------------------------------------------------')

            # Step 3: Make cargo specification (integrated into the next steps

            # Step 4: Unloading equipment specification and berth configuration estimation
            self.berth_invest(year, fully_cellular_calls, panamax_calls, panamax_max_calls,
                              post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, VLCS_calls, ULCS_calls)

            # Step 5: Quay to storage (specification of apron & stack equipment)
            if self.debug:
                print('')
                print('$$$ Check horizontal transport (coupled with quay crane presence) -----------')
            self.horizontal_transport_invest(year)

            if self.debug:
                if self.space_boundary:
                    print('')
                    print('$$$ Check terminal layout, including laden and reefer stack investments (coupled with demand and coords) ------------------')

                    self.layout_generator(year)

                else:
                    print('')
                    print('$$$ Check laden stack investments (coupled with demand) ----------')
                    self.laden_stack_invest(year)

                    print('')
                    print('$$$ Check reefer stack investments (coupled with demand) ----------')
                    self.reefer_stack_invest(year)

            if self.debug:
                print('')
                print('$$$ Check empty stack investments (coupled with demand) ---------------------')
            self.empty_stack_invest(year)

            if self.debug:
                print('')
                print('$$$ Check oog stack investments (coupled with demand) -----------------------')
            self.oog_stack_invest(year)

            if self.debug:
                print('')
                print('$$$ Check stacking equipment investment (coupled with quay crane presence) --')
            self.stack_equipment_invest(year)

            if self.debug:
                print('')
                print('$$$ Check empty handlers (coupled with quay crane presence) -----------------')
            self.empty_handler_invest(year)

            # Step 6: Calculate storage area (nr of elements needed + surface area + roads)
            # if self.debug:
                # print('')
                # print('$$$ Check laden stack investments (coupled with demand) ----------')
            # self.laden_stack_invest(year)

            # Step 7: Storage to hinterland
            if self.debug:
                print('')
                print('$$$ Check gate investments (coupled with quay crane presence) ---------------')
            self.gate_invest(year)

        #     if self.debug:
        #         print('')
        #         print('$$$ Check general services --------------------------------------------------')
        #     self.general_services_invest(year)
        #
        # # 3. for each year calculate the general labour, fuel and energy costs (requires insight in realized demands)
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_energy_cost(year)
        #
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_general_labour_cost(year)
        #
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_fuel_cost(year)
        #
        # # 4. for each year calculate the demurrage costs (requires insight in realized demands)
        # self.demurrage = []
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_demurrage_cost(year)

        # Todo: see if here a method can be implemented to estimate the revenue that is needed to get NPV = 0
        # 5.  for each year calculate terminal revenues
        # self.revenues = []
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_revenue(year)

        # 6. collect all cash flows (capex, opex, revenues)
        # cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()

        # 7. calculate key numbers
        # Todo: check to see if core method can be used in stead
        # df = core.NPV(self, Labour(**container_defaults.labour_data))
        # print(df)
        # NPV, capex_normal, opex_normal, labour_normal = self.NPV()

        # 8. calculate land use
        total_land_use = self.calculate_land_use(year)

        # Todo: implement a return method for Simulate()
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
        #         "NPV": NPV}
        #
        # # Todo: check if this statement is indeed obsolete
        # # cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()
        #
        # # Todo: this return statement should be obsolete as everything is logged in the Terminal object
        # return NPV, data

    # *** Individual investment methods for terminal elements
    def berth_invest(self, year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II, new_panamax,
                     VLCS, ULCS):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and
        Mulder, 2004; Van Koningsveld et al., 2020) for the berth investments.

        Decision recipe Berth:
           QSC: berth_occupancy & allowable_waiting_service_time_ratio
           Benchmarking procedure: there is a problem if the estimated berth_occupancy triggers a waiting time over
           service time ratio that is larger than the allowed waiting time over service time ratio
              - allowable_waiting_service_time_ratio = .10 # 10% (see PIANC (2014, 2014b))
              - a berth needs:
                 - a quay
                 - cranes (min:1 and max: max_cranes)
              - berth occupancy depends on:
                 - total_calls, total_vol and time needed for mooring, unmooring
                 - total_service_capacity as delivered by the cranes
              - berth occupancy in combination with nr of berths is used to lookup the waiting over service time ratio
           Intervention procedure: invest enough to make the planned waiting service time ratio < allowable waiting
              service time ratio
              - adding berths, quays and cranes decreases berth_occupancy_rate (and increases the number of servers)
                which will yield a smaller waiting time over service time ratio
        """

        # report on the status of all berth elements
        if self.debug:
            print('')
            print('--- Status terminal @ start of year ----------------')

        core.report_element(self, Berth, year)
        core.report_element(self, Quay_wall, year)
        core.report_element(self, Cyclic_Unloader, year)

        # calculate planned berth occupancy and planned nr of berths
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
            self.calculate_berth_occupancy(year, fully_cellular, panamax, panamax_max, post_panamax_I, post_panamax_II,
                                           new_panamax, VLCS, ULCS)
        berths = len(core.find_elements(self, Berth))

        # get the waiting time as a factor of service time
        if berths != 0:
            planned_waiting_service_time_ratio_berth = core.occupancy_to_waitingfactor(
                utilisation=berth_occupancy_planned, nr_of_servers_to_chk=berths, kendall=self.kendall)
        else:
            planned_waiting_service_time_ratio_berth = np.inf

        if self.debug:
            print('     Berth occupancy planned (@ start of year): {:.2f} (trigger level: {:.2f})'.format(
                berth_occupancy_planned, self.allowable_berth_occupancy))
            print(
                '     Planned waiting time service time factor (@ start of year): {:.2f} (trigger level: {:.2f})'.format(
                    planned_waiting_service_time_ratio_berth, self.allowable_waiting_service_time_ratio_berth))

            print('')
            print('--- Start investment analysis ----------------------')
            print('')
            print('$$$ Check berth elements (coupled with berth occupancy) ---------------')

        core.report_element(self, Berth, year)
        core.report_element(self, Quay_wall, year)
        core.report_element(self, Cyclic_Unloader, year)

        # while planned_waiting_service_time_ratio is larger than self.allowable_waiting_service_time_ratio_berth
        # see also PIANC (2014b), p. 58/59
        while planned_waiting_service_time_ratio_berth > self.allowable_waiting_service_time_ratio_berth:

            # while planned waiting service time ratio is too large add a berth when no crane slots are available
            if not (self.check_crane_slot_available()):
                if self.debug:
                    print(' ')
                    print('  *** add Berth to elements')

                berth = Berth(**container_defaults.berth_data)
                berth.year_online = year + berth.delivery_time
                self.elements.append(berth)

            # while planned waiting service time ratio is too large add a berth if a quay is needed
            berths = len(core.find_elements(self, Berth))
            quay_walls = len(core.find_elements(self, Quay_wall))
            if berths > quay_walls:
                # bug fixed, should only take the value of the vessels that actually come
                Ls_max = max([
                    int(not container_defaults.container_data['fully_cellular_perc'] == 0) * container_defaults.fully_cellular_data["LOA"],
                    int(not container_defaults.container_data['panamax_perc'] == 0) * container_defaults.panamax_data["LOA"],
                    int(not container_defaults.container_data['panamax_max_perc'] == 0) * container_defaults.panamax_max_data["LOA"],
                    int(not container_defaults.container_data['post_panamax_I_perc'] == 0) * container_defaults.post_panamax_I_data["LOA"],
                    int(not container_defaults.container_data['post_panamax_II_perc'] == 0) * container_defaults.post_panamax_II_data["LOA"],
                    int(not container_defaults.container_data['new_panamax_perc'] == 0) * container_defaults.new_panamax_data["LOA"],
                    int(not container_defaults.container_data['VLCS_perc'] == 0) * container_defaults.VLCS_data["LOA"],
                    int(not container_defaults.container_data['ULCS_perc'] == 0) * container_defaults.ULCS_data["LOA"]
                    ])  # max length
                draught = max([
                    int(not container_defaults.container_data['fully_cellular_perc'] == 0) * container_defaults.fully_cellular_data["draught"],
                    int(not container_defaults.container_data['panamax_perc'] == 0) * container_defaults.panamax_data["draught"],
                    int(not container_defaults.container_data['panamax_max_perc'] == 0) * container_defaults.panamax_max_data["draught"],
                    int(not container_defaults.container_data['post_panamax_I_perc'] == 0) * container_defaults.post_panamax_I_data["draught"],
                    int(not container_defaults.container_data['post_panamax_II_perc'] == 0) * container_defaults.post_panamax_II_data["draught"],
                    int(not container_defaults.container_data['new_panamax_perc'] == 0) * container_defaults.new_panamax_data["draught"],
                    int(not container_defaults.container_data['VLCS_perc'] == 0) * container_defaults.VLCS_data["draught"],
                    int(not container_defaults.container_data['ULCS_perc'] == 0) * container_defaults.ULCS_data["draught"]
                    ])  # max draught

                Ls_avg = (fully_cellular * container_defaults.fully_cellular_data["LOA"] +
                          panamax * container_defaults.panamax_data["LOA"] +
                          panamax_max * container_defaults.panamax_max_data["LOA"] +
                          post_panamax_I * container_defaults.post_panamax_I_data["LOA"] +
                          post_panamax_II * container_defaults.post_panamax_II_data["LOA"] +
                          new_panamax * container_defaults.new_panamax_data["LOA"] +
                          VLCS * container_defaults.VLCS_data["LOA"] +
                          ULCS * container_defaults.ULCS_data["LOA"]) / \
                         (fully_cellular + panamax + panamax_max + post_panamax_I + post_panamax_II + new_panamax +
                          VLCS + ULCS)  # average length

                # NB: the implementation below takes the first quay to follow the n=1 rule from PIANC (2014), and the
                # next quays to follow the n>1 rule. Hence for each quay >1 we add 1.1 * (Ls_avg + berthing_gap)
                # This ensures that in the iteration 1 quay is still always large enough, and when we add another, it
                # follows the 1.1 * Lav rule. This might give a slight overestimation (!).

                # - length (apply PIANC 2014)
                berthing_gap = container_defaults.quay_wall_data["berthing_gap"]
                if quay_walls == 0:  # - length when next quay is n = 1
                    # Lq = Ls,max + (2 x 15) ref: PIANC 2014, p 98
                    length_calculated = Ls_max + 2 * berthing_gap
                else:  # - length when next quay is n > 1
                    # Lq = 1.1 x n x (Ls,avg+15) + 15 ref: PIANC 2014, p 98
                    # after the first quay, we add 1.1 * (Ls_avg + berthing_gap).
                    length_calculated = 1.1 * (Ls_avg + berthing_gap)

                if self.space_boundary:
                    # while planned quay wall length is smaller than available quay wall length
                    coords = self.coords
                    length_available = coords[(len(coords)) - 2][0] - coords[0][0]

                    length_berth = 0
                    for element in self.elements:
                        if isinstance(element, Quay_wall):
                            length_berth = length_berth + element.length

                    if length_berth + length_calculated <= length_available:
                        length = length_calculated
                    else:
                        print('*** The available quay length has reached the maximum ---------------')
                        length = 0
                else:
                    length = length_calculated
                    length_berth = None
                    length_available = None

                # - depth
                quay_wall = Quay_wall(**container_defaults.quay_wall_data)
                depth = np.sum([draught, quay_wall.max_sinkage, quay_wall.wave_motion, quay_wall.safety_margin])

                # add a quay to self.elements
                self.quay_invest(year, length, depth, length_berth, length_available)

            # while planned berth occupancy is too large add a crane if a crane is needed
            if self.check_crane_slot_available():
                self.crane_invest(year)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
                    self.calculate_berth_occupancy(year, fully_cellular, panamax, panamax_max, post_panamax_I,
                                                   post_panamax_II, new_panamax, VLCS, ULCS)
                planned_waiting_service_time_ratio_berth = core.occupancy_to_waitingfactor(
                    utilisation=berth_occupancy_planned, nr_of_servers_to_chk=berths)

                if self.debug:
                    print('     Berth occupancy planned (after adding crane): {:.2f} (trigger level: {:.2f})'.format(
                        berth_occupancy_planned, self.allowable_berth_occupancy))
                    print('     Planned waiting time service time factor : {:.2f} (trigger level: {:.2f})'.format(
                        planned_waiting_service_time_ratio_berth, self.allowable_waiting_service_time_ratio_berth))

    def quay_invest(self, year, length, depth, length_berth, length_available):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and
        Mulder, 2004; Van Koningsveld et al, 2020) for the quay investments.

        Decision recipe Quay:
           QSC: quay_per_berth
           Benchmarking procedure (triggered in self.berth_invest): there is a problem when
              the number of berths > the number of quays, but also while the planned waiting over service time ratio is
              too large
           Intervention procedure: invest enough to make sure that each quay has a berth and the planned waiting over
           service time ratio is below the max allowable waiting over service time ratio
              - adding quay will increase quay_per_berth
              - quay_wall.length must be long enough to accommodate largest expected vessel
              - quay_wall.depth must be deep enough to accommodate largest expected vessel
              - quay_wall.freeboard must be high enough to accommodate largest expected vessel
        """

        if self.debug:
            print('  *** add Quay to elements')
        # add a Quay_wall element
        quay_wall = Quay_wall(**container_defaults.quay_wall_data)

        # add length and depth to the elements (useful for later reporting)
        quay_wall.length = length
        quay_wall.depth = depth  # draught + max_sinkage + wave_motion + safety_margin
        quay_wall.retaining_height = 2 * (depth + quay_wall.freeboard)

        # - capex
        # Todo: check this unit rate estimate
        quay_wall.unit_rate = int(quay_wall.Gijt_constant * quay_wall.retaining_height ** quay_wall.Gijt_coefficient)
        mobilisation = int(max((length * quay_wall.unit_rate * quay_wall.mobilisation_perc), quay_wall.mobilisation_min))

        quay_wall.capex = int(length * quay_wall.unit_rate + mobilisation +  # costs related to the quay wall
                              length * quay_wall.apron_width * self.land_price)  # costs related to the apron area

        # - opex
        quay_wall.insurance = quay_wall.unit_rate * length * quay_wall.insurance_perc
        quay_wall.maintenance = quay_wall.unit_rate * length * quay_wall.maintenance_perc
        quay_wall.year_online = year + quay_wall.delivery_time

        # - land use
        quay_wall.land_use = length * quay_wall.apron_width

        # add cash flow information to quay_wall object in a dataframe
        quay_wall = core.add_cashflow_data_to_element(self, quay_wall)

        if self.space_boundary:
            if length_berth <= length_available:
                self.elements.append(quay_wall)
        else:
            self.elements.append(quay_wall)

    def crane_invest(self, year):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and
        Mulder, 2004) for the crane investments.

        Decision recipe Crane:
           QSC: planned waiting over service time ratio
           Benchmarking procedure (triggered in self.berth_invest): there is a problem when the planned planned
           waiting over service time ratio is larger than the max allowable waiting over service time ratio
           Intervention procedure: invest until planned waiting over service time ratio is below the max allowable
           waiting over service time ratio
        """

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
        crane.shift = crane.crew * labour.daily_shifts
        crane.labour = crane.shift * labour.blue_collar_salary
        # Todo: check if the number of shifts (crane.shift) is modelled correctly

        # apply proper timing for the crane to come online (in the same year as the latest Quay_wall)
        years_online = []
        for element in core.find_elements(self, Quay_wall):
            years_online.append(element.year_online)
        crane.year_online = max([year + crane.delivery_time, max(years_online)])

        # add cash flow information to quay_wall object in a dataframe
        crane = core.add_cashflow_data_to_element(self, crane)

        # add object to elements
        self.elements.append(crane)

    def horizontal_transport_invest(self, year):
        """current strategy is to add horizontal transport (tractors) as soon as a service trigger is achieved
        - find out how many cranes are online and planned
        - find out how many tractors trailers are online and planned (each STS needs a pre-set number of tractors trailers)
        - add tractor trailers until the required amount (given by the cranes) is achieved
        """

        # check the number of cranes
        cranes_planned = 0
        cranes_online = 0
        list_of_elements = core.find_elements(self, Cyclic_Unloader)
        if list_of_elements != []:
            for element in list_of_elements:
                cranes_planned += 1
                if year >= element.year_online:
                    cranes_online += 1

        # check the number of horizontal transporters
        hor_transport_planned = 0
        hor_transport_online = 0
        list_of_elements = core.find_elements(self, Horizontal_Transport)
        if list_of_elements != []:
            for element in list_of_elements:
                hor_transport_planned += 1
                if year >= element.year_online:
                    hor_transport_online += 1

        if self.debug:
            print('     Number of STS cranes planned (@ start of year): {}'.format(cranes_planned))
            print('     Horizontal transport planned (@ start of year): {}'.format(hor_transport_planned))

        # object needs to be instantiated here so that tractor.required may be determined
        tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)

        # when the total number of online horizontal transporters < total number of transporters required by the cranes
        while cranes_planned * tractor.required > hor_transport_planned:
            # add a tractor to elements
            if self.debug:
                print('  *** add tractor trailer to elements')
            tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)

            # - capex
            unit_rate = tractor.unit_rate
            mobilisation = tractor.mobilisation
            tractor.capex = int(unit_rate + mobilisation)

            # - opex
            # Todo: shouldn't the tractor also be insured?
            tractor.maintenance = unit_rate * tractor.maintenance_perc

            # - labour
            labour = Labour(**container_defaults.labour_data)
            # Todo: check if the number of shifts is calculated properly
            tractor.shift = tractor.crew * labour.daily_shifts
            tractor.labour = tractor.shift * labour.blue_collar_salary

            # apply proper timing for the crane to come online (in the same year as the latest Quay_wall)
            years_online = [element.year_online for element in core.find_elements(self, Cyclic_Unloader)]
            tractor.year_online = max([year + tractor.delivery_time, max(years_online)])

            # add cash flow information to tractor object in a dataframe
            tractor = core.add_cashflow_data_to_element(self, tractor)

            self.elements.append(tractor)

            hor_transport_planned += 1

            if self.debug:
                print('     a total of {} tractor trailers is online; {} tractor trailers still pending'.format(
                    hor_transport_online, hor_transport_planned - hor_transport_online))

    def laden_stack_invest(self, year):
        """current strategy is to add stacks as soon as trigger is achieved
              - find out how much stack capacity is planned
              - find out how much stack capacity is required
              - add stack capacity until service_trigger is no longer exceeded
        The laden stack has a number of positions for laden containers and a number of positions for reefer containers
        """

        stack_capacity_planned, stack_capacity_required, laden_ground_slots = self.laden_stack_capacity(year)

        if self.debug:
            print('     Laden stack capacity planned (@ start of year): {:.2f} teu'.format(stack_capacity_planned))
            print('     Laden stack capacity required (@ start of year): {:.2f} teu'.format(stack_capacity_required))

        # Required capacity should be ≤ Stack capacity planned.
        # While this is not the case, add stacks (PIANC (2014b), p63)
        while stack_capacity_required > stack_capacity_planned:
            if self.debug:
                print('  *** add laden stack to elements')

            laden = Container(**container_defaults.laden_container_data)
            if self.stack_equipment == 'rtg':  # Rubber Tired Gantry Crane
                stack = Laden_Stack(**container_defaults.rtg_stack_data)
            elif self.stack_equipment == 'rmg':  # Rail Mounted Gantry Crane
                stack = Laden_Stack(**container_defaults.rmg_stack_data)
            elif self.stack_equipment == 'sc':  # Straddle Carrier
                stack = Laden_Stack(**container_defaults.sc_stack_data)
            elif self.stack_equipment == 'rs':  # Reach Stacker
                stack = Laden_Stack(**container_defaults.rs_stack_data)
            else:  # Rubber Tired Gantry
                stack = Laden_Stack(**container_defaults.rtg_stack_data)
            stack.capacity = laden.width * laden.length * laden.height

            # - per stack that is added determine the land use
            # alternative calculation method (same result):
            #                 stack.length * stack.width * stack.gross_tgs * stack.area_factor
            #                     TEU      *     TEU     *  area per teu ground slot
            stack.land_use = (laden.width * laden.length) * stack.gross_tgs

            pavement = stack.pavement
            drainage = stack.drainage

            # - capex
            stack.capex = int(
                (stack.land_use + pavement + drainage) * self.land_price + stack.mobilisation)

            # - opex
            stack.maintenance = int((stack.land_use + pavement + drainage) * stack.maintenance_perc)

            # apply proper timing for the crane to come online
            # stack comes online in year + delivery time, or the same year as the last quay wall (whichever is largest)
            years_online = [element.year_online for element in core.find_elements(self, Quay_wall)]
            stack.year_online = max([year + stack.delivery_time, max(years_online)])

            # add cash flow information to quay_wall object in a dataframe
            stack = core.add_cashflow_data_to_element(self, stack)

            self.elements.append(stack)

            stack_capacity_planned, stack_capacity_required, laden_ground_slots = self.laden_stack_capacity(year)

        if self.debug:
            print('     Laden stack capacity planned (@ start of year): {:.2f}'.format(stack_capacity_planned))
            print('     Laden stack capacity required (@ start of year): {:.2f}'.format(stack_capacity_required))

    def laden_stack_capacity(self, year):

        # find the total planned laden stack capacity
        list_of_elements = core.find_elements(self, Laden_Stack)
        stack_capacity_planned = 0
        for element in list_of_elements:
            stack_capacity_planned += element.capacity

        laden_teu_ts, reefer_teu_ts, empty_teu_ts, oog_teu_ts,\
        laden_box_ts, reefer_box_ts, empty_box_ts, oog_box_ts = self.cargo_split_terminal_throughput(year)

        # instantiate laden, reefer and stack objects (needed to get properties)
        laden = Container(**container_defaults.laden_container_data)

        # calculate operational days
        operational_days = self.operational_hours / 24

        # determine the number of ground slots needed
        laden_ground_slots = np.ceil(((laden_teu_ts * laden.peak_factor * laden.dwell_time) /
                                      (laden.height * laden.stack_ratio * laden.stack_occupancy * operational_days)))

        print('laden_teu_ts: {}'.format(laden_teu_ts))
        print('laden.peak_factor: {}'.format(laden.peak_factor))
        print('laden.dwell_time: {}'.format(laden.dwell_time))
        print('laden.height: {}'.format(laden.height))
        print('laden.stack_ratio: {}'.format(laden.stack_ratio))
        print('laden.stack_occupancy: {}'.format(laden.stack_occupancy))
        print('operational_days: {}'.format(operational_days))

        print('laden_ground_slots: {}'.format(laden_ground_slots))
        # determine capacity needed (nr ground slots x height)
        stack_capacity_required = laden_ground_slots * laden.height

        return stack_capacity_planned, stack_capacity_required, laden_ground_slots

    def reefer_stack_invest(self, year):
        """current strategy is to add stacks as soon as trigger is achieved
              - find out how much stack capacity is planned
              - find out how much stack capacity is required
              - add stack capacity until service_trigger is no longer exceeded
        The laden stack has a number of positions for laden containers and a number of positions for reefer containers
        """

        stack_capacity_planned, stack_capacity_required, reefer_ground_slots = self.reefer_stack_capacity(year)

        if self.debug:
            print('     Reefer stack capacity planned (@ start of year): {:.2f} teu'.format(stack_capacity_planned))
            print('     Reefer stack capacity required (@ start of year): {:.2f} teu'.format(stack_capacity_required))

        # Required capacity should be ≤ Stack capacity planned.
        # While this is not the case, add stacks (PIANC (2014b), p63)
        while stack_capacity_required > stack_capacity_planned:
            if self.debug:
                print('  *** add reefer stack to elements')

            reefer = Container(**container_defaults.reefer_container_data)
            if self.stack_equipment == 'rtg':  # Rubber Tired Gantry Crane
                stack = Reefer_Stack(**container_defaults.rtg_stack_data)
            elif self.stack_equipment == 'rmg':  # Rail Mounted Gantry Crane
                stack = Reefer_Stack(**container_defaults.rmg_stack_data)
            elif self.stack_equipment == 'sc':  # Straddle Carrier
                stack = Reefer_Stack(**container_defaults.sc_stack_data)
            elif self.stack_equipment == 'rs':  # Reach Stacker
                stack = Reefer_Stack(**container_defaults.rs_stack_data)
            else:  # Rubber Tired Gantry
                stack = Reefer_Stack(**container_defaults.rtg_stack_data)
            stack.capacity = reefer.width * reefer.length * reefer.height

            # - per stack that is added determine the land use
            # alternative calculation method (same result):
            #                 stack.length * stack.width * stack.gross_tgs * stack.area_factor
            #                     TEU      *     TEU     *  area per teu ground slot
            stack.land_use = (reefer.width * reefer.length) * stack.gross_tgs

            pavement = stack.pavement
            drainage = stack.drainage

            # - capex
            stack.capex = int(
                (stack.land_use + pavement + drainage) * self.land_price + stack.mobilisation)

            # - opex
            stack.maintenance = int((stack.land_use + pavement + drainage) * stack.maintenance_perc)

            # apply proper timing for the crane to come online
            # stack comes online in year + delivery time, or the same year as the last quay wall (whichever is largest)
            years_online = [element.year_online for element in core.find_elements(self, Quay_wall)]
            stack.year_online = max([year + stack.delivery_time, max(years_online)])

            # add cash flow information to quay_wall object in a dataframe
            stack = core.add_cashflow_data_to_element(self, stack)

            self.elements.append(stack)

            stack_capacity_planned, stack_capacity_required, reefer_ground_slots = self.reefer_stack_capacity(year)

        if self.debug:
            print('     Reefer stack capacity planned (@ start of year): {:.2f}'.format(stack_capacity_planned))
            print('     Reefer stack capacity required (@ start of year): {:.2f}'.format(stack_capacity_required))

    def reefer_stack_capacity(self, year):

        # find the total planned laden stack capacity
        list_of_elements = core.find_elements(self, Reefer_Stack)
        stack_capacity_planned = 0
        for element in list_of_elements:
            stack_capacity_planned += element.capacity

        laden_teu_ts, reefer_teu_ts, empty_teu_ts, oog_teu_ts, \
        laden_box_ts, reefer_box_ts, empty_box_ts, oog_box_ts = self.cargo_split_terminal_throughput(year)

        # instantiate laden, reefer and stack objects (needed to get properties)
        reefer = Container(**container_defaults.reefer_container_data)

        # calculate operational days
        operational_days = self.operational_hours / 24

        # determine the number of ground slots needed
        reefer_ground_slots = np.ceil(((reefer_teu_ts * reefer.peak_factor * reefer.dwell_time) /
                                      (reefer.height * reefer.stack_ratio * reefer.stack_occupancy * operational_days)))

        # determine capacity needed (nr ground slots x height)
        stack_capacity_required = reefer_ground_slots * reefer.height

        return stack_capacity_planned, stack_capacity_required, reefer_ground_slots

    # *** Generating terminal layout
    def layout_generator(self, year):

        # specify the element to the terminal layout for each equipment
        if self.stack_equipment == 'rtg':  # Rubber Tired Gantry Crane
            terminal_layout = Terminal_Layout(**container_defaults.rtg_design_rules_data)
            terminal_layout.name = (container_defaults.terminal_layout_data["name"])
            terminal_layout.apron_width = (container_defaults.quay_wall_data["apron_width"])

            stack = Laden_Stack(**container_defaults.rtg_stack_data)
            terminal_layout.stack = stack
        elif self.stack_equipment == 'rmg':  # Rail Mounted Gantry Crane
            terminal_layout = Terminal_Layout(**container_defaults.rmg_design_rules_data)
            terminal_layout.name = (container_defaults.terminal_layout_data["name"])
            terminal_layout.apron_width = (container_defaults.quay_wall_data["apron_width"])

            stack = Laden_Stack(**container_defaults.rmg_stack_data)
            terminal_layout.stack = stack
        elif self.stack_equipment == 'sc':  # Straddle Carrier
            terminal_layout = Terminal_Layout(**container_defaults.sc_design_rules_data)
            terminal_layout.name = (container_defaults.terminal_layout_data["name"])
            terminal_layout.apron_width = (container_defaults.quay_wall_data["apron_width"])

            stack = Laden_Stack(**container_defaults.sc_stack_data)
            terminal_layout.stack = stack
        elif self.stack_equipment == 'rs':  # Reach Stacker
            terminal_layout = Terminal_Layout(**container_defaults.rs_design_rules_data)
            terminal_layout.name = (container_defaults.terminal_layout_data["name"])
            terminal_layout.apron_width = (container_defaults.quay_wall_data["apron_width"])

            stack = Laden_Stack(**container_defaults.rs_stack_data)
            terminal_layout.stack = stack

        # specify the laden containers properties
        laden = Container(**container_defaults.laden_container_data)

        # specify the year
        terminal_layout.year_online = year
        # specify the terminal shape and dimensions
        terminal_layout.coords = self.coords
        # specify the stack_equipment
        terminal_layout.stack_equipment = self.stack_equipment
        # specify the land price
        terminal_layout.land_price = self.land_price
        # specify the laden percentage
        terminal_layout.laden_perc = self.laden_perc
        # specify the reefer percentage
        terminal_layout.reefer_perc = self.reefer_perc

        # specify toggle
        # specify whether the tool will incluide primary yard only or not
        terminal_layout.prim_yard_only = self.prim_yard_only
        # specify whether the block configuration is determined (True) or it will determined by the boundary of the terminal
        terminal_layout.block_configuration = self.block_configuration

        # determine (and reset) the block_list and block_location_list
        list_of_terminal_layout = core.find_elements(self, Terminal_Layout)
        if list_of_terminal_layout != []:
            terminal_layout_ref = list_of_terminal_layout[len(list_of_terminal_layout) - 1]

            block_list = []
            terminal_layout.block_list = []
            for element in terminal_layout_ref.block_list:
                block_list.append(element)
            terminal_layout.block_list = block_list

            block_location_list = []
            terminal_layout.block_location_list = []
            for element in terminal_layout_ref.block_location_list:
                block_location_list.append(element)
            terminal_layout.block_location_list = block_location_list

        # specify the terminal TEU ground slots (TGS) demand and capacity planned
        laden_capacity_planned, laden_capacity_required, laden_ground_slots = self.laden_stack_capacity(year)
        reefer_capacity_planned, reefer_capacity_required, reefer_ground_slots = self.reefer_stack_capacity(year)

        total_ground_slots = laden_ground_slots + reefer_ground_slots
        total_capacity_planned = laden_capacity_planned + reefer_capacity_planned

        if self.debug:
            print('     Stack capacity planned (@ start of year): {:.2f}'.format(laden_capacity_planned))
            print('     Stack capacity required (@ start of year): {:.2f}'.format(laden_capacity_required))

        # add the tgs_demand to the yard layout element
        terminal_layout.tgs_demand = total_ground_slots
        # add the tgs_capacity to the yard layout element
        terminal_layout.tgs_capacity = total_capacity_planned / terminal_layout.stack.height

        if self.debug:
            # Creating the terminal area
            if self.stack_equipment == 'rtg':
                terminal_layout = container_layout.rtg_layout(laden, terminal_layout)
            if self.stack_equipment == 'rmg':
                terminal_layout = container_layout.rmg_layout(laden, terminal_layout)
            if self.stack_equipment == 'sc':
                terminal_layout = container_layout.sc_layout(laden, terminal_layout)
            if self.stack_equipment == 'rs':
                terminal_layout = container_layout.rs_layout(laden, terminal_layout)

        # add the new generated stack layout
        stack_layout_required = []
        stack_layout_planned = []

        for element in terminal_layout.block_list:
            if isinstance(element, Laden_Stack):
                stack_layout_required.append(element)

        stack_layout_planned = core.find_elements(self, Laden_Stack)

        stack_list = []
        stack_list = list(set(stack_layout_required) - set(stack_layout_planned))

        for element in stack_list:
            if isinstance(element, Laden_Stack):
                'Apply proper timing for the crane to come online'
                'stack comes online in year + delivery time, or the same year as the last quay wall (whichever is largest)'
                years_online = [element.year_online for element in core.find_elements(self, Quay_wall)]
                element.year_online = max([year + stack.delivery_time, max(years_online)])

                # add cash flow information to quay_wall object in a dataframe
                element = core.add_cashflow_data_to_element(self, element)

                'Add the stack to the Terminal elements'
                self.elements.append(element)

        if terminal_layout.available_space == False:
            print('     Container layout has reached its maximum capacity')
            print('     Container layout TGS capacity: {:.2f}'.format(terminal_layout.tgs_capacity))

        self.elements.append(terminal_layout)

    def empty_stack_invest(self, year):
        """current strategy is to add stacks as soon as trigger is achieved
             - find out how much stack capacity is online
             - find out how much stack capacity is planned
             - find out how much stack capacity is needed
             - add stack capacity until service_trigger is no longer exceeded
        """

        stack_capacity_planned, stack_capacity_required = self.empty_stack_capacity(year)

        if self.debug:
            print('     Empty stack capacity planned (@ start of year): {:.2f}'.format(stack_capacity_planned))
            print('     Empty stack capacity required (@ start of year): {:.2f}'.format(stack_capacity_required))

        while stack_capacity_required > stack_capacity_planned:
            if self.debug:
                print('  *** add empty stack to elements')

            empty = Container(**container_defaults.empty_container_data)
            stack = Empty_Stack(**container_defaults.empty_stack_data)
            stack.capacity = empty.width * empty.length * empty.height

            # - land use
            stack_ground_slots = empty.width * empty.length
            stack.land_use = stack_ground_slots * stack.gross_tgs * stack.area_factor

            # - capex
            area = stack.length * stack.width
            gross_tgs = stack.gross_tgs
            pavement = stack.pavement
            drainage = stack.drainage
            area_factor = stack.area_factor
            mobilisation = stack.mobilisation
            cost_of_land = self.land_price
            stack.capex = int(
                (pavement + drainage + cost_of_land) * gross_tgs * area * area_factor + mobilisation)

            # - opex
            stack.maintenance = int(
                (pavement + drainage) * gross_tgs * area * area_factor * stack.maintenance_perc)

            # apply proper timing for the crane to come online
            # stack comes online in year + delivery time, or the same year as the last quay wall (whichever is largest)
            years_online = [element.year_online for element in core.find_elements(self, Quay_wall)]
            stack.year_online = max([year + stack.delivery_time, max(years_online)])

            # add cash flow information to quay_wall object in a dataframe
            stack = core.add_cashflow_data_to_element(self, stack)

            self.elements.append(stack)

            stack_capacity_planned, stack_capacity_required = self.empty_stack_capacity(year)

        if self.debug:
            print('     Empty stack capacity planned (@ start of year): {:.2f}'.format(stack_capacity_planned))
            print('     Empty stack capacity required (@ start of year): {:.2f}'.format(stack_capacity_required))

    def empty_stack_capacity(self, year):
        """Calculate the stack capacity for empty containers"""

        # find the total stack capacity
        list_of_elements = core.find_elements(self, Empty_Stack)
        empty_capacity_planned = 0
        for element in list_of_elements:
            empty_capacity_planned += element.capacity

        # determine the on-terminal total TEU/year for every throughput type (types: ladens, reefers, empties, oogs)
        laden_teu_ts, reefer_teu_ts, empty_teu_ts, oog_teu_ts, \
        laden_box_ts, reefer_box_ts, empty_box_ts, oog_box_ts = self.cargo_split_terminal_throughput(year)

        # Transhipment containers are counted twice in berth throughput calculations – once off the ship and once on the
        # ship – but are counted only once in the yard capacity calculations. PIANC (2014b), p 63
        # total positions = half of the amount that it transhipped + the full amount of what is not transhipped

        # instantiate laden, reefer and stack objects
        empty = Container(**container_defaults.empty_container_data)

        # calculate operational days
        operational_days = self.operational_hours / 24

        # determine empty ground slots (see Quist and Wijdeven (2014) p. 49)
        #  throughput demand (corrected for ts) x peak factor x dwell times = total nr of containers to be stacked
        #  total nr of containers to be stacked divided by stack height times nr of operational days times stack
        #  occupancy increases nr of containers to be stacked and leads to the number of ground slots you need
        empty_ground_slots = np.ceil(((empty_teu_ts * empty.peak_factor * empty.dwell_time) /
                                     (empty.height * empty.stack_occupancy * operational_days)))

        empty_capacity_required = empty_ground_slots * empty.height

        return empty_capacity_planned, empty_capacity_required

    def oog_stack_invest(self, year):
        """Current strategy is to add stacks as soon as trigger is achieved
        - find out how much stack capacity is planned
        - find out how much stack capacity is needed
        - add stack capacity until service_trigger is no longer exceeded
        """

        oog_capacity_planned, oog_capacity_required = self.oog_stack_capacity(year)

        if self.debug:
            print('     OOG slots planned (@ start of year): {:.2f}'.format(oog_capacity_planned))
            print('     OOG slots required (@ start of year): {:.2f}'.format(oog_capacity_required))

        while oog_capacity_required > oog_capacity_planned:
            if self.debug:
                print('  *** add OOG stack to elements')

            oog = Container(**container_defaults.oog_container_data)
            stack = OOG_Stack(**container_defaults.oog_stack_data)
            stack.capacity = oog.width * oog.length * oog.height

            # - capex
            area = stack.length * stack.width
            gross_tgs = stack.gross_tgs
            pavement = stack.pavement
            drainage = stack.drainage
            area_factor = stack.area_factor
            mobilisation = stack.mobilisation
            cost_of_land = self.land_price
            stack.capex = int((pavement + drainage + cost_of_land) * gross_tgs * area * area_factor + mobilisation)

            # - opex
            stack.maintenance = int(
                (pavement + drainage) * gross_tgs * area * area_factor * stack.maintenance_perc)

            # - land use
            stack_ground_slots = oog.width * oog.length
            stack.land_use = stack_ground_slots * stack.gross_tgs

            # apply proper timing for the crane to come online
            # stack comes online in year + delivery time, or the same year as the last quay wall (whichever is largest)
            years_online = [element.year_online for element in core.find_elements(self, Quay_wall)]
            stack.year_online = max([year + stack.delivery_time, max(years_online)])

            # add cash flow information to quay_wall object in a dataframe
            stack = core.add_cashflow_data_to_element(self, stack)

            self.elements.append(stack)

            oog_capacity_planned, oog_capacity_required = self.oog_stack_capacity(year)

        if self.debug:
            print('     OOG slots planned (@ start of year): {:.2f}'.format(oog_capacity_planned))
            print('     OOG slots required (@ start of year): {:.2f}'.format(oog_capacity_required))

    def oog_stack_capacity(self, year):
        """Calculate the stack capacity for OOG containers"""

        # find the total stack capacity
        list_of_elements = core.find_elements(self, OOG_Stack)
        oog_capacity_planned = 0
        for element in list_of_elements:
            oog_capacity_planned += element.capacity

        # determine the on-terminal total TEU/year for every throughput type (types: ladens, reefers, empties, oogs)
        laden_teu_ts, reefer_teu_ts, empty_teu_ts, oog_teu_ts, \
        laden_box_ts, reefer_box_ts, empty_box_ts, oog_box_ts = self.cargo_split_terminal_throughput(year)

        # instantiate laden, reefer and stack objects
        oog = Container(**container_defaults.oog_container_data)

        # calculate operational days
        operational_days = self.operational_hours / 24

        # determine oog ground slots (see Quist and Wijdeven (2014) p. 49)
        #  throughput demand (corrected for ts) x peak factor x dwell times = total nr of containers to be stacked
        #  total nr of containers to be stacked divided by stack height times nr of operational days times stack
        #  occupancy increases nr of containers to be stacked and leads to the number of ground slots you need
        oog_ground_spots = np.ceil(((oog_teu_ts * oog.peak_factor * oog.dwell_time) /
                                   (oog.height * oog.stack_occupancy * operational_days)))

        oog_capacity_required = oog_ground_spots

        return oog_capacity_planned, oog_capacity_required

    def stack_equipment_invest(self, year):
        """current strategy is to add stack equipment as soon as a service trigger is achieved
        - find out how much stack equipment is online
        - find out how much stack equipment is planned
        - find out how much stack equipment is needed
        - add equipment until service_trigger is no longer exceeded
        """

        sts_cranes_online = 0
        sts_cranes_planned = 0
        stack_equipment_online = 0
        stack_equipment_planned = 0
        stacks_online = 0
        stacks_planned = 0
        for element in self.elements:
            if isinstance(element, Cyclic_Unloader):
                sts_cranes_planned += 1
                if year >= element.year_online:
                    sts_cranes_online += 1
            if isinstance(element, Stack_Equipment):
                stack_equipment_planned += 1
                if year >= element.year_online:
                    stack_equipment_online += 1
            if isinstance(element, Laden_Stack):
                stacks_planned += 1
                if year >= element.year_online:
                    stacks_online += 1

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

        # the rtg, sc and rs are coupled with the STS cranes, the rmg with the stack
        if (self.stack_equipment == 'rtg' or
                self.stack_equipment == 'sc' or
                self.stack_equipment == 'rs'):
            governing_object = sts_cranes_planned
        elif self.stack_equipment == 'rmg':
            governing_object = stacks_planned

        while governing_object * stack_equipment.required > stack_equipment_planned:

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
            stack_equipment.shift = stack_equipment.crew * labour.daily_shifts
            stack_equipment.labour = stack_equipment.shift * labour.blue_collar_salary

            # apply proper timing for the crane to come online
            # year + delivery time or in the year as the last laden stack
            years_online = []
            for element in core.find_elements(self, Laden_Stack):
                years_online.append(element.year_online)

            stack_equipment.year_online = max([year + stack_equipment.delivery_time, max(years_online)])

            # add cash flow information to tractor object in a dataframe
            stack_equipment = core.add_cashflow_data_to_element(self, stack_equipment)

            self.elements.append(stack_equipment)

            # add one to planned stack equipment (important for while loop)
            stack_equipment_planned += 1

            if self.debug:
                print('     a total of {} stack equipment is online; {} stack equipment still pending'.format(
                    stack_equipment_online, stack_equipment_planned - stack_equipment_online))

    def empty_handler_invest(self, year):
        """current strategy is to add empty hanlders as soon as a service trigger is achieved
        - find out how many empty handlers are online
        - find out how many empty handlers areplanned
        - find out how many empty handlers are needed
        - add empty handlers until service_trigger is no longer exceeded
        """
        sts_cranes_planned = len(core.find_elements(self, Cyclic_Unloader))

        empty_handlers_planned = 0
        empty_handlers_online = 0
        for element in self.elements:
            if isinstance(element, Empty_Handler):
                empty_handlers_planned += 1
                if year >= element.year_online:
                    empty_handlers_online += 1

        if self.debug:
            print('     Empty handlers planned (@ start of year): {}'.format(empty_handlers_planned))

        # object needs to be instantiated here so that empty_handler.required may be determined
        empty_handler = Empty_Handler(**container_defaults.empty_handler_data)
        while sts_cranes_planned * empty_handler.required > empty_handlers_planned:
            # add a tractor when not enough to serve number of STS cranes
            if self.debug:
                print('  *** add empty handler to elements')

            # - capex
            unit_rate = empty_handler.unit_rate
            mobilisation = empty_handler.mobilisation
            empty_handler.capex = int(unit_rate + mobilisation)

            # - opex
            empty_handler.maintenance = unit_rate * empty_handler.maintenance_perc

            #   labour
            labour = Labour(**container_defaults.labour_data)
            empty_handler.shift = empty_handler.crew * labour.daily_shifts
            empty_handler.labour = empty_handler.shift * labour.blue_collar_salary

            # apply proper timing for the empty handler to come online
            # year + empty_handler.delivery_time or last Empty_Stack, which ever is largest
            years_online = []
            for element in core.find_elements(self, Empty_Stack):
                years_online.append(element.year_online)

            empty_handler.year_online = max([year + empty_handler.delivery_time, max(years_online)])

            # add cash flow information to tractor object in a dataframe
            empty_handler = core.add_cashflow_data_to_element(self, empty_handler)

            self.elements.append(empty_handler)

            empty_handlers_planned += 1

            if self.debug:
                print('     a total of {} empty handlers is online; {} empty handlers still pending'.format(
                    empty_handlers_online, empty_handlers_planned - empty_handlers_online))

    def gate_invest(self, year):
        """current strategy is to add gates as soon as trigger is achieved
              - find out how much gate capacity is online
              - find out how much gate capacity is planned
              - find out how much gate capacity is needed
              - add gate capacity until service_trigger is no longer exceeded
              """

        # Calculate the cargo split over the quay
        commodities = core.find_elements(self, Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        import_teu = volume * self.import_perc
        export_teu = volume * self.export_perc

        import_box_moves = import_teu / self.teu_factor
        export_box_moves = export_teu / self.teu_factor

        gate = Gate(**container_defaults.gate_data)

        # operational weeks per year
        weeks_year = self.operational_hours/(gate.operating_days*24)

        # find installed gates
        exit_gate_minutes_planned = 0
        entry_gate_minutes_planned = 0
        gates = core.find_elements(self, Gate)
        for gate in gates:
            if gate.type == 'exit':
                exit_gate_minutes_planned += gate.capacity
            elif gate.type == 'entry':
                entry_gate_minutes_planned += gate.capacity

        # calculate exit gate minutes
        exit_gate_minutes_required = import_box_moves * (gate.truck_moves / weeks_year) *\
            gate.peak_factor * gate.peak_day * gate.peak_hour * gate.exit_inspection_time * gate.design_capacity
        print('exit_gate_minutes_required {:.2f}'.format(exit_gate_minutes_required))
        while exit_gate_minutes_required > exit_gate_minutes_planned:
            if self.debug:
                print('  *** add exit gate to elements')

            gate = Gate(**container_defaults.gate_data)
            gate.type = 'exit'

            # - land use
            gate.land_use = gate.area

            # - capex
            unit_rate = gate.unit_rate
            mobilisation = gate.mobilisation
            canopy = gate.canopy_costs * gate.area
            gate.capex = int(unit_rate + mobilisation + canopy + (gate.area * self.land_price))

            # - opex
            gate.maintenance = unit_rate * gate.maintenance_perc

            #   labour
            labour = Labour(**container_defaults.labour_data)
            gate.shift = gate.crew * labour.daily_shifts
            gate.labour = gate.shift * labour.blue_collar_salary

            if year == self.startyear:
                gate.year_online = year + gate.delivery_time + 1
            else:
                gate.year_online = year + gate.delivery_time

            # add cash flow information to tractor object in a dataframe
            gate = core.add_cashflow_data_to_element(self, gate)

            self.elements.append(gate)

            exit_gate_minutes_planned += gate.capacity
        print('exit_gate_minutes_planned {:.2f}'.format(exit_gate_minutes_planned))
        print('')

        # calculate entry gate minutes
        entry_gate_minutes_required = export_box_moves * (gate.truck_moves / weeks_year) *  \
            gate.peak_factor * gate.peak_day * gate.peak_hour * gate.entry_inspection_time * gate.design_capacity
        print('entry_gate_minutes_required {:.2f}'.format(entry_gate_minutes_required))
        while entry_gate_minutes_required > entry_gate_minutes_planned:
            if self.debug:
                print('  *** add entry gate to elements')

            gate = Gate(**container_defaults.gate_data)
            gate.type = 'entry'

            # - land use
            gate.land_use = gate.area

            # - capex
            unit_rate = gate.unit_rate
            mobilisation = gate.mobilisation
            canopy = gate.canopy_costs * gate.area
            gate.capex = int(unit_rate + mobilisation + canopy + (gate.area * self.land_price))

            # - opex
            gate.maintenance = unit_rate * gate.maintenance_perc

            #   labour
            labour = Labour(**container_defaults.labour_data)
            gate.shift = gate.crew * labour.daily_shifts
            gate.labour = gate.shift * labour.blue_collar_salary

            if year == self.startyear:
                gate.year_online = year + gate.delivery_time + 1
            else:
                gate.year_online = year + gate.delivery_time

            # add cash flow information to tractor object in a dataframe
            gate = core.add_cashflow_data_to_element(self, gate)

            self.elements.append(gate)

            entry_gate_minutes_planned += gate.capacity
        print('entry_gate_minutes_planned {:.2f}'.format(entry_gate_minutes_planned))

    def general_services_invest(self, year):

        laden_teu, reefer_teu, empty_teu, oog_teu, \
        laden_box, reefer_box, empty_box, oog_box = self.cargo_split_quay_throughput(year)

        cranes = 0
        general = 0
        for element in self.elements:
            if isinstance(element, Cyclic_Unloader):
                if year >= element.year_online:
                    cranes += 1
            if isinstance(element, General_Services):
                if year >= element.year_online:
                    general += 1

        general = General_Services(**container_defaults.general_services_data)

        quay_land_use = 0
        stack_land_use = 0
        empty_land_use = 0
        oog_land_use = 0
        gate_land_use = 0

        for element in self.elements:
            if isinstance(element, Quay_wall):
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

        total_land_use = \
            (quay_land_use + stack_land_use + empty_land_use + oog_land_use + gate_land_use + general.office +
             general.workshop + general.scanning_inspection_area + general.repair_building) * 0.0001

        if year == (self.startyear + 1):
            # add general services as soon as berth  is online
            if self.debug:
                print('  *** add general services to elements')

            # land use
            general.land_use = general.office + general.workshop + general.scanning_inspection_area \
                               + general.repair_building

            # - capex
            area = general.office + general.workshop + general.scanning_inspection_area \
                   + general.repair_building
            cost_of_land = self.land_price
            office = general.office * general.office_cost
            workshop = general.workshop * general.workshop_cost
            inspection = general.scanning_inspection_area * general.scanning_inspection_area_cost
            light = general.lighting_mast_cost * (total_land_use / general.lighting_mast_required)
            repair = general.repair_building * general.repair_building_cost
            basic = general.fuel_station_cost + general.firefight_cost + general.maintenance_tools_cost \
                    + general.terminal_operating_software_cost + general.electrical_station_cost
            general.capex = office + workshop + inspection + light + repair + basic + (area * cost_of_land)

            # - opex
            general.maintenance = general.capex * general.general_maintenance

            if year == self.startyear:
                general.year_online = year + general.delivery_time
            else:
                general.year_online = year + general.delivery_time

            # add cash flow information to tractor object in a dataframe
            general = core.add_cashflow_data_to_element(self, general)

            self.elements.append(general)

    # Todo: include CFS (container freight station)

    # *** Various cost calculation methods
    def calculate_energy_cost(self, year):
        """
        # todo voeg energy toe voor nieuwe elementen
        """

        sts_moves, tractor_moves, empty_moves, stack_moves = self.box_moves(year)
        energy_price = self.energy_price

        # STS crane energy costs
        cranes = 0
        for element in self.elements:
            if isinstance(element, Cyclic_Unloader):
                if year >= element.year_online:
                    cranes += 1

        for element in core.find_elements(self, Cyclic_Unloader):
            if year >= element.year_online:
                sts_moves_per_element = sts_moves / cranes
                if element.consumption * sts_moves_per_element * energy_price != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = \
                        element.consumption * sts_moves_per_element * energy_price
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # calculate stack equipment energy costs
        if self.stack_equipment == 'rmg':
            list_of_elements_Stack = core.find_elements(self, Stack_Equipment)
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

        # reefer energy costs
        stack_capacity_planned, total_capacity_required, reefer_ground_slots = self.laden_reefer_stack_capacity(year)

        stacks = 0
        for element in self.elements:
            if isinstance(element, Laden_Stack):
                if year >= element.year_online:
                    stacks += 1

        for element in core.find_elements(self, Laden_Stack):
            if year >= element.year_online:
                slots_per_stack = reefer_ground_slots / stacks
                if slots_per_stack * element.reefers_present * energy_price * 24 * 365 != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = slots_per_stack * element.reefers_present \
                                                                           * energy_price * 24 * 365
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        # Calculate general power use
        general = General_Services(**container_defaults.general_services_data)

        # - lighting
        quay_land_use = 0
        stack_land_use = 0
        empty_land_use = 0
        oog_land_use = 0
        gate_land_use = 0
        general_land_use = 0

        for element in self.elements:
            if isinstance(element, Quay_wall):
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

        # - office, gates, workshops power use
        general_consumption = general.general_consumption * energy_price * self.operational_hours
        for element in core.find_elements(self, General_Services):
            if year >= element.year_online:
                if lighting + general_consumption != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = lighting + general_consumption
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

    def calculate_general_labour_cost(self, year):
        """General labour"""

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
            white_collar = crew_required * labour.daily_shifts * (general.operations) * labour.white_collar_salary
            blue_collar = crew_required * labour.daily_shifts * (
                    general.engineering + general.security) * labour.blue_collar_salary

            shift_labour = white_collar + blue_collar

            # total labour
            list_of_elements_general = core.find_elements(self, General_Services)

            for element in list_of_elements_general:
                if year >= element.year_online:
                    if fixed_labour + shift_labour != np.inf:
                        element.df.loc[element.df['year'] == year, 'labour'] = fixed_labour + shift_labour
                else:
                    element.df.loc[element.df['year'] == year, 'labour'] = 0

    def calculate_fuel_cost(self, year):
        """Fuel cost"""
        sts_moves, tractor_moves, empty_moves, stack_moves = self.box_moves(year)
        fuel_price = self.fuel_price

        # calculate empty handler fuel costs
        list_of_elements_ech = core.find_elements(self, Empty_Handler)
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
            list_of_elements_Stack = core.find_elements(self, Stack_Equipment)
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
        list_of_elements_Tractor = core.find_elements(self, Horizontal_Transport)

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

        fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls, post_panamax_II_calls, \
            new_panamax_calls, VLCS_calls, ULCS_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
            self.calculate_berth_occupancy(year, fully_cellular_calls, panamax_calls, panamax_max_calls,
                                           post_panamax_I_calls, post_panamax_II_calls,
                                           new_panamax_calls, VLCS_calls, ULCS_calls)

        berths = len(core.find_elements(self, Berth))

        waiting_factor = \
            core.occupancy_to_waitingfactor(utilisation=berth_occupancy_online, nr_of_servers_to_chk=berths)

        waiting_time_hours = waiting_factor * crane_occupancy_online * self.operational_hours / total_calls
        waiting_time_occupancy = waiting_time_hours * total_calls / self.operational_hours

        # Find the service_rate per quay_wall to find the average service hours at the quay for a vessel
        quay_walls = len(core.find_elements(self, Quay_wall))

        service_rate = 0
        for element in (core.find_elements(self, Cyclic_Unloader)):
            if year >= element.year_online:
                service_rate += element.effective_capacity / quay_walls

        # Find the demurrage cost per type of vessel
        if service_rate != 0:
            fully_cellular = Vessel(**container_defaults.fully_cellular_data)
            service_time_fully_cellular = fully_cellular.call_size / service_rate
            waiting_time_hours_fully_cellular = waiting_factor * service_time_fully_cellular
            port_time_fully_cellular = waiting_time_hours_fully_cellular + service_time_fully_cellular + fully_cellular.mooring_time
            penalty_time_fully_cellular = max(0, port_time_fully_cellular - fully_cellular.all_turn_time)
            demurrage_time_fully_cellular = penalty_time_fully_cellular * fully_cellular_calls
            demurrage_cost_fully_cellular = demurrage_time_fully_cellular * fully_cellular.demurrage_rate

            panamax = Vessel(**container_defaults.panamax_data)
            service_time_panamax = panamax.call_size / service_rate
            waiting_time_hours_panamax = waiting_factor * service_time_panamax
            port_time_panamax = waiting_time_hours_panamax + service_time_panamax + panamax.mooring_time
            penalty_time_panamax = max(0, port_time_panamax - panamax.all_turn_time)
            demurrage_time_panamax = penalty_time_panamax * panamax_calls
            demurrage_cost_panamax = demurrage_time_panamax * panamax.demurrage_rate

            panamax_max = Vessel(**container_defaults.panamax_max_data)
            service_time_panamax_max = panamax_max.call_size / service_rate
            waiting_time_hours_panamax_max = waiting_factor * service_time_panamax_max
            port_time_panamax_max = waiting_time_hours_panamax_max + service_time_panamax_max + panamax_max.mooring_time
            penalty_time_panamax_max = max(0, port_time_panamax_max - panamax_max.all_turn_time)
            demurrage_time_panamax_max = penalty_time_panamax_max * panamax_max_calls
            demurrage_cost_panamax_max = demurrage_time_panamax_max * panamax_max.demurrage_rate

            post_panamax_I = Vessel(**container_defaults.post_panamax_I_data)
            service_time_post_panamax_I = post_panamax_I.call_size / service_rate
            waiting_time_hours_post_panamax_I = waiting_factor * service_time_post_panamax_I
            port_time_post_panamax_I = waiting_time_hours_post_panamax_I + service_time_post_panamax_I + post_panamax_I.mooring_time
            penalty_time_post_panamax_I = max(0, port_time_post_panamax_I - post_panamax_I.all_turn_time)
            demurrage_time_post_panamax_I = penalty_time_post_panamax_I * post_panamax_I_calls
            demurrage_cost_post_panamax_I = demurrage_time_post_panamax_I * post_panamax_I.demurrage_rate

            post_panamax_II = Vessel(**container_defaults.post_panamax_II_data)
            service_time_post_panamax_II = post_panamax_II.call_size / service_rate
            waiting_time_hours_post_panamax_II = waiting_factor * service_time_post_panamax_II
            port_time_post_panamax_II = waiting_time_hours_post_panamax_II + service_time_post_panamax_II + post_panamax_II.mooring_time
            penalty_time_post_panamax_II = max(0, port_time_post_panamax_II - post_panamax_II.all_turn_time)
            demurrage_time_post_panamax_II = penalty_time_post_panamax_II * post_panamax_II_calls
            demurrage_cost_post_panamax_II = demurrage_time_post_panamax_II * post_panamax_II.demurrage_rate

            new_panamax = Vessel(**container_defaults.new_panamax_data)
            service_time_new_panamax = new_panamax.call_size / service_rate
            waiting_time_hours_new_panamax = waiting_factor * service_time_new_panamax
            port_time_new_panamax = waiting_time_hours_new_panamax + service_time_new_panamax + new_panamax.mooring_time
            penalty_time_new_panamax = max(0, port_time_new_panamax - new_panamax.all_turn_time)
            demurrage_time_new_panamax = penalty_time_new_panamax * new_panamax_calls
            demurrage_cost_new_panamax = demurrage_time_new_panamax * new_panamax.demurrage_rate

            VLCS = Vessel(**container_defaults.VLCS_data)
            service_time_VLCS = VLCS.call_size / service_rate
            waiting_time_hours_VLCS = waiting_factor * service_time_VLCS
            port_time_VLCS = waiting_time_hours_VLCS + service_time_VLCS + VLCS.mooring_time
            penalty_time_VLCS = max(0, port_time_VLCS - VLCS.all_turn_time)
            demurrage_time_VLCS = penalty_time_VLCS * VLCS_calls
            demurrage_cost_VLCS = demurrage_time_VLCS * VLCS.demurrage_rate

            ULCS = Vessel(**container_defaults.ULCS_data)
            service_time_ULCS = ULCS.call_size / service_rate
            waiting_time_hours_ULCS = waiting_factor * service_time_ULCS
            port_time_ULCS = waiting_time_hours_ULCS + service_time_ULCS + ULCS.mooring_time
            penalty_time_ULCS = max(0, port_time_ULCS - ULCS.all_turn_time)
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
                               demurrage_cost_post_panamax_I + demurrage_cost_post_panamax_II + \
                               demurrage_cost_new_panamax + demurrage_cost_VLCS + demurrage_cost_ULCS

        self.demurrage.append(total_demurrage_cost)

    def calculate_indirect_costs(self):
        """Indirect costs are a function of overall CAPEX."""
        # Todo: check why this is not done per year
        indirect = Indirect_Costs(**container_defaults.indirect_costs_data)

        # collect CAPEX from terminal elements
        cash_flows, cash_flows_WACC_real = core.add_cashflow_elements(self, Labour(**container_defaults.labour_data))
        capex = cash_flows['capex'].values

        # add indirect costs for different stack equipment:
        #  - electrical work, miscellaneous, preliminaries and engineering
        if self.stack_equipment == 'rtg' or self.stack_equipment == 'rs' or self.stack_equipment == 'sc':
            electrical_works = indirect.electrical_works_fuel_terminal * capex
        elif self.stack_equipment == 'rmg' or self.stack_equipment == 'ertg':
            electrical_works = indirect.electrical_works_power_terminal * capex
        miscellaneous = indirect.miscellaneous * capex
        preliminaries = indirect.preliminaries * capex
        engineering = indirect.engineering * capex

        indirect_costs = capex + electrical_works + miscellaneous + preliminaries + engineering
        print(indirect_costs)

        cash_flows['capex'].values = indirect_costs

    # *** General functions
    def calculate_vessel_calls(self, year):
        """Calculate volumes to be transported and the number of vessel calls (both per vessel type and in total) """

        # intialize values to be returned
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
        commodities = core.find_elements(self, Commodity)
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
        vessels = core.find_elements(self, Vessel)
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

        total_calls = np.sum([fully_cellular_calls, panamax_calls, panamax_max_calls,
                              post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls,
                              VLCS_calls, ULCS_calls])

        return fully_cellular_calls, panamax_calls, panamax_max_calls, \
               post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls, \
               VLCS_calls, ULCS_calls, \
               total_calls, total_vol

    def calculate_berth_occupancy(self, year, fully_cellular_calls, panamax_calls, panamax_max_calls,
                                  post_panamax_I_calls, post_panamax_II_calls, new_panamax_calls,
                                  VLCS_calls, ULCS_calls):
        """
        - Find all cranes and sum their effective_capacity to get service_capacity
        - Divide callsize_per_vessel by service_capacity and add mooring time to get total time at berth
        - Occupancy is total_time_at_berth divided by operational hours
        """

        # intialize values to be returned
        total_vol = 0

        # gather volumes from each commodity scenario
        commodities = core.find_elements(self, Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                total_vol += volume
            except:
                pass

        # list all crane objects in the system
        list_of_elements_cranes = core.find_elements(self, Cyclic_Unloader)
        list_of_elements_berths = core.find_elements(self, Berth)
        # Todo: check if nr_berths is important to include or not
        nr_berths = len(list_of_elements_berths)

        # find the total service rate and determine the time at berth (in hours, per vessel type and in total)
        # Todo: calculation of effective capacity is done in container_mixins (now changed here to cycles*capacity)
        service_rate_planned = 0
        service_rate_online = 0
        if list_of_elements_cranes != []:
            for element in list_of_elements_cranes:
                service_rate_planned += element.hourly_cycles * element.lifting_capacity
                if year >= element.year_online:
                    service_rate_online += element.hourly_cycles * element.lifting_capacity


            # time at berth per vessel type
            time_mooring_unmooring_fully_cellular = fully_cellular_calls * \
                container_defaults.fully_cellular_data["mooring_time"]
            time_mooring_unmooring_panamax = panamax_calls * \
                container_defaults.panamax_data["mooring_time"]
            time_mooring_unmooring_panamax_max = panamax_max_calls * \
                container_defaults.panamax_max_data["mooring_time"]
            time_mooring_unmooring_post_panamax_I = post_panamax_I_calls * \
                container_defaults.post_panamax_I_data["mooring_time"]
            time_mooring_unmooring_post_panamax_II = post_panamax_II_calls * \
                container_defaults.post_panamax_II_data["mooring_time"]
            time_mooring_unmooring_new_panamax = new_panamax_calls * \
                container_defaults.new_panamax_data["mooring_time"]
            time_mooring_unmooring_VLCS = VLCS_calls * \
                container_defaults.VLCS_data["mooring_time"]
            time_mooring_unmooring_ULCS = ULCS_calls * \
                container_defaults.ULCS_data["mooring_time"]

            # total time at berth
            total_time_mooring_unmooring_planned = np.sum(
                [time_mooring_unmooring_fully_cellular,
                 time_mooring_unmooring_panamax,
                 time_mooring_unmooring_panamax_max,
                 time_mooring_unmooring_post_panamax_I,
                 time_mooring_unmooring_post_panamax_II,
                 time_mooring_unmooring_new_panamax,
                 time_mooring_unmooring_VLCS,
                 time_mooring_unmooring_ULCS])
            # print('total_time_mooring_unmooring_planned: {}'.format(total_time_mooring_unmooring_planned))

            # total boxes to move over the quay
            # total_boxes = np.ceil(total_vol * self.laden_perc / self.laden_teu_factor +\
            #               total_vol * self.reefer_perc / self.reefer_teu_factor +\
            #               total_vol * self.empty_perc / self.empty_teu_factor +\
            #               total_vol * self.oog_perc / self.oog_teu_factor)

            total_boxes = np.ceil(total_vol / self.teu_factor)

            # total time at cranes
            total_time_at_cranes_planned = (total_boxes * self.peak_factor) / service_rate_planned
            # print('total_boxes: {}'.format(total_boxes))
            # print('peak_factor: {}'.format(self.peak_factor))
            # print('service_rate_planned: {}'.format(service_rate_planned))
            # print('total_time_at_cranes_planned: {}'.format(total_time_at_cranes_planned))

            # total time at berth
            total_time_at_berth_planned = total_time_mooring_unmooring_planned + total_time_at_cranes_planned
            # print('total_time_at_berth_planned: {}'.format(total_time_at_berth_planned))

            # occupancy is the total time at berth divided by the operational hours
            crane_occupancy_planned = total_time_at_cranes_planned / self.operational_hours
            berth_occupancy_planned = total_time_at_berth_planned / self.operational_hours

            # Todo: update this (now only updated for planned)
            if service_rate_online != 0:  # when some cranes are actually online

                time_at_cranes_online_fully_cellular = fully_cellular_calls * \
                    (container_defaults.fully_cellular_data["call_size"] / service_rate_online)
                time_at_cranes_online_panamax = panamax_calls * \
                    (container_defaults.panamax_data["call_size"] / service_rate_online)
                time_at_cranes_online_panamax_max = panamax_max_calls * \
                    (container_defaults.panamax_max_data["call_size"] / service_rate_online)
                time_at_cranes_online_post_panamax_I = post_panamax_I_calls * \
                    (container_defaults.post_panamax_I_data["call_size"] / service_rate_online)
                time_at_cranes_online_post_panamax_II = post_panamax_II_calls * \
                    (container_defaults.post_panamax_II_data["call_size"] / service_rate_online)
                time_at_cranes_online_new_panamax = new_panamax_calls * \
                    (container_defaults.new_panamax_data["call_size"] / service_rate_online)
                time_at_cranes_online_VLCS = VLCS_calls * \
                    (container_defaults.VLCS_data["call_size"] / service_rate_online)
                time_at_cranes_online_ULCS = ULCS_calls * \
                    (container_defaults.ULCS_data["call_size"] / service_rate_online)

                total_time_at_berth_online = np.sum(
                    [time_mooring_unmooring_fully_cellular + time_at_cranes_online_fully_cellular,
                     time_mooring_unmooring_panamax + time_at_cranes_online_panamax,
                     time_mooring_unmooring_panamax_max + time_at_cranes_online_panamax_max,
                     time_mooring_unmooring_post_panamax_I + time_at_cranes_online_post_panamax_I,
                     time_mooring_unmooring_post_panamax_II + time_at_cranes_online_post_panamax_II,
                     time_mooring_unmooring_new_panamax + time_at_cranes_online_new_panamax,
                     time_mooring_unmooring_VLCS + time_at_cranes_online_VLCS,
                     time_mooring_unmooring_ULCS + time_at_cranes_online_ULCS])

                total_time_at_cranes_online = np.sum(
                    [time_at_cranes_online_fully_cellular,
                     time_at_cranes_online_panamax,
                     time_at_cranes_online_panamax_max,
                     time_at_cranes_online_post_panamax_I,
                     time_at_cranes_online_post_panamax_II,
                     time_at_cranes_online_new_panamax,
                     time_at_cranes_online_VLCS,
                     time_at_cranes_online_ULCS])

                # berth_occupancy is the total time at berth divided by the operational hours
                berth_occupancy_online = min([total_time_at_berth_online / self.operational_hours, 1])
                crane_occupancy_online = min([total_time_at_cranes_online / self.operational_hours, 1])

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

    def check_crane_slot_available(self):
        # find number of available crane slots
        list_of_elements = core.find_elements(self, Berth)
        slots = 0
        for element in list_of_elements:
            slots += element.max_cranes

        # create a list of all quay unloaders
        list_of_elements = core.find_elements(self, Cyclic_Unloader)

        # when there are more available slots than installed cranes there are still slots available (True)
        if slots > len(list_of_elements):
            return True
        else:
            return False

    def calculate_throughput(self, year):
        """Find throughput (minimum of crane capacity and demand)"""
        # intialize values to be returned
        total_vol = 0

        # gather volumes from each commodity scenario
        commodities = core.find_elements(self, Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                total_vol += volume
            except:
                pass

        # find the total service rate and determine the capacity at the quay
        list_of_elements = core.find_elements(self, Cyclic_Unloader)
        quay_capacity_planned = 0
        quay_capacity_online = 0
        if list_of_elements != []:
            for element in list_of_elements:
                quay_capacity_planned += (
                            element.effective_capacity * self.operational_hours * self.allowable_berth_occupancy)
                if year >= element.year_online:
                    quay_capacity_online += (
                                element.effective_capacity * self.operational_hours * self.allowable_berth_occupancy)

        if quay_capacity_online is not 0:
            throughput_online = min(quay_capacity_online, total_vol)
        else:
            throughput_online = total_vol

        return throughput_online

    def cargo_split_quay_throughput(self, year):
        # Calculate the cargo split over the quay
        commodities = core.find_elements(self, Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        # divide throughput over different categories based on indicated split
        laden_teu = volume * self.laden_perc
        reefer_teu = volume * self.reefer_perc
        empty_teu = volume * self.empty_perc
        oog_teu = volume * self.oog_perc

        # divide throughput per category by teu factor to arrive at boxes
        laden_box = laden_teu / self.laden_teu_factor
        reefer_box = reefer_teu / self.reefer_teu_factor
        empty_box = empty_teu / self.empty_teu_factor
        oog_box = oog_teu / self.oog_teu_factor

        return laden_teu, reefer_teu, empty_teu, oog_teu,\
               laden_box, reefer_box, empty_box, oog_box

    def cargo_split_terminal_throughput(self, year):
        # Calculate the cargo split over the terminal (excludes transhipment)
        commodities = core.find_elements(self, Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        # divide throughput over different categories based on indicated split
        laden_teu = volume * self.laden_perc
        reefer_teu = volume * self.reefer_perc
        empty_teu = volume * self.empty_perc
        oog_teu = volume * self.oog_perc

        laden_teu_ts = laden_teu * self.transhipment_ratio *0.5 + laden_teu*(1 - self.transhipment_ratio)
        reefer_teu_ts = reefer_teu * self.transhipment_ratio *0.5 + reefer_teu*(1 - self.transhipment_ratio)
        empty_teu_ts = empty_teu * self.transhipment_ratio *0.5 + empty_teu*(1 - self.transhipment_ratio)
        oog_teu_ts = oog_teu * self.transhipment_ratio *0.5 + oog_teu*(1 - self.transhipment_ratio)

        # divide throughput per category by teu factor to arrive at boxes
        laden_box_ts = laden_teu_ts / self.laden_teu_factor
        reefer_box_ts = reefer_teu_ts / self.reefer_teu_factor
        empty_box_ts = empty_teu_ts / self.empty_teu_factor
        oog_box_ts = oog_teu_ts / self.oog_teu_factor

        return laden_teu_ts, reefer_teu_ts, empty_teu_ts, oog_teu_ts,\
               laden_box_ts, reefer_box_ts, empty_box_ts, oog_box_ts

    # def throughput_characteristics(self, year):
    #     """
    #     - Find commodity volume
    #     - Find the on terminal modal split (types: ladens, empties, reefers, oogs)
    #     - Return the total TEU/year for every throughput type
    #     """
    #
    #     # Calculate the total throughput in TEU per year
    #     commodities = core.find_elements(self, Commodity)
    #     for commodity in commodities:
    #         try:
    #             volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
    #         except:
    #             pass
    #
    #     # divide throughput over different categories based on indicated split
    #     laden_teu = volume * self.laden_perc
    #     reefer_teu = volume * self.reefer_perc
    #     empty_teu = volume * self.empty_perc
    #     oog_teu = volume * self.oog_perc
    #
    #     return laden_teu, reefer_teu, empty_teu, oog_teu

    # def throughput_box(self, year):
    #     """
    #     - Find the total TEU/year for every throughput type (types: ladens, empties, reefers, oogs)
    #     - Translate the total TEU/year to number of boxes for every throughput type
    #     """
    #
    #     # import container throughput
    #     laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)
    #
    #     # instantiate terminal objexts
    #     laden = Container(**container_defaults.laden_container_data)
    #     reefer = Container(**container_defaults.reefer_container_data)
    #     empty = Container(**container_defaults.empty_container_data)
    #     oog = Container(**container_defaults.oog_container_data)
    #
    #     laden_box = laden_teu / laden.teu_factor
    #     reefer_box = reefer_teu / reefer.teu_factor
    #     empty_box = empty_teu / empty.teu_factor
    #     oog_box = oog_teu / oog.teu_factor
    #
    #     throughput_box = laden_box + reefer_box + empty_box + oog_box
    #
    #     return laden_box, reefer_box, empty_box, oog_box, throughput_box

    def box_moves(self, year):
        """Calculate the box moves as input for the power and fuel consumption"""

        laden_box, reefer_box, empty_box, oog_box, throughput_box = self.throughput_box(year)

        # calculate STS moves (equal to the throughput)
        sts_moves = throughput_box

        # calculate the number of tractor moves
        tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)
        tractor_moves = throughput_box * tractor.non_essential_moves

        # calculate the number of empty moves
        empty = Empty_Stack(**container_defaults.empty_stack_data)
        empty_moves = empty_box * empty.household * empty.digout

        # Todo: wellicht reefer and laden nog scheiden van elkaar in alles

        # calculate laden and reefer stack moves
        if self.laden_stack == 'rtg':  # Rubber Tired Gantry crane
            stack = Laden_Stack(**container_defaults.rtg_stack_data)
        elif self.laden_stack == 'rmg':  # Rail Mounted Gantry crane
            stack = Laden_Stack(**container_defaults.rmg_stack_data)
        elif self.laden_stack == 'sc':  # Straddle Carrier
            stack = Laden_Stack(**container_defaults.sc_stack_data)
        elif self.laden_stack == 'rs':  # Reach Stacker
            stack = Laden_Stack(**container_defaults.rs_stack_data)

        # The number of moves per laden box moves for transhipment (t/s)
        moves_t_s = 0.5 * ((2 + stack.household) * stack.digout_margin)
        # The number of moves per laden box moves for import and export (i/e)
        digout_moves = (stack.height - 1) / 2  # JvBeemen
        moves_i_e = ((2 + stack.household + digout_moves) + ((2 + stack.household) * stack.digout_margin)) / 2

        # The number of laden/reefer boxes for transhipment (t/s)
        laden_reefer_box_t_s = (laden_box + reefer_box) * self.transhipment_ratio
        # The number of laden/reefer boxes for import and export (i/e)
        laden_reefer_box_i_e = (laden_box + reefer_box) - laden_reefer_box_t_s

        # The number of moves for transhipment (t/s)
        laden_reefer_moves_t_s = laden_reefer_box_t_s * moves_t_s
        # The number of moves for import and export (i/e)
        laden_reefer_moves_i_e = laden_reefer_box_i_e * moves_i_e

        # number of stack moves is import export moves + transhipment moves
        stack_moves = laden_reefer_moves_i_e + laden_reefer_moves_t_s

        return sts_moves, tractor_moves, empty_moves, stack_moves

    def calculate_land_use(self, year):
        """Calculate total land use by summing all land_use values of the physical terminal elements"""

        quay_land_use = 0
        stack_land_use = 0
        empty_land_use = 0
        oog_land_use = 0
        gate_land_use = 0
        general_land_use = 0

        for element in self.elements:
            if isinstance(element, Quay_wall):
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

        # sum total of all
        total_land_use = \
            quay_land_use + \
            stack_land_use + \
            empty_land_use + \
            oog_land_use + \
            gate_land_use + \
            general_land_use

        return total_land_use

    # *** Plotting functions
    def terminal_elements_plot(self, width=0.08, alpha=0.6, fontsize=20, demand_step=50_000):
        """Gather data from Terminal and plot which elements come online when"""
        years = []
        berths = []
        quays = []
        cranes = []
        tractor_trailer = []
        laden_reefer_stack = []
        empty_stack = []
        oog_stack = []
        stack_equipment = []
        empty_handler = []
        gates = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            berths.append(0)
            quays.append(0)
            cranes.append(0)
            tractor_trailer.append(0)
            laden_reefer_stack.append(0)
            empty_stack.append(0)
            oog_stack.append(0)
            stack_equipment.append(0)
            empty_handler.append(0)
            gates.append(0)

            for element in self.elements:
                if isinstance(element, Berth):
                    if year >= element.year_online:
                        berths[-1] += 1
                if isinstance(element, Quay_wall):
                    if year >= element.year_online:
                        quays[-1] += 1
                if isinstance(element, Cyclic_Unloader):
                    if year >= element.year_online:
                        cranes[-1] += 1
                if isinstance(element, Horizontal_Transport):
                    if year >= element.year_online:
                        tractor_trailer[-1] += 1
                if isinstance(element, Laden_Stack):
                    if year >= element.year_online:
                        laden_reefer_stack[-1] += 1
                if isinstance(element, Empty_Stack):
                    if year >= element.year_online:
                        empty_stack[-1] += 1
                if isinstance(element, OOG_Stack):
                    if year >= element.year_online:
                        oog_stack[-1] += 1
                if isinstance(element, Stack_Equipment):
                    if year >= element.year_online:
                        stack_equipment[-1] += 1
                if isinstance(element, Empty_Handler):
                    if year >= element.year_online:
                        empty_handler[-1] += 1
                if isinstance(element, Gate):
                    if year >= element.year_online:
                        gates[-1] += 1

        # tractor_trailer = [x / 10 for x in tractor_trailer]

        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 12))
        ax1.grid(zorder=0, which='major', axis='both')

        colors = ['firebrick', 'darksalmon', 'sandybrown', 'darkkhaki', 'palegreen', 'lightseagreen', 'mediumpurple',
                  'mediumvioletred', 'lightgreen', 'red']
        offset = 4.5 * width

        ax1.bar([x - offset + 0 * width for x in years], berths, zorder=1, width=width, alpha=alpha,
               label="berths", color=colors[0], edgecolor='darkgrey')
        ax1.bar([x - offset + 1 * width for x in years], quays, zorder=1, width=width, alpha=alpha,
               label="quays", color=colors[1], edgecolor='darkgrey')
        ax1.bar([x - offset + 2 * width for x in years], cranes, zorder=1, width=width, alpha=alpha,
               label="STS cranes", color=colors[2], edgecolor='darkgrey')
        ax1.bar([x - offset + 3 * width for x in years], tractor_trailer, zorder=1, width=width, alpha=alpha,
               label="tractor_trailers", color=colors[3], edgecolor='darkgrey')
        ax1.bar([x - offset + 4 * width for x in years], laden_reefer_stack, zorder=1, width=width, alpha=alpha,
               label="laden / reefer stack", color=colors[4], edgecolor='darkgrey')
        ax1.bar([x - offset + 5 * width for x in years], empty_stack, zorder=1, width=width, alpha=alpha,
               label="empty stack", color=colors[5], edgecolor='darkgrey')
        ax1.bar([x - offset + 6 * width for x in years], oog_stack, zorder=1, width=width, alpha=alpha,
               label="oog stack", color=colors[6], edgecolor='darkgrey')
        ax1.bar([x - offset + 7 * width for x in years], stack_equipment, zorder=1, width=width, alpha=alpha,
               label="stack equipment", color=colors[7], edgecolor='darkgrey')
        ax1.bar([x - offset + 8 * width for x in years], empty_handler, zorder=1, width=width, alpha=alpha,
               label="empty handlers", color=colors[8], edgecolor='darkgrey')
        ax1.bar([x - offset + 9 * width for x in years], gates, zorder=1, width=width, alpha=alpha,
               label="gates", color=colors[9], edgecolor='darkgrey')

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

        # Making a second graph
        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, zorder=2, label="Demand [teu/y]", where='mid', color='blue')

        # title and labels
        ax1.set_title('Terminal elements online', fontsize=fontsize)
        ax1.set_xlabel('Years', fontsize=fontsize)
        ax1.set_ylabel('Terminal elements on line [nr]', fontsize=fontsize)
        ax2.set_ylabel('Demand/throughput[t/y]', fontsize=fontsize)

        # ticks and tick labels
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels([int(x) for x in years], rotation='vertical', fontsize=fontsize)
        max_elements = max([max(berths), max(quays), max(cranes),
                            max(tractor_trailer), max(laden_reefer_stack),
                            max(empty_stack), max(oog_stack),
                            max(stack_equipment), max(empty_handler), max(gates)])
        ax1.set_yticks([x for x in range(0, max_elements + 1 + 2, 10)])
        ax1.set_yticklabels([int(x) for x in range(0, max_elements + 1 + 2, 10)], fontsize=fontsize)

        ax2.set_yticks([x for x in range(0, np.max(demand["demand"]) + demand_step, demand_step)])
        ax2.set_yticklabels([int(x) for x in range(0, np.max(demand["demand"]) + demand_step, demand_step)], fontsize=fontsize)

        # print legend
        fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=5, fontsize=fontsize)
        fig.subplots_adjust(bottom=0.23)

    def land_use_plot(self, width=0.25, alpha=0.6, fontsize=20):
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
                if isinstance(element, Quay_wall):
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
        fig, ax = plt.subplots(figsize=(20, 12))
        ax.grid(zorder=0, which='major', axis='both')

        offset = 0 * width

        ax.bar([x - offset for x in years], quay_land_use, width=width, alpha=alpha,
               label="apron")
        ax.bar([x - offset for x in years], stack_land_use, width=width, alpha=alpha,
               label="laden and reefer stack", bottom=quay_land_use)
        ax.bar([x - offset for x in years], empty_land_use, width=width, alpha=alpha,
               label="empty stack", bottom=quay_stack)
        ax.bar([x - offset for x in years], oog_land_use, width=width, alpha=alpha,
               label="oog stack", bottom=quay_stack_empty)
        ax.bar([x - offset for x in years], gate_land_use, width=width, alpha=alpha,
               label="gate area", bottom=quay_stack_empty_oog)
        ax.bar([x - offset for x in years], general_land_use, width=width, alpha=alpha,
               label="general service area", bottom=quay_stack_empty_oog_gate)

        # title and labels
        ax.set_title('Terminal land use ' + self.stack_equipment, fontsize=fontsize)
        ax.set_xlabel('Years', fontsize=fontsize)
        ax.set_ylabel('Land use [ha]', fontsize=fontsize)

        # ticks and tick labels
        ax.set_xticks([x for x in years])
        ax.set_xticklabels([int(x) for x in years], rotation='vertical', fontsize=fontsize)

        ticks = ax.get_yticks()
        ax.set_yticks([x for x in ticks])
        ax.set_yticklabels([int(x) for x in ticks], fontsize=fontsize)

        # print legend
        fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=3, fontsize=fontsize)
        fig.subplots_adjust(bottom=0.18)

    def terminal_capacity_plot(self, width=0.25, alpha=0.6):
        """Gather data from Terminal and plot which elements come online when"""

        # get crane service capacity and storage capacity
        years = []
        cranes = []
        cranes_capacity = []

        for year in range(self.startyear, self.startyear + self.lifecycle):

            years.append(year)
            cranes.append(0)
            cranes_capacity.append(0)

            fully_cellular_calls, panamax_calls, panamax_max_calls, post_panamax_I_calls, post_panamax_II_calls, \
            new_panamax_calls, VLCS_calls, ULCS_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
            berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
                self.calculate_berth_occupancy(year, fully_cellular_calls, panamax_calls, panamax_max_calls,
                                               post_panamax_I_calls, post_panamax_II_calls,
                                               new_panamax_calls, VLCS_calls, ULCS_calls)

            for element in self.elements:
                if isinstance(element, Cyclic_Unloader):
                    # calculate cranes service capacity: effective_capacity * operational hours * berth_occupancy?
                    if year >= element.year_online:
                        cranes[-1] += 1
                        cranes_capacity[
                            -1] += element.effective_capacity * self.operational_hours * crane_occupancy_online

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
        # ax.bar([x + 0.5 * width for x in years], storages_capacity, width=width, alpha=alpha, label="storages",
        #        color='green')
        ax.step(years, demand['demand'].values, label="demand", where='mid')

        ax.set_xlabel('Years')
        ax.set_ylabel('Throughput capacity [TEU/year]')
        ax.set_title('Terminal capacity online ({})'.format(self.crane_type_defaults['crane_type']))
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def laden_stack_area_plot(self, width=0.25, alpha=0.6):
        """Gather data from laden stack area and plot it against demand"""

        # collect elements to add to plot
        years = []
        area = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)
            area.append(0)

            # stack_capacity_online, stack_capacity_planned, required_capacity, \
            #     total_ground_slots, laden_stack_area, reefer_capacity = \
            #     self.laden_reefer_stack_capacity(year)

            for element in self.elements:
                if isinstance(element, Laden_Stack):
                    if year >= element.year_online:
                        area[-1] += element.land_use   # laden_stack_area

        # transform from m2 to hectares
        area = [x * 0.0001 for x in area]
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
        fig, ax1 = plt.subplots(figsize=(20, 10))
        ax1.set_xticks([x for x in years])
        ax1.set_xticklabels(years)
        ax1.set_xlabel('Years')
        ax1.set_ylabel('Laden stack area [ha]')
        ax1.bar([x - 0.5 * width for x in years], area, width=width, alpha=alpha, label="laden stack area",
                color='red')

        ax2 = ax1.twinx()
        ax2.step(years, demand['demand'].values, label="demand", where='mid')
        ax2.set_ylabel('Throughput capacity [TEU/year]')

        ax2.set_title('Terminal capacity online ({})'.format(self.crane_type_defaults['crane_type']))

        ax1.legend()
        ax2.legend()

    def opex_plot(self, cash_flows):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        # prepare years, revenue, capex and opex for plotting
        years = cash_flows['year'].values
        insurance = cash_flows['insurance'].values
        maintenance = cash_flows['maintenance'].values
        energy = cash_flows['energy'].values
        labour = cash_flows['labour'].values
        fuel = cash_flows['fuel'].values
        # demurrage = cash_flows['demurrage'].values
        print(cash_flows)

        # generate plot
        fig, ax = plt.subplots(figsize=(14, 5))

        ax.step(years, insurance, label='insurance', where='mid')
        ax.step(years, labour, label='labour', where='mid')
        ax.step(years, fuel, label='fuel', where='mid')
        ax.step(years, energy, label='energy', where='mid')
        ax.step(years, maintenance, label='maintenance', where='mid')

        ax.set_xlabel('Years')
        ax.set_ylabel('Opex [ M $]')
        ax.set_title('Overview of Opex')
        ax.set_xticks([x for x in years])
        ax.set_xticklabels(years)
        ax.legend()

    def terminal_layout_plot(self, fontsize=20):

        years = []
        terminal = []
        prim_yard = []

        for year in range(self.startyear, self.startyear + self.lifecycle):
            years.append(year)

            for element in self.elements:
                if isinstance(element, Terminal_Layout):
                    if year == element.year_online:
                        terminal = element.terminal
                        prim_yard = element.prim_yard
                        apron = element.apron
                        block_location_list = element.block_location_list
                        tgs_capacity = element.tgs_capacity
                        tgs_demand = element.tgs_demand
                        stack_height = element.stack.height

            terminal_x, terminal_y = terminal.exterior.xy
            prim_yard_x, prim_yard_y = prim_yard.exterior.xy
            apron_x, apron_y = apron.exterior.xy

            fig, ax = plt.subplots(figsize=(20, 12))
            ax.grid(zorder=0, which='major', axis='both')

            # Plotting Container Terminal
            ax.plot(terminal_x, terminal_y)

            # Plotting Primary Yard
            ax.plot(prim_yard_x, prim_yard_y)

            # Plotting Apron
            apron_fig = mpatches.Rectangle([apron_x[0],apron_y[0]], (max(apron_x) - min(apron_x)), (max(apron_y) - min(apron_y)), fc='red', ec="red", label='Apron area')
            ax.add_patch(apron_fig)

            for element in self.elements:
                if isinstance(element, Laden_Stack):
                    if year >= element.year_online:
                        stack_online = True
                        break
                    if year < element.year_online:
                        stack_online = False

            if stack_online:
                # Plotting Container Stack
                for stack in block_location_list:
                    stack_fig = mpatches.Rectangle(stack[0], stack[3][0] - stack[0][0], stack[1][1] - stack[0][1], fc = "white", ec = "black")
                    ax.add_patch(stack_fig)
            else:
                tgs_capacity = 0

            terminal_capacity = tgs_capacity * stack_height
            terminal_demand = tgs_demand * stack_height

            ax.axis('equal')
            ax.set_title('Container terminal layout at year = ' + str(year), fontsize=fontsize)
            ax.set_xlabel('x-direction (m)', fontsize=fontsize)
            ax.set_ylabel('y-direction (m)', fontsize=fontsize)

            'Give legend information'
            terminal_legend = mlines.Line2D([], [], color='#1f77b4', markersize=15, label='Terminal area')
            prim_yard_legend = mlines.Line2D([], [], color='#ff7f0e', markersize=15, label='Primary yard area')

            ax.annotate('Yard TGS capacity = ' + str(math.floor(tgs_capacity)) + ' TGS', xy=(1600, 650), size=14, ha='right', va='top', bbox=dict(boxstyle='round', fc='w'))
            ax.annotate('Yard TGS demand = ' + str(math.floor(tgs_demand)) + ' TGS', xy=(1600, 600), size=14, ha='right', va='top', bbox=dict(boxstyle='round', fc='w'))

            ax.legend(handles=[terminal_legend, prim_yard_legend, apron_fig], loc='lower center', bbox_to_anchor=(0.5, -0.135),
                      fancybox=True, shadow=True, ncol=4, fontsize=10)

            plt.savefig('Container Terminal Layout at year ' + str(year) + ' .png')