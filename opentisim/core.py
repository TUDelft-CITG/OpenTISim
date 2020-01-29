# package(s) for data handling
import pandas as pd
import numpy as np


# *** General functions
def report_element(Terminal, Element, year):
    elements = 0
    elements_online = 0
    element_name = []
    list_of_elements = find_elements(Terminal, Element)
    if list_of_elements != []:
        for element in list_of_elements:
            element_name = element.name
            elements += 1
            if year >= element.year_online:
                elements_online += 1

    if Terminal.debug:
        if elements_online or elements:
            print('     a total of {} {} is online; a total of {} is still pending'.format(elements_online, element_name, elements - elements_online))

    return elements_online, elements


def find_elements(Terminal, obj):
    """return elements of type obj part of Terminal.elements"""

    list_of_elements = []
    if Terminal.elements != []:
        for element in Terminal.elements:
            if isinstance(element, obj):
                list_of_elements.append(element)

    return list_of_elements


def add_cashflow_data_to_element(Terminal, element):
    """Place cashflow data in element dataframe
    Elements that take two years to build are assign 60% to year one and 40% to year two."""

    # years
    years = list(range(Terminal.startyear, Terminal.startyear + Terminal.lifecycle))

    # capex
    capex = element.capex

    # opex
    maintenance = element.maintenance
    insurance = element.insurance
    labour = element.labour

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

    # opex
    if maintenance:
        df.loc[df["year"] >= year_online, "maintenance"] = maintenance
    if insurance:
        df.loc[df["year"] >= year_online, "insurance"] = insurance
    if labour:
        df.loc[df["year"] >= year_online, "labour"] = labour

    df.fillna(0, inplace=True)

    element.df = df

    return element


def add_cashflow_elements(Terminal, labour):
    """Cycle through each element and collect all cash flows into a pandas dataframe."""

    cash_flows = pd.DataFrame()

    # initialise cash_flows
    cash_flows['year'] = list(range(Terminal.startyear, Terminal.startyear + Terminal.lifecycle))
    cash_flows['capex'] = 0
    cash_flows['maintenance'] = 0
    cash_flows['insurance'] = 0
    cash_flows['energy'] = 0
    cash_flows['labour'] = 0
    cash_flows['demurrage'] = Terminal.demurrage
    try:
       cash_flows['revenues'] = Terminal.revenues
    except:
       cash_flows['revenues'] = 0

    # add labour component for years were revenues are not zero
    cash_flows.loc[cash_flows[
                       'revenues'] != 0, 'labour'] = labour.international_staff * labour.international_salary + labour.local_staff * labour.local_salary
    # todo: check the labour costs of the container terminals (they are not included now)

    for element in Terminal.elements:
        if hasattr(element, 'df'):
            for column in cash_flows.columns:
                if column in element.df.columns and column != "year":
                    cash_flows[column] += element.df[column]

    # calculate WACC real cashflows
    cash_flows_WACC_real = pd.DataFrame()
    cash_flows_WACC_real['year'] = cash_flows['year']
    for year in range(Terminal.startyear, Terminal.startyear + Terminal.lifecycle):
        for column in cash_flows.columns:
            if column != "year":
                cash_flows_WACC_real.loc[cash_flows_WACC_real['year'] == year, column] = \
                    cash_flows.loc[
                        cash_flows[
                            'year'] == year, column] / (
                            (1 + WACC_real()) ** (
                            year - Terminal.startyear))

    cash_flows = cash_flows.fillna(0)
    cash_flows_WACC_real = cash_flows_WACC_real.fillna(0)

    return cash_flows, cash_flows_WACC_real


def NPV(Terminal, labour):
    """Gather data from Terminal elements and combine into a cash flow overview"""

    # add cash flow information for each of the Terminal elements
    cash_flows, cash_flows_WACC_real = add_cashflow_elements(Terminal, labour)

    # prepare years, revenue, capex and opex for plotting
    years = cash_flows_WACC_real['year'].values
    revenues = cash_flows_WACC_real['revenues'].values
    capex = cash_flows_WACC_real['capex'].values
    opex = cash_flows_WACC_real['insurance'].values + \
           cash_flows_WACC_real['maintenance'].values + \
           cash_flows_WACC_real['energy'].values + \
           cash_flows_WACC_real['demurrage'].values + \
           cash_flows_WACC_real['labour'].values

    # collect all results in a pandas dataframe
    df = pd.DataFrame(index=years, data=-capex, columns=['CAPEX'])
    df['OPEX'] = -opex
    df['REVENUES'] = revenues
    df['PV'] = - capex - opex + revenues
    df['cum-PV'] = np.cumsum(- capex - opex + revenues)

    return df


