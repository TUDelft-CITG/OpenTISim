
# coding: utf-8

# # Table of Contents
# 
# ### 1 Traffic Generator
# Generates numerous traffic projections, which can be used as a basis for the *temporal terminal design*. Traffic growth is based on two components: a pre-defined steady growth rate and a pre-defined normal distributed growth rate. The present value of each traffic projection is calculated and the median is defined as the *traffic scenario* (only used in the perfect *foresight method*) 
# ### 2 Temporal Terminal Design
# Translates a traffic projection into an accompanying terminal design with the following terminal elements. Each design process produces a single *terminal* instance, under which all infrastructure and financial components are grouped (e.g. *terminal.quays*, *terminal.cashflows*). The temporal development of individual infrastructure can be inspected through the info tab (i.e. *terminal.berths.info*. The infrastructure elements that are defined in this model are: 
# - Quays
# - Cranes
# - Storage
# - Hinterland train loading stations 
# - Conveyors 
# ### 3 Simulator
# Runs the simulator (chapter 2) multiple times, while slightly changing each investment trigger. The resulting *terminal* variables are saved in a list after which the impact of each trigger alteration can be visualised.

# In[1]:


import copy
import plotly
import numpy as np
import pandas as pd

import plotly.tools as tls 
import plotly.plotly as py  
import plotly.graph_objs as go
from plotly.graph_objs import *
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
get_ipython().run_line_magic('matplotlib', 'inline')

import terminal_optimization.visualisation               as visualisation
import terminal_optimization.forecast                    as forecast
import terminal_optimization.investment_decisions        as invest
import terminal_optimization.infrastructure              as infra
import terminal_optimization.financial_analysis          as financial
import terminal_optimization.initial_terminal            as initial
import terminal_optimization.investment_decisions_future as future_invest

# Log in to Plotly servers
plotly.tools.set_credentials_file(username='jorisneuman', api_key='zButeTrlr5xVETcyvazd')
#plotly.tools.set_credentials_file(username='wijzermans', api_key='FKGDvSah3z5WCNREBZEq')
#plotly.tools.set_credentials_file(username='wijnandijzermans', api_key='xeDEwwpCK3aLLR4TIrM9')


# ## 1 Traffic Generator

# In[2]:


def traffic_generator(nr_generations, start_year, simulation_window):
    
    ###################################################################################################
    # Traffic projections on which estimate is based
    ###################################################################################################

    # Import commodities from package
    maize   = forecast.bulk_commodities(**forecast.maize_data)
    soybean = forecast.bulk_commodities(**forecast.maize_data)
    wheat   = forecast.bulk_commodities(**forecast.wheat_data)

    # Maize - Probabilistic demand
    maize.historic = [1600000,1700000,1680000,1760000,1800000]
    maize.rate     = 1.0336         # Average consumption growth in South Africa in the past 5 years
    maize.sigma    = 0.0374         # Standard deviation in consumption growth in South Africa in the past 5 years

    # If required number of traffic generations is even, one iteration is added in order to be able to identify the median
    if nr_generations % 2 == 0:
        nr_generations = nr_generations + 1 

    # Create traffic projections
    start_year = 2018
    simulation_window = 20
    traffic_projections = []
    for iterations in range(nr_generations):
        maize.random_scenario(start_year, simulation_window, maize.historic, maize.rate, maize.sigma)
        traffic_projections.append(maize.demand)
    
    ###################################################################################################
    # Traffic scenario based on median present quantity of all projections
    ################################################################################################### 
    
    # Calculate the net present quantity of each projection
    project_WACC = 0.09
    WACC_factor = []
    for year in range (len(maize.historic)):
        WACC_factor.append(1.0)
    for year in range (simulation_window):
        WACC_factor.append(1/((1+project_WACC)**(year)))

    traffic_matrix = np.zeros(shape=(len(traffic_projections), 2))
    for i in range(len(traffic_projections)):
        traffic_matrix[i,0] = i
        present_value_volume = []
        for j in range(len(traffic_projections[i])):
            present_value_volume.append(traffic_projections[i][j]*WACC_factor[j])
        traffic_matrix[i,1] = int(np.sum(present_value_volume))

    df=pd.DataFrame(traffic_matrix, columns=['Iteration','NPQ'])

    # Select the median traffic projection in terms of present quantity
    median_iteration = df.loc[df['NPQ']==np.median(df['NPQ'])].index[0]
    traffic_scenario = traffic_projections[median_iteration] 
    maize.demand   = traffic_scenario 
    soybean.demand = [0]*len(maize.demand)
    wheat.demand   = [0]*len(maize.demand)
    commodities    = [maize, soybean, wheat]
    
    ###################################################################################################
    # Translate traffic projection into terminal calls 
    ################################################################################################### 
    
    # Import vessels from package
    handysize = forecast.vessel(**forecast.handysize_data)
    handymax  = forecast.vessel(**forecast.handymax_data)
    panamax   = forecast.vessel(**forecast.panamax_data)
    vessels = [handysize, handymax, panamax]
    
    # Calculate yearly calls
    vessels = forecast.vessel_call_calc(vessels, commodities, simulation_window)

    # Plot forecast
    fig = visualisation.scenario(traffic_projections, commodities)
    
    return vessels, commodities, fig, traffic_projections, traffic_scenario


