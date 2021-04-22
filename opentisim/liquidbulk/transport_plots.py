
# coding: utf-8

# In[ ]:


import numpy as np
import numpy.matlib as npml
import pandas as pd
import statistics as st
from copy import deepcopy

import networkx as nx
import simpy

import matplotlib.pyplot as plt
from simplekml import Kml, Style   # for graph_kml
import math

import shapely.geometry
import pyproj

import pandas as pd
from opentisim.liquidbulk.hydrogen_defaults import *
from opentisim.liquidbulk.hydrogen_objects import *
import opentisim


# In[ ]:


def cashflow_data(terminal, element):  #(Terminal, element):
    """Place cashflow data in element dataframe
    Elements that take two years to build are assign 60% to year one and 40% to year two."""

    # years
    years = terminal.modelframe
    #years = list(range(Terminal.startyear, Terminal.startyear + Terminal.lifecycle))
    
    # capex
    capex = element.capex
    #capex_material = element.capex_material

    # opex
    maintenance = element.maintenance
    insurance = element.insurance
    labour = element.labour
    fuel = element.fuel
    #purchaseH2 = element.purchaseH2
    #purchase_material = element.purchase_material     

    # year online
    year_online = element.year_online
    year_delivery = element.delivery_time

    df = pd.DataFrame()

    # years
    df["year"] = years

    # capex
    if year_delivery > 1:
        df.loc[df["year"] == year_online - 2, "capex"] = 0.6 * capex
        df.loc[df["year"] == year_online - 1, "capex"] = 0.4 * capex
    else:
        df.loc[df["year"] == year_online - 1, "capex"] = capex
    
    #if capex_material:
        #df.loc[df["year"] == year_online, "capex_material"] = capex_material

    # opex
    if maintenance:
        df.loc[df["year"] >= year_online, "maintenance"] = maintenance
    if insurance:
        df.loc[df["year"] >= year_online, "insurance"] = insurance
    if labour:
        df.loc[df["year"] >= year_online, "labour"] = labour
    if fuel:
        df.loc[df["year"] >= year_online, "fuel"] = fuel
    
#     if insurance:
#         df.loc[df["year"] >= year_online, "purchaseH2"] = purchaseH2
#     if labour:
#         df.loc[df["year"] >= year_online, "purchase_material"] =  purchase_material 

    df.fillna(0, inplace=True)

    element.df = df

    return element


# In[ ]:


def vessel_objects(terminal, dataframe_vessel, vessel_defaults,durationdays,numberoftrips):
        
    list_year = dataframe_vessel['year'].tolist()
    list_vessels = dataframe_vessel['vessel count'].tolist()
    
    new_array = np.zeros(len(list_vessels))
    for i in range(len(list_vessels)):
        new_array[i] = list_vessels[i]-list_vessels[i-1]
    
    new_array[0] = list_vessels[1]
    #print(new_array)
    
    seaborne_transport = []
    for year_index, vessels_year in enumerate(new_array):
        new = int(vessels_year)
        if vessels_year != 0:
            for i in range(new):
                #print(years[year_index])
                #print('** Add vessel to elements')
                vessel = Vessel(**vessel_defaults)

                # - capex
                vessel.capex = vessel.unit_rate + vessel.mobilisation_min

                # - opex
                vessel.insurance = vessel.unit_rate * vessel.insurance_perc
                vessel.maintenance = vessel.unit_rate * vessel.maintenance_perc

                #   labour**hydrogen_defaults
                labour = Labour(**labour_data)
                vessel.shift = (
                            (vessel.crew_for5 * vessel.utilization) / (labour.shift_length * labour.annual_shifts))
                vessel.labour = vessel.shift * labour.operational_salary
                vessel.year_online = list_year[year_index]

                #Add fuel  
                displacement = vessel.call_size + vessel.ship_weight + (1-vessel.gamma)*vessel.DWT
                avspeedknots = vessel.avspeed * 0.54
                fuelconsumption_load = (1/120000)*(displacement)**(2/3)*(avspeedknots)**(3)
                fuelconsumption_unload = (1/120000)*(vessel.ship_weight + vessel.call_size)**(2/3)*(avspeedknots)**(3)

