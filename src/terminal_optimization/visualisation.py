
# coding: utf-8

# In[1]:


import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ### Plot colours

# In[2]:


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


# ### Import Plotly packages

# In[3]:


# Log in to Plotly servers
import plotly
#plotly.tools.set_credentials_file(username='wijzermans', api_key='FKGDvSah3z5WCNREBZEq')
plotly.tools.set_credentials_file(username='wijnandijzermans', api_key='xeDEwwpCK3aLLR4TIrM9')

# (*) To communicate with Plotly's server, sign in with credentials file
import plotly.plotly as py  
import plotly.graph_objs as go
import plotly.tools as tls 
from plotly.graph_objs import *
get_ipython().run_line_magic('matplotlib', 'inline')


# # Scenarios

# In[4]:


def scenario(commodities, simulation_window, start_year):
    
    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]
    demand_matrix = np.zeros(shape=(len(commodities[0].years), 4))
    
    ############################################################################################################
    # For each year, register each commodities' demand 
    ############################################################################################################
    
    for t in range (len(commodities[0].years)):

        # Years (Column 0)
        year = t + commodities[0].years[0] 
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
    y_min = int((np.ceil(min(y_min)/100000)-1)*100000)

    # You typically want your plot to be ~1.33x wider than tall
    # Common sizes: (10, 7.5) and (12, 9)    
    plt.figure(figsize=(10, 7.5))    

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
    plt.yticks(range(y_min, y_max+1, 500000), 
               [str(x) for x in range(y_min, y_max+1, 500000)], fontsize=14)
    plt.xticks(range(x_min, x_max+1, 1), [str(x) for x in range(x_min, x_max+1, 1)], fontsize=14, rotation=45)
    
    # Provide tick lines across the plot to help your viewers trace along    
    # the axis ticks. Make sure that the lines are light and small so they    
    # don't obscure the primary data lines    
    for y in range(y_min+200000, y_max+1, 200000):    
        plt.plot((x_min-1, x_max+1), (y, y), "--", lw=0.5, color="black", alpha=0.3)    

    # Remove the tick marks; they are unnecessary with the tick lines we just plotted    
    plt.tick_params(axis="both", which="both", bottom=False, top=False,    
                    labelbottom=True, left=False, right=False, labelleft=True)   

    # The names of each asset equals the name of the corresponding dataframe column
    commodity_names = demand.loc[:, demand.columns != 'Year'].columns.values
    
    # Plot each commodity
    plt.plot(demand.Year.values, demand['Maize demand'].values, lw=2.5, color=tableau20[0])
    plt.plot(demand.Year.values, demand['Soybean demand'].values, lw=2.5, color=tableau20[1])
    plt.plot(demand.Year.values, demand['Wheat demand'].values, lw=2.5, color=tableau20[0])
    plt.plot((start_year, start_year), (y_min, y_max), "--", lw=3, color="black", alpha=0.3)
    
    #plt.text(x_max+1, y_max*1.0, 'Maize demand', fontsize=16, color=tableau20[0])
    #plt.text(x_max+1, y_max*0.9, 'Soybean demand', fontsize=16, color=tableau20[1])
    plt.text(x_max+1, max(demand['Maize demand']), 'Maize demand', fontsize=16, color=tableau20[0])
    plt.text(start_year-1, 3000000, "Historic data", fontsize=16, ha="center", rotation=90)
    plt.text(start_year+1, 3000000, "Scenario", fontsize=16, ha="center", rotation=90)

    # matplotlib's title() call centers the title on the plot, but not the graph,    
    # so I used the text() call to customize where the title goes.    

    # Make the title big enough so it spans the entire plot, but don't make it    
    # so big that it requires two lines to show.    

    # Note that if the title is descriptive enough, it is unnecessary to include    
    # axis labels; they are self-evident, in this plot's case.    
    plt.text((x_min + x_max)/2, 1.1*y_max, "Demand Scenario", fontsize=20, ha="center")    

    # Always include your data source(s) and copyright notice! And for your    
    # data sources, tell your viewers exactly where the data came from,    
    # preferably with a direct link to the data. Just telling your viewers    
    # that you used data from the "U.S. Census Bureau" is completely useless:    
    # the U.S. Census Bureau provides all kinds of data, so how are your    
    # viewers supposed to know which data set you used?    
    plt.text(x_max+1, y_min-0.1*y_min, "Data source: Scenario generator", horizontalalignment='left', fontsize=10)    

    # Finally, save the figure as a PNG.    
    # You can also save it as a PDF, JPEG, etc.    
    # Just change the file extension in this call.    
    # bbox_inches="tight" removes all the extra whitespace on the edges of your plot.  
    
    # Save figure at designated folder. Create scenario folder if it is not present
    cwd = os.getcwd()
    folder = cwd + str('\\visualisations\\scenarios')
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    # Save figure
    plt.savefig(str(folder + "\\Scenario.png"), bbox_inches="tight")
    
    # Online-based, interactive graphic
    figure = plt.gcf()
    #py.iplot_mpl(figure, filename='Scenario')

    return


