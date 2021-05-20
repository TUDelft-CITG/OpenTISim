
# coding: utf-8

# In[4]:


# package(s) for data handling
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .hydrogen_defaults import *
from .hydrogen_objects import *
import opentisim

class EndUseLocation:
    """This class implements the 'complete supply chain' concept (Van Koningsveld et al, 2021) for liquid bulk
    terminals. The module allows variation of the commodity type, the storage type and the h2conversion type.
    Terminal development is governed by three triggers: the allowable waiting time as factor of service time,
    the allowable dwell time and an h2conversion trigger."""

    def __init__(self, startyear=2020, lifecycle=10, operational_hours=5840, debug=False, elements=[],
                 terminal_supply_chain={'storage','h2_retrieval'},
                 commodity_type_defaults=commodity_ammonia_data,
                 storage_type_defaults=storage_nh3_data,
                 kendall='E2/E2/n',
                 h2retrieval_type_defaults=h2retrieval_nh3_data,
                 allowable_dwelltime=15 / 365, 
                 h2retrieval_trigger=1):
        
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

        # triggers for the various elements (berth, storage and h2conversion)
        self.allowable_dwelltime = allowable_dwelltime
        self.h2retrieval_trigger = h2retrieval_trigger

        # storage variables for revenue
        #self.revenues = []
        
        # input testing: vessel percentages should add up to 100

