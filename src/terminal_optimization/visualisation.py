
# coding: utf-8

# In[1]:


import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# # Plot colours

# In[3]:


# Applied colours within the plots
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]    

# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.    
for i in range(len(tableau20)):    
    r, g, b = tableau20[i]    
    tableau20[i] = (r / 255., g / 255., b / 255.) 


# # Scenario Trend

# In[1]:


def trend(commodities, simulation_window, start_year):
    
    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]
    demand_matrix = np.zeros(shape=(simulation_window, 4))
    
    ############################################################################################################
    # For each year, register each commodities' demand 
    ############################################################################################################
    
    for t in range (simulation_window):

        # Years (Column 0)
        year = t + start_year 
        demand_matrix[t,0] = year
        # Maize (Column 1)
        demand_matrix[t,1] = maize.demand[t]
        # Soybean (Column 2)
        demand_matrix[t,2] = soybean.demand[t]
        # Wheat (Column 3)
        demand_matrix[t,3] = wheat.demand[t]
    
    demand = pd.DataFrame(demand_matrix, columns=['Year', 'Maize demand', 'Soybean demand', 'Wheat demand'])
    demand = demand.astype(int)

    # Determining max and min x and y values
    x_max = int(max(demand['Year']))
    x_min = int(min(demand['Year']))
    y_max = []
    y_min = []
    for i in range (1, len(demand.columns)):
        y_max.append(max(demand.iloc[:,i]))
        y_min.append(min(demand.iloc[:,i]))
    y_max = int(max(y_max))
    y_max = int(np.ceil(y_max/100000)*100000)
    y_min = int(max(y_min)) 

    # You typically want your plot to be ~1.33x wider than tall
    # Common sizes: (10, 7.5) and (12, 9)    
    plt.figure(figsize=(6, 4))    

    # Remove the plot frame lines
    ax = plt.subplot(111)    
    ax.spines["top"].set_visible(False)    
    ax.spines["bottom"].set_visible(False)    
    ax.spines["right"].set_visible(False)    
    ax.spines["left"].set_visible(False)    

    # Ensure that the axis ticks only show up on the bottom and left of the plot.      
    ax.get_xaxis().tick_bottom()    
    ax.get_yaxis().tick_left()    

    # Limit the range of the plot to only where the data is  
    # Avoid unnecessary whitespace
    plt.ylim(y_min, y_max)
    plt.xlim(x_min-1, x_max+1)    

    # Make sure your axis ticks are large enough to be easily read      
    plt.yticks(range(y_min, y_max+1, 200000), 
               [str(x) for x in range(y_min, y_max+1, 200000)], fontsize=14)
    plt.xticks(range(x_min, x_max+1, int((x_max-x_min)/4)), [str(x) for x in range(x_min, x_max+1, int((x_max-x_min)/4))], fontsize=14)  

    # Provide tick lines across the plot to help your viewers trace along    
    # the axis ticks. Make sure that the lines are light and small so they    
    # don't obscure the primary data lines    
    for y in range(y_min+200000, y_max+1, 200000):    
        plt.plot((x_min-1, x_max+1), (y, y), "--", lw=0.5, color="black", alpha=0.3)    

    # Remove the tick marks; they are unnecessary with the tick lines we just plotted    
    plt.tick_params(axis="both", which="both", bottom="off", top="off",    
                    labelbottom="on", left="off", right="off", labelleft="on")    

    # The names of each asset equals the name of the corresponding dataframe column
    commodity_names = demand.loc[:, demand.columns != 'Year'].columns.values
    
    # Plot each commodity
    plt.plot(demand.Year.values, demand['Maize demand'].values, lw=2.5, color=tableau20[0])
    plt.plot(demand.Year.values, demand['Soybean demand'].values, lw=2.5, color=tableau20[1])
    plt.plot(demand.Year.values, demand['Wheat demand'].values, lw=2.5, color=tableau20[2])
    
    plt.text(x_max+1, y_max*1.0, 'Maize demand', fontsize=14, color=tableau20[0])
    plt.text(x_max+1, y_max*0.9, 'Soybean demand', fontsize=14, color=tableau20[1])
    plt.text(x_max+1, y_max*0.8, 'Wheat demand', fontsize=14, color=tableau20[2])  

    # matplotlib's title() call centers the title on the plot, but not the graph,    
    # so I used the text() call to customize where the title goes.    

    # Make the title big enough so it spans the entire plot, but don't make it    
    # so big that it requires two lines to show.    

    # Note that if the title is descriptive enough, it is unnecessary to include    
    # axis labels; they are self-evident, in this plot's case.    
    plt.text((x_min + x_max)/2, 1.2*y_max, "Commodity demand", fontsize=17, ha="center")    

    # Always include your data source(s) and copyright notice! And for your    
    # data sources, tell your viewers exactly where the data came from,    
    # preferably with a direct link to the data. Just telling your viewers    
    # that you used data from the "U.S. Census Bureau" is completely useless:    
    # the U.S. Census Bureau provides all kinds of data, so how are your    
    # viewers supposed to know which data set you used?    
    plt.text(x_max+1, y_min-0.1*y_min, "Data source: Forecasting model", fontsize=10)    

    # Finally, save the figure as a PNG.    
    # You can also save it as a PDF, JPEG, etc.    
    # Just change the file extension in this call.    
    # bbox_inches="tight" removes all the extra whitespace on the edges of your plot.    
    #plt.savefig("percent-bachelors-degrees-women-usa.png", bbox_inches="tight") 

    return


