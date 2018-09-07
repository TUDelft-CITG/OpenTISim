#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import unittest
from terminal_optimization import core

__author__ = "VANOORD\MRV"
__copyright__ = "VANOORD\MRV"
__license__ = "gpl3"


class Test_vessel_properties_mixin(unittest.TestCase):

    def test_init(self):
        # define sample input
        vessel_type = 'blabla'
        call_size = None
        LOA = None
        draft = None
        beam = None
        max_cranes = None
        all_turn_time = None
        mooring_time = None
        demurrage = None

        # initialize object
        VP = core.vessel_properties_mixin(vessel_type, call_size, LOA, draft, beam, max_cranes, all_turn_time, mooring_time, demurrage)

        # make sure that argument is passed to the envisaged attribute
        assert VP.vessel_type == vessel_type
        assert VP.call_size == call_size
        # ... do this for all arguments
