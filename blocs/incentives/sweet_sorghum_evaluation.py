#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 11:54:26 2023

@author: daltonwstewart
"""

import flexsolve as flx
import biosteam as bst
from biorefineries import corn as cn
import biorefineries.oilcane as oc
from chaospy import distributions as shape
import blocs as blc
import numpy as np
import pandas as pd
import os

# Initial LCA setup
from biorefineries.corn import default_stream_GWP_CFs as corn_stream_GWP_CFs
stream_GWP_CFs = corn_stream_GWP_CFs.copy()
stream_GWP_CFs.pop('Corn')
GWP = 'GWP 100yr'
bst.settings.define_impact_indicator(key=GWP, units='kg*CO2e')

# Import state scenario data
folder = os.path.dirname(__file__)
st_data_file = os.path.join(folder, 'state_scenarios_for_import.xlsx')
state_data = pd.read_excel(st_data_file, index_col=[0])

# !!! will also need to set operation_mode parameter
# Create sweet sorghum (ss) TEA
def create_ss_tea():
    oc.load('S1*') # !!! there might be a better way to do this; probably called sugarcane_sys
    tea = oc.create_tea(gs.grain_sorghum_sys, cls=blc.ConventionalBLocSTEA)
    tea.incentive_numbers = [] # Empty for now
    tea.fuel_tax = 0.
    tea.sales_tax = 0.
    tea.federal_income_tax = 0.21
    tea.state_income_tax = 0.065
    tea.property_tax = 0.013
    tea.utility_tax = 0.
    tea.ethanol_product = oc.ethanol
    tea.ethanol_group = bst.UnitGroup('Ethanol group', oc.grain_sorghum_sys.units) # Assume all unit operations qualify
    tea.feedstock = gs.feedstock
    return tea