#                 average_fuelconsumption = (fuelconsumption_load + fuelconsumption_unload)/2 #t/d 
#                 fuelcon_trip = (durationdays*2)*average_fuelconsumption
#                 tripsperyear = numberoftrips
#                 fuelcon_year = tripsperyear * fuelcon_trip #ton 
#                 fuelcost_year = fuelcon_year * vessel.fuelprice #€/ton --> € 
            
                for commodity in opentisim.core.find_elements(terminal, Commodity):
                    if commodity.type == 'MCH': 
                        average_fuelconsumption = fuelconsumption_load
                        fuelcon_trip = (durationdays*2)*average_fuelconsumption
                        tripsperyear = numberoftrips
                        fuelcon_year = tripsperyear * fuelcon_trip #ton 
                        fuelcost_year = fuelcon_year * vessel.fuelprice #€/ton --> € 
                        #loaded and unloaded is the same 
                    elif commodity.type == 'Liquid hydrogen':
                        average_fuelconsumption = fuelconsumption_unload 
                        fuelcon_trip = (durationdays)*average_fuelconsumption
                        tripsperyear = numberoftrips
                        fuelcon_year = tripsperyear * fuelcon_trip #ton 
                        fuelcost_year = fuelcon_year * vessel.fuelprice #€/ton --> €  
                        #unloaded back on diesel/hydrogen?  
                    else:
                        average_fuelconsumption = fuelconsumption_unload 
                        fuelcon_trip = (durationdays)*average_fuelconsumption
                        tripsperyear = numberoftrips
                        fuelcon_year = tripsperyear * fuelcon_trip #ton 
                        fuelcost_year = fuelcon_year * vessel.fuelprice #€/ton --> €  
                        #unloaded back on diesel/hydrogen?
                
                vessel.fuel = fuelcost_year
                #add cashflow to vessel 
                vessel = cashflow_data(terminal, vessel)
                #vessel = opentisim.core.add_cashflow_data_to_element(self, jetty)

                seaborne_transport.append(vessel)
    return seaborne_transport