# # Cash Flows
# - Profit / Loss (present value)
# - Profit / Loss (nominal value)
# - Revenues (nominal value)
# - Revenues + Capex + Opex (nominal value)

# ### Profit / Loss (present value)

# In[ ]:


def profit_loss_pv(WACC_cashflows, width, height):
    
    profits = WACC_cashflows.profits
    years = WACC_cashflows.years
    
    x = []
    y1 = []
    y_min = []
    y_max = []
    
    for i in range (len(profits)):
        x.append(years[i])
        y1.append(profits[i])
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
    fig1.set_title ('Annualised profits in present value terms')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Profit / Loss [$]')
    fig1.legend()

    return fig1


# ### Profit / Loss (nominal)

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


# ### Revenues

# In[ ]:


def revenues(terminal):
    
    cashflows = terminal.cashflows
    revenues = cashflows[['Year', 'Revenues']]

    x_max = int(max(revenues['Year']))
    x_min = int(min(revenues['Year']))
    y_max = []
    y_min = []
    for i in range (1, len(revenues.columns)):
        y_max.append(max(revenues.iloc[:,i]))
        y_min.append(min(revenues.iloc[:,i]))
    y_max = int(max(y_max))
    y_max = int(np.ceil(y_max/10000000)*10000000)
    y_min = int(max(y_min))


    # Create figure
    #revenue_plot = plt.figure(figsize=(6, 4.5))

    # Create bars
    barWidth = 0.7
    bars1 = terminal.cashflows.Revenues.values

    # The X position of bars
    x1 = terminal.cashflows.Year.values

    # Create barplot
    plt.bar(x1, bars1, width = barWidth, color = '#2CA02C', label='Revenues')

    # Remove the plot frame lines  
    ax = plt.subplot(111)    
    ax.spines["top"].set_visible(False)    
    ax.spines["bottom"].set_visible(False)    
    ax.spines["right"].set_visible(False)    
    ax.spines["left"].set_visible(False)    

    # Ensure that the axis ticks only show up on the bottom and left of the plot.     
    ax.get_xaxis().tick_bottom()    
    ax.get_yaxis().tick_left()

    # Create legend
    #plt.legend()

    # Text below each barplot with a rotation at 90°
    plt.yticks(range(y_min, y_max+1, 10000000), 
               ["$" + str('{:0,.0f}'.format(x)) for x in range(y_min, y_max+1, 10000000)], fontsize=9)
    plt.xticks(range(x_min, x_max+1, 1), [str(x) for x in range(x_min, x_max+1, 1)], fontsize=9, rotation=45)

    plt.tick_params(axis="both", which="both", bottom="off", top="off",    
                    labelbottom="on", left="off", right="off", labelleft="on") 

    # Add a text label to the right end of every line. Most of the code below    
    # is adding specific offsets y position because some labels overlapped.    
    #y_pos = terminal.cashflows.Revenues.values[-1]
    #plt.text(x_max+1, y_pos, 'Revenues', fontsize=14, color='#2CA02C') 

    # Text on the top of each barplot
    #for i in range(len(r4)):
    #    plt.text(x = r4[i]-0.5 , y = bars4[i]+0.1, s = label[i], size = 6)

    # Add the title
    plt.text((x_min+x_max)/2, 1.2*y_max, "Terminal Revenues", fontsize=17, ha="center")  

    # Adjust the margins
    plt.subplots_adjust(bottom= 0.2, top = 0.98)

    # Show graphic
    plt.show()