def WACC_nominal(Gearing=60, Re=.10, Rd=.30, Tc=.28):
    """Nominal cash flow is the true dollar amount of future revenues the company expects
    to receive and expenses it expects to pay out, including inflation.
    When all cashflows within the model are denoted in real terms and including inflation."""

    Gearing = Gearing
    Re = Re  # return on equity
    Rd = Rd  # return on debt
    Tc = Tc  # income tax
    E = 100 - Gearing
    D = Gearing

    WACC_nominal = ((E / (E + D)) * Re + (D / (E + D)) * Rd) * (1 - Tc)

    return WACC_nominal


def WACC_real(inflation=0.02):  # old: interest=0.0604
    """Real cash flow expresses a company's cash flow with adjustments for inflation.
    When all cashflows within the model are denoted in real terms and have been
    adjusted for inflation (no inlfation has been taken into account),
    WACC_real should be used. WACC_real is computed by as follows:"""

    WACC_real = (WACC_nominal() + 1) / (inflation + 1) - 1

    return WACC_real


def occupancy_to_waitingfactor(occupancy=.3, nr_of_servers_chk=4, poly_order=6, kendall='E2/E2/n'):
    """Waiting time factor (E2/E2/n or M/E2/n) queueing theory using 6th order polynomial regression)"""

    if kendall == 'E2/E2/n':
        # Create dataframe with data from Groenveld (2007) - Table V
        # See also PIANC 2014 Table 6.2
        utilisation = np.array([.1, .2, .3, .4, .5, .6, .7, .8, .9])
        nr_of_servers = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        data = np.array([
            [0.0166, 0.0006, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0604, 0.0065, 0.0011, 0.0002, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.1310, 0.0235, 0.0062, 0.0019, 0.0007, 0.0002, 0.0001, 0.0000, 0.0000, 0.0000],
            [0.2355, 0.0576, 0.0205, 0.0085, 0.0039, 0.0019, 0.0009, 0.0005, 0.0003, 0.0001],
            [0.3904, 0.1181, 0.0512, 0.0532, 0.0142, 0.0082, 0.0050, 0.0031, 0.0020, 0.0013],
            [0.6306, 0.2222, 0.1103, 0.0639, 0.0400, 0.0265, 0.0182, 0.0128, 0.0093, 0.0069],
            [1.0391, 0.4125, 0.2275, 0.1441, 0.0988, 0.0712, 0.0532, 0.0407, 0.0319, 0.0258],
            [1.8653, 0.8300, 0.4600, 0.3300, 0.2300, 0.1900, 0.1400, 0.1200, 0.0900, 0.0900],
            [4.3590, 2.0000, 1.2000, 0.9200, 0.6500, 0.5700, 0.4400, 0.4000, 0.3200, 0.3000]
        ])

    elif kendall == 'M/E2/n':
        # Create dataframe with data from Groenveld (2007) - Table IV
        # See also PIANC 2014 Table 6.1
        utilisation = np.array([.1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7, .75, .8, .85, .9])
        nr_of_servers = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        data = np.array([
            [0.08, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.13, 0.02, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.19, 0.03, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.25, 0.05, 0.02, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.32, 0.08, 0.03, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.40, 0.11, 0.04, 0.02, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.50, 0.15, 0.06, 0.03, 0.02, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.60, 0.20, 0.08, 0.05, 0.03, 0.02, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.75, 0.26, 0.12, 0.07, 0.04, 0.03, 0.02, 0.01, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00],
            [0.91, 0.33, 0.16, 0.10, 0.06, 0.04, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01, 0.00, 0.00],
            [1.13, 0.43, 0.23, 0.14, 0.09, 0.06, 0.05, 0.03, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01],
            [1.38, 0.55, 0.30, 0.19, 0.12, 0.09, 0.07, 0.05, 0.04, 0.03, 0.03, 0.02, 0.02, 0.02],
            [1.75, 0.73, 0.42, 0.27, 0.19, 0.14, 0.11, 0.09, 0.07, 0.06, 0.05, 0.04, 0.03, 0.03],
            [2.22, 0.96, 0.59, 0.39, 0.28, 0.21, 0.17, 0.14, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05],
            [3.00, 1.34, 0.82, 0.57, 0.42, 0.33, 0.27, 0.22, 0.18, 0.16, 0.13, 0.11, 0.10, 0.09],
            [4.50, 2.00, 1.34, 0.90, 0.70, 0.54, 0.46, 0.39, 0.34, 0.30, 0.26, 0.23, 0.20, 0.18],
            [6.75, 3.14, 2.01, 1.45, 1.12, 0.91, 0.76, 0.65, 0.56, 0.50, 0.45, 0.40, 0.36, 0.33]
        ])

    df = pd.DataFrame(data, index=utilisation, columns=nr_of_servers)

    # Create a 6th order polynomial fit through the data (for nr_of_stations_chk)
    target = df.loc[:, nr_of_servers_chk]
    p_p = np.polyfit(target.index, target.values, poly_order)

    waiting_factor = np.polyval(p_p, occupancy)
    # todo: when the nr of servers > 10 the waiting factor should be set to inf (definitively more equipment needed)

    # Return waiting factor
    return waiting_factor