def inland_objects(terminal, dataframe_vessel, transport_defaults, durationdays, numberoftrips,distancekm):
    list_year = dataframe_vessel['year'].tolist()
    list_vessels = dataframe_vessel['vessel count'].tolist()
    #print(list_year)
    #print(list_vessels)
    
    new_array = np.zeros(len(list_vessels))
    for i in range(len(list_vessels)):
        new_array[i] = list_vessels[i]-list_vessels[i-1]
    
    new_array[0] = list_vessels[1]
    #print(new_array)
    
    inland_transport = []
    for year_index, vessels_year in enumerate(new_array):
        new = int(vessels_year)
        if vessels_year != 0:
            for i in range(new):
                if terminal.transport_sc2 == 'barge':
                    #print('** Add vessel to elements')
                    transport = Barge(**transport_defaults)

                    # - capex
                    transport.capex = transport.unit_rate + transport.mobilisation_min

                    # - opex
                    transport.insurance = transport.unit_rate * transport.insurance_perc
                    transport.maintenance =transport.unit_rate * transport.maintenance_perc

                    #   labour**hydrogen_defaults
                    labour = Labour(**labour_data)
                    transport.shift = (
                                (transport.crew_for5 * transport.utilization) / (labour.shift_length * labour.annual_shifts))
                    transport.labour = transport.shift * labour.operational_salary
                    transport.year_online = list_year[year_index]

                    #Add fuel 
                    commodity = Commodity(**terminal.commodity_type_defaults)
                    capacity = transport.call_size
                    fuelprice = transport.fuelprice
                    hycontent = commodity.Hcontent

                    weightship = transport.ship_weight 
                    weightload = transport.call_size + weightship 
                    weightunload = weightship 

                    hoursperyear = transport.utilization #h/y 
                    avspeed = transport.avspeed #km/h
                    capacity = transport.call_size
                    consumption = transport.consumption
                    loadingtime = transport.loadingtime #h 
                    unloadingtime = transport.unloadingtime #h

                    distance = distancekm 
                    tripsperyear = numberoftrips
                    traveldist = numberoftrips*distancekm

                    fuelusageload = weightload/consumption #L/km
                    fuelusageunload = weightunload/consumption #L/km

                    for commodity in opentisim.core.find_elements(terminal, Commodity):
                        if commodity.type == 'MCH': 
                            literperyear = fuelusageload * (traveldist * 2)
                        elif commodity.type == 'Liquid hydrogen':
                            literperyear = fuelusageunload*traveldist
                        else:
                            literload = fuelusageload * traveldist
                            literunload = fuelusageunload*traveldist
                            literperyear = literload + literunload 

                    transport.fuel = literperyear * fuelprice

                    #add cashflow to vessel 
                    transport = cashflow_data(terminal, transport)
                    #vessel = opentisim.core.add_cashflow_data_to_element(self, jetty)

                    inland_transport.append(transport)
                
                if terminal.transport_sc2 == 'train':
                    #print('** Add vessel to elements')
                    transport = Train(**transport_defaults)

                    # - capex
                    transport.capex = transport.unit_rate + transport.mobilisation_min

                    # - opex
                    transport.insurance = transport.unit_rate * transport.insurance_perc
                    transport.maintenance =transport.unit_rate * transport.maintenance_perc

                    #   labour**hydrogen_defaults
                    labour = Labour(**labour_data)
                    transport.shift = (
                                (transport.crew_for5 * transport.utilization) / (labour.shift_length * labour.annual_shifts))
                    transport.labour = transport.shift * labour.operational_salary
                    transport.year_online = list_year[year_index]

                    #Add fuel 
                    commodity = Commodity(**terminal.commodity_type_defaults)
                    capacity = transport.call_size
                    fuelprice = transport.fuelprice
                    hycontent = commodity.Hcontent

                    weightship = transport.train_weight 
                    weightload = transport.call_size + weightship 
                    weightunload = weightship 

                    hoursperyear = transport.utilization #h/y 
                    avspeed = transport.avspeed #km/h
                    capacity = transport.call_size
                    consumption = transport.consumption
                    loadingtime = transport.loadingtime #h 
                    unloadingtime = transport.unloadingtime #h

                    distance = distancekm 
                    tripsperyear = numberoftrips
                    traveldist = numberoftrips*distancekm

                    fuelusageload = weightload/consumption
                    fuelusageunload = weightunload/consumption

                    for commodity in opentisim.core.find_elements(terminal, Commodity):
                        if commodity.type == 'MCH': 
                            literperyear = fuelusageload * (traveldist * 2)
                        elif commodity.type == 'Liquid hydrogen':
                            literperyear = fuelusageunload*traveldist
                        else:
                            literload = fuelusageload * traveldist
                            literunload = fuelusageunload*traveldist
                            literperyear = literload + literunload 

                    transport.fuel = literperyear * fuelprice

                    #add cashflow to vessel 
                    transport = cashflow_data(terminal, transport)
                    #vessel = opentisim.core.add_cashflow_data_to_element(self, jetty)

                    inland_transport.append(transport)
                    
                if terminal.transport_sc2 == 'truck':
                                        #print('** Add vessel to elements')
                    transport = Truck(**transport_defaults)
                    
                    # - capex
                    transport.capex = transport.unit_rate + transport.mobilisation_min

                    # - opex
                    transport.insurance = transport.unit_rate * transport.insurance_perc
                    transport.maintenance =transport.unit_rate * transport.maintenance_perc

                    #   labour**hydrogen_defaults
                    labour = Labour(**labour_data)
                    transport.shift = (
                                (transport.crew_for5 * transport.utilization) / (labour.shift_length * labour.annual_shifts))
                    transport.labour = transport.shift * labour.operational_salary
                    transport.year_online = list_year[year_index]

                    #Add fuel 
                    

                    capacity = truck.capacity
                    hoursperyear = truck.utilization #h/y 

                    avspeed = truck.avspeed #km/h
                    distance = distancekm
                    loadingtime = truck.loadingtime #h 
                    unloadingtime = truck.unloadingtime #h 
                    tripsperyear = numberoftrips

                    travelleddistance = tripsperyear * distance * 2 
                    fuelprice = truck.fuelprice #€/km
                    
                    transport.fuel = travelleddistance * fuelprice


                    #add cashflow to vessel 
                    transport = cashflow_data(terminal, transport)
                    #vessel = opentisim.core.add_cashflow_data_to_element(self, jetty)
                    inland_transport.append(transport)
                    
    return inland_transport

# In[3]:


