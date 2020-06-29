import pandas as pd
import numpy as np
import math
import copy

import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, LineString

from opentisim.container_system import *
from opentisim.container_objects import *
from opentisim import container_defaults
from opentisim import core

'Function for determining the terminal configuration'


def terminal_configuration(terminal_layout):
    'Define the terminal area based on the coordinates'

    'Nomenclature :'
    'TERMINAL = Full area of the terminal based on the coordinates'
    'PRIM_YARD = Effective area of the terminal for container stacking (primary yard)'

    '(1) Determining the TERMINAL'
    'Creating area using line string, in order to use parallel offset function (because it is not working for polygon)'
    coords = []
    coords = copy.deepcopy(terminal_layout.coords)

    terminal_line = LineString(coords)

    'Converting TERMINAL to Polygon'
    terminal = Polygon(terminal_line)
    terminal_x, terminal_y = terminal.exterior.xy

    '(2) Define the APRON area'
    'Determine the quay length'
    quay_length = coords[(len(coords)) - 2][0] - coords[0][0]

    'Creating area for the apron'
    apron_coords = [None] * 5
    apron_coords[0] = coords[0]
    apron_coords[1] = [coords[0][0], coords[0][1] + terminal_layout.apron_width]
    apron_coords[2] = [coords[0][0] + quay_length, coords[0][1] + terminal_layout.apron_width]
    apron_coords[3] = [coords[0][0] + quay_length, coords[0][1]]
    apron_coords[4] = coords[0]

    apron = Polygon(apron_coords)

    apron_area = apron.area

    '(3) Determine the PRIMARY YARD area'
    'Determine the y location of the imaginary line that will be iterated to find the 60-75% value primary yard ratio to total terminal yard'
    line_y = max(terminal_y) - 10

    'Determine the line'
    line = LineString([[min(terminal_x) - 1 / 4 * max(terminal_x), line_y], [max(terminal_x) + 1 / 4 * max(terminal_x), line_y]])

    'Define the intersection point of the line and the terminal area'
    intersection = line.intersection(terminal_line)

    if intersection.geom_type == 'MultiPoint':
        intersection_x, intersection_y = LineString(intersection).xy
    elif intersection.geom_type == 'Point':
        intersection_x, intersection_y = intersection.xy

    'Define temporary parameters for the while loop in determining the primary yard boundary'
    p = 0
    q = 0

    'Determine list for the primary yard coordinate'
    prim_yard_coords = []

    'Algorithm in determining the FIRST coordinate points for the primary yard'
    'Different approach is implemented for triangular terminal (or terminal that has less or equal than 3 points, because it will generate 1 additional point'
    'For case of non-triangular terminal, len(coords) > 4'
    if len(coords) > 4:
        for p in range(0, len(coords)):
            if intersection_y[0] <= coords[p][1]:
                if q + 1 <= len(intersection_y):
                    prim_yard_coords.append([intersection_x[q], intersection_y[q]])
                    q = q + 1
                else:
                    p = p
            if intersection_y[0] >= coords[p][1]:
                prim_yard_coords.append(coords[p])

    else:
        for p in range(0, len(coords)):
            if intersection_y[0] <= coords[p][1]:
                while q + 1 <= len(intersection_y):
                    prim_yard_coords.append([intersection_x[q], intersection_y[q]])
                    q = q + 1
                else:
                    p = p
            if intersection_y[0] >= coords[p][1]:
                prim_yard_coords.append(coords[p])

    'Determine the prim_yard coords to exclude the apron'
    prim_yard_coords[0][1] = terminal_layout.apron_width
    prim_yard_coords[len(prim_yard_coords) - 2][1] = terminal_layout.apron_width
    prim_yard_coords[len(prim_yard_coords) - 1][1] = terminal_layout.apron_width

    'Determine the area of the total terminal area'
    terminal_area = terminal.area

    'Determine the primary yard area'
    prim_yard = Polygon(prim_yard_coords)

    'Determine the area of the primary yard area'
    prim_yard_area = prim_yard.area

    'Determine the current primary yard to total terminal area ratio'
    prim_full_ratio = prim_yard_area / terminal_area

    'Algorithm to find the condition where 60-75% is the value of the primary yard ratio to total terminal yard'
    'Determine the planned primary yard to total terminal area ratio'
    planned_prim_full_ratio = 0.75

    while prim_full_ratio >= planned_prim_full_ratio:
        'Determine the y location of the line'
        line_y = math.ceil((line_y - 10) * 100) / 100

        'Determine the line'
        line = LineString([[min(terminal_x) - 1 / 4 * max(terminal_x), line_y], [max(terminal_x) + 1 / 4 * max(terminal_x), line_y]])

        'Define the intersection point of the line and the terminal area'
        intersection = line.intersection(terminal_line)

        if intersection.geom_type == 'MultiPoint':
            intersection_x, intersection_y = LineString(intersection).xy
        elif intersection.geom_type == 'Point':
            intersection_x, intersection_y = intersection.xy

        'Define parameters for the while loop in determining the primary yard boundary'
        p = 0
        q = 0

        'Determine the primary yard coordinate'
        prim_yard_coords = list()

        'Algorithm in determining the coordinate points for the primary yard'
        if len(coords) > 4:
            for p in range(0, len(coords)):
                if intersection_y[0] <= coords[p][1]:
                    if q + 1 <= len(intersection_y):
                        prim_yard_coords.append([intersection_x[q], intersection_y[q]])
                        q = q + 1
                    else:
                        p = p
                if intersection_y[0] >= coords[p][1]:
                    prim_yard_coords.append(coords[p])

        else:
            for p in range(0, len(coords)):
                if intersection_y[0] <= coords[p][1]:
                    while q + 1 <= len(intersection_y):
                        prim_yard_coords.append([intersection_x[q], intersection_y[q]])
                        q = q + 1
                    else:
                        p = p
                if intersection_y[0] >= coords[p][1]:
                    prim_yard_coords.append(coords[p])

        'Determine the primary yard area'
        prim_yard = Polygon(prim_yard_coords)
        prim_yard_area = prim_yard.area

        'Determine the current primary yard to total terminal area ratio'
        prim_full_ratio = prim_yard_area / terminal_area

    'Creating area for the primary yard using line string, to use parallel offset function (because it is not working for polygon)'
    prim_yard_line = LineString(prim_yard_coords)

    'Creating terminal area that is already decreased by the traffic lane, because it is assumed that traffic lane is available in all side of the container terminal'
    prim_yard_wotl_line = prim_yard_line.parallel_offset(terminal_layout.traffic_lane, 'right', join_style=2, mitre_limit=terminal_layout.traffic_lane)

    """# The length of the primary yard coordinates
    len_prim = len(prim_yard_coords)

    # Moving the primary yard bottom line upwards to the apron line
    prim_yard_coords[0][1] = terminal_layout.apron_width
    prim_yard_coords[len_prim - 2][1] = terminal_layout.apron_width
    prim_yard_coords[len_prim - 1][1] = terminal_layout.apron_width"""

    'Converting TERMINAL to Polygon'
    prim_yard = Polygon(prim_yard_wotl_line)

    return terminal, quay_length, prim_yard, apron, terminal_area, prim_yard_area, apron_area, prim_full_ratio


def block_configuration(terminal_layout):
    coords = []
    coords = terminal_layout.coords

    'Determine the quay length'
    quay_length = coords[(len(coords)) - 2][0] - coords[0][0]

    'Determine the terminal boundary'
    prim_yard_x, prim_yard_y = terminal_layout.prim_yard.exterior.xy

    if terminal_layout.stack_equipment == 'rtg':
        'Determine block length'
        'Determine number of blocks in x direction'
        max_blocks_x = math.ceil((quay_length - terminal_layout.traffic_lane) / (terminal_layout.max_block_length + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head))

        'Determine block length"'
        block_length = math.floor((((quay_length - terminal_layout.traffic_lane) / max_blocks_x) - terminal_layout.traffic_lane - 2 * terminal_layout.margin_head) * 100) / 100

        'If block length is shorter than minimum block length, decrease the number of blocks by 1'
        if block_length < terminal_layout.min_block_length:
            while block_length < terminal_layout.min_block_length:
                max_blocks_x = max_blocks_x - 1
                block_length = math.floor((((quay_length - terminal_layout.traffic_lane) / max_blocks_x) - terminal_layout.traffic_lane - 2 * terminal_layout.margin_head) * 100) / 100

        'If block length is larger than the maximum block length, the block length is equal to maximum block length'
        if block_length > terminal_layout.max_block_length:
            block_length = terminal_layout.max_block_length

        'Determine block width'
        block_width = 2 * terminal_layout.equipment_track + terminal_layout.vehicle_track + terminal_layout.stack.width * terminal_layout.tgs_y

        'Determine number of blocks in row direction'
        max_blocks_y = math.floor((max(prim_yard_y) - terminal_layout.apron_width + terminal_layout.bypass_lane - terminal_layout.traffic_lane) / (block_width + terminal_layout.bypass_lane))

    elif terminal_layout.stack_equipment == 'rmg':
        'Determine number of blocks in y direction'
        max_blocks_y = math.ceil((max(prim_yard_y) - terminal_layout.apron_width) / (terminal_layout.max_block_length + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head))

        'Determine block length'
        block_length = math.floor((((max(prim_yard_y)) - terminal_layout.apron_width - max_blocks_y * (terminal_layout.traffic_lane + 2 *
                                                                                                       terminal_layout.margin_head)) / max_blocks_y) * 100) / 100

        'If block length is shorter than minimum block length, decrease the number of blocks by 1'
        if block_length < terminal_layout.min_block_length:
            while block_length < terminal_layout.min_block_length:
                max_blocks_y = max_blocks_y - 1

                block_length = math.floor((((max(prim_yard_y)) - terminal_layout.apron_width - max_blocks_y * (terminal_layout.traffic_lane + 2 *
                                                                                                               terminal_layout.margin_head)) / max_blocks_y) * 100) / 100

        'If block length is larger than the maximum block length, the block length is equal to maximum block length'
        if block_length > terminal_layout.max_block_length:
            block_length = terminal_layout.max_block_length

        'Determine block width'
        block_width = math.floor((terminal_layout.tgs_x * terminal_layout.stack.width + 2 * terminal_layout.equipment_track) * 100) / 100

        'Determine number of blocks in x direction'
        max_blocks_x = math.floor((quay_length - 2 * terminal_layout.traffic_lane + terminal_layout.margin_parallel) / (block_width + terminal_layout.margin_parallel))

        'Determine the modified traffic lane width'
        margin_parallel = math.floor(((quay_length - 2 * terminal_layout.traffic_lane - max_blocks_x * block_width) / (max_blocks_x - 1)) * 100) / 100
        terminal_layout.margin_parallel = margin_parallel

    elif terminal_layout.stack_equipment == 'sc':
        'Determine number of blocks in bay direction'
        max_blocks_y = math.ceil((max(prim_yard_y) - terminal_layout.apron_width - terminal_layout.margin_head) / (terminal_layout.max_block_length + terminal_layout.traffic_lane))

        'Determine block length"'
        block_length = math.floor((((max(prim_yard_y) - terminal_layout.apron_width - terminal_layout.margin_head) / max_blocks_y) - terminal_layout.traffic_lane) *
                                  100) / 100

        'If block length is shorter than minimum block length, decrease the number of blocks by 1'
        if block_length < terminal_layout.min_block_length:
            while block_length < terminal_layout.min_block_length:
                max_blocks_y = max_blocks_y - 1
                block_length = math.floor((((max(prim_yard_y) - terminal_layout.apron_width - terminal_layout.margin_head) / max_blocks_y) -
                                           terminal_layout.traffic_lane) * 100) / 100

        'If block length is larger than the maximum block length, the block length is equal to maximum block length'
        if block_length > terminal_layout.max_block_length:
            block_length = terminal_layout.max_block_length

        'Determine number of blocks in row direction'
        max_blocks_x = math.ceil((quay_length - terminal_layout.traffic_lane) / (terminal_layout.max_block_width + terminal_layout.traffic_lane))

        'Determine block length"'
        block_width = math.floor((((quay_length - terminal_layout.traffic_lane) / max_blocks_x) - terminal_layout.traffic_lane) * 100) / 100

        'If block length is shorter than minimum block length, decrease the number of blocks by 1'
        if block_width < terminal_layout.min_block_width:
            while block_width < terminal_layout.min_block_width:
                max_blocks_x = max_blocks_x - 1
                block_width = math.floor((((quay_length - terminal_layout.traffic_lane) / max_blocks_x) - terminal_layout.traffic_lane) * 100) / 100

        'If block length is larger than the maximum block length, the block length is equal to maximum block length'
        if block_width > terminal_layout.max_block_width:
            block_width = terminal_layout.max_block_width

    elif terminal_layout.stack_equipment == 'rs':
        'Determine number of blocks in x direction'
        max_blocks_x = math.ceil((quay_length - terminal_layout.traffic_lane) / (terminal_layout.max_block_length + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head))

        'Determine block length"'
        block_length = math.floor((((quay_length - terminal_layout.traffic_lane) / max_blocks_x) - terminal_layout.traffic_lane - 2 * terminal_layout.margin_head) * 100) / 100

        'If block length is shorter than minimum block length, decrease the number of blocks by 1'
        if block_length < terminal_layout.min_block_length:
            while block_length < terminal_layout.min_block_length:
                max_blocks_x = max_blocks_x - 1
                block_length = math.floor((((quay_length - terminal_layout.traffic_lane) / max_blocks_x) - terminal_layout.traffic_lane - 2 * terminal_layout.margin_head) * 100) / 100

        'If block length is larger than the maximum block length, the block length is equal to maximum block length'
        if block_length > terminal_layout.max_block_length:
            block_length = terminal_layout.max_block_length

        'Determine block width'
        block_width = terminal_layout.stack.width * terminal_layout.tgs_y

        'Determine number of blocks in row direction'
        max_blocks_y = math.floor((max(prim_yard_y) - terminal_layout.apron_width - terminal_layout.traffic_lane) / (block_width + terminal_layout.operating_space))

    return block_length, block_width, max_blocks_x, max_blocks_y


'Function for checking whether the container block are inside or outside the terminal'


def check_block_inside(block_location, terminal_layout):
    'Check whether point 0 is inside the location'
    if Point(block_location[0]).within(terminal_layout.prim_yard) is True or Point(block_location[0]).touches(terminal_layout.prim_yard) is True:
        block_0_inside = True
    else:
        block_0_inside = False

    'Check whether point 1 is inside the location'
    if Point(block_location[1]).within(terminal_layout.prim_yard) is True or Point(block_location[1]).touches(terminal_layout.prim_yard) is True:
        block_1_inside = True
    else:
        block_1_inside = False

    'Check whether point 2 is inside the location'
    if Point(block_location[2]).within(terminal_layout.prim_yard) is True or Point(block_location[2]).touches(terminal_layout.prim_yard) is True:
        block_2_inside = True
    else:
        block_2_inside = False

    'Check whether point 3 is inside the location'
    if Point(block_location[3]).within(terminal_layout.prim_yard) is True or Point(block_location[3]).touches(terminal_layout.prim_yard) is True:
        block_3_inside = True
    else:
        block_3_inside = False

    return block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location