def waitingfactor_to_occupancy(factor=.3, nr_of_servers_chk=4, poly_order=6):
    """Waiting time factor (E2/E2/n or M/E2/n) queueing theory using 6th order polynomial regression)"""

    if kendall == 'E2/E2/n':
        # Create dataframe with data from Groenveld (2007) - Table V
        # See also PIANC 2014 Table 6.2
        utilisation = np.array([.1, .2, .3, .4, .5, .6, .7, .8, .9])
        nr_of_servers = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        data = np.array([
            [0.0166, 0.0006, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.0604, 0.0065, 0.0011, 0.0002, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
            [0.1310, 0.0235, 0.0062, 0.0019, 0.0007, 0.0002, 0.0001, 0.0000, 0.0000, 0.0000],
            [0.2355, 0.0576, 0.0205, 0.0085, 0.0039, 0.0019, 0.0009, 0.0005, 0.0003, 0.0001],
            [0.3904, 0.1181, 0.0512, 0.0532, 0.0142, 0.0082, 0.0050, 0.0031, 0.0020, 0.0013],
            [0.6306, 0.2222, 0.1103, 0.0639, 0.0400, 0.0265, 0.0182, 0.0128, 0.0093, 0.0069],
            [1.0391, 0.4125, 0.2275, 0.1441, 0.0988, 0.0712, 0.0532, 0.0407, 0.0319, 0.0258],
            [1.8653, 0.8300, 0.4600, 0.3300, 0.2300, 0.1900, 0.1400, 0.1200, 0.0900, 0.0900],
            [4.3590, 2.0000, 1.2000, 0.9200, 0.6500, 0.5700, 0.4400, 0.4000, 0.3200, 0.3000]
        ])
    elif kendall == 'M/E2/n':
        # Create dataframe with data from Groenveld (2007) - Table IV
        # See also PIANC 2014 Table 6.1
        utilisation = np.array([.1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7, .75, .8, .85, .9])
        nr_of_servers = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        data = np.array([
            [0.08, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.13, 0.02, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.19, 0.03, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.25, 0.05, 0.02, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.32, 0.08, 0.03, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.40, 0.11, 0.04, 0.02, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.50, 0.15, 0.06, 0.03, 0.02, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.60, 0.20, 0.08, 0.05, 0.03, 0.02, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            [0.75, 0.26, 0.12, 0.07, 0.04, 0.03, 0.02, 0.01, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00],
            [0.91, 0.33, 0.16, 0.10, 0.06, 0.04, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01, 0.00, 0.00],
            [1.13, 0.43, 0.23, 0.14, 0.09, 0.06, 0.05, 0.03, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01],
            [1.38, 0.55, 0.30, 0.19, 0.12, 0.09, 0.07, 0.05, 0.04, 0.03, 0.03, 0.02, 0.02, 0.02],
            [1.75, 0.73, 0.42, 0.27, 0.19, 0.14, 0.11, 0.09, 0.07, 0.06, 0.05, 0.04, 0.03, 0.03],
            [2.22, 0.96, 0.59, 0.39, 0.28, 0.21, 0.17, 0.14, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05],
            [3.00, 1.34, 0.82, 0.57, 0.42, 0.33, 0.27, 0.22, 0.18, 0.16, 0.13, 0.11, 0.10, 0.09],
            [4.50, 2.00, 1.34, 0.90, 0.70, 0.54, 0.46, 0.39, 0.34, 0.30, 0.26, 0.23, 0.20, 0.18],
            [6.75, 3.14, 2.01, 1.45, 1.12, 0.91, 0.76, 0.65, 0.56, 0.50, 0.45, 0.40, 0.36, 0.33]
        ])

    df = pd.DataFrame(data, index=utilisation, columns=nr_of_servers)

    # Create a 6th order polynomial fit through the data (for nr_of_stations_chk)
    target = df.loc[:, nr_of_servers_chk]
    p_p = np.polyfit(target.values, target.index, poly_order)
    print(p_p)

    occupancy = np.polyval(p_p, factor)

    # Return occupancy
    return occupancy

# def waiting_time(self, year):
#     """
#    - Import the berth occupancy of every year
#    - Find the factor for the waiting time with the E2/E/n quing theory using 4th order polynomial regression
#    - Waiting time is the factor times the crane occupancy
#    """
#
#     smallhydrogen_calls, largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, total_calls, total_vol, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned, handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned, total_calls_planned,  total_vol_planned = self.calculate_vessel_calls(year)
#     berth_occupancy_planned, berth_occupancy_online, unloading_occupancy_planned, unloading_occupancy_online = self.calculate_berth_occupancy(year, smallhydrogen_calls,     largehydrogen_calls, smallammonia_calls, largeammonia_calls, handysize_calls, panamax_calls, vlcc_calls, smallhydrogen_calls_planned, largehydrogen_calls_planned, smallammonia_calls_planned, largeammonia_calls_planned,handysize_calls_planned, panamax_calls_planned, vlcc_calls_planned)
#
#     #find the different factors which are linked to the number of berths
#     berths = len(core.find_elements(self, Berth))
#
#     if berths == 1:
#         factor = max(0,
#                      79.726 * berth_occupancy_online ** 4 - 126.47 * berth_occupancy_online ** 3 + 70.660 * berth_occupancy_online ** 2 - 14.651 * berth_occupancy_online + 0.9218)
#     elif berths == 2:
#         factor = max(0,
#                      29.825 * berth_occupancy_online ** 4 - 46.489 * berth_occupancy_online ** 3 + 25.656 * berth_occupancy_online ** 2 - 5.3517 * berth_occupancy_online + 0.3376)
#     elif berths == 3:
#         factor = max(0,
#                      19.362 * berth_occupancy_online ** 4 - 30.388 * berth_occupancy_online ** 3 + 16.791 * berth_occupancy_online ** 2 - 3.5457 * berth_occupancy_online + 0.2253)
#     elif berths == 4:
#         factor = max(0,
#                      17.334 * berth_occupancy_online ** 4 - 27.745 * berth_occupancy_online ** 3 + 15.432 * berth_occupancy_online ** 2 - 3.2725 * berth_occupancy_online + 0.2080)
#     elif berths == 5:
#         factor = max(0,
#                      11.149 * berth_occupancy_online ** 4 - 17.339 * berth_occupancy_online ** 3 + 9.4010 * berth_occupancy_online ** 2 - 1.9687 * berth_occupancy_online + 0.1247)
#     elif berths == 6:
#         factor = max(0,
#                      10.512 * berth_occupancy_online ** 4 - 16.390 * berth_occupancy_online ** 3 + 8.8292 * berth_occupancy_online ** 2 - 1.8368 * berth_occupancy_online + 0.1158)
#     elif berths == 7:
#         factor = max(0,
#                      8.4371 * berth_occupancy_online ** 4 - 13.226 * berth_occupancy_online ** 3 + 7.1446 * berth_occupancy_online ** 2 - 1.4902 * berth_occupancy_online + 0.0941)
#     else:
#         # if there are no berths the occupancy is 'infinite' so a berth is certainly needed
#         factor = float("inf")
#
#     waiting_time_hours = factor * unloading_occupancy_online * self.operational_hours / total_calls
#     waiting_time_occupancy = waiting_time_hours * total_calls / self.operational_hours
#
#     return factor, waiting_time_occupancy
