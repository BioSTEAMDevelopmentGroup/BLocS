#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 13:46:34 2021

@author: daltonstewart
"""

import biosteam as bst
from biorefineries import lipidcane as lc
from chaospy import distributions as shape
import incentives as ti
import numpy as np
import pandas as pd
import os

#Import state scenarios data
folder = os.path.dirname(__file__)
st_data_file = os.path.join(folder, 'state_scenarios_for_import.xlsx')
st_data = pd.read_excel(st_data_file, index_col=[0])

states = ['Illinois',
            'Pennsylvania'
           ]

tea = lc.create_tea(lc.lipidcane_sys, ti.IncentivesTEA)
model = bst.Model(lc.lipidcane_sys, exception_hook='raise')

tea.fuel_tax = 0.332
tea.sales_tax = 0.06
tea.federal_income_tax = 0.35
tea.state_income_tax = 0.12
tea.utility_tax = 0.
tea.incentive_numbers = ()
tea.ethanol_product = lc.ethanol
tea.biodiesel_product = lc.biodiesel
tea.ethanol_group = lc.ethanol_production_units
tea.biodiesel_group = lc.biodiesel_production_units
tea.feedstock = lc.lipidcane
tea.BT = lc.BT

@model.metric(name='Net electricity production', units='MWh/yr')
def get_electricity_production():
    return sum(i.power_utility.rate for i in lc.lipidcane_sys.units) * tea.operating_hours/1000

MFSP_box = [None]

@model.metric(name="Baseline MFSP", units='USD/gal')
def MFSP_baseline():
    tea.incentive_numbers = ()
    MFSP_box[0] = 2.98668849 * tea.solve_price(lc.ethanol)
    return 2.98668849 * tea.solve_price(lc.ethanol)

get_exemptions = lambda: tea.exemptions.sum()
get_deductions = lambda: tea.deductions.sum()
get_credits = lambda: tea.credits.sum()
get_refunds = lambda: tea.refunds.sum()

def MFSP_getter(incentive_numbers):
    def MFSP():
        tea.incentive_numbers = incentive_numbers
        return 2.98668849 * tea.solve_price(lc.ethanol)
    return MFSP

def MFSP_reduction_getter(incentive_numbers):
    def MFSP():
        tea.incentive_numbers = incentive_numbers
        return (2.98668849 * tea.solve_price(lc.ethanol) - MFSP_box[0])/MFSP_box[0] * 100
    return MFSP

for state in states:
    element = f"{state}"
    tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
    tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
    bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
    tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
    incentive_numbers = ()#st_data.loc[state]['Incentives Available']
    
    model.metric(MFSP_getter(incentive_numbers), 'MFSP', 'USD/gal', element)
    model.metric(MFSP_reduction_getter(incentive_numbers), 'MFSP Percent Reduction', '%', element)
    model.metric(get_exemptions, 'Excemptions', 'USD', element)
    model.metric(get_deductions, 'Deductions', 'USD', element)
    model.metric(get_credits, 'Credits', 'USD', element)
    model.metric(get_refunds, 'Refunds', 'USD', element)
    
# Feedstock prices, distribution taken from Yoel's example
lipidcane = lc.lipidcane
FP_L = lipidcane.price * 0.9 # min price
FP_U = lipidcane.price * 1.1 # max price
    
# Electricty generation efficiency
EGeff_dist = shape.Triangle(0.7,0.85,0.9)
    
### Add Parameters ============================================================= 
# Feedstock price
@model.parameter(element=lipidcane, kind='isolated', units='USD/kg',
                 distribution=shape.Uniform(FP_L, FP_U))
def set_feed_price(feedstock_price):
    lipidcane.price = feedstock_price
        
# Turbogenerator efficiency
@model.parameter(element=lc.BT, units='%', distribution=EGeff_dist)
def set_turbogenerator_efficiency(turbo_generator_efficiency):
    lc.BT.turbogenerator_efficiency = turbo_generator_efficiency  
    
np.random.seed(1688)
N_samples = 5
rule = 'L' # For Latin-Hypercube sampling
samples = model.sample(N_samples, rule)
model.load_samples(samples)
model.evaluate()
