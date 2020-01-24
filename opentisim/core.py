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
    """return elements of type obj part of self.elements"""

    list_of_elements = []
    if Terminal.elements != []:
        for element in Terminal.elements:
            if isinstance(element, obj):
                list_of_elements.append(element)

    return list_of_elements

def occupancy_to_waitingfactor(occupancy=.3, nr_of_servers_chk=4, poly_order=6):
    """Waiting time factor (E2/E2/n Erlang queueing theory using 6th order polynomial regression)"""

    # Create dataframe with data from Groenveld (2007) - Table V
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
    df = pd.DataFrame(data, index=utilisation, columns=nr_of_servers)

    # Create a 6th order polynomial fit through the data (for nr_of_stations_chk)
    target = df.loc[:, nr_of_servers_chk]
    p_p = np.polyfit(target.index, target.values, poly_order)

    waiting_factor = np.polyval(p_p, occupancy)
    # todo: when the nr of servers > 10 the waiting factor should be set to inf (definitively more equipment needed)

    # Return waiting factor
    return waiting_factor

def waitingfactor_to_occupancy(factor=.3, nr_of_servers_chk=4, poly_order=6):
    """Waiting time factor (E2/E2/n Erlang queueing theory using 6th order polynomial regression)"""

    # Create dataframe with data from Groenveld (2007) - Table V
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
    df = pd.DataFrame(data, index=utilisation, columns=nr_of_servers)

    # Create a 6th order polynomial fit through the data (for nr_of_stations_chk)
    target = df.loc[:, nr_of_servers_chk]
    p_p = np.polyfit(target.values, target.index, poly_order)
    print(p_p)

    occupancy = np.polyval(p_p, factor)

    # Return occupancy
    return occupancy