def transport_elements_plot(terminal, seaborne_transport, numberoftrips, width=0.25, alpha=0.6):
    
    vessels = []
    vessels_capacity = []
    
    years = terminal.years
    
    for year in years:
    # years.append(year)
        vessels.append(0)
        vessels_capacity.append(0)

        for element in seaborne_transport:
            if isinstance(element, Vessel):
                if year >= element.year_online:
                    vessels[-1] += 1
                    vessels_capacity[-1] += (element.call_size * numberoftrips)

                
    demand = pd.DataFrame()
    demand['year'] = years
    demand['demand'] = 0

    for commodity in opentisim.core.find_elements(terminal, Commodity):
        try:
            for column in commodity.scenario_data.columns:
                if column in commodity.scenario_data.columns and column != "year":
                    demand['demand'] += commodity.scenario_data[column]
                elif column in commodity.scenario_data.columns and column != "volume":
                    demand['year'] = commodity.scenario_data[column]
        except:
            demand['demand'] += 0
            demand['year'] += 0
            pass
    
    throughputs_online = []
    for year in terminal.years:
        # years.append(year)
        throughputs_online.append(0)
        try:
            throughput_online, throughput_terminal_in ,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej, throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in, Demand_jetty_in  = terminal.throughput_elements(
                year)

        except:
            throughput_online = 0
            pass

        for element in terminal.elements:
            if isinstance(element, Vessel):
                if year >= element.year_online:
                    throughputs_online[-1] = throughput_online

            # generate plot
    fig, ax1 = plt.subplots(figsize=(20, 10))
    ax1.bar([x for x in years], vessels, width=width, alpha=alpha, label="Vessels", color='#9edae5',
            edgecolor='darkgrey')

    for i, occ in enumerate(vessels):
        occ = occ if type(occ) != float else 0
        ax1.text(x=years[i] - 0.05, y=occ + 0.2, s="{:01.0f}".format(occ), size=15)

    ax2 = ax1.twinx()

    dem = demand['year'].values[~np.isnan(demand['year'].values)]
    values = demand['demand'].values[~np.isnan(demand['demand'].values)]
    # print(dem, values)
    ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')

    #ax2.step(years, demand['demand'].values, label="Demand", where='mid',color='#ff9896')
    ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
    ax2.step(years, vessels_capacity, label="vessels capacity", where='mid', linestyle='--', color='steelblue')

    ax1.set_xlabel('Years')
    ax1.set_ylabel('Vessels [nr]')
    ax2.set_ylabel('Demand/Capacity [t/y]')
    ax1.set_title('Vessels')
    ax1.set_xticks([x for x in years])
    ax1.set_xticklabels(years)
    fig.legend(loc=1)


def inlandtransport_elements_plot(terminal, inland_transport, numberoftrips, width=0.25, alpha=0.6, fontsize=20):
    
    transportmodes = []
    modes_capacity = []
    
    years = terminal.years
    
    for year in years:
    # years.append(year)
        transportmodes.append(0)
        modes_capacity.append(0)
        
        
        if terminal.transport_sc2 == 'barge':
            labelx = 'Barges'
            for element in inland_transport:
                if isinstance(element, Barge):
                    if year >= element.year_online:
                        transportmodes[-1] += 1
                        modes_capacity[-1] += (element.call_size * numberoftrips)
        
        if terminal.transport_sc2 == 'train':
            labelx = 'Trains'
            for element in inland_transport:
                if isinstance(element, Train):
                    if year >= element.year_online:
                        transportmodes[-1] += 1
                        modes_capacity[-1] += (element.call_size * numberoftrips)    
                        
        if terminal.transport_sc2 == 'truck':
            labelx = 'Trucks'
            for element in inland_transport:
                if isinstance(element, Truck):
                    if year >= element.year_online:
                        transportmodes[-1] += 1
                        modes_capacity[-1] += (element.capacity * numberoftrips)                
                
    demand = pd.DataFrame()
    demand['year'] = years
    demand['demand'] = 0

    for commodity in opentisim.core.find_elements(terminal, Commodity):
        try:
            for column in commodity.scenario_data.columns:
                if column in commodity.scenario_data.columns and column != "year":
                    demand['demand'] += commodity.scenario_data[column]
                elif column in commodity.scenario_data.columns and column != "volume":
                    demand['year'] = commodity.scenario_data[column]
        except:
            demand['demand'] += 0
            demand['year'] += 0
            pass
    
    throughputs_online = []
    for year in terminal.years:
        # years.append(year)
        throughputs_online.append(0)
        try:
            throughput_online, throughput_terminal_in ,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej, throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in, Demand_jetty_in  = terminal.throughput_elements(
                year)

        except:
            throughput_online = 0
            pass
        
        throughputs_online[-1] = throughput_online
        
