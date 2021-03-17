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

state_scenarios_no_fed = {
    'Alabama': {'Incentives' : (8,9),
                'st_income_tax' : 0.065,
                'property_tax' : 0.007,
                'fuel_tax' : 0.24,
                'utility_tax' : 0.02,
                'sales_tax' : 0.04,
                'elec_price' : 0.0601,
                'LCCF' : 0.82},
     'Alaska': {'Incentives' : (),
                'st_income_tax' : 0.094,
                'property_tax' : 0.00111,
                'fuel_tax' : 0.0895,
                'utility_tax' : 0.02,
                'sales_tax' : 0.,
                'elec_price' : 0.171,
                'LCCF' : 2.56},
     'Arizona': {'Incentives' : (),
                'st_income_tax' : 0.049,
                'property_tax' : 0.019,
                'fuel_tax' : 0.19,
                'utility_tax' : 0.02,
                'sales_tax' : 0.056,
                'elec_price' : 0.0655,
                'LCCF' : 0.96},
     'Arkansas': {'Incentives' : (),
                'st_income_tax' : 0.065,
                'property_tax' : 0.0066,
                'fuel_tax' : 0.248,
                'utility_tax' : 0.02,
                'sales_tax' : 0.065,
                'elec_price' : 0.0564,
                'LCCF' : 0.85},
     'California': {'Incentives' : (),
                'st_income_tax' : 0.0884,
                'property_tax' : 0.0075,
                'fuel_tax' : 0.533,
                'utility_tax' : 0.02,
                'sales_tax' : 0.0725,
                'elec_price' : 0.132,
                'LCCF' : 1.1}}

tea = lc.create_tea(lc.lipidcane_sys, ti.IncentivesTEA)
model = bst.Model(lc.lipidcane_sys, exception_hook='raise')

tea = lc.create_tea(lc.lipidcane_sys, ti.IncentivesTEA)
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
tea.BT = lc.BT

@model.metric(name='Net electricity production', units='MWh/yr')
def get_electricity_production():
    return sum(i.power_utility.rate for i in lc.lipidcane_sys.units) * tea._operating_hours/1000

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

def MFSP_getter(incentive_number):
    def MFSP():
        tea.incentive_numbers = (incentive_number,)
        return 2.98668849 * tea.solve_price(lc.ethanol)
    return MFSP

def MFSP_reduction_getter(incentive_number):
    def MFSP():
        tea.incentive_numbers = (incentive_number,)
        return (2.98668849 * tea.solve_price(lc.ethanol) - MFSP_box[0])/MFSP_box[0] * 100
    return MFSP

for state in state_scenarios_no_fed.keys():
    element = f"{state}"
    model.metric(MFSP_getter(state_scenarios_no_fed[state]['Incentives']), 'MFSP', 'USD/gal', element)
    model.metric(MFSP_reduction_getter(state_scenarios_no_fed[state]['Incentives']), 'MFSP Percent Reduction', '%', element)
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

# def MFSP_by_state(state):       
#     tea.fuel_tax = state_scenarios_no_fed[state]['fuel_tax']
#     tea.sales_tax = state_scenarios_no_fed[state]['sales_tax']
#     tea.federal_income_tax = 0.35
#     tea.state_income_tax = state_scenarios_no_fed[state]['st_income_tax']
#     tea.utility_tax = state_scenarios_no_fed[state]['utility_tax']
#     tea.property_tax = state_scenarios_no_fed[state]['property_tax']
#     bst.PowerUtility.price = state_scenarios_no_fed[state]['elec_price']
#     tea.ethanol_product = lc.ethanol
#     tea.biodiesel_product = lc.biodiesel
#     tea.ethanol_group = lc.ethanol_production_units
#     tea.biodiesel_group = lc.biodiesel_production_units
#     tea.BT = lc.BT    
    
np.random.seed(1688)
N_samples = 5
rule = 'L' # For Latin-Hypercube sampling
samples = model.sample(N_samples, rule)
model.load_samples(samples)
model.evaluate
    # return model.table
