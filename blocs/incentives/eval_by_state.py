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
import blocs as blc
import numpy as np
import pandas as pd
import os

#Import state scenario data
folder = os.path.dirname(__file__)
st_data_file = os.path.join(folder, 'state_scenarios_for_import.xlsx')
st_data = pd.read_excel(st_data_file, index_col=[0])

all_states = [
            # 'Alabama',
            # 'Arkansas',
            # 'California',
            # 'Colorado',
            # 'Delaware',
            'Florida',
            # 'Georgia',
            # 'Iowa',
            # 'Illinois',
            # 'Indiana',
            # 'Kansas',
            # 'Kentucky',
            'Louisiana',
            # 'Maryland',
            # 'Michigan',
            # 'Minnesota',
            # 'Missouri',
            # 'Mississippi',
            # 'North Carolina',
            # 'North Dakota',
            # 'Nebraska',
            # 'New Jersey',
            # 'New York',
            # 'Ohio',
            # 'Oklahoma',
            # 'Pennsylvania',
            # 'South Carolina',
            # 'South Dakota',
            # 'Tennessee',
            'Texas',
            # 'Virginia',
            # 'Wisconsin',
            # 'West Virginia',
            # 'Montana',
            # 'New Mexico',
            # 'Oregon',
            # 'Utah',
            'Hawaii'
            ]

states_w_inc = [
                # 'Alabama',
                # 'Colorado',
                # 'Iowa',
                # 'Kansas',
                # 'Kentucky',
                'Louisiana',
                # 'Michigan',
                # 'Montana',
                # 'Nebraska',
                # 'New Mexico',
                # 'Oregon',
                # 'South Carolina',
                # 'Utah',
                # 'Virginia',
                'Hawaii'
                ]




