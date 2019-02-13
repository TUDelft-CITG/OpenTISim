
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# # Commodity classes

# In[2]:


# create commodity class **will ultimately be placed in package**
class commodity_properties_mixin(object):
    def __init__(self, commodity_name, handling_fee, handysize_perc, handymax_perc, panamax_perc, utilization):
        self.commodity_name = commodity_name
        self.handling_fee   = handling_fee
        self.handysize_perc = handysize_perc
        self.handymax_perc  = handymax_perc
        self.panamax_perc   = panamax_perc
        self.utilization    = utilization
    
maize_data   = {"commodity_name": 'Maize',    "handling_fee": 9.80, "handysize_perc": 0, "handymax_perc": 100, "panamax_perc": 0, "utilization": 0.85}
soybean_data = {"commodity_name": 'Soybeans', "handling_fee": 9.80, "handysize_perc": 0, "handymax_perc": 100, "panamax_perc": 0, "utilization": 0.85}
wheat_data   = {"commodity_name": 'Wheat',    "handling_fee": 9.80, "handysize_perc": 0, "handymax_perc": 100, "panamax_perc": 0, "utilization": 0.85}


# In[3]:


class bulk_commodities(commodity_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass
    
    # Scenario generator
    def linear_scenario(self, year, window, historic_demand, growth):
        scenario = create_scenario(year, window, historic_demand)
        t, d = scenario.linear(growth)
        self.years  = t
        self.demand = d
        
    def exponential_scenario(self, year, window, historic_demand, rate):
        scenario = create_scenario(year, window, historic_demand)
        t, d = scenario.constant(rate)
        self.years  = t
        self.demand = d
        
    def random_scenario(self, year, window, historic_demand, rate, sigma):
        scenario = create_scenario(year, window, historic_demand)
        t, d = scenario.random(rate, sigma)
        self.years  = t
        self.demand = d
        
    def predefined_scenario(self, year, window, historic_demand, predefined_demand):
        scenario = create_scenario(year, window, historic_demand)
        t, d = scenario.predefined(predefined_demand)
        self.years  = t
        self.demand = d


# # Scenario generator
# - Linear
# - Exponential
# - Exponential using standard deviation
# - Predefined

# In[4]:


class create_scenario:

    def __init__(self, year, window, historic_demand):
        """initialization"""
        self.year   = year
        self.window = window
        self.historic_demand = historic_demand
        self.historic_years = []
        
        for t in range((year-len(self.historic_demand)), year):
            self.historic_years.append(t)  
        
    def linear(self, growth):
        """trend generated from constant growth increments"""
        years  = range(self.year, self.year + self.window)
        demand = self.historic_demand[-1]
        t = []
        d = []
        
        # add historic data
        for i in range(len(self.historic_demand)):
            t.append(self.historic_years[i])
            d.append(self.historic_demand[i])
            
        # create scenario
        for year in years:
            t.append(int(year))
            d.append(int(demand))
            demand = demand + growth    
        return t, d
    
    def constant(self, rate):
        """trend generated from constant growth rate increments"""
        years  = range(self.year, self.year + self.window)
        demand = self.historic_demand[-1]
        t = []
        d = []
        
        # add historic data
        for i in range(len(self.historic_demand)):
            t.append(self.historic_years[i])
            d.append(self.historic_demand[i])
            
        # create scenario
        for year in years:
            t.append(int(year))
            d.append(int(demand))
            demand = demand * rate    
        return t, d
    
    def random(self, rate, sigma):
        """trend generated from random growth rate increments"""
        # package(s) used for probability
        years  = range(self.year, self.year + self.window)
        demand = self.historic_demand[-1]
        rate   = rate
        t = []
        d = []
        
        # add historic data
        for i in range(len(self.historic_demand)):
            t.append(self.historic_years[i])
            d.append(self.historic_demand[i])
            
        # create scenario
        for year in years:
            t.append(int(year))
            d.append(int(demand))
            change = np.random.normal(rate, sigma, 1000)
            new_rate = change[0]
            demand = demand * new_rate  
        return t, d
    
    def predefined(self, predefined_demand):
        """trend generated from random growth rate increments"""
        years  = range(self.year, self.year + self.window)
        demand = self.historic_demand[-1]
        t = []
        d = []
        
        # add historic data
        for i in range(len(self.historic_demand)):
            t.append(self.historic_years[i])
            d.append(self.historic_demand[i])
            
        # create scenario
        for year in years:
            t.append(int(year))
            d.append(int(predefined_demand[year - self.year]))
        return t, d


# # Forecast generator
# - Perfect foresight method 
# - Current performance method

# In[5]:


def forecaster(design_method, forecast_type, commodities, forecast_t, hindcast_t, timestep):
    
    maize = commodities[0]
    index = len(maize.historic) + timestep
    year  = maize.years[index]
    start_year = maize.years[index - timestep]
    
    if year >= start_year:

        # Forecast and hindcast data
        hindcast_volumes = maize.demand[index-hindcast_t:index+1]
        hindcast_years   = maize.years[index-hindcast_t:index+1]
        forecast_years   = maize.years[index:index+forecast_t+1]

        # Create forecast (linear approach)
        coefficients = np.polyfit(hindcast_years, hindcast_volumes, 1)
        trendline = []
        for t in forecast_years:
            if t == forecast_years[0]:
                trendline.append(maize.demand[index])
            else:
                trendline.append(int(coefficients[0]*t + coefficients[1]))
        forecastlinear = trendline

        # When assuming perfect foresight, the forecast is identical to the guaranteed future traffic volumes
        if design_method == 'Perfect foresight method':   
            maize.forecast = maize.demand[index:index+forecast_t+1]
        else:
            maize.forecast = forecastlinear

        # Log forecats
        if timestep == 0:
            maize.forecastlog = []
            maize.forecastyears = []
            for i in range(forecast_t+1):
                maize.forecastlog.append(maize.forecast[i])
                maize.forecastyears.append(forecast_years[i])   
        if timestep != 0:
            maize.forecastlog.append(maize.forecast[-1])
            maize.forecastyears.append(forecast_years[-1])
    
    return commodities


# In[6]:


def ARIMA_forecaster(design_method, forecast_type, commodities, forecast_t, hindcast_t, timestep):
    
    maize = commodities[0]
    index = len(maize.historic) + timestep
    year  = maize.years[index]
    start_year = maize.years[index - timestep]
    
    if year >= start_year:

        # Forecast and hindcast data
        hindcast_volumes = maize.demand[index-hindcast_t:index+1]
        hindcast_years   = maize.years[index-hindcast_t:index+1]
        forecast_years   = maize.years[index:index+forecast_t+1]

        # Create forecast (linear approach)
        coefficients = np.polyfit(hindcast_years, hindcast_volumes, 1)
        trendline = []
        for t in forecast_years:
            if t == forecast_years[0]:
                trendline.append(maize.demand[index])
            else:
                trendline.append(int(coefficients[0]*t + coefficients[1]))
        forecastlinear = trendline

        # When assuming perfect foresight, the forecast is identical to the guaranteed future traffic volumes
        if design_method == 'Perfect foresight method':   
            maize.forecast = maize.demand[index:index+forecast_t+1]
        else:
            maize.forecast = forecastlinear

        # Log forecats
        if timestep == 0:
            maize.forecastlog = []
            maize.forecastyears = []
            for i in range(forecast_t+1):
                maize.forecastlog.append(maize.forecast[i])
                maize.forecastyears.append(forecast_years[i])   
        maize.forecastlog.append(maize.forecast[-1])
        maize.forecastyears.append(forecast_years[-1])
    
    return commodities


# # Vessel classes

# In[7]:


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
                  "all_turn_time": 24, "mooring_time": 3, "demurrage_rate": 333}