# ### Revenues + Capex + Opex (nominal value)

# In[ ]:


def revenue_capex_opex(terminal):
    
    cashflows = terminal.cashflows
    cashflows = cashflows[['Year', 'Revenues', 'Capex', 'Opex']]
    NPV = terminal.NPV

    x_max = int(max(cashflows['Year']))
    x_min = int(min(cashflows['Year']))
    y_max = []
    y_min = []
    for i in range (1, len(cashflows.columns)):
        y_max.append(max(cashflows.iloc[:,i]))
        y_min.append(min(cashflows.iloc[:,i]))
    y_max = int(max(y_max))
    y_max = int(np.ceil(y_max/20000000)*20000000)
    y_min = int(min(y_min))
    y_min = int((np.ceil(y_min/20000000)-1)*20000000)

    # Create bars
    barWidth = 0.7
    revenue = terminal.cashflows.Revenues.values 
    opex = terminal.cashflows.Opex.values
    capex = terminal.cashflows.Capex.values+opex

    # The X position of bars
    x1 = terminal.cashflows.Year.values

    # Create barplot
    plt.bar(x1, revenue, width = barWidth, color = '#2CA02C', label='Revenues')
    plt.bar(x1, capex, width = barWidth, color = '#D62728', label='Capex')
    plt.bar(x1, opex, width = barWidth, color = '#1F77B4', label='Opex')

    # Remove the plot frame lines  
    ax = plt.subplot(111)    
    ax.spines["top"].set_visible(False)    
    ax.spines["bottom"].set_visible(False)    
    ax.spines["right"].set_visible(False)    
    ax.spines["left"].set_visible(False)    

    # Ensure that the axis ticks only show up on the bottom and left of the plot.     
    ax.get_xaxis().tick_bottom()    
    ax.get_yaxis().tick_left()

    # Create legend
    #plt.legend()

    # Text below each barplot with a rotation at 90°
    plt.yticks(range(y_min, y_max+1, 20000000), 
               ["$" + str('{:0,.0f}'.format(x)) for x in range(y_min, y_max+1, 20000000)], fontsize=9)
    plt.xticks(range(x_min, x_max+1, 1), [str(x) for x in range(x_min, x_max+1, 1)], fontsize=9, rotation=45)

    # Horizontal dashed lines instead of y-ticks
    for y in range(y_min-1 , y_max+1, 20000000):    
        plt.plot((x_min-1, x_max+1), (y, y), "--", lw=0.4, color="black", alpha=0.3)  

    plt.tick_params(axis="both", which="both", bottom="off", top="off",    
                    labelbottom="on", left="off", right="off", labelleft="on") 

    # Add a text label to the right end of every line. Most of the code below    
    # is adding specific offsets y position because some labels overlapped.    
    y_pos_revenue = y_max * 0.9
    y_pos_capex = y_max * 0.7
    y_pos_opex = y_max * 0.5
    plt.text(x_max+2, y_pos_revenue, 'Revenues', fontsize=14, color='#2CA02C')
    plt.text(x_max+2, y_pos_capex, 'Capex', fontsize=14, color='#D62728')
    plt.text(x_max+2, y_pos_opex, 'Opex', fontsize=14, color='#1F77B4')

    # Text on the top of each barplot
    #for i in range(len(r4)):
    #    plt.text(x = r4[i]-0.5 , y = bars4[i]+0.1, s = label[i], size = 6)

    # Add the title
    plt.text((x_min+x_max)/2, 1.2*y_max, "Terminal Revenues, Capex and Opex in Nominal Values", fontsize=14, ha="center")  

    # Adjust the margins
    plt.subplots_adjust(bottom= 0.2, top = 0.98)

    # Show graphic
    plt.show()