# ## 2 Temporal Terminal Design
# - Current performance method 
# - Perfect foresight method
# - Forecast based method

# In[3]:


def design(chosen_method, terminal, vessels, commodities, start_year, simulation_window):
    
    for i in range (start_year, start_year + simulation_window): 
        
        year = i 
        timestep = year - start_year

        ##################################################################
        # Investment Decisions (current performance method)
        ##################################################################     
        
        if chosen_method == 'Current performance method':
            
            # Berths and cranes
            terminal.berths, terminal.cranes = invest.berth_invest_decision(terminal.berths, terminal.cranes, commodities, vessels, terminal.allowable_vessel_waiting_time, year, timestep, operational_hours)

            # Quay
            terminal.quays = invest.quay_invest_decision(terminal.quays, terminal.berths, year, timestep)

            # Storage
            storage_type = 'Silos'
            terminal.storage = invest.storage_invest_decision(terminal.storage, terminal.required_storage_factor, terminal.aspired_storage_factor, storage_type, commodities, year, timestep)

            # Loading stations
            terminal.stations, terminal.trains = invest.station_invest_decision(terminal.stations, forecast.train(**forecast.train_data), terminal.allowable_train_waiting_time, commodities, timestep, year, operational_hours)

            # Conveyors
            terminal.quay_conveyors = invest.quay_conveyor_invest_decision(terminal.quay_conveyors, terminal.berths, year, timestep, operational_hours)
            terminal.hinterland_conveyors = invest.hinterland_conveyor_invest_decision(terminal.hinterland_conveyors, terminal.stations, year, timestep, operational_hours)

        ##################################################################
        # Investment Decisions (Perfect foresight and forecast method)
        ################################################################## 
        
        if chosen_method == 'Perfect foresight method' or chosen_method == 'Forecast based method':
            
            # Create forecast and accompanying vessel calcs
            commodities = forecast.forecaster(chosen_method, 'Linear', commodities, forecast_window, hindcast_window, timestep)
            vessels = forecast.forecast_call_calc(vessels, commodities, simulation_window)
            
            # Berths and cranes
            terminal.berths, terminal.cranes = future_invest.berth_invest_decision(terminal.berths, terminal.cranes, commodities, vessels, terminal.allowable_vessel_waiting_time, year, timestep, operational_hours)

            # Quay
            terminal.quays = future_invest.quay_invest_decision(terminal.quays, terminal.berths, year, timestep)

            # Storage
            storage_type = 'Silos'
            terminal.storage = future_invest.storage_invest_decision(terminal.storage, terminal.required_storage_factor, terminal.aspired_storage_factor, storage_type, commodities, year, timestep)

            # Loading stations
            terminal.stations, terminal.trains = future_invest.station_invest_decision(terminal.stations, forecast.train(**forecast.train_data), terminal.allowable_train_waiting_time, commodities, timestep, year, operational_hours)

            # Conveyors
            terminal.quay_conveyors = future_invest.quay_conveyor_invest_decision(terminal.quay_conveyors, terminal.berths, year, timestep, operational_hours)
            terminal.hinterland_conveyors = future_invest.hinterland_conveyor_invest_decision(terminal.hinterland_conveyors, terminal.stations, year, timestep, operational_hours)
        
        ##################################################################
        # Business logic
        ################################################################## 
        
        # Terminal throughput
        terminal.throughputs = financial.throughput_calc(terminal, commodities, vessels, terminal.trains, operational_hours, timestep, year)
        # Revenue
        terminal.revenues = financial.revenue_calc(terminal.revenues, terminal.throughputs, commodities, year, timestep)       
        # Capex
        terminal.capex = financial.capex_calc(terminal, year, timestep)
        # Labour costs
        terminal.labour = financial.labour_calc(terminal, year, timestep, operational_hours)
        # Maintenance costs
        terminal.maintenance = financial.maintenance_calc(terminal, year, timestep)
        # Energy costs
        terminal.energy = financial.energy_calc(terminal, year, operational_hours, timestep)
        # Insurance costs
        terminal.insurance = financial.insurance_calc(terminal, year, timestep)
        # Lease costs 
        terminal.lease = financial.lease_calc(terminal, year,timestep)
        # Demurrage costs
        terminal.demurrage = financial.demurrage_calc(terminal.demurrage, terminal.berths, terminal.cranes, commodities, vessels, operational_hours, timestep, year)
        # Residual value calculations 
        terminal.residuals = financial.residual_calc(terminal, year, timestep)
        # Profits
        terminal.profits = financial.profit_calc(terminal, simulation_window, timestep, year, start_year)
        # Opex
        terminal.opex = financial.opex_calc(terminal, year, timestep)  
        
    #WACC depreciated profits
    terminal.WACC_cashflows = financial.WACC_calc(terminal.project_WACC, terminal.profits, terminal.revenues, terminal.capex, terminal.opex, simulation_window, start_year)
    
    # Combine all cashflows
    terminal.cashflows = financial.cashflow_calc(terminal, simulation_window, start_year) 
    
    #NPV 
    terminal.NPV = financial.NPV_calc(terminal.WACC_cashflows)
        
    return terminal