# Model for state specific analysis ===========================================
def create_states_model(biorefinery):
    biorefinery = biorefinery.lower()
    if biorefinery == 'corn':
        tea = blc.create_corn_tea()
        name = 'CN'
    elif biorefinery == 'cornstover':
        name = 'CS'
        tea = blc.create_cornstover_tea()
    elif biorefinery == 'sugarcane':
        name = 'SC'
        tea = blc.create_sugarcane_tea()
    else:
        raise ValueError("invalid biorefinery; must be either "
                         "'corn', 'cornstover', or 'sugarcane'")
    
    model = bst.Model(tea.system, exception_hook='raise')
    bst.PowerUtility.price = 0.0685
    tea.fuel_tax = 0.05
    tea.sales_tax = 0.05785
    tea.federal_income_tax = 0.35
    tea.state_income_tax = 0.065
    tea.property_tax = 0.0136
    tea.F_investment = 1
    
    def get_state_incentives(state):
            avail_incentives = st_data.loc[state]['Incentives Available']
            avail_incentives = None if pd.isna(avail_incentives) else avail_incentives # no incentives
            if avail_incentives is not None:
                try: # multiple incentives
                    avail_incentives = [int(i) for i in avail_incentives if i.isnumeric()]
                except TypeError: # only one incentive
                    avail_incentives = [int(avail_incentives)]
            return avail_incentives

    def solve_price():
        try:
            MFSP = tea.solve_price(tea.ethanol_product)
        except:
            MFSP = tea.solve_price([tea.ethanol_product], [4])
        return 2.98668849 * MFSP

    def MFSP_getter(state):
        def MFSP():
            tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
            tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
            tea.fuel_tax = st_data.loc[state]['State Motor Fuel Tax (decimal)']
            tea.sales_tax = st_data.loc[state]['State Sales Tax Rate (decimal)']
            bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
            tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
            tea.incentive_numbers = ()
            tea.feedstock.price = st_data.loc[state][f'{name} Price (USD/kg)']
            
            if state == 'Ohio' or state == 'Texas':
                tea.state_tax_by_gross_receipts = True
            else:
                tea.state_tax_by_gross_receipts = False
            
            return solve_price()
        return MFSP
    
    def MFSP_w_inc_getter(state):
        def MFSP():
            tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
            tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
            tea.fuel_tax = st_data.loc[state]['State Motor Fuel Tax (decimal)']
            tea.sales_tax = st_data.loc[state]['State Sales Tax Rate (decimal)']
            bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
            tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
            # tea.incentive_numbers = get_state_incentives(state)
            tea.feedstock.price = st_data.loc[state][f'{name} Price (USD/kg)']
            
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
                tea.incentive_numbers = (13,14,22) #Incentive 14 should only be simulated here for corn or cellulosic feedstocks, i.e., NOT sugarcane
            elif state == 'Louisiana':
                tea.incentive_numbers = (15,)
            elif state == 'Michigan':
                tea.incentive_numbers = (3,)
            elif state == 'Montana':
                tea.incentive_numbers = (4,23) #TODO Incentive 23 should only be simulated here for grain feedstocks, i.e., corn
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
                
            return solve_price()
        return MFSP
    
    @model.metric(name='Utility cost', units='10^6 USD/yr')
    def get_utility_cost():
        return tea.utility_cost / 1e6
    
    @model.metric(name='Net electricity production', units='MWh/yr')
    def get_electricity_production():
        return sum(i.power_utility.rate for i in tea.system.units) * tea.operating_hours/1000
    
    @model.metric(name='Ethanol production', units='gal/yr')
    def get_ethanol_production():
        return tea.ethanol_product.F_mass * 2.98668849 * tea.operating_hours

    @model.metric(name='Total capital investment', units='USD')
    def get_TCI():
        return tea.TCI
    
    @model.metric(name="Baseline MFSP", units='USD/gal') #within this function, set whatever parameter values you want to use as the baseline
    def MFSP_baseline():
        tea.state_income_tax = 0
        tea.property_tax = 0.001
        tea.fuel_tax = 0
        tea.sales_tax = 0
        bst.PowerUtility.price = 0.0571675
        tea.F_investment = 1
        tea.incentive_numbers = ()
        MFSP = 2.98668849 * tea.solve_price(tea.ethanol_product)
        return MFSP
    
    get_inc_value = lambda: tea.exemptions.sum() + tea.deductions.sum() + tea.credits.sum()+ tea.refunds.sum()
    
    for state in all_states:
        model.metric(MFSP_getter(state), 'MFSP', 'USD/gal', state)
        
    for state in states_w_inc:
        model.metric(MFSP_w_inc_getter(state), 'Inc MFSP', 'USD/gal', state)
        model.metric(get_inc_value, 'Inc value', 'USD', state)
    
    
    ### Create parameter distributions ============================================
    # Feedstock prices, distribution taken from Yoel's example
    feedstock = tea.feedstock
    FP_L = feedstock.price * 0.9 # min price
    FP_M = feedstock.price       # avg price
    FP_U = feedstock.price * 1.1 # max price
    
    # Electricty generation efficiency
    EGeff_dist = shape.Triangle(0.7,0.85,0.9)
    
    ### Add Parameters =============================================================
    # Feedstock price
    @model.parameter(element=feedstock, kind='isolated', units='USD/kg',
                      distribution=triang(feedstock.price))
    def set_feed_price(feedstock_price):
        feedstock.price = feedstock_price
    
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

def evaluate_SS(biorefinery, N=10):
    model = create_states_model(biorefinery)
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model.sample(N, rule)
    model.load_samples(samples)
    model.evaluate()
    return model.table

def bsl_eval(biorefinery, N=10):
    model = create_states_model(biorefinery)
    model.load_default_parameters(blc.create_cornstover_tea().feedstock, operating_days=True)
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model.sample(N, rule)
    model.load_samples(samples)
    model.evaluate()
    sp_rho_table, sp_p_table = model.spearman_r()
    return model.table, sp_rho_table, sp_p_table
    
# fig, ax = bst.plots.plot_spearman_1d(sp_rho_table['Biorefinery']['Baseline MFSP [USD/gal]'])
# labels = [item.get_text() for item in ax.get_yticklabels()]
# ax.set_yticklabels(labels)