#         commodities = opentisim.core.find_elements(self, Commodity)
#         for commodity in commodities:
#             np.testing.assert_equal(commodity.smallhydrogen_perc + commodity.largehydrogen_perc + commodity.largeammonia_perc + commodity.largeammonia_perc  + commodity.handysize_perc + commodity.panamax_perc + commodity.vlcc_perc, 100, 
#             'error: all vessel percentages should add up to 100')

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

            # 1. for each year estimate the volume that is deliverd based on the demand
            #smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls,             handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol,             smallhydrogen_calls_planned, largehydrogen_calls_planned,             smallammonia_calls_planned, largeammonia_calls_planned,             handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned,             total_calls_planned, total_vol_planned = self.calculate_vessel_calls(year)
            
            hydrogen_defaults_h2retrieval_data = self.h2retrieval_type_defaults
            hydrogen_defaults_storage_data = self.storage_type_defaults
            
            h2retrieval = H2retrieval(**hydrogen_defaults_h2retrieval_data)
            plantloss = h2retrieval.losses
            
            if self.place == 'centralized':
                storloss = 0
            if self.place == 'decentralized': 
                storage = Storage(**hydrogen_defaults_storage_data)
                storloss = (storage.losses) * ((self.allowable_dwelltime) *365)
        

            commodities = opentisim.core.find_elements(self, Commodity)
            for commodity in commodities:
                try:
                    volume = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                    volume_transport_out = (volume*(100+(plantloss+storloss)))/100
                except:
                    pass

            if self.debug:
                print('--- Cargo volume for {} ---------'.format(year))
                print('  Total demand volume transport out: {}'.format(volume_transport_out))
                print('----------------------------------------------------')

            # 2. for each year evaluate which investment are needed given the strategic and operational objectives
            if 'storage' in self.terminal_supply_chain:
                if self.debug:
                    print('')
                    print('$$$ Check storage ----------------------------------')
                self.storage_invest(year, self.storage_type_defaults)

            if 'h2_retrieval' in self.terminal_supply_chain:
                if self.debug:
                    print('')
                    print('$$$ Check H2 retrieval plants ----------------------')
                self.h2retrieval_invest(year, self.h2retrieval_type_defaults)

        # 3. for each year calculate the energy costs (requires insight in realized demands)
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_energy_cost(year)

        # 5.  for each year calculate terminal revenues
        if self.lifecycle > 1: 
            self.revenues = []
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.calculate_revenue(year, self.commodity_type_defaults)

        # 6. for each year calculate the throughput (requires insight in realized demands)
        self.throughputonline = []
        for year in range(self.startyear, self.startyear + self.lifecycle):
            self.throughput_elements(year)
            
            throughput_online, throughput_terminal_in,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,  throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in,Demand_jetty_in = self.throughput_elements(year)
            
            throughput_plant_in = throughput_online_plant_in
            throughput_storage_in = throughput_online_stor_in
    
            if self.debug:
                print('--- Throughput online and in elements for {} ---------'.format(year))
                print('  Total demand at end-use: {}'.format(Demand))
                print('  Total demand plant in: {}'.format(Demand_plant_in))
                print('  Total demand storage in: {}'.format(Demand_storage_in))

                print('  Total throughput online at end-use: {}'.format(throughput_online))
                print('  Total throughput online plant in: {}'.format(throughput_plant_in))
                print('  Total throughput online storage in: {}'.format(throughput_storage_in))
                print('----------------------------------------------------')

        # # 7. collect all cash flows (capex, opex, revenues)
        # cash_flows, cash_flows_WACC_nominal = self.add_cashflow_elements()

        # 8. calculate PV's and aggregate to NPV
        #opentisim.core.NPV(self, Labour(**labour_data))

    # *** Individual investment methods for terminal elements
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
                if element.type == hydrogen_defaults_storage_data['type']:
                    storage_capacity += element.capacity
                    if year >= element.year_online:
                        storage_capacity_online += element.capacity

        if self.debug:
            print('     a total of {} ton of {} storage capacity is online; {} ton total planned'.format(
                storage_capacity_online, hydrogen_defaults_storage_data['type'], storage_capacity))

        # max_vessel_call_size = max([x.call_size for x in opentisim.core.find_elements(self, Vessel)])
        for commodity in opentisim.core.find_elements(self, Commodity):
            if commodity.type == 'MCH': 
                max_vessel_call_size = MCH_barge_data["call_size"]
            elif commodity.type == 'DBT': 
                max_vessel_call_size = DBT_barge_data["call_size"]
            elif commodity.type == 'Liquid hydrogen':
                max_vessel_call_size = hydrogen_barge_data["call_size"]
            else:
                max_vessel_call_size = ammonia_barge_data["call_size"]
        

        # find the total throughput
        throughput_online, throughput_terminal_in,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,  throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in,Demand_jetty_in = self.throughput_elements(year)

        storage_capacity_dwelltime_demand = (Demand_storage_in * self.allowable_dwelltime) * 1.1  # IJzerman p.26

        storage_capacity_dwelltime_throughput = (throughput_planned_storage * self.allowable_dwelltime) * 1.1  # IJzerman p.26
        #  or
        # check if sufficient storage capacity is available
        while storage_capacity < max_vessel_call_size or storage_capacity < storage_capacity_dwelltime_demand:
        #(
