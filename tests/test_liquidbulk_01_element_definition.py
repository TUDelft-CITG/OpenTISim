#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `opentisim` package."""

def test_liquidbulk_01():
	"""Test to see if object initialisation works properly"""

	import opentisim

	Smallhydrogen = opentisim.liquidbulk.Vessel(**opentisim.liquidbulk.smallhydrogen_data)

	assert Smallhydrogen.call_size == opentisim.liquidbulk.smallhydrogen_data['call_size']
	assert Smallhydrogen.LOA == opentisim.liquidbulk.smallhydrogen_data['LOA']
	assert Smallhydrogen.draft == opentisim.liquidbulk.smallhydrogen_data['draft']
	assert Smallhydrogen.beam == opentisim.liquidbulk.smallhydrogen_data['beam']