# ### All cashflows seperate

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

# ### Determine development trajectory of terminals assets

# In[4]:


# Line plots of the development trajectory of all terminal assets

def asset_trajectory(terminal, simulation_window, start_year):

    assets = np.zeros(shape=(simulation_window, 12))
    percentages = np.zeros(shape=(simulation_window, 12))
    quays, berths, cranes, storage, stations, quay_conveyors, hinterland_conveyors = terminal.quays, terminal.berths, terminal.cranes, terminal.storage, terminal.stations, terminal.quay_conveyors, terminal.hinterland_conveyors

    ############################################################################################################
    # For each year, register how many assets are online 
    ############################################################################################################
    
    for t in range (simulation_window):

        # Years (Column 0)
        year = t + start_year 
        assets[t,0] = year

        # Quays (Column 1)
        online = []
        for i in range (len(quays)):
            if quays[i].online_date <= year:
                online.append(quays[i].length)
        assets[t,1] = int(np.sum(online))

        # Berths (Column 2)
        online = []
        for i in range (len(berths)):
            if berths[i].online_date <= year:
                online.append(1)
        assets[t,2] = int(np.sum(online))

        # Gantry cranes (Column 3)
        online = []
        for i in range (len(cranes[0])):
            if cranes[0][i].online_date <= year:
                online.append(1)
        assets[t,3] = int(np.sum(online))

        # Harbour cranes (Column 4)
        online = []
        for i in range (len(cranes[1])):
            if cranes[1][i].online_date <= year:
                online.append(1)
        assets[t,4] = int(np.sum(online))

        # Mobile cranes (Column 5)
        online = []
        for i in range (len(cranes[2])):
            if cranes[2][i].online_date <= year:
                online.append(1)
        assets[t,5] = int(np.sum(online))

        # Screw unloaders (Column 6)
        online = []
        for i in range (len(cranes[3])):
            if cranes[3][i].online_date <= year:
                online.append(1)
        assets[t,6] = int(np.sum(online))

        # Silos (Column 7)
        online = []
        for i in range (len(storage[0])):
            if storage[0][i].online_date <= year:
                online.append(storage[0][i].capacity)
        assets[t,7] = int(np.sum(online))

        # Warehouses (Column 8)
        online = []
        for i in range (len(storage[1])):
            if storage[1][i].online_date <= year:
                online.append(storage[1][i].capacity)
        assets[t,8] = int(np.sum(online))

        # Hinterland loading stations (Column 9)
        online = []
        for i in range (len(stations)):
            if stations[i].online_date <= year:
                online.append(stations[i].capacity)
        assets[t,9] = int(np.sum(online))

        # Quay conveyors (Column 10) 
        online = []
        for i in range (len(quay_conveyors)):
            if quay_conveyors[i].online_date <= year:
                online.append(quay_conveyors[i].capacity)
        assets[t,10] = int(np.sum(online))

        # Hinterland conveyors (Column 11)
        online = []
        for i in range (len(hinterland_conveyors)):
            if hinterland_conveyors[i].online_date <= year:
                online.append(hinterland_conveyors[i].capacity)
        assets[t,11] = int(np.sum(online))

    online_assets = pd.DataFrame(assets, columns=['Year', 'Online quay length', 'Berths online', 'Gantry cranes online', 
                                                  'Harbour cranes online', 'Mobile cranes online', 'Screw unloaders online', 
                                                  'Silo capacity online', 'Warehouse capacity online', 
                                                  'Loading station capacity online', 'Quay conveyor capacity online', 
                                                  'Hinterland conveyor capacity online'])
    online_assets = online_assets.astype(int)

    ############################################################################################################
    # For each year, register how many assets are online. Results are shown as a percentage of final capacity
    ############################################################################################################
    
    def percentage_visualisation(online_assets, simulation_window):
    
        for t in range (simulation_window):

            # Years (Column 0)
            year = t + start_year 

            # Quays (Column 1)
            online = []
            for i in range (len(quays)):
                if quays[i].online_date <= year:
                    online.append(quays[i].length)
            percentages[t,1] = np.sum(online)/assets[simulation_window-1,1]

            # Berths (Column 2)
            online = []
            for i in range (len(berths)):
                if berths[i].online_date <= year:
                    online.append(1)
            percentages[t,2] = np.sum(online)/assets[simulation_window-1,2]

            # Gantry cranes (Column 3)
            online = []
            for i in range (len(cranes[0])):
                if cranes[0][i].online_date <= year:
                    online.append(1)
            percentages[t,3] = np.sum(online)/assets[simulation_window-1,3]

            # Harbour cranes (Column 4)
            online = []
            for i in range (len(cranes[1])):
                if cranes[1][i].online_date <= year:
                    online.append(1)
            percentages[t,4] = np.sum(online)/assets[simulation_window-1,4]

            # Mobile cranes (Column 5)
            online = []
            for i in range (len(cranes[2])):
                if cranes[2][i].online_date <= year:
                    online.append(1)
            percentages[t,5] = np.sum(online)/assets[simulation_window-1,5]

            # Screw unloaders (Column 6)
            online = []
            for i in range (len(cranes[3])):
                if cranes[3][i].online_date <= year:
                    online.append(1)
            percentages[t,6] = np.sum(online)/assets[simulation_window-1,6]

            # Silos (Column 7)
            online = []
            for i in range (len(storage[0])):
                if storage[0][i].online_date <= year:
                    online.append(storage[0][i].capacity)
            percentages[t,7] = np.sum(online)/assets[simulation_window-1,7]

            # Warehouses (Column 8)
            online = []
            for i in range (len(storage[1])):
                if storage[1][i].online_date <= year:
                    online.append(storage[1][i].capacity)
            percentages[t,8] = np.sum(online)/assets[simulation_window-1,8]

            # Hinterland loading stations (Column 9)
            online = []
            for i in range (len(stations)):
                if stations[i].online_date <= year:
                    online.append(stations[i].capacity)
            percentages[t,9] = np.sum(online)/assets[simulation_window-1,9]

            # Quay conveyors (Column 10) 
            online = []
            for i in range (len(quay_conveyors)):
                if quay_conveyors[i].online_date <= year:
                    online.append(quay_conveyors[i].capacity)
            percentages[t,10] = np.sum(online)/assets[simulation_window-1,10]

            # Hinterland conveyors (Column 11)
            online = []
            for i in range (len(hinterland_conveyors)):
                if hinterland_conveyors[i].online_date <= year:
                    online.append(hinterland_conveyors[i].capacity)
            percentages[t,11] = np.sum(online)/assets[simulation_window-1,11]

        online_assets_perc = pd.DataFrame(percentages, columns=['Year', 'Online quay length', 'Berths online', 'Gantry cranes online',
                                                                'Harbour cranes online', 'Mobile cranes online', 'Screw unloaders online',
                                                                'Silo capacity online', 'Warehouse capacity online', 
                                                                'Loading station capacity online', 'Quay conveyor capacity online', 
                                                                'Hinterland conveyor capacity online'])
        online_assets_perc = online_assets_perc.fillna(0)
        online_assets_perc = online_assets_perc *100
        online_assets_perc = online_assets_perc.astype(int)
        online_assets_perc['Year'] = online_assets['Year']
        
        return online_assets_perc
    
    ############################################################################################################
    # Slice the dataframe into seperate dataframes, each focussed on a specific area within the terminal
    ############################################################################################################
    
    quays = online_assets[['Year', 'Online quay length']]
    berths = online_assets[['Year', 'Berths online','Gantry cranes online', 'Gantry cranes online', 'Mobile cranes online', 'Screw unloaders online']]
    berths = berths.loc[:, (berths != 0).any(axis=0)]
    storage = online_assets[['Year', 'Silo capacity online','Warehouse capacity online']]
    storage = storage.loc[:, (storage != 0).any(axis=0)]
    station = online_assets[['Year', 'Loading station capacity online']]
    conveyors = online_assets[['Year', 'Quay conveyor capacity online','Hinterland conveyor capacity online']]
    
    ############################################################################################################
    # Line plot function uses a dataframe object as input
    ############################################################################################################ 
    
    def line_plot(data):

        # Determining max and min x and y values
        x_max = int(max(data['Year']))
        x_min = int(min(data['Year']))
        y_max = []
        y_min = []
        for i in range (1, len(data.columns)):
            y_max.append(max(data.iloc[:,i]))
            y_min.append(min(data.iloc[:,i]))
        y_max = int(max(y_max))
        y_min = int(max(y_min))

        # Read the data into a pandas DataFrame.    
        #gender_degree_data = pd.read_csv("http://www.randalolson.com/wp-content/uploads/percent-bachelors-degrees-women-usa.csv")    
        #gender_degree_data = online_assets_perc

        # These are the "Tableau 20" colors as RGB.    
        tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
                     (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
                     (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
                     (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
                     (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]    

        # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.    
        for i in range(len(tableau20)):    
            r, g, b = tableau20[i]    
            tableau20[i] = (r / 255., g / 255., b / 255.)    

        # You typically want your plot to be ~1.33x wider than tall
        # Common sizes: (10, 7.5) and (12, 9)    
        plt.figure(figsize=(6, 4))    

        # Remove the plot frame lines
        ax = plt.subplot(111)    
        ax.spines["top"].set_visible(False)    
        ax.spines["bottom"].set_visible(False)    
        ax.spines["right"].set_visible(False)    
        ax.spines["left"].set_visible(False)    

        # Ensure that the axis ticks only show up on the bottom and left of the plot.      
        ax.get_xaxis().tick_bottom()    
        ax.get_yaxis().tick_left()    

        # Limit the range of the plot to only where the data is  
        # Avoid unnecessary whitespace
        plt.ylim(y_min, y_max)
        plt.xlim(x_min-1, x_max+1)    

        # Make sure your axis ticks are large enough to be easily read      
        plt.yticks(range(y_min, y_max+1, int(np.ceil((y_max-y_min)/10))), 
                   [str(x) for x in range(y_min, y_max+1, int(np.ceil((y_max-y_min)/10)))], fontsize=14)
        plt.xticks(range(x_min, x_max+1, int((x_max-x_min)/4)), [str(x) for x in range(x_min, x_max+1, int((x_max-x_min)/4))], fontsize=14)  

        # Provide tick lines across the plot to help your viewers trace along    
        # the axis ticks. Make sure that the lines are light and small so they    
        # don't obscure the primary data lines    
        for y in range(y_min + int(np.ceil((y_max-y_min)/10)), y_max+1, int(np.ceil((y_max-y_min)/10))):    
            plt.plot((x_min-1, x_max+1), (y, y), "--", lw=0.5, color="black", alpha=0.3)    

        # Remove the tick marks; they are unnecessary with the tick lines we just plotted    
        plt.tick_params(axis="both", which="both", bottom="off", top="off",    
                        labelbottom="on", left="off", right="off", labelleft="on")    

        # The names of each asset equals the name of the corresponding dataframe column
        asset_names = data.loc[:, data.columns != 'Year'].columns.values

        for rank, column in enumerate(asset_names):    
            # Plot each line separately with its own color, using the Tableau 20    
            # color set in order.    
            plt.plot(data.Year.values, data[column.replace("\n", " ")].values, lw=2.5, color=tableau20[rank])       

            # Add a text label to the right end of every line. Most of the code below    
            # is adding specific offsets y position because some labels overlapped.    
            y_pos = data[column.replace("\n", " ")].values[-1] - 0.5       

            # Again, make sure that all labels are large enough to be easily read    
            # by the viewer.    
            plt.text(x_max+1, y_pos, column, fontsize=14, color=tableau20[rank])    

        # matplotlib's title() call centers the title on the plot, but not the graph,    
        # so I used the text() call to customize where the title goes.    

        # Make the title big enough so it spans the entire plot, but don't make it    
        # so big that it requires two lines to show.    

        # Note that if the title is descriptive enough, it is unnecessary to include    
        # axis labels; they are self-evident, in this plot's case.    
        plt.text((x_min + x_max)/2, 1.2*y_max, "Asset capacity trajectory", fontsize=17, ha="center")    

        # Always include your data source(s) and copyright notice! And for your    
        # data sources, tell your viewers exactly where the data came from,    
        # preferably with a direct link to the data. Just telling your viewers    
        # that you used data from the "U.S. Census Bureau" is completely useless:    
        # the U.S. Census Bureau provides all kinds of data, so how are your    
        # viewers supposed to know which data set you used?    
        plt.text(x_max+1, y_min-0.1*y_min, "Data source: Optimization model", fontsize=10)    

        # Finally, save the figure as a PNG.    
        # You can also save it as a PDF, JPEG, etc.    
        # Just change the file extension in this call.    
        # bbox_inches="tight" removes all the extra whitespace on the edges of your plot.    
        #plt.savefig("percent-bachelors-degrees-women-usa.png", bbox_inches="tight") 
    
    quay_plot = line_plot(quays)
    berths_plot = line_plot(berths)
    storage_plot = line_plot(storage)
    stations_plot = line_plot(station)
    conveyor_plot = line_plot(conveyors)

    return


# # Compare investment triggers

# ### Compare capex

# In[ ]:


def revenues(terminal):
    
    cashflows = terminal.cashflows
    revenues = cashflows[['Year', 'Revenues']]

    x_max = int(max(revenues['Year']))
    x_min = int(min(revenues['Year']))
    y_max = []
    y_min = []
    for i in range (1, len(revenues.columns)):
        y_max.append(max(revenues.iloc[:,i]))
        y_min.append(min(revenues.iloc[:,i]))
    y_max = int(max(y_max))
    y_max = int(np.ceil(y_max/10000000)*10000000)
    y_min = int(max(y_min))


    # Create figure
    #revenue_plot = plt.figure(figsize=(6, 4.5))

    # Create bars
    barWidth = 0.7
    bars1 = terminal.cashflows.Revenues.values

    # The X position of bars
    x1 = terminal.cashflows.Year.values

    # Create barplot
    plt.bar(x1, bars1, width = barWidth, color = '#2CA02C', label='Revenues')

    # Remove the plot frame lines  
    ax = plt.subplot(111)    
    ax.spines["top"].set_visible(False)    
    ax.spines["bottom"].set_visible(False)    
    ax.spines["right"].set_visible(False)    
    ax.spines["left"].set_visible(False)    

    # Ensure that the axis ticks only show up on the bottom and left of the plot.     
    ax.get_xaxis().tick_bottom()    
    ax.get_yaxis().tick_left()

    # Create legend
    #plt.legend()

    # Text below each barplot with a rotation at 90°
    plt.yticks(range(y_min, y_max+1, 10000000), 
               ["$" + str('{:0,.0f}'.format(x)) for x in range(y_min, y_max+1, 10000000)], fontsize=9)
    plt.xticks(range(x_min, x_max+1, 1), [str(x) for x in range(x_min, x_max+1, 1)], fontsize=9, rotation=45)

    plt.tick_params(axis="both", which="both", bottom="off", top="off",    
                    labelbottom="on", left="off", right="off", labelleft="on") 

    # Add a text label to the right end of every line. Most of the code below    
    # is adding specific offsets y position because some labels overlapped.    
    #y_pos = terminal.cashflows.Revenues.values[-1]
    #plt.text(x_max+1, y_pos, 'Revenues', fontsize=14, color='#2CA02C') 

    # Text on the top of each barplot
    #for i in range(len(r4)):
    #    plt.text(x = r4[i]-0.5 , y = bars4[i]+0.1, s = label[i], size = 6)

    # Add the title
    plt.text((x_min+x_max)/2, 1.2*y_max, "Terminal Revenues", fontsize=17, ha="center")  

    # Adjust the margins
    plt.subplots_adjust(bottom= 0.2, top = 0.98)

    # Show graphic
    plt.show()