# In[5]:


def consecutive_reative_trend(commodities, simulation_window, start_year):
    
    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]
    demand_matrix = np.zeros(shape=(len(commodities[0].years), 4))
    
    ############################################################################################################
    # For each year, register each commodities' demand 
    ############################################################################################################
    
    for t in range (len(commodities[0].years)):

        # Years (Column 0)
        year = t + commodities[0].years[0] 
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
    y_min = int((np.ceil(min(y_min)/100000)-1)*100000)

    for z in range (8):
        # You typically want your plot to be ~1.33x wider than tall
        plt.figure(figsize=(10, 7.5))    

        # Remove the plot frame lines
        ax = plt.subplot(111)    
        ax.spines["top"].set_visible(False)    
        ax.spines["bottom"].set_visible(False)    
        ax.spines["right"].set_visible(False)    
        ax.spines["left"].set_visible(False)    

        # Ensure that the axis ticks only show up on the bottom and left of the plot.      
        ax.get_xaxis().tick_bottom()    
        ax.get_yaxis().tick_left()    

        # Limit the range of the plot to only where the data is to avoid unnecessary whitespace
        plt.ylim(y_min, y_max)
        plt.xlim(x_min-1, 2031)    

        # Make sure your axis ticks are large enough to be easily read      
        plt.yticks(range(y_min, y_max+1, 500000), 
               [str(x) for x in range(y_min, y_max+1, 500000)], fontsize=19)
        plt.xticks(range(x_min, x_max+1, 2), [str(x) for x in range(x_min, x_max+1, 2)], fontsize=19, rotation=45)
        
        # Provide tick lines across the plot to help your viewers trace along    
        # the axis ticks. Make sure that the lines are light and small so they    
        # don't obscure the primary data lines    
        for y in range(y_min+200000, y_max+1, 200000):    
            plt.plot((x_min-1, x_max+1), (y, y), "--", lw=0.5, color="black", alpha=0.3)    

        # Remove the tick marks; they are unnecessary with the tick lines we just plotted    
        plt.tick_params(axis="both", which="both", bottom=False, top=False,    
                        labelbottom=True, left=False, right=False, labelleft=True)   

        # The names of each asset equals the name of the corresponding dataframe column
        commodity_names = demand.loc[:, demand.columns != 'Year'].columns.values

        # Plot each commodity
        plt.plot(demand.Year[0:5+z].values, demand['Maize demand'][0:5+z].values, lw=2.5, color=tableau20[0])
        plt.plot((start_year, start_year), (y_min, y_max), "--", lw=3, color="black", alpha=0.3)

        # Name each plot line
        plt.text(demand.Year[5+z] + 1, demand['Maize demand'][5+z], 'Maize demand', fontsize=19, color=tableau20[0])  
        plt.text(start_year-1, 3000000, "Historic data", fontsize=16, ha="center", rotation=90)
        plt.text(start_year+1, 3000000, "Scenario", fontsize=16, ha="center", rotation=90)
 

        # Make the title big enough so it spans the entire plot, but don't make it so big that it requires two lines to show.    

        # Note that if the title is descriptive enough, it is unnecessary to include    
        # axis labels; they are self-evident, in this plot's case.    
        plt.text((x_min + x_max)/2, 1.1*y_max, "Commodity demand", fontsize=24, ha="center")    

        # Include data source    
        #plt.text(x_max+1, y_min-0.1*y_min, "Data source: Forecasting model", fontsize=10)    
        
        # Save figure at designated folder. Create scenario folder if it is not present
        cwd = os.getcwd()
        folder = cwd + str('\\visualisations\\forecasts\\reactive')
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Save figure
        file = folder + str("\\Forecast ") + str(z) + str(".png")
        plt.savefig(str(file), bbox_inches="tight") 

    return


# In[6]:


