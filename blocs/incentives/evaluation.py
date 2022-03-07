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
import blocs as blc
import numpy as np
import pandas as pd
import os

#Import state scenario data
folder = os.path.dirname(__file__)
st_data_file = os.path.join(folder, 'state_scenarios_for_import.xlsx')
st_data = pd.read_excel(st_data_file, index_col=[0])


# Model for state specific analysis ===========================================
def create_states_model(biorefinery):
    biorefinery = biorefinery.lower()
    if biorefinery == 'corn':
        name = 'CN'
        tea = blc.create_corn_tea()
        all_states = [
                    'Alabama',
                    'Arizona',
                    'Arkansas',
                    'California',
                    'Colorado',
                    'Delaware',
                    'Florida',
                    'Georgia',
                    'Idaho',
                    'Illinois',
                    'Indiana',
                    'Iowa',
                    'Kansas',
                    'Kentucky',
                    'Louisiana',
                    'Maryland',
                    'Michigan',
                    'Minnesota',
                    'Mississippi',
                    'Missouri',
                    'Montana',
                    'Nebraska',
                    'New Jersey',
                    'New Mexico',
                    'New York',
                    'North Carolina',
                    'North Dakota',
                    'Ohio',
                    'Oklahoma',
                    'Oregon',
                    'Pennsylvania',
                    'South Carolina',
                    'South Dakota',
                    'Tennessee',
                    'Texas',
                    'Utah',
                    'Virginia',
                    'Washington',
                    'West Virginia',
                    'Wisconsin',
                    'Wyoming',
                    ]
        states_w_inc = [
                        'Alabama',
                        'Colorado',
                        'Iowa',
                        'Kansas',
                        'Kentucky',
                        'Louisiana',
                        'Montana',
                        'Nebraska',
                        'New Mexico',
                        'Oregon',
                        'South Carolina',
                        'Utah',
                        'Virginia',
                        ]
        
    elif biorefinery == 'cornstover':
        name = 'CS'
        tea = blc.create_cornstover_tea()
        all_states = [
                    'Alabama',
                    'Arizona',
                    'Arkansas',
                    'California',
                    'Colorado',
                    'Delaware',
                    'Florida',
                    'Georgia',
                    'Idaho',
                    'Illinois',
                    'Indiana',
                    'Iowa',
                    'Kansas',
                    'Kentucky',
                    'Louisiana',
                    'Maryland',
                    'Michigan',
                    'Minnesota',
                    'Mississippi',
                    'Missouri',
                    'Montana',
                    'Nebraska',
                    'New Jersey',
                    'New Mexico',
                    'New York',
                    'North Carolina',
                    'North Dakota',
                    'Ohio',
                    'Oklahoma',
                    'Oregon',
                    'Pennsylvania',
                    'South Carolina',
                    'South Dakota',
                    'Tennessee',
                    'Texas',
                    'Utah',
                    'Virginia',
                    'Washington',
                    'West Virginia',
                    'Wisconsin',
                    'Wyoming',
                    ]
        states_w_inc = [
                        'Alabama',
                        'Colorado',
                        'Iowa',
                        'Kansas',
                        'Kentucky',
                        'Louisiana',
                        'Montana',
                        'Nebraska',
                        'New Mexico',
                        'Oregon',
                        'South Carolina',
                        'Utah',
                        'Virginia',
                        ]
        
    elif biorefinery == 'sugarcane':
        name = 'SC'
        tea = blc.create_sugarcane_tea()
        all_states = [
            'Florida',
            'Hawaii',
            'Louisiana',
            'Texas',
            ]
        states_w_inc = [
            'Hawaii',
            'Louisiana'
            ]
    else:
        raise ValueError("invalid biorefinery; must be either "
                         "'corn', 'cornstover', or 'sugarcane'")
    
    model = bst.Model(tea.system, exception_hook='raise')
    bst.PowerUtility.price = 0.0685
    tea.fuel_tax = 0.
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
                if biorefinery == 'sugarcane':
                    tea.incentive_numbers = (13,22)
                else:
                    tea.incentive_numbers = (13,14,22)
            elif state == 'Louisiana':
                tea.incentive_numbers = (15,)
            elif state == 'Michigan':
                tea.incentive_numbers = (3,)
            elif state == 'Montana':
                if biorefinery == 'corn':
                    tea.incentive_numbers = (4,23)
                else:
                    tea.incentive_numbers = (4,)
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
        return tea.ethanol_product.F_mass / 2.98668849 * tea.operating_hours

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
    
    ### Add Parameters =============================================================
    feedstock = tea.feedstock
    kg_per_ton = 907.185
    def param(name, baseline, bounds=None, **kwargs):
        lb = 0.9 * baseline
        ub = 1.1 * baseline
        if bounds is not None:
            if lb < bounds[0]:
                lb = bounds[0]
            if ub > bounds[1]:
                ub = bounds[1]
        distribution = shape.Uniform(lb, ub)
        return model.parameter(name=name, bounds=bounds, distribution=distribution, baseline=baseline, **kwargs)

    if biorefinery == 'corn':
        
        @param(name='Corn price', element=feedstock, kind='isolated',
               units='USD/ton', baseline=feedstock.price * kg_per_ton)
        def set_corn_price(price):
            feedstock.price = price / kg_per_ton
            
        @model.parameter(element=tea.V405, kind='coupled', units='%',
                          distribution=shape.Triangle(0.9,0.95,1))
        def set_ferm_efficiency(conversion):
            tea.V405.reaction.X = conversion
        
        @param(name='DDGS price', element=tea.DDGS, kind='isolated', 
               units='USD/ton', baseline=tea.DDGS.price * kg_per_ton)
        def set_DDGS_price(price):
            tea.DDGS.price = price / kg_per_ton
            
        @param(name='Crude oil price', element=tea.crude_oil, kind='isolated', 
               units='USD/ton', baseline=tea.crude_oil.price * kg_per_ton)
        def set_crude_oil_price(price):
            tea.crude_oil.price = price / kg_per_ton
            
        @param(name='Electricity price', element='TEA', kind='isolated', units='USD/kWh',
               baseline=bst.PowerUtility.price)
        def set_electricity_price(price):
            bst.PowerUtility.price = price  

    elif biorefinery == 'cornstover':   
        cornstover = feedstock
        pretreatment_conversions = tea.R201.reactions.X
        cofermentation_conversions = tea.R303.cofermentation.X
        saccharification_conversions = tea.R303.saccharification.X
       
        @param(name='Cornstover price', element=cornstover, kind='isolated', 
               units='USD/ton', baseline=cornstover.price * kg_per_ton)
        def set_cornstover_price(price):
            cornstover.price = price / kg_per_ton
            
        @param(name='Enzyme price', element=tea.cellulase, kind='isolated',
               description='price of cellulase enzyme mixture containing 50 g of cellulase per 1000g of cocktail',
               units='$USD/ton', baseline=tea.cellulase.price * kg_per_ton)
        def set_cellulase_price(price):
            tea.cellulase.price = price / kg_per_ton

        @param(name='Electricity price', element='TEA', kind='isolated', units='USD/kWh',
               baseline=bst.PowerUtility.price)
        def set_electricity_price(price):
            bst.PowerUtility.price = price    

        @param(name='Plant capacity', element=cornstover, kind='coupled', units='dry US ton/yr',
               baseline=(cornstover.F_mass - cornstover.imass['H2O']) * tea.operating_hours / kg_per_ton,
               description="annual feestock processing capacity")
        def set_plant_size(flow_rate):
            dry_content = 1 - cornstover.imass['H2O'] / cornstover.F_mass
            cornstover.F_mass = flow_rate / tea.operating_hours / dry_content * kg_per_ton

        @param(name='PT glucan-to-glucose', element=tea.R201, kind='coupled', units='% theoretical',
               description='extent of reaction, glucan + water -> glucose, in pretreatment reactor',
               baseline=pretreatment_conversions[0] * 100,
               bounds=(0, 100))
        def set_PT_glucan_to_glucose(X):
            X /= 100.
            pretreatment_conversions[0] = X
            corxns = pretreatment_conversions[1:3] 
            corxns[:] = 0.003
            if pretreatment_conversions[:3].sum() > 1.:
                f = corxns / corxns.sum()
                corxns[:] = f * (1. - X) * 0.9999999

        @param(name='PT xylan-to-xylose', element=tea.R201, kind='coupled', units='% theoretical',
               description='extent of reaction, xylan + water -> xylose, in pretreatment reactor',
               baseline=pretreatment_conversions[8] * 100,
               bounds=(0, 100))
        def set_PT_xylan_to_xylose(X):
            X /= 100.
            pretreatment_conversions[8] = X
            corxns = pretreatment_conversions[9:11] 
            corxns[:] = [0.024, 0.05]
            if pretreatment_conversions[8:11].sum() > 1.:
                f = corxns / corxns.sum()
                corxns[:] = f * (1. - X) * 0.9999999

        @param(name='PT xylan-to-furfural', element=tea.R201, kind='coupled', units='% theoretical',
               description='extent of reaction, xylan -> furfural + 2 water, in pretreatment reactor',
               baseline=pretreatment_conversions[10] * 100,
               bounds=(0, 100))
        def set_PT_xylan_to_furfural(X):
            # To make sure the overall xylan conversion doesn't exceed 100%
            lb = 1. - pretreatment_conversions[8] - pretreatment_conversions[9]
            pretreatment_conversions[10] = min(lb, X / 100.) * 0.9999999

        @param(name='EH cellulose-to-glucose', element=tea.R303, kind='coupled', units='% theoretical',
               description='extent of reaction, gluan + water -> glulose, in enzyme hydrolysis',
               baseline=saccharification_conversions[2] * 100,
               bounds=(0, 100))
        def set_EH_glucan_to_glucose(X):
            X /= 100.
            saccharification_conversions[2] = X
            corxns = saccharification_conversions[:2] 
            corxns[:] = [0.04, 0.0012]
            if saccharification_conversions[:3].sum() > 1.:
                f = corxns / corxns.sum()
                corxns[:] = f * (1. - X) * 0.9999999

        @param(name='FERM glucose-to-ethanol', element=tea.R303, kind='coupled', units='% theoretical',
               description='extent of reaction, glucose -> 2 ethanol + 2 CO2, in enzyme hydrolysis',
               baseline=cofermentation_conversions[0] * 100,
               bounds=(0, 100))
        def set_FERM_glucose_to_ethanol(X):
            X /= 100.
            cofermentation_conversions[0] = X
            corxns = cofermentation_conversions[1:4] 
            corxns[:] = [0.02, 0.0004, 0.006]
            if cofermentation_conversions[:4].sum() > 1.:
                f = corxns / corxns.sum()
                corxns[:] = f * (1. - X) * 0.9999999

        @param(name='Boiler efficiency', element=tea.BT, kind='coupled', units='%',
               description='efficiency of burning fuel to produce steam',
               baseline=tea.BT.boiler_efficiency * 100,
               bounds=(0, 100))
        def set_boiler_efficiency(X):
            tea.BT.boiler_efficiency = X / 100.

        @param(name='Turbogenerator efficiency', element=tea.BT, kind='coupled', units='%',
               description='efficiency of converting steam to power',
               baseline=tea.BT.turbogenerator_efficiency * 100,
               bounds=(0, 100))
        def set_turbogenerator_efficiency(X):
            tea.BT.turbogenerator_efficiency = X / 100.
        
    elif biorefinery == 'sugarcane':
        
        @param(name='Sugarcane price', element=feedstock, kind='isolated',
               units='USD/ton', baseline=feedstock.price * kg_per_ton)
        def set_sugarcane_price(price):
            feedstock.price = price / kg_per_ton
            
        @model.parameter(element=tea.R301, kind='coupled', units='%',
                         distribution=shape.Triangle(0.85,0.9,0.95))
        def set_ferm_efficiency(eff):
            tea.R301.efficiency = eff
        
        @param(name='Vinasse price', element=tea.vinasse, kind='isolated',
               units='USD/ton', baseline=tea.vinasse.price * kg_per_ton)
        def set_vinasse_price(price):
            tea.vinasse.price = price / kg_per_ton
        
        @param(name='Boiler efficiency', element=tea.BT, kind='coupled', units='%',
               description='efficiency of burning fuel to produce steam',
               baseline=tea.BT.boiler_efficiency * 100,
               bounds=(0, 100))
        def set_boiler_efficiency(X):
            tea.BT.boiler_efficiency = X / 100.

        @param(name='Turbogenerator efficiency', element=tea.BT, kind='coupled', units='%',
               description='efficiency of converting steam to power',
               baseline=tea.BT.turbogenerator_efficiency * 100,
               bounds=(0, 100))
        def set_turbogenerator_efficiency(X):
            tea.BT.turbogenerator_efficiency = X / 100.
            
        @param(name='Electricity price', element='TEA', kind='isolated', units='USD/kWh',
               baseline=bst.PowerUtility.price)
        def set_electricity_price(price):
            bst.PowerUtility.price = price  

    return model