# In[4]:


def evaluate_perfect_foresight(terminal, commodities, simulation_window, start_year):
    
    terminal_capacity = []
    terminal_throughputs = []
    terminal_revenues = []
    demurrage_costs = []
    profits = []
    
    for timestep in range(len(terminal.throughputs)):
        
        year = start_year + timestep
    
        # Terminal throughput
        terminal_capacity.append(int(terminal.throughputs[timestep].capacity))
        demand = commodities[0].demand[timestep]
        terminal_throughputs.append(int(min(demand, terminal_capacity[timestep])))

        # Terminal revenues
        terminal_revenues.append(int(commodities[0].handling_fee * terminal_throughputs[timestep]))
        
        # Demurrage costs
        costs = terminal.demurrage[0].calc(terminal.berths, terminal.cranes, commodities, vessels, operational_hours, timestep, year)
        demurrage_costs.append(costs)
        
        # Profits
        revenues    = terminal_revenues[-1]
        capex       = terminal.capex[timestep].total
        labour      = terminal.labour[timestep].total
        maintenance = terminal.maintenance[timestep].total
        energy      = terminal.energy[timestep].total
        insurance   = terminal.insurance[timestep].total
        demurrage   = demurrage_costs[-1]
        if timestep == len(terminal.throughputs)-1:
            residuals = terminal.residuals[timestep].total
        else:
            residuals = 0
        profits.append(int(revenues + capex - labour - maintenance - energy - insurance - demurrage + residuals))
        
        # Overwrite terminal cashflow data
        terminal.revenues[timestep].total = terminal_revenues[-1]
        terminal.demurrage[timestep].total = demurrage_costs[-1]
        terminal.profits[timestep].total = profits[-1]
    
    #WACC depreciated profits
    terminal.WACC_cashflows = financial.WACC_calc(terminal.project_WACC, terminal.profits, terminal.revenues, terminal.capex, terminal.opex, simulation_window, start_year)

    # Combine all cashflows
    terminal.cashflows = financial.cashflow_calc(terminal, simulation_window, start_year) 

    #NPV 
    terminal.NPV = financial.NPV_calc(terminal.WACC_cashflows)
    
    return terminal


# # 3 Simulator
# - Simulation parameters
# - Performance trigger optimization
# - Estimate project value
# - Evaluate financial performance
# - Evaluate design method
# - Run single simulation
# - Risk sensitivity analysis

# ## 3.1 Simulation parameters

# In[5]:


# Simulation parameters
start_year        = 2018   # start year of simulation
simulation_window = 20     # forecast 20 years
end_year          = start_year + simulation_window - 1
operational_hours = 5840   # operational hours per year (16 hours per day 365 days a year)
project_WACC      = 0.09   # Applied project weighted average cost of capital
nr_generations    = 1001   # Number of traffic projections generated