def consecutive_predictive_trend(commodities, simulation_window, start_year):

    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]
    demand_matrix = np.zeros(shape=(len(commodities[0].years), 4))
    
    ############################################################################################################
    # For each year, register each commodities' demand 
    ############################################################################################################
    
    for t in range (len(commodities[0].years)):

        # Years (Column 0)
        year = t + commodities[0].years[0] 
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
    y_min = int((np.ceil(min(y_min)/100000)-1)*100000)

    for zz in range (2):
        if zz == 0: 
            trendtype = 'linear'
        if zz == 1:
            trendtype = '2nd polynomial'
            
        for z in range (6):
            # You typically want your plot to be ~1.33x wider than tall
            # Common sizes: (10, 7.5) and (12, 9)    
            plt.figure(figsize=(10, 7.5))    

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
            plt.yticks(range(y_min, y_max+1, 500000), 
               [str(x) for x in range(y_min, y_max+1, 500000)], fontsize=19)
            plt.xticks(range(x_min, x_max+1, 2), [str(x) for x in range(x_min, x_max+1, 2)], fontsize=19, rotation=45)

            # Provide tick lines across the plot to help your viewers trace along    
            # the axis ticks. Make sure that the lines are light and small so they    
            # don't obscure the primary data lines    
            for y in range(y_min+200000, y_max+1, 200000):    
                plt.plot((x_min-1, x_max+1), (y, y), "--", lw=0.5, color="black", alpha=0.3)    

            # Remove the tick marks; they are unnecessary with the tick lines we just plotted    
            plt.tick_params(axis="both", which="both", bottom=False, top=False,    
                            labelbottom=True, left=False, right=False, labelleft=True)   

            # The names of each asset equals the name of the corresponding dataframe column
            commodity_names = demand.loc[:, demand.columns != 'Year'].columns.values

            foresight = 5
            hindsight = 5
            start_year = 2018
            year = start_year + z
            timestep = year - start_year

            # List historic demand
            start_row = demand.loc[demand['Year']==2018].index[0]
            if hindsight > start_row:
                hindsight = start_row
            previous_years = commodities[0].years[timestep+start_row-hindsight:timestep+start_row]
            previous_demand = []
            for i in range (len(commodities)):
                previous_demand.append(commodities[i].demand[timestep+start_row-hindsight:timestep+start_row])
            
            if zz == 0:
                # Create linear trendline
                trendlines = []
                trendline_years = range (previous_years[0], previous_years[-1]+foresight+1, 1)
                for i in range (len(commodities)):
                    coefficients = np.polyfit(previous_years, previous_demand[i], 1)
                    trendline = []
                    for k in trendline_years:
                        trendline.append(coefficients[0]*k+coefficients[1])
                    trendlines.append(trendline)

            if zz == 1:
                # Create 2nd order polynomial trendline
                trendlines = []
                trendline_years = range (previous_years[0], previous_years[-1]+foresight+1)
                for i in range (len(commodities)):
                    coefficients = np.polyfit(previous_years, previous_demand[i], 2)
                    trendline = []
                    for k in trendline_years:
                        trendline.append(coefficients[0]*k**2+coefficients[1]*k+coefficients[2])
                    trendlines.append(trendline)

            # Plot historic data
            plt.scatter(demand.Year[0:5+z].values, demand['Maize demand'][0:5+z].values, lw=2.5, color=tableau20[0])
            plt.text(demand.Year[z]-2, demand['Maize demand'][3+z]+100000, 'Previous Demand', fontsize=19, color=tableau20[0])

            # Plot trendline
            plt.plot(trendline_years, trendlines[2], lw=2.5, color=tableau20[1])
            plt.text(trendline_years[-1]+1, min(max(1000000,trendlines[2][-1]),y_max), 'Demand forecast', fontsize=19, color=tableau20[1])  

            # Plot border of historic and scenario data
            plt.plot((start_year, start_year), (y_min, y_max), "--", lw=3, color="black", alpha=0.3)
            plt.text(start_year-1, 3000000, "Historic data", fontsize=19, ha="center", rotation=90)
            plt.text(start_year+1, 3000000, "Scenario", fontsize=19, ha="center", rotation=90)
        
            # matplotlib's title() call centers the title on the plot, but not the graph,    
            # so I used the text() call to customize where the title goes.    

            # Make the title big enough so it spans the entire plot, but don't make it    
            # so big that it requires two lines to show.    

            # Note that if the title is descriptive enough, it is unnecessary to include    
            # axis labels; they are self-evident, in this plot's case.    
            plt.text((x_min + x_max)/2, 1.1*y_max, "Commodity demand", fontsize=24, ha="center")    

            # Always include your data source(s) and copyright notice! And for your    
            # data sources, tell your viewers exactly where the data came from,    
            # preferably with a direct link to the data. Just telling your viewers    
            # that you used data from the "U.S. Census Bureau" is completely useless:    
            # the U.S. Census Bureau provides all kinds of data, so how are your    
            # viewers supposed to know which data set you used?    
            #plt.text(x_max+1, y_min-0.1*y_min, "Data source: Forecasting model", fontsize=10)    
            
            # Save figure at designated folder. Create folder if it is not present
            cwd = os.getcwd()
            folder = cwd + str('\\visualisations\\forecasts\\predictive') + str('\\') + str(trendtype)
            if not os.path.exists(folder):
                os.makedirs(folder)

            # Save figure
            file = folder + str("\\Forecast ") + str(z) + str ('(') + str(trendtype) + str (')') + str(".png")
            plt.savefig(str(file), bbox_inches="tight") 

    return
    


