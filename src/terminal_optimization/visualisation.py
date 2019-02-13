
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
colors = ['rgba(55, 83, 109, 1)', 'rgba(55, 83, 109, 0.8)', 'rgba(55, 83, 109, 0.5)',
          'rgb(129, 180, 179, 1)', 'rgb(79, 127, 127, 1)', 'rgb(110,110,110)']  


# ### Import Plotly packages

# In[7]:


# Log in to Plotly servers
import plotly
#plotly.tools.set_credentials_file(username='wijzermans', api_key='FKGDvSah3z5WCNREBZEq')
#plotly.tools.set_credentials_file(username='wijnandijzermans', api_key='xeDEwwpCK3aLLR4TIrM9')
plotly.tools.set_credentials_file(username='jorisneuman', api_key='zButeTrlr5xVETcyvazd')

import plotly.plotly as py  
import plotly.graph_objs as go
import plotly.tools as tls 
from plotly.graph_objs import *
import plotly.figure_factory as ff
get_ipython().run_line_magic('matplotlib', 'inline')


# # Scenarios

# In[ ]:


def scenario(traffic_projections, commodities):
    
    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]
    
    # Visualize each traffic projections
    data = []
    for i in range(len(traffic_projections)):
        if i == 0:
            data.append(
                go.Scatter(
                    x = maize.years,
                    y = traffic_projections[i],
                    name = 'Traffic projections',
                    line = dict(
                        color = ('rgb(215, 215, 215)'),
                        width = 2)))
        else:
            data.append(
                go.Scatter(
                    x = maize.years,
                    y = traffic_projections[i],
                    name = 'Traffic projections',
                    showlegend = False,
                    line = dict(
                        color = ('rgb(215, 215, 215)'),
                        width = 2)))        
    
    # Calculate the median traffic projection (i.e. traffic scenario)
    traffic_scenario = []
    for i in range (len(maize.historic)):
        traffic_scenario.append(
            maize.historic[i]) 
    for year in range (len(maize.historic), len(maize.years)):
        throughputs = []
        for i in range (len(traffic_projections)):
            throughputs.append(
                traffic_projections[i][year])
        traffic_scenario.append(
            np.median(throughputs))                    
            
    # Visualize median traffic projections
    data.append(
        go.Scatter(
            x = maize.years,
            y = traffic_scenario,
            name = 'Traffic scenario',
            line = dict(
               color = ('rgb(214, 39, 40)'),
                width = 2)))

    # Edit the layout
    layout = dict(
                title = 'Traffic projections',
                yaxis = dict(title = 'Maize throughput (t/year)'),
                legend=dict(
                    x=1.05,
                    y=1),
                annotations=[
                    dict(
                        x=1,
                        y=-0.12,
                        showarrow=False,
                        text='Source: Computer model',
                        xref='paper',
                        yref='paper'),
                    dict(
                        x=2018.7,
                        y=1,
                        showarrow=False,
                        text='Projected traffic',
                        yref='paper',
                        textangle=90,
                        font=dict(
                            size=13)),
                    dict(
                        x=2017.3,
                        y=1,
                        showarrow=False,
                        text='Historic traffic',
                        yref='paper',
                        textangle=90,
                        font=dict(
                            size=13))],
                shapes=[
                    dict(
                        type='line',
                        x0=2018,
                        y0=-0.05,
                        x1=2018,
                        y1=1.05,
                        yref='paper',
                        line=dict(
                            color='rgb(60, 60, 60)',
                            width=3,
                            dash='dashdot'))]
    )
    
    fig = dict(data=data, layout=layout)
    
    return fig


# In[ ]:


def traffic_development(commodities):
        
    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]

    # Visualize traffic projection
    data = []
    data.append(
        go.Scatter(
            x = maize.years,
            y = maize.demand,
            mode='lines',
            name = 'Traffic scenario',
            line = dict(
               color = ('rgb(214, 39, 40)'),
                width = 2,
                shape='hv')))

    # Edit the layout
    layout = dict(
                title = 'Traffic projections',
                yaxis = dict(
                            title='Maize throughput (t/year)',
                            range=[0,1.1*max(maize.demand)]),
                xaxis = dict(
                            range=[2018,2027],
                            dtick=1,
                            tickangle=315),
                legend=dict(
                    x=1.05,
                    y=1),
                annotations=[
                    dict(
                        x=1,
                        y=-0.15,
                        showarrow=False,
                        text='Source: url or QR code',
                        xref='paper',
                        yref='paper')]
                    )

    fig = dict(data=data, layout=layout)

    return fig


# In[ ]:


def forecast_visualization(traffic_scenario, forecast, commodities):
    
    maize = commodities[0]
       
    # Visualize the yearly forecasted traffic projection
    data = []
    data.append(
        go.Scatter(
            x = maize.years,
            y = traffic_scenario,
            name = 'Traffic scenario',
            line = dict(
               color = ('rgb(214, 39, 40)'),
                width = 2)))
    data.append(
        go.Scatter(
            x = maize.years,
            y = forecast,
            name = 'Forecasted volumes',
            line = dict(
               color = 'rgb(215, 215, 215)',
                width = 2)))

    # Edit the layout
    layout = dict(
                title = 'Traffic forecasts',
                yaxis = dict(title = 'Maize throughput (t/year)'),
                legend=dict(
                    x=1.05,
                    y=1),
                annotations=[
                    dict(
                        x=1,
                        y=-0.12,
                        showarrow=False,
                        text='Source: Computer model',
                        xref='paper',
                        yref='paper'),
                    dict(
                        x=2018.7,
                        y=1,
                        showarrow=False,
                        text='Interim forecasts',
                        yref='paper',
                        textangle=90,
                        font=dict(
                            size=13)),
                    dict(
                        x=2017.3,
                        y=1,
                        showarrow=False,
                        text='Historic traffic',
                        yref='paper',
                        textangle=90,
                        font=dict(
                            size=13))],
                shapes=[
                    dict(
                        type='line',
                        x0=2018,
                        y0=-0.05,
                        x1=2018,
                        y1=1.05,
                        yref='paper',
                        line=dict(
                            color='rgb(60, 60, 60)',
                            width=3,
                            dash='dashdot'))]
    )
    
    fig = dict(data=data, layout=layout)
    
    return fig


# In[2]:


def terminal_design(commodities):

    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]

    # Visualize median traffic projections
    data = []
    data.append(
        go.Scatter(
            x = maize.years,
            y = maize.demand,
            name = 'Traffic projection',
            line = dict(
               color = ('rgb(214, 39, 40)'),
                width = 2)))

    # Edit the layout
    layout = dict(
                title = 'Terminal design',
                yaxis = dict(title = 'Maize throughput (t/year)'),
                xaxis = dict(
                            range=[2016,2037],
                            dtick=1,
                            tickangle=315),
                legend=dict(
                    x=1.05,
                    y=1),
                annotations=[
                    dict(
                        x=1,
                        y=-0.2,
                        showarrow=False,
                        text='Arbitrary (simplified) example',
                        xref='paper',
                        yref='paper')],
                shapes=[
                    dict(
                        type='line',
                        x0=2018,
                        y0=0,
                        x1=2018,
                        y1=1.05,
                        yref='paper',
                        line=dict(
                            color='rgb(60, 60, 60)',
                            width=3,
                            dash='dot')),
                    dict(
                        type='line',
                        x0=2019,
                        y0=0,
                        x1=2019,
                        y1=1.05,
                        yref='paper',
                        line=dict(
                            color='rgb(60, 60, 60)',
                            width=3,
                            dash='dot')),
                    dict(
                        type='line',
                        x0=2021,
                        y0=0,
                        x1=2021,
                        y1=1.05,
                        yref='paper',
                        line=dict(
                            color='rgb(60, 60, 60)',
                            width=3,
                            dash='dot')),
                    dict(
                        type='line',
                        x0=2028,
                        y0=0,
                        x1=2028,
                        y1=1.05,
                        yref='paper',
                        line=dict(
                            color='rgb(60, 60, 60)',
                            width=3,
                            dash='dot')),
                    dict(
                        type='line',
                        x0=2032,
                        y0=0,
                        x1=2032,
                        y1=1.05,
                        yref='paper',
                        line=dict(
                            color='rgb(60, 60, 60)',
                            width=3,
                            dash='dot'))]
                    )

    fig = dict(data=data, layout=layout)

    return fig


# In[ ]:


def forecast_methods(traffic_scenario, linear, forecastpoly2, forecastpoly3, forecastpoly4, commodities):
    
    maize = commodities[0]
       
    # Visualize the yearly forecasted traffic projection
    data = []
    data.append(
        go.Scatter(
            x = maize.years,
            y = traffic_scenario,
            name = 'Traffic scenario',
            line = dict(
               color = ('rgb(214, 39, 40)'),
                width = 2)))
    data.append(
        go.Scatter(
            x = maize.years,
            y = linear,
            name = 'Linear forecasts',
            line = dict(
               color = colors[0],
                width = 2)))
    data.append(
        go.Scatter(
            x = maize.years,
            y = forecastpoly2,
            name = '2nd poly forecasts',
            line = dict(
               color = colors[1],
                width = 2)))
    data.append(
        go.Scatter(
            x = maize.years,
            y = forecastpoly3,
            name = '3rd poly forecasts',
            line = dict(
               color = colors[3],
                width = 2)))
    data.append(
        go.Scatter(
            x = maize.years,
            y = forecastpoly4,
            name = '4th poly forecasts',
            line = dict(
               color = colors[4],
                width = 2)))

    # Edit the layout
    layout = dict(
                title = 'Traffic forecasts',
                yaxis = dict(title = 'Maize throughput (t/year)'),
                legend=dict(
                    x=1.05,
                    y=1),
                annotations=[
                    dict(
                        x=1,
                        y=-0.12,
                        showarrow=False,
                        text='Source: Computer model',
                        xref='paper',
                        yref='paper'),
                    dict(
                        x=2018.7,
                        y=1,
                        showarrow=False,
                        text='Interim forecasts',
                        yref='paper',
                        textangle=90,
                        font=dict(
                            size=13)),
                    dict(
                        x=2017.3,
                        y=1,
                        showarrow=False,
                        text='Historic traffic',
                        yref='paper',
                        textangle=90,
                        font=dict(
                            size=13))],
                shapes=[
                    dict(
                        type='line',
                        x0=2018,
                        y0=-0.05,
                        x1=2018,
                        y1=1.05,
                        yref='paper',
                        line=dict(
                            color='rgb(60, 60, 60)',
                            width=3,
                            dash='dashdot'))]
    )
    
    fig = dict(data=data, layout=layout)
    
    return fig