# In case of future based methods:
hindcast_window = 5  # Number of years of materialized traffic volumes that are included in assessment
forecast_window = 2  # Number of years of forecasted traffic volumes

# Choose design method
chosen_method = 'Perfect foresight method'
#chosen_method = 'Current performance method'
#chosen_method = 'Forecast based method'

# Performance triggers (static values)
triggers = []
triggers.append([0.30, 'Acceptable waiting vessel time as factor of service time'])
triggers.append([0.05, 'Minimum fraction of yearly throughput required as storage']) # PIANC guidelines
triggers.append([0.06, 'Fraction of yearly throughput aspired as storage'])
triggers.append([0.30, 'Acceptable waiting train time as factor of service time'])

# Make traffic projections
vessels, commodities, fig, traffic_projections, traffic_scenario = traffic_generator(nr_generations, start_year, simulation_window)

# Visualize traffic projections
#py.iplot(fig, filename='Traffic projections')

# Save traffic projections
#np.savetxt('Saved_traffic_scenario.txt', traffic_scenario, fmt='%d')
#np.savetxt('Saved_traffic_projections.txt', traffic_projections, fmt='%d')

# Load traffic projections
traffic_scenario = np.loadtxt('Saved_traffic_scenario2.txt', dtype=int)
traffic_projections = np.loadtxt('Saved_traffic_projections2.txt', dtype=int)
commodities[0].demand = traffic_scenario
fig = visualisation.scenario(traffic_projections, commodities)
#py.iplot(fig, filename='Traffic projections')


# ## 3.2 Performance trigger optimization

# In[6]:


# Performance triggers (iteration values)
triggers_spectrum = [] 
triggers_spectrum.append([np.linspace(0.10, 1.50, 141), 'Acceptable waiting vessel time as factor of service time'])
triggers_spectrum.append([np.linspace(0.06, 0.15, 10),  'Fraction of yearly throughput aspired as storage'])
triggers_spectrum.append([np.linspace(0.01, 0.60, 60), 'Acceptable waiting train time as factor of service time'])

# Run multiple simulations, while iterating through each investment trigger
results = []

# Iterate through allowable vessel waiting times
iterations = []
original_value = copy.deepcopy(triggers[0][0])
for waiting_time in triggers_spectrum[0][0]:
    triggers[0][0] = waiting_time
    terminal  = initial.terminal(project_WACC, triggers)
    terminal  = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
    iteration = copy.deepcopy(terminal)
    iterations.append(iteration)
results.append(iterations)
triggers[0][0] = original_value

# Iterate through aspired storage factors
iterations = []
original_value = copy.deepcopy(triggers[2][0])
for storage_factor in triggers_spectrum[1][0]:
    triggers[2][0] = storage_factor
    terminal = initial.terminal(project_WACC, triggers)
    terminal = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
    iteration = copy.deepcopy(terminal)
    iterations.append(iteration)
results.append(iterations)
triggers[2][0] = original_value

# Iterate through allowable train waiting times
iterations = []
original_value = copy.deepcopy(triggers[3][0])
for waiting_time in triggers_spectrum[2][0]:
    triggers[3][0] = waiting_time
    terminal  = initial.terminal(project_WACC, triggers)
    terminal  = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
    iteration = copy.deepcopy(terminal)
    iterations.append(iteration)
results.append(iterations)
triggers[3][0] = original_value


# In[7]:


# Visualise NPV distribution as a result of allowable vessel waiting time
waiting_time_iterations = results[0]
plotdata = visualisation.NPV_distribution_vessel_waiting_times(waiting_time_iterations)
fig = dict(data=plotdata[0], layout=plotdata[1])
py.iplot(fig, filename='Trigger iteration - vessel waiting time')


# In[8]:


# Visualise NPV distribution as a result of aspired storage factor
waiting_time_iterations = results[1]
plotdata = visualisation.NPV_distribution_aspired_storage(waiting_time_iterations)
fig = dict(data=plotdata[0], layout=plotdata[1])
py.iplot(fig, filename='Trigger iteration - required storage factor')


# In[9]:


