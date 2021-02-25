
# coding: utf-8

# In[ ]:


import datetime, time
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


# In[ ]:


def length_section(section):
    """
    This method determines the distance over each section, 
    where sections are defined as shapely.geometry.LineString
    """

    wgs84 = pyproj.Geod(ellps='WGS84')

    # intitialise distance over path
    section_length = 0
    for index, item  in enumerate(section.coords[:-1]):
        section_length += int(wgs84.inv(section.coords[index][0],section.coords[index][1],
                                        section.coords[index+1][0],section.coords[index+1][1])[2])

    return section_length

def section_to_points(section):
    """
    This method returns a list of tuples with coordinate
    Needed for plotting on folium
    """
    points = []
    for index, item  in enumerate(section.coords):
        points.append(tuple([section.coords[index][1],section.coords[index][0]]))
        
    return points

def convert_path_to_graph(path):
    """This method converts points in a path to a networkx graph object"""
        
    FG = nx.Graph()
    positions = {}
    names = {}
    for i, j in enumerate(path):
        FG.add_node('node-' + str(i), name='node-' + str(i), geometry=shapely.geometry.Point(path[i][0], path[i][1]))
        positions['node-' + str(i)] = (path[i][0], path[i][1])
        names['node-' + str(i)] = 'node-' + str(i)
        if i > 0:
            FG.add_edge('node-' + str(i-1), 'node-' + str(i), weight=1)
            
    return FG, positions, names

def distance_over_path(FG, loc1, loc2):
    """This method determines the distance over a path between two points
    (NB: loc1 and loc2 are strings that define the names on the graph)"""

    wgs84 = pyproj.Geod(ellps='WGS84')

    # get path from graph
    path = nx.dijkstra_path(FG, loc1, loc2)

    # intitialise distance over path
    distance_over_path = 0

    # add the length of each path section to distance_path
    for node in enumerate(path[:-1]):
        orig = nx.get_node_attributes(FG, "geometry")[path[node[0]]]
        dest = nx.get_node_attributes(FG, "geometry")[path[node[0] + 1]]

        distance_over_path += int(wgs84.inv(shapely.geometry.asShape(orig).x, shapely.geometry.asShape(orig).y,
                                            shapely.geometry.asShape(dest).x, shapely.geometry.asShape(dest).y)[2])

        if node[0] + 2 == len(path):
            break

    return distance_over_path

def graph_kml(
    FG,
    fname="graph.kml",
    icon="http://maps.google.com/mapfiles/kml/shapes/donut.png",
    size=0.5,
    scale=0.5,
    width=5):
    """Create a kml visualisation of graph."""

    # create a kml file containing the visualisation
    kml = Kml()
    fol = kml.newfolder(name="Graph")

    shared_style = Style()
    shared_style.labelstyle.color = "ffffffff"  # White
    shared_style.labelstyle.scale = size
    shared_style.iconstyle.color = "ffffffff"  # White
    shared_style.iconstyle.scale = scale
    shared_style.iconstyle.icon.href = icon
    shared_style.linestyle.color = "ff0055ff"  # Red
    shared_style.linestyle.width = width

    nodes = list(FG.nodes)

    # each timestep will be represented as a single point
    for log_index, _ in enumerate(list(FG.nodes)):

        pnt = fol.newpoint(
            name="",
            coords=[
                (
                    nx.get_node_attributes(FG, "geometry")[nodes[log_index]].x,
                    nx.get_node_attributes(FG, "geometry")[nodes[log_index]].y,
                )
            ],
        )
        pnt.style = shared_style

    edges = list(FG.edges)
    for log_index, _ in enumerate(list(FG.edges)):

        lne = fol.newlinestring(
            name="",
            coords=[
                (
                    nx.get_node_attributes(FG, "geometry")[edges[log_index][0]].x,
                    nx.get_node_attributes(FG, "geometry")[edges[log_index][0]].y,
                ),
                (
                    nx.get_node_attributes(FG, "geometry")[edges[log_index][1]].x,
                    nx.get_node_attributes(FG, "geometry")[edges[log_index][1]].y,
                ),
            ],
        )
        lne.style = shared_style

    kml.save(fname)

