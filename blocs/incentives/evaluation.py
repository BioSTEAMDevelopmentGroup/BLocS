#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Examples
--------
>>> models = [create_model(i) for i in ('corn', 'sugarcane', 'cornstover')]
>>> dfs = [evaluate(i) for i in ('corn', 'sugarcane', 'cornstover')]


"""
import flexsolve as flx
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
results_folder = os.path.join(folder, 'results')

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
                    'Arkansas',
                    'California',
                    'Colorado',
                    'Delaware',
                    'Florida',
                    'Georgia',
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
                    'West Virginia',
                    'Wisconsin',
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
    tea.federal_income_tax = 0.21
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
                tea.incentive_numbers = (7,)
            elif state == 'Colorado':
                tea.incentive_numbers = (8,)
            elif state == 'Hawaii':
                tea.incentive_numbers = (9,)
            elif state == 'Iowa':
                tea.incentive_numbers = (1,10,18)
            elif state == 'Kansas':
                tea.incentive_numbers = (2,)
            elif state == 'Kentucky':
                if biorefinery == 'sugarcane':
                    tea.incentive_numbers = (11,19)
                else:
                    tea.incentive_numbers = (11,12,19) #need to cap value of incs 11+12 at inc tax amt
            elif state == 'Louisiana':
                tea.incentive_numbers = (13,)
            elif state == 'Montana':
                if biorefinery == 'corn':
                    tea.incentive_numbers = (3,20)
                else:
                    tea.incentive_numbers = (3,)
            elif state == 'Nebraska':
                tea.incentive_numbers = (4,)
            elif state == 'New Mexico':
                tea.incentive_numbers = (6,)
            elif state == 'Oregon':
                tea.incentive_numbers = (5,)
            elif state == 'South Carolina':
                tea.incentive_numbers = (14,15)
            elif state == 'Utah':
                tea.incentive_numbers = (16,)
            elif state == 'Virginia':
                tea.incentive_numbers = (17,)
                
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
    model.evaluate(**evaluate_args('SS'))
    model.table.to_excel(get_file_name('SS.xlsx'))
    return model.table

# Model for analysis by incentivized parameters ===========================================
def create_IPs_model(biorefinery):
    biorefinery = biorefinery.lower()
    if biorefinery == 'corn':
        tea = blc.create_corn_tea()
        tea.feedstock.price = 0.1461
        
    elif biorefinery == 'cornstover':
        tea = blc.create_cornstover_tea()
        tea.feedstock.price = 0.0990
        
    elif biorefinery == 'sugarcane':
        tea = blc.create_sugarcane_tea()
        tea.feedstock.price = 0.0427
        
    else:
        raise ValueError("invalid biorefinery; must be either "
                         "'corn', 'cornstover', or 'sugarcane'")
    
    model = bst.Model(tea.system, exception_hook='raise')
    bst.PowerUtility.price = 0.0685
    tea.fuel_tax = 0.
    tea.sales_tax = 0.05785
    tea.federal_income_tax = 0.21
    tea.state_income_tax = 0.065
    tea.property_tax = 0.0136
    tea.F_investment = 1

    def solve_price():
        try:
            MFSP = tea.solve_price(tea.ethanol_product)
        except:
            original_price = tea.ethanol_product.price
            def f(price):
                tea.ethanol_product.price = price
                return tea.NPV
            (x0, x1, y0, y1) = flx.find_bracket(f, 0, 10)
            MFSP = flx.IQ_interpolation(f, x0, x1, y0, y1, xtol=1e-3, ytol=1e4, maxiter=100000)
            tea.ethanol_product.price = original_price
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
    
    @model.metric(name='Fixed capital investment', units='USD')
    def get_FCI():
        return tea.FCI
    
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
        return solve_price()

    @model.metric(name="Ethanol production cost", units='USD/gal')
    def ethanol_production_cost():
        return tea.total_production_cost([tea.ethanol_product], with_annual_depreciation=False) / get_ethanol_production.get()

    get_exemptions = lambda: tea.exemptions.sum()
    get_deductions = lambda: tea.deductions.sum()
    get_credits = lambda: tea.credits.sum()
    get_refunds = lambda: tea.refunds.sum()
    
    def MFSP_getter(incentive_number):
        def MFSP():
            tea.incentive_numbers = (incentive_number,)
            return solve_price()
        return MFSP

    def MFSP_reduction_getter(incentive_number):
        def MFSP():
            tea.incentive_numbers = (incentive_number,)
            return solve_price() - MFSP_baseline.get()
        return MFSP

    for incentive_number in range(1, 21):
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
    
    # TODO Only activate these first 6 parameters when using evaluate_across_X_parameter functions
    # State income tax
    # SITR_dist = shape.Triangle(0, 0.065, 0.12)
    # @model.parameter(element='TEA', kind='isolated', units='%', distribution=SITR_dist)
    # def set_state_income_tax(State_income_tax_rate):
    #     tea.state_income_tax = State_income_tax_rate
    
    # Property tax
    # SPTR_dist = shape.Triangle(0.0, 0.0136, 0.04)
    # @model.parameter(element='TEA', kind='isolated', units='%', distribution=SPTR_dist) 
    # def set_state_property_tax(State_property_tax_rate):
    #     tea.property_tax = State_property_tax_rate
        
    # State motor fuel tax
    # SMFTR_dist = shape.Triangle(0, 0, 0.1)
    # @model.parameter(element='TEA', kind='isolated', units='USD/gal', distribution=SMFTR_dist)
    # def set_motor_fuel_tax(fuel_tax_rate):
    #     tea.fuel_tax = fuel_tax_rate
        
    # State sales tax
    # SSTR_dist = shape.Triangle(0, 0.05875, 0.0725)
    # @model.parameter(element='TEA', kind='isolated', units='%', distribution=SSTR_dist)
    # def set_sales_tax(sales_tax_rate):
    #     tea.sales_tax = sales_tax_rate

    # Electricity price
    elec_utility = bst.PowerUtility
    EP_dist = shape.Triangle(0.0471, 0.0685, 0.1007)
    @model.parameter(element=elec_utility, kind='isolated', units='USD/kWh',
                      distribution=EP_dist)
    def set_elec_price(electricity_price):
          elec_utility.price = electricity_price
          
    # Location capital cost factor
    # LCCF_dist = shape.Triangle(0.8, 1, 1.2)
    # @model.parameter(element='LCCF', kind='isolated', units='unitless', distribution=LCCF_dist)
    # def set_LCCF(LCCF):
    #     tea.F_investment = LCCF

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
            
        # @param(name='Electricity price', element='TEA', kind='isolated', units='USD/kWh',
        #         baseline=bst.PowerUtility.price)
        # def set_electricity_price(price):
        #     bst.PowerUtility.price = price  

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

        # @param(name='Electricity price', element='TEA', kind='isolated', units='USD/kWh',
        #        baseline=bst.PowerUtility.price)
        # def set_electricity_price(price):
        #     bst.PowerUtility.price = price    

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
            
        # @param(name='Electricity price', element='TEA', kind='isolated', units='USD/kWh',
        #        baseline=bst.PowerUtility.price)
        # def set_electricity_price(price):
        #     bst.PowerUtility.price = price  

    return model

def get_file_name(name):
    return os.path.join(results_folder, name)

def evaluate_args(name, nbox=None):
    if nbox is None:
        return {'autoload': True,
                'autosave': 20,
                'file': get_file_name(name)}
    else:
        nbox[0] += 1
        return {'autoload': True,
                'autosave': 20,
                'file': get_file_name(os.path.join(name, str(nbox[0])))}

def evaluate_IP(biorefinery, N=3000):
    model = create_IPs_model(biorefinery)
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model.sample(N, rule)
    model.load_samples(samples)
    model.evaluate(**evaluate_args('IP'))
    model.table.to_excel(get_file_name('IP.xlsx'))
    return model.table

#Evaluate across property tax
def evaluate_propT(biorefinery, N=1000):
    model = create_IPs_model(biorefinery)
    if biorefinery == 'corn':
        tea = blc.create_corn_tea()
        tea.feedstock.price = 0.1461
        
    elif biorefinery == 'cornstover':
        tea = blc.create_cornstover_tea()
        tea.feedstock.price = 0.0990
        
    elif biorefinery == 'sugarcane':
        tea = blc.create_sugarcane_tea()
        tea.feedstock.price = 0.0427
        
    parameters = list(model.get_parameters())
    for parameter in parameters:
        if parameter.name == 'State property tax rate':#TODO change this before running
            set_state_property_tax = parameter
            parameters.remove(parameter)
            break
    model_ = bst.Model(tea.system,
                       metrics=model.metrics,
                       parameters=parameters,
                       exception_hook='raise')
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model_.sample(N, rule)
    model_.load_samples(samples)
    nbox = [0]
    def f_evaluate(notify=True):
        model_.evaluate(**evaluate_args('propT', nbox), notify=20)
    return model_.evaluate_across_coordinate(
                                            '[TEA] State property tax rate (%)', #TODO change this before running
                                            set_state_property_tax, #TODO change this before running
                                            np.linspace(
                                            set_state_property_tax.distribution.lower.min(), #TODO change this before running
                                            set_state_property_tax.distribution.upper.max(), #TODO change this before running
                                            8,), #TODO change this before running
                                            xlfile=get_file_name('Eval_across_st_prop_tax.xlsx'), #TODO change this before running
                                            notify=True,
                                            f_evaluate=f_evaluate,
                                            )

#Evaluate across state income tax
def evaluate_incT(biorefinery, N=1000):
    model = create_IPs_model(biorefinery)
    if biorefinery == 'corn':
        tea = blc.create_corn_tea()
        tea.feedstock.price = 0.1461
        
    elif biorefinery == 'cornstover':
        tea = blc.create_cornstover_tea()
        tea.feedstock.price = 0.0990
        
    elif biorefinery == 'sugarcane':
        tea = blc.create_sugarcane_tea()
        tea.feedstock.price = 0.0427
        
    parameters = list(model.get_parameters())
    for parameter in parameters:
        if parameter.name == 'State income tax rate':
            set_state_income_tax = parameter
            parameters.remove(parameter)
            break
    model_ = bst.Model(tea.system,
                       metrics=model.metrics,
                       parameters=parameters,
                       exception_hook='raise')
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model_.sample(N, rule)
    model_.load_samples(samples)
    nbox = [0]
    def f_evaluate(notify=True):
        model_.evaluate(**evaluate_args('incT', nbox), notify=20)
    return model_.evaluate_across_coordinate(
                                            '[TEA] State income tax rate (%)', 
                                            set_state_income_tax, 
                                            np.linspace(
                                            set_state_income_tax.distribution.lower.min(), 
                                            set_state_income_tax.distribution.upper.max(), 
                                            24,), 
                                            xlfile=get_file_name('Eval_across_st_inc_tax.xlsx'), 
                                            notify=True,
                                            f_evaluate=f_evaluate,
                                            )

#Evaluate across fuel tax
def evaluate_fuelT(biorefinery, N=1000):
    model = create_IPs_model(biorefinery)
    if biorefinery == 'corn':
        tea = blc.create_corn_tea()
        tea.feedstock.price = 0.1461
        
    elif biorefinery == 'cornstover':
        tea = blc.create_cornstover_tea()
        tea.feedstock.price = 0.0990
        
    elif biorefinery == 'sugarcane':
        tea = blc.create_sugarcane_tea()
        tea.feedstock.price = 0.0427
        
    parameters = list(model.get_parameters())
    for parameter in parameters:
        if parameter.name == 'Fuel tax rate':
            set_motor_fuel_tax = parameter
            parameters.remove(parameter)
            break
    model_ = bst.Model(tea.system,
                       metrics=model.metrics,
                       parameters=parameters,
                       exception_hook='raise')
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model_.sample(N, rule)
    model_.load_samples(samples)
    nbox = [0]
    def f_evaluate(notify=True):
        model_.evaluate(**evaluate_args('fuelT', nbox), notify=20)
    return model_.evaluate_across_coordinate(
                                            '[TEA] Fuel tax rate (%)', 
                                            set_motor_fuel_tax, 
                                            np.linspace(
                                            set_motor_fuel_tax.distribution.lower.min(), 
                                            set_motor_fuel_tax.distribution.upper.max(), 
                                            20,), 
                                            xlfile=get_file_name('Eval_across_fuel_tax.xlsx'), 
                                            notify=True,
                                            f_evaluate=f_evaluate,
                                            )

#Evaluate across sales tax
def evaluate_saleT(biorefinery, N=1000):
    model = create_IPs_model(biorefinery)
    if biorefinery == 'corn':
        tea = blc.create_corn_tea()
        tea.feedstock.price = 0.1461
        
    elif biorefinery == 'cornstover':
        tea = blc.create_cornstover_tea()
        tea.feedstock.price = 0.0990
        
    elif biorefinery == 'sugarcane':
        tea = blc.create_sugarcane_tea()
        tea.feedstock.price = 0.0427
        
    parameters = list(model.get_parameters())
    for parameter in parameters:
        if parameter.name == 'Sales tax rate':
            set_sales_tax = parameter
            parameters.remove(parameter)
            break
    model_ = bst.Model(tea.system,
                       metrics=model.metrics,
                       parameters=parameters,
                       exception_hook='raise')
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model_.sample(N, rule)
    model_.load_samples(samples)
    nbox = [0]
    def f_evaluate(notify=True):
        model_.evaluate(**evaluate_args('saleT', nbox), notify=20)
    return model_.evaluate_across_coordinate(
                                            '[TEA] State sales tax rate (%)',
                                            set_sales_tax, 
                                            np.linspace(
                                            set_sales_tax.distribution.lower.min(), 
                                            set_sales_tax.distribution.upper.max(), 
                                            14,), 
                                            xlfile=get_file_name('Eval_across_st_sales_tax.xlsx'), 
                                            notify=True,
                                            f_evaluate=f_evaluate,
                                            )

#Evaluate across LCCF
def evaluate_LCCF(biorefinery, N=1000):
    model = create_IPs_model(biorefinery)
    if biorefinery == 'corn':
        tea = blc.create_corn_tea()
        tea.feedstock.price = 0.1461
        
    elif biorefinery == 'cornstover':
        tea = blc.create_cornstover_tea()
        tea.feedstock.price = 0.0990
        
    elif biorefinery == 'sugarcane':
        tea = blc.create_sugarcane_tea()
        tea.feedstock.price = 0.0427
        
    parameters = list(model.get_parameters())
    set_LCCF = None
    for parameter in parameters:
        if parameter.name == 'LCCF':
            set_LCCF = parameter
            parameters.remove(parameter)
            break
    if set_LCCF is None:
        def set_LCCF(LCCF): tea.F_investment = LCCF
    model_ = bst.Model(tea.system,
                       metrics=model.metrics,
                       parameters=parameters,
                       exception_hook='raise')
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model_.sample(N, rule)
    model_.load_samples(samples)
    nbox = [0]
    def f_evaluate(notify=True):
        model_.evaluate(**evaluate_args(f'LCCF', nbox), notify=20)
    return model_.evaluate_across_coordinate(
                                            '[TEA] LCCF (unitless)', 
                                            set_LCCF, 
                                            np.linspace(
                                            set_LCCF.distribution.lower.min(), 
                                            set_LCCF.distribution.upper.max(), 
                                            8,), 
                                            xlfile=get_file_name('Eval_across_LCCF.xlsx'), 
                                            notify=True,
                                            f_evaluate=f_evaluate,
                                            )

#Evaluate across electricity price
def evaluate_elecP(biorefinery, N=1000):
    model = create_IPs_model(biorefinery)
    if biorefinery == 'corn':
        tea = blc.create_corn_tea()
        tea.feedstock.price = 0.1461
        
    elif biorefinery == 'cornstover':
        tea = blc.create_cornstover_tea()
        tea.feedstock.price = 0.0990
        
    elif biorefinery == 'sugarcane':
        tea = blc.create_sugarcane_tea()
        tea.feedstock.price = 0.0427
        
    parameters = list(model.get_parameters())
    for parameter in parameters:
        if parameter.name == 'Electricity price':
            set_elec_price = parameter
            parameters.remove(parameter)
            break
    model_ = bst.Model(tea.system,
                       metrics=model.metrics,
                       parameters=parameters,
                       exception_hook='raise')
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model_.sample(N, rule)
    model_.load_samples(samples)
    nbox = [0]
    def f_evaluate(notify=True):
        model_.evaluate(**evaluate_args('elecP', nbox), notify=20)
    return model_.evaluate_across_coordinate(
                                            '[Power utility] Electricity price (USD/kWh)', 
                                            set_elec_price, 
                                            np.linspace(
                                            set_elec_price.distribution.lower.min(), 
                                            set_elec_price.distribution.upper.max(), 
                                            10,), 
                                            xlfile=get_file_name('Eval_across_elec_price.xlsx'), 
                                            notify=True,
                                            f_evaluate=f_evaluate,
                                            )
# fig, ax = bst.plots.plot_spearman_1d(sp_rho_table['Biorefinery']['Baseline MFSP [USD/gal]'])
# labels = [item.get_text() for item in ax.get_yticklabels()]
# ax.set_yticklabels(labels)