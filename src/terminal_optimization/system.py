# package(s) for data handling
import pandas as pd
import numpy as np

# Used for making the graph to visualize our problem
import networkx as nx

# terminal_optimization package
from terminal_optimization.objects import *
from terminal_optimization import defaults


class System:
    def __init__(self, startyear=2019, lifecycle=20, operational_hours=4680, elements=[], supply_chains=[],
                 supply_graph=[], cargo_type=[],
                 cargo_forecast=[],
                 traffic_forecast=[]):
        # time inputs
        self.startyear = startyear
        self.lifecycle = lifecycle
        self.operational_hours = operational_hours

        # status terminal @ T=startyear
        self.supply_chains = supply_chains
        self.supply_graph = supply_graph
        self.elements = elements

        # cargo and traffic inputs
        self.cargo_type = cargo_type
        self.cargo_forecast = cargo_forecast
        self.traffic_forecast = traffic_forecast

    def create_data_dict(self, obj):
        # add cash flow information to quay_wall object in a dataframe
        data = {}

        data['year'] = list(range(self.startyear, self.startyear + self.lifecycle))
        try:
            data['capex'] = list(np.multiply(0, range(self.startyear, obj.year_online - 1))) + [
                obj.capex] + list(
                np.multiply(0, range(obj.year_online, self.startyear + self.lifecycle)))
        except:
            pass

        try:
            data['maintenance'] = list(np.multiply(0, range(self.startyear, obj.year_online - 1))) + \
                                  list(np.multiply(obj.maintenance,
                                                   len(range(obj.year_online - 1, self.startyear + self.lifecycle)) * [
                                                       1]))
        except:
            pass

        try:
            data['insurance'] = list(np.multiply(0, range(self.startyear, obj.year_online - 1))) + \
                                list(np.multiply(obj.maintenance,
                                                 len(range(obj.year_online - 1, self.startyear + self.lifecycle)) * [
                                                     1]))
        except:
            pass

        try:
            data['energy'] = list(np.multiply(0, range(self.startyear, obj.year_online - 1))) + \
                             list(np.multiply(obj.energy,
                                              len(range(obj.year_online - 1, self.startyear + self.lifecycle)) * [
                                                  1]))
        except:
            pass

        try:
            data['labour'] = list(np.multiply(0, range(self.startyear, obj.year_online - 1))) + \
                             list(np.multiply(obj.labour,
                                              len(range(obj.year_online - 1, self.startyear + self.lifecycle)) * [
                                                  1]))
        except:
            pass

        return data

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

    def calculate_vessel_calls(self, year=2019):
        handysize_vol = 0
        handymax_vol = 0
        panamax_vol = 0

        vessels = self.find_elements(objects.Vessel)
        commodities = self.find_elements(objects.Commodity)

        for commodity in commodities:
            volume = commodity.scenario_data.loc[maize.scenario_data['year'] == year]['volume'].item()
            handysize_vol += volume * commodity.handysize_perc / 100
            handymax_vol += volume * commodity.handymax_perc / 100
            panamax_vol += volume * commodity.panamax_perc / 100

        for vessel in vessels:
            if vessel.type == 'Handysize':
                handysize_calls = int(np.ceil(handysize_vol / vessel.call_size))
            elif vessel.type == 'Handymax':
                handymax_calls = int(np.ceil(handymax_vol / vessel.call_size))
            elif vessel.type == 'Panamax':
                panamax_calls = int(np.ceil(panamax_vol / vessel.call_size))

        return handysize_calls, handymax_calls, panamax_calls

    def find_elements(self, obj):
        """return elements of type obj part of self.elements"""

        list_of_elements = []
        if self.elements != []:
            for element in self.elements:
                if isinstance(element, obj):
                    list_of_elements.append(element)

        return list_of_elements

    def quay_invest(self, year, target_quay_length):
        """current strategy is to add quay walls as long as target length is not yet achieved
        - find out how much quay wall is online
        - find out how much quay wall is planned
        - find out how much quay wall is needed
        - add quay_walls until target is reached
        """

        # from all Quay objects sum online length
        quay_length = 0
        quay_length_online = 0
        list_of_elements = self.find_elements(Quay_wall)
        if list_of_elements != []:
            for element in list_of_elements:
                quay_length += element.length
                if year >= element.year_online:
                    quay_length_online += element.length

        print('a total of {} m of quay length is online; {} m total planned'.format(quay_length_online, quay_length))

        # check if total planned length is smaller than target length, if so add a quay
        while quay_length < target_quay_length:
            print('add Quay to elements')
            quay_wall = Quay_wall(**defaults.quay_wall_data)

            # - capex
            # todo: check what this delta actually means. Now I assume it means all potential quay length
            delta = quay_wall.length
            unit_rate = int(
                quay_wall.Gijt_constant * (quay_wall.depth * 2 + quay_wall.freeboard) ** quay_wall.Gijt_coefficient)
            mobilisation = int(max((delta * unit_rate * quay_wall.mobilisation_perc), quay_wall.mobilisation_min))
            quay_wall.capex = int(delta * unit_rate + mobilisation)

            # - opex
            quay_wall.insurance = quay_wall.capex * quay_wall.insurance_perc
            quay_wall.maintenance = quay_wall.capex * quay_wall.maintenance_perc
            quay_wall.year_online = year + quay_wall.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            data = self.create_data_dict(quay_wall)
            quay_wall.df = pd.DataFrame(data=data)

            self.elements.append(quay_wall)

            quay_length += quay_wall.length

        print('a total of {} m of quay length is online; {} m total planned'.format(quay_length_online, quay_length))

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
            data = self.create_data_dict(silo)
            silo.df = pd.DataFrame(data=data)

            self.elements.append(silo)

            storage += silo.capacity

        print('a total of {} ton of storage capacity is online; {} ton total planned'.format(storage_online, storage))

    def crane_invest(self, year, service_capacity_trigger):
        """current strategy is to add cranes as soon as a service trigger is achieved
        - find out how much service capacity is online
        - find out how much service capacity is planned
        - find out how much service capacity is needed
        - add service capacity until service_trigger is no longer exceeded
        """

        # from all Crane objects sum online length
        service_capacity = 0
        service_capacity_online = 0
        list_of_elements_1 = self.find_elements(Cyclic_Unloader)
        list_of_elements_2 = self.find_elements(Continuous_Unloader)
        list_of_elements = list_of_elements_1 + list_of_elements_2
        if list_of_elements != []:
            for element in list_of_elements:
                service_capacity += element.lifting_capacity * element.hourly_cycles * element.eff_fact * self.operational_hours
                if year >= element.year_online:
                    service_capacity_online += element.lifting_capacity * element.hourly_cycles * element.eff_fact * self.operational_hours

        print('a total of {} ton of crane service capacity is online; {} ton total planned'.format(
            service_capacity_online,
            service_capacity))

        # check if total planned length is smaller than target length, if so add a quay
        while service_capacity < service_capacity_trigger:
            print('add Harbour crane to elements')
            crane = Cyclic_Unloader(**defaults.harbour_crane_data)

            # - capex
            delta = 1
            unit_rate = crane.unit_rate
            mobilisation = delta * unit_rate * crane.mobilisation_perc
            crane.capex = int(delta * unit_rate + mobilisation)

            # - opex
            crane.insurance = crane.capex * crane.insurance_perc
            crane.maintenance = crane.capex * crane.maintenance_perc

            occupancy = 0.8  # todo: Figure out occupancy
            consumption = crane.consumption
            hours = self.operational_hours * occupancy
            crane.energy = consumption * hours

            labour = Labour(**defaults.labour_data)
            crane.labour = crane.crew * self.operational_hours / labour.shift_length
            crane.year_online = year + crane.delivery_time

            # add cash flow information to quay_wall object in a dataframe
            data = self.create_data_dict(crane)
            crane.df = pd.DataFrame(data=data)

            self.elements.append(crane)

            service_capacity += crane.lifting_capacity * crane.hourly_cycles * crane.eff_fact * self.operational_hours

        print('a total of {} ton of crane service capacity is online; {} ton total planned'.format(
            service_capacity_online,
            service_capacity))

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
            data = self.create_data_dict(conveyor)
            conveyor.df = pd.DataFrame(data=data)

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
            data = self.create_data_dict(hinterland_station)
            hinterland_station.df = pd.DataFrame(data=data)

            self.elements.append(hinterland_station)

            service_capacity += hinterland_station.production

        print('a total of {} ton of conveyor service capacity is online; {} ton total planned'.format(
            service_capacity_online,
            service_capacity))

    def simulate(self, startyear=2019, lifecycle=20):
        """Step through each year of the terminal lifecycle and check if investment is needed
        1. step through investment decisions
        2. collect cash flows
        3. collect revenues
        4. calculate profits
        5. apply WACC to cashflows and revenues
        6. aggregate to NPV

        """
        # 1. step through investment decisions
        for year in range(startyear, startyear + lifecycle):
            print('Simulate year: {}'.format(year))
            self.quay_invest(year, 1000)
            self.storage_invest(year, 10000)
            self.crane_invest(year, 1200)
            self.conveyor_invest(year, 1000)
            self.unloading_station_invest(year, 1000)

            if False:
                self.berth_invest(year, 3)

        # 2. collect cash flows

        # 3. collect revenues

        # 4. calculate profits

        # 5. apply WACC to cashflows and revenues

        # 6. aggregate to NPV

    def plot_system(self):
        pass

    def NPV(self):
        pass

    def traffic_scenario(startyear=2019, lifecycle=20):
        # Import commodities from package
        maize = forecast.bulk_commodities(**forecast.maize_data)
        soybean = forecast.bulk_commodities(**forecast.maize_data)
        wheat = forecast.bulk_commodities(**forecast.wheat_data)

        # Maize - Linear demand
        historic_demand_maize = [1000000, 1100000, 1250000, 1400000, 1500000]  # demand at t=0
        historic_demand_maize = [i * 3 for i in historic_demand_maize]

        # Growth scenario
        # predefined_demand_maize = [1600000, 1900000, 1900000, 1950000, 2000000, 2100000, 2150000, 2200000,
        #                           2200000, 2250000, 2350000, 2400000, 2450000, 2550000, 2700000, 2900000,
        #                           3000000, 3050000, 3150000, 3300000]

        # Erratic growth scenario
        # predefined_demand_maize = [1705000, 1883000, 1835000, 2090000, 2093000, 2100000, 2047000, 2341000,
        #                           2549000, 2522000, 2670000, 2795000, 2717000, 2631000, 2561000, 2673000,
        #                           2878000, 3105000, 3342000, 3323000]

        # Crisis scenario
        predefined_demand_maize = [1600000, 1900000, 1900000, 1950000, 1750000, 1600000, 1550000, 1530000,
                                   1570000, 1620000, 1700000, 1750000, 1800000, 1900000, 2050000, 2250000,
                                   2350000, 2400000, 2500000, 2650000]
        predefined_demand_maize = [i * 3 for i in predefined_demand_maize]

        # Soybean - Exponential demand
        historic_demand_soybean = 5 * [0]
        rate_soybean = 1.06  # year on year growth rate of demand (% points) - input for constant method and random method

        # Wheat - Probabilistic demand
        historic_demand_wheat = 5 * [0]
        rate_wheat = 1.02
        mu_wheat = 0.01  # avg bonus rate added to base rate (% points)  - input for random method
        sigma_wheat = 0.065  # standard deviation of bonus rate (% points)   - input for random method

        # Create demand scenario
        # maize.linear_scenario      (start_year, simulation_window, historic_demand_maize  , growth_maize)
        maize.predefined_scenario(start_year, simulation_window, historic_demand_maize, predefined_demand_maize)
        soybean.exponential_scenario(start_year, simulation_window, historic_demand_soybean, rate_soybean)
        wheat.random_scenario(start_year, simulation_window, historic_demand_wheat, rate_wheat, mu_wheat, sigma_wheat)
        commodities = [maize, soybean, wheat]

        # Import vessels from package
        handysize = forecast.vessel(**forecast.handysize_data)
        handymax = forecast.vessel(**forecast.handymax_data)
        panamax = forecast.vessel(**forecast.panamax_data)
        vessels = [handysize, handymax, panamax]

        # Calculate yearly calls
        vessels = forecast.vessel_call_calc(vessels, commodities, simulation_window)

        # Plot forecast
        visualisation.scenario(commodities, simulation_window, start_year)

        return vessels, commodities

    def cargo_scenario(startyear=2019, lifecycle=20):
        # Import commodities from package
        maize = forecast.bulk_commodities(**forecast.maize_data)
        soybean = forecast.bulk_commodities(**forecast.maize_data)
        wheat = forecast.bulk_commodities(**forecast.wheat_data)

        # Maize - Linear demand
        historic_demand_maize = [1000000, 1100000, 1250000, 1400000, 1500000]  # demand at t=0
        historic_demand_maize = [i * 3 for i in historic_demand_maize]

        # Growth scenario
        # predefined_demand_maize = [1600000, 1900000, 1900000, 1950000, 2000000, 2100000, 2150000, 2200000,
        #                           2200000, 2250000, 2350000, 2400000, 2450000, 2550000, 2700000, 2900000,
        #                           3000000, 3050000, 3150000, 3300000]

        # Erratic growth scenario
        # predefined_demand_maize = [1705000, 1883000, 1835000, 2090000, 2093000, 2100000, 2047000, 2341000,
        #                           2549000, 2522000, 2670000, 2795000, 2717000, 2631000, 2561000, 2673000,
        #                           2878000, 3105000, 3342000, 3323000]

        # Crisis scenario
        predefined_demand_maize = [1600000, 1900000, 1900000, 1950000, 1750000, 1600000, 1550000, 1530000,
                                   1570000, 1620000, 1700000, 1750000, 1800000, 1900000, 2050000, 2250000,
                                   2350000, 2400000, 2500000, 2650000]
        predefined_demand_maize = [i * 3 for i in predefined_demand_maize]

        # Soybean - Exponential demand
        historic_demand_soybean = 5 * [0]
        rate_soybean = 1.06  # year on year growth rate of demand (% points) - input for constant method and random method

        # Wheat - Probabilistic demand
        historic_demand_wheat = 5 * [0]
        rate_wheat = 1.02
        mu_wheat = 0.01  # avg bonus rate added to base rate (% points)  - input for random method
        sigma_wheat = 0.065  # standard deviation of bonus rate (% points)   - input for random method

        # Create demand scenario
        # maize.linear_scenario      (start_year, simulation_window, historic_demand_maize  , growth_maize)
        maize.predefined_scenario(start_year, simulation_window, historic_demand_maize, predefined_demand_maize)
        soybean.exponential_scenario(start_year, simulation_window, historic_demand_soybean, rate_soybean)
        wheat.random_scenario(start_year, simulation_window, historic_demand_wheat, rate_wheat, mu_wheat, sigma_wheat)
        commodities = [maize, soybean, wheat]

        # Import vessels from package
        handysize = forecast.vessel(**forecast.handysize_data)
        handymax = forecast.vessel(**forecast.handymax_data)
        panamax = forecast.vessel(**forecast.panamax_data)
        vessels = [handysize, handymax, panamax]

        # Calculate yearly calls
        vessels = forecast.vessel_call_calc(vessels, commodities, simulation_window)

        # Plot forecast
        visualisation.scenario(commodities, simulation_window, start_year)

        return vessels, commodities


def forecast_call_calc(vessels, commodities, simulation_window):
    for i in range(len(vessels)):
        calls = []
        for t in range(simulation_window):
            if i == 0:
                percentage = commodities[0].handysize_perc / 100
            if i == 1:
                percentage = commodities[0].handymax_perc / 100
            if i == 2:
                percentage = commodities[0].panamax_perc / 100

            calls.append(int(np.ceil(np.sum(commodities[0].forecast[-1] / vessels[i].call_size) * percentage)))

        vessels[i].calls = calls

    return vessels