# # Cash Flows
# - Profit / Loss (nominal value)
# - Profit / Loss (present value)
# - Revenues (nominal value)
# - Revenues + Capex + Opex (nominal value)
# - NPV distribution
# - Risk sensitivity

# In[ ]:


def revenue_capex_opex(terminal):

    cashflows = terminal.cashflows

    # Add residual asset value as cashflow in final year
    for i in range(len(cashflows)):
        if i != len(cashflows) - 1:
            cashflows['Residual asset value'].values[i] = 0

    revenues = cashflows['Revenues'] + terminal.cashflows['Residual asset value']
    discounted_revenues = cashflows['Revenues (discounted)'] + terminal.cashflows['Residual asset value'] * terminal.WACC_cashflows.WACC_factor[-1]

    x = cashflows['Year']

    trace1 = {
      'x': x,
      'y': revenues,
      'name': 'Revenues',
      'type': 'bar',
      'marker': dict(color=colors[3])
    };

    trace2 = {
      'x': x,
      'y': cashflows['Capex'],
      'name': 'Capex',
      'type': 'bar',
      'marker': dict(color='rgb(214, 39, 40)')
    };

    trace3 = {
      'x': x,
      'y': cashflows['Opex'],
      'name': 'Opex',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    trace4 = go.Scatter(
                name='Cumulative<br>FCFF',
                x=x,
                y=cashflows['Compounded profit'],
                mode='lines',
                fill='tozeroy',
                fillcolor='rgba(100, 100, 100, 0.3)',
                line=dict(
                    color='rgba(200, 200, 200, 1)', 
                    width=2,
                    shape='spline',
                    dash='dot'))

    trace5 = {
      'x': x,
      'y': discounted_revenues,
      'name': 'Revenues',
      'type': 'bar',
      'marker': dict(color=colors[3])
    };

    trace6 = {
      'x': x,
      'y': cashflows['Capex (discounted)'],
      'name': 'Capex',
      'type': 'bar',
      'marker': dict(color='rgb(214, 39, 40)')
    };

    trace7 = {
      'x': x,
      'y': cashflows['Opex (discounted)'],
      'name': 'Opex',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    trace8 = go.Scatter(
                name='Cumulative<br>FCFF',
                x=x,
                y=cashflows['Compounded profit (discounted)'],
                mode='lines',
                fill='tozeroy',
                fillcolor='rgba(100, 100, 100, 0.3)',
                line=dict(
                    color='rgba(200, 200, 200, 1)', 
                    width=2,
                    shape='spline',
                    dash='dot'))

    data = [trace1, trace2, trace3, trace4];
    layout = {
        'xaxis': {'tickangle': 315,
                  'dtick': 1},
        'yaxis': {'title': 'Cashflows',
                  'tickprefix': '$',
                  'range':[min(cashflows['Compounded profit'])*1.1, max(revenues)*1.1]},
        'title': 'Terminal cashflows',
        'legend': dict(x=1,
                     y=1),
        'bargap': 0.35,
        'bargroupgap' :0.05,
        'annotations' :[dict(
                        x=1,
                        y=-0.18,
                        showarrow=False,
                        text='Source: Computer model',
                        xanchor='right',
                        xref='paper',
                        yref='paper')]
    }

    fig = {'data': data, 'layout': layout}
    
    return fig


# In[ ]:


def discounted_revenue_capex_opex(terminal):

    cashflows = terminal.cashflows

    # Add residual asset value as cashflow in final year
    for i in range(len(cashflows)):
        if i != len(cashflows) - 1:
            cashflows['Residual asset value'].values[i] = 0

    revenues = cashflows['Revenues'] + terminal.cashflows['Residual asset value']
    discounted_revenues = cashflows['Revenues (discounted)'] + terminal.cashflows['Residual asset value'] * terminal.WACC_cashflows.WACC_factor[-1]

    x = cashflows['Year']

    trace1 = {
      'x': x,
      'y': revenues,
      'name': 'Revenues',
      'type': 'bar',
      'marker': dict(color=colors[3])
    };

    trace2 = {
      'x': x,
      'y': cashflows['Capex'],
      'name': 'Capex',
      'type': 'bar',
      'marker': dict(color='rgb(214, 39, 40)')
    };

    trace3 = {
      'x': x,
      'y': cashflows['Opex'],
      'name': 'Opex',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    trace4 = go.Scatter(
                name='Profit/Loss',
                x=x,
                y=cashflows['Compounded profit'],
                mode='lines',
                fill='tozeroy',
                fillcolor='rgba(100, 100, 100, 0.3)',
                line=dict(
                    color='rgba(200, 200, 200, 1)', 
                    width=2,
                    shape='spline',
                    dash='dot'))

    trace5 = {
      'x': x,
      'y': discounted_revenues,
      'name': 'Revenues',
      'type': 'bar',
      'marker': dict(color=colors[3])
    };

    trace6 = {
      'x': x,
      'y': cashflows['Capex (discounted)'],
      'name': 'Capex',
      'type': 'bar',
      'marker': dict(color='rgb(214, 39, 40)')
    };

    trace7 = {
      'x': x,
      'y': cashflows['Opex (discounted)'],
      'name': 'Opex',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    trace8 = go.Scatter(
                name='Profit/Loss',
                x=x,
                y=cashflows['Compounded profit (discounted)'],
                mode='lines',
                fill='tozeroy',
                fillcolor='rgba(100, 100, 100, 0.3)',
                line=dict(
                    color='rgba(200, 200, 200, 1)', 
                    width=2,
                    shape='spline',
                    dash='dot'))

    data = [trace4, trace5, trace6, trace7];
    layout = {
        'xaxis': {'tickangle': 315,
                  'dtick': 1},
        'yaxis': {'title': 'Cashflows',
                  'tickprefix': '$',
                  'range':[min(cashflows['Compounded profit'])*1.1, max(revenues)*1.1]},
        'title': 'Terminal cashflows',
        'legend': dict(x=1,
                     y=1),
        'bargap': 0.35,
        'bargroupgap' :0.05,
        'annotations' :[dict(
                        x=1,
                        y=-0.18,
                        showarrow=False,
                        text='Source: Computer model',
                        xanchor='right',
                        xref='paper',
                        yref='paper'),
                       dict(
                        x=1,
                        y=terminal.NPV*1.2,
                        showarrow=False,
                        text= 'NPV: $' + str('{:0,.0f}'.format(terminal.NPV)),
                        xanchor='right',
                        xref='paper')]
    }

    fig = {'data': data, 'layout': layout}
    
    return fig


# ### NPV distribution

# In[ ]:


from IPython.display import display, HTML


# In[ ]:


def NPV_distribution_WACC(iterations):

    NPV_matrix = np.zeros(shape=(len(iterations), 3))

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(iterations)):

        terminal = iterations[i]
        NPV = terminal.NPV
        WACC = terminal.project_WACC

        # Iteration (Column 0)
        iteration = i 
        NPV_matrix[i,0] = iteration
        # NPV (Column 1)
        NPV_matrix[i,1] = NPV
        # Allowable waiting factor
        NPV_matrix[i,2] = WACC * 100

    df = pd.DataFrame(NPV_matrix, columns=['Iteration', 'NPV', 'WACC'])
    
    x = df['WACC']
    y = df['NPV']

    trace1 = {
      'x': x,
      'y': y,
      'name': 'Iterations',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    data = [trace1];
    layout = dict(
                xaxis= dict(
                    title='Weighted average cost of capital (WACC)',
                    ticksuffix='%'
                ),
                yaxis= dict(
                    title='Terminal NPV',
                    tickprefix='$'
                ),
                title= 'Financial impact of the weighted average<br>cost of capital',
                showlegend=False,
                annotations=[dict(
                                x=1,
                                y=-0.13,
                                showarrow=False,
                                text='Source: Computer model',
                                xanchor='right',
                                xref='paper',
                                yref='paper')]
    )

    return [data, layout]


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

# In[ ]:


def capacity(terminal, commodities):

    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]

    terminal_capacity = []
    quay_capacity = []
    storage_capacity = []
    station_capacity = []
        
    df = terminal.berths[0].info   
    for x in df['Year'].values:
        
        # Quay
        df = terminal.berths[0].info 
        quay_capacity.append(int(round(df.loc[df['Year'] == x]['Capacity'])))  
        
        # Storage
        df = terminal.storage[0][0].info
        if df['Year'].values[0] > x:
            storage_capacity.append(0)
        else:
            storage_capacity.append(int(round(df.loc[df['Year'] == x]['Capacity'])))
            
        # Stations
        df = terminal.stations[0].info
        if df['Year'].values[0] > x:
            station_capacity.append(0)
        else:
            station_capacity.append(int(round(df.loc[df['Year'] == x]['Total yearly loading capacity'])))
            
        terminal_capacity.append(int(round(min(quay_capacity[-1],storage_capacity[-1],station_capacity[-1]))))
            
    x = maize.years[len(commodities[0].historic):]
    demand = maize.demand[len(commodities[0].historic):]

    trace1 = go.Scatter(
        name='Terminal capacity',
        x=x,
        y=terminal_capacity,
        mode='lines',
        line=dict(
            color='rgba(60, 60, 60, 1)', 
            width=3,
            shape='hv',
            dash='dot'),
    )

    trace2 = {
      'x': x,
      'y': quay_capacity,
      'name': 'Quay capacity',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    trace3 = {
      'x': x,
      'y': storage_capacity,
      'name': 'Storage capacity',
      'type': 'bar',
      'marker': dict(color='rgba(170, 170, 170, 0.6)')
    };

    trace4 = {
      'x': x,
      'y': station_capacity,
      'name': 'Train loading capacity',
      'type': 'bar',
      'marker': dict(color=colors[3])
    };
    
    trace5 = go.Scatter(
        name='Traffic projection',
        x=x,
        y=demand,
        mode='lines',
        line=dict(
            color='rgb(214, 39, 40)', 
            width=2
        )
    )

    data = [trace1, trace2, trace3, trace4, trace5];
    layout = {
        'xaxis': dict(
                tick0=0,
                dtick=1,
                tickangle=315),
        'yaxis': {'title': 'Terminal throughput (t/year)'},
        'yaxis2':dict(
                    title='Traffic projection (t/year)',
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    ),
        'title': 'Terminal capacity over the years',
        'legend': dict(x=1,
                     y=1),
        'bargap': 0.15,
        'bargroupgap' :0.1,
        'annotations' :[dict(
                        x=1,
                        y=-0.18,
                        showarrow=False,
                        text='Source: Computer model',
                        xanchor='right',
                        xref='paper',
                        yref='paper')]
    }
    fig = {'data': data, 'layout': layout}
    
    return fig


# # Trigger Iteration

# ### Vessel waiting times

# In[ ]:


def NPV_distribution_vessel_waiting_times(iterations):

    NPV_matrix = np.zeros(shape=(len(iterations), 3))

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(iterations)):

        terminal = iterations[i]
        NPV = terminal.NPV
        allowable_waiting_time = terminal.allowable_vessel_waiting_time

        # Iteration (Column 0)
        iteration = i 
        NPV_matrix[i,0] = iteration
        # NPV (Column 1)
        NPV_matrix[i,1] = NPV
        # Allowable waiting factor
        NPV_matrix[i,2] = allowable_waiting_time * 100

    df = pd.DataFrame(NPV_matrix, columns=['Iteration', 'NPV', 'Allowable waiting factor'])
    
    x = df['Allowable waiting factor']
    y = df['NPV']

    trace1 = {
      'x': x,
      'y': y,
      'name': 'Iterations',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    data = [trace1];
    layout = dict(
                xaxis= dict(
                    title='Allowable waiting time as factor of service time',
                    ticksuffix='%',
                    range = [9, 145]
                ),
                yaxis= dict(
                    title='Terminal NPV',
                    tickprefix='$'
                ),
                title= 'Financial impact of the allowable<br>vessel waiting time',
                showlegend=False,
                annotations=[dict(
                                x=1,
                                y=-0.13,
                                showarrow=False,
                                text='Source: Computer model',
                                xanchor='right',
                                xref='paper',
                                yref='paper')]
    )

    return [data, layout]


# ### Required storage factor

# In[ ]:


def NPV_distribution_required_storage(iterations):

    NPV_matrix = np.zeros(shape=(len(iterations), 3))

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(iterations)):

        terminal = iterations[i]
        NPV = terminal.NPV
        required_storage_factor = terminal.required_storage_factor

        # Iteration (Column 0)
        iteration = i 
        NPV_matrix[i,0] = iteration
        # NPV (Column 1)
        NPV_matrix[i,1] = NPV
        # Allowable waiting factor
        NPV_matrix[i,2] = required_storage_factor * 100

    df = pd.DataFrame(NPV_matrix, columns=['Iteration', 'NPV', 'Required storage factor'])
    
    x = df['Required storage factor']
    y = df['NPV']

    trace1 = {
      'x': x,
      'y': y,
      'name': 'Iterations',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    data = [trace1];
    layout = dict(
                xaxis= dict(
                    title='Percentage of annual throughput',
                    ticksuffix='%'
                ),
                yaxis= dict(
                    title='Terminal NPV',
                    tickprefix='$'
                ),
                title= 'Minimum percentage of annual throughput required as storage volume',
                showlegend=False,
                annotations=[dict(
                                x=1,
                                y=-0.13,
                                showarrow=False,
                                text='Source: Computer model',
                                xanchor='right',
                                xref='paper',
                                yref='paper')]
    )
    return [data, layout]


# ### Aspired storage factor

# In[ ]:


def NPV_distribution_dwell_times(iterations):

    NPV_matrix = np.zeros(shape=(len(iterations), 3))

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(iterations)):

        terminal = iterations[i]
        NPV = terminal.NPV
        dwell_time = terminal.dwell_time

        # Iteration (Column 0)
        iteration = i 
        NPV_matrix[i,0] = iteration
        # NPV (Column 1)
        NPV_matrix[i,1] = NPV
        # Allowable waiting factor
        NPV_matrix[i,2] = dwell_time

    df = pd.DataFrame(NPV_matrix, columns=['Iteration', 'NPV', 'Dwell time'])
    
    x = df['Dwell time']
    y = df['NPV']

    trace1 = {
      'x': x,
      'y': y,
      'name': 'Iterations',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    data = [trace1];
    layout = dict(
                xaxis= dict(
                    title='Dwell time',
                    ticksuffix=' days'
                ),
                yaxis= dict(
                    title='Terminal NPV',
                    tickprefix='$'
                ),
                title= 'The financial impact of commodity dwell times',
                showlegend=False,
                annotations=[dict(
                                x=1,
                                y=-0.13,
                                showarrow=False,
                                text='Source: Computer model',
                                xanchor='right',
                                xref='paper',
                                yref='paper')]
    ) 
    return [data, layout]


# ### Allowable train waiting times 

# In[ ]:


def NPV_distribution_train_waiting_times(iterations):

    NPV_matrix = np.zeros(shape=(len(iterations), 3))

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(iterations)):

        terminal = iterations[i]
        NPV = terminal.NPV
        allowable_train_waiting_time = terminal.allowable_train_waiting_time

        # Iteration (Column 0)
        iteration = i 
        NPV_matrix[i,0] = iteration
        # NPV (Column 1)
        NPV_matrix[i,1] = NPV
        # Allowable waiting factor
        NPV_matrix[i,2] = allowable_train_waiting_time * 100

    df = pd.DataFrame(NPV_matrix, columns=['Iteration', 'NPV', 'Allowable train waiting times'])
    
    x = df['Allowable train waiting times']
    y = df['NPV']

    trace1 = {
      'x': x,
      'y': y,
      'name': 'Iterations',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    data = [trace1];
    layout = dict(
                xaxis= dict(
                    title='Waiting time as factor of service time',
                    ticksuffix='%'
                ),
                yaxis= dict(
                    title='Terminal NPV',
                    tickprefix='$'
                ),
                title= 'Financial impact of the allowable<br>train waiting time',
                showlegend=False,
                annotations=[dict(
                                x=1,
                                y=-0.13,
                                showarrow=False,
                                text='Source: Computer model',
                                xanchor='right',
                                xref='paper',
                                yref='paper')]
    ) 
    return [data, layout]


# # Terminal Assets

# ### Berths and cranes 

# In[ ]:


def berth_cranes(terminal, commodities):

    colors = ['rgba(55, 83, 109, 1)', 'rgba(55, 83, 109, 0.8)', 'rgba(55, 83, 109, 0.5)',
          'rgb(129, 180, 179, 1)', 'rgb(79, 127, 127, 1)', 'rgb(110,110,110)']  

    maize   = commodities[0]
    soybean = commodities[1]
    wheat   = commodities[2]

    x  = maize.years[5:]
    demand = maize.demand[5:]
    n_berths, n_cranes = [], []

    for year in x:

        # Number of berths online
        online = []
        for i in range(len(terminal.berths)):
            if year >= terminal.berths[i].online_date:
                online.append(1)
        n_berths.append(np.sum(online))

        # Number of cranes online
        online = []
        for i in range(4):
            for j in range(len(terminal.cranes[i])):
                if year >= terminal.cranes[i][j].online_date:
                    online.append(1)
        n_cranes.append(np.sum(online))

    trace1 = {
      'x': x,
      'y': n_berths,
      'name': 'Berths',
      'type': 'bar',
      'marker': dict(color=colors[0])
    };

    trace2 = {
      'x': x,
      'y': n_cranes,
      'name': 'Mobile cranes',
      'type': 'bar',
      'marker': dict(color='rgba(170, 170, 170, 0.6)')
    };

    trace3 = go.Scatter(
        name='Traffic projection',
        x=x,
        y=demand,
        yaxis='y2',
        mode='lines',
        line=dict(
            color='rgb(214, 39, 40)', 
            width=2
        )
    )

    data = [trace1, trace2, trace3];
    layout = {
        'xaxis': dict(
                tick0=0,
                dtick=1,
                tickangle=315),
        'yaxis': dict(
                    title='Number of assets',
                    dtick=1),
        'yaxis2':dict(
                    title='Traffic projection (t/year)',
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    ),
        'title': 'Berth configuration over the years',
        'annotations': [dict(
                            x=1,
                            y=-0.15,
                            showarrow=False,
                            text='Source: Computer model',
                            xref='paper',
                            yref='paper'
                            )],
        'legend': dict(x=1.1,
                     y=1),
        'bargap': 0.18,
        'bargroupgap' :0.1,
        };
    
    fig = dict(data=data, layout=layout)
    
    return fig


# # Estimate project value

# In[ ]:


def NPV_distribution_estimated_designs(iterations):

    NPV_matrix = np.zeros(shape=(len(iterations), 2))

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(iterations)):

        # Iteration # (Column 0)
        NPV_matrix[i,0] = i
        # NPV (Column 1)
        NPV_matrix[i,1] = iterations[i].NPV

    df = pd.DataFrame(NPV_matrix, columns=['Iteration', 'NPV'])
    
    # Add histogram data
    hist_data = [df['NPV']]
    group_labels = ['Terminal designs based on<br>ex-ante traffic projections']
    
    NPV_estimation = np.average(df['NPV'])
    estimated_NPV = "$" + str('{:0,.0f}'.format(np.average(df['NPV'])))
    standard_deviation = np.std(df['NPV'])
    min_x = NPV_estimation - 4*standard_deviation
    max_x = NPV_estimation + 4*standard_deviation

    # Create distplot with curve_type set to 'normal'
    fig = ff.create_distplot(hist_data, group_labels, show_hist=False, colors=['rgb(214, 39, 40)'])

    fig['layout'].update(
        xaxis=dict(
            title='Project NPV',
            tickprefix='$',
            range=[min_x, max_x]
        ),
        yaxis=dict(
            title='Probability distribution (%)',
            autorange=True,
            showgrid=True,
            zeroline=True,
            showline=True,
            ticks='',
            showticklabels=False
        ),
        legend=dict(
                x=0.78,
                y=1),
        annotations=[
            dict(
                x=0.5,
                y=1.25,
                showarrow=False,
                text='Estimating project value',
                xref='paper',
                yref='paper',
                font=dict(
                    size=16)
            ),
            dict(
                x=np.average(df['NPV']),
                y=0.55,
                showarrow=False,
                text='Estimated project value:<br>' + str("$" + str('{:0,.0f}'.format(np.average(df['NPV'])))),
                yref='paper',
                font=dict(
                    size=13)
            ),
            dict(
                x=1,
                y=-0.12,
                showarrow=False,
                text='Source: Computer model',
                xref='paper',
                yref='paper'
            )],
        shapes=[dict(type='line',
                     x0=np.average(df['NPV']),
                     y0=0.36,
                     x1=np.average(df['NPV']),
                     y1=0.48,
                     yref='paper',
                     line=dict(
                         color='rgb(214, 39, 40)',
                         width=2,
                         dash='dot')),
                dict(type='line',
                     x0=np.average(df['NPV']),
                     y0=0.62,
                     x1=np.average(df['NPV']),
                     y1=1,
                     yref='paper',
                     line=dict(
                         color='rgb(214, 39, 40)',
                         width=2,
                         dash='dot'))]
    )

    return fig


# In[ ]:


def NPV_distribution_single_design(terminal):
    
    NPV = terminal.NPV

    trace1 = {
      'x': [NPV],
      'y': [0],
      'name': 'Berths',
      'visible': False,
      'type': 'bar',
      'marker': dict(color='rgb(0,0,0)')
    };

    data = [trace1]

    layout = {
    'xaxis': dict(
                range=[0.70*NPV, 1.30*NPV],
                title='Project NPV',
                tickprefix='$'),
    'yaxis': dict(
                title='',
                showticklabels=False,
                zeroline=True,
                range = [0,4],
                dtick=1),
    'title': 'Project value estimation',
    'annotations': [dict(
                        x=1,
                        y=-0.15,
                        showarrow=False,
                        text='Source: Computer model',
                        xref='paper',
                        yref='paper'
                        ),
                    dict(
                        x=NPV,
                        y=0.53,
                        showarrow=False,
                        text='Estimated project value:<br>' + str("$" + str('{:0,.0f}'.format(NPV))),
                        yref='paper',
                        font=dict(
                            size=13,
                            color='rgb(214, 39, 40)')
                        )],
    'shapes': [dict(
                    type='line',
                    x0=0.70*NPV,
                    y0=0,
                    x1=0.70*NPV,
                    y1=1,
                    yref='paper',
                    line=dict(
                        color='rgb(60, 60, 60)',
                        width=2)),
               dict(
                    type='line',
                    x0=NPV,
                    y0=0,
                    x1=NPV,
                    y1=0.45,
                    yref='paper',
                    line=dict(
                        color='rgb(214, 39, 40)',
                        width=2,
                        dash='dot')),
                dict(
                    type='line',
                    x0=NPV,
                    y0=0.60,
                    x1=NPV,
                    y1=1.05,
                    yref='paper',
                    line=dict(
                        color='rgb(214, 39, 40)',
                        width=2,
                        dash='dot'))],
    'showlegend': False,
    'bargap': 0.18,
    'bargroupgap' :0.1
    };

    fig = dict(data=data, layout=layout)

    return fig


# # Simulate project value

# In[ ]:


def NPV_distribution_simulated_designs(iterations):

    NPV_matrix = np.zeros(shape=(len(iterations), 2))

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(iterations)):

        # Iteration # (Column 0)
        NPV_matrix[i,0] = i
        # NPV (Column 1)
        NPV_matrix[i,1] = iterations[i].NPV

    df = pd.DataFrame(NPV_matrix, columns=['Iteration', 'NPV'])
    
    # Add histogram data
    hist_data = [df['NPV']]
    group_labels = ['Terminal designs based on<br>ex-post traffic simulations']
    
    standard_deviation = np.std(df['NPV'])
    min_x = np.average(df['NPV']) - 4*standard_deviation
    max_x = np.average(df['NPV']) + 4*standard_deviation

    # Create distplot with curve_type set to 'normal'
    fig = ff.create_distplot(hist_data, group_labels, show_hist=False, colors=['rgba(55, 83, 109, 1)'])

    fig['layout'].update(
        xaxis=dict(
            title='Project NPV',
            tickprefix='$',
            range=[min_x, max_x]
        ),
        yaxis=dict(
            title='Probability distribution (%)',
            autorange=True,
            showgrid=True,
            zeroline=True,
            showline=True,
            ticks='',
            showticklabels=False
        ),
        legend=dict(
                x=0.78,
                y=1),
        annotations=[
            dict(
                x=0.5,
                y=1.25,
                showarrow=False,
                text='Simulated project value',
                xref='paper',
                yref='paper',
                font=dict(
                    size=16)
            ),
            dict(
                x=np.average(df['NPV']),
                y=0.55,
                showarrow=False,
                text='Average project value<br> after simulations:<br>' + str("$" + str('{:0,.0f}'.format(np.average(df['NPV'])))),
                yref='paper',
                font=dict(
                    size=13)
            ),
            dict(
                x=1,
                y=-0.12,
                showarrow=False,
                text='Source: Computer model',
                xref='paper',
                yref='paper'
            )],
        shapes=[dict(type='line',
                     x0=np.average(df['NPV']),
                     y0=0.36,
                     x1=np.average(df['NPV']),
                     y1=0.45,
                     yref='paper',
                     line=dict(
                         color='rgba(55, 83, 109, 1)',
                         width=2,
                         dash='dot')),
                dict(type='line',
                     x0=np.average(df['NPV']),
                     y0=0.65,
                     x1=np.average(df['NPV']),
                     y1=1,
                     yref='paper',
                     line=dict(
                         color='rgba(55, 83, 109, 1)',
                         width=2,
                         dash='dot'))]
    )

    return fig


# # Assessing the design method

# In[ ]:


def method_evaluation(chosen_method, estimate_designs, evaluate_designs):

    NPV_matrix = np.zeros(shape=(len(evaluate_designs), 3))

    if chosen_method == 'Perfect foresight method':
        title = 'Evaluation of the established common practice'
    if chosen_method == 'Current performance method':
        title = 'Evaluation of the current performance method'
    if chosen_method == 'Forecast based method':
        title = 'Evaluation of the interim forecast method'

    ############################################################################################################
    # For each run, register the terminal's NPV 
    ############################################################################################################

    for i in range (len(evaluate_designs)):

        simulation_NPV = evaluate_designs[i].NPV
        if chosen_method == 'Perfect foresight method':
            estimate_NPV = estimate_designs[0].NPV
        else:
            estimate_NPV = estimate_designs[i].NPV

        # Iteration (Column 0)
        iteration = i 
        NPV_matrix[i,0] = iteration
        # Simulations (Column 1)
        NPV_matrix[i,1] = simulation_NPV
        # Estimates (Column 2)
        NPV_matrix[i,2] = estimate_NPV

    df = pd.DataFrame(NPV_matrix, columns=['Iteration', 'Simulations', 'Estimations'])

    if chosen_method == 'Perfect foresight method':
        # Add histogram data
        hist_data    = [df['Simulations']]
        group_labels = ['Terminal designs based on<br>ex-post traffic simulations']

    else:
        # Add histogram data
        hist_data = [df['Simulations'], df['Estimations']]
        group_labels = ['Terminal designs based on<br>ex-post traffic simulations',
                        'Terminal designs based on<br>ex-ante traffic projections']

    simulation_NPV = int(np.average(df['Simulations']))
    estimate_NPV   = int(np.average(df['Estimations']))
    NPV_difference = "$" + str('{:0,.0f}'.format(abs(simulation_NPV - estimate_NPV)))
    midway = 0.5 * abs(simulation_NPV - estimate_NPV) + min(simulation_NPV, estimate_NPV)

    standard_deviation = max(np.std(df['Simulations']), np.std(df['Estimations']))
    min_x = min(simulation_NPV, estimate_NPV) - 4*standard_deviation
    max_x = max(simulation_NPV, estimate_NPV) + 4*standard_deviation

    if simulation_NPV > estimate_NPV:
        anchor_estimation = 'right'
        anchor_simulation = 'left'
    else:
        anchor_estimation = 'left'
        anchor_simulation = 'right'

    # Create distplot with curve_type set to 'normal'
    fig = ff.create_distplot(hist_data, group_labels, show_hist=False, colors=['rgba(55, 83, 109, 1)', 'rgb(214, 39, 40)'])

    fig['layout'].update(
        xaxis=dict(
            title='Project NPV',
            tickprefix='$',
            range=[min_x, max_x]
        ),
        yaxis=dict(
            title='Probability distribution (%)',
            autorange=True,
            showgrid=True,
            zeroline=True,
            showline=True,
            ticks='',
            showticklabels=False
        ),
        legend=dict(
                x=0.78,
                y=1),
        annotations=[
            dict(
                x=midway,
                y=0.73,
                showarrow=False,
                text=u'Δ ' + 'NPV: ' + str(round(100*abs(simulation_NPV - estimate_NPV)/midway,1)) + '%',
                yref='paper',
                font=dict(
                    size=13)
            ),
            dict(
                x=np.average(df['Simulations']),
                y=0.56,
                showarrow=False,
                text='Average simulated value<br>'+ "$" + str('{:0,.0f}'.format(abs(simulation_NPV))),
                xanchor = anchor_simulation,
                yref='paper',
                font=dict(
                    size=11,
                    color='rgba(55, 83, 109, 1)')
            ),
            dict(
                x=np.average(df['Estimations']),
                y=0.49,
                showarrow=False,
                text='Estimated value<br>'+ "$" + str('{:0,.0f}'.format(abs(estimate_NPV))),
                xanchor = anchor_estimation,
                yref='paper',
                font=dict(
                    size=11,
                    color='rgb(214, 39, 40)')
            ),
            dict(
                x=1,
                y=-0.12,
                showarrow=False,
                text='Source: Computer model',
                xref='paper',
                yref='paper'
            )],
        shapes=[dict(type='line',
                     x0=np.average(df['Simulations']),
                     y0=0.36,
                     x1=np.average(df['Simulations']),
                     y1=0.65,
                     yref='paper',
                     line=dict(
                         color='rgba(55, 83, 109, 1)',
                         width=2,
                         dash='dot')
                    ),
                dict(type='line',
                     x0=np.average(df['Simulations']),
                     y0=0.75,
                     x1=np.average(df['Simulations']),
                     y1=1,
                     yref='paper',
                     line=dict(
                         color='rgba(55, 83, 109, 1)',
                         width=2,
                         dash='dot')
                    ),
                dict(type='line',
                     x0=np.average(df['Estimations']),
                     y0=0.36,
                     x1=np.average(df['Estimations']),
                     y1=0.65,
                     yref='paper',
                     line=dict(
                         color='rgb(214, 39, 40)',
                         width=2,
                         dash='dot')
                    ),
                dict(type='line',
                     x0=np.average(df['Estimations']),
                     y0=0.74,
                     x1=np.average(df['Estimations']),
                     y1=1,
                     yref='paper',
                     line=dict(
                         color='rgb(214, 39, 40)',
                         width=2,
                         dash='dot')
                    )]
    )

    return fig

