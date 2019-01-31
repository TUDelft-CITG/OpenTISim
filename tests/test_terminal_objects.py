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