# Visualise NPV distribution as a result of allowable train waiting time
waiting_time_iterations = results[2]
plotdata = visualisation.NPV_distribution_train_waiting_times(waiting_time_iterations)
fig = dict(data=plotdata[0], layout=plotdata[1])
py.iplot(fig, filename='Trigger iteration - train waiting time')


# ## 3.3 Estimate project value
# Iterating through the numerous traffic projections (in the case of the perfect foresight method, the single traffic scenario is fed into the value estimator) 

# In[10]:


estimate_designs = []

if chosen_method == 'Perfect foresight method':
    
    # Commodity demand (vessel calc iterates yearly and is integrated into design function)
    commodities[0].demand = traffic_scenario
    
    # Temporal terminal design
    terminal  = initial.terminal(project_WACC, triggers)
    terminal  = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
    iteration = copy.deepcopy(terminal)
    estimate_designs.append(iteration)
    print('Estimated NPV: $' + str('{:0,.0f}'.format(terminal.NPV)))
    
if chosen_method == 'Current performance method':
    for i in range(len(traffic_projections)):
        
        if round(i/len(traffic_projections),3) == 0.250:
            print ('25% complete')
        if round(i/len(traffic_projections),3) == 0.500:
            print ('50% complete')
        if round(i/len(traffic_projections),3) == 0.750:
            print ('75% complete')
        
        # Commodity demand and resulting vessel calls
        commodities[0].demand = traffic_projections[i]
        vessels = forecast.vessel_call_calc(vessels, commodities, simulation_window)

        # Temporal terminal designs
        terminal  = initial.terminal(project_WACC, triggers)
        terminal  = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
        iteration = copy.deepcopy(terminal)
        estimate_designs.append(iteration)
    
    # Visualize data
    fig = visualisation.NPV_distribution_estimated_designs(estimate_designs)
    py.iplot(fig, filename='Project value estimate')  
        
if chosen_method == 'Forecast based method':
    for i in range(len(traffic_projections)):
        
        if round(i/len(traffic_projections),3) == 0.250:
            print ('25% complete')
        if round(i/len(traffic_projections),3) == 0.500:
            print ('50% complete')
        if round(i/len(traffic_projections),3) == 0.750:
            print ('75% complete')
        
        # Commodity demand (vessel calc iterates yearly and is integrated into design function)
        commodities[0].demand = traffic_projections[i]
        
        # Temporal terminal designs
        terminal  = initial.terminal(project_WACC, triggers)
        terminal  = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
        iteration = copy.deepcopy(terminal)
        estimate_designs.append(iteration)
        
    # Visualize data
    fig = visualisation.NPV_distribution_estimated_designs(estimate_designs)
    py.iplot(fig, filename='Project value estimation')  


# ## 3.4 Evaluate Financial Performance

# In[12]:


evaluate_designs = []

# Create traffic simulations
vessels, commodities, fig, traffic_simulations, traffic_scenario = traffic_generator(nr_generations, start_year, simulation_window)

# Save / Load traffic simulations
#np.savetxt('traffic_simulations.txt', traffic_simulations, fmt='%d')
traffic_simulations = np.loadtxt('traffic_simulations2.txt', dtype=int)

if chosen_method == 'Perfect foresight method':
    initial_terminal = terminal
    for i in range(len(traffic_simulations)):
        
        if round(i/len(traffic_simulations),3) == 0.250:
            print ('25% complete')
            display(terminal.berths[0].info)
        if round(i/len(traffic_simulations),3) == 0.500:
            print ('50% complete')
        if round(i/len(traffic_simulations),3) == 0.750:
            print ('75% complete')
            display(terminal.berths[0].info)
        
        # Commodity demand (vessel calc iterates yearly and is integrated into design function)
        commodities[0].demand = traffic_simulations[i]

        # Design is kept static and fed with the various traffic volumes
    
        terminal = evaluate_perfect_foresight(initial_terminal, commodities, simulation_window, start_year)
        iteration = copy.deepcopy(terminal)
        evaluate_designs.append(iteration)   
    
if chosen_method == 'Current performance method':
    for i in range(len(traffic_simulations)):
        
        if round(i/len(traffic_simulations),3) == 0.250:
            print ('25% complete')
        if round(i/len(traffic_simulations),3) == 0.500:
            print ('50% complete')
        if round(i/len(traffic_simulations),3) == 0.750:
            print ('75% complete')
        
        # Commodity demand and resulting vessel calls
        commodities[0].demand = traffic_simulations[i]
        vessels = forecast.vessel_call_calc(vessels, commodities, simulation_window)

        # Temporal terminal designs
        terminal = initial.terminal(project_WACC, triggers)
        terminal = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
        iteration = copy.deepcopy(terminal)
        evaluate_designs.append(iteration)  
        