#         for element in terminal.elements:
#             if isinstance(element, Barge):
#                 if year >= element.year_online:
#                     throughputs_online[-1] = throughput_online

            # generate plot
    fig, ax1 = plt.subplots(figsize=(20, 10))
    ax1.bar([x for x in years], transportmodes, width=width, alpha=alpha, label=labelx, color='#9edae5',
            edgecolor='darkgrey')

    for i, occ in enumerate(transportmodes):
        occ = occ if type(occ) != float else 0
        ax1.text(x=years[i] - 0.05, y=occ + 0.2, s="{:01.0f}".format(occ), size=15)

    ax2 = ax1.twinx()

    dem = demand['year'].values[~np.isnan(demand['year'].values)]
    values = demand['demand'].values[~np.isnan(demand['demand'].values)]
    # print(dem, values)
    ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')

    #ax2.step(years, demand['demand'].values, label="Demand", where='mid',color='#ff9896')
    ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
    ax2.step(years, modes_capacity, label="element capacity", where='mid', linestyle='--', color='steelblue')

    ax1.set_xlabel('Years', fontsize=fontsize)
    ax1.set_ylabel('Transport modes [nr]',fontsize=fontsize)
    ax2.set_ylabel('Demand/Capacity [t/y]',fontsize=fontsize)
    ax1.set_title('Transport modes',fontsize=fontsize)
    ax1.set_xticks([x for x in years])
    ax1.set_xticklabels(years, fontsize = fontsize)
    
    fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=4, fontsize=fontsize)
    fig.subplots_adjust(bottom=0.2)
    #fig.legend(loc=1)

    
# In[ ]:

def transport_elements_plot(terminal, seaborne_transport, numberoftrips, width=0.25, alpha=0.6, fontsize = 20):
    
    vessels = []
    vessels_capacity = []
    
    years = terminal.years
    
    for year in years:
    # years.append(year)
        vessels.append(0)
        vessels_capacity.append(0)

        for element in seaborne_transport:
            if isinstance(element, Vessel):
                if year >= element.year_online:
                    vessels[-1] += 1
                    vessels_capacity[-1] += (element.call_size * numberoftrips)
                
                
    demand = pd.DataFrame()
    demand['year'] = years
    demand['demand'] = 0

    for commodity in opentisim.core.find_elements(terminal, Commodity):
        try:
            for column in commodity.scenario_data.columns:
                if column in commodity.scenario_data.columns and column != "year":
                    demand['demand'] += commodity.scenario_data[column]
                elif column in commodity.scenario_data.columns and column != "volume":
                    demand['year'] = commodity.scenario_data[column]
        except:
            demand['demand'] += 0
            demand['year'] += 0
            pass
    
    throughputs_online = []
    for year in terminal.years:
        # years.append(year)
        throughputs_online.append(0)
        try:
            throughput_online, throughput_terminal_in ,throughput_online_jetty_in, throughput_online_stor_in, throughput_online_plant_in, throughput_planned, throughput_planned_jetty,throughput_planned_pipej, throughput_planned_storage, throughput_planned_plant, Demand,Demand_plant_in, Demand_storage_in, Demand_jetty_in  = terminal.throughput_elements(
                year)

        except:
            throughput_online = 0
            pass

        for element in terminal.elements:
            if isinstance(element, Berth):
                if year >= element.year_online:
                    throughputs_online[-1] = throughput_online

            # generate plot
    fig, ax1 = plt.subplots(figsize=(20, 10))
    ax1.bar([x for x in years], vessels, width=width, alpha=alpha, label="Vessels", color='#9edae5',
            edgecolor='darkgrey')

    for i, occ in enumerate(vessels):
        occ = occ if type(occ) != float else 0
        ax1.text(x=years[i] - 0.05, y=occ + 0.2, s="{:01.0f}".format(occ), size=15)

    ax2 = ax1.twinx()

    dem = demand['year'].values[~np.isnan(demand['year'].values)]
    values = demand['demand'].values[~np.isnan(demand['demand'].values)]
    # print(dem, values)
    ax2.step(dem, values, label="Demand [t/y]", where='mid', color='#ff9896')

    #ax2.step(years, demand['demand'].values, label="Demand", where='mid',color='#ff9896')
    ax2.step(years, throughputs_online, label="Throughput [t/y]", where='mid', color='#aec7e8')
    ax2.step(years, vessels_capacity, label="vessels capacity", where='mid', linestyle='--', color='steelblue')

    ax1.set_xlabel('Years',fontsize=fontsize)
    ax1.set_ylabel('Vessels [nr]',fontsize=fontsize)
    ax2.set_ylabel('Demand/Capacity [t/y]',fontsize=fontsize)
    ax1.set_title('Vessels',fontsize=fontsize)
    ax1.set_xticks([x for x in years])
    ax1.set_xticklabels(years,fontsize=fontsize)
    
    fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
                   fancybox=True, shadow=True, ncol=4, fontsize=fontsize)
    fig.subplots_adjust(bottom=0.2)
    #fig.legend(loc=1)


