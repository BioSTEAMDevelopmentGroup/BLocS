#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 13:46:34 2021

@author: daltonstewart
"""

import biosteam as bst
from biorefineries import lipidcane as lc
from chaospy import distributions as shape
import blocs as blc
import numpy as np
import pandas as pd
import os
from biosteam.evaluation.evaluation_tools import triang

#Import state scenarios data
folder = os.path.dirname(__file__)
st_data_file = os.path.join(folder, 'state_scenarios_for_import.xlsx')
st_data = pd.read_excel(st_data_file, index_col=[0])

states = ['Alaska',
          'Arizona',
          'Arkansas',
          'California',
          'Connecticut',
          'Delaware',
          'Florida',
          'Georgia',
          'Idaho',
          'Illinois',
          'Indiana',
          'Maine',
          'Maryland',
          'Massachusetts',
          'Minnesota',
          'Mississippi',
          'Missouri',
          'Nevada',
          'New Hampshire',
          'New Jersey',
          'New York',
          'North Carolina',
          'North Dakota',
          'Ohio',
          'Oklahoma',
          'Pennsylvania',
          'Rhode Island',
          'South Dakota',
          'Tennessee',
          'Texas',
          'Vermont',
          'Washington',
          'West Virginia',
          'Wisconsin',
          'Wyoming'
           ]

states_w_inc = ['Alabama',
                'Colorado',
                'Hawaii',
                'Iowa',
                'Kansas',
                'Kentucky',
                'Louisiana',
                'Michigan',
                'Montana',
                'Nebraska',
                'New Mexico',
                'Oregon',
                'South Carolina',
                'Utah',
                'Virginia'
                ]

all_states = ['Alaska',
          'Arizona',
          'Arkansas',
          'California',
          'Connecticut',
          'Delaware',
          'Florida',
          'Georgia',
          'Idaho',
          'Illinois',
          'Indiana',
          'Maine',
          'Maryland',
          'Massachusetts',
          'Minnesota',
          'Mississippi',
          'Missouri',
          'Nevada',
          'New Hampshire',
          'New Jersey',
          'New York',
          'North Carolina',
          'North Dakota',
          'Ohio',
          'Oklahoma',
          'Pennsylvania',
          'Rhode Island',
          'South Dakota',
          'Tennessee',
          'Texas',
          'Vermont',
          'Washington',
          'West Virginia',
          'Wisconsin',
          'Wyoming',
          'Alabama',
          'Colorado',
          'Hawaii',
          'Iowa',
          'Kansas',
          'Kentucky',
          'Louisiana',
          'Michigan',
          'Montana',
          'Nebraska',
          'New Mexico',
          'Oregon',
          'South Carolina',
          'Utah',
          'Virginia'
           ]

tea = lc.create_tea(lc.lipidcane_sys, blc.ConventionalIncentivesTEA)
# tea = lc.create_tea(lc.lipidcane_sys, blc.IncentivesTEA)
model = bst.Model(lc.lipidcane_sys, exception_hook='raise')

#=============================================================================
#Activate this section if including fuel and sales taxes
#=============================================================================
# tea.fuel_tax = 0.28
# tea.sales_tax = 0.05875
# tea.federal_income_tax = 0.35
# tea.state_income_tax = 0.065
# tea.property_tax = 0.013
# tea.utility_tax = 0.
# tea.incentive_numbers = ()
# tea.ethanol_product = lc.ethanol
# tea.biodiesel_product = lc.biodiesel
# tea.ethanol_group = lc.ethanol_production_units
# tea.biodiesel_group = lc.biodiesel_production_units
# tea.feedstock = lc.lipidcane
# tea.BT = lc.BT
# bst.PowerUtility.price = 0.0685

# @model.metric(name='Net electricity production', units='MWh/yr')
# def get_electricity_production():
#     return sum(i.power_utility.rate for i in lc.lipidcane_sys.units) * tea.operating_hours/1000

# MFSP_box = [None]

# @model.metric(name="Baseline MFSP", units='USD/gal')
# def MFSP_baseline():
#     tea.incentive_numbers = ()
#     MFSP_box[0] = 2.98668849 * tea.solve_price(lc.ethanol)
#     return 2.98668849 * tea.solve_price(lc.ethanol)

# get_exemptions = lambda: tea.exemptions.sum()
# get_deductions = lambda: tea.deductions.sum()
# get_credits = lambda: tea.credits.sum()
# get_refunds = lambda: tea.refunds.sum()

# def MFSP_getter(state):
#     def MFSP():
#         tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
#         tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
#         bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
#         tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
#         tea.incentive_numbers = ()
#         return 2.98668849 * tea.solve_price(lc.ethanol)
#     return MFSP

# def MFSP_w_inc_getter(state):
#     def MFSP():
#         tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
#         tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
#         bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
#         tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']

#         if state == 'Alabama':
#             tea.incentive_numbers = (8,9)
#         elif state == 'Colorado':
#             tea.incentive_numbers = (10,)
#         elif state == 'Hawaii':
#             tea.incentive_numbers = (11,)
#         elif state == 'Iowa':
#             tea.incentive_numbers = (1,12,21)
#         elif state == 'Kansas':
#             tea.incentive_numbers = (2,)
#         elif state == 'Kentucky':
#             tea.incentive_numbers = (13,14,22)
#         elif state == 'Louisiana':
#             tea.incentive_numbers = (15,)
#         elif state == 'Michigan':
#             tea.incentive_numbers = (3,)
#         elif state == 'Montana':
#             tea.incentive_numbers = (4,23)
#         elif state == 'Nebraska':
#             tea.incentive_numbers = (5,)
#         elif state == 'New Mexico':
#             tea.incentive_numbers = (7,)
#         elif state == 'Oregon':
#             tea.incentive_numbers = (6,)
#         elif state == 'South Carolina':
#             tea.incentive_numbers = (16,17)
#         elif state == 'Utah':
#             tea.incentive_numbers = (18,)
#         elif state == 'Virginia':
#             tea.incentive_numbers = (19,)

#         return 2.98668849 * tea.solve_price(lc.ethanol)
#     return MFSP

# def MFSP_reduction_getter(incentive_numbers):
#     def MFSP():
#         tea.incentive_numbers = incentive_numbers
#         return (2.98668849 * tea.solve_price(lc.ethanol) - MFSP_box[0])/MFSP_box[0] * 100
#     return MFSP

#=============================================================================
#Activate this section if including only income and property taxes
#=============================================================================
tea.fuel_tax = 0.
tea.sales_tax = 0.
tea.federal_income_tax = 0.35
tea.state_income_tax = 0.065
tea.property_tax = 0.013
tea.utility_tax = 0.
# tea.incentive_numbers = ()
#Activate lines 235 and 236 and deactivate line 233 to simulate federal incentives for every state
tea.incentive_numbers = (20,)
tea.depreciation_incentive_24(True)
tea.ethanol_product = lc.ethanol
tea.biodiesel_product = lc.biodiesel
tea.ethanol_group = lc.ethanol_production_units
tea.biodiesel_group = lc.biodiesel_production_units
tea.feedstock = lc.lipidcane
tea.BT = lc.BT
bst.PowerUtility.price = 0.0685

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

def MFSP_getter(state):
    def MFSP():
        tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
        tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
        bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
        tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
        tea.incentive_numbers = ()
        return 2.98668849 * tea.solve_price(lc.ethanol)
    return MFSP


def get_state_incentives(state):
        avail_incentives = st_data.loc[state]['Incentives Available']
        avail_incentives = None if pd.isna(avail_incentives) else avail_incentives # no incentives
        if avail_incentives is not None:
            try: # multiple incentives
                avail_incentives = [int(i) for i in avail_incentives if i.isnumeric()]
            except TypeError: # only one incentive
                avail_incentives = [int(avail_incentives)]
        return avail_incentives


#Use this function if not including federal incentives
def MFSP_w_inc_getter(state):
    def MFSP():
        tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
        tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
        bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
        tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
        tea.incentive_numbers = get_state_incentives(state)

        # if state == 'Alabama':
        #     tea.incentive_numbers = (8,9)
        # elif state == 'Colorado':
        #     tea.incentive_numbers = (10,)
        # elif state == 'Hawaii':
        #     tea.incentive_numbers = (11,)
        # elif state == 'Iowa':
        #     tea.incentive_numbers = (1,12,21)
        # elif state == 'Kansas':
        #     tea.incentive_numbers = (2,)
        # elif state == 'Kentucky':
        #     tea.incentive_numbers = (13,14,22)
        # elif state == 'Louisiana':
        #     tea.incentive_numbers = (15,)
        # elif state == 'Michigan':
        #     tea.incentive_numbers = (3,)
        # elif state == 'Montana':
        #     tea.incentive_numbers = (4,23)
        # elif state == 'Nebraska':
        #     tea.incentive_numbers = (5,)
        # elif state == 'New Mexico':
        #     tea.incentive_numbers = (7,)
        # elif state == 'Oregon':
        #     tea.incentive_numbers = (6,)
        # elif state == 'South Carolina':
        #     tea.incentive_numbers = (16,17)
        # elif state == 'Utah':
        #     tea.incentive_numbers = (18,)
        # elif state == 'Virginia':
        #     tea.incentive_numbers = (19,)

        return 2.98668849 * tea.solve_price(lc.ethanol)
    return MFSP

#Use this function if including federal incentives
def MFSP_fed_getter(state):
    def MFSP():
        tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
        tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
        bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
        tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
        # tea.incentive_numbers = ()
        return 2.98668849 * tea.solve_price(lc.ethanol)
    return MFSP

def MFSP_w_inc_fed_getter(state):
    def MFSP():
        tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
        tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
        bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
        tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
        tea.incentive_numbers = get_state_incentives(state)

        # if state == 'Alabama':
        #     tea.incentive_numbers = (8,9,20)
        # elif state == 'Colorado':
        #     tea.incentive_numbers = (10,20)
        # elif state == 'Hawaii':
        #     tea.incentive_numbers = (11,20)
        # elif state == 'Iowa':
        #     tea.incentive_numbers = (1,12,21,20)
        # elif state == 'Kansas':
        #     tea.incentive_numbers = (2,20)
        # elif state == 'Kentucky':
        #     tea.incentive_numbers = (13,14,22,20)
        # elif state == 'Louisiana':
        #     tea.incentive_numbers = (15,20)
        # elif state == 'Michigan':
        #     tea.incentive_numbers = (3,20)
        # elif state == 'Montana':
        #     tea.incentive_numbers = (4,23,20)
        # elif state == 'Nebraska':
        #     tea.incentive_numbers = (5,20)
        # elif state == 'New Mexico':
        #     tea.incentive_numbers = (7,20)
        # elif state == 'Oregon':
        #     tea.incentive_numbers = (6,20)
        # elif state == 'South Carolina':
        #     tea.incentive_numbers = (16,17,20)
        # elif state == 'Utah':
        #     tea.incentive_numbers = (18,20)
        # elif state == 'Virginia':
        #     tea.incentive_numbers = (19,20)

        return 2.98668849 * tea.solve_price(lc.ethanol)
    return MFSP

#If not including federal incentives
# #Use this for loop to simulate all states without incentives
# for state in all_states:
#     element = f"{state}"
#     model.metric(MFSP_getter(state), 'MFSP', 'USD/gal', element)

# #Use these for loops to include incentives for states that have them
# for state in states:
#     element = f"{state}"
#     model.metric(MFSP_getter(state), 'MFSP', 'USD/gal', element)

# for state in states_w_inc:
#     element = f"{state}"
#     model.metric(MFSP_w_inc_getter(state), 'MFSP', 'USD/gal', element)

#If including federal incentives
#Use this for loop to simulate all states without incentives
for state in all_states:
    element = f"{state}"
    model.metric(MFSP_fed_getter(state), 'MFSP', 'USD/gal', element)

# #Use these for loops to include incentives for states that have them
# for state in states:
#     element = f"{state}"
#     model.metric(MFSP_fed_getter(state), 'MFSP', 'USD/gal', element)

# for state in states_w_inc:
#     element = f"{state}"
#     model.metric(MFSP_w_inc_fed_getter(state), 'MFSP', 'USD/gal', element)

### Parameter distributions ===================================================
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

# Plant capacity
@model.parameter(element=lipidcane, kind='isolated', units='kg/hr',
                  distribution=triang(lipidcane.F_mass))
def set_plant_capacity(plant_capacity):
    lipidcane.F_mass = plant_capacity

# Boiler efficiency
@model.parameter(element=lc.BT, units='%', distribution=triang(lc.BT.boiler_efficiency))
def set_boiler_efficiency(boiler_efficiency):
    lc.BT.boiler_efficiency = boiler_efficiency

# Fermentation efficiency
fermentation = lc.R301
@model.parameter(
    element=fermentation, distribution=shape.Triangle(0.85, 0.90, 0.95),
    baseline=fermentation.efficiency,
)
def set_fermentation_efficiency(efficiency):
    fermentation.efficiency= efficiency

# Biodiesel price
@model.parameter(
    element=lc.biodiesel, distribution=triang(lc.biodiesel.price),
    baseline=lc.biodiesel.price,
)
def set_biodiesel_price(price):
    lc.biodiesel.price = price

# # Lipid fraction
# # Originally 0.10, but this is much too optimistic. In fact,
# # even 0.05 is optimistic.
# model.parameter(lc.set_lipid_fraction, element=lc.lipidcane,
#                 distribution=triang(0.05), baseline=0.05)

# np.random.seed(1688)
# N_samples = 2000
# rule = 'L' # For Latin-Hypercube sampling
# samples = model.sample(N_samples, rule)
# model.load_samples(samples)
# model.evaluate()
# table=model.table