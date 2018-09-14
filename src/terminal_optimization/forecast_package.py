
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


# create trend estimating class **will ultimately be placed in package**

class estimate_trend:
    """trend estimate class"""

    def __init__(self, year, window, demand, growth, rate, mu, sigma):
        """initialization"""
        self.year   = year
        self.window = window
        self.demand = demand
        self.growth = growth
        self.rate   = 1 + rate/100
        self.mu     = mu/100
        self.sigma  = sigma/100
        
    def linear(self):
        """trend generated from constant growth increments"""
        years  = range(self.year, self.year + self.window)
        demand = self.demand
        growth = self.growth
        t = []
        d = []
        for year in years:
            t.append(year)
            d.append(demand)
            demand = demand + growth    

        return t, d
    
    def constant(self):
        """trend generated from constant growth rate increments"""
        years  = range(self.year, self.year + self.window)
        demand = self.demand
        rate   = self.rate
        t = []
        d = []
        for year in years:
            t.append(year)
            d.append(demand)
            demand = demand * rate    

        return t, d
    
    def random(self):
        """trend generated from random growth rate increments"""
        # package(s) used for probability
        import numpy as np

        years  = range(self.year, self.year + self.window)
        demand = self.demand
        rate   = self.rate
        t = []
        d = []
        for year in years:
            t.append(year)
            d.append(demand)
            
            change = np.random.normal(self.mu, self.sigma, 1000)
            rate = rate + change[0]
            
            demand = demand * rate    

        return t, d
    
    def print(self, t, d):
        """simpel print statement of estimated trend"""
        print(t)
        print(d)
        
    def plot(self, t, d):
        """simpel plot of estimated trend"""
        plt.plot(t, d, 'ro')
        plt.show()


# # Commodity classes

# In[3]:


# create commodity class **will ultimately be placed in package**
class commodity_properties_mixin(object):
    def __init__(self, commodity_name, handling_fee):
        self.commodity_name = commodity_name
        self.handling_fee   = handling_fee
    
maize_data   = {"commodity_name": 'Maize',    "handling_fee": 10}
soybean_data = {"commodity_name": 'Soybeans', "handling_fee": 10}
wheat_data   = {"commodity_name": 'Wheat',    "handling_fee": 10}


# In[17]:


# define commodity functions **will ultimately be placed in package**
class bulk_commodities(commodity_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass
    
    def generate_trend(self, trend_type, year, window, demand, growth, rate, mu, sigma):
        trendestimate = estimate_trend(year, window, demand, growth, rate, mu, sigma)
        if trend_type == 'linear':
            t, d = trendestimate.linear()  # linear trend generator
        if trend_type == 'constant':
            t, d = trendestimate.constant()  # constant growth trend generator
        if trend_type == 'probabilistic':
            t, d = trendestimate.random()  # probabilistic trend generator
        self.years  = t
        self.demand = d
        self.forecast_start  = t[0]
        self.forecast_stop   = t[len(t)-1]
        
    def modal_split(self):
        #fname = 'Excel_input.xlsx'
        fname = 'C:\\Checkouts\\Terminal_optimization\\notebooks\\Excel_input.xlsx'
        modal_split = pd.read_excel(fname, 'Vessel distribution')
        if self.commodity_name == "Maize":
            self.handysize_demand = modal_split["Handysize maize"]    * self.demand
            self.handymax_demand  = modal_split["Handymax maize"]     * self.demand
            self.panamax_demand   = modal_split["Panamax maize"]      * self.demand
        if self.commodity_name == "Soybeans":
            self.handysize_demand = modal_split["Handysize soybeans"] * self.demand
            self.handymax_demand  = modal_split["Handymax soybeans"]  * self.demand
            self.panamax_demand   = modal_split["Panamax soybeans"]   * self.demand
        if self.commodity_name == "Wheat":
            self.handysize_demand = modal_split["Handysize wheat"]    * self.demand
            self.handymax_demand  = modal_split["Handymax wheat"]     * self.demand
            self.panamax_demand   = modal_split["Panamax wheat"]      * self.demand
            
    def calls_calc(self):
        self.handysize_calls = self.handysize_demand / handysize.call_size
        self.handymax_calls  = self.handymax_demand  / handymax.call_size
        self.panamax_calls   = self.panamax_demand   / panamax.call_size
        
    def generate_forecast(self, trend_type, year, window, demand, growth, rate, mu, sigma):
        self.generate_trend(trend_type, year, window, demand, growth, rate, mu, sigma)
        self.modal_split()
        self.calls_calc()
        if self.commodity_name == 'Wheat':
            handysize.calls_calc()
            handymax.calls_calc()
            panamax.calls_calc()


# In[10]:


# create commodity objects **will ultimately be placed in notebook**
maize   = bulk_commodities(**maize_data)
soybean = bulk_commodities(**soybean_data)
wheat   = bulk_commodities(**wheat_data)


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


# define vessel class functions **will ultimately be placed in package**
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


# In[8]:


# create objects **will ultimately be placed in notebook**
handysize = vessel(**handysize_data)
handymax  = vessel(**handymax_data)
panamax   = vessel(**panamax_data)