if chosen_method == 'Forecast based method':
    for i in range(len(traffic_simulations)):
        
        if round(i/len(traffic_simulations),3) == 0.250:
            print ('25% complete')
        if round(i/len(traffic_simulations),3) == 0.500:
            print ('50% complete')
        if round(i/len(traffic_simulations),3) == 0.750:
            print ('75% complete')
        
        # Commodity demand (vessel calc iterates yearly and is integrated into design function)
        commodities[0].demand = traffic_simulations[i]
        
        # Temporal terminal designs
        terminal = initial.terminal(project_WACC, triggers)
        terminal = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
        iteration = copy.deepcopy(terminal)
        evaluate_designs.append(iteration)
    
# Visualise NPV distribution of all terminal designs
fig = visualisation.NPV_distribution_simulated_designs(evaluate_designs)
py.iplot(fig, filename='Project value simulation')     


# # 3.5 Evaluate design method

# In[13]:


fig = visualisation.method_evaluation(chosen_method, estimate_designs, evaluate_designs)
py.iplot(fig, filename='Design method evaluation')


# ## 3.6 Single simulation run

# In[34]:


project_WACC = 0.09
chosen_method = 'Perfect foresight method'
#chosen_method = 'Current performance method'
#chosen_method = 'Forecast based method'

commodities[0].demand = traffic_scenario

triggers = []
triggers.append([0.30, 'Acceptable waiting vessel time as factor of service time'])
triggers.append([0.05, 'Minimum fraction of yearly throughput required as storage']) # PIANC guidelines
triggers.append([0.06, 'Fraction of yearly throughput aspired as storage'])
triggers.append([0.30, 'Acceptable waiting train time as factor of service time'])

terminal = initial.terminal(project_WACC, triggers)
terminal = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)

# Visualise terminal discounted cashflows 
plotdata = visualisation.revenue_capex_opex(terminal)
#py.iplot({'data': plotdata[0], 'layout': plotdata[1]}, filename='Cashflows')

terminal.NPV


# In[33]:


terminal.cashflows # current performance


# In[35]:


terminal.cashflows # perfect foresight


# ### 3.7 Terminal capacity

# In[15]:


# Perfect foresight method


# In[25]:


fig = visualisation.capacity(terminal, commodities)
py.iplot(fig, filename='Capacity')


# In[17]:


# Current performance method


# In[18]:


fig = visualisation.capacity(terminal, commodities)
py.iplot(fig, filename='Capacity')


# In[20]:


# Forecast based method


# In[28]:


fig = visualisation.capacity(terminal, commodities)
py.iplot(fig, filename='Capacity')


# ## 3.7 Risk Sensitivity Iteration

# In[21]:


# Define traffic projection 
commodities[0].demand = traffic_scenario

# Iterate through project WACC
WACC_spectrum = np.linspace(0.01,0.15,15)

WACC_iterations = []
for WACC in WACC_spectrum:
    terminal = initial.terminal(WACC, triggers)
    terminal = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
    iteration = copy.deepcopy(terminal)
    WACC_iterations.append(iteration)

# Visualise NPV distribution as a result of project WACC
plotdata = visualisation.NPV_distribution_WACC(WACC_iterations)
fig = dict(data=plotdata[0], layout=plotdata[1])
#py.iplot(fig, filename='Trigger iteration - vessel waiting time')


# ## 3.8 Forecast method evaluation 

# In[22]:


chosen_method


# In[23]:


if chosen_method == 'Forecast based method':

    project_WACC = 0.09
    commodities[0].demand = traffic_scenario
    
    terminal = initial.terminal(project_WACC, triggers)
    terminal = design(chosen_method, terminal, vessels, commodities, start_year, simulation_window)
    
    registered_forecast = commodities[0].historic
    registered_forecast.append(commodities[0].demand[len(commodities[0].historic)])
    for i in range (len(commodities[0].forecastlog)-1): 
        registered_forecast.append(commodities[0].forecastlog[i])

    fig = visualisation.forecast_visualization(traffic_scenario, registered_forecast, commodities)
    py.iplot(fig, filename='forecast evaluation')