#                 storage_capacity < storage_capacity_dwelltime_demand and storage_capacity < storage_capacity_dwelltime_throughput):
            if self.debug:
                print('  *** add storage to elements')

            # add storage object
            storage = Storage(**hydrogen_defaults_storage_data)

            # - capex
            storage.capex = storage.unit_rate + storage.mobilisation_min

            # - opex
            storage.insurance = storage.unit_rate * storage.insurance_perc
            storage.maintenance = storage.unit_rate * storage.maintenance_perc
            
            storage.capex_material = 0 
            storage.purchaseH2 = 0 
            storage.purchase_material = 0 

            #   labour**hydrogen_defaults
            labour = Labour(**labour_data)
            storage.shift = (
                        (storage.crew_for5 * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            storage.labour = storage.shift * labour.operational_salary

#             jettys = opentisim.core.find_elements(self, opentisim.liquidbulk.Jetty)
#             jetty_year_online = 0
#             for jetty in jettys:
#                 jetty_year_online = np.max([jetty_year_online, jetty.year_online])

#             storage.year_online = np.max([jetty_year_online, year + storage.delivery_time])

            storage.year_online = year + storage.delivery_time

            # residual
            storage.assetvalue = storage.unit_rate * (
                        1 - ((self.years[0] + len(self.years) - storage.year_online) / storage.lifespan))
                        #1 - ((self.lifecycle + self.startyear - storage.year_online) / storage.lifespan))
            storage.residual = max(storage.assetvalue, 0)

            # add cash flow information to storage object in a dataframe
            storage = opentisim.core.add_cashflow_data_to_element(self, storage)

            self.elements.append(storage)
            
            storage_capacity += storage.capacity

            if self.debug:
                print('     a total of {} ton of {} storage capacity is online; {} ton total planned'.format(
                    storage_capacity_online, hydrogen_defaults_storage_data['type'], storage_capacity))
        
    def h2retrieval_invest(self, year, hydrogen_defaults_h2retrieval_data):
#     """current strategy is to add h2 retrieval as long as target h2 retrieval is not yet achieved
#     - find out how much h2 retrieval is online
#     - find out how much h2 retrieval is planned
#     - find out how much h2 retrieval is needed
#     - add h2 retrieval until target is reached
#     """

        plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(year, hydrogen_defaults_h2retrieval_data)

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

            h2retrieval.capex_material = 0 
            h2retrieval.purchaseH2 = 0 
            h2retrieval.purchase_material = 0

            #   labour**hydrogen_defaults
            labour = Labour(**labour_data)
            h2retrieval.shift = (
                        (h2retrieval.crew_for5 * self.operational_hours) / (labour.shift_length * labour.annual_shifts))
            h2retrieval.labour = h2retrieval.shift * labour.operational_salary

            #jetty = Jetty(**jetty_data)

    #         jettys = opentisim.core.find_elements(self, opentisim.liquidbulk.Jetty)
    #         jetty_year_online = 0
    #         for jetty in jettys:
    #             jetty_year_online = np.max([jetty_year_online, jetty.year_online])

    #         h2retrieval.year_online = np.max([jetty_year_online, year + h2retrieval.delivery_time])
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

    def calculate_energy_cost(self, year):
        """
        The energy cost of all different element are calculated.
        1. At first find the consumption, capacity and working hours per element
        2. Find the total energy price to multiply the consumption with the energy price
        """

        energy = Energy(**energy_data)
        
        throughput_online, throughput_terminal_in,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,  throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in,Demand_jetty_in = self.throughput_elements(year)

        hydrogen_defaults_h2retrieval_data = self.h2retrieval_type_defaults
        hydrogen_defaults_storage_data = self.storage_type_defaults

        # calculate storage energy
        for commodity in opentisim.core.find_elements(self, Commodity):
            if commodity.type == 'MCH': 
                max_vessel_call_size = MCH_barge_data["call_size"]
            elif commodity.type == 'DBT': 
                max_vessel_call_size = DBT_barge_data["call_size"]
            elif commodity.type == 'Liquid hydrogen':
                max_vessel_call_size = hydrogen_barge_data["call_size"]
            else:
                max_vessel_call_size = ammonia_barge_data["call_size"]
        
        
        list_of_elements_Storage = opentisim.core.find_elements(self, Storage)

        throughput_online, throughput_terminal_in,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,  throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in,Demand_jetty_in = self.throughput_elements(year)

        #throughput_online_storage = (throughput_online*(100+(plantloss+storloss)))/100
#         throughput_online_storage = throughput_online_stor_in
        
#         storage_capacity_dwelltime_throughput = (throughput_online_storage * self.allowable_dwelltime) * 1.1

#         for element in list_of_elements_Storage:
#             if year >= element.year_online:
#                 consumption = element.consumption
#                 hours = self.operational_hours
#                 capacity = max(max_vessel_call_size, storage_capacity_dwelltime_throughput)

#                 if consumption * capacity * hours * energy.price != np.inf:
#                     element.df.loc[element.df['year'] == year, 'energy'] = consumption * capacity * energy.price

#             else:
#                 element.df.loc[element.df['year'] == year, 'energy'] = 0

        storage_occupancy_planned, storage_occupancy_online, storage_capacity_planned, storage_capacity_online = self.calculate_storage_occupancy(year, hydrogen_defaults_storage_data)
        
        list_of_elements_Storage = opentisim.core.find_elements(self, Storage)
        
        for element in list_of_elements_Storage:
            if year >= element.year_online:
                consumption = element.consumption
                capacity = element.capacity #* self.operational_hours
                yearly_capacity = (365/((self.allowable_dwelltime * 365)*1.1))*capacity 
                #capacityH2 = (capacity * Hcontent) / 100
                
                if consumption * throughput_online * energy.price != np.inf:
                    element.df.loc[element.df[
                                       'year'] == year, 'energy'] = consumption * storage_occupancy_online * yearly_capacity * energy.price
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0
        
        
        # calculate H2 retrieval energy
        list_of_elements_H2retrieval = opentisim.core.find_elements(self, H2retrieval)

        # find the total throughput,
        # throughput_online, throughput_planned, throughput_planned_jetty, throughput_planned_pipej, throughput_planned_storage, throughput_planned_h2retrieval, throughput_planned_pipeh = self.throughput_elements(year)
        hydrogen_defaults_h2retrieval_data = self.h2retrieval_type_defaults
        plant_occupancy_planned, plant_occupancy_online, h2retrieval_capacity_planned, h2retrieval_capacity_online = self.calculate_h2retrieval_occupancy(
            year, hydrogen_defaults_h2retrieval_data)
        
        commodities = opentisim.core.find_elements(self,Commodity)
        for commodity in commodities:
            Hcontent = commodity.Hcontent

        for element in list_of_elements_H2retrieval:
            if year >= element.year_online:
                consumption = element.consumption
                capacity = element.capacity * self.operational_hours
                capacityH2 = (capacity * Hcontent) / 100
                
                if consumption * throughput_online * energy.price != np.inf:
                    element.df.loc[element.df[
                                       'year'] == year, 'energy'] = consumption * plant_occupancy_online * capacityH2 * energy.price
            else:
                element.df.loc[element.df['year'] == year, 'energy'] = 0
    
    def calculate_revenue(self, year, hydrogen_defaults_commodity_data):
        """
        1. calculate the value of the total throughput in year (throughput * handling fee)
        """

        # gather the fee from the selected commodity
        commodity = Commodity(**hydrogen_defaults_commodity_data)
        fee = commodity.handling_fee

        throughput_online, throughput_terminal_in,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,  throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in,Demand_jetty_in = self.throughput_elements(year)
        
        if self.debug:
            print('     Revenues: {}'.format(int(throughput_online * fee)))

        try:
            self.revenues.append(throughput_online * fee)
        except:
            pass
 
    def calculate_storage_occupancy(self, year, hydrogen_defaults_storage_data):
        """
        - Divide the throughput by the service rate to get the total hours in a year
        - Occupancy is total_time_at_h2retrieval divided by operational hours
        """
        # Find throughput
        throughput_online, throughput_terminal_in,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,  throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in,Demand_jetty_in = self.throughput_elements(year)

        hydrogen_defaults_h2retrieval_data = self.h2retrieval_type_defaults
        hydrogen_defaults_storage_data = self.storage_type_defaults

        # find the total service rate and determine the time at h2retrieval
        storage_capacity_planned = 0
        storage_capacity_online = 0

        storage = Storage(**hydrogen_defaults_storage_data)
        capacity = storage.capacity

        #yearly_capacity = capacity * self.operational_hours

        list_of_elements = opentisim.core.find_elements(self, Storage)
        if list_of_elements != []:
            for element in list_of_elements:
                storage_capacity_planned += capacity
                if year >= element.year_online:
                    storage_capacity_online += capacity

            # h2retrieval_occupancy is the total time at h2retrieval divided by the operational hours
            Demand_stor_in_dwell = (Demand_storage_in * self.allowable_dwelltime)*1.1
            storage_occupancy_planned = Demand_stor_in_dwell / storage_capacity_planned

            if storage_capacity_online != 0:
                #throughput_online_plant_in = (throughput_online * (100+(plantloss)))/100
                throughput_online_stor_in_dwell = (throughput_online_stor_in * self.allowable_dwelltime)*1.1
                time_at_storage_online = throughput_online_stor_in_dwell / storage_capacity_online  # element.capacity

                # h2retrieval occupancy is the total time at h2retrieval divided by the operational hours
                storage_occupancy_online = min([time_at_storage_online, 1])
            else:
                storage_occupancy_online = float("inf")

        else:
            # if there are no cranes the berth occupancy is 'infinite' so a berth is certainly needed
            storage_occupancy_planned = float("inf")
            storage_occupancy_online = float("inf")

        return storage_occupancy_planned, storage_occupancy_online, storage_capacity_planned, storage_capacity_online
    
    def calculate_h2retrieval_occupancy(self, year, hydrogen_defaults_h2retrieval_data):
        """
        - Divide the throughput by the service rate to get the total hours in a year
        - Occupancy is total_time_at_h2retrieval divided by operational hours
        """
        # Find throughput
        throughput_online, throughput_terminal_in,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,  throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in,Demand_jetty_in = self.throughput_elements(year)

        hydrogen_defaults_h2retrieval_data = self.h2retrieval_type_defaults
        hydrogen_defaults_storage_data = self.storage_type_defaults


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
            
            plant_occupancy_planned = Demand_plant_in / h2retrieval_capacity_planned

            if h2retrieval_capacity_online != 0:
                #throughput_online_plant_in = (throughput_online * (100+(plantloss)))/100
                time_at_plant_online = throughput_online_plant_in / h2retrieval_capacity_online  # element.capacity

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
        plant_capacity_planned = 0
        plant_capacity_online = 0
        list_of_elements = opentisim.core.find_elements(self, H2retrieval)
        if list_of_elements != []:
            for element in list_of_elements:
                plant_capacity_planned += element.capacity * self.operational_hours
                if year >= element.year_online:
                    plant_capacity_online += element.capacity * self.operational_hours
        
        hydrogen_defaults_h2retrieval_data = self.h2retrieval_type_defaults
        hydrogen_defaults_storage_data = self.storage_type_defaults
        
        h2retrieval = H2retrieval(**hydrogen_defaults_h2retrieval_data)
        plantloss = h2retrieval.losses
        
        if self.place == 'centralized':
                storloss = 0
        if self.place == 'decentralized': 
            storage = Storage(**hydrogen_defaults_storage_data)
            storloss = storage.losses  * ((self.allowable_dwelltime) *365)
            
        fullarray = [0, 0]
        for element in self.terminal_supply_chain:
            if element == 'storage':
                fullarray[0] = 1
            elif element == 'h2_retrieval':
                fullarray[1] = 1 

        if fullarray[1] == 0: 
            plantloss = 0 
        if fullarray[0] == 0:
            #Demand = Demand_storage_in
            storloss = 0 

                # Find demand
        Demand = []
        for commodity in opentisim.core.find_elements(self, Commodity):
            try:
                Demand = commodity.scenario_data.loc[commodity.scenario_data['year'] == year]['volume'].item()
                Demand_plant_in = (Demand*(100+plantloss))/100
                Demand_storage_in = (Demand*(100+(plantloss+storloss)))/100
            except:
                print('problem occurs at {}'.format(year))
                pass

        x = np.array(fullarray)
        t = np.where(x == 0)[0]
        t1 = t.tolist()
        t1.sort(reverse = True)#places where value is zero in array
        

        storage_cap_planned_end = (storage_cap_planned *100)/(100+(plantloss+storloss))
        plant_capacity_planned_end = (plant_capacity_planned *100)/(100+(plantloss))

        storage_cap_online_end = (storage_cap_online *100)/(100+(plantloss+storloss))
        plant_capacity_online_end = (plant_capacity_online *100)/(100+(plantloss))
                
        array_planned =[storage_cap_planned_end, plant_capacity_planned_end , Demand]
        array_online = [storage_cap_online_end, plant_capacity_online_end, Demand] 
        #print(array_online)
        #print(array_online)

        for i in t1:
            array_planned.pop(i)
            array_online.pop(i)            
            
        throughput_planned = min(array_planned)
        throughput_online = min(array_online) 
                           
        throughput_planned_storage = 0 
        throughput_planned_plant = 0 
        #throughput_planned_pipeh = 0 
        
        stor = list.copy(array_planned)
        h2plant = list.copy(array_planned)
        
        if fullarray[0] == 1:
            stor.pop(0)
            throughput_planned_storage = min(stor)
        if fullarray[1] == 1:
            h2plant.pop(1)
            throughput_planned_plant = min(h2plant)
        
         
        
        throughput_online_stor_in = (throughput_online*(100+(plantloss+storloss)))/100
        throughput_online_plant_in = (throughput_online*(100+(plantloss)))/100
        
        throughput_terminal_in = throughput_online_stor_in
        
        throughput_online_jetty_in = throughput_online_stor_in
        throughput_planned_jetty = 0
        throughput_planned_pipej = 0 
        Demand_jetty_in = Demand_storage_in
        

        return throughput_online, throughput_terminal_in,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,  throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in,Demand_jetty_in 
  
       
        self.throughput.append(throughput_online)
        
    def terminal_elements_plot(self, width=0.2, alpha=0.6, fontsize=20):
        """Gather data from Terminal and plot which elements come online when"""

        # collect elements to add to plot
        years = self.years
        storages = []
        h2retrievals = []
        throughputs_online = []

        # matplotlib.rcParams.update({'font.size': 18})

        for year in self.years:
            storages.append(0)
            h2retrievals.append(0)
            throughputs_online.append(0)
            
            for element in self.elements:
                if isinstance(element, Storage):
                    if year >= element.year_online:
                        storages[-1] += 1
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        h2retrievals[-1] += 1


        # generate plot
        fig, ax1 = plt.subplots(figsize=(20, 10))

        ax1.bar([x + 0 * width for x in years], storages, width=width, alpha=alpha, label="Storages", color='#9edae5',
                edgecolor='darkgrey')
        ax1.bar([x + 1 * width for x in years], h2retrievals, width=width, alpha=alpha, label="H2 retrievals",
                color='#DBDB8D', edgecolor='darkgrey')


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
                throughput_online, throughput_terminal_in,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej,  throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in,Demand_jetty_in = self.throughput_elements(year)
            except:
                throughput_online = 0
                pass

            for element in self.elements:
                if isinstance(element, H2retrieval):
                    if year >= element.year_online:
                        throughputs_online[-1] = throughput_online

        # Making a second graph
        ax2 = ax1.twinx()

        dem = demand['year'].values[~np.isnan(demand['year'].values)]
        values = demand['demand'].values[~np.isnan(demand['demand'].values)]
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
        max_elements = max([max(storages), max(h2retrievals)])

        #ax1.set_yticks([x for x in range(0, max_elements + 1 + 2, 2)])
        #ax1.set_yticklabels([int(x) for x in range(0, max_elements + 1 + 2, 2)])
#, fontsize=fontsize)

        # print legend
        fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=4, fontsize=fontsize)
        fig.subplots_adjust(bottom=0.2)

