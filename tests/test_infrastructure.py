#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `opentisim` package."""

def test_berth():
	"""Test to see if object initialisation works properly"""

	from opentisim import agribulk_objects
	from opentisim import agribulk_defaults
	
	berth_data = {"name": 'Berth_01',
	              "crane_type": 'Mobile cranes',
	              "delivery_time": 1,
              	      "max_cranes": 3}
        
	berth = agribulk_objects.Berth(**berth_data)

	assert berth.name == 'Berth_01'
	assert berth.crane_type == 'Mobile cranes'
	assert berth.delivery_time == 1
	assert berth.max_cranes == 3