handymax_data = {"vessel_type": 'Handymax', "call_size": 55000, 
                  "LOA": 180, "draft": 11.5, "beam": 28, "max_cranes": 2, 
                  "all_turn_time": 24, "mooring_time": 3, "demurrage_rate": 375}

panamax_data = {"vessel_type": 'Panamax', "call_size": 80000, 
                  "LOA": 220, "draft": 13, "beam": 32.2, "max_cranes": 3, 
                  "all_turn_time": 36, "mooring_time": 3, "demurrage_rate": 460} 


# In[8]:


class vessel(vessel_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


# In[9]:


def vessel_call_calc(vessels, commodities, simulation_window):
    
    vessels[0].calls = []
    vessels[1].calls = []
    vessels[2].calls = []
    
    historic_years = len(commodities[0].historic)
    
    for t in range(simulation_window):
        percentage = commodities[0].handysize_perc/100
        vessels[0].calls.append(int(np.ceil(commodities[0].demand[t+historic_years]*percentage)))
        percentage = commodities[0].handymax_perc/100
        vessels[1].calls.append(int(np.ceil(commodities[0].demand[t+historic_years]*percentage)))
        percentage = commodities[0].panamax_perc/100
        vessels[2].calls.append(int(np.ceil(commodities[0].demand[t+historic_years]*percentage)))
        
    return vessels


# In[10]:


def forecast_call_calc(vessels, commodities, simulation_window):
    
    for i in range (len(vessels)):
        calls = []
        for t in range(simulation_window):
            if i == 0:
                percentage = commodities[0].handysize_perc/100
            if i == 1:
                percentage = commodities[0].handymax_perc/100
            if i == 2:
                percentage = commodities[0].panamax_perc/100 
        
            calls.append(int(np.ceil(np.sum(commodities[0].forecast[-1]/vessels[i].call_size)*percentage)))
            
        vessels[i].calls = calls
        
    return vessels


# # Train class

# In[11]:


# create vessel class **will ultimately be placed in package**
class train_properties_mixin(object):
    def __init__(self, wagon_payload, number_of_wagons, *args, **kwargs):
        super().__init__(*args, **kwargs)
        "initialize"
        self.wagon_payload    = wagon_payload
        self.number_of_wagons = number_of_wagons 
        self.prep_time        = 2
        self.call_size        = wagon_payload * number_of_wagons
        self.call_log         = []
        
# Initial data set, data from Excel_input.xlsx
train_data = {"wagon_payload": 60, "number_of_wagons": 60}


# In[12]:


class train(train_properties_mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    # Waiting time factor (E2/E2/n Erlang quing theory using 6th order polynomial regression)
    def occupancy_to_waitingfactor(self, occupancy, n_stations):
        x = [10, 20, 30, 40, 50, 60, 70, 80, 90]
        berth1 = [0.055555556,0.125, 0.214285714, 0.333333333, 0.5, 0.75, 1.1667, 2.0, 4.5] 
        berth2 = [0.0006, 0.0065, 0.0235, 0.0516, 0.1181, 0.2222, 0.4125, 0.83, 2.00]
        berth3 = [0,0.0011,0.0062,0.0205,0.0512,0.1103,0.2275,0.46,1.2]
        berth4 = [0,0.0002,0.0019,0.0085,0.0532,0.0639,0.1441,0.33,0.92]

        #Polynomial regression
        coefficients1 = np.polyfit(x, berth1, 6)
        coefficients2 = np.polyfit(x, berth2, 6)
        coefficients3 = np.polyfit(x, berth3, 6)
        coefficients4 = np.polyfit(x, berth4, 6)
        
        #Resulting continuous representation
        def berth1_trend(occupancy):
            return (coefficients1[0]*occupancy**6+coefficients1[1]*occupancy**5+coefficients1[2]*occupancy**4+
                    coefficients1[3]*occupancy**3+coefficients1[4]*occupancy**2+coefficients1[5]*occupancy+coefficients1[6])

        def berth2_trend(occupancy):
            return (coefficients2[0]*occupancy**6+coefficients2[1]*occupancy**5+coefficients2[2]*occupancy**4+
                    coefficients2[3]*occupancy**3+coefficients2[4]*occupancy**2+coefficients2[5]*occupancy+coefficients2[6])

        def berth3_trend(occupancy):
            return (coefficients3[0]*occupancy**6+coefficients3[1]*occupancy**5+coefficients3[2]*occupancy**4+
                    coefficients3[3]*occupancy**3+coefficients3[4]*occupancy**2+coefficients3[5]*occupancy+coefficients3[6])

        def berth4_trend(occupancy):
            return (coefficients4[0]*occupancy**6+coefficients4[1]*occupancy**5+coefficients4[2]*occupancy**4+
                    coefficients4[3]*occupancy**3+coefficients4[4]*occupancy**4+coefficients4[5]*occupancy+coefficients4[6])
        
        x = occupancy*100
        if n_stations == 1:
            return max(0, berth1_trend(x))
        if n_stations == 2:
            return max(0, berth2_trend(x))
        if n_stations == 3:
            return max(0, berth3_trend(x))
        if n_stations == 4:
            return max(0, berth4_trend(x))
        
    # Waiting time factor (E2/E2/n Erlang quing theory using 6th order polynomial regression)  
    def waitingfactor_to_occupancy(self, factor, n_stations):
        factor = factor * 100
        if n_stations == 1:
            return max(1,(19.462 * np.log(factor) - 25.505))/100
        if n_stations == 2:
            return max(1,(14.091 * np.log(factor) + 16.509))/100
        if n_stations == 3:
            return max(1,(12.625 * np.log(factor) + 30.298))/100
        if n_stations == 4:
            return max(1,(11.296 * np.log(factor) + 38.548))/100

