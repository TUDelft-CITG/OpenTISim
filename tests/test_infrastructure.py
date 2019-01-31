#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `terminal_optimization` package."""

def test_quay():
	"""Testing if object properties are properly processed while creating a quay class"""

	import terminal_optimization.infrastructure as infra
	
	quay_data = {"t0_length": 0, "ownership": 'Port authority', "delivery_time": 2, "lifespan": 50, "mobilisation_min": 2500000,
             "mobilisation_perc": 0.02, "maintenance_perc": 0.01, "insurance_perc": 0.01,"length": 400, "depth": 14,
             "freeboard": 4, "Gijt_constant": 757.20, "Gijt_coefficient": 1.2878} 

	quay = infra.quay_wall_class(**quay_data)

	assert quay.Gijt_coefficient == 1.2878
	assert quay.Gijt_constant == 757.2
	assert quay.delivery_time == 2
	assert quay.depth == 14
	assert quay.freeboard == 4
	assert quay.insurance_perc == 0.01
	assert quay.length == 400
	assert quay.lifespan == 50
	assert quay.maintenance_perc == 0.01
	assert quay.mobilisation_min == 2500000
	assert quay.mobilisation_perc == 0.02
	assert quay.ownership == 'Port authority'
	assert quay.t0_length == 0

def test_berth():
	"""Testing if object properties are properly processed while creating a berth class"""

	import terminal_optimization.infrastructure as infra
	
	berth_data = {"t0_quantity": 0, "crane_type": 'Mobile cranes', "max_cranes": 3}

	berth = infra.berth_class(**berth_data)

	assert berth.t0_quantity == 0
	assert berth.crane_type == 'Mobile cranes'
	assert berth.max_cranes == 3

def test_hinterland_station():
	import terminal_optimization.infrastructure as infra

	# Initial data set, data from Excel_input.xlsx
	hinterland_station_data = {"t0_capacity": 0, "ownership": 'Terminal operator', "delivery_time": 1, "lifespan": 15, "unit_rate": 4000, "mobilisation": 100000, "maintenance_perc": 0.02, "consumption": 0.25, "insurance_perc": 0.01, "crew": 2, "utilisation": 0.80, "capacity_steps": 300}

	# define loading station class functions **will ultimately be placed in package**
	hinterland_station = infra.hinterland_station(**hinterland_station_data)

	assert hinterland_station.t0_capacity == 0
	assert hinterland_station.ownership == 'Terminal operator'
	assert hinterland_station.delivery_time == 1
	assert hinterland_station.lifespan ==15
	assert hinterland_station.unit_rate == 4000
	assert hinterland_station.mobilisation == 100000
	assert hinterland_station.maintenance_perc == 0.02
	assert hinterland_station.consumption == 0.25
	assert hinterland_station.insurance_perc == 0.01
	assert hinterland_station.crew == 2
	assert hinterland_station.utilisation == 0.80
	assert hinterland_station.capacity_steps == 300

def test_conveyor():
	import terminal_optimization.infrastructure as infra
	
	quay_conveyor_data = {"t0_capacity": 0, "length": 500, "ownership": 'Terminal operator', 
	"delivery_time": 1, "lifespan": 10, "unit_rate": 6, "mobilisation": 30000,
	"maintenance_perc": 0.10, "insurance_perc": 0.01, "consumption_constant": 81,
	"consumption_coefficient":0.08, "crew": 1, "utilisation": 0.80, "capacity_steps": 400}
    
	quay_conveyor_object = infra.conveyor(**quay_conveyor_data)

	assert quay_conveyor_object.t0_capacity == 0
	assert quay_conveyor_object.length == 500
	assert quay_conveyor_object.ownership == 'Terminal operator'
	assert quay_conveyor_object.delivery_time == 1
	assert quay_conveyor_object.lifespan == 10
	assert quay_conveyor_object.unit_rate == 6
	assert quay_conveyor_object.mobilisation == 30000
	assert quay_conveyor_object.maintenance_perc == 0.10
	assert quay_conveyor_object.insurance_perc == 0.01
	assert quay_conveyor_object.consumption_constant == 81
	assert quay_conveyor_object.consumption_coefficient == 0.08
	assert quay_conveyor_object.crew == 1
	assert quay_conveyor_object.utilisation == 0.80
	assert quay_conveyor_object.capacity_steps == 400