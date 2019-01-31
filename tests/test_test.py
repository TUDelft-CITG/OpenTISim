#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `digital_twin` package."""

def test_test():
	import terminal_optimization.forecast as forecast
	forecast = forecast.create_scenario(2020,10,range(10))
	
	assert len(forecast.historic_years)==10