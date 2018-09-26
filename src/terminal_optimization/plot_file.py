
# coding: utf-8

# In[2]:


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
# ### Capex

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

    fig1.plot(x, y, label='Capex')
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


def all_cashflows(revenues, capex, labour, maintenance, energy, insurance, demurrage, residuals, width, height):
    
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
    
    fig1.step(x, y1, where='pre', label='Revenues')
    fig1.step(x, y2, where='pre', label='Capex')
    fig1.step(x, y3, where='pre', label='Labour')
    fig1.step(x, y4, where='pre', label='Maintenance')
    fig1.step(x, y5, where='pre', label='Energy')
    fig1.step(x, y6, where='pre', label='Insurance')
    fig1.step(x, y7, where='pre', label='Demurrage')
    fig1.step(x, y8, where='pre', label='Residual value')
    fig1.set_title ('Cash flows')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Profit/loss [$]')
    fig1.legend()
    
    return fig1


# ### Demand vs Capacity

# In[ ]:


def throughput(commodities, throughputs, width, height):
    
    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]
    
    x  = []
    y1 = []
    y2 = []
    
    for i in range (len(throughputs)):
        demand = maize.demand[i] + soybean.demand[i] + wheat.demand[i]
        x.append(throughputs[i].year)
        y1.append(throughputs[i].total)
        y2.append(demand)
        
    fig  = plt.figure(figsize=(width, height))
    grid = plt.GridSpec(1, 1, wspace=0.4, hspace=0.5)
    fig1 = fig.add_subplot(grid[0, 0])

    fig1.plot(x, y1, label='Terminal throughput')
    fig1.plot(x, y2, label='Demand')
    fig1.set_title ('Demand vs. capacity')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Annual throughput [t/y]')
    fig1.legend()
    
    return fig1

