
# coding: utf-8

# In[2]:


import numpy as np
import matplotlib.pyplot as plt


# # Scenario Trend

# In[ ]:


def trend(maize, soybean, wheat, width, height):
    fig  = plt.figure(figsize=(width, height))
    grid = plt.GridSpec(1, 1, wspace=0.4, hspace=0.5)
    fig1 = fig.add_subplot(grid[0, 0])

    fig1.plot(maize.years, maize.demand    , label='Maize demand')
    fig1.plot(soybean.years, soybean.demand, label='Soybean demand')
    fig1.plot(wheat.years, wheat.demand    , label='Wheat demand')
    fig1.set_title ('Commodity demand')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Demand [t/y]')
    fig1.legend()

    return fig1


# # Business Logic
# ### NPV

# In[ ]:


###


# ### Capex

# In[ ]:


def profit_loss(profits, width, height):
    
    x = []
    y1 = []
    y_min = []
    y_max = []
    
    for i in range (len(profits)):
        x.append(profits[i].year)
        y1.append(profits[i].total)
        if y1[i] <= 0:
            y_min.append(0)
        else:
            y_min.append(y1[i])
        if y1[i] >= 0:
            y_max.append(0)
        else:
            y_max.append(y1[i])
    
    fig  = plt.figure(figsize=(width, height))
    grid = plt.GridSpec(1, 1, wspace=0.4, hspace=0.5)
    fig1 = fig.add_subplot(grid[0, 0])

    fig1.step(x, y1, where='post', label='Profit / loss')
    fig1.fill_between(x, y1, y_min, step='post', facecolor='red', alpha=0.4)
    fig1.fill_between(x, y1, y_max, step='post', facecolor='green', alpha=0.4)
    fig1.set_title ('Annualised profits')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Profit / Loss [$]')
    fig1.legend()

    return fig1


# In[ ]:


def capex(capex, width, height):
    
    x = []
    y = []
    for i in range (len(capex)):
        x.append(capex[i].year)
        y.append(capex[i].total)
    
    fig  = plt.figure(figsize=(width, height))
    grid = plt.GridSpec(1, 1, wspace=0.4, hspace=0.5)
    fig1 = fig.add_subplot(grid[0, 0])

    fig1.step(x, y, where='post', label='Capex')
    fig1.set_title ('Capex')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Cost [$]')
    fig1.legend()

    return fig1


# ### Overall

# In[ ]:


def cashflows(profits, revenues, capex, opex, width, height):
    
    x  = []
    y1 = []
    y2 = []
    y3 = []
    y4 = []
    
    for i in range (len(capex)):
        x.append(capex[i].year)
        y1.append(profits[i].total)
        y2.append(revenues[i].total)
        y3.append(capex[i].total)
        y4.append(opex[i].total)
        
    fig  = plt.figure(figsize=(width, height))
    grid = plt.GridSpec(1, 1, wspace=0.4, hspace=0.5)
    fig1 = fig.add_subplot(grid[0, 0])

    fig1.plot(x, y1, label='Profits')
    fig1.plot(x, y2, label='Revenues')
    fig1.plot(x, y3, label='Capex')
    fig1.plot(x, y3, label='Opex')
    fig1.set_title ('Cash flows')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Profit/loss [$]')
    fig1.legend()
    
    return fig1


# In[ ]:


def all_cashflows(terminal, width, height):
    
    revenues, capex, labour, maintenance, energy, insurance, demurrage, residuals = terminal.revenues, terminal.capex, terminal.labour, terminal.maintenance, terminal.energy, terminal.insurance, terminal.demurrage, terminal.residuals
    
    x  = []
    y1 = []
    y2 = []
    y3 = []
    y4 = []
    y5 = []
    y6 = []
    y7 = []
    y8 = []
    
    for i in range (len(capex)):
        x.append(revenues[i].year)
        y1.append(revenues[i].total)
        y2.append(capex[i].total)
        y3.append(labour[i].total)
        y4.append(maintenance[i].total)
        y5.append(energy[i].total)
        y6.append(insurance[i].total)
        y7.append(demurrage[i].total)
        y8.append(residuals[i].total)
        
    fig  = plt.figure(figsize=(width, height))
    grid = plt.GridSpec(1, 1, wspace=0.4, hspace=0.5)
    fig1 = fig.add_subplot(grid[0, 0])
    
    fig1.step(x, y1, where='post', label='Revenues')
    fig1.step(x, y2, where='post', label='Capex')
    fig1.step(x, y3, where='post', label='Labour')
    fig1.step(x, y4, where='post', label='Maintenance')
    fig1.step(x, y5, where='post', label='Energy')
    fig1.step(x, y6, where='post', label='Insurance')
    fig1.step(x, y7, where='post', label='Demurrage')
    fig1.step(x, y8, where='post', label='Residual value')
    fig1.set_title ('Cash flows')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Profit/loss [$]')
    fig1.legend()
    
    #fig1.text((start_year+5), 0.75*max(y8), '${:0,.0f}'.format(min(y2)), horizontalalignment='center', fontsize=14)
    #fig1.text((start_year+window), 0.75*max(y8), '${:0,.0f}'.format(min(y2)), horizontalalignment='center', fontsize=14)
    #fig1.text((start_year+5), 0.75*max(y8), '${:0,.0f}'.format(min(y2)), horizontalalignment='center', fontsize=14)
    
    return fig1


# ### Demand vs Capacity

# In[ ]:


def throughput(terminal, width, height):
    
    throughputs = terminal.throughputs
    
    x  = []
    y1 = []
    y2 = []
    overcapacity = []
    undercapacity = []
    
    for i in range (len(throughputs)):
        x.append(throughputs[i].year)
        y1.append(throughputs[i].capacity)
        y2.append(throughputs[i].demand)
        
        if y1[i] >= y2[i]:
            overcapacity.append(y1[i])
        else:
            overcapacity.append(y2[i])
        if y1[i] <= y2[i]:
            undercapacity.append(y1[i])
        else:
            undercapacity.append(y2[i])

    fig  = plt.figure(figsize=(width, height))
    grid = plt.GridSpec(1, 1, wspace=0.4, hspace=0.5)
    fig1 = fig.add_subplot(grid[0, 0])
    
    fig1.step(x, y1, where='post', label='Capacity')
    fig1.step(x, y2, where='post', label='Demand')
    fig1.fill_between(x, overcapacity, y2, step='post', facecolor='#63FE41', alpha=0.4)
    fig1.fill_between(x, undercapacity, y2, step='post', facecolor='#FF5733', alpha=0.4)
    fig1.fill_between(x, y1, step='post', facecolor='#524634', alpha=0.4)
    fig1.set_title ('Demand vs. capacity')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Annual throughput [t/y]')
    fig1.legend()
    
    return fig1


# # Terminal Assets

# In[1]:


def asset_overview(terminal, width, height):
    
    quays, berths, cranes, storage, stations, quay_conveyors, hinterland_conveyors, profits = terminal.quays, terminal.berths, terminal.cranes, terminal.storage, terminal.stations, terminal.quay_conveyors, terminal.hinterland_conveyors, terminal.profits 
    x, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11 = [], [], [], [], [], [], [], [], [], [], [], []
    
    for i in range (len(profits)):
        x.append(profits[i].year)
        
        # Quays (y1)
        online = []
        for j in range (len(quays)):
            if quays[j].online_date <= x[i]:
                online.append(quays[j].length)
        y1.append(np.sum(online))
        
        # Berths (y2)
        online = []
        for j in range (len(berths)):
            if berths[j].online_date <= x[i]:
                online.append(1)
        y2.append(np.sum(online))
            
        # Gantry cranes (y3)
        online = []
        for j in range (len(cranes[0])):
            if cranes[0][j].online_date <= x[i]:
                online.append(1)
        y3.append(np.sum(online))
            
        # Harbour cranes (y4)
        online = []
        for j in range (len(cranes[1])):
            if cranes[1][j].online_date <= x[i]:
                online.append(1)
        y4.append(np.sum(online))
            
        # Mobile cranes (y5)
        online = []
        for j in range (len(cranes[2])):
            if cranes[2][j].online_date <= x[i]:
                online.append(1)
        y5.append(np.sum(online))
            
        # Screw unloaders (y6)
        online = []
        for j in range (len(cranes[3])):
            if cranes[3][j].online_date <= x[i]:
                online.append(1)
        y6.append(np.sum(online))
            
        # Silos (y7)
        online = []
        for j in range (len(storage[0])):
            if storage[0][j].online_date <= x[i]:
                online.append(storage[0][j].capacity)
        y7.append(np.sum(online))
            
        # Warehouses (y8)
        online = []
        for j in range (len(storage[1])):
            if storage[1][j].online_date <= x[i]:
                online.append(storage[1][j].capacity)
        y8.append(np.sum(online))
            
        # Hinterland loading stations (y9)
        online = []
        for j in range (len(stations)):
            if stations[j].online_date <= x[i]:
                online.append(stations[j].capacity)
        y9.append(np.sum(online))
            
        # Quay conveyors (y10) 
        online = []
        for j in range (len(quay_conveyors)):
            if quay_conveyors[j].online_date <= x[i]:
                online.append(quay_conveyors[j].capacity)
        y10.append(np.sum(online))
            
        # Hinterland conveyors (y11)
        online = []
        for j in range (len(hinterland_conveyors)):
            if hinterland_conveyors[j].online_date <= x[i]:
                online.append(hinterland_conveyors[j].capacity)
        y11.append(np.sum(online))
        
    fig  = plt.figure(figsize=(width, height))
    grid = plt.GridSpec(3, 2, wspace=0.4, hspace=0.5)
    fig1 = fig.add_subplot(grid[0, 0])
    fig2 = fig.add_subplot(grid[0, 1])
    fig3 = fig.add_subplot(grid[1, 0])
    fig4 = fig.add_subplot(grid[1, 1])
    fig5 = fig.add_subplot(grid[2, 0])
    
    # Quay
    fig1.step(x, y1, where='post', label='Online quay length')
    fig1.set_title ('Quay length')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Online quay length [m]')
    
    # Berths and cranes
    fig2.step(x, y2, where='post', label='Online berths')
    if len(cranes[0]) != 0:
        fig2.step(x, y3, where='post', label='Online gantry cranes')
    if len(cranes[1]) != 0:
        fig2.step(x, y4, where='post', label='Online harbour cranes')
    if len(cranes[2]) != 0:
        fig2.step(x, y5, where='post', label='Online mobile cranes')
    if len(cranes[3]) != 0:
        fig2.step(x, y6, where='post', label='Online screw unloaders')
    fig2.set_title ('Berths and cranes')
    fig2.set_xlabel('Year')
    fig2.set_ylabel('Number of assets online')
    fig2.legend()
    
    # Storage
    if len(storage[0]) != 0:
        fig3.step(x, y7, where='post', label='Online silo capacity')
    if len(storage[1]) != 0:
        fig3.step(x, y8, where='post', label='Online warehouse capacity')
    fig3.set_title ('Storage')
    fig3.set_xlabel('Year')
    fig3.set_ylabel('Storage capacity online')
    fig3.legend()
    
    # Stations
    fig4.step(x, y9, where='post', label='Online hinterland station capacity')
    fig4.set_title ('Hinterland loading stations')
    fig4.set_xlabel('Year')
    fig4.set_ylabel('Loading capacity online')
    
    # Conveyors
    fig5.step(x, y10, where='post', label='Online quay conveyor capacity')
    fig5.step(x, y11, where='post', label='Online hinterland conveyor capacity')
    fig5.set_title ('Conveyors')
    fig5.set_xlabel('Year')
    fig5.set_ylabel('Conveyor capacity online')
    fig5.legend()