# # Cash Flows
# - Profit / Loss (nominal value)
# - Profit / Loss (present value)
# - Revenues (nominal value)
# - Revenues + Capex + Opex (nominal value)
# - NPV distribution
# - Risk sensitivity

# In[7]:


def revenue_capex_opex(terminal):
    
    cashflows = terminal.cashflows
    
    # Determine payback timestep
    payback_t = cashflows['Compounded profit'].loc[cashflows['Compounded profit'] == min(cashflows['Compounded profit'], key=abs)].index[0]
    
    # Construct data for underlying profit/loss area chart
    loss = []
    profit = []
    for t in range (len(cashflows['Compounded profit'])):
        if t < payback_t:
            loss.append(cashflows['Compounded profit'][t])
            profit.append(0)
        if t == payback_t:
            loss.append(0)
            profit.append(0)
        if t > payback_t:
            loss.append(0)
            profit.append(cashflows['Compounded profit'][t])

    # Plot bars
    trace1 = go.Bar(
        x=cashflows['Year'],
        y=cashflows['Revenues'],
        name='Revenues',
        marker=dict(
            color='#025928'
        )
    )
    trace2 = go.Bar(
        x=cashflows['Year'],
        y=cashflows['Capex'],
        name='Capex',
        marker=dict(
            color='#8c1c03'
        )
    )
    trace3 = go.Bar(
        x=cashflows['Year'],
        y=cashflows['Opex'],
        name='Opex',
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    )
    trace4 = go.Scatter(
        x=cashflows['Year'],
        y=loss,
        name='Loss',
        mode='none',
        line=dict(
            color='#8c1c03',
            shape='spline'),
        fill='tozeroy'
    )
    trace5 = go.Scatter(
        x=cashflows['Year'],
        y=profit,
        name='Profit',
        mode='none',
        line=dict(
            color='rgb(44, 160, 44)',
            shape='spline'),
        fill='tozeroy',
    )
    data = [trace1, trace2, trace3, trace4, trace5]
    layout = go.Layout(
        title='Terminal cashflows',

        xaxis=dict(
            tickfont=dict(
                size=24,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='Cashflows in USD ($)',
            titlefont=dict(
                size=27,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=24,
                color='rgb(107, 107, 107)'
            )
        ),       
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            font=dict(
                size=25,
                color='rgb(107, 107, 107)'
            )
        ),
        barmode='group',
        bargap=0.05,
        bargroupgap=0.1
    )
    
    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, filename='Revenue, Capex and Opex')


# ### Profit / Loss (nominal value)

# In[8]:


def profit_loss(terminal):
    
    cashflows = terminal.cashflows
    cashflows = cashflows[['Year', 'Profits']]

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
    bars1 = cashflows.Profits.values

    # The X position of bars
    x1 = cashflows.Year.values

    # Create barplot
    ax = plt.subplot(111)   
    plt.bar(x1, bars1, width = barWidth, color = '#3F5D7D', label='Profit')

    # Remove the plot frame lines
    ax.spines["top"].set_visible(False)    
    ax.spines["bottom"].set_visible(False)    
    ax.spines["right"].set_visible(False)    
    ax.spines["left"].set_visible(False)    

    # Ensure that the axis ticks only show up on the bottom and left of the plot.     
    ax.get_xaxis().tick_bottom()    
    ax.get_yaxis().tick_left()

    # Text below each barplot with a rotation at 90°
    plt.yticks(range(y_min, y_max+1, 20000000), 
               ["$" + str('{:0,.0f}'.format(x)) for x in range(y_min, y_max+1, 20000000)], fontsize=9)
    plt.xticks(range(x_min, x_max+1, 1), [str(x) for x in range(x_min, x_max+1, 1)], fontsize=9, rotation=45)

    plt.tick_params(axis="both", which="both", bottom=False, top=False,    
                    labelbottom=True, left=False, right=False, labelleft=True) 

    # Add the title
    plt.text((x_min+x_max)/2, 1.2*y_max, "Profit/Loss overview", fontsize=17, ha="center")

    # Adjust the margins
    plt.subplots_adjust(bottom= 0.2, top = 0.98)
    
    # Save figure at designated folder. Create folder if it is not present
    cwd = os.getcwd()
    folder = cwd + str('\\visualisations\\cashflows\\Profits') 
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Save figure
    file = folder + str("\\Profits (real)") + str(".png")
    plt.savefig(str(file), bbox_inches="tight") 

    # Show graphic
    plt.show()


