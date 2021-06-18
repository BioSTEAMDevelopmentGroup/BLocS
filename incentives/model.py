#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Examples
--------
>>> models = [create_model(i) for i in ('corn', 'sugarcane', 'cornstover')]
>>> dfs = [evaluate(i) for i in ('corn', 'sugarcane', 'cornstover')]


"""

import biosteam as bst
from chaospy import distributions as shape
from biosteam.evaluation.evaluation_tools import triang
import incentives as ti
import numpy as np
import pandas as pd
import os

#Import state scenario data
folder = os.path.dirname(__file__)
st_data_file = os.path.join(folder, 'state_scenarios_for_import.xlsx')
st_data = pd.read_excel(st_data_file, index_col=[0])

states = [
          'Arkansas',
          'California',
          'Delaware',
          'Georgia',
          'Idaho',
          'Illinois',
          'Indiana',
          'Maryland',
          'Minnesota',
          'Mississippi',
          'Missouri',
          'New York',
          'North Carolina',
          'North Dakota',
          'Ohio',
          'Oklahoma',
          'Pennsylvania',
          'South Dakota',
          'Tennessee',
          'Texas',
          'Wisconsin',
           ]

states_w_inc = ['Alabama',
                'Colorado',
                'Iowa',
                'Kansas',
                'Kentucky',
                'Louisiana',
                'Michigan',
                'Nebraska',
                'South Carolina',
                'Virginia'
                ]

all_states = [
          'Arkansas',
          'California',
          'Delaware',
          'Georgia',
          'Idaho',
          'Illinois',
          'Indiana',
          'Maryland',
          'Minnesota',
          'Mississippi',
          'Missouri',
          'New York',
          'North Carolina',
          'North Dakota',
          'Ohio',
          'Oklahoma',
          'Pennsylvania',
          'South Dakota',
          'Tennessee',
          'Texas',
          'Wisconsin',
          'Alabama',
          'Colorado',
          'Iowa',
          'Kansas',
          'Kentucky',
          'Louisiana',
          'Michigan',
          'Nebraska',
          'South Carolina',
          'Virginia'
           ]

def create_model(biorefinery):
    biorefinery = biorefinery.lower()
    if biorefinery == 'corn':
        tea = ti.create_corn_tea()
    elif biorefinery == 'cornstover':
        tea = ti.create_cornstover_tea()
    elif biorefinery == 'sugarcane':
        tea = ti.create_sugarcane_tea()
    else:
        raise ValueError("invalid biorefinery; must be either "
                         "'corn', 'cornstover', or 'sugarcane'")
    
    model = bst.Model(tea.system, exception_hook='raise')
    bst.PowerUtility.price = 0.0685

    def MFSP_getter(state):
        def MFSP():
            tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
            tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
            tea.fuel_tax = st_data.loc[state]['State Motor Fuel Tax (decimal)']
            tea.sales_tax = st_data.loc[state]['State Sales Tax Rate (decimal)']
            bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
            tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
            tea.incentive_numbers = ()
            return 2.98668849 * tea.solve_price(tea.ethanol_product)
        return MFSP
    
    def MFSP_w_inc_getter(state):
        def MFSP():
            tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
            tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
            tea.fuel_tax = st_data.loc[state]['State Motor Fuel Tax (decimal)']
            tea.sales_tax = st_data.loc[state]['State Sales Tax Rate (decimal)']
            bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
            tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
            
            if state == 'Alabama':
                tea.incentive_numbers = (8,9)
            elif state == 'Colorado':
                tea.incentive_numbers = (10,)
            elif state == 'Hawaii':
                tea.incentive_numbers = (11,)
            elif state == 'Iowa':
                tea.incentive_numbers = (1,12,21)
            elif state == 'Kansas':
                tea.incentive_numbers = (2,)
            elif state == 'Kentucky':
                tea.incentive_numbers = (13,14,22)
            elif state == 'Louisiana':
                tea.incentive_numbers = (15,)
            elif state == 'Michigan':
                tea.incentive_numbers = (3,)
            elif state == 'Montana':
                tea.incentive_numbers = (4,23)
            elif state == 'Nebraska':
                tea.incentive_numbers = (5,)
            elif state == 'New Mexico':
                tea.incentive_numbers = (7,)
            elif state == 'Oregon':
                tea.incentive_numbers = (6,)
            elif state == 'South Carolina':
                tea.incentive_numbers = (16,17)
            elif state == 'Utah':
                tea.incentive_numbers = (18,)
            elif state == 'Virginia':
                tea.incentive_numbers = (19,)
                
            return 2.98668849 * tea.solve_price(tea.ethanol_product)
        return MFSP
    
    @model.metric(name='Utility cost', units='10^6 USD/yr')
    def get_utility_cost():
        return tea.utility_cost / 1e6
    
    @model.metric(name='Net electricity production', units='MWh/yr')
    def get_electricity_production():
        return sum(i.power_utility.rate for i in tea.system.units) * tea.operating_hours/1000
    
    @model.metric(name="Baseline MFSP", units='USD/gal')
    def MFSP_baseline():
        tea.incentive_numbers = ()
        MFSP = 2.98668849 * tea.solve_price(tea.ethanol_product)
        return MFSP
    
    for state in states:
        element = f"{state}"
        model.metric(MFSP_getter(state), 'MFSP', 'USD/gal', element)
        
    for state in states_w_inc:
        element = f"{state}"
        model.metric(MFSP_w_inc_getter(state), 'MFSP', 'USD/gal', element)
    
    
    ### Create parameter distributions ============================================
    # Feedstock prices, distribution taken from Yoel's example
    feedstock = tea.feedstock
    FP_L = feedstock.price * 0.9 # min price
    FP_U = feedstock.price * 1.1 # max price
    
    # Gasoline prices, USD/gal
    GP_dist = shape.Uniform(2.103, 2.934)
    
    # Location capital cost factors
    LCCF_dist = shape.Triangle(0.82, 1, 2.56)
    
    # Electricty generation efficiency
    EGeff_dist = shape.Triangle(0.7,0.85,0.9)
    
    ### Add Parameters =============================================================
    # Feedstock price
    @model.parameter(element=feedstock, kind='isolated', units='USD/kg',
                      distribution=shape.Uniform(FP_L, FP_U))
    def set_feed_price(feedstock_price):
        feedstock.price = feedstock_price
        
    #: WARNING: these distributions are arbitrary and a thorough literature search
    #: and an analysis of U.S. ethanol price projections should be made 
    #: to include these
    
    # Plant capacity
    @model.parameter(element=feedstock, kind='isolated', units='kg/hr',
                      distribution=triang(feedstock.F_mass))
    def set_plant_capacity(plant_capacity):
        feedstock.F_mass = plant_capacity
    
    if tea.BT:
        # Boiler efficiency
        @model.parameter(element=tea.BT, units='%', distribution=triang(tea.BT.boiler_efficiency))
        def set_boiler_efficiency(boiler_efficiency):
            tea.BT.boiler_efficiency = boiler_efficiency    
        
        # Turbogenerator efficiency
        @model.parameter(element=tea.BT, units='%', distribution=EGeff_dist)
        def set_turbogenerator_efficiency(turbo_generator_efficiency):
            tea.BT.turbogenerator_efficiency = turbo_generator_efficiency

    return model

def evaluate(biorefinery, N=100):
    model = create_model(biorefinery)
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model.sample(N, rule)
    model.load_samples(samples)
    model.evaluate()
    return model.table
