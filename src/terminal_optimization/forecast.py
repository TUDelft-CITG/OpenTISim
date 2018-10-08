
# coding: utf-8

# In[2]:


import numpy as np
import pandas as pd


# # Commodity classes

# In[ ]:


# create commodity class **will ultimately be placed in package**
class commodity_properties_mixin(object):
    def __init__(self, commodity_name, handling_fee, handysize_perc, handymax_perc,panamax_perc):
        self.commodity_name = commodity_name
        self.handling_fee   = handling_fee
        self.handysize_perc = handysize_perc
        self.handymax_perc  = handymax_perc
        self.panamax_perc   = panamax_perc
    
maize_data   = {"commodity_name": 'Maize',    "handling_fee": 3.5, "handysize_perc": 50, "handymax_perc": 50, "panamax_perc": 0}
soybean_data = {"commodity_name": 'Soybeans', "handling_fee": 3.5, "handysize_perc": 50, "handymax_perc": 50, "panamax_perc": 0}
wheat_data   = {"commodity_name": 'Wheat',    "handling_fee": 3.5, "handysize_perc": 0, "handymax_perc": 0, "panamax_perc": 100}


# In[ ]:


class bulk_commodities(commodity_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass
    
    # Scenario generator
    def linear_scenario(self, year, window, initial_demand, growth):
        scenario = create_scenario(year, window, initial_demand)
        t, d = scenario.linear(growth)
        self.years  = t
        self.demand = d
        
    def exponential_scenario(self, year, window, initial_demand, rate):
        scenario = create_scenario(year, window, initial_demand)
        t, d = scenario.constant(rate)
        self.years  = t
        self.demand = d
        
    def random_scenario(self, year, window, initial_demand, rate, mu, sigma):
        scenario = create_scenario(year, window, initial_demand)
        t, d = scenario.random(rate, mu, sigma)
        self.years  = t
        self.demand = d


# # Scenario generator

# In[ ]:


class create_scenario:

    def __init__(self, year, window, initial_demand):
        """initialization"""
        self.year   = year
        self.window = window
        self.demand = initial_demand
        
    def linear(self, growth):
        """trend generated from constant growth increments"""
        years  = range(self.year, self.year + self.window)
        demand = self.demand
        t = []
        d = []
        for year in years:
            t.append(int(year))
            d.append(int(demand))
            demand = demand + growth    
        return t, d
    
    def constant(self, rate):
        """trend generated from constant growth rate increments"""
        years  = range(self.year, self.year + self.window)
        demand = self.demand
        t = []
        d = []
        for year in years:
            t.append(int(year))
            d.append(int(demand))
            demand = demand * rate    
        return t, d
    
    def random(self, rate, mu, sigma):
        """trend generated from random growth rate increments"""
        # package(s) used for probability
        years  = range(self.year, self.year + self.window)
        demand = self.demand
        rate   = rate
        t = []
        d = []
        for year in years:
            t.append(int(year))
            d.append(int(demand))
            
            change = np.random.normal(mu, sigma, 1000)
            new_rate = rate + change[0]
            demand = demand * new_rate  
        return t, d


# # Forecast generator

# In[ ]:


class create_forecast:

    def __init__(self, commodities, foresight, hindsight, timestep, year):
        """initialization"""
        self.foresight = foresight
        self.hindsight = hindsight
        self.year      = year

        
        foresight = 5
        hindsight = 5
        year = 2030
        start_year = 2018
        timestep = year - start_year

        # List historic demand
        if self.hindsight > len(commodities[0].years[timestep-self.hindsight:timestep]):
            self.hindsight = len(commodities[0].years[timestep-self.hindsight:timestep])
        historic_years = commodities[0].years[timestep-self.hindsight:timestep]
        historic_data = []
        for i in range (len(commodities)):
            historic_data.append(commodities[i].demand[timestep-self.hindsight:timestep])

        # Create linear trendline
        #trendlines = []
        #trendline_years = range (historic_years[0], historic_years[-1]+self.foresight+1, 1)
        #for i in range (len(commodities)):
        #    coefficients = np.polyfit(historic_years, historic_data[i], 1)
        #    trendline = []
        #    for t in trendline_years:
        #        trendline.append(int(t*coefficients[0] + coefficients[1]))
        #   trendlines.append(trendline)

        # Create 2nd order polynomial trendline
        trendlines = []
        trendline_years = range (historic_years[0], historic_years[-1]+self.foresight+1)
        for i in range (len(commodities)):
            coefficients = np.polyfit(historic_years, historic_data[i], 2)
            trendline = []
            for t in trendline_years:
                trendline.append(z[0]*t**2+z[1]*t+z[2])
            trendlines.append(trendline)
    
    
    
        
    def create_trendline(self):
        """trend generated from constant growth increments"""
        years  = range(self.year, self.year + self.window)
        demand = self.demand
        t = []
        d = []
        for year in years:
            t.append(year)
            d.append(demand)
            demand = demand + growth    
        return t, d
    
    def constant(self, rate):
        """trend generated from constant growth rate increments"""
        years  = range(self.year, self.year + self.window)
        demand = self.demand
        t = []
        d = []
        for year in years:
            t.append(year)
            d.append(demand)
            demand = demand * rate    
        return t, d
    
    def random(self, rate, mu, sigma):
        """trend generated from random growth rate increments"""
        # package(s) used for probability
        years  = range(self.year, self.year + self.window)
        demand = self.demand
        rate   = rate
        t = []
        d = []
        for year in years:
            t.append(year)
            d.append(demand)
            
            change = np.random.normal(mu, sigma, 1000)
            new_rate = rate + change[0]
            demand = demand * new_rate  
        return t, d


# # Vessel classes

# In[1]:


# create vessel class **will ultimately be placed in package**
class vessel_properties_mixin(object):
    def __init__(self, vessel_type, call_size, LOA, draft, beam, max_cranes, all_turn_time, mooring_time, demurrage_rate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.vessel_type   = vessel_type
        self.call_size     = call_size 
        self.LOA           = LOA
        self.draft         = draft
        self.beam          = beam
        self.max_cranes    = max_cranes
        self.all_turn_time = all_turn_time
        self.mooring_time  = mooring_time
        self.demurrage_rate= demurrage_rate
        
# Initial data set, data from Excel_input.xlsx
handysize_data = {"vessel_type": 'Handysize', "call_size": 35000, 
                  "LOA": 130, "draft": 10, "beam": 24, "max_cranes": 2, 
                  "all_turn_time": 24, "mooring_time": 3, "demurrage_rate": 600}

handymax_data = {"vessel_type": 'Handymax', "call_size": 50000, 
                  "LOA": 180, "draft": 11.5, "beam": 28, "max_cranes": 2, 
                  "all_turn_time": 24, "mooring_time": 3, "demurrage_rate": 750}

panamax_data = {"vessel_type": 'Panamax', "call_size": 65000, 
                  "LOA": 220, "draft": 13, "beam": 32.2, "max_cranes": 3, 
                  "all_turn_time": 36, "mooring_time": 4, "demurrage_rate": 730} 


# In[ ]:


class vessel(vessel_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


# In[ ]:


def vessel_call_calc(vessels, commodities, simulation_window):
    
    for i in range (len(vessels)):
        calls = []
        for t in range(simulation_window):
            commodity_specific_demand = []
            for j in range(len(commodities)):
                if i == 0:
                    percentage = commodities[j].handysize_perc/100
                if i == 1:
                    percentage = commodities[j].handymax_perc/100
                if i == 2:
                    percentage = commodities[j].panamax_perc/100  
                commodity_specific_demand.append(commodities[j].demand[t] * percentage)
            calls.append(int(np.ceil(np.sum(commodity_specific_demand)/vessels[i].call_size)))
        vessels[i].calls = calls
        
    return vessels