# ### Profit / Loss (present value)

# In[9]:


def profit_loss_pv(terminal):
    
    cashflows = terminal.cashflows
    cashflows = cashflows[['Year', 'Profits', 'Profits (discounted)']]

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
    
    WACC = terminal.WACC_cashflows.WACC 
    WACC = [i * 100 for i in WACC]
    NPV = terminal.NPV

    # Create figure
    #revenue_plot = plt.figure(figsize=(6, 4.5))

    # Create bars
    barWidth = 0.7
    bars1 = cashflows['Profits (discounted)']
    bars2 = cashflows['Profits']

    # The X position of bars
    x1 = cashflows.Year.values

    # Create barplot
    ax = plt.subplot(111)  
    plt.bar(x1, bars2, width = barWidth, color = '#CEDCEF', label='Profit')
    plt.bar(x1, bars1, width = barWidth, color = '#3F5D7D', label='Profit (PV)')
    
    # Remove the plot frame lines    
    ax.spines["top"].set_visible(False)    
    ax.spines["bottom"].set_visible(False)    
    ax.spines["right"].set_visible(False)    
    ax.spines["left"].set_visible(False) 
    
    # Ensure that the axis ticks only show up on the bottom and left of the plot.     
    ax.get_xaxis().tick_bottom()    
    ax.get_yaxis().tick_left()
    
    # Remove the plot frame lines    
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

    plt.tick_params(axis="both", which="both", bottom=False, top=False,    
                    labelbottom=True, left=False, right=False, labelleft=True) 
    
    plt.text(((x_min + x_max)/2), y_min, "NPV: $" + str('{:0,.0f}'.format(NPV)), fontsize=11, ha="center")
    
    # Add the title
    plt.text((x_min+x_max)/2, 1.2*y_max, "Profit/Loss overview", fontsize=17, ha="center")
    
    # Create line plot
    ax1 = ax.twinx()
    ax1.spines["top"].set_visible(False)    
    ax1.spines["bottom"].set_visible(False)    
    ax1.spines["right"].set_visible(False)    
    ax1.spines["left"].set_visible(False) 
    
    #plt.ylim(0, 100)
    #plt.xlim(x_min-1, x_max+1)
    
    plt.plot(x1, WACC, color = '#D62728', label='WACC') 
    plt.yticks(range(0, 101, 10), 
               [str('{:0,.0f}'.format(x)) for x in range(0, 101, 10)], fontsize=9)
    plt.xticks(range(x_min, x_max+1, 1), [str(x) for x in range(x_min, x_max+1, 1)], fontsize=9, rotation=45)
    plt.text(2029, 20, "WACC discount", color = '#D62728', fontsize=9, ha="center")

    # Adjust the margins
    plt.subplots_adjust(bottom= 0.2, top = 0.98)
    
    # Save figure at designated folder. Create folder if it is not present
    cwd = os.getcwd()
    folder = cwd + str('\\visualisations\\cashflows\\Profits') 
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Save figure
    file = folder + str("\\Profits (PV and real)") + str(".png")
    plt.savefig(str(file), bbox_inches="tight") 

    # Show graphic
    plt.show()


# ### Revenues

# In[10]:


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
    ax = plt.subplot(111)
    plt.bar(x1, bars1, width = barWidth, color = '#2CA02C', label='Revenues')

    # Remove the plot frame lines      
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

    plt.tick_params(axis="both", which="both", bottom=False, top=False,    
                    labelbottom=True, left=False, right=False, labelleft=True) 

    # Add the title
    plt.text((x_min+x_max)/2, 1.2*y_max, "Terminal Revenues", fontsize=17, ha="center")  

    # Adjust the margins
    plt.subplots_adjust(bottom= 0.2, top = 0.98)
    
    # Save figure at designated folder. Create folder if it is not present
    cwd = os.getcwd()
    folder = cwd + str('\\visualisations\\cashflows\\Revenues') 
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Save figure
    file = folder + str("\\Revenues") + str(".png")
    plt.savefig(str(file), bbox_inches="tight") 

    # Show graphic
    plt.show()


# ### NPV distribution

# In[ ]:


from IPython.display import display, HTML


# In[11]:


def NPV_distribution_occupancy(iterations):

    NPV_matrix = np.zeros(shape=(len(iterations), 3))

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(iterations)):

        terminal = iterations[i]
        NPV = terminal.NPV
        allowable_occupancy = terminal.allowable_berth_occupancy

        # Iteration (Column 0)
        iteration = i 
        NPV_matrix[i,0] = iteration
        # NPV (Column 1)
        NPV_matrix[i,1] = NPV
        # Allowable occupancy
        NPV_matrix[i,2] = allowable_occupancy * 100

    NPV_spectrum = pd.DataFrame(NPV_matrix, columns=['Iteration', 'NPV', 'Allowable occupancy'])
    NPV_spectrum = NPV_spectrum.astype(int)
    
    # Assuming that dataframes df1 and df2 are already defined:
    display(NPV_spectrum)

    # Determining max and min x and y values
    x_max = int(max(NPV_spectrum['Allowable occupancy']))
    x_min = int(min(NPV_spectrum['Allowable occupancy'])) 
    y_max = int(max(NPV_spectrum['NPV']))
    y_max = int(np.ceil(y_max/40000000)*40000000)
    y_min = int(min(NPV_spectrum['NPV']))
    y_min = int((np.ceil(y_min/40000000)-1)*40000000)

    # Create figure
    #revenue_plot = plt.figure(figsize=(6, 4.5))

    # Create bars
    barWidth = 0.7
    bars1 = NPV_spectrum.NPV.values

    # The X position of bars
    x1 = NPV_spectrum['Allowable occupancy'].values

    # Create barplot
    ax = plt.subplot(111) 
    plt.bar(x1, bars1, width = barWidth, color = '#3F5D7D', label='NPV')

    # Remove the plot frame lines     
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
    plt.yticks(range(y_min, y_max+1, 40000000), 
               ["$" + str('{:0,.0f}'.format(x)) for x in range(y_min, y_max+1, 40000000)], fontsize=9)
    plt.xticks(range(x_min, x_max+1, 10), [str(x) + "%" for x in range(x_min, x_max+1, 10)], fontsize=9, rotation=45)

    plt.tick_params(axis="both", which="both", bottom=False, top=False,    
                    labelbottom=True, left=False, right=False, labelleft=True) 

    # Allowable occupancy value that coincides with maximum NPV
    max_iteration = NPV_spectrum.loc[NPV_spectrum['NPV']==max(NPV_spectrum['NPV'])].index[0]
    x_max_NPV = NPV_spectrum['Allowable occupancy'][max_iteration] 
    plt.plot((x_max_NPV, x_max_NPV), (y_min, y_max), "--", lw=1, color="black", alpha=0.3)
    plt.text(x_max_NPV, 0.3*y_min, str('Optimial: ''{:0,.0f}'.format(x_max_NPV))+"%", fontsize=9, ha="center", rotation=90)

    # Add a text label to the right end of every line. Most of the code below    
    # is adding specific offsets y position because some labels overlapped.    
    #y_pos = terminal.cashflows.Revenues.values[-1]
    #plt.text(x_max+1, y_pos, 'Revenues', fontsize=14, color='#2CA02C') 

    # Text on the top of each barplot
    #for i in range(len(r4)):
    #    plt.text(x = r4[i]-0.5 , y = bars4[i]+0.1, s = label[i], size = 6)

    # Add the title
    plt.text((x_min+x_max)/2, 1.2*y_max, "The impact of allowable berth occupation on NPV", fontsize=17, ha="center")

    # Adjust the margins
    plt.subplots_adjust(bottom= 0.2, top = 0.98)
    
    # Save figure at designated folder. Create folder if it is not present
    cwd = os.getcwd()
    folder = cwd + str('\\visualisations\\optimization\\NPV') 
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Save figure
    file = folder + str("\\Berth occupancy") + str(".png")
    plt.savefig(str(file), bbox_inches="tight") 

    # Show graphic
    plt.show()


# In[ ]:


def NPV_distribution_WACC(iterations):

    NPV_matrix = np.zeros(shape=(len(iterations), 3))

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(iterations)):

        terminal = iterations[i]
        NPV = terminal.NPV
        project_WACC = terminal.project_WACC

        # Iteration (Column 0)
        iteration = i 
        NPV_matrix[i,0] = iteration
        # NPV (Column 1)
        NPV_matrix[i,1] = NPV
        # Project WACC
        NPV_matrix[i,2] = project_WACC * 100

    NPV_spectrum = pd.DataFrame(NPV_matrix, columns=['Iteration', 'NPV', 'Project WACC'])
    NPV_spectrum['NPV'] = NPV_spectrum['NPV'].astype(int)
    
    # Assuming that dataframes df1 and df2 are already defined:
    display(NPV_spectrum)

    # Determining max and min x and y values
    x_max = int(max(NPV_spectrum['Project WACC']))
    x_min = int(min(NPV_spectrum['Project WACC'])) 
    y_max = int(max(NPV_spectrum['NPV']))
    y_max = int(np.ceil(y_max/40000000)*40000000)
    y_min = int(min(NPV_spectrum['NPV']))
    y_min = int((np.ceil(y_min/40000000)-1)*40000000)

    # Create figure
    #revenue_plot = plt.figure(figsize=(6, 4.5))

    # Create bars
    barWidth = 0.7
    bars1 = NPV_spectrum.NPV.values

    # The X position of bars
    x1 = NPV_spectrum['Project WACC'].values

    # Create barplot
    ax = plt.subplot(111) 
    plt.bar(x1, bars1, width = barWidth, color = '#3F5D7D', label='NPV')

    # Remove the plot frame lines     
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
    plt.yticks(range(y_min, y_max+1, 40000000), 
               ["$" + str('{:0,.0f}'.format(x)) for x in range(y_min, y_max+1, 40000000)], fontsize=9)
    plt.xticks(range(x_min, x_max+1, 10), [str(x) + "%" for x in range(x_min, x_max+1, 10)], fontsize=9, rotation=45)

    plt.tick_params(axis="both", which="both", bottom=False, top=False,    
                    labelbottom=True, left=False, right=False, labelleft=True) 

    # Project WACC value that coincides with maximum NPV
    max_iteration = NPV_spectrum.loc[NPV_spectrum['NPV']==max(NPV_spectrum['NPV'])].index[0]
    x_max_NPV = NPV_spectrum['Project WACC'][max_iteration] 
    plt.plot((x_max_NPV, x_max_NPV), (y_min, y_max), "--", lw=1, color="black", alpha=0.3)
    plt.text(x_max_NPV, 0.3*y_min, str('Optimial: ''{:0,.0f}'.format(x_max_NPV))+"%", fontsize=9, ha="center", rotation=90)

    # Add a text label to the right end of every line. Most of the code below    
    # is adding specific offsets y position because some labels overlapped.    
    #y_pos = terminal.cashflows.Revenues.values[-1]
    #plt.text(x_max+1, y_pos, 'Revenues', fontsize=14, color='#2CA02C') 

    # Text on the top of each barplot
    #for i in range(len(r4)):
    #    plt.text(x = r4[i]-0.5 , y = bars4[i]+0.1, s = label[i], size = 6)

    # Add the title
    plt.text((x_min+x_max)/2, 1.2*y_max, "The impact of the WACC on project NPV", fontsize=17, ha="center")

    # Adjust the margins
    plt.subplots_adjust(bottom= 0.2, top = 0.98)
    
    # Save figure at designated folder. Create folder if it is not present
    cwd = os.getcwd()
    folder = cwd + str('\\visualisations\\optimization\\NPV') 
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Save figure
    file = folder + str("\\Berth occupancy") + str(".png")
    plt.savefig(str(file), bbox_inches="tight") 

    # Show graphic
    plt.show()


# ### Risk Sensitivity

# In[12]:


def risk_sensitivity(cashflow_list, WACC_list):
    
    revenues_list = []
    capex_list = []
    opex_list = []
    compounded_profit_list = []
    loss_list = []
    profit_list = []
    years = cashflow_list[0]['Year']
    
    for i in range(len(cashflow_list)):
        revenues_list.append(cashflow_list[i]['Revenues'])
        capex_list.append(cashflow_list[i]['Capex'])
        opex_list.append(cashflow_list[i]['Opex'])
        compounded_profit_list.append(cashflow_list[i]['Compounded profit'])
        
        # Determine payback timestep
        payback_t = cashflow_list[i]['Compounded profit'].loc[cashflow_list[i]['Compounded profit'] == 
                                                              min(cashflow_list[i]['Compounded profit'], key=abs)].index[0]

        # Construct data for underlying profit/loss area chart
        loss = []
        profit = []
        for t in range (len(cashflow_list[i]['Compounded profit'])):
            if t < payback_t:
                loss.append(cashflow_list[i]['Compounded profit'][t])
                profit.append(0)
            if t == payback_t:
                loss.append(0)
                profit.append(0)
            if t > payback_t:
                loss.append(0)
                profit.append(cashflow_list[i]['Compounded profit'][t])
        loss_list.append(loss)
        profit_list.append(profit)
    
    bars = []
    for step in range (len(cashflow_list)):
        
        # Plot bars
        trace1 = go.Bar(
            x=years,
            y=revenues_list[step],
            visible=False,
            name='Revenues',
            marker=dict(
                color='#025928'
            )
        )
        trace2 = go.Bar(
            x=years,
            y=capex_list[step],
            visible=False,
            name='Capex',
            marker=dict(
                color='#8c1c03'
            )
        ) 
        trace3 = go.Bar(
            x=years,
            y=opex_list[step],
            visible=False,
            name='Opex',
            marker=dict(
                color='rgb(55, 83, 109)'
            )
        )
        trace4 = go.Scatter(
            x=years,
            y=loss_list[step],
            visible=False,
            opacity = 0.1,
            fill='tozeroy',
            mode='none',
            line=dict(
                color='#8c1c03',
                shape='spline'
            )
        )       
        trace5 = go.Scatter(
            x=years,
            y=profit_list[step],
            visible=False,
            opacity = 0.1,
            fill='tozeroy',
            mode='none',
            line=dict(
                color='rgb(55, 83, 109)',
                shape='spline'
            )
        )
        
        bars.append([trace1, trace2, trace3, trace4, trace5])
    
    data = bars[0]
    
    layout = go.Layout(
        title='Terminal cashflows in real terms',

        xaxis=dict(
            tickfont=dict(
                size=24,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='Cashflow in USD ($)',
            titlefont=dict(
                size=27,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=24,
                color='rgb(107, 107, 107)'
            )
        ),       
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            font=dict(
                size=27,
                color='black'
            )
        ),
        barmode='group',
        bargap=0.1,
        bargroupgap=0.05
    )
    
    fig = go.Figure(data=data, layout=layout)
    
    py.iplot(fig, filename='Risk sensitivity')
    
    return