'Function for checking whether the points are inside or outside the terminal'


def check_points_inside(check_points, terminal_layout):
    'Check whether check_points 0 is inside the location'
    if Point(check_points[0]).within(terminal_layout.prim_yard) is True or Point(check_points[0]).touches(terminal_layout.prim_yard) is True:
        point_1_inside = True
    else:
        point_1_inside = False

    'Check whether check_points 1 is inside the location'
    if Point(check_points[1]).within(terminal_layout.prim_yard) is True or Point(check_points[1]).touches(terminal_layout.prim_yard) is True:
        point_2_inside = True
    else:
        point_2_inside = False

    'Check whether all check_points is inside the container terminal'
    if point_1_inside is True and point_2_inside is True:
        points_inside = True
    else:
        points_inside = False

    return points_inside


'Function for generating the container terminal for RTG'


def rtg_terminal_generation(starting_origin, current_origin, block_length, block_width, block_location, block_reference, first_placement, terminal_layout, laden):
    'Define all parameters in the terminal_layout'

    'Check whether all points of the container block is inside the terminal'
    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

    """Algorithm for the case : There is possibility for : 
    A  container block can be placed in the space on the x- direction

    But, this is an exception for the first container block, because the algorithm should not be repeated
    This exception is indicated by the parameter : m"""

    'Generating blocks in bay direction'
    if block_0_inside is True and block_1_inside is True and block_2_inside is True and block_3_inside is True:
        'Define that it is possible to place on the next container block in bay direction'
        possible_placement = True

        if block_location[0][0] == starting_origin[0] and block_location[0][1] == starting_origin[1] and first_placement == True:

            first_placement = False

            'Define the points that needs to be checked'
            check_points = [[block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1]],
                            [block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1] + block_width]]

            'Check whether the check points is inside the terminal'
            points_inside = check_points_inside(check_points, terminal_layout)

            'If the check points is INSIDE the terminal, then it is POSSIBLE to have a FULL container block in the space on x-direction'
            if points_inside is True:
                while points_inside is True:
                    'Define new current_origin location'
                    current_origin = [check_points[0][0], check_points[0][1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [current_origin[0] + block_length, current_origin[1] + block_width]
                    block_location[3] = [current_origin[0] + block_length, current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Define the points that needs to be checked'
                    check_points = [[block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1]],
                                    [block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1] + block_width]]

                    'Check whether the check points is inside the terminal'
                    points_inside = check_points_inside(check_points, terminal_layout)

                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_width]]

                points_inside = check_points_inside(check_points, terminal_layout)

                if points_inside is True:
                    'Check whether it is possible to INCREASE the block length in x- direction'
                    'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                    while block_0_inside is True and block_1_inside is True:
                        current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                        'Determine the new block location'
                        block_location[0] = [current_origin[0], current_origin[1]]
                        block_location[1] = [current_origin[0], current_origin[1] + block_width]
                        block_location[4] = [current_origin[0], current_origin[1]]

                        'Determine new all points of the container block'
                        block_location = [block_location[0],
                                          block_location[1],
                                          block_location[2],
                                          block_location[3],
                                          block_location[4]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Determine the location after the while loop: Move the current origin by 1 container'
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [block_location[2][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[2][1]]
                    block_location[3] = [block_location[3][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[3][1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                    'If it is NOT POSSIBLE to place a FULL container block on the further row ahead'

                    'If the check points is OUTSIDE the terminal, then it is NOT POSSIBLE to have a FULL container block in the space on x-direction'
            else:
                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_width]]

                points_inside = check_points_inside(check_points, terminal_layout)

                'If it is possible to place a container block that fulfill minimum block length requirement'
                if points_inside is True:

                    block_reference = block_reference + 1

                    'Check whether it is possible to INCREASE the block length in x- direction'
                    'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                    while block_0_inside is True and block_1_inside is True:
                        current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                        'Determine the new block location'
                        block_location[0] = [current_origin[0], current_origin[1]]
                        block_location[1] = [current_origin[0], current_origin[1] + block_width]
                        block_location[4] = [current_origin[0], current_origin[1]]

                        'Determine new all points of the container block'
                        block_location = [block_location[0],
                                          block_location[1],
                                          block_location[2],
                                          block_location[3],
                                          block_location[4]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Determine the location after the while loop: Move the current origin by 1 container'
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [block_location[2][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[2][1]]
                    block_location[3] = [block_location[3][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[3][1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        'Draw the container block'
        if block_location[3][0] - block_location[0][0] > terminal_layout.min_block_length:
            stack = terminal_layout.stack

            # Add the block location to the
            stack.location = block_location
            stack.length_m = math.floor(block_location[3][0] - block_location[0][0])
            stack.width_m = math.floor(block_location[1][1] - block_location[0][1])

            'Define the land use of the block'
            stack.land_use = stack.length_m * stack.width_m
            pavement = stack.pavement
            drainage = stack.drainage

            'Calculates number of container in the container block on bay direction'
            number_of_container_bay = math.floor(stack.length_m / terminal_layout.tgs_x)
            stack.length = number_of_container_bay

            'Define the number of container in the container block on row direction'
            number_of_container_row = math.ceil((stack.width_m - 2 * terminal_layout.equipment_track - terminal_layout.vehicle_track) / terminal_layout.tgs_y)
            stack.width = number_of_container_row

            'Define the capacity for each container block'
            stack.capacity = stack.length * stack.width * stack.height

            'Define the tgs_capacity for each container block'
            stack.tgs_capacity = stack.length * stack.width

            'Determine the number of reefer slots'
            reefer_slots = (terminal_layout.reefer_perc / (terminal_layout.laden_perc + terminal_layout.reefer_perc)) * stack.capacity
            reefer_racks = reefer_slots * stack.reefer_rack

            'Determine capex'
            stack.capex = int((stack.land_use + pavement + drainage) * terminal_layout.land_price + stack.mobilisation + reefer_racks)

            'Determine opex'
            stack.maintenance = int((stack.land_use + pavement + drainage) * stack.maintenance_perc)

            'Define the capacity for the container terminal layout'
            terminal_layout.tgs_capacity = terminal_layout.tgs_capacity + terminal_layout.stack.tgs_capacity

            """'Define clearance space for each container'
            container_clearance_x = ((block_location[3][0] - block_location[0][0]) - number_of_container_bay * laden.length) / (number_of_container_bay - 1)
            container_clearance_y = terminal_layout.tgs_y - laden.width

            'Define new current origin for the algorithm in drawing the TGS'
            container_current_origin = block_location[0][0], block_location[0][1] + terminal_layout.equipment_track + terminal_layout.vehicle_track + container_clearance_y / 2

            p = 1
            q = 1

            for p in range(0, number_of_container_row):
                for q in range(0, number_of_container_bay):
                    'Draw the container'
                    # container = plt.Rectangle(container_current_origin, laden.length, laden.width, fc = "white", ec = "black")
                    # plt.gca().add_patch(container)
                    # above are not active because takes a lot of computational to draw each containers, but it can be activated for visualization

                    'Determine the container location'
                    container_location[0] = [container_current_origin[0], container_current_origin[1]]
                    container_location[1] = [container_current_origin[0], container_current_origin[1] + laden.width]
                    container_location[2] = [container_current_origin[0] + laden.length, container_current_origin[1] + laden.width]
                    container_location[3] = [container_current_origin[0] + laden.length, container_current_origin[1]]
                    container_location[4] = [container_current_origin[0], container_current_origin[1]]

                    'Determine new all points of the container block'
                    container_location = [container_location[0],
                                          container_location[1],
                                          container_location[2],
                                          container_location[3],
                                          container_location[4]]

                    'Add the current container_location to the container_list'
                    container_list.append(container_location)

                    'Add the generated tgs to the capacity'
                    tgs_capacity = tgs_capacity + 1
                    terminal_layout.tgs_capacity = tgs_capacity

                    'Move container to the next location'
                    container_current_origin = container_current_origin[0] + laden.length + container_clearance_x, container_current_origin[1]

                'Move container to the next location'
                q = 0
                container_current_origin = block_location[0][0], container_current_origin[1] + laden.width + container_clearance_y"""

            # Add new laden_stack elements
            terminal_layout.block_list.append(stack)

            # Add new stack location to the stack location list
            terminal_layout.block_location_list.append(block_location)

            # Reset the stack data
            stack = Laden_Stack(**container_defaults.rtg_stack_data)
            terminal_layout.stack = stack

        'Move the current origin to the next block in the bay direction'
        current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head
        current_origin[1] = block_location[3][1]

        'Determine all new points of the container block'
        block_location = [[current_origin[0], current_origin[1]],
                          [current_origin[0], current_origin[1] + block_width],
                          [current_origin[0] + block_length, current_origin[1] + block_width],
                          [current_origin[0] + block_length, current_origin[1]],
                          [current_origin[0], current_origin[1]]]

    else:
        """        
        Algorithm for the case : Container cannot place a new container block in bay direction, it moves the current_origin to the location of the new container block in row direction
        If block_location[1] and block_location[2] is outisde of the terminal --> for rectangular case'
        If block_location[1] and block_location [2] and block_location [3] is outisde of the terminal --> for triangular & trapezoidal case
        If block_location[0] and block location[2] and block_location[3] is outside of the terminal --> for reversed triangular & trapezoidal case
        """

        if (block_1_inside is False and block_2_inside is False) or (block_1_inside is False and block_2_inside is False and block_3_inside is False) or (block_0_inside is False and block_2_inside is False and block_3_inside is False):
            'Define that it is possible to place on the next container block in bay direction'
            possible_placement = False

            'Define new current_origin point to the next container block in row direction'
            current_origin = [terminal_layout.block_location_list[block_reference][0][0], current_origin[1] + block_width + terminal_layout.bypass_lane]

            'Determine the new block location on the new row direction'
            block_location[0] = [terminal_layout.block_location_list[block_reference][0][0], current_origin[1]]
            block_location[1] = [terminal_layout.block_location_list[block_reference][1][0], current_origin[1] + block_width]
            block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width]
            block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
            block_location[4] = [terminal_layout.block_location_list[block_reference][0][0], current_origin[1]]

            'Determine new all points of the container block'
            block_location = [block_location[0],
                              block_location[1],
                              block_location[2],
                              block_location[3],
                              block_location[4]]

            'Check whether all pointsthe point in block is inside the terminal'
            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            """The coding below this row, is the coding in determining the container block 
            after it moves to the new container block location in row direction

            The x-location of the new container block is the same as the previous row
            Therefore, it needs to be checked wether a container block can be placed in this location"""

            'If the container block cannot be placed at all at this location (block_location[0] and block_location[1] and block_location[2] is outside the terminal'
            if block_0_inside is False and block_1_inside is False and block_2_inside is False:
                'Define new current_origin on the next container block in bay direction'
                current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head

                'Define new value of block_reference, to indicate the starting point for the algorithm in generating new container block in row direction'
                block_reference = block_reference + 1

                'Determine all new points of the container block'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_width],
                                  [current_origin[0] + block_length, current_origin[1] + block_width],
                                  [current_origin[0] + block_length, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether all points of the container block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                """The algorithm for the case of moving current_origin to the next container block in bay direction ends here
                Next is the algorithm in defining container block location"""

            # Moving current origin to the left to check whether there is a space to place the block

            """Algorithm for the case : There is possibility for : 
            (a) A full container block (with full block length) can be placed in the space on the x-direction
            (b) The container block length can be INCREASED to the x-direction

            It happens if block_location[0] and block_location[1] is inside the terminal"""
            if block_0_inside is True and block_1_inside is True:

                'Check for possibility of (a)'
                'Define the points that needs to be checked'
                check_points = [[block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1]],
                                [block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1] + block_width]]

                'Check whether it is actually possible to place a full container block on the further row ahead'
                'A new container block might be possible to be placed in the space on x- direction'

                'If It is POSSIBLE to place a FULL container block on the further row ahead'
                prim_yard_x, prim_yard_y = terminal_layout.prim_yard.exterior.xy
                if min(prim_yard_x) <= check_points[0][0]:
                    'Define the points that needs to be checked'
                    check_points = [[block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1]],
                                    [block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1] + block_width]]

                    'Check whether the check points is inside the terminal'
                    points_inside = check_points_inside(check_points, terminal_layout)

                    'If the check points is INSIDE the terminal, then it is POSSIBLE to have a FULL container block in the space on x-direction'
                    if points_inside is True:
                        while points_inside is True:
                            'Define new current_origin location'
                            current_origin = [check_points[0][0], check_points[0][1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_width]
                            block_location[2] = [current_origin[0] + block_length, current_origin[1] + block_width]
                            block_location[3] = [current_origin[0] + block_length, current_origin[1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Define the points that needs to be checked'
                            check_points = [[block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1]],
                                            [block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1] + block_width]]

                            'Check whether the check points is inside the terminal'
                            points_inside = check_points_inside(check_points, terminal_layout)

                        'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                        check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                        [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_width]]

                        points_inside = check_points_inside(check_points, terminal_layout)

                        if points_inside is True:
                            'Check whether it is possible to INCREASE the block length in x- direction'
                            'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                            while block_0_inside is True and block_1_inside is True:
                                current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                                'Determine the new block location'
                                block_location[0] = [current_origin[0], current_origin[1]]
                                block_location[1] = [current_origin[0], current_origin[1] + block_width]
                                block_location[4] = [current_origin[0], current_origin[1]]

                                'Determine new all points of the container block'
                                block_location = [block_location[0],
                                                  block_location[1],
                                                  block_location[2],
                                                  block_location[3],
                                                  block_location[4]]

                                'Check whether all points of the container block is inside the terminal'
                                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Determine the location after the while loop: Move the current origin by 1 container'
                            current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_width]
                            block_location[2] = [block_location[2][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[2][1]]
                            block_location[3] = [block_location[3][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[3][1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                            'If it is NOT POSSIBLE to place a FULL container block on the further row ahead'

                            'If the check points is OUTSIDE the terminal, then it is NOT POSSIBLE to have a FULL container block in the space on x-direction'
                    else:
                        'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                        check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                        [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_width]]

                        points_inside = check_points_inside(check_points, terminal_layout)

                        'If it is possible to place a container block that fulfill minimum block length requirement'
                        if points_inside is True:

                            'Check whether it is possible to INCREASE the block length in x- direction'
                            'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                            while block_0_inside is True and block_1_inside is True:
                                current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                                'Determine the new block location'
                                block_location[0] = [current_origin[0], current_origin[1]]
                                block_location[1] = [current_origin[0], current_origin[1] + block_width]
                                block_location[4] = [current_origin[0], current_origin[1]]

                                'Determine new all points of the container block'
                                block_location = [block_location[0],
                                                  block_location[1],
                                                  block_location[2],
                                                  block_location[3],
                                                  block_location[4]]

                                'Check whether all points of the container block is inside the terminal'
                                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Determine the location after the while loop: Move the current origin by 1 container'
                            current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_width]
                            block_location[2] = [block_location[2][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[2][1]]
                            block_location[3] = [block_location[3][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[3][1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                    'If it is NOT POSSIBLE to place a FULL container block on the further row ahead'
                else:
                    'Check whether it is possible to INCREASE the block length in x- direction'
                    'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'

                    'Check whether the right side already fulfill the requirments for rtg_safety_clearance'
                    check_points = [[block_location[0][0] - terminal_layout.margin_head, block_location[0][1]],
                                    [block_location[0][0] - terminal_layout.margin_head, block_location[0][1] + block_width]]

                    points_inside = check_points_inside(check_points, terminal_layout)

                    while block_0_inside is True and block_1_inside is True and points_inside is True:
                        current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                        'Determine the new block location'
                        block_location[0] = [current_origin[0], current_origin[1]]
                        block_location[1] = [current_origin[0], current_origin[1] + block_width]
                        block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width]
                        block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                        block_location[4] = [current_origin[0], current_origin[1]]

                        'Determine new all points of the container block'
                        block_location = [block_location[0],
                                          block_location[1],
                                          block_location[2],
                                          block_location[3],
                                          block_location[4]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                        'Check whether the right side already fulfill the requirments for rtg_safety_clearance'
                        check_points = [[block_location[0][0] - terminal_layout.margin_head, block_location[0][0]],
                                        [block_location[0][0] - terminal_layout.margin_head, block_location[0][0] + block_width]]

                        points_inside = check_points_inside(check_points, terminal_layout)

                    'Determine the location after the while loop: Move the current origin by 1 container'
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width]
                    block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

            'Algorithm for the case : Cannot place a new container block, because it already reaches outside of the terminal'
            if block_1_inside is False and block_2_inside is False:
                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

            """Algorithm for the case : There is possibility for : 
            (a) The container block length should be DECREASED to the x+ direction in order to place the container block
            (b) The decreasing container block starts on the LEFT side of the container block

            It happens if block_location[0] or block_location[1] is outside the terminal"""
            if block_0_inside is False or block_1_inside is False:

                'Algorithm for : Decreasing the block length until it reaches the edge of the terminal in x+ direction'
                while block_0_inside is False or block_1_inside is False:
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width]
                    block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        'Algorithm for anomaly condition where the block_location[3][0] is less than block_location[0][0]'
        if block_location[3][0] < block_location[0][0]:

            possible_placement = False

            current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head

            block_location = [[current_origin[0], current_origin[1]],
                              [current_origin[0], current_origin[1] + block_width],
                              [current_origin[0] + block_length, current_origin[1] + block_width],
                              [current_origin[0] + block_length, current_origin[1]],
                              [current_origin[0], current_origin[1]]]

            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            block_reference = block_reference + 1

            if block_0_inside is False or block_1_inside is False:
                while block_0_inside is False or block_1_inside is False:
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    block_location = [[current_origin[0], current_origin[1]],
                                      [current_origin[0], current_origin[1] + block_width],
                                      [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width],
                                      [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]],
                                      [current_origin[0], current_origin[1]]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            if block_1_inside is False and block_2_inside is False:
                possible_placement = False
                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        """
            Algorithm for the (special) case : Reversed triangular
            If block_location[0] and block_location[1] is outside the terminal --> reversed triangular case
        """

        if block_0_inside is False or block_1_inside is False:
            while block_0_inside is False or block_1_inside is False:
                current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                'Determine the new block location'
                block_location[0] = [current_origin[0], current_origin[1]]
                block_location[1] = [current_origin[0], current_origin[1] + block_width]
                block_location[2] = block_location[2]
                block_location[3] = block_location[3]
                block_location[4] = [current_origin[0], current_origin[1]]

                'Determine new all points of the container block'
                block_location = [block_location[0],
                                  block_location[1],
                                  block_location[2],
                                  block_location[3],
                                  block_location[4]]

                'Check whether all points of the container block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            """The algorithm for the case of moving current_origin to the next container block in bay direction ends here
            Next is the algorithm in defining container block location"""

            possible_placement = True

            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        if block_0_inside is True and block_1_inside is True and block_2_inside is True and block_3_inside is True:
            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        else:
            """Algorithm for the case : There is possibility for : 
            (a) The container block length can be DECREASED to the x- direction in order to place the container block
            (b) The decreasing container block starts on the RIGHT side of the container block

            It happens if block_location[0] or block_location[1] is outside the terminal"""

            'Check whether it is possible to place a container block that fulfill minimum block length requirement'
            'If it is POSSIBLE to fulfill minimum block length requirement'
            if block_location[3][0] - block_location[0][0] > terminal_layout.min_block_length:

                'Check whether the right side already fulfill the requirments for rtg_safety_clearance'
                check_points = [[block_location[3][0] + terminal_layout.margin_head, block_location[3][1]],
                                [block_location[3][0] + terminal_layout.margin_head, block_location[3][1] + block_width]]

                points_inside = check_points_inside(check_points, terminal_layout)

                'Algorithm for : Decreasing the block length until it reaches the edge of the terminal in x- direction'
                while (block_2_inside is False or block_3_inside is False) and points_inside is False:
                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [block_location[2][0] - terminal_layout.tgs_x, current_origin[1] + block_width]
                    block_location[3] = [block_location[3][0] - terminal_layout.tgs_x, current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Check whether the right side already fulfill the requirments for rtg_safety_clearance'
                    check_points = [[block_location[3][0] + terminal_layout.margin_head, block_location[3][1]],
                                    [block_location[3][0] + terminal_layout.margin_head, block_location[3][1] + block_width]]

                    points_inside = check_points_inside(check_points, terminal_layout)

            else:
                'If it is NOT POSSIBLE to fulfill minimum block length requirement'
                'Define that it is possible to place on the next container block in bay direction'
                possible_placement = False

                'Determine the new location for current_origin and block_location'
                current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head

                'Determine the new block location'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_width],
                                  [current_origin[0] + block_length, current_origin[1] + block_width],
                                  [current_origin[0] + block_length, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether all points of the container block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

            if current_origin[0] == terminal_layout.block_location_list[0][0][0]:
                possible_placement = True

            else:
                possible_placement = True

    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout


'Function for generating the container terminal for RMG'


def rmg_terminal_generation(starting_origin, current_origin, block_length, block_width, block_location, block_reference, first_placement, terminal_layout, laden):
    'Check whether the point in block is inside the terminal'
    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

    """Algorithm for the case : There is possibility for : 
    A  container block can be placed in the space on the x- direction

    But, this is an exception for the first container block, because the algorithm should not be repeated
    This exception is indicated by the parameter : m"""

    if block_location[0][0] == starting_origin[0] and block_location[0][1] == starting_origin[1] and first_placement == True:

        'Parameters for exception case : first container block'
        first_placement = False

        'Check whether it is possible to place a container block that fulfill minimum block length requirement'
        'Check point on the top of the container block'
        check_points_top = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                            [block_location[3][0], block_location[3][1] + terminal_layout.min_block_length]]

        points_inside_top = check_points_inside(check_points_top, terminal_layout)

        'Check point on the top of the container block'
        check_points_bot = [[block_location[1][0], block_location[1][1] - terminal_layout.min_block_length],
                            [block_location[2][0], block_location[2][1] - terminal_layout.min_block_length]]

        points_inside_bot = check_points_inside(check_points_bot, terminal_layout)

        if (points_inside_top is True and block_0_inside is True and block_3_inside is True) or (points_inside_bot is True and block_1_inside is True and block_2_inside is True):
            while (points_inside_top is True and block_0_inside is True and block_3_inside is True) or (points_inside_bot is True and block_1_inside is True and block_2_inside is True):
                'Move the current origin to the previous block in the bay direction'
                current_origin[0] = block_location[0][0] - block_width - terminal_layout.margin_parallel

                'Determine all new points of the container block'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                'Check point on the top of the container block'
                check_points_top = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                                    [block_location[3][0], block_location[3][1] + terminal_layout.min_block_length]]

                points_inside_top = check_points_inside(check_points_top, terminal_layout)

                'Check point on the top of the container block'
                check_points_bot = [[block_location[1][0], block_location[1][1] - terminal_layout.min_block_length],
                                    [block_location[2][0], block_location[2][1] - terminal_layout.min_block_length]]

                points_inside_bot = check_points_inside(check_points_bot, terminal_layout)

                'Check whether all points of the point in block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            'Determine the location after the while loop: Move the current origin by 1 block'
            current_origin[0] = block_location[0][0] + block_width + terminal_layout.margin_parallel

            'Determine all new points of the container block'
            block_location = [[current_origin[0], current_origin[1]],
                              [current_origin[0], current_origin[1] + block_length],
                              [current_origin[0] + block_width, current_origin[1] + block_length],
                              [current_origin[0] + block_width, current_origin[1]],
                              [current_origin[0], current_origin[1]]]

            'Check whether all points of the point in block is inside the terminal'
            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

    'Case 1 : Check all block_location, whether all is inside'
    if block_0_inside is True and block_1_inside is True and block_2_inside is True and block_3_inside is True:

        'Define that it is possible to place on the next container block in bay direction'
        possible_placement = True

        'Draw the container block'
        if block_location[1][1] - block_location[0][1] > terminal_layout.min_block_length:
            stack = terminal_layout.stack

            # Add the block location to the
            stack.location = block_location
            stack.length_m = math.floor(block_location[1][1] - block_location[0][1])
            stack.width_m = math.floor(block_location[3][0] - block_location[0][0])

            'Define the land use of the block'
            stack.land_use = stack.length_m * stack.width_m
            pavement = stack.pavement
            drainage = stack.drainage

            'Calculates number of container in the container block on bay direction'
            number_of_container_bay = math.floor(stack.width_m / terminal_layout.tgs_x)
            stack.width = number_of_container_bay

            'Define the number of container in the container block on row direction'
            number_of_container_row = math.floor(stack.length_m / terminal_layout.tgs_y)
            stack.length = number_of_container_row

            'Define the capacity for each container block'
            stack.capacity = stack.length * stack.width * stack.height

            'Define the tgs_capacity for each container block'
            stack.tgs_capacity = stack.length * stack.width

            'Determine the number of reefer slots'
            reefer_slots = (terminal_layout.reefer_perc / (terminal_layout.laden_perc + terminal_layout.reefer_perc)) * stack.capacity
            reefer_racks = reefer_slots * stack.reefer_rack

            'Determine capex'
            stack.capex = int((stack.land_use + pavement + drainage) * terminal_layout.land_price + stack.mobilisation + reefer_racks)

            'Determine opex'
            stack.maintenance = int((stack.land_use + pavement + drainage) * stack.maintenance_perc)

            'Define the capacity for the container terminal layout'
            terminal_layout.tgs_capacity = terminal_layout.tgs_capacity + terminal_layout.stack.tgs_capacity

            """'Define clearance space for each container'
            container_clearance_x = terminal_layout.tgs_x - container_x
            container_clearance_y = ((block_location[1][1] - block_location[0][1] - 2 * terminal_layout.length_buffer) - number_of_container_bay * container_y) / (number_of_container_bay - 1)

            'Define new current origin for the algorithm in drawing the TGS'
            container_current_origin = block_location[0][0] + terminal_layout.equipment_track + container_clearance_x / 2, block_location[0][1] + terminal_layout.length_buffer

            p = 0
            q = 0

            for p in range(0, number_of_container_row):
                for q in range(0, number_of_container_bay):
                    # container = plt.Rectangle(container_current_origin, container_x, container_y, fc = "white", ec = "black")
                    # plt.gca().add_patch(container)
                    # above are not active because takes a lot of computational to draw each containers, but it can be activated for visualization

                    'Determine the container location'
                    container_location[0] = [container_current_origin[0], container_current_origin[1]]
                    container_location[1] = [container_current_origin[0], container_current_origin[1] + container_y]
                    container_location[2] = [container_current_origin[0] + container_x, container_current_origin[1] + container_y]
                    container_location[3] = [container_current_origin[0], +container_x, container_current_origin[1]]
                    container_location[4] = [container_current_origin[0], container_current_origin[1]]

                    'Determine new all points of the container block'
                    container_location = [container_location[0],
                                          container_location[1],
                                          container_location[2],
                                          container_location[3],
                                          container_location[4]]

                    'Add the current container_location to the container_list'
                    container_list.append(container_location)

                    'Add the generated container block to the capacity'
                    tgs_capacity = tgs_capacity + 1

                    'Move container to the next location'
                    container_current_origin = container_current_origin[0], container_current_origin[1] + container_y + container_clearance_y

                'Move container to the next location'
                q = 0
                container_current_origin = container_current_origin[0] + container_x + container_clearance_x, block_location[0][1] + terminal_layout.length_buffer"""

            # Add new laden_stack elements
            terminal_layout.block_list.append(terminal_layout.stack)

            # Add new stack location to the stack location list
            terminal_layout.block_location_list.append(block_location)

            # Reset the stack data
            stack = Laden_Stack(**container_defaults.rmg_stack_data)
            terminal_layout.stack = stack

        'Move the current origin to the next block in the bay direction'
        current_origin[0] = block_location[3][0] + terminal_layout.margin_parallel

        'Determine all new points of the container block'
        block_location = [[current_origin[0], current_origin[1]],
                          [current_origin[0], current_origin[1] + block_length],
                          [current_origin[0] + block_width, current_origin[1] + block_length],
                          [current_origin[0] + block_width, current_origin[1]],
                          [current_origin[0], current_origin[1]]]

        return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

    'Case 2 : Check block_location[1] or block_location[2], whether it is inside and whether it is still possible to place a container block that fulfill minimum block length'
    if block_1_inside is False or block_2_inside is False:
        'Check whether it is possible to place a container block that fulfill minimum block length requirement'
        'Check point on the top of the container block'
        check_points_top = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                            [block_location[3][0], block_location[3][1] + terminal_layout.min_block_length]]

        points_inside_top = check_points_inside(check_points_top, terminal_layout)

        if points_inside_top is True:
            'Algorithm to decrease the block length on the top side'
            while block_1_inside is False or block_2_inside is False:
                'Determine the new block location on the new row direction'
                block_location[0] = block_location[0]
                block_location[1] = [block_location[1][0], block_location[1][1] - terminal_layout.tgs_y]
                block_location[2] = [block_location[2][0], block_location[2][1] - terminal_layout.tgs_y]
                block_location[3] = block_location[3]
                block_location[4] = block_location[4]

                'Determine new all points of the container block'
                block_location = [block_location[0],
                                  block_location[1],
                                  block_location[2],
                                  block_location[3],
                                  block_location[4]]

                'Check whether all points of the point in block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            if block_0_inside is True and block_1_inside is True and block_2_inside is True and block_3_inside is True:
                'Define that it is possible to place on the next container block in bay direction'
                possible_placement = True

                'Draw the container block'
                if block_location[1][1] - block_location[0][1] > terminal_layout.min_block_length:
                    stack = terminal_layout.stack

                    # Add the block location to the
                    stack.location = block_location
                    stack.length_m = math.floor(block_location[1][1] - block_location[0][1])
                    stack.width_m = math.floor(block_location[3][0] - block_location[0][0])

                    'Define the land use of the block'
                    stack.land_use = stack.length_m * stack.width_m
                    pavement = stack.pavement
                    drainage = stack.drainage

                    'Calculates number of container in the container block on bay direction'
                    number_of_container_bay = math.floor(stack.width_m / terminal_layout.tgs_x)
                    stack.width = number_of_container_bay

                    'Define the number of container in the container block on row direction'
                    number_of_container_row = math.floor(stack.length_m / terminal_layout.tgs_y)
                    stack.length = number_of_container_row

                    'Define the capacity for each container block'
                    stack.capacity = stack.length * stack.width * stack.height

                    'Define the tgs_capacity for each container block'
                    stack.tgs_capacity = stack.length * stack.width

                    'Determine the number of reefer slots'
                    reefer_slots = (terminal_layout.reefer_perc / (terminal_layout.laden_perc + terminal_layout.reefer_perc)) * stack.capacity
                    reefer_racks = reefer_slots * stack.reefer_rack

                    'Determine capex'
                    stack.capex = int((stack.land_use + pavement + drainage) * terminal_layout.land_price + stack.mobilisation + reefer_racks)

                    'Determine opex'
                    stack.maintenance = int((stack.land_use + pavement + drainage) * stack.maintenance_perc)

                    'Define the capacity for the container terminal layout'
                    terminal_layout.tgs_capacity = terminal_layout.tgs_capacity + terminal_layout.stack.tgs_capacity

                    """'Define clearance space for each container'
                    container_clearance_x = terminal_layout.tgs_x - container_x
                    container_clearance_y = ((block_location[1][1] - block_location[0][1] - 2 * terminal_layout.length_buffer) - number_of_container_bay * container_y) / (number_of_container_bay - 1)

                    'Define new current origin for the algorithm in drawing the TGS'
                    container_current_origin = block_location[0][0] + terminal_layout.equipment_track + container_clearance_x / 2, block_location[0][1] + terminal_layout.length_buffer

                    p = 0
                    q = 0

                    for p in range(0, number_of_container_row):
                        for q in range(0, number_of_container_bay):
                            # container = plt.Rectangle(container_current_origin, container_x, container_y, fc = "white", ec = "black")
                            # plt.gca().add_patch(container)
                            # above are not active because takes a lot of computational to draw each containers, but it can be activated for visualization

                            'Determine the container location'
                            container_location[0] = [container_current_origin[0], container_current_origin[1]]
                            container_location[1] = [container_current_origin[0], container_current_origin[1] + container_y]
                            container_location[2] = [container_current_origin[0] + container_x, container_current_origin[1] + container_y]
                            container_location[3] = [container_current_origin[0], +container_x, container_current_origin[1]]
                            container_location[4] = [container_current_origin[0], container_current_origin[1]]

                            'Determine new all points of the container block'
                            container_location = [container_location[0],
                                                  container_location[1],
                                                  container_location[2],
                                                  container_location[3],
                                                  container_location[4]]

                            'Add the current container_location to the container_list'
                            container_list.append(container_location)

                            'Add the generated container block to the capacity'
                            tgs_capacity = tgs_capacity + 1

                            'Move container to the next location'
                            container_current_origin = container_current_origin[0], container_current_origin[1] + container_y + container_clearance_y

                        'Move container to the next location'
                        q = 0
                        container_current_origin = container_current_origin[0] + container_x + container_clearance_x, block_location[0][1] + terminal_layout.length_buffer"""

                    # Add new laden_stack elements
                    terminal_layout.block_list.append(terminal_layout.stack)

                    # Add new stack location to the stack location list
                    terminal_layout.block_location_list.append(block_location)

                    # Reset the stack data
                    stack = Laden_Stack(**container_defaults.rmg_stack_data)
                    terminal_layout.stack = stack

                'Move the current origin to the next block in the bay direction'
                current_origin[0] = block_location[3][0] + terminal_layout.margin_parallel

                'Determine all new points of the container block'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        else:
            'trial : parameters that is the indicator for the while loop to stop if the loop is already reached 20 times --> stops '
            trial = 0

            while points_inside_top is False and trial in range(0, 20):
                trial = trial + 1

                'Move the current origin to the next block in the bay direction'
                current_origin[0] = block_location[3][0] + terminal_layout.margin_parallel

                'Determine all new points of the container block'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                'Check point on the top of the container block'
                check_points_top = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                                    [block_location[3][0] + block_width, block_location[3][1] + terminal_layout.min_block_length]]

                points_inside_top = check_points_inside(check_points_top, terminal_layout)

                'Check whether all points of the point in block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            if trial == 20:
                'Define that it is possible to place on the next container block in bay direction'
                possible_placement = False

                'Define new current_origin point to the next container block in row direction'
                current_origin = [terminal_layout.block_location_list[0][0][0], current_origin[1] + block_length + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head]

                block_location[0] = [terminal_layout.block_location_list[0][0][0], current_origin[1]]
                block_location[1] = [terminal_layout.block_location_list[0][1][0], current_origin[1] + block_length]
                block_location[2] = [terminal_layout.block_location_list[0][2][0], current_origin[1] + block_length]
                block_location[3] = [terminal_layout.block_location_list[0][3][0], current_origin[1]]
                block_location[4] = [terminal_layout.block_location_list[0][0][0], current_origin[1]]

                'Check whether all points of the point in block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                """Algorithm for the case : There is possibility for : 
                A  container block can be placed in the space on the x- direction"""

                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                'Check point on the top of the container block'
                check_points_top = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                                    [block_location[3][0], block_location[3][1] + terminal_layout.min_block_length]]

                points_inside_top = check_points_inside(check_points_top, terminal_layout)

                'Check point on the top of the container block'
                check_points_bot = [[block_location[1][0], block_location[1][1] - terminal_layout.min_block_length],
                                    [block_location[2][0], block_location[2][1] - terminal_layout.min_block_length]]

                points_inside_bot = check_points_inside(check_points_bot, terminal_layout)

                while (points_inside_top is True and block_0_inside is True and block_3_inside is True) or (points_inside_bot is True and block_1_inside is True and block_2_inside is True):
                    'Move the current origin to the previous block in the bay direction'
                    current_origin[0] = block_location[0][0] - block_width - terminal_layout.margin_parallel

                    'Determine all new points of the container block'
                    block_location = [[current_origin[0], current_origin[1]],
                                      [current_origin[0], current_origin[1] + block_length],
                                      [current_origin[0] + block_width, current_origin[1] + block_length],
                                      [current_origin[0] + block_width, current_origin[1]],
                                      [current_origin[0], current_origin[1]]]

                    'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                    'Check point on the top of the container block'
                    check_points_top = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                                        [block_location[3][0], block_location[3][1] + terminal_layout.min_block_length]]

                    points_inside_top = check_points_inside(check_points_top, terminal_layout)

                    'Check point on the top of the container block'
                    check_points_bot = [[block_location[1][0], block_location[1][1] - terminal_layout.min_block_length],
                                        [block_location[2][0], block_location[2][1] - terminal_layout.min_block_length]]

                    points_inside_bot = check_points_inside(check_points_bot, terminal_layout)

                    'Check whether all points of the point in block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                'Determine the location after the while loop: Move the current origin by 1 block'
                current_origin[0] = block_location[0][0] + block_width + terminal_layout.margin_parallel

                'Determine all new points of the container block'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether all points of the point in block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            else:
                'Define that it is possible to place on the next container block in bay direction'
                possible_placement = True

            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

    'Case 3 : Check block_location[0] or block_location[3], whether it is inside and whether it is still possible to place a container block that fulfill minimum block length'
    if block_0_inside is False or block_3_inside is False:

        'Check whether it is possible to place a container block that fulfill minimum block length requirement'
        'Check point on the bottom of the container block'
        check_points_bot = [[block_location[1][0], block_location[1][1] - terminal_layout.min_block_length],
                            [block_location[2][0], block_location[2][1] - terminal_layout.min_block_length]]

        points_inside_bot = check_points_inside(check_points_bot, terminal_layout)

        if points_inside_bot is True:
            while block_0_inside is False or block_3_inside is False:
                'Determine the new block location on the new row direction'
                block_location[0] = [block_location[0][0], block_location[0][1] + + terminal_layout.tgs_y]
                block_location[1] = [block_location[1][0], block_location[1][1]]
                block_location[2] = [block_location[2][0], block_location[2][1]]
                block_location[3] = [block_location[3][0], block_location[3][1] + terminal_layout.tgs_y]
                block_location[4] = [block_location[4][0], block_location[4][1]]

                'Determine new all points of the container block'
                block_location = [block_location[0],
                                  block_location[1],
                                  block_location[2],
                                  block_location[3],
                                  block_location[4]]

                'Check whether all points in block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            if block_0_inside is True and block_1_inside is True and block_2_inside is True and block_3_inside is True:
                'Define that it is possible to place on the next container block in bay direction'
                possible_placement = True

                'Draw the container block'
                if block_location[1][1] - block_location[0][1] > terminal_layout.min_block_length:
                    stack = terminal_layout.stack

                    # Add the block location to the
                    stack.location = block_location
                    stack.length_m = math.floor(block_location[1][1] - block_location[0][1])
                    stack.width_m = math.floor(block_location[3][0] - block_location[0][0])

                    'Define the land use of the block'
                    stack.land_use = stack.length_m * stack.width_m
                    pavement = stack.pavement
                    drainage = stack.drainage

                    'Calculates number of container in the container block on bay direction'
                    number_of_container_bay = math.floor(stack.width_m / terminal_layout.tgs_x)
                    stack.width = number_of_container_bay

                    'Define the number of container in the container block on row direction'
                    number_of_container_row = math.floor(stack.length_m / terminal_layout.tgs_y)
                    stack.length = number_of_container_row

                    'Define the capacity for each container block'
                    stack.capacity = stack.length * stack.width * stack.height

                    'Define the tgs_capacity for each container block'
                    stack.tgs_capacity = stack.length * stack.width

                    'Determine the number of reefer slots'
                    reefer_slots = (terminal_layout.reefer_perc / (terminal_layout.laden_perc + terminal_layout.reefer_perc)) * stack.capacity
                    reefer_racks = reefer_slots * stack.reefer_rack

                    'Determine capex'
                    stack.capex = int((stack.land_use + pavement + drainage) * terminal_layout.land_price + stack.mobilisation + reefer_racks)

                    'Determine opex'
                    stack.maintenance = int((stack.land_use + pavement + drainage) * stack.maintenance_perc)

                    'Define the capacity for the container terminal layout'
                    terminal_layout.tgs_capacity = terminal_layout.tgs_capacity + terminal_layout.stack.tgs_capacity

                    """'Define clearance space for each container'
                    container_clearance_x = terminal_layout.tgs_x - container_x
                    container_clearance_y = ((block_location[1][1] - block_location[0][1] - 2 * terminal_layout.length_buffer) - number_of_container_bay * container_y) / (number_of_container_bay - 1)

                    'Define new current origin for the algorithm in drawing the TGS'
                    container_current_origin = block_location[0][0] + terminal_layout.equipment_track + container_clearance_x / 2, block_location[0][1] + terminal_layout.length_buffer

                    p = 0
                    q = 0

                    for p in range(0, number_of_container_row):
                        for q in range(0, number_of_container_bay):
                            # container = plt.Rectangle(container_current_origin, container_x, container_y, fc = "white", ec = "black")
                            # plt.gca().add_patch(container)
                            # above are not active because takes a lot of computational to draw each containers, but it can be activated for visualization

                            'Determine the container location'
                            container_location[0] = [container_current_origin[0], container_current_origin[1]]
                            container_location[1] = [container_current_origin[0], container_current_origin[1] + container_y]
                            container_location[2] = [container_current_origin[0] + container_x, container_current_origin[1] + container_y]
                            container_location[3] = [container_current_origin[0], +container_x, container_current_origin[1]]
                            container_location[4] = [container_current_origin[0], container_current_origin[1]]

                            'Determine new all points of the container block'
                            container_location = [container_location[0],
                                                  container_location[1],
                                                  container_location[2],
                                                  container_location[3],
                                                  container_location[4]]

                            'Add the current container_location to the container_list'
                            container_list.append(container_location)

                            'Add the generated container block to the capacity'
                            tgs_capacity = tgs_capacity + 1

                            'Move container to the next location'
                            container_current_origin = container_current_origin[0], container_current_origin[1] + container_y + container_clearance_y

                        'Move container to the next location'
                        q = 0
                        container_current_origin = container_current_origin[0] + container_x + container_clearance_x, block_location[0][1] + terminal_layout.length_buffer"""

                    # Add new laden_stack elements
                    terminal_layout.block_list.append(terminal_layout.stack)

                    # Add new stack location to the stack location list
                    terminal_layout.block_location_list.append(block_location)

                    # Reset the stack data
                    stack = Laden_Stack(**container_defaults.rmg_stack_data)
                    terminal_layout.stack = stack

                'Move the current origin to the next block in the bay direction'
                current_origin[0] = block_location[3][0] + terminal_layout.margin_parallel

                'Determine all new points of the container block'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        else:
            'trial : parameters that is the indicator for the while loop to stop if the loop is already reached 20 times --> stops '
            trial = 0

            while points_inside_bot is False and trial in range(0, 20):
                trial = trial + 1

                'Move the current origin to the next block in the bay direction'
                current_origin[0] = block_location[3][0] + terminal_layout.margin_parallel

                'Determine all new points of the container block'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                'Check point on the bottom of the container block'
                check_points_bot = [[block_location[1][0], block_location[1][1] - terminal_layout.min_block_length],
                                    [block_location[2][0], block_location[2][1] - terminal_layout.min_block_length]]

                points_inside_bot = check_points_inside(check_points_bot, terminal_layout)

                'Check whether all points of the point in block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            if trial == 20:
                'Define that it is possible to place on the next container block in bay direction'
                possible_placement = False

                'Define new current_origin point to the next container block in row direction'
                current_origin = [terminal_layout.block_location_list[0][0][0], current_origin[1] + block_length + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head]

                block_location[0] = [terminal_layout.block_location_list[0][0][0], current_origin[1]]
                block_location[1] = [terminal_layout.block_location_list[0][1][0], current_origin[1] + block_length]
                block_location[2] = [terminal_layout.block_location_list[0][2][0], current_origin[1] + block_length]
                block_location[3] = [terminal_layout.block_location_list[0][3][0], current_origin[1]]
                block_location[4] = [terminal_layout.block_location_list[0][0][0], current_origin[1]]

                'Check whether all points of the point in block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                """Algorithm for the case : There is possibility for : 
                A  container block can be placed in the space on the x- direction"""

                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                'Check point on the top of the container block'
                check_points_top = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                                    [block_location[3][0], block_location[3][1] + terminal_layout.min_block_length]]

                points_inside_top = check_points_inside(check_points_top, terminal_layout)

                'Check point on the top of the container block'
                check_points_bot = [[block_location[1][0], block_location[1][1] - terminal_layout.min_block_length],
                                    [block_location[2][0], block_location[2][1] - terminal_layout.min_block_length]]

                points_inside_bot = check_points_inside(check_points_bot, terminal_layout)

                while (points_inside_top is True and block_0_inside is True and block_3_inside is True) or (points_inside_bot is True and block_1_inside is True and block_2_inside is True):
                    'Move the current origin to the previous block in the bay direction'
                    current_origin[0] = block_location[0][0] - block_width - terminal_layout.margin_parallel

                    'Determine all new points of the container block'
                    block_location = [[current_origin[0], current_origin[1]],
                                      [current_origin[0], current_origin[1] + block_length],
                                      [current_origin[0] + block_width, current_origin[1] + block_length],
                                      [current_origin[0] + block_width, current_origin[1]],
                                      [current_origin[0], current_origin[1]]]

                    'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                    'Check point on the top of the container block'
                    check_points_top = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                                        [block_location[3][0], block_location[3][1] + terminal_layout.min_block_length]]

                    points_inside_top = check_points_inside(check_points_top, terminal_layout)

                    'Check point on the top of the container block'
                    check_points_bot = [[block_location[1][0], block_location[1][1] - terminal_layout.min_block_length],
                                        [block_location[2][0], block_location[2][1] - terminal_layout.min_block_length]]

                    points_inside_bot = check_points_inside(check_points_bot, terminal_layout)

                    'Check whether all points of the point in block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                'Determine the location after the while loop: Move the current origin by 1 block'
                current_origin[0] = block_location[0][0] + block_width + terminal_layout.margin_parallel

                'Determine all new points of the container block'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether all points of the point in block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            else:
                'Define that it is possible to place on the next container block in bay direction'
                possible_placement = True

            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout


'Function for generating the container terminal for SC'


def sc_terminal_generation(starting_origin, current_origin, block_length, block_width, block_location, block_reference, first_placement, terminal_layout, laden):
    'Check whether all points of the container block is inside the terminal'
    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

    """Algorithm for the case : There is possibility for : 
        A  container block can be placed in the space on the x- direction

        But, this is an exception for the first container block, because the algorithm should not be repeated
        This exception is indicated by the parameter : m"""

    'Generating blocks in bay direction'
    if block_0_inside is True and block_1_inside is True and block_2_inside is True and block_3_inside is True:
        'Define that it is possible to place on the next container block in bay direction'
        possible_placement = True

        if block_location[0][0] == starting_origin[0] and block_location[0][1] == starting_origin[1] and first_placement == True:

            first_placement = False

            'Define the points that needs to be checked'
            check_points = [[block_location[0][0] - block_width - terminal_layout.traffic_lane, block_location[0][1]],
                            [block_location[0][0] - block_width - terminal_layout.traffic_lane, block_location[0][1] + block_length]]

            'Check whether the check points is inside the terminal'
            points_inside = check_points_inside(check_points, terminal_layout)

            'If the check points is INSIDE the terminal, then it is POSSIBLE to have a FULL container block in the space on x-direction'
            if points_inside is True:
                while points_inside is True:
                    'Define new current_origin location'
                    current_origin = [check_points[0][0], check_points[0][1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_length]
                    block_location[2] = [current_origin[0] + block_width, current_origin[1] + block_length]
                    block_location[3] = [current_origin[0] + block_width, current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Define the points that needs to be checked'
                    check_points = [[block_location[0][0] - block_width - terminal_layout.traffic_lane, block_location[0][1]],
                                    [block_location[0][0] - block_width - terminal_layout.traffic_lane, block_location[0][1] + block_length]]

                    'Check whether the check points is inside the terminal'
                    points_inside = check_points_inside(check_points, terminal_layout)

                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_length]]

                points_inside = check_points_inside(check_points, terminal_layout)

                if points_inside is True:
                    'Check whether it is possible to INCREASE the block length in x- direction'
                    'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                    while block_0_inside is True and block_1_inside is True:
                        current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                        'Determine the new block location'
                        block_location[0] = [current_origin[0], current_origin[1]]
                        block_location[1] = [current_origin[0], current_origin[1] + block_length]
                        block_location[4] = [current_origin[0], current_origin[1]]

                        'Determine new all points of the container block'
                        block_location = [block_location[0],
                                          block_location[1],
                                          block_location[2],
                                          block_location[3],
                                          block_location[4]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Determine the location after the while loop: Move the current origin by 1 container'
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_length]
                    block_location[2] = [block_location[2][0] - block_width - terminal_layout.traffic_lane, block_location[2][1]]
                    block_location[3] = [block_location[3][0] - block_width - terminal_layout.traffic_lane, block_location[3][1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                    'If it is NOT POSSIBLE to place a FULL container block on the further row ahead'

                    'If the check points is OUTSIDE the terminal, then it is NOT POSSIBLE to have a FULL container block in the space on x-direction'
            else:
                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_length]]

                points_inside = check_points_inside(check_points, terminal_layout)

                'If it is possible to place a container block that fulfill minimum block length requirement'
                if points_inside is True:

                    block_reference = block_reference + 1

                    'Check whether it is possible to INCREASE the block length in x- direction'
                    'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                    while block_0_inside is True and block_1_inside is True:
                        current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                        'Determine the new block location'
                        block_location[0] = [current_origin[0], current_origin[1]]
                        block_location[1] = [current_origin[0], current_origin[1] + block_length]
                        block_location[4] = [current_origin[0], current_origin[1]]

                        'Determine new all points of the container block'
                        block_location = [block_location[0],
                                          block_location[1],
                                          block_location[2],
                                          block_location[3],
                                          block_location[4]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Determine the location after the while loop: Move the current origin by 1 container'
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_length]
                    block_location[2] = [block_location[2][0] - block_width - terminal_layout.traffic_lane, block_location[2][1]]
                    block_location[3] = [block_location[3][0] - block_width - terminal_layout.traffic_lane, block_location[3][1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        'Draw the container block'
        if block_location[3][0] - block_location[0][0] > terminal_layout.min_block_width and block_location[1][1] - block_location[0][1] > terminal_layout.min_block_length:
            stack = terminal_layout.stack

            # Add the block location, length, and width to the stack
            stack.location = block_location
            stack.length_m = math.floor(block_location[3][0] - block_location[0][0])
            stack.width_m = math.floor(block_location[1][1] - block_location[0][1])

            'Define the land use of the block'
            stack.land_use = stack.length_m * stack.width_m
            pavement = stack.pavement
            drainage = stack.drainage

            'Calculates number of container in the container block on bay direction'
            number_of_container_bay = math.floor(stack.width_m / terminal_layout.tgs_x)
            stack.width = number_of_container_bay

            'Define the number of container in the container block on row direction'
            number_of_container_row = math.floor(stack.length_m / terminal_layout.tgs_y)
            stack.length = number_of_container_row

            'Define the capacity for each container block'
            stack.capacity = stack.length * stack.width * stack.height

            'Define the tgs_capacity for each container block'
            stack.tgs_capacity = stack.length * stack.width

            'Determine the number of reefer slots'
            reefer_slots = (terminal_layout.reefer_perc / (terminal_layout.laden_perc + terminal_layout.reefer_perc)) * stack.capacity
            reefer_racks = reefer_slots * stack.reefer_rack

            'Determine capex'
            stack.capex = int((stack.land_use + pavement + drainage) * terminal_layout.land_price + stack.mobilisation + reefer_racks)

            'Determine opex'
            stack.maintenance = int((stack.land_use + pavement + drainage) * stack.maintenance_perc)

            'Define the capacity for the container terminal layout'
            terminal_layout.tgs_capacity = terminal_layout.tgs_capacity + terminal_layout.stack.tgs_capacity

            """'Define clearance space for each container'
            container_clearance_x = ((block_location[3][0] - block_location[0][0]) - number_of_container_bay * laden.length) / (number_of_container_bay - 1)
            container_clearance_y = terminal_layout.tgs_y - laden.width

            'Define new current origin for the algorithm in drawing the TGS'
            container_current_origin = block_location[0][0], block_location[0][1] + terminal_layout.equipment_track + terminal_layout.vehicle_track + container_clearance_y / 2

            p = 1
            q = 1

            for p in range(0, number_of_container_row):
                for q in range(0, number_of_container_bay):
                    'Draw the container'
                    # container = plt.Rectangle(container_current_origin, laden.length, laden.width, fc = "white", ec = "black")
                    # plt.gca().add_patch(container)
                    # above are not active because takes a lot of computational to draw each containers, but it can be activated for visualization

                    'Determine the container location'
                    container_location[0] = [container_current_origin[0], container_current_origin[1]]
                    container_location[1] = [container_current_origin[0], container_current_origin[1] + laden.width]
                    container_location[2] = [container_current_origin[0] + laden.length, container_current_origin[1] + laden.width]
                    container_location[3] = [container_current_origin[0] + laden.length, container_current_origin[1]]
                    container_location[4] = [container_current_origin[0], container_current_origin[1]]

                    'Determine new all points of the container block'
                    container_location = [container_location[0],
                                          container_location[1],
                                          container_location[2],
                                          container_location[3],
                                          container_location[4]]

                    'Add the current container_location to the container_list'
                    container_list.append(container_location)

                    'Add the generated tgs to the capacity'
                    tgs_capacity = tgs_capacity + 1
                    terminal_layout.tgs_capacity = tgs_capacity

                    'Move container to the next location'
                    container_current_origin = container_current_origin[0] + laden.length + container_clearance_x, container_current_origin[1]

                'Move container to the next location'
                q = 0
                container_current_origin = block_location[0][0], container_current_origin[1] + laden.width + container_clearance_y"""

            # Add new laden_stack elements
            terminal_layout.block_list.append(terminal_layout.stack)

            # Add new stack location to the stack location list
            terminal_layout.block_location_list.append(block_location)

            # Reset the stack data
            stack = Laden_Stack(**container_defaults.sc_stack_data)
            terminal_layout.stack = stack

        'Move the current origin to the next block in the bay direction'
        current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane

        'Determine all new points of the container block'
        block_location = [[current_origin[0], current_origin[1]],
                          [current_origin[0], current_origin[1] + block_length],
                          [current_origin[0] + block_width, current_origin[1] + block_length],
                          [current_origin[0] + block_width, current_origin[1]],
                          [current_origin[0], current_origin[1]]]

    else:
        """        
        Algorithm for the case : Container cannot place a new container block in bay direction, it moves the current_origin to the location of the new container block in row direction
        If block_location[1] and block_location[2] is outisde of the terminal --> for rectangular case'
        If block_location[1] and block_location [2] and block_location [3] is outisde of the terminal --> for triangular & trapezoidal case
        If block_location[0] and block location[2] and block_location[3] is outside of the terminal --> for reversed triangular & trapezoidal case
        """

        if (block_1_inside is False and block_2_inside is False) or (
                block_1_inside is False and block_2_inside is False and block_3_inside is False) or (block_0_inside is False and block_2_inside is False and block_3_inside is False):

            'Define that it is possible to place on the next container block in bay direction'
            possible_placement = False

            'Define new current_origin point to the next container block in row direction'
            current_origin = [terminal_layout.block_location_list[block_reference][0][0], current_origin[1] + block_length + terminal_layout.traffic_lane]

            'Determine the new block location on the new row direction'
            block_location[0] = [terminal_layout.block_location_list[block_reference][0][0], current_origin[1]]
            block_location[1] = [terminal_layout.block_location_list[block_reference][1][0], current_origin[1] + block_length]
            block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_length]
            block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
            block_location[4] = [terminal_layout.block_location_list[block_reference][0][0], current_origin[1]]

            'Determine new all points of the container block'
            block_location = [block_location[0],
                              block_location[1],
                              block_location[2],
                              block_location[3],
                              block_location[4]]

            'Check whether all pointsthe point in block is inside the terminal'
            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            """The coding below this row, is the coding in determining the container block 
            after it moves to the new container block location in row direction

            The x-location of the new container block is the same as the previous row
            Therefore, it needs to be checked wether a container block can be placed in this location"""

            'If the container block cannot be placed at all at this location (block_location[0] and block_location[1] and block_location[2] is outside the terminal'
            if block_1_inside is False and block_2_inside is False:
                if block_0_inside is True or block_3_inside is True:
                    while block_1_inside is False and block_2_inside is False:
                        'Define new current_origin on the next container block in bay direction'
                        current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane

                        'Define new value of block_reference, to indicate the starting point for the algorithm in generating new container block in row direction'
                        block_reference = block_reference + 1

                        'Determine all new points of the container block'
                        block_location = [[current_origin[0], current_origin[1]],
                                          [current_origin[0], current_origin[1] + block_length],
                                          [current_origin[0] + block_width, current_origin[1] + block_length],
                                          [current_origin[0] + block_width, current_origin[1]],
                                          [current_origin[0], current_origin[1]]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                        """The algorithm for the case of moving current_origin to the next container block in bay direction ends here
                        Next is the algorithm in defining container block location"""

            # Moving current origin to the left to check whether there is a space to place the block

            """Algorithm for the case : There is possibility for : 
            (a) A full container block (with full block length) can be placed in the space on the x-direction
            (b) The container block length can be INCREASED to the x-direction

            It happens if block_location[0] and block_location[1] is inside the terminal"""
            if block_0_inside is True and block_1_inside is True:

                'Check for possibility of (a)'
                'Define the points that needs to be checked'
                check_points = [[block_location[0][0] - terminal_layout.traffic_lane - block_width, block_location[0][1]],
                                [block_location[0][0] - terminal_layout.traffic_lane - block_width, block_location[0][1] + block_length]]

                'Check whether it is actually possible to place a full container block on the further row ahead'
                'A new container block might be possible to be placed in the space on x- direction'

                'If It is POSSIBLE to place a FULL container block on the further row ahead'
                prim_yard_x, prim_yard_y = terminal_layout.prim_yard.exterior.xy
                if min(prim_yard_x) <= check_points[0][0]:
                    'Define the points that needs to be checked'
                    check_points = [[block_location[0][0] - block_width - terminal_layout.traffic_lane, block_location[0][1]],
                                    [block_location[0][0] - block_width - terminal_layout.traffic_lane, block_location[0][1] + block_length]]

                    'Check whether the check points is inside the terminal'
                    points_inside = check_points_inside(check_points, terminal_layout)

                    'If the check points is INSIDE the terminal, then it is POSSIBLE to have a FULL container block in the space on x-direction'
                    if points_inside is True:
                        while points_inside is True:
                            'Define new current_origin location'
                            current_origin = [check_points[0][0], check_points[0][1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_length]
                            block_location[2] = [current_origin[0] + block_width, current_origin[1] + block_length]
                            block_location[3] = [current_origin[0] + block_width, current_origin[1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Define the points that needs to be checked'
                            check_points = [[block_location[0][0] - block_width - terminal_layout.traffic_lane, block_location[0][1]],
                                            [block_location[0][0] - block_width - terminal_layout.traffic_lane, block_location[0][1] + block_length]]

                            'Check whether the check points is inside the terminal'
                            points_inside = check_points_inside(check_points, terminal_layout)

                        'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                        check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                        [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_length]]

                        points_inside = check_points_inside(check_points, terminal_layout)

                        if points_inside is True:
                            'Check whether it is possible to INCREASE the block length in x- direction'
                            'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                            while block_0_inside is True and block_1_inside is True:
                                current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                                'Determine the new block location'
                                block_location[0] = [current_origin[0], current_origin[1]]
                                block_location[1] = [current_origin[0], current_origin[1] + block_length]
                                block_location[4] = [current_origin[0], current_origin[1]]

                                'Determine new all points of the container block'
                                block_location = [block_location[0],
                                                  block_location[1],
                                                  block_location[2],
                                                  block_location[3],
                                                  block_location[4]]

                                'Check whether all points of the container block is inside the terminal'
                                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Determine the location after the while loop: Move the current origin by 1 container'
                            current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_length]
                            block_location[2] = [block_location[2][0] - block_width - terminal_layout.traffic_lane, block_location[2][1]]
                            block_location[3] = [block_location[3][0] - block_width - terminal_layout.traffic_lane, block_location[3][1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                            'If it is NOT POSSIBLE to place a FULL container block on the further row ahead'

                            'If the check points is OUTSIDE the terminal, then it is NOT POSSIBLE to have a FULL container block in the space on x-direction'
                    else:
                        'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                        check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                        [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_length]]

                        points_inside = check_points_inside(check_points, terminal_layout)

                        'If it is possible to place a container block that fulfill minimum block length requirement'
                        if points_inside is True:

                            'Check whether it is possible to INCREASE the block length in x- direction'
                            'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                            while block_0_inside is True and block_1_inside is True:
                                current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                                'Determine the new block location'
                                block_location[0] = [current_origin[0], current_origin[1]]
                                block_location[1] = [current_origin[0], current_origin[1] + block_length]
                                block_location[4] = [current_origin[0], current_origin[1]]

                                'Determine new all points of the container block'
                                block_location = [block_location[0],
                                                  block_location[1],
                                                  block_location[2],
                                                  block_location[3],
                                                  block_location[4]]

                                'Check whether all points of the container block is inside the terminal'
                                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Determine the location after the while loop: Move the current origin by 1 container'
                            current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_length]
                            block_location[2] = [block_location[2][0] - block_width - terminal_layout.traffic_lane, block_location[2][1]]
                            block_location[3] = [block_location[3][0] - block_width - terminal_layout.traffic_lane, block_location[3][1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                    'If it is NOT POSSIBLE to place a FULL container block on the further row ahead'
                else:
                    'Check whether it is possible to INCREASE the block length in x- direction'
                    'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'

                    'Check whether the right side already fulfill the requirments for terminal_layout.traffic_lane'
                    check_points = [[block_location[0][0] - terminal_layout.traffic_lane, block_location[0][1]],
                                    [block_location[0][0] - terminal_layout.traffic_lane, block_location[0][1] + block_length]]

                    points_inside = check_points_inside(check_points, terminal_layout)

                    if block_0_inside is True and block_1_inside is True and points_inside is True:
                        while block_0_inside is True and block_1_inside is True and points_inside is True:
                            current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_length]
                            block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_length]
                            block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Check whether the right side already fulfill the requirments for terminal_layout.traffic_lane'
                            check_points = [[block_location[0][0] - terminal_layout.traffic_lane, block_location[0][0]],
                                            [block_location[0][0] - terminal_layout.traffic_lane, block_location[0][0] + block_width]]

                            points_inside = check_points_inside(check_points, terminal_layout)

                        'Determine the location after the while loop: Move the current origin by 1 container'
                        current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                        'Determine the new block location'
                        block_location[0] = [current_origin[0], current_origin[1]]
                        block_location[1] = [current_origin[0], current_origin[1] + block_length]
                        block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_length]
                        block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                        block_location[4] = [current_origin[0], current_origin[1]]

                        'Determine new all points of the container block'
                        block_location = [block_location[0],
                                          block_location[1],
                                          block_location[2],
                                          block_location[3],
                                          block_location[4]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

            'Algorithm for the case : Cannot place a new container block, because it already reaches outside of the terminal'
            if block_1_inside is False and block_2_inside is False:
                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

            """Algorithm for the case : There is possibility for : 
            (a) The container block length should be DECREASED to the x+ direction in order to place the container block
            (b) The decreasing container block starts on the LEFT side of the container block

            It happens if block_location[0] or block_location[1] is outside the terminal"""
            if block_0_inside is False or block_1_inside is False:

                'Check whether it is fulfilling minimum block width'
                'Define the points that needs to be checked'
                check_points = [[block_location[3][0] - terminal_layout.min_block_width, block_location[3][1]],
                                [block_location[3][0] - terminal_layout.min_block_width, block_location[3][1] + block_length]]

                'Check whether the check points is inside the terminal'
                points_inside = check_points_inside(check_points, terminal_layout)

                if points_inside is False:

                    'Check whether it is fulfilling minimum block length'
                    'Define the points that needs to be checked'
                    check_points = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                                    [block_location[0][0] + block_width, block_location[0][1] + terminal_layout.min_block_length]]

                    'Check whether the check points is inside the terminal'
                    points_inside = check_points_inside(check_points, terminal_layout)

                    if points_inside is True:
                        while block_0_inside is False or block_1_inside is False:
                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [block_location[1][0], block_location[1][1] - terminal_layout.tgs_y]
                            block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], block_location[1][1] - terminal_layout.tgs_y]
                            block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                'Algorithm for : Decreasing the block length until it reaches the edge of the terminal in x+ direction'
                while block_0_inside is False or block_1_inside is False:
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_length]
                    block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_length]
                    block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        'Algorithm for anomaly condition where the block_location[3][0] is less than block_location[0][0]'
        if block_location[3][0] < block_location[0][0]:

            possible_placement = False

            current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane

            block_location = [[current_origin[0], current_origin[1]],
                              [current_origin[0], current_origin[1] + block_length],
                              [current_origin[0] + block_width, current_origin[1] + block_length],
                              [current_origin[0] + block_width, current_origin[1]],
                              [current_origin[0], current_origin[1]]]

            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            block_reference = block_reference + 1

            if block_0_inside is False or block_1_inside is False:
                while block_0_inside is False or block_1_inside is False:
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    block_location = [[current_origin[0], current_origin[1]],
                                      [current_origin[0], current_origin[1] + block_length],
                                      [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_length],
                                      [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]],
                                      [current_origin[0], current_origin[1]]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            if block_1_inside is False and block_2_inside is False:
                possible_placement = False
                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        """
            Algorithm for the (special) case : Reversed triangular
            If block_location[0] and block_location[1] is outside the terminal --> reversed triangular case
        """

        if block_0_inside is False or block_1_inside is False:
            while block_0_inside is False or block_1_inside is False:
                current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                'Determine the new block location'
                block_location[0] = [current_origin[0], current_origin[1]]
                block_location[1] = [current_origin[0], current_origin[1] + block_length]
                block_location[2] = block_location[2]
                block_location[3] = block_location[3]
                block_location[4] = [current_origin[0], current_origin[1]]

                'Determine new all points of the container block'
                block_location = [block_location[0],
                                  block_location[1],
                                  block_location[2],
                                  block_location[3],
                                  block_location[4]]

                'Check whether all points of the container block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            """The algorithm for the case of moving current_origin to the next container block in bay direction ends here
            Next is the algorithm in defining container block location"""

            possible_placement = True

            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        if block_0_inside is True and block_1_inside is True and block_2_inside is True and block_3_inside is True:
            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        else:
            """Algorithm for the case : There is possibility for : 
            (a) The container block length can be DECREASED to the x- direction in order to place the container block
            (b) The decreasing container block starts on the RIGHT side of the container block

            It happens if block_location[0] or block_location[1] is outside the terminal"""

            'Check whether it is possible to place a container block that fulfill minimum block length requirement'
            'If it is POSSIBLE to fulfill minimum block length requirement'

            if block_location[3][0] - block_location[0][0] > terminal_layout.min_block_length:

                possible_placement = True

                'Check whether the right side already fulfill the requirments for sc_safety_clearance'
                check_points = [[block_location[3][0] + terminal_layout.traffic_lane, block_location[3][1]],
                                [block_location[3][0] + terminal_layout.traffic_lane, block_location[3][1] + block_length]]

                points_inside = check_points_inside(check_points, terminal_layout)

                if points_inside is False:

                    'Check whether it is fulfilling minimum block width'
                    'Define the points that needs to be checked'
                    check_points = [[block_location[0][0] + terminal_layout.min_block_width, block_location[0][1]],
                                    [block_location[0][0] + terminal_layout.min_block_width, block_location[0][1] + block_length]]

                    'Check whether the check points is inside the terminal'
                    points_inside = check_points_inside(check_points, terminal_layout)

                    if points_inside is True:

                        'Check whether it is fulfilling minimum block length'
                        'Define the points that needs to be checked'
                        check_points = [[block_location[0][0], block_location[0][1] + terminal_layout.min_block_length],
                                        [block_location[0][0] + block_width, block_location[0][1] + terminal_layout.min_block_length]]

                        'Check whether the check points is inside the terminal'
                        points_inside = check_points_inside(check_points, terminal_layout)

                        if points_inside is True:
                            while block_1_inside is False or block_2_inside is False:
                                'Determine the new block location'
                                block_location[0] = [current_origin[0], current_origin[1]]
                                block_location[1] = [block_location[1][0], block_location[1][1] - terminal_layout.tgs_y]
                                block_location[2] = [block_location[2][0], block_location[2][1] - terminal_layout.tgs_y]
                                block_location[3] = [block_location[3][0], current_origin[1]]
                                block_location[4] = [current_origin[0], current_origin[1]]

                                'Determine new all points of the container block'
                                block_location = [block_location[0],
                                                  block_location[1],
                                                  block_location[2],
                                                  block_location[3],
                                                  block_location[4]]

                                'Check whether all points of the container block is inside the terminal'
                                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                        'Algorithm for : Decreasing the block length until it reaches the edge of the terminal in x- direction'
                        while (block_2_inside is False or block_3_inside is False):
                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_length]
                            block_location[2] = [block_location[2][0] - terminal_layout.tgs_x, current_origin[1] + block_length]
                            block_location[3] = [block_location[3][0] - terminal_layout.tgs_x, current_origin[1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    else:
                        'If it is NOT POSSIBLE to fulfill minimum block length requirement'

                        'Determine the new location for current_origin and block_location'
                        current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane

                        'Determine the new block location'
                        block_location = [[current_origin[0], current_origin[1]],
                                          [current_origin[0], current_origin[1] + block_length],
                                          [current_origin[0] + block_width, current_origin[1] + block_length],
                                          [current_origin[0] + block_width, current_origin[1]],
                                          [current_origin[0], current_origin[1]]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                        return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                else:
                    'If it is NOT POSSIBLE to fulfill minimum block length requirement'

                    'Determine the new location for current_origin and block_location'
                    current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane

                    'Determine the new block location'
                    block_location = [[current_origin[0], current_origin[1]],
                                      [current_origin[0], current_origin[1] + block_length],
                                      [current_origin[0] + block_width, current_origin[1] + block_length],
                                      [current_origin[0] + block_width, current_origin[1]],
                                      [current_origin[0], current_origin[1]]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

            else:
                'If it is NOT POSSIBLE to fulfill minimum block length requirement'

                'Determine the new location for current_origin and block_location'
                current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane

                'Determine the new block location'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1] + block_length],
                                  [current_origin[0] + block_width, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether all points of the container block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout


'Function for generating the container terminal for RS'


def rs_terminal_generation(starting_origin, current_origin, block_length, block_width, block_location, block_reference, first_placement, terminal_layout, laden):
    'Check whether all points of the container block is inside the terminal'
    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

    """Algorithm for the case : There is possibility for : 
        A  container block can be placed in the space on the x- direction

        But, this is an exception for the first container block, because the algorithm should not be repeated
        This exception is indicated by the parameter : m"""

    'Generating blocks in bay direction'
    if block_0_inside is True and block_1_inside is True and block_2_inside is True and block_3_inside is True:
        'Define that it is possible to place on the next container block in bay direction'
        possible_placement = True

        if block_location[0][0] == starting_origin[0] and block_location[0][1] == starting_origin[1] and first_placement == True:

            first_placement = False

            'Define the points that needs to be checked'
            check_points = [[block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1]],
                            [block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1] + block_width]]

            'Check whether the check points is inside the terminal'
            points_inside = check_points_inside(check_points, terminal_layout)

            'If the check points is INSIDE the terminal, then it is POSSIBLE to have a FULL container block in the space on x-direction'
            if points_inside is True:
                while points_inside is True:
                    'Define new current_origin location'
                    current_origin = [check_points[0][0], check_points[0][1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [current_origin[0] + block_length, current_origin[1] + block_width]
                    block_location[3] = [current_origin[0] + block_length, current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Define the points that needs to be checked'
                    check_points = [[block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1]],
                                    [block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1] + block_width]]

                    'Check whether the check points is inside the terminal'
                    points_inside = check_points_inside(check_points, terminal_layout)

                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_width]]

                points_inside = check_points_inside(check_points, terminal_layout)

                if points_inside is True:
                    'Check whether it is possible to INCREASE the block length in x- direction'
                    'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                    while block_0_inside is True and block_1_inside is True:
                        current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                        'Determine the new block location'
                        block_location[0] = [current_origin[0], current_origin[1]]
                        block_location[1] = [current_origin[0], current_origin[1] + block_width]
                        block_location[4] = [current_origin[0], current_origin[1]]

                        'Determine new all points of the container block'
                        block_location = [block_location[0],
                                          block_location[1],
                                          block_location[2],
                                          block_location[3],
                                          block_location[4]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Determine the location after the while loop: Move the current origin by 1 container'
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [block_location[2][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[2][1]]
                    block_location[3] = [block_location[3][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[3][1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                    'If it is NOT POSSIBLE to place a FULL container block on the further row ahead'

                    'If the check points is OUTSIDE the terminal, then it is NOT POSSIBLE to have a FULL container block in the space on x-direction'
            else:
                'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_width]]

                points_inside = check_points_inside(check_points, terminal_layout)

                'If it is possible to place a container block that fulfill minimum block length requirement'
                if points_inside is True:

                    block_reference = block_reference + 1

                    'Check whether it is possible to INCREASE the block length in x- direction'
                    'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                    while block_0_inside is True and block_1_inside is True:
                        current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                        'Determine the new block location'
                        block_location[0] = [current_origin[0], current_origin[1]]
                        block_location[1] = [current_origin[0], current_origin[1] + block_width]
                        block_location[4] = [current_origin[0], current_origin[1]]

                        'Determine new all points of the container block'
                        block_location = [block_location[0],
                                          block_location[1],
                                          block_location[2],
                                          block_location[3],
                                          block_location[4]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Determine the location after the while loop: Move the current origin by 1 container'
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [block_location[2][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[2][1]]
                    block_location[3] = [block_location[3][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[3][1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        'Draw the container block'
        if block_location[3][0] - block_location[0][0] > terminal_layout.min_block_length:
            stack = terminal_layout.stack

            # Add the block location to the
            terminal_layout.stack.location = block_location
            terminal_layout.stack.length_m = math.floor(block_location[3][0] - block_location[0][0])
            terminal_layout.stack.width_m = math.floor(block_location[1][1] - block_location[0][1])

            'Define the land use of the block'
            stack.land_use = stack.length_m * stack.width_m
            pavement = stack.pavement
            drainage = stack.drainage

            'Calculates number of container in the container block on bay direction'
            number_of_container_bay = math.floor(terminal_layout.stack.length_m / terminal_layout.tgs_x)
            terminal_layout.stack.length = number_of_container_bay

            'Define the number of container in the container block on row direction'
            number_of_container_row = math.ceil(terminal_layout.stack.width_m / terminal_layout.tgs_y)
            terminal_layout.stack.width = number_of_container_row

            'Define the capacity for each container block'
            stack.capacity = stack.length * stack.width * stack.height

            'Define the tgs_capacity for each container block'
            stack.tgs_capacity = stack.length * stack.width

            'Determine the number of reefer slots'
            reefer_slots = (terminal_layout.reefer_perc / (terminal_layout.laden_perc + terminal_layout.reefer_perc)) * stack.capacity
            reefer_racks = reefer_slots * stack.reefer_rack

            'Determine capex'
            stack.capex = int((stack.land_use + pavement + drainage) * terminal_layout.land_price + stack.mobilisation + reefer_racks)

            'Determine opex'
            stack.maintenance = int((stack.land_use + pavement + drainage) * stack.maintenance_perc)

            'Define the capacity for the container terminal layout'
            terminal_layout.tgs_capacity = terminal_layout.tgs_capacity + terminal_layout.stack.tgs_capacity

            """'Define clearance space for each container'
            container_clearance_x = ((block_location[3][0] - block_location[0][0]) - number_of_container_bay * laden.length) / (number_of_container_bay - 1)
            container_clearance_y = terminal_layout.tgs_y - laden.width

            'Define new current origin for the algorithm in drawing the TGS'
            container_current_origin = block_location[0][0], block_location[0][1] + terminal_layout.equipment_track + terminal_layout.vehicle_track + container_clearance_y / 2

            p = 1
            q = 1

            for p in range(0, number_of_container_row):
                for q in range(0, number_of_container_bay):
                    'Draw the container'
                    # container = plt.Rectangle(container_current_origin, laden.length, laden.width, fc = "white", ec = "black")
                    # plt.gca().add_patch(container)
                    # above are not active because takes a lot of computational to draw each containers, but it can be activated for visualization

                    'Determine the container location'
                    container_location[0] = [container_current_origin[0], container_current_origin[1]]
                    container_location[1] = [container_current_origin[0], container_current_origin[1] + laden.width]
                    container_location[2] = [container_current_origin[0] + laden.length, container_current_origin[1] + laden.width]
                    container_location[3] = [container_current_origin[0] + laden.length, container_current_origin[1]]
                    container_location[4] = [container_current_origin[0], container_current_origin[1]]

                    'Determine new all points of the container block'
                    container_location = [container_location[0],
                                          container_location[1],
                                          container_location[2],
                                          container_location[3],
                                          container_location[4]]

                    'Add the current container_location to the container_list'
                    container_list.append(container_location)

                    'Add the generated tgs to the capacity'
                    tgs_capacity = tgs_capacity + 1
                    terminal_layout.tgs_capacity = tgs_capacity

                    'Move container to the next location'
                    container_current_origin = container_current_origin[0] + laden.length + container_clearance_x, container_current_origin[1]

                'Move container to the next location'
                q = 0
                container_current_origin = block_location[0][0], container_current_origin[1] + laden.width + container_clearance_y"""

            # Add new laden_stack elements
            terminal_layout.block_list.append(terminal_layout.stack)

            # Add new stack location to the stack location list
            terminal_layout.block_location_list.append(block_location)

            # Reset the stack data
            stack = Laden_Stack(**container_defaults.rs_stack_data)
            terminal_layout.stack = stack

        'Move the current origin to the next block in the bay direction'
        current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head

        'Determine all new points of the container block'
        block_location = [[current_origin[0], current_origin[1]],
                          [current_origin[0], current_origin[1] + block_width],
                          [current_origin[0] + block_length, current_origin[1] + block_width],
                          [current_origin[0] + block_length, current_origin[1]],
                          [current_origin[0], current_origin[1]]]

    else:
        """        
        Algorithm for the case : Container cannot place a new container block in bay direction, it moves the current_origin to the location of the new container block in row direction
        If block_location[1] and block_location[2] is outisde of the terminal --> for rectangular case'
        If block_location[1] and block_location [2] and block_location [3] is outisde of the terminal --> for triangular & trapezoidal case
        If block_location[0] and block location[2] and block_location[3] is outside of the terminal --> for reversed triangular & trapezoidal case
        """

        if (block_1_inside is False and block_2_inside is False) or (block_1_inside is False and block_2_inside is False and block_3_inside is False) or (
                block_0_inside is False and block_2_inside is False and block_3_inside is False):
            'Define that it is possible to place on the next container block in bay direction'
            possible_placement = False

            'Define new current_origin point to the next container block in row direction'
            current_origin = [terminal_layout.block_location_list[block_reference][0][0], current_origin[1] + block_width + terminal_layout.operating_space]

            'Determine the new block location on the new row direction'
            block_location[0] = [terminal_layout.block_location_list[block_reference][0][0], current_origin[1]]
            block_location[1] = [terminal_layout.block_location_list[block_reference][1][0], current_origin[1] + block_width]
            block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width]
            block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
            block_location[4] = [terminal_layout.block_location_list[block_reference][0][0], current_origin[1]]

            'Determine new all points of the container block'
            block_location = [block_location[0],
                              block_location[1],
                              block_location[2],
                              block_location[3],
                              block_location[4]]

            'Check whether all pointsthe point in block is inside the terminal'
            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            """The coding below this row, is the coding in determining the container block 
            after it moves to the new container block location in row direction

            The x-location of the new container block is the same as the previous row
            Therefore, it needs to be checked wether a container block can be placed in this location"""

            'If the container block cannot be placed at all at this location (block_location[0] and block_location[1] and block_location[2] is outside the terminal'
            if block_0_inside is False and block_1_inside is False and block_2_inside is False:
                'Define new current_origin on the next container block in bay direction'
                current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head

                'Define new value of block_reference, to indicate the starting point for the algorithm in generating new container block in row direction'
                block_reference = block_reference + 1

                'Determine all new points of the container block'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_width],
                                  [current_origin[0] + block_length, current_origin[1] + block_width],
                                  [current_origin[0] + block_length, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether all points of the container block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                """The algorithm for the case of moving current_origin to the next container block in bay direction ends here
                Next is the algorithm in defining container block location"""

            # Moving current origin to the left to check whether there is a space to place the block

            """Algorithm for the case : There is possibility for : 
            (a) A full container block (with full block length) can be placed in the space on the x-direction
            (b) The container block length can be INCREASED to the x-direction

            It happens if block_location[0] and block_location[1] is inside the terminal"""
            if block_0_inside is True and block_1_inside is True:

                'Check for possibility of (a)'
                'Define the points that needs to be checked'
                check_points = [[block_location[0][0] - terminal_layout.traffic_lane - 2 * terminal_layout.margin_head - block_length, block_location[0][1]],
                                [block_location[0][0] - terminal_layout.traffic_lane - 2 * terminal_layout.margin_head - block_length, block_location[0][1] + block_width]]

                'Check whether it is actually possible to place a full container block on the further row ahead'
                'A new container block might be possible to be placed in the space on x- direction'

                'If It is POSSIBLE to place a FULL container block on the further row ahead'
                prim_yard_x, prim_yard_y = terminal_layout.prim_yard.exterior.xy
                if min(prim_yard_x) <= check_points[0][0]:
                    'Define the points that needs to be checked'
                    check_points = [[block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1]],
                                    [block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1] + block_width]]

                    'Check whether the check points is inside the terminal'
                    points_inside = check_points_inside(check_points, terminal_layout)

                    'If the check points is INSIDE the terminal, then it is POSSIBLE to have a FULL container block in the space on x-direction'
                    if points_inside is True:
                        while points_inside is True:
                            'Define new current_origin location'
                            current_origin = [check_points[0][0], check_points[0][1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_width]
                            block_location[2] = [current_origin[0] + block_length, current_origin[1] + block_width]
                            block_location[3] = [current_origin[0] + block_length, current_origin[1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Define the points that needs to be checked'
                            check_points = [[block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1]],
                                            [block_location[0][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[0][1] + block_width]]

                            'Check whether the check points is inside the terminal'
                            points_inside = check_points_inside(check_points, terminal_layout)

                        'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                        check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                        [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_width]]

                        points_inside = check_points_inside(check_points, terminal_layout)

                        if points_inside is True:
                            'Check whether it is possible to INCREASE the block length in x- direction'
                            'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                            while block_0_inside is True and block_1_inside is True:
                                current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                                'Determine the new block location'
                                block_location[0] = [current_origin[0], current_origin[1]]
                                block_location[1] = [current_origin[0], current_origin[1] + block_width]
                                block_location[4] = [current_origin[0], current_origin[1]]

                                'Determine new all points of the container block'
                                block_location = [block_location[0],
                                                  block_location[1],
                                                  block_location[2],
                                                  block_location[3],
                                                  block_location[4]]

                                'Check whether all points of the container block is inside the terminal'
                                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Determine the location after the while loop: Move the current origin by 1 container'
                            current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_width]
                            block_location[2] = [block_location[2][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[2][1]]
                            block_location[3] = [block_location[3][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[3][1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                            'If it is NOT POSSIBLE to place a FULL container block on the further row ahead'

                            'If the check points is OUTSIDE the terminal, then it is NOT POSSIBLE to have a FULL container block in the space on x-direction'
                    else:
                        'Check whether it is possible to place a container block that fulfill minimum block length requirement'
                        check_points = [[block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1]],
                                        [block_location[0][0] - terminal_layout.traffic_lane - terminal_layout.min_block_length, block_location[0][1] + block_width]]

                        points_inside = check_points_inside(check_points, terminal_layout)

                        'If it is possible to place a container block that fulfill minimum block length requirement'
                        if points_inside is True:

                            'Check whether it is possible to INCREASE the block length in x- direction'
                            'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'
                            while block_0_inside is True and block_1_inside is True:
                                current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                                'Determine the new block location'
                                block_location[0] = [current_origin[0], current_origin[1]]
                                block_location[1] = [current_origin[0], current_origin[1] + block_width]
                                block_location[4] = [current_origin[0], current_origin[1]]

                                'Determine new all points of the container block'
                                block_location = [block_location[0],
                                                  block_location[1],
                                                  block_location[2],
                                                  block_location[3],
                                                  block_location[4]]

                                'Check whether all points of the container block is inside the terminal'
                                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            'Determine the location after the while loop: Move the current origin by 1 container'
                            current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                            'Determine the new block location'
                            block_location[0] = [current_origin[0], current_origin[1]]
                            block_location[1] = [current_origin[0], current_origin[1] + block_width]
                            block_location[2] = [block_location[2][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[2][1]]
                            block_location[3] = [block_location[3][0] - block_length - 2 * terminal_layout.margin_head - terminal_layout.traffic_lane, block_location[3][1]]
                            block_location[4] = [current_origin[0], current_origin[1]]

                            'Determine new all points of the container block'
                            block_location = [block_location[0],
                                              block_location[1],
                                              block_location[2],
                                              block_location[3],
                                              block_location[4]]

                            'Check whether all points of the container block is inside the terminal'
                            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

                    'If it is NOT POSSIBLE to place a FULL container block on the further row ahead'
                else:
                    'Check whether it is possible to INCREASE the block length in x- direction'
                    'Algorithm for : Increasing the block length until it reaches the edge of the terminal in x- direction'

                    'Check whether the right side already fulfill the requirments for terminal_layout.margin_head'
                    check_points = [[block_location[0][0] - terminal_layout.margin_head, block_location[0][1]],
                                    [block_location[0][0] - terminal_layout.margin_head, block_location[0][1] + block_width]]

                    points_inside = check_points_inside(check_points, terminal_layout)

                    while block_0_inside is True and block_1_inside is True and points_inside is True:
                        current_origin = [current_origin[0] - terminal_layout.tgs_x, current_origin[1]]

                        'Determine the new block location'
                        block_location[0] = [current_origin[0], current_origin[1]]
                        block_location[1] = [current_origin[0], current_origin[1] + block_width]
                        block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width]
                        block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                        block_location[4] = [current_origin[0], current_origin[1]]

                        'Determine new all points of the container block'
                        block_location = [block_location[0],
                                          block_location[1],
                                          block_location[2],
                                          block_location[3],
                                          block_location[4]]

                        'Check whether all points of the container block is inside the terminal'
                        block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                        'Check whether the right side already fulfill the requirments for terminal_layout.margin_head'
                        check_points = [[block_location[0][0] - terminal_layout.margin_head, block_location[0][0]],
                                        [block_location[0][0] - terminal_layout.margin_head, block_location[0][0] + block_width]]

                        points_inside = check_points_inside(check_points, terminal_layout)

                    'Determine the location after the while loop: Move the current origin by 1 container'
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width]
                    block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

            'Algorithm for the case : Cannot place a new container block, because it already reaches outside of the terminal'
            if block_1_inside is False and block_2_inside is False:
                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

            """Algorithm for the case : There is possibility for : 
            (a) The container block length should be DECREASED to the x+ direction in order to place the container block
            (b) The decreasing container block starts on the LEFT side of the container block

            It happens if block_location[0] or block_location[1] is outside the terminal"""
            if block_0_inside is False or block_1_inside is False:

                'Algorithm for : Decreasing the block length until it reaches the edge of the terminal in x+ direction'
                while block_0_inside is False or block_1_inside is False:
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width]
                    block_location[3] = [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        'Algorithm for anomaly condition where the block_location[3][0] is less than block_location[0][0]'
        if block_location[3][0] < block_location[0][0]:

            possible_placement = False

            current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head

            block_location = [[current_origin[0], current_origin[1]],
                              [current_origin[0], current_origin[1] + block_width],
                              [current_origin[0] + block_length, current_origin[1] + block_width],
                              [current_origin[0] + block_length, current_origin[1]],
                              [current_origin[0], current_origin[1]]]

            block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            block_reference = block_reference + 1

            if block_0_inside is False or block_1_inside is False:
                while block_0_inside is False or block_1_inside is False:
                    current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                    block_location = [[current_origin[0], current_origin[1]],
                                      [current_origin[0], current_origin[1] + block_width],
                                      [terminal_layout.block_location_list[block_reference][2][0], current_origin[1] + block_width],
                                      [terminal_layout.block_location_list[block_reference][3][0], current_origin[1]],
                                      [current_origin[0], current_origin[1]]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            if block_1_inside is False and block_2_inside is False:
                possible_placement = False
                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        """
            Algorithm for the (special) case : Reversed triangular
            If block_location[0] and block_location[1] is outside the terminal --> reversed triangular case
        """

        if block_0_inside is False or block_1_inside is False:
            while block_0_inside is False or block_1_inside is False:
                current_origin = [current_origin[0] + terminal_layout.tgs_x, current_origin[1]]

                'Determine the new block location'
                block_location[0] = [current_origin[0], current_origin[1]]
                block_location[1] = [current_origin[0], current_origin[1] + block_width]
                block_location[2] = block_location[2]
                block_location[3] = block_location[3]
                block_location[4] = [current_origin[0], current_origin[1]]

                'Determine new all points of the container block'
                block_location = [block_location[0],
                                  block_location[1],
                                  block_location[2],
                                  block_location[3],
                                  block_location[4]]

                'Check whether all points of the container block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

            """The algorithm for the case of moving current_origin to the next container block in bay direction ends here
            Next is the algorithm in defining container block location"""

            possible_placement = True

            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        if block_0_inside is True and block_1_inside is True and block_2_inside is True and block_3_inside is True:
            return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

        else:
            """Algorithm for the case : There is possibility for : 
            (a) The container block length can be DECREASED to the x- direction in order to place the container block
            (b) The decreasing container block starts on the RIGHT side of the container block

            It happens if block_location[0] or block_location[1] is outside the terminal"""

            'Check whether it is possible to place a container block that fulfill minimum block length requirement'
            'If it is POSSIBLE to fulfill minimum block length requirement'
            if block_location[3][0] - block_location[0][0] > terminal_layout.min_block_length:

                'Check whether the right side already fulfill the requirments for terminal_layout.margin_head'
                check_points = [[block_location[3][0] + terminal_layout.margin_head, block_location[3][1]],
                                [block_location[3][0] + terminal_layout.margin_head, block_location[3][1] + block_width]]

                points_inside = check_points_inside(check_points, terminal_layout)

                'Algorithm for : Decreasing the block length until it reaches the edge of the terminal in x- direction'
                while (block_2_inside is False or block_3_inside is False) and points_inside is False:
                    'Determine the new block location'
                    block_location[0] = [current_origin[0], current_origin[1]]
                    block_location[1] = [current_origin[0], current_origin[1] + block_width]
                    block_location[2] = [block_location[2][0] - terminal_layout.tgs_x, current_origin[1] + block_width]
                    block_location[3] = [block_location[3][0] - terminal_layout.tgs_x, current_origin[1]]
                    block_location[4] = [current_origin[0], current_origin[1]]

                    'Determine new all points of the container block'
                    block_location = [block_location[0],
                                      block_location[1],
                                      block_location[2],
                                      block_location[3],
                                      block_location[4]]

                    'Check whether all points of the container block is inside the terminal'
                    block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                    'Check whether the right side already fulfill the requirments for terminal_layout.margin_head'
                    check_points = [[block_location[3][0] + terminal_layout.margin_head, block_location[3][1]],
                                    [block_location[3][0] + terminal_layout.margin_head, block_location[3][1] + block_width]]

                    points_inside = check_points_inside(check_points, terminal_layout)

            else:
                'If it is NOT POSSIBLE to fulfill minimum block length requirement'
                'Define that it is possible to place on the next container block in bay direction'
                possible_placement = False

                'Determine the new location for current_origin and block_location'
                current_origin[0] = block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head

                'Determine the new block location'
                block_location = [[current_origin[0], current_origin[1]],
                                  [current_origin[0], current_origin[1] + block_width],
                                  [current_origin[0] + block_length, current_origin[1] + block_width],
                                  [current_origin[0] + block_length, current_origin[1]],
                                  [current_origin[0], current_origin[1]]]

                'Check whether all points of the container block is inside the terminal'
                block_0_inside, block_1_inside, block_2_inside, block_3_inside, block_location = check_block_inside(block_location, terminal_layout)

                return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout

            if current_origin[0] == terminal_layout.block_location_list[0][0][0]:
                possible_placement = True

            else:
                possible_placement = True

    return current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout


'Function for determining the container terminal layout for RTG'


def rtg_layout(laden, terminal_layout):
    terminal, quay_length, prim_yard, apron, terminal_area, prim_yard_area, apron_area, prim_full_ratio = terminal_configuration(terminal_layout)

    # add elements to the terminal_layout
    terminal_layout.terminal = terminal
    terminal_layout.quay_length = quay_length
    terminal_layout.prim_yard = prim_yard
    terminal_layout.apron = apron
    terminal_layout.terminal_area = terminal_area
    terminal_layout.prim_yard_area = prim_yard_area
    terminal_layout.apron_area = apron_area
    terminal_layout.prim_full_ratio = prim_full_ratio

    block_length, block_width, max_blocks_x, max_blocks_y = block_configuration(terminal_layout)
    # add elements to the terminal layout
    terminal_layout.max_blocks_x = max_blocks_x
    terminal_layout.max_blocks_y = max_blocks_y

    'BLOCK GENERATION PARAMETER'
    'The starting origin for the container block is : x = terminal_layout.traffic_lane + terminal_layout.margin_head ; y = apron_width'
    starting_origin = [terminal_layout.traffic_lane + terminal_layout.margin_head, terminal_layout.apron_width]

    if terminal_layout.block_location_list != []:
        last_block_location = terminal_layout.block_location_list[(len(terminal_layout.block_location_list)) - 1]
        current_origin = [last_block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head, last_block_location[3][1]]

    else:
        'Moving current_origin to starting origin for the container block'
        current_origin = [terminal_layout.traffic_lane + terminal_layout.margin_head, terminal_layout.apron_width + terminal_layout.traffic_lane]

    'Define the first container block location'
    block_location = [[current_origin[0], current_origin[1]],
                      [current_origin[0], current_origin[1] + block_width],
                      [current_origin[0] + block_length, current_origin[1] + block_width],
                      [current_origin[0] + block_length, current_origin[1]],
                      [current_origin[0], current_origin[1]]]

    'Define parameters value'
    block_reference = 0

    'Determine the condition for the first placement of the container block'
    first_placement = True

    'Define the top of the block parameter for while loop, so it stops if it reaches the top edge of the primary yard'
    block_top = starting_origin[1] + block_width

    'Define the top of the primary yard terminal boundary for while loop, so it stops if it reaches the top edge of the primary yard'
    prim_yard_x, prim_yard_y = prim_yard.exterior.xy
    prim_yard_top = max(prim_yard_y)

    while block_top <= prim_yard_top and terminal_layout.tgs_demand >= terminal_layout.tgs_capacity:

        current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout = rtg_terminal_generation(starting_origin, current_origin, block_length, block_width, block_location, block_reference, first_placement, terminal_layout, laden)

        if possible_placement is False:
            block_top = block_top + block_width + terminal_layout.bypass_lane

    return terminal_layout


'Function for determining the container terminal layout for RMG'


def rmg_layout(laden, terminal_layout):
    terminal, quay_length, prim_yard, apron, terminal_area, prim_yard_area, apron_area, prim_full_ratio = terminal_configuration(terminal_layout)

    # add elements to the terminal_layout
    terminal_layout.terminal = terminal
    terminal_layout.quay_length = quay_length
    terminal_layout.prim_yard = prim_yard
    terminal_layout.apron = apron
    terminal_layout.terminal_area = terminal_area
    terminal_layout.prim_yard_area = prim_yard_area
    terminal_layout.apron_area = apron_area
    terminal_layout.prim_full_ratio = prim_full_ratio

    block_length, block_width, max_blocks_x, max_blocks_y = block_configuration(terminal_layout)

    # add elements to the terminal layout
    terminal_layout.max_blocks_x = max_blocks_x
    terminal_layout.max_blocks_y = max_blocks_y

    'BLOCK GENERATION PARAMETER'
    'The starting origin for the container block is : x = terminal_layout.traffic_lane ; y = apron_width + terminal_layout.margin_head'
    starting_origin = [terminal_layout.traffic_lane, terminal_layout.apron_width + terminal_layout.margin_head + terminal_layout.traffic_lane]

    if terminal_layout.block_location_list != []:
        last_block_location = terminal_layout.block_location_list[(len(terminal_layout.block_location_list)) - 1]
        current_origin = [last_block_location[3][0] + terminal_layout.margin_parallel, last_block_location[3][1]]

    else:
        'Moving current_origin to starting origin for the container block'
        current_origin = [terminal_layout.traffic_lane, terminal_layout.apron_width + terminal_layout.margin_head + terminal_layout.traffic_lane]

    'Define the first container block location'
    block_location = [[current_origin[0], current_origin[1]],
                      [current_origin[0], current_origin[1] + block_length],
                      [current_origin[0] + block_width, current_origin[1] + block_length],
                      [current_origin[0] + block_width, current_origin[1]],
                      [current_origin[0], current_origin[1]]]

    'Define parameters value'
    block_reference = 0

    'Determine the condition for the first placement of the container block'
    first_placement = True

    'Define the top of the block parameter for while loop, so it stops if it reaches the top edge of the primary yard'
    block_top = starting_origin[1] + block_length

    'Define the top of the primary yard terminal boundary for while loop, so it stops if it reaches the top edge of the primary yard'
    prim_yard_x, prim_yard_y = prim_yard.exterior.xy
    prim_yard_top = max(prim_yard_y)

    while block_top <= prim_yard_top and terminal_layout.tgs_demand >= terminal_layout.tgs_capacity:

        current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout = rmg_terminal_generation(starting_origin, current_origin, block_length, block_width, block_location, block_reference, first_placement, terminal_layout, laden)

        if possible_placement is False:
            block_top = block_top + block_length + 2 * terminal_layout.margin_head + terminal_layout.traffic_lane

    return terminal_layout


'Function for determining the container terminal layout for SC'


def sc_layout(laden, terminal_layout):
    terminal, quay_length, prim_yard, apron, terminal_area, prim_yard_area, apron_area, prim_full_ratio = terminal_configuration(terminal_layout)

    # add elements to the terminal_layout
    terminal_layout.terminal = terminal
    terminal_layout.quay_length = quay_length
    terminal_layout.prim_yard = prim_yard
    terminal_layout.apron = apron
    terminal_layout.terminal_area = terminal_area
    terminal_layout.prim_yard_area = prim_yard_area
    terminal_layout.apron_area = apron_area
    terminal_layout.prim_full_ratio = prim_full_ratio

    # add elements to the terminal_layout
    block_length, block_width, max_blocks_x, max_blocks_y = block_configuration(terminal_layout)
    terminal_layout.max_blocks_x = max_blocks_x
    terminal_layout.max_blocks_y = max_blocks_y

    'BLOCK GENERATION PARAMETER'
    'The starting origin for the container block is : x = terminal_layout.traffic_lane; y = apron_width'
    starting_origin = [terminal_layout.traffic_lane, terminal_layout.apron_width + terminal_layout.traffic_lane + terminal_layout.margin_head]

    if terminal_layout.block_location_list != []:
        last_block_location = terminal_layout.block_location_list[(len(terminal_layout.block_location_list)) - 1]
        current_origin = [last_block_location[3][0] + terminal_layout.traffic_lane, last_block_location[3][1]]

    else:
        'Moving current_origin to starting origin for the container block'
        current_origin = [terminal_layout.traffic_lane, terminal_layout.apron_width + terminal_layout.traffic_lane + terminal_layout.margin_head]

    'Define the first container block location'
    block_location = [[current_origin[0], current_origin[1]],
                      [current_origin[0], current_origin[1] + block_length],
                      [current_origin[0] + block_width, current_origin[1] + block_length],
                      [current_origin[0] + block_width, current_origin[1]],
                      [current_origin[0], current_origin[1]]]

    'Define parameters value'
    block_reference = 0

    'Determine the condition for the first placement of the container block'
    first_placement = True

    'Define the top of the block parameter for while loop, so it stops if it reaches the top edge of the primary yard'
    block_top = starting_origin[1] + block_length

    'Define the top of the primary yard terminal boundary for while loop, so it stops if it reaches the top edge of the primary yard'
    prim_yard_x, prim_yard_y = prim_yard.exterior.xy
    prim_yard_top = max(prim_yard_y)

    while block_top <= prim_yard_top and terminal_layout.tgs_demand >= terminal_layout.tgs_capacity:

        current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout = sc_terminal_generation(starting_origin, current_origin, block_length, block_width, block_location, block_reference, first_placement, terminal_layout, laden)

        if possible_placement is False:
            block_top = block_top + block_length + terminal_layout.traffic_lane

    return terminal_layout


'Function for determining the container terminal layout for RS'


def rs_layout(laden, terminal_layout):
    terminal, quay_length, prim_yard, apron, terminal_area, prim_yard_area, apron_area, prim_full_ratio = terminal_configuration(terminal_layout)

    # add elements to the terminal_layout
    terminal_layout.terminal = terminal
    terminal_layout.quay_length = quay_length
    terminal_layout.prim_yard = prim_yard
    terminal_layout.apron = apron
    terminal_layout.terminal_area = terminal_area
    terminal_layout.prim_yard_area = prim_yard_area
    terminal_layout.apron_area = apron_area
    terminal_layout.prim_full_ratio = prim_full_ratio

    # add elements to the terminal_layout
    block_length, block_width, max_blocks_x, max_blocks_y = block_configuration(terminal_layout)
    terminal_layout.max_blocks_x = max_blocks_x
    terminal_layout.max_blocks_y = max_blocks_y

    'BLOCK GENERATION PARAMETER'
    'The starting origin for the container block is : x = terminal_layout.traffic_lane + terminal_layout.margin_head ; y = apron_width'
    starting_origin = [terminal_layout.traffic_lane + terminal_layout.margin_head, terminal_layout.apron_width + terminal_layout.traffic_lane]

    if terminal_layout.block_location_list != []:
        last_block_location = terminal_layout.block_location_list[(len(terminal_layout.block_location_list)) - 1]
        current_origin = [last_block_location[3][0] + terminal_layout.traffic_lane + 2 * terminal_layout.margin_head, last_block_location[3][1]]

    else:
        'Moving current_origin to starting origin for the container block'
        current_origin = [terminal_layout.traffic_lane + terminal_layout.margin_head, terminal_layout.apron_width + terminal_layout.traffic_lane]

    'Define the first container block location'
    block_location = [[current_origin[0], current_origin[1]],
                      [current_origin[0], current_origin[1] + block_width],
                      [current_origin[0] + block_length, current_origin[1] + block_width],
                      [current_origin[0] + block_length, current_origin[1]],
                      [current_origin[0], current_origin[1]]]

    'Define which block reference in BAY DIRECTION in generating container terminals, 0 means its the first block which the starting origins located'
    block_reference = 0

    'Determine the condition for the first placement of the container block'
    first_placement = True

    'Define the top of the block parameter for while loop, so it stops if it reaches the top edge of the primary yard'
    block_top = starting_origin[1] + block_width

    'Define the top of the primary yard terminal boundary for while loop, so it stops if it reaches the top edge of the primary yard'
    prim_yard_x, prim_yard_y = prim_yard.exterior.xy
    prim_yard_top = max(prim_yard_y)

    while block_top <= prim_yard_top and terminal_layout.tgs_demand >= terminal_layout.tgs_capacity:

        current_origin, possible_placement, block_location, block_reference, first_placement, terminal_layout = rs_terminal_generation(starting_origin, current_origin, block_length, block_width, block_location, block_reference, first_placement, terminal_layout, laden)

        if possible_placement is False:
            block_top = block_top + block_width + terminal_layout.operating_space

        if block_top > prim_yard_top:
            terminal_layout.available_space = False

    return terminal_layout