def evaluate_SS(biorefinery, N=3000):
    model = create_states_model(biorefinery)
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model.sample(N, rule)
    model.load_samples(samples)
    model.evaluate()
    return model.table

# Model for state specific analysis ===========================================
def create_IPs_model(biorefinery):
    biorefinery = biorefinery.lower()
    if biorefinery == 'corn':
        name = 'CN'
        tea = blc.create_corn_tea()
        tea.feedstock.price = 0.1461
        
    elif biorefinery == 'cornstover':
        name = 'CS'
        tea = blc.create_cornstover_tea()
        tea.feedstock.price = 0.0990
        
    elif biorefinery == 'sugarcane':
        name = 'SC'
        tea = blc.create_sugarcane_tea()
        tea.feedstock.price = 0.0427
        
    else:
        raise ValueError("invalid biorefinery; must be either "
                         "'corn', 'cornstover', or 'sugarcane'")
    
    model = bst.Model(tea.system, exception_hook='raise')
    bst.PowerUtility.price = 0.0685
    tea.fuel_tax = 0.
    tea.sales_tax = 0.05785
    tea.federal_income_tax = 0.35
    tea.state_income_tax = 0.065
    tea.property_tax = 0.0136
    tea.F_investment = 1

    def solve_price():
        try:
            MFSP = tea.solve_price(tea.ethanol_product)
        except:
            MFSP = tea.solve_price([tea.ethanol_product], [4])
        return 2.98668849 * MFSP
    
    @model.metric(name='Utility cost', units='10^6 USD/yr')
    def get_utility_cost():
        return tea.utility_cost / 1e6
    
    @model.metric(name='Net electricity production', units='MWh/yr')
    def get_electricity_production():
        return sum(i.power_utility.rate for i in tea.system.units) * tea.operating_hours/1000
    
    @model.metric(name='Ethanol production', units='gal/yr')
    def get_ethanol_production():
        return tea.ethanol_product.F_mass / 2.98668849 * tea.operating_hours

    @model.metric(name='Total capital investment', units='USD')
    def get_TCI():
        return tea.TCI
    
    @model.metric(name='Ethanol equipment cost', units='USD')
    def get_ETOH_eq():
        if tea.lang_factor:
            ethanol_eq = 1e6 * tea.lang_factor * tea.ethanol_group.get_purchase_cost()
        else:
            ethanol_eq = 1e6 * tea.ethanol_group.get_installed_cost()
        return ethanol_eq

    @model.metric(name='Electricity equipment cost', units='USD')
    def get_elec_eq():
        if tea.lang_factor:
            elec_eq = tea.lang_factor * tea.BT.purchase_cost if tea.BT else 0.
        else:
            elec_eq = tea.BT.installed_cost if tea.BT else 0.
        return elec_eq

    @model.metric(name='NM value', units='USD')
    def get_NM_value():
        if tea.lang_factor:
            elec_eq = tea.lang_factor * tea.BT.purchase_cost if tea.BT else 0.
        else:
            elec_eq = tea.BT.installed_cost if tea.BT else 0.
        feedstock_value = feedstock.cost * tea.operating_hours * (tea._years + tea._start)
        return elec_eq + feedstock_value

    @model.metric(name='IA value', units='USD')
    def get_IA_value():
        if tea.lang_factor:
            conveyor_costs = tea.lang_factor * sum([i.purchase_cost for i in tea.units if isinstance(i, bst.ConveyingBelt)])
        else:
            conveyor_costs = sum([i.installed_cost for i in tea.units if isinstance(i, bst.ConveyingBelt)])
        return conveyor_costs

    @model.metric(name='Building materials', units='USD')
    def get_building_mats():
        return tea.purchase_cost

    @model.metric(name='Assessed income tax', units='USD')
    def get_inc_tax():
        return tea.state_income_tax * tea.sales

    @model.metric(name='Assessed fuel tax', units='USD')
    def get_fuel_tax():
        return tea.fuel_tax * get_ethanol_production.get()
    
    @model.metric(name="Baseline MFSP", units='USD/gal') #within this function, set whatever parameter values you want to use as the baseline
    def MFSP_baseline():
        tea.incentive_numbers = ()
        MFSP_baseline_box[0] = MFSP = 2.98668849 * tea.solve_price(tea.ethanol_product)
        return MFSP

    MFSP_baseline_box = [None]

    get_exemptions = lambda: tea.exemptions.sum()
    get_deductions = lambda: tea.deductions.sum()
    get_credits = lambda: tea.credits.sum()
    get_refunds = lambda: tea.refunds.sum()
    
    def MFSP_getter(incentive_number):
        def MFSP():
            tea.incentive_numbers = (incentive_number,)
            return 2.98668849 * tea.solve_price(tea.ethanol_product)
        return MFSP

    def MFSP_reduction_getter(incentive_number):
        def MFSP():
            tea.incentive_numbers = (incentive_number,)
            return (2.98668849 * tea.solve_price(tea.ethanol_product) - MFSP_baseline_box[0])
        return MFSP

    for incentive_number in range(1, 24):
        element = f"Incentive {incentive_number}"
        model.metric(MFSP_getter(incentive_number), 'MFSP', 'USD/gal', element)
        model.metric(MFSP_reduction_getter(incentive_number), 'MFSP Reduction', 'USD/gal', element)
        model.metric(get_exemptions, 'Exemptions', 'USD', element)
        model.metric(get_deductions, 'Deductions', 'USD', element)
        model.metric(get_credits, 'Credits', 'USD', element)
        model.metric(get_refunds, 'Refunds', 'USD', element)
    
    ### Add Parameters =============================================================
    feedstock = tea.feedstock
    kg_per_ton = 907.185
    def param(name, baseline, bounds=None, **kwargs):
        lb = 0.9 * baseline
        ub = 1.1 * baseline
        if bounds is not None:
            if lb < bounds[0]:
                lb = bounds[0]
            if ub > bounds[1]:
                ub = bounds[1]
        distribution = shape.Uniform(lb, ub)
        return model.parameter(name=name, bounds=bounds, distribution=distribution, baseline=baseline, **kwargs)

    if biorefinery == 'corn':
        
        @param(name='Corn price', element=feedstock, kind='isolated',
               units='USD/ton', baseline=feedstock.price * kg_per_ton)
        def set_corn_price(price):
            feedstock.price = price / kg_per_ton
            
        @model.parameter(element=tea.V405, kind='coupled', units='%',
                          distribution=shape.Triangle(0.9,0.95,1))
        def set_ferm_efficiency(conversion):
            tea.V405.reaction.X = conversion
        
        @param(name='DDGS price', element=tea.DDGS, kind='isolated', 
               units='USD/ton', baseline=tea.DDGS.price * kg_per_ton)
        def set_DDGS_price(price):
            tea.DDGS.price = price / kg_per_ton
            
        @param(name='Crude oil price', element=tea.crude_oil, kind='isolated', 
               units='USD/ton', baseline=tea.crude_oil.price * kg_per_ton)
        def set_crude_oil_price(price):
            tea.crude_oil.price = price / kg_per_ton
            
        @param(name='Electricity price', element='TEA', kind='isolated', units='USD/kWh',
               baseline=bst.PowerUtility.price)
        def set_electricity_price(price):
            bst.PowerUtility.price = price  

    elif biorefinery == 'cornstover':   
        cornstover = feedstock
        pretreatment_conversions = tea.R201.reactions.X
        cofermentation_conversions = tea.R303.cofermentation.X
        saccharification_conversions = tea.R303.saccharification.X
       
        @param(name='Cornstover price', element=cornstover, kind='isolated', 
               units='USD/ton', baseline=cornstover.price * kg_per_ton)
        def set_cornstover_price(price):
            cornstover.price = price / kg_per_ton
            
        @param(name='Enzyme price', element=tea.cellulase, kind='isolated',
               description='price of cellulase enzyme mixture containing 50 g of cellulase per 1000g of cocktail',
               units='$USD/ton', baseline=tea.cellulase.price * kg_per_ton)
        def set_cellulase_price(price):
            tea.cellulase.price = price / kg_per_ton

        @param(name='Electricity price', element='TEA', kind='isolated', units='USD/kWh',
               baseline=bst.PowerUtility.price)
        def set_electricity_price(price):
            bst.PowerUtility.price = price    

        @param(name='Plant capacity', element=cornstover, kind='coupled', units='dry US ton/yr',
               baseline=(cornstover.F_mass - cornstover.imass['H2O']) * tea.operating_hours / kg_per_ton,
               description="annual feestock processing capacity")
        def set_plant_size(flow_rate):
            dry_content = 1 - cornstover.imass['H2O'] / cornstover.F_mass
            cornstover.F_mass = flow_rate / tea.operating_hours / dry_content * kg_per_ton

        @param(name='PT glucan-to-glucose', element=tea.R201, kind='coupled', units='% theoretical',
               description='extent of reaction, glucan + water -> glucose, in pretreatment reactor',
               baseline=pretreatment_conversions[0] * 100,
               bounds=(0, 100))
        def set_PT_glucan_to_glucose(X):
            X /= 100.
            pretreatment_conversions[0] = X
            corxns = pretreatment_conversions[1:3] 
            corxns[:] = 0.003
            if pretreatment_conversions[:3].sum() > 1.:
                f = corxns / corxns.sum()
                corxns[:] = f * (1. - X) * 0.9999999

        @param(name='PT xylan-to-xylose', element=tea.R201, kind='coupled', units='% theoretical',
               description='extent of reaction, xylan + water -> xylose, in pretreatment reactor',
               baseline=pretreatment_conversions[8] * 100,
               bounds=(0, 100))
        def set_PT_xylan_to_xylose(X):
            X /= 100.
            pretreatment_conversions[8] = X
            corxns = pretreatment_conversions[9:11] 
            corxns[:] = [0.024, 0.05]
            if pretreatment_conversions[8:11].sum() > 1.:
                f = corxns / corxns.sum()
                corxns[:] = f * (1. - X) * 0.9999999

        @param(name='PT xylan-to-furfural', element=tea.R201, kind='coupled', units='% theoretical',
               description='extent of reaction, xylan -> furfural + 2 water, in pretreatment reactor',
               baseline=pretreatment_conversions[10] * 100,
               bounds=(0, 100))
        def set_PT_xylan_to_furfural(X):
            # To make sure the overall xylan conversion doesn't exceed 100%
            lb = 1. - pretreatment_conversions[8] - pretreatment_conversions[9]
            pretreatment_conversions[10] = min(lb, X / 100.) * 0.9999999

        @param(name='EH cellulose-to-glucose', element=tea.R303, kind='coupled', units='% theoretical',
               description='extent of reaction, gluan + water -> glulose, in enzyme hydrolysis',
               baseline=saccharification_conversions[2] * 100,
               bounds=(0, 100))
        def set_EH_glucan_to_glucose(X):
            X /= 100.
            saccharification_conversions[2] = X
            corxns = saccharification_conversions[:2] 
            corxns[:] = [0.04, 0.0012]
            if saccharification_conversions[:3].sum() > 1.:
                f = corxns / corxns.sum()
                corxns[:] = f * (1. - X) * 0.9999999

        @param(name='FERM glucose-to-ethanol', element=tea.R303, kind='coupled', units='% theoretical',
               description='extent of reaction, glucose -> 2 ethanol + 2 CO2, in enzyme hydrolysis',
               baseline=cofermentation_conversions[0] * 100,
               bounds=(0, 100))
        def set_FERM_glucose_to_ethanol(X):
            X /= 100.
            cofermentation_conversions[0] = X
            corxns = cofermentation_conversions[1:4] 
            corxns[:] = [0.02, 0.0004, 0.006]
            if cofermentation_conversions[:4].sum() > 1.:
                f = corxns / corxns.sum()
                corxns[:] = f * (1. - X) * 0.9999999

        @param(name='Boiler efficiency', element=tea.BT, kind='coupled', units='%',
               description='efficiency of burning fuel to produce steam',
               baseline=tea.BT.boiler_efficiency * 100,
               bounds=(0, 100))
        def set_boiler_efficiency(X):
            tea.BT.boiler_efficiency = X / 100.

        @param(name='Turbogenerator efficiency', element=tea.BT, kind='coupled', units='%',
               description='efficiency of converting steam to power',
               baseline=tea.BT.turbogenerator_efficiency * 100,
               bounds=(0, 100))
        def set_turbogenerator_efficiency(X):
            tea.BT.turbogenerator_efficiency = X / 100.
        
    elif biorefinery == 'sugarcane':
        
        @param(name='Sugarcane price', element=feedstock, kind='isolated',
               units='USD/ton', baseline=feedstock.price * kg_per_ton)
        def set_sugarcane_price(price):
            feedstock.price = price / kg_per_ton
            
        @model.parameter(element=tea.R301, kind='coupled', units='%',
                         distribution=shape.Triangle(0.85,0.9,0.95))
        def set_ferm_efficiency(eff):
            tea.R301.efficiency = eff
        
        @param(name='Vinasse price', element=tea.vinasse, kind='isolated',
               units='USD/ton', baseline=tea.vinasse.price * kg_per_ton)
        def set_vinasse_price(price):
            tea.vinasse.price = price / kg_per_ton
        
        @param(name='Boiler efficiency', element=tea.BT, kind='coupled', units='%',
               description='efficiency of burning fuel to produce steam',
               baseline=tea.BT.boiler_efficiency * 100,
               bounds=(0, 100))
        def set_boiler_efficiency(X):
            tea.BT.boiler_efficiency = X / 100.

        @param(name='Turbogenerator efficiency', element=tea.BT, kind='coupled', units='%',
               description='efficiency of converting steam to power',
               baseline=tea.BT.turbogenerator_efficiency * 100,
               bounds=(0, 100))
        def set_turbogenerator_efficiency(X):
            tea.BT.turbogenerator_efficiency = X / 100.
            
        @param(name='Electricity price', element='TEA', kind='isolated', units='USD/kWh',
               baseline=bst.PowerUtility.price)
        def set_electricity_price(price):
            bst.PowerUtility.price = price  

    return model

def evaluate_IP(biorefinery, N=3000):
    model = create_IPs_model(biorefinery)
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model.sample(N, rule)
    model.load_samples(samples)
    model.evaluate()
    return model.table
    
# fig, ax = bst.plots.plot_spearman_1d(sp_rho_table['Biorefinery']['Baseline MFSP [USD/gal]'])
# labels = [item.get_text() for item in ax.get_yticklabels()]
# ax.set_yticklabels(labels)