# ### Demand vs Capacity

# In[13]:


def throughput(terminal):
    
    throughputs = terminal.throughputs
    start_year = throughputs[0].start_year
    
    throughput_matrix = np.zeros(shape=(len(throughputs), 4))
    
    for t in range (len(throughputs)):
        # Years (Column 0)
        year = t + start_year
        throughput_matrix[t,0] = year
        # Throughput (Column 1)
        throughput_matrix[t,1] = throughputs[t].demand
        # Capacity (Column 2)
        throughput_matrix[t,2] = throughputs[t].capacity
        # Demand (Column 3)
        throughput_matrix[t,3] = throughputs[t].demand
    
    df = pd.DataFrame(throughput_matrix, columns=['Year', 'Throughput', 'Capacity', 'Demand'])
    df = df.astype(int)
 
    # Plot bars
    trace1 = go.Scatter(
        x=df['Year'],
        y=df['Demand'],
        name='Demand',
        line=dict(
            color='#8c1c03',
            shape='spline'
        )
    )     
    trace2 = go.Bar(
        x=df['Year'],
        y=df['Capacity'],
        name='Capacity',
        opacity = 0.2,
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    ) 
    trace3 = go.Bar(
        x=df['Year'],
        y=df['Throughput'],
        name='Throughput',
        opacity = 0.9,
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    ) 
    
    
    data = [trace1, trace2, trace3]
    layout = go.Layout(
        title='Terminal throughput vs. capacity',

        xaxis=dict(
            tickfont=dict(
                size=24,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='Throughputs [t/annum]',
            titlefont=dict(
                size=27,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=24,
                color='rgb(107, 107, 107)'
            )
        ),       
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            font=dict(
                size=25,
                color='rgb(107, 107, 107)'
            )
        ),
        barmode='group',
        bargap=0.1,
        bargroupgap=0.05
    )
    
    fig = go.Figure(data=data, layout=layout)
    
    # Save figure at designated folder. Create folder if it is not present
    cwd = os.getcwd()
    folder = cwd + str('\\visualisations\\terminal capacity') 
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Save figure
    file = folder + str("\\Capacity vs demand") + str(".png")
    plt.savefig(str(file), bbox_inches="tight")
    
    py.iplot(fig, filename='Terminal capacity')
    
    return


# # Terminal Assets

# ### Determine development trajectory of terminals assets

# In[14]:


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
    
    def line_plot(data, asset):

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
        plt.tick_params(axis="both", which="both", bottom=False, top=False,    
                        labelbottom=True, left=False, right=False, labelleft=True)    

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
        
        # Save figure at designated folder. Create folder if it is not present
        cwd = os.getcwd()
        folder = cwd + str('\\visualisations\\assets') 
        if not os.path.exists(folder):
            os.makedirs(folder)            
        
        # Save figure
        file = folder + str("\\") + str(asset) + str(".png")
        plt.savefig(str(file), bbox_inches="tight") 
        
    quay_plot = line_plot(quays, 'Quay trajectory')
    berths_plot = line_plot(berths, 'Berths trajectory')
    storage_plot = line_plot(storage, 'Storage trajectory')
    stations_plot = line_plot(station, 'Stations trajectory')
    conveyor_plot = line_plot(conveyors, 'Conveyors trajectory')
    
    return

