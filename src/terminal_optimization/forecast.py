
# coding: utf-8

# # # Forecast Package
#  This package includes: 
#  - Trend generator
#  - Commodity classes
#  - Vessel classes
#  - Forecast simulation
#  <br><br>
#  
# #### Object outputs
#  
#  - maize
#  - soybean
#  - wheat
#  - handysize
#  - handymax
#  - panamax

# In[1]:


import numpy as np
import pandas as pd


# # Trend Generator

# In[2]:


class estimate_trend:
    """trend estimate class"""

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


# # Commodity classes

# In[3]:


# create commodity class **will ultimately be placed in package**
class commodity_properties_mixin(object):
    def __init__(self, commodity_name, handling_fee, handysize_perc, handymax_perc,panamax_perc):
        self.commodity_name = commodity_name
        self.handling_fee   = handling_fee
        self.handysize_perc = handysize_perc
        self.handymax_perc  = handymax_perc
        self.panamax_perc   = panamax_perc
    
maize_data   = {"commodity_name": 'Maize',    "handling_fee": 10, "handysize_perc": 50, "handymax_perc": 50, "panamax_perc": 0}
soybean_data = {"commodity_name": 'Soybeans', "handling_fee": 10, "handysize_perc": 50, "handymax_perc": 50, "panamax_perc": 0}
wheat_data   = {"commodity_name": 'Wheat',    "handling_fee": 10, "handysize_perc": 0, "handymax_perc": 0, "panamax_perc": 100}


# In[ ]:


class bulk_commodities(commodity_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def modal_split(self, window):
        #fname = 'Excel_input.xlsx'
        #modal_split = pd.read_excel(fname, 'Vessel distribution')
        handysize_demand = []
        handymax_demand  = []
        panamax_demand   = []
        for i in range (window):
            handysize_demand.append(self.handysize_perc/100 * self.demand[i])
            handymax_demand.append(self.handysize_perc/100  * self.demand[i])
            panamax_demand.append(self.handysize_perc/100   * self.demand[i])
        self.handysize_demand = handysize_demand
        self.handymax_demand  = handymax_demand
        self.panamax_demand   = panamax_demand
            
    def calls_calc(self):
        self.handysize_calls = [x / handysize.call_size for x in self.handysize_demand]
        self.handymax_calls  = [x / handymax.call_size for x in self.handymax_demand]
        self.panamax_calls   = [x / panamax.call_size for x in self.panamax_demand]
        #self.handysize_calls = self.handysize_demand / handysize.call_size
        #self.handymax_calls  = self.handymax_demand  / handymax.call_size
        #self.panamax_calls   = self.panamax_demand   / panamax.call_size
        
    def linear_forecast(self, year, window, initial_demand, growth):
        trendestimate = estimate_trend(year, window, initial_demand)
        t, d = trendestimate.linear(growth)
        self.years  = t
        self.demand = d
        self.modal_split(window)
        self.calls_calc()
        if self.commodity_name == 'Wheat':
            handysize.calls_calc()
            handymax.calls_calc()
            panamax.calls_calc()
        
    def exponential_forecast(self, year, window, initial_demand, rate):
        trendestimate = estimate_trend(year, window, initial_demand)
        t, d = trendestimate.constant(rate)
        self.years  = t
        self.demand = d
        self.modal_split(window)
        self.calls_calc()
        if self.commodity_name == 'Wheat':
            handysize.calls_calc()
            handymax.calls_calc()
            panamax.calls_calc()
        
    def random_forecast(self, year, window, initial_demand, rate, mu, sigma):
        trendestimate = estimate_trend(year, window, initial_demand)
        t, d = trendestimate.random(rate, mu, sigma)
        self.years  = t
        self.demand = d
        self.modal_split(window)
        self.calls_calc()
        if self.commodity_name == 'Wheat':
            handysize.calls_calc()
            handymax.calls_calc()
            panamax.calls_calc()


# In[10]:


# create commodity objects **will ultimately be placed in notebook**
maize       = bulk_commodities(**maize_data)
soybean     = bulk_commodities(**soybean_data)
wheat       = bulk_commodities(**wheat_data)


# # Vessel classes

# In[6]:


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


# In[7]:


class vessel(vessel_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass
    
    def calls_calc(self):
        if self.vessel_type == 'Handysize':
            self.calls = maize.handysize_calls + soybean.handysize_calls + wheat.handysize_calls
        if self.vessel_type == 'Handymax':
            self.calls = maize.handymax_calls + soybean.handymax_calls + wheat.handymax_calls
        if self.vessel_type == 'Panamax':
            self.calls = maize.panamax_calls + soybean.panamax_calls + wheat.panamax_calls
            
    def berth_time_calc(self, unloading_rate):
        self.berth_time = self.call_size / unloading_rate + self.mooring_time


# In[8]:


# create objects **will ultimately be placed in notebook**
handysize = vessel(**handysize_data)
handymax  = vessel(**handymax_data)
panamax   = vessel(**panamax_data)

