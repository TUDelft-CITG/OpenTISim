# package(s) for data handling
import pandas as pd

# Used for making the graph to visualize our problem
import networkx as nx

# terminal_optimization package
from terminal_optimization.objects import *
from terminal_optimization import defaults


class System:
    def __init__(self, startyear=2019, lifecycle=20, elements=[], supply_chains=[], supply_graph=[], cargo_type=[],
                 cargo_forecast=[],
                 traffic_forecast=[]):
        # time inputs
        self.startyear = startyear
        self.lifecycle = lifecycle

        # status terminal @ T=startyear
        self.supply_chains = supply_chains
        self.supply_graph = supply_graph
        self.elements = elements

        # cargo and traffic inputs
        self.cargo_type = cargo_type
        self.cargo_forecast = cargo_forecast
        self.traffic_forecast = traffic_forecast

    def supply_chain(self, nodes, edges):
        """Create a supply chain of example objects
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
        supply_chain = list([p for p in nx.all_shortest_paths(FG, nodes[0].name, nodes[-1].name)])

        return supply_chain

    def find_elements(self, obj):
        """return elements of type obj part of self.elements"""
        list_of_elements = [isinstance(element, obj) for element in System.elements]

        return list_of_elements

    def quay_invest(self, year, target_quay_length):
        # *** current strategy is to add quay walls as long as target length is not yet achieved
        # find out how much quay wall is online

        # from all Quay objects sum online length
        list_of_elements = self.find_elements(Quay)
        quay_length = 0
        quay_length_online = 0
        for element in list_of_elements:
            quay_length += element.length
            if year >= element.year_online:
                quay_length_online += element.length

        print('a total of {} m of quay length is online; {} m total planned'.format(quay_length_online, quay_length))

        # check if total planned length is smaller than target length, if so add a quay
        while quay_length < target_quay_length:
            print('add Quay to elements')
            quay = Quay(**defaults.quay_data)
            quay.year_online = year + quay.delivery_time

            df = pd.DataFrame(index=range(self.startyear, self.startyear + self.lifecycle))
            df['capex'] = 0
            df.at[year, 'capex'] = quay.unit_rate
            df.at[range(year, self.startyear + self.lifecycle), 'maintenance'] = quay.unit_rate * quay.maintenance_perc
            df.at[range(year, self.startyear + self.lifecycle), 'insurance'] = quay.unit_rate * quay.insurance_perc
            quay.df = df

            self.elements.append(quay)
            # todo: add cost to cost matrix

            quay_length += quay.length

        print('a total of {} m of quay length is online; {} m total planned'.format(quay_length_online, quay_length))

    def storage_invest(self, year, storage_type, storage_trigger):
        """ current strategy is to add quay walls as long as target length is not yet achieved"""

        # find out how much quay wall is online
        list_of_elements = self.list_elements(storage_type)
        storage = 0
        storage_online = 0
        for element in list_of_elements:
            storage += element.silo_capacity
            if year >= element.year_online:
                storage_online += element.silo_capacity

        print('a total of {} ton of storage capacity is online; {} ton total planned'.format(storage_online, storage))

        # check if total planned length is smaller than target length, if so add a quay
        while storage < storage_trigger:
            print('add Storage to elements')
            silo = Storage(**defaults.silo_data)
            silo.year_online = year + silo.delivery_time

            df = pd.DataFrame(index=range(self.startyear, self.startyear + self.lifecycle))
            df['capex'] = 0
            df.at[year, 'capex'] = silo.unit_rate
            df.at[range(year, self.startyear + self.lifecycle), 'maintenance'] = silo.unit_rate * silo.maintenance_perc
            df.at[range(year, self.startyear + self.lifecycle), 'insurance'] = silo.unit_rate * silo.insurance_perc
            silo.df = df

            self.elements.append(silo)

            storage += silo.silo_capacity

        print('a total of {} ton of storage capacity is online; {} ton total planned'.format(storage_online, storage))

    def berth_invest(self, year, berth_occupancy):
        # *** current strategy is to add quay walls as long as target length is not yet achieved
        # find out how much quay wall is online

        # from all Quay objects sum online length
        list_of_elements = self.list_elements(Berth)
        quay_length = 0
        quay_length_online = 0
        for element in list_of_elements:
            quay_length += element.length
            if year >= element.year_online:
                quay_length_online += element.length

        print('a total of {} m of quay length is online; {} m total planned'.format(quay_length_online, quay_length))

        # check if total planned length is smaller than target length, if so add a quay
        while quay_length < target_quay_length:
            print('add Quay to elements')
            quay = Quay(**defaults.quay_data)
            quay.year_online = year + quay.delivery_time

            df = pd.DataFrame(index=range(self.startyear, self.startyear + self.lifecycle))
            df['capex'] = 0
            df.at[year, 'capex'] = quay.unit_rate
            df['maintenance'] = quay.unit_rate * quay.maintenance_perc
            df['insurance'] = quay.unit_rate * quay.insurance_perc
            quay.df = df

            self.elements.append(quay)
            # to do: add cost to cost matrix

            quay_length += quay.length

        print('a total of {} m of quay length is online; {} m total planned'.format(quay_length_online, quay_length))

    def simulate(self, startyear=2019, lifecycle=20):
        print('start')
        for year in range(startyear, startyear + interval):
            System.quay_invest(2020, 400)
            System.storage_invest(2020, Storage, 0.1 * 100000)

            timestep = year - start_year

            # *** for each element run investment trigger logic
            for element in self.elements:
                if isinstance(element, Berth):
                    self.berth_invest_decision_waiting(terminal.berths, terminal.cranes, vessels,
                                                       terminal.allowable_waiting_time, year, timestep,
                                                       operational_hours)

                if isinstance(element, Quay):
                    quay_invest_decision(System, year, target_quay_length)
                    self.quay_invest_decision(terminal.quays, terminal.berths, year, timestep)

                if isinstance(element, Berth):
                    pass

                if isinstance(element, Storage):
                    storage_type = 'Silos'
                    terminal.storage = invest.storage_invest_decision(terminal.storage, trigger_throughput_perc,
                                                                      aspired_throughput_perc, storage_type,
                                                                      commodities, year, timestep)

                if isinstance(element, Loader):
                    # Loading stations
                    terminal.stations = invest.station_invest_decision(terminal.stations, station_utilisation,
                                                                       trigger_throughput_perc, aspired_throughput_perc,
                                                                       commodities, year, timestep, operational_hours)

                if isinstance(element, Conveyor):
                    # Conveyors
                    terminal.quay_conveyors = invest.quay_conveyor_invest_decision(terminal.quay_conveyors,
                                                                                   terminal.cranes, year, timestep,
                                                                                   operational_hours)
                    terminal.hinterland_conveyors = invest.hinterland_conveyor_invest_decision(
                        terminal.hinterland_conveyors, terminal.stations, year, timestep, operational_hours)

            # Terminal throughput
            terminal = financial.throughput_calc(terminal, vessels, commodities, allowable_berth_occupancy, year,
                                                 start_year, timestep, operational_hours)

            # *** for updated terminal run financial calculations
            terminal.revenues = financial.revenue_calc(terminal.revenues, terminal.throughputs, commodities, year,
                                                       timestep)
            terminal.capex = financial.capex_calc(terminal, year, timestep)
            terminal.labour = financial.labour_calc(terminal, year, timestep, operational_hours)
            terminal.maintenance = financial.maintenance_calc(terminal, year, timestep)
            terminal.energy = financial.energy_calc(terminal, year, operational_hours, timestep)
            terminal.insurance = financial.insurance_calc(terminal, year, timestep)
            terminal.lease = financial.lease_calc(terminal, year, timestep)
            terminal.demurrage = financial.demurrage_calc(terminal.demurrage, terminal.berths, vessels, year, timestep)
            terminal.residuals = financial.residual_calc(terminal, year, timestep)
            terminal.profits = financial.profit_calc(terminal, simulation_window, timestep, year, start_year)
            terminal.opex = financial.opex_calc(terminal, year, timestep)

            # WACC depreciated profits
        terminal.WACC_cashflows = financial.WACC_calc(terminal.project_WACC, terminal.profits, simulation_window,
                                                      start_year)

        # Combine all cashflows
        terminal.cashflows = financial.cashflow_calc(terminal, simulation_window, start_year)

        # NPV
        terminal.NPV = financial.NPV_calc(terminal.WACC_cashflows)

        return terminal

    def plot_system(self):
        pass

    def NPV(self):
        pass


def scenario_generator(startyear, lifecycle):
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