def add_cashflow_vessels(terminal, seaborne_transport):
    cash_flows = pd.DataFrame()
    
    cash_flows['year'] = terminal.modelframe
    cash_flows['capex'] = 0
    #     cash_flows['capex_material'] = 0 
    cash_flows['maintenance'] = 0
    cash_flows['insurance'] = 0
    #     cash_flows['energy'] = 0
    cash_flows['labour'] = 0
    cash_flows['fuel'] = 0
    
    for element in seaborne_transport:
        if hasattr(element, 'df'):
            element.df = element.df.fillna(0)
            for column in cash_flows.columns:
                if column in element.df.columns and column != "year":
                    cash_flows[column] += element.df[column]

    cash_flows_WACC_real = pd.DataFrame()
    cash_flows_WACC_real['year'] = cash_flows['year']
    for year in terminal.years: #range(Terminal.startyear, Terminal.startyear + Terminal.lifecycle):
        for column in cash_flows.columns:
            if column != "year":
                cash_flows_WACC_real.loc[cash_flows_WACC_real['year'] == year, column] =                     cash_flows.loc[cash_flows['year'] == year, column] /                            ((1 + opentisim.core.WACC_real()) ** (year - terminal.startyear))

    cash_flows = cash_flows.fillna(0)
    cash_flows_WACC_real = cash_flows_WACC_real.fillna(0)

    return cash_flows,cash_flows_WACC_real 


# In[ ]:


def cashflow_plot(cash_flows, title='Cash flow plot', width=0.2, alpha=0.6, fontsize=20):
    """Gather data from Terminal elements and combine into a cash flow plot"""

    # prepare years, revenue, capex and opex for plotting
    years = cash_flows['year'].values
    #revenues = cash_flows['revenues'].values
    capex = cash_flows['capex'].values
    opex = cash_flows['insurance'].values + cash_flows['maintenance'].values + cash_flows['fuel'].values +            cash_flows['labour'].values 
    
        # generate plot canvas
    fig, ax1 = plt.subplots(figsize=(20, 12))

    colors = ['mediumseagreen', 'firebrick', 'steelblue', 'blueviolet']

    # print capex, opex and revenue
    ax1.bar([x - 2*width for x in years], -capex, zorder=1, width=width, alpha=alpha, label="capex", color=colors[1],
            edgecolor='darkgrey')
    ax1.bar([x - width for x in years], -opex, zorder=1, width=width, alpha=alpha, label="opex", color=colors[0],
            edgecolor='darkgrey')


    # title and labels
    ax1.set_title(title, fontsize=fontsize)
    ax1.set_xlabel('Years', fontsize=fontsize)
    ax1.set_ylabel('Cashflow [M $]', fontsize=fontsize)
    # todo: check the units

    # ticks and tick labels
    ax1.set_xticks([x for x in years])
    ax1.set_xticklabels([int(x) for x in years], rotation='vertical', fontsize=fontsize)
    ax1.yaxis.set_tick_params(labelsize=fontsize)

    # add grid
    ax1.grid(zorder=0, which='major', axis='both')

    # print legend
    fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
               fancybox=True, shadow=True, ncol=5, fontsize=fontsize)
    fig.subplots_adjust(bottom=0.15)

