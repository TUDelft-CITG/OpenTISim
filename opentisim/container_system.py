# package(s) for data handling
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# opentisim package
from opentisim.container_objects import *
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

    def __init__(self, startyear=2019, lifecycle=20, operational_hours=7500, debug=False, elements=[],
                 crane_type_defaults=container_defaults.sts_crane_data,
                 stack_equipment='rs', laden_stack='rs',
                 allowable_waiting_service_time_ratio_berth=0.1, allowable_berth_occupancy=0.6,
                 laden_perc=0.80, empty_perc=0.05, reefer_perc=0.1, oog_perc=0.05,
                 transhipment_ratio=0.69,
                 energy_price=0.17, fuel_price=1, land_price=0):
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

    # *** Overall terminal investment strategy for terminal class.
    def simulate(self):
        """The 'simulate' method implements the terminal investment strategy for this terminal class.

        This method automatically generates investment decisions, parametrically derived from overall demand trends and
        a number of investment triggers.

        Generic approaches based on:
        - PIANC. 2014. Master plans for the development of existing ports. MarCom - Report 158, PIANC
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
                print('$$$ Check horizontal transport investments ------')
            self.horizontal_transport_invest(year)

            if self.debug:
                print('')
                print('$$$ Check laden stack investments ---------------')
            self.laden_stack_invest(year)

            if self.debug:
                print('')
                print('$$$ Check empty stack investments ---------------')
            self.empty_stack_invest(year)

            if self.debug:
                print('')
                print('$$$ Check stack investments ----------------------')
            self.oog_stack_invest(year)

            if self.debug:
                print('')
                print('$$$ Check equipment investment -------------------')
            self.stack_equipment_invest(year)

            if self.debug:
                print('')
                print('$$$ Check gate investments -----------------------')
            self.gate_invest(year)

            if self.debug:
                print('')
                print('$$$ Check empty handlers -------------------------')
            self.empty_handler_invest(year)

            if self.debug:
                print('')
                print('$$$ Check general services -----------------------')
            self.general_services_invest(year)

        # 3. for each year calculate the general labour, fuel and energy costs (requires insight in realized demands)
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_energy_cost(year)

        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_general_labour_cost(year)

        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_fuel_cost(year)

        # 4. for each year calculate the demurrage costs (requires insight in realized demands)
        self.demurrage = []
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_demurrage_cost(year)

        # Todo: see if here a method can be implemented to estimate the revenue that is needed to get NPV = 0
        # 5.  for each year calculate terminal revenues
        # self.revenues = []
        # for year in range(self.startyear, self.startyear + self.lifecycle):
        #     self.calculate_revenue(year)

        # 6. collect all cash flows (capex, opex, revenues)
        cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()

        # 7. calculate key numbers
        # Todo: check to see if core method can be used in stead
        NPV, capex_normal, opex_normal, labour_normal = self.NPV()

        # 8. calculate land use
        total_land_use = self.calculate_land_use(year)

        # Todo: implement a return method for Simulate()
        land = total_land_use
        labour = labour_normal[-1]
        opex = opex_normal[-1]
        capex_normal = np.nan_to_num(capex_normal)
        capex = np.sum(capex_normal)

        data = {"equipment": self.stack_equipment,
                "cost_land": self.land_price,
                "cost_fuel": self.fuel_price,
                "cost_power": self.energy_price,
                "land": land,
                "labour": labour,
                "opex": opex,
                "capex": capex,
                "NPV": NPV}

        # Todo: check if this statement is indeed obsolete
        # cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()

        # Todo: this return statement should be obsolete as everything is logged in the Terminal object
        return NPV, data

    # *** Individual investment methods for terminal elements
    def berth_invest(self, year, handysize, handymax, panamax):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and
        Mulder, 2004) for the berth investments.

        Decision recipe Berth:
           QSC: berth_occupancy & allowable_waiting_service_time_ratio
           Benchmarking procedure: there is a problem if the estimated berth_occupancy triggers a waiting time over
           service time ratio that is larger than the allowed waiting time over service time ratio
              - allowable_waiting_service_time_ratio = .10 # 10% (see PIANC (2014))
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
        # Todo: check if more elements should be reported here

        # calculate planned berth occupancy and planned nr of berths
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
            self.calculate_berth_occupancy(year, handysize, handymax, panamax)
        berths = len(core.find_elements(self, Berth))

        # get the waiting time as a factor of service time
        if berths != 0:
            planned_waiting_service_time_ratio_berth = core.occupancy_to_waitingfactor(
                utilisation=berth_occupancy_planned, nr_of_servers_to_chk=berths)
        else:
            planned_waiting_service_time_ratio_berth = np.inf

#        factor, waiting_time_occupancy = self.waiting_time(year)
        if self.debug:
            print('     Berth occupancy online (@ start of year): {:.2f} (trigger level: {:.2f})'.format(berth_occupancy_online, self.allowable_berth_occupancy))
            print('     Berth occupancy planned (@ start of year): {:.2f} (trigger level: {:.2f})'.format(berth_occupancy_planned, self.allowable_berth_occupancy))
            print('     Planned waiting time service time factor (@ start of year): {:.2f} (trigger level: {:.2f})'.format(planned_waiting_service_time_ratio_berth, self.allowable_waiting_service_time_ratio_berth))

            print('')
            print('--- Start investment analysis ----------------------')
            print('')
            print('$$$ Check berth elements (coupled with berth occupancy) ---------------')

        core.report_element(self, Berth, year)
        core.report_element(self, Quay_wall, year)
        core.report_element(self, Cyclic_Unloader, year)

        # while planned_waiting_service_time_ratio is larger than self.allowable_waiting_service_time_ratio_berth
        while planned_waiting_service_time_ratio_berth > self.allowable_waiting_service_time_ratio_berth:

            # while planned waiting service time ratio is too large add a berth when no crane slots are available
            if not (self.check_crane_slot_available()):
                if self.debug:
                    print('  *** add Berth to elements')

                berth = Berth(**container_defaults.berth_data)
                berth.year_online = year + berth.delivery_time
                self.elements.append(berth)
                berths = len(core.find_elements(self, Berth))

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
                    self.calculate_berth_occupancy(year, handysize, handymax, panamax)
                planned_waiting_service_time_ratio_berth = core.occupancy_to_waitingfactor(
                    utilisation=berth_occupancy_planned, nr_of_servers_to_chk=berths)

                if self.debug:
                    print('     Berth occupancy planned (after adding berth): {:.2f} (trigger level: {:.2f})'.format(
                        berth_occupancy_planned, self.allowable_berth_occupancy))
                    print('     Planned waiting time service time factor : {:.2f} (trigger level: {:.2f})'.format(
                        planned_waiting_service_time_ratio_berth, self.allowable_waiting_service_time_ratio_berth))

            # while planned waiting service time ratio is too large add a berth if a quay is needed
            berths = len(core.find_elements(self, Berth))
            quay_walls = len(core.find_elements(self, Quay_wall))
            if berths > quay_walls:
                length_v = max(container_defaults.handysize_data["LOA"], container_defaults.handymax_data["LOA"],
                              container_defaults.panamax_data["LOA"])  # average size
                draft = max(container_defaults.handysize_data["draft"], container_defaults.handymax_data["draft"],
                           container_defaults.panamax_data["draft"])

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
                quay_wall = Quay_wall(**container_defaults.quay_wall_data)
                depth = np.sum([draft, quay_wall.max_sinkage, quay_wall.wave_motion, quay_wall.safety_margin])
                self.quay_invest(year, length, depth)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
                    self.calculate_berth_occupancy(year, handysize, handymax, panamax)
                planned_waiting_service_time_ratio_berth = core.occupancy_to_waitingfactor(
                    utilisation=berth_occupancy_planned, nr_of_servers_to_chk=berths)

                if self.debug:
                    print('     Berth occupancy planned (after adding berth): {:.2f} (trigger level: {:.2f})'.format(
                        berth_occupancy_planned, self.allowable_berth_occupancy))
                    print('     Planned waiting time service time factor : {:.2f} (trigger level: {:.2f})'.format(
                        planned_waiting_service_time_ratio_berth, self.allowable_waiting_service_time_ratio_berth))

            # while planned berth occupancy is too large add a crane if a crane is needed
            if self.check_crane_slot_available():
                self.crane_invest(year)

                berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
                    self.calculate_berth_occupancy(year, handysize, handymax, panamax)
                planned_waiting_service_time_ratio_berth = core.occupancy_to_waitingfactor(
                    utilisation=berth_occupancy_planned, nr_of_servers_to_chk=berths)

                if self.debug:
                    print('     Berth occupancy planned (after adding berth): {:.2f} (trigger level: {:.2f})'.format(
                        berth_occupancy_planned, self.allowable_berth_occupancy))
                    print('     Planned waiting time service time factor : {:.2f} (trigger level: {:.2f})'.format(
                        planned_waiting_service_time_ratio_berth, self.allowable_waiting_service_time_ratio_berth))

    def quay_invest(self, year, length, depth):
        """
        Given the overall objectives for the terminal apply the following decision recipe (Van Koningsveld and
        Mulder, 2004) for the quay investments.

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

        # - capex
        # Todo: check this. Clearly some error was introduced here (now made equal to agribulk example)
        # unit_rate = int(quay_wall.Gijt_constant * (depth * 2 + quay_wall.freeboard) ** quay_wall.Gijt_coefficient)
        unit_rate = int(quay_wall.Gijt_constant_2 * 2 * (depth + quay_wall.freeboard))
        mobilisation = int(max((length * unit_rate * quay_wall.mobilisation_perc), quay_wall.mobilisation_min))
        apron_pavement = length * quay_wall.apron_width*quay_wall.apron_pavement
        cost_of_land = length * quay_wall.apron_width * self.land_price
        quay_wall.capex = int(length * unit_rate + mobilisation + apron_pavement + cost_of_land)

        # - opex
        quay_wall.insurance = unit_rate * length * quay_wall.insurance_perc
        quay_wall.maintenance = unit_rate * length * quay_wall.maintenance_perc
        quay_wall.year_online = year + quay_wall.delivery_time

        # - land use
        quay_wall.land_use = length * quay_wall.apron_width

        # add cash flow information to quay_wall object in a dataframe
        quay_wall = core.add_cashflow_data_to_element(self, quay_wall)

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
        '''old formula --> crane.labour = crane.crew * self.operational_hours / labour.shift_length  '''
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
        """current strategy is to add horizontal transport as soon as a service trigger is achieved
        - find out how much transport is online
        - find out how much transport is planned
        - find out how much transport is needed
        - add transport until service_trigger is no longer exceeded
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
            print('     Number of STS cranes planned (@start of year): {}'.format(cranes_planned))
            print('     Number of STS cranes online (@start of year): {}'.format(cranes_online))
            print('     Horizontal transport planned (@ start of year): {}'.format(hor_transport_planned))
            print('     Horizontal transport online (@ start of year): {}'.format(hor_transport_online))

        tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)
        # when the total number of online horizontal transporters < total number of transporters required by the cranes
        if self.stack_equipment != 'sc':

            while cranes_planned * tractor.required > hor_transport_planned:
                # add a tractor to elements
                if self.debug:
                    print('  *** add tractor to elements')
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

                if year == self.startyear:
                    # Todo: check why this is needed/logical
                    tractor.year_online = year + tractor.delivery_time + 1
                else:
                    tractor.year_online = year + tractor.delivery_time

                # add cash flow information to tractor object in a dataframe
                tractor = core.add_cashflow_data_to_element(self, tractor)

                self.elements.append(tractor)

                hor_transport_planned += 1

                if self.debug:
                    print('     a total of {} tractors is online; {} tractors still pending'.format(
                        hor_transport_online, hor_transport_planned-hor_transport_online))

        # Todo: check why this return statement is needed (and if it needs planned or online values)
        return cranes_planned

    def laden_stack_invest(self, year):
        """current strategy is to add stacks as soon as trigger is achieved
              - find out how much stack capacity is online
              - find out how much stack capacity is planned
              - find out how much stack capacity is needed
              - add stack capacity until service_trigger is no longer exceeded
              """

        stack_capacity_planned, stack_capacity_online, required_capacity, total_ground_slots, laden_stack_area, \
        reefer_slots = self.laden_reefer_stack_capacity(year)

        if self.debug:
            print('     Stack capacity planned (@ start of year): {:.2f}'.format(stack_capacity_planned))
            print('     Stack capacity online (@ start of year): {:.2f}'.format(stack_capacity_online))
            print('     Stack capacity required (@ start of year): {:.2f}'.format(required_capacity))
            print('     Total laden and reefer ground slots required (@ start of year): {:.2f}'.format(total_ground_slots))

        while required_capacity > (stack_capacity_planned):
            if self.debug:
                print('  *** add stack to elements')

            if self.laden_stack == 'rtg':
                stack = Laden_Stack(** container_defaults.rtg_stack_data)
            elif self.laden_stack == 'rmg':
                stack = Laden_Stack(** container_defaults.rmg_stack_data)
            elif self.laden_stack == 'sc':
                stack = Laden_Stack(**container_defaults.sc_stack_data)
            elif self.laden_stack == 'rs':
                stack = Laden_Stack(**container_defaults.rs_stack_data)

            reefer_slots = (self.reefer_perc/self.laden_perc) * stack.capacity

            # - land use
            stack_ground_slots = stack.capacity / stack.height
            stack.land_use = (stack_ground_slots * stack.gross_tgs) * stack.area_factor

            # - capex
            area = stack.length*stack.width
            gross_tgs = stack.gross_tgs
            pavement = stack.pavement
            drainage = stack.drainage
            area_factor = stack.area_factor
            reefer_rack=reefer_slots*stack.reefer_rack
            mobilisation = stack.mobilisation
            cost_of_land = self.land_price
            stack.capex = int((pavement+drainage+cost_of_land)*gross_tgs*area*area_factor + mobilisation + reefer_rack)

            # - opex
            stack.maintenance = int((pavement+drainage)*gross_tgs*area*area_factor * stack.maintenance_perc)




            if year == self.startyear:
                stack.year_online = year + stack.delivery_time + 1
            else:
                stack.year_online = year + stack.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            stack = core.add_cashflow_data_to_element(self, stack)

            self.elements.append(stack)

            stack_capacity_planned, stack_capacity_online, required_capacity, total_ground_slots, laden_stack_area, \
            reefer_slots = self.laden_reefer_stack_capacity(year)

    def empty_stack_invest(self, year):

        """current strategy is to add stacks as soon as trigger is achieved
                     - find out how much stack capacity is online
                     - find out how much stack capacity is planned
                     - find out how much stack capacity is needed
                     - add stack capacity until service_trigger is no longer exceeded
                     """

        empty_capacity_planned, empty_capacity_online, empty_required_capacity, empty_ground_slots, empty_stack_area = self.empty_stack_capacity(year)

        if self.debug:
            print('     Empty stack capacity planned (@ start of year): {:.2f}'.format(empty_capacity_planned))
            print('     Empty stack capacity online (@ start of year): {:.2f}'.format(empty_capacity_online))
            print('     Empty stack capacity required (@ start of year): {:.2f}'.format(empty_required_capacity))
            print('     Empty ground slots required (@ start of year): {:.2f}'.format(empty_ground_slots))

        while empty_required_capacity > (empty_capacity_planned):
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
            empty_stack.capex = int((pavement + drainage + cost_of_land) * gross_tgs * area * area_factor + mobilisation)

            # - opex
            empty_stack.maintenance = int((pavement + drainage) * gross_tgs * area * area_factor * empty_stack.maintenance_perc)



            if year == self.startyear:
                empty_stack.year_online = year + empty_stack.delivery_time + 1
            else:
                empty_stack.year_online = year + empty_stack.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            empty_stack = core.add_cashflow_data_to_element(self, empty_stack)

            self.elements.append(empty_stack)

            empty_capacity_planned, empty_capacity_online, empty_required_capacity, empty_ground_slots, \
            empty_stack_area = self.empty_stack_capacity(
                year)

    def oog_stack_invest(self, year):

        """current strategy is to add stacks as soon as trigger is achieved
                     - find out how much stack capacity is online
                     - find out how much stack capacity is planned
                     - find out how much stack capacity is needed
                     - add stack capacity until service_trigger is no longer exceeded
                     """

        oog_capacity_planned, oog_capacity_online, oog_required_capacity = self.oog_stack_capacity(year)

        if self.debug:
            print('     OOG slots planned (@ start of year): {:.2f}'.format(oog_capacity_planned))
            print('     OOG slots online (@ start of year): {:.2f}'.format(oog_capacity_online))
            print('     OOG slots required (@ start of year): {:.2f}'.format(oog_required_capacity))

        while oog_required_capacity > (oog_capacity_planned):
            if self.debug:
                print('  *** add empty stack to elements')

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
            oog_stack.maintenance = int(
                (pavement + drainage) * gross_tgs * area * area_factor * oog_stack.maintenance_perc)

            # - land use
            stack_ground_slots = oog_stack.capacity / oog_stack.height
            oog_stack.land_use = stack_ground_slots * oog_stack.gross_tgs

            if year == self.startyear:
                oog_stack.year_online = year + oog_stack.delivery_time + 1
            else:
                oog_stack.year_online = year + oog_stack.delivery_time

            # add cash flow information to quay_wall object in a dataframe
                oog_stack = core.add_cashflow_data_to_element(self, oog_stack)

            self.elements.append(oog_stack)

            oog_capacity_planned, oog_capacity_online, oog_required_capacity = self.oog_stack_capacity(year)

    def stack_equipment_invest(self, year):
        """current strategy is to add stack equipment as soon as a service trigger is achieved
        - find out how much stack equipment is online
        - find out how much stack equipment is planned
        - find out how much stack equipment is needed
        - add equipment until service_trigger is no longer exceeded
        """

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
            while sts_cranes > (stack_equipment_online//stack_equipment.required):

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


                if year == self.startyear:
                    stack_equipment.year_online = year + stack_equipment.delivery_time + 1
                else:
                    stack_equipment.year_online = year + stack_equipment.delivery_time

                # add cash flow information to tractor object in a dataframe
                stack_equipment = core.add_cashflow_data_to_element(self, stack_equipment)

                self.elements.append(stack_equipment)

                list_of_elements_stack_equipment = core.find_elements(self, Stack_Equipment)
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
                stack_equipment.shift = stack_equipment.crew * labour.daily_shifts
                stack_equipment.labour = stack_equipment.shift * labour.blue_collar_salary

                if year == self.startyear:
                    stack_equipment.year_online = year + stack_equipment.delivery_time + 1
                else:
                    stack_equipment.year_online = year + stack_equipment.delivery_time

                # add cash flow information to tractor object in a dataframe
                stack_equipment = core.add_cashflow_data_to_element(self, stack_equipment)

                self.elements.append(stack_equipment)

                list_of_elements_stack_equipment = core.find_elements(self, Stack_Equipment)
                stack_equipment_online = len(list_of_elements_stack_equipment)

    def gate_invest(self, year):
        """current strategy is to add gates as soon as trigger is achieved
              - find out how much gate capacity is online
              - find out how much gate capacity is planned
              - find out how much gate capacity is needed
              - add gate capacity until service_trigger is no longer exceeded
              """

        gate_capacity_planned, gate_capacity_online, service_rate_planned, total_design_gate_minutes = self.calculate_gate_minutes(year)

        if self.debug:
            print('     Gate capacity planned (@ start of year): {:.2f}'.format(gate_capacity_planned))
            print('     Gate capacity online (@ start of year): {:.2f}'.format(gate_capacity_online))
            print('     Service rate planned (@ start of year): {:.2f}'.format(service_rate_planned))
            print('     Gate lane minutes  (@ start of year): {:.2f}'.format(total_design_gate_minutes))

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
            canopy = gate.canopy_costs * gate.area
            cost_of_land = self.land_price
            gate.capex = int(unit_rate + mobilisation + canopy + (cost_of_land*gate.area))

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

            gate_capacity_planned, gate_capacity_online, service_rate_planned, total_design_gate_minutes = self.calculate_gate_minutes(year)

    def empty_handler_invest(self, year):
        """current strategy is to add empty hanlders as soon as a service trigger is achieved
        - find out how many empty handlers are online
        - find out how many empty handlers areplanned
        - find out how many empty handlers are needed
        - add empty handlers until service_trigger is no longer exceeded
        """
        list_of_elements_empty_handler = core.find_elements(self, Empty_Handler)
        list_of_elements_sts = core.find_elements(self, Cyclic_Unloader)
        sts_cranes=len(list_of_elements_sts)
        empty_handler_online=len(list_of_elements_empty_handler)


        empty_handler = Empty_Handler(**container_defaults.empty_handler_data)

        if self.debug:
            # print('     Horizontal transport planned (@ start of year): {}'.format(tractor_planned))
            print('     Empty handlers online (@ start of year): {}'.format(empty_handler_online))

        while sts_cranes > (empty_handler_online//empty_handler.required):
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
            empty_handler.shift = empty_handler.crew * labour.daily_shifts
            empty_handler.labour = empty_handler.shift * labour.blue_collar_salary

            if year == self.startyear:
                empty_handler.year_online = year + empty_handler.delivery_time + 1
            else:
                empty_handler.year_online = year + empty_handler.delivery_time

            # add cash flow information to tractor object in a dataframe
            empty_handler = core.add_cashflow_data_to_element(self, empty_handler)

            self.elements.append(empty_handler)

            list_of_elements_empty_handler = core.find_elements(self, Empty_Handler)
            empty_handler_online = len(list_of_elements_empty_handler)

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


        quay_land_use=0
        stack_land_use=0
        empty_land_use=0
        oog_land_use=0
        gate_land_use=0

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

        total_land_use=(quay_land_use+stack_land_use+empty_land_use+oog_land_use+gate_land_use + general.office
                        + general.workshop + general.scanning_inspection_area + general.repair_building)*0.0001

        if year == (self.startyear+1):
            # add general services as soon as berth  is online
            if self.debug:
                print('  *** add general services to elements')


            # land use
            general.land_use = general.office + general.workshop + general.scanning_inspection_area\
                               + general.repair_building

            # - capex
            area = general.office + general.workshop + general.scanning_inspection_area\
                               + general.repair_building
            cost_of_land = self.land_price
            office = general.office * general.office_cost
            workshop = general.workshop * general.workshop_cost
            inspection = general.scanning_inspection_area * general.scanning_inspection_area_cost
            light = general.lighting_mast_cost * (total_land_use/general.lighting_mast_required)
            repair = general.repair_building * general.repair_building_cost
            basic = general.fuel_station_cost + general.firefight_cost + general.maintenance_tools_cost\
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

    # *** Energy costs, demurrage costs and revenue calculation methods
    def calculate_energy_cost(self, year): # todo voeg energy toe voor nieuwe elementen
        """

        """

        sts_moves, stack_moves, empty_moves, tractor_moves = self.box_moves(year)
        energy_price = self.energy_price

        '''STS crane energy costs'''
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

        '''calculate stack equipment energy costs'''
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
        stack_capacity_planned, stack_capacity_online, required_capacity, total_ground_slots, laden_stack_area, \
        reefer_slots = self.laden_reefer_stack_capacity(year)

        stacks = 0
        for element in self.elements:
            if isinstance(element, Laden_Stack):
                if year >= element.year_online:
                    stacks += 1

        for element in core.find_elements(self, Laden_Stack):
            if year >= element.year_online:
                slots_per_stack = reefer_slots / stacks
                if slots_per_stack * element.reefers_present * energy_price * 24*365 != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = slots_per_stack * element.reefers_present\
                                                                           * energy_price * 24*365
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

        '''Calculate general power use'''

        general = General_Services(**container_defaults.general_services_data)

        #lighting
        quay_land_use=0
        stack_land_use=0
        empty_land_use=0
        oog_land_use=0
        gate_land_use=0
        general_land_use=0

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

        total_land_use=quay_land_use+stack_land_use+empty_land_use+oog_land_use+gate_land_use+general_land_use
        lighting = total_land_use * energy_price * general.lighting_consumption

        #Office, gates, workshops power use
        general_consumption=general.general_consumption*energy_price*self.operational_hours
        for element in core.find_elements(self, General_Services):
            if year >= element.year_online:
                if lighting +general_consumption != np.inf:
                    element.df.loc[element.df['year'] == year, 'energy'] = lighting +general_consumption
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0

    def calculate_general_labour_cost(self,year):
        '''General labour'''
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
        sts_moves, stack_moves, empty_moves, tractor_moves = self.box_moves(year)
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

        handysize_calls, handymax_calls, panamax_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
        berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online = \
            self.calculate_berth_occupancy(year, handysize_calls, handymax_calls, panamax_calls)

        berths = len(core.find_elements(self, Berth))

        waiting_factor = \
            core.occupancy_to_waitingfactor(utilisation=berth_occupancy_online, nr_of_servers_to_chk=berths)

        waiting_time_hours = waiting_factor * crane_occupancy_online * self.operational_hours / total_calls
        waiting_time_occupancy = waiting_time_hours * total_calls / self.operational_hours

        # waiting_factor = \
        #     core.occupancy_to_waitingfactor(utilisation=berth_occupancy_online, nr_of_servers_to_chk=berths)
        #
        # handysize_calls, handymax_calls, panamax_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
        #
        # factor, waiting_time_occupancy = self.waiting_time(year)

        # Find the service_rate per quay_wall to find the average service hours at the quay for a vessel
        quay_walls = len(core.find_elements(self, Quay_wall))

        service_rate = 0
        for element in (core.find_elements(self, Cyclic_Unloader)):
            if year >= element.year_online:
                service_rate += element.effective_capacity / quay_walls

        # Find the demurrage cost per type of vessel
        if service_rate != 0:
            handymax = Vessel(**container_defaults.handymax_data)
            service_time_handymax = handymax.call_size / service_rate
            waiting_time_hours_handymax = waiting_factor * service_time_handymax
            port_time_handymax = waiting_time_hours_handymax + service_time_handymax + handymax.mooring_time
            penalty_time_handymax = max(0, port_time_handymax - handymax.all_turn_time)
            demurrage_time_handymax = penalty_time_handymax * handymax_calls
            demurrage_cost_handymax = demurrage_time_handymax * handymax.demurrage_rate

            handysize = Vessel(**container_defaults.handysize_data)
            service_time_handysize = handysize.call_size / service_rate
            waiting_time_hours_handysize = waiting_factor * service_time_handysize
            port_time_handysize = waiting_time_hours_handysize + service_time_handysize + handysize.mooring_time
            penalty_time_handysize = max(0, port_time_handysize - handysize.all_turn_time)
            demurrage_time_handysize = penalty_time_handysize * handysize_calls
            demurrage_cost_handysize = demurrage_time_handysize * handysize.demurrage_rate

            panamax = Vessel(**container_defaults.panamax_data)
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

    def calculate_indirect_costs(self):
        """Indirect costs are a function of overall CAPEX."""
        # Todo: check why this is not done per year
        indirect = Indirect_Costs(**container_defaults.indirect_costs_data)

        # collect CAPEX from terminal elements
        cash_flows, cash_flows_WACC_real = core.add_cashflow_elements(self, Labour(**container_defaults.labour_data))
        capex = cash_flows['capex'].values
        print(capex)

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

    # *** Financial analyses
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
            cash_flows['demurrage'] = self.demurrage
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
                                    (1 + core.WACC_real()) ** (
                                    year - self.startyear))


            return cash_flows, cash_flows_WACC_real

    # def add_cashflow_data_to_element(self, element):
    #
    #     """Place cashflow data in element dataframe"""
    #
    #     # years
    #     years = list(range(self.startyear, self.startyear + self.lifecycle))
    #
    #     # capex
    #     capex = element.capex
    #
    #     # opex
    #     maintenance = element.maintenance
    #     insurance = element.insurance
    #     labour = element.labour
    #
    #     # year online
    #     year_online = element.year_online
    #     year_delivery = element.delivery_time
    #
    #     df = pd.DataFrame()
    #
    #     # years
    #     df["year"] = years
    #
    #     # capex
    #     if year_delivery > 1:
    #         df.loc[df["year"] == year_online - 2, "capex"] = 0.6 * capex
    #         df.loc[df["year"] == year_online - 1, "capex"] = 0.4 * capex
    #     else:
    #         df.loc[df["year"] == year_online - 1, "capex"] = capex
    #
    #     # opex
    #     if maintenance:
    #         df.loc[df["year"] >= year_online, "maintenance"] = maintenance
    #     if insurance:
    #         df.loc[df["year"] >= year_online, "insurance"] = insurance
    #     if labour:
    #         df.loc[df["year"] >= year_online, "labour"] = labour
    #
    #     df.fillna(0, inplace=True)
    #
    #     element.df = df
    #
    #     return element

    # def WACC_nominal(self, Gearing=60, Re=.10, Rd=.30, Tc=.28):
    #     """Nominal cash flow is the true dollar amount of future revenues the company expects
    #     to receive and expenses it expects to pay out, including inflation.
    #     When all cashflows within the model are denoted in real terms and including inflation."""
    #
    #     Gearing = Gearing
    #     Re = Re  # return on equity
    #     Rd = Rd  # return on debt
    #     Tc = Tc  # income tax
    #     E = 100 - Gearing
    #     D = Gearing
    #
    #     WACC_nominal = ((E / (E + D)) * Re + (D / (E + D)) * Rd) * (1 - Tc)
    #
    #     return WACC_nominal

    # def WACC_real(self, inflation=0.02):  # old: interest=0.0604
    #     """Real cash flow expresses a company's cash flow with adjustments for inflation.
    #     When all cashflows within the model are denoted in real terms and have been
    #     adjusted for inflation (no inlfation has been taken into account),
    #     WACC_real should be used. WACC_real is computed by as follows:"""
    #
    #     WACC_real = (self.WACC_nominal() + 1) / (inflation + 1) - 1
    #
    #     return WACC_real

    def NPV(self):
        """Gather data from Terminal elements and combine into a cash flow plot"""

        # add cash flow information for each of the Terminal elements
        cash_flows, cash_flows_WACC_real = self.add_cashflow_elements()

        # prepare years, revenue, capex and opex for plotting
        years = cash_flows_WACC_real['year'].values
        # revenue = self.revenues
        capex = cash_flows_WACC_real['capex'].values
        opex = cash_flows_WACC_real['insurance'].values + \
               cash_flows_WACC_real['maintenance'].values + \
               cash_flows_WACC_real['energy'].values + \
               cash_flows_WACC_real['demurrage'].values + \
               cash_flows_WACC_real['fuel'].values + \
               cash_flows_WACC_real['labour'].values
        opex = np.nan_to_num(opex)

        # prepare years, revenue, capex and opex for plotting
        years = cash_flows_WACC_real['year'].values
        # revenue = self.revenues
        capex_normal = cash_flows['capex'].values
        opex_normal = cash_flows['insurance'].values + \
               cash_flows['maintenance'].values + \
               cash_flows['energy'].values + \
               cash_flows['demurrage'].values + \
               cash_flows['fuel'].values + \
               cash_flows['labour'].values
        labour_normal = cash_flows['labour'].values

        NPV = - capex - opex
        NPV = np.sum(NPV)


        return NPV, capex_normal, opex_normal, labour_normal

    # *** General functions
    # def find_elements(self, obj):
    #     """return elements of type obj part of self.elements"""
    #
    #     list_of_elements = []
    #     if self.elements != []:
    #         for element in self.elements:
    #             if isinstance(element, obj):
    #                 list_of_elements.append(element)
    #
    #     return list_of_elements

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

    def throughput_characteristics(self, year):

        """
        - Find all commodities and the modal split
        - Translate the total TEU/year to every container type troughput
        """

        ''' Calculate the total throughput in TEU per year'''
        commodities = core.find_elements(self, Commodity)
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
        - Translate the total TEU/year to every container type troughput
        """

        '''import container throughputs'''

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
        ''''Calculate the box moves as input for the power and fuel consumption'''

        laden_box, reefer_box, empty_box, oog_box, throughput_box = self.throughput_box(year)

        # calculate STS moves
        '''STS cranes are responsible for the throughput (containers over the quay), 
        therefore the total number of boxes is the total number of box moves for STS cranes'''

        sts_moves = throughput_box

        # calculate the number of tractor moves
        tractor = Horizontal_Transport(**container_defaults.tractor_trailer_data)
        tractor_moves = throughput_box * tractor.non_essential_moves

        # calculate the number of empty moves
        empty = Empty_Stack(**container_defaults.empty_stack_data)
        empty_moves = empty_box * empty.household * empty.digout

        #todo wellicht reefer and laden nog scheiden van elkaar in alles

        #calculate laden and reefer stack moves
        if self.laden_stack == 'rtg':
            stack = Laden_Stack(**container_defaults.rtg_stack_data)
        elif self.laden_stack == 'rmg':
            stack = Laden_Stack(**container_defaults.rmg_stack_data)
        elif self.laden_stack == 'sc':
            stack = Laden_Stack(**container_defaults.sc_stack_data)
        elif self.laden_stack == 'rs':
            stack = Laden_Stack(**container_defaults.rs_stack_data)

        digout_moves = (stack.height -1)/2 #JvBeemen
        ''''The number of moves per laden box moves differs for import and export (i/e) and for transhipment (t/s)'''
        moves_i_e = ((2+stack.household+digout_moves)+((2+stack.household) * stack.digout_margin))/2
        moves_t_s = 0.5 * ((2+stack.household) * stack.digout_margin)

        laden_reefer_box_t_s = (laden_box + reefer_box) * self.transhipment_ratio
        laden_reefer_box_i_e = (laden_box + reefer_box) - laden_reefer_box_t_s

        laden_reefer_moves_t_s = laden_reefer_box_t_s * moves_t_s
        laden_reefer_moves_i_e = laden_reefer_box_i_e * moves_i_e

        stack_moves = laden_reefer_moves_i_e + laden_reefer_moves_t_s

        return  sts_moves, stack_moves, empty_moves, tractor_moves

    def calculate_land_use(self, year):

        quay_land_use=0
        stack_land_use=0
        empty_land_use=0
        oog_land_use=0
        gate_land_use=0
        general_land_use=0

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


        total_land_use=quay_land_use+stack_land_use+empty_land_use+oog_land_use+gate_land_use+general_land_use

        return total_land_use

    def laden_reefer_stack_capacity(self, year):

        """
        - #todo beschrijving laden reefer stack
        """


        list_of_elements = core.find_elements(self, Laden_Stack)
        # find the total stack capacity

        stack_capacity_planned = 0
        stack_capacity_online = 0
        required_capacity = 0
        for element in list_of_elements:
            stack_capacity_planned += element.capacity
            if year >= element.year_online:
                stack_capacity_online += element.capacity

        laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)

        ts=self.transhipment_ratio

        laden_teu = (laden_teu*ts*0.5)+(laden_teu*(1-ts))
        reefer_teu = (reefer_teu * ts * 0.5) + (reefer_teu * (1 - ts))

        laden = Container(**container_defaults.laden_container_data)
        reefer = Container(**container_defaults.reefer_container_data)
        stack = Laden_Stack(**container_defaults.rtg_stack_data)

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

        required_capacity = (laden_ground_slots+reefer_ground_slots)*stack.height
        laden_stack_area = total_ground_slots*stack.area_factor

        return stack_capacity_planned, stack_capacity_online, required_capacity, total_ground_slots, laden_stack_area, reefer_slots

    def empty_stack_capacity(self, year):


        """
        - #todo beschrijving empty stack
        """

        list_of_elements = core.find_elements(self, Empty_Stack)
        # find the total stack capacity

        empty_capacity_planned = 0
        empty_capacity_online = 0
        empty_required_capacity = 0
        for element in list_of_elements:
            empty_capacity_planned += element.capacity
            if year >= element.year_online:
                empty_capacity_online += element.capacity

        ts=self.transhipment_ratio

        laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)

        empty = Container(**container_defaults.empty_container_data)

        stack = Empty_Stack(**container_defaults.empty_stack_data)

        operational_days = self.operational_hours // 24
        empty_teu = (empty_teu * ts * 0.5) + (empty_teu * (1 - ts))
        empty_ground_slots = empty_teu * empty.peak_factor * empty.dwell_time / empty.stack_occupancy / stack.height / operational_days

        empty_required_capacity = empty_ground_slots*stack.height
        empty_stack_area = empty_ground_slots*stack.area_factor

        return empty_capacity_planned, empty_capacity_online, empty_required_capacity, empty_ground_slots, empty_stack_area

    def oog_stack_capacity(self, year):


        """
        - #todo beschrijving oog stack
        """

        list_of_elements = core.find_elements(self, OOG_Stack)
        # find the total stack capacity

        oog_capacity_planned = 0
        oog_capacity_online = 0
        oog_required_capacity = 0
        for element in list_of_elements:
            oog_capacity_planned += element.capacity
            if year >= element.year_online:
                oog_capacity_online += element.capacity
        ts=self.transhipment_ratio

        laden_teu, reefer_teu, empty_teu, oog_teu = self.throughput_characteristics(year)

        oog_teu = (oog_teu * ts * 0.5) + (oog_teu * (1 - ts))

        oog = Container(**container_defaults.oog_container_data)

        stack = OOG_Stack(**container_defaults.oog_stack_data)

        operational_days = self.operational_hours // 24

        oog_spots = oog_teu * oog.peak_factor * oog.dwell_time / oog.stack_occupancy / stack.height / operational_days / oog.teu_factor

        oog_required_capacity = oog_spots

        return oog_capacity_planned, oog_capacity_online, oog_required_capacity

    def calculate_berth_occupancy(self, year, handysize_calls, handymax_calls, panamax_calls):
        """
        - Find all cranes and sum their effective_capacity to get service_capacity
        - Divide callsize_per_vessel by service_capacity and add mooring time to get total time at berth
        - Occupancy is total_time_at_berth divided by operational hours
        """

        # list all crane objects in system
        list_of_elements = core.find_elements(self, Cyclic_Unloader)
        list_of_elements_berth = core.find_elements(self, Berth)
        nr_berths = len(list_of_elements_berth)

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
                    (container_defaults.handysize_data["call_size"] / service_rate_planned) +(container_defaults.handysize_data[
                "mooring_time"]/nr_berths))
            time_at_berth_handymax_planned = handymax_calls * (
                    (container_defaults.handymax_data["call_size"] / service_rate_planned) +(container_defaults.handymax_data[
                "mooring_time"]/nr_berths))
            time_at_berth_panamax_planned = panamax_calls * (
                    (container_defaults.panamax_data["call_size"] / service_rate_planned) +(container_defaults.panamax_data[
                "mooring_time"]/nr_berths))


            total_time_at_berth_planned = np.sum(
                [time_at_berth_handysize_planned, time_at_berth_handymax_planned, time_at_berth_panamax_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            berth_occupancy_planned = total_time_at_berth_planned / self.operational_hours

            # estimate crane occupancy
            time_at_crane_handysize_planned = handysize_calls * (
                (container_defaults.handysize_data["call_size"] / service_rate_planned))
            time_at_crane_handymax_planned = handymax_calls * (
                (container_defaults.handymax_data["call_size"] / service_rate_planned))
            time_at_crane_panamax_planned = panamax_calls * (
                (container_defaults.panamax_data["call_size"] / service_rate_planned))


            total_time_at_crane_planned = np.sum(
                [time_at_crane_handysize_planned, time_at_crane_handymax_planned, time_at_crane_panamax_planned])

            # berth_occupancy is the total time at berth divided by the operational hours
            crane_occupancy_planned = total_time_at_crane_planned / self.operational_hours

            if service_rate_online != 0:
                time_at_berth_handysize_online = handysize_calls * (
                        (container_defaults.handysize_data["call_size"] / service_rate_online) +container_defaults.handysize_data[
                    "mooring_time"])
                time_at_berth_handymax_online = handymax_calls * (
                        (container_defaults.handymax_data["call_size"] / service_rate_online) +container_defaults.handymax_data[
                    "mooring_time"])
                time_at_berth_panamax_online = panamax_calls * (
                        (container_defaults.panamax_data["call_size"] / service_rate_online) +(container_defaults.panamax_data[
                    "mooring_time"]/nr_berths))




                total_time_at_berth_online = np.sum(
                    [time_at_berth_handysize_online, time_at_berth_handymax_online, time_at_berth_panamax_online])

                # berth_occupancy is the total time at berth devided by the operational hours
                berth_occupancy_online = min([total_time_at_berth_online / self.operational_hours, 1])

                time_at_crane_handysize_online = handysize_calls * (
                    (container_defaults.handysize_data["call_size"] / service_rate_online))
                time_at_crane_handymax_online = handymax_calls * (
                    (container_defaults.handymax_data["call_size"] / service_rate_online))
                time_at_crane_panamax_online = panamax_calls * (
                    (container_defaults.panamax_data["call_size"] / service_rate_online))

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

    def calculate_throughput(self,year):
        # list_of_elements = core.find_elements(self, Cyclic_Unloader)
        # list_of_elements_berth = core.find_elements(self, Berth)
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

        commodities = core.find_elements(self, Commodity)
        for commodity in commodities:
            try:
                volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
            except:
                pass

        demand = volume


        # find the total service rate and determine the capacity at the quay
        list_of_elements = core.find_elements(self, Cyclic_Unloader)
        # list_of_elements_berth = core.find_elements(self, Berth)
        quay_capacity_planned = 0
        quay_capacity_online = 0
        if list_of_elements != []:
            for element in list_of_elements:
                quay_capacity_planned += (element.effective_capacity*self.operational_hours*self.allowable_berth_occupancy)
                if year >= element.year_online:
                    quay_capacity_online += (element.effective_capacity*self.operational_hours*self.allowable_berth_occupancy)


        # # find the total laden capacity
        # list_of_elements = core.find_elements(self, Laden_Stack)
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
        # list_of_elements = core.find_elements(self, Empty_Stack)
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
        # list_of_elements = core.find_elements(self, OOG_Stack)
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

    def calculate_gate_minutes(self, year):
        """
        - Find all gates and sum their effective_capacity to get service_capacity
        - Calculate average entry and exit time to get total time at gate
        - Occupancy is total_minutes_at_gate per hour divided by 1 hour
        """

        # list all gate objects in system
        list_of_elements = core.find_elements(self, Gate)

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
            '''Get input: import box moves en export box moves, translate to design gate lanes per hour.
            Every gate is 60 minutes, which is the capacity. Dan is het gewoon while totaal is meer dan totale capacity gate toevoegen'''



            ''' Calculate the total throughput in TEU per year'''
            laden_box, reefer_box, empty_box, oog_box, throughput_box = self.throughput_box(year)

            import_box_moves = (throughput_box * (1-self.transhipment_ratio)) * 0.5 #assume import / export is always 50/50
            export_box_moves = (throughput_box * (1 - self.transhipment_ratio)) * 0.5 #assume import / export is always 50/50
            weeks_year = 52

            gate = Gate(**container_defaults.gate_data)

            design_exit_gate_minutes = import_box_moves*gate.truck_moves / weeks_year * gate.peak_factor * gate.peak_day * gate.peak_hour * \
                                       gate.exit_inspection_time * gate.design_capacity

            design_entry_gate_minutes = export_box_moves * gate.truck_moves / weeks_year * gate.peak_factor * gate.peak_day * gate.peak_hour * \
                                       gate.entry_inspection_time * gate.design_capacity

            total_design_gate_minutes = design_entry_gate_minutes + design_exit_gate_minutes

            service_rate_planend = total_design_gate_minutes / capacity_planned

        else:
            service_rate_planend = float("inf")

        return capacity_planned, capacity_online, service_rate_planend, total_design_gate_minutes

    # def waiting_time(self, year):
    #     """
    #    - Import the berth occupancy of every year
    #    - Find the factor for the waiting time with the E2/E/n quing theory using 4th order polynomial regression
    #    - Waiting time is the factor times the crane occupancy
    #    """
    #     # todo: fix the waiting time method to use
    #     handysize_calls, handymax_calls, panamax_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
    #     berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online= self.calculate_berth_occupancy(
    #         year, handysize_calls, handymax_calls, panamax_calls)
    #
    #     # find the different factors which are linked to the number of berths
    #     berths = len(core.find_elements(self, Berth))
    #
    #     if berths == 1:
    #         factor = max(0,
    #                      79.726 * berth_occupancy_online ** 4 - 126.47 * berth_occupancy_online ** 3 + 70.660 * berth_occupancy_online ** 2 - 14.651 * berth_occupancy_online + 0.9218)
    #     elif berths == 2:
    #         factor = max(0,
    #                      29.825 * berth_occupancy_online ** 4 - 46.489 * berth_occupancy_online ** 3 + 25.656 * berth_occupancy_online ** 2 - 5.3517 * berth_occupancy_online + 0.3376)
    #     elif berths == 3:
    #         factor = max(0,
    #                      19.362 * berth_occupancy_online ** 4 - 30.388 * berth_occupancy_online ** 3 + 16.791 * berth_occupancy_online ** 2 - 3.5457 * berth_occupancy_online + 0.2253)
    #     elif berths == 4:
    #         factor = max(0,
    #                      17.334 * berth_occupancy_online ** 4 - 27.745 * berth_occupancy_online ** 3 + 15.432 * berth_occupancy_online ** 2 - 3.2725 * berth_occupancy_online + 0.2080)
    #     elif berths == 5:
    #         factor = max(0,
    #                      11.149 * berth_occupancy_online ** 4 - 17.339 * berth_occupancy_online ** 3 + 9.4010 * berth_occupancy_online ** 2 - 1.9687 * berth_occupancy_online + 0.1247)
    #     elif berths == 6:
    #         factor = max(0,
    #                      10.512 * berth_occupancy_online ** 4 - 16.390 * berth_occupancy_online ** 3 + 8.8292 * berth_occupancy_online ** 2 - 1.8368 * berth_occupancy_online + 0.1158)
    #     elif berths == 7:
    #         factor = max(0,
    #                      8.4371 * berth_occupancy_online ** 4 - 13.226 * berth_occupancy_online ** 3 + 7.1446 * berth_occupancy_online ** 2 - 1.4902 * berth_occupancy_online + 0.0941)
    #     else:
    #         # if there are no berths the occupancy is 'infinite' so a berth is certainly needed
    #         factor = float("inf")
    #
    #     waiting_time_hours = factor * crane_occupancy_online * self.operational_hours / total_calls
    #     waiting_time_occupancy = waiting_time_hours * total_calls / self.operational_hours
    #
    #     return factor, waiting_time_occupancy

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

    # def report_element(self, Element, year):
    #     elements = 0
    #     elements_online = 0
    #     element_name = []
    #     list_of_elements = core.find_elements(self, Element)
    #     if list_of_elements != []:
    #         for element in list_of_elements:
    #             element_name = element.name
    #             elements += 1
    #             if year >= element.year_online:
    #                 elements_online += 1
    #
    #     if self.debug:
    #         print('     a total of {} {} is online; {} total planned'.format(elements_online, element_name, elements))
    #
    #     return elements_online, elements

    # *** Plotting functions
    def terminal_elements_plot(self, width=0.1, alpha=0.6, fontsize=20):
        """Gather data from Terminal and plot which elements come online when"""

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
                if isinstance(element, Quay_wall):
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

        tractor = [x / 10 for x in tractor]

        # generate plot
        fig, ax = plt.subplots(figsize=(20, 12))
        ax.grid(zorder=0, which='major', axis='both')

        colors = ['firebrick', 'darksalmon', 'sandybrown', 'darkkhaki', 'palegreen', 'lightseagreen', 'mediumpurple',
                  'mediumvioletred', 'lightgreen']
        offset = 4 * width

        ax.bar([x - offset + 0 * width for x in years], berths, zorder=1, width=width, alpha=alpha, label="berths", color=colors[0], edgecolor='darkgrey')
        ax.bar([x - offset + 1 * width for x in years], quays, zorder=1, width=width, alpha=alpha, label="quays", color=colors[1], edgecolor='darkgrey')
        ax.bar([x - offset + 2 * width for x in years], cranes, zorder=1, width=width, alpha=alpha, label="STS cranes", color=colors[2], edgecolor='darkgrey')
        ax.bar([x - offset + 3 * width for x in years], tractor, zorder=1, width=width, alpha=alpha, label="tractor x10", color=colors[3], edgecolor='darkgrey')
        ax.bar([x - offset + 4 * width for x in years], stack, zorder=1, width=width, alpha=alpha, label="stack", color=colors[4], edgecolor='darkgrey')
        ax.bar([x - offset + 5 * width for x in years], empty_stack, zorder=1, width=width, alpha=alpha, label="empty stack", color=colors[5], edgecolor='darkgrey')
        ax.bar([x - offset + 6 * width for x in years], oog_stack, zorder=1, width=width, alpha=alpha, label="oog stack", color=colors[6], edgecolor='darkgrey')
        ax.bar([x - offset + 7 * width for x in years], stack_equipment, zorder=1, width=width, alpha=alpha, label="stack equipment", color=colors[7], edgecolor='darkgrey')
        ax.bar([x - offset + 8 * width for x in years], gates, zorder=1, width=width, alpha=alpha, label="gates", color=colors[8], edgecolor='darkgrey')

        # title and labels
        ax.set_title('Terminal elements online', fontsize=fontsize)
        ax.set_xlabel('Years', fontsize=fontsize)
        ax.set_ylabel('Terminal elements on line [nr]', fontsize=fontsize)
        ax.set_ylabel('Demand/throughput[t/y]', fontsize=fontsize)

        # ticks and tick labels
        ax.set_xticks([x for x in years])
        ax.set_xticklabels([int(x) for x in years], rotation='vertical', fontsize=fontsize)
        max_elements = max([max(berths), max(quays), max(cranes),
                            max(tractor), max(stack),
                            max(empty_stack), max(oog_stack),
                            max(stack_equipment), max(gates)])
        ax.set_yticks([x for x in range(0, max_elements + 1 + 2, 10)])
        ax.set_yticklabels([int(x) for x in range(0, max_elements + 1 + 2, 10)], fontsize=fontsize)

        # print legend
        fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=5, fontsize=fontsize)
        fig.subplots_adjust(bottom=0.18)

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
        # generate plot
        fig, ax = plt.subplots(figsize=(20, 12))
        ax.grid(zorder=0, which='major', axis='both')

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
        # storages = []
        # storages_capacity = []

        for year in range(self.startyear, self.startyear + self.lifecycle):

            years.append(year)
            cranes.append(0)
            cranes_capacity.append(0)
            # storages.append(0)
            # storages_capacity.append(0)

            handysize_calls, handymax_calls, panamax_calls, total_calls, total_vol = self.calculate_vessel_calls(year)
            berth_occupancy_planned, berth_occupancy_online, crane_occupancy_planned, crane_occupancy_online= self.calculate_berth_occupancy(
                year, handysize_calls, handymax_calls, panamax_calls)

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

    def cashflow_plot(self, cash_flows, width=0.3, alpha=0.6):
        """Gather data from Terminal elements and combine into a cash flow plot"""
        #prepare NPV
        NPV, capex_normal, opex_normal, labour_normal = self.NPV()
        print(NPV)



        # prepare years, revenue, capex and opex for plotting
        years = cash_flows['year'].values
        # revenue = self.revenues
        capex = cash_flows['capex'].values
        opex = cash_flows['insurance'].values + cash_flows['maintenance'].values + cash_flows['energy'].values + \
               cash_flows['labour'].values + cash_flows['demurrage'].values

        # sum cash flows to get profits as a function of year
        profits = []
        for year in years:
            profits.append(-cash_flows.loc[cash_flows['year'] == year]['capex'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['insurance'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['maintenance'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['energy'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['labour'].item() -
                           cash_flows.loc[cash_flows['year'] == year]['demurrage'].item())
                          # + revenue[cash_flows.loc[cash_flows['year'] == year].index.item()])

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
        # ax.bar([x + width for x in years], revenue, width=width, alpha=alpha, label="revenue", color='lightgreen')
        # ax.step(years, profits, label='profits', where='mid')
        # ax.step(years, profits_cum, label='profits_cum', where='mid')
        ax.set_xlabel('Years')
        ax.set_ylabel('Cashflow [000 M $]')
        ax.set_title('Cash flow plot')
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

            stack_capacity_planned, stack_capacity_online, required_capacity, total_ground_slots, laden_stack_area = self.laden_reefer_stack_capacity(year)

            for element in self.elements:
                if isinstance(element, Laden_Stack):
                    if year >= element.year_online:
                        area[-1] = laden_stack_area
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