# package for unique identifiers
import uuid

# package(s) for data handling
import numpy as np
import pandas as pd

# package(s) for plotting
import matplotlib.pyplot as plt

# terminal_optimization package
from terminal_optimization import defaults
from terminal_optimization import mixins

# ## 1. Source
# ### System classes
# todo: we should move common properties to more general mixins

# The generic berth class
Berth = type('Berth', (mixins.identifiable_properties_mixin,      # Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.berth_properties_mixin,
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
            {})                         # The dictionary is empty because the site type is generic

# The generic crane class
Crane = type('Crane', (mixins.identifiable_properties_mixin,      # Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.cyclic_properties_mixin,
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
            {})                         # The dictionary is empty because the site type is generic

# The generic storage class
Storage = type('Storage', (mixins.identifiable_properties_mixin,  # Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.storage_properties_mixin,    
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
            {})                         # The dictionary is empty because the site type is generic

# The generic quay class
Quay = type('Quay', (mixins.identifiable_properties_mixin,        # Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.quay_wall_properties_mixin,
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
            {})                         # The dictionary is empty because the site type is generic

# The generic conveyor class
Conveyor = type('Conveyor', (mixins.identifiable_properties_mixin,# Give it a name
                       mixins.history_properties_mixin,           # Give it procurement history
                       mixins.conveyor_properties_mixin,
                       mixins.hascapex_properties_mixin,          # Give it capex info
                       mixins.hasopex_properties_mixin,           # Give it opex info
                       mixins.hasrevenue_properties_mixin,        # Give it revenue info
                       mixins.hastriggers_properties_mixin),      # Give it investment triggers (lambda?)
            {})                         # The dictionary is empty because the site type is generic

class system:
    def __init__(self, elements = [], startyear = 2019, lifecycle = 20, scenario = []):
        self.elements = elements
        self.startyear = startyear
        self.lifecycle = lifecycle
        self.scenario = scenario

    def list_elements(self, obj):
        """return elements of type obj part of self.elements"""
        list_of_elements = []
        for element in System.elements:
            if isinstance(element, obj):
                list_of_elements.append(element)

        return list_of_elements

    def quay_invest(self, year, target_quay_length):
        # *** current strategy is to add quay walls as long as target length is not yet achieved
        # find out how much quay wall is online
        
        # from all Quay objects sum online length
        list_of_elements = self.list_elements(Quay)
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
            
            df = pd.DataFrame(index=range(self.startyear,self.startyear+self.lifecycle))
            df['capex'] = 0
            df.at[year, 'capex']=quay.unit_rate
            df.at[range(year,self.startyear+self.lifecycle), 'maintenance'] = quay.unit_rate * quay.maintenance_perc
            df.at[range(year,self.startyear+self.lifecycle), 'insurance'] = quay.unit_rate * quay.insurance_perc
            quay.df = df

            self.elements.append(quay)
            # todo: add cost to cost matrix
            
            quay_length += quay.length

        print('a total of {} m of quay length is online; {} m total planned'.format(quay_length_online, quay_length))

    def storage_invest(self, year, storage_type, storage_trigger):
        # *** current strategy is to add quay walls as long as target length is not yet achieved
        # find out how much quay wall is online
        
        # from all Quay objects sum online length
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
            
            df = pd.DataFrame(index=range(self.startyear,self.startyear+self.lifecycle))
            df['capex'] = 0
            df.at[year, 'capex']=silo.unit_rate
            df.at[range(year,self.startyear+self.lifecycle), 'maintenance'] = silo.unit_rate * silo.maintenance_perc
            df.at[range(year,self.startyear+self.lifecycle), 'insurance'] = silo.unit_rate * silo.insurance_perc
            silo.df = df

            self.elements.append(silo)
            # to do: add cost to cost matrix
            
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
            
            df = pd.DataFrame(index=range(self.startyear,self.startyear+self.lifecycle))
            df['capex'] = 0
            df.at[year, 'capex']=quay.unit_rate
            df['maintenance'] = quay.unit_rate * quay.maintenance_perc
            df['insurance'] = quay.unit_rate * quay.insurance_perc
            quay.df = df

            self.elements.append(quay)
            # to do: add cost to cost matrix
            
            quay_length += quay.length

        print('a total of {} m of quay length is online; {} m total planned'.format(quay_length_online, quay_length))

    def simulate(self, startyear = 2019, lifecycle = 20):
        print('start')
        for year in range(startyear,startyear+interval):
            System.quay_invest(2020, 400)
            System.storage_invest(2020, Storage, 0.1*100000)

            timestep = year - start_year
    
            # *** for each element run investment trigger logic
            for element in self.elements:
                if isinstance(element, Berth):
                    self.berth_invest_decision_waiting(terminal.berths, terminal.cranes, vessels, terminal.allowable_waiting_time, year, timestep, operational_hours)

                if isinstance(element, Quay):
                    quay_invest_decision(System, year, target_quay_length)
                    self.quay_invest_decision(terminal.quays, terminal.berths, year, timestep)

                if isinstance(element, Berth):
                    pass

                if isinstance(element, Storage):
                    storage_type            = 'Silos'
                    terminal.storage = invest.storage_invest_decision(terminal.storage, trigger_throughput_perc, aspired_throughput_perc, storage_type, commodities, year, timestep)

                if isinstance(element, Loader):
                    # Loading stations
                    terminal.stations = invest.station_invest_decision(terminal.stations, station_utilisation, trigger_throughput_perc, aspired_throughput_perc, commodities, year, timestep, operational_hours)

                if isinstance(element, Conveyor):
                    # Conveyors
                    terminal.quay_conveyors = invest.quay_conveyor_invest_decision(terminal.quay_conveyors, terminal.cranes, year, timestep, operational_hours)
                    terminal.hinterland_conveyors = invest.hinterland_conveyor_invest_decision(terminal.hinterland_conveyors, terminal.stations, year, timestep, operational_hours)

            # Terminal throughput
            terminal = financial.throughput_calc(terminal, vessels, commodities, allowable_berth_occupancy, year, start_year, timestep, operational_hours)

            # *** for updated terminal run financial calculations
            terminal.revenues    = financial.revenue_calc(terminal.revenues, terminal.throughputs, commodities, year, timestep)
            terminal.capex       = financial.capex_calc(terminal, year, timestep)
            terminal.labour      = financial.labour_calc(terminal, year, timestep, operational_hours)
            terminal.maintenance = financial.maintenance_calc(terminal, year, timestep)
            terminal.energy      = financial.energy_calc(terminal, year, operational_hours, timestep)
            terminal.insurance   = financial.insurance_calc(terminal, year, timestep)
            terminal.lease       = financial.lease_calc(terminal, year,timestep)
            terminal.demurrage   = financial.demurrage_calc(terminal.demurrage, terminal.berths, vessels, year, timestep)
            terminal.residuals   = financial.residual_calc(terminal, year, timestep)
            terminal.profits     = financial.profit_calc(terminal, simulation_window, timestep, year, start_year)
            terminal.opex        = financial.opex_calc(terminal, year, timestep)  

        #WACC depreciated profits
        terminal.WACC_cashflows = financial.WACC_calc(terminal.project_WACC, terminal.profits, simulation_window, start_year)

        # Combine all cashflows
        terminal.cashflows = financial.cashflow_calc(terminal, simulation_window, start_year) 

        #NPV 
        terminal.NPV = financial.NPV_calc(terminal.WACC_cashflows)

        return terminal

    def plot_system(self):
        pass
    
    def NPV(self):
        pass

# ## 2. Prepare simulation objects
# start an empty system (green field terminal)
System = []
System = system(startyear = 2019, lifecycle = 20)


# ## 3. Simulate 
print(2020)
System.quay_invest(2020, 400)
System.storage_invest(2020, Storage, 0.1*100000)
print(2021)
System.quay_invest(2021, 400)
System.storage_invest(2021, Storage, 0.1*110000)
print(2022)
System.quay_invest(2022, 800)
System.storage_invest(2022, Storage, 0.1*120000)
print(2023)
System.quay_invest(2023, 1200)
System.storage_invest(2023, Storage, 0.1*130000)
print(2024)
System.quay_invest(2024, 1200)
System.storage_invest(2024, Storage, 0.1*140000)
print(2025)
System.quay_invest(2025, 1200)
System.storage_invest(2025, Storage, 0.1*150000)
