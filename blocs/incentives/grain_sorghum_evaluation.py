#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 12:30:04 2023

@author: daltonwstewart
"""

# Import necessary modules
import flexsolve as flx
import biosteam as bst
from biorefineries import corn as cn
from biorefineries.sorghum import grain_sorghum as gs
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

# Create a more extensive grain sorghum (gs) TEA
def create_gs_tea():
    gs.load() # !!! there might be a better way to do this
    tea = cn.create_tea(gs.grain_sorghum_sys, cls=blc.ConventionalBLocSTEA)
    tea.incentive_numbers = [] # Empty for now
    tea.fuel_tax = 0.
    tea.sales_tax = 0.
    tea.federal_income_tax = 0.21
    tea.state_income_tax = 0.065
    tea.property_tax = 0.013
    tea.utility_tax = 0.
    tea.ethanol_product = gs.ethanol
    tea.ethanol_group = bst.UnitGroup('Ethanol group', gs.grain_sorghum_sys.units) # Assume all unit operations qualify
    tea.feedstock = gs.feedstock
    tea.DDGS = gs.DDGS
    tea.DDGS.price = 0.13709
    tea.V405 = gs.V405
    tea.crude_oil = gs.crude_oil
    tea.crude_oil.price = 0.64
    tea.sulfuric_acid = gs.sulfuric_acid
    tea.sulfuric_acid.price = 0.1070
    tea.lime = gs.lime
    tea.lime.price = 0.2958
    tea.alpha_amylase = gs.alpha_amylase
    tea.alpha_amylase.price = 2.56
    tea.gluco_amylase = gs.gluco_amylase
    tea.gluco_amylase.price = 2.56
    tea.ammonia = gs.ammonia
    tea.ammonia.price = 0.4727
    tea.denaturant = gs.denaturant
    tea.denaturant.price = 0.496
    tea.steam = gs.steam
    tea.steam.price = 0.01466
    tea.yeast = gs.yeast
    tea.yeast.price = 2.12
    return tea

# Create model for TEA and LCA
def create_gs_model():
    tea = create_gs_tea()
    all_states = ['Alabama',
                  'Arkansas',
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
                  'Nebraska',
                  'New Jersey',
                  'North Carolina',
                  'North Dakota',
                  'Ohio',
                  'Oklahoma',
                  'Pennsylvania',
                  'South Carolina',
                  'South Dakota',
                  'Tennessee',
                  'Texas',
                  'Virginia',
                  'West Virginia',
                  'Wisconsin']
    
    model = bst.Model(tea.system, exception_hook='raise')
    bst.PowerUtility.price = 0.0681
    bst.CE = 596.2
    tea.location = None
    tea.fuel_tax = 0.
    tea.sales_tax = 0.05785
    tea.federal_income_tax = 0.21
    tea.state_income_tax = 0.065
    tea.property_tax = 0.0136
    tea.F_investment = 1.02
    tea.jobs_50 = 25 # Kwiatkowski (2006) does not specify the number of jobs for a corn biorefinery, McAloon (2000) suggests that corn biorefineries provide half the jobs of cellulosic, assumption for cellulosic is 50 jobs
    
    # gs.H3PO4.set_CF(GWP, 1.) # no phosphoric acid for gs
    lime_dilution = 1 - gs.lime.get_mass_composition('Water')
    gs.lime.set_CF(GWP, 1.28 * lime_dilution)
    gs.denaturant.set_CF(GWP, 0.84)

    def solve_price():
        try:
            MFSP = tea.solve_price(tea.ethanol_product)
        except:
            MFSP = tea.solve_price([tea.ethanol_product], [4])
        return 2.98668849 * MFSP

    def MFSP_getter(state):
        def MFSP():
            names = (
                  'state_income_tax',
                  'property_tax',
                  'fuel_tax',
                  'sales_tax',
                  'F_investment',
                  'state_tax_by_gross_receipts',
                  'deduct_federal_income_tax_to_state_taxable_earnings',
                  'deduct_half_federal_income_tax_to_state_taxable_earnings',
                  'incentive_numbers',
              )
            original_feedstock_price = tea.feedstock.price
            original_electricity_price = bst.PowerUtility.price
            dct = {i: getattr(tea, i) for i in names}
            # tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
            # tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
            # tea.fuel_tax = st_data.loc[state]['State Motor Fuel Tax (decimal)']
            # tea.sales_tax = st_data.loc[state]['State Sales Tax Rate (decimal)']
            # bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
            # tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
            # tea.incentive_numbers = ()
            # tea.feedstock.price = st_data.loc[state][f'{name} Price (USD/kg)']
            tea.location = state

            if state == 'Ohio' or state == 'Texas':
                tea.state_tax_by_gross_receipts = True
            else:
                tea.state_tax_by_gross_receipts = False

            if state == 'Alabama' or state == 'Louisiana':
                tea.deduct_federal_income_tax_to_state_taxable_earnings = True
            else:
                tea.deduct_federal_income_tax_to_state_taxable_earnings = False

            if state == 'Iowa' or state == 'Missouri':
                tea.deduct_half_federal_income_tax_to_state_taxable_earnings = True
            else:
                tea.deduct_half_federal_income_tax_to_state_taxable_earnings = False

            MFSP = solve_price()
            tea.feedstock.price = original_feedstock_price
            bst.PowerUtility.price = original_electricity_price
            for i in names: setattr(tea, i, dct[i])
            return MFSP
        return MFSP

    def MFSP_w_inc_getter(state):
        def MFSP():
            names = (
                 'state_income_tax',
                 'property_tax',
                 'fuel_tax',
                 'sales_tax',
                 'F_investment',
                 'state_tax_by_gross_receipts',
                 'deduct_federal_income_tax_to_state_taxable_earnings',
                 'deduct_half_federal_income_tax_to_state_taxable_earnings',
                 'incentive_numbers',
             )
            original_feedstock_price = tea.feedstock.price
            original_electricity_price = bst.PowerUtility.price
            dct = {i: getattr(tea, i) for i in names}
            # tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
            # tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
            # tea.fuel_tax = st_data.loc[state]['State Motor Fuel Tax (decimal)']
            # tea.sales_tax = st_data.loc[state]['State Sales Tax Rate (decimal)']
            # bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
            # tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
            # # tea.incentive_numbers = get_state_incentives(state)
            # tea.feedstock.price = st_data.loc[state][f'{name} Price (USD/kg)']
            tea.location = state

            if state == 'Ohio' or state == 'Texas':
                tea.state_tax_by_gross_receipts = True
            else:
                tea.state_tax_by_gross_receipts = False

            if state == 'Alabama' or state == 'Louisiana':
                tea.deduct_federal_income_tax_to_state_taxable_earnings = True
            else:
                tea.deduct_federal_income_tax_to_state_taxable_earnings = False

            if state == 'Iowa' or state == 'Missouri':
                tea.deduct_half_federal_income_tax_to_state_taxable_earnings = True
            else:
                tea.deduct_half_federal_income_tax_to_state_taxable_earnings = False

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
                tea.incentive_numbers = (11,12,19)
            elif state == 'Louisiana':
                tea.incentive_numbers = (13,)
            elif state == 'Montana':
                tea.incentive_numbers = (3,20)
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

            MFSP = solve_price()
            tea.feedstock.price = original_feedstock_price
            bst.PowerUtility.price = original_electricity_price
            for i in names: setattr(tea, i, dct[i])
            return MFSP
        return MFSP
    
    def GWP_getter(state):
        def get_GWP():
            tea.feedstock.set_CF(GWP, state_data.loc[state]['Grain Sorghum GWP (kg CO2e/kg)'], basis='kg', units='kg*CO2e') # !!! be sure to adjust for moisture content
            bst.PowerUtility.set_CF(key=GWP, consumption=state_data.loc[state]['Electricity GWP-100 (kg CO2-eq/kWh)'], production=state_data.loc[state]['Methane GWP-100 (kg CO2-eq/kWh)'], basis='kWhr', units='kg*CO2e')
            GWP_total_displacement = (tea.system.get_total_feeds_impact(GWP) + tea.system.get_net_electricity_impact(GWP)) # kg CO2 eq. / yr
            annual_ethanol_flow_rate = tea.system.get_mass_flow(gs.ethanol)
            GWP_ = GWP_total_displacement / annual_ethanol_flow_rate
            return GWP_
        return get_GWP
    
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
        names = (
            'state_income_tax', 'property_tax', 'fuel_tax', 'sales_tax', 'F_investment',
            'incentive_numbers',
        )
        dct_old = {i: getattr(tea, i) for i in names}
        tea.state_income_tax = 0
        tea.property_tax = 0.001
        tea.fuel_tax = 0
        tea.sales_tax = 0
        tea.F_investment = 1
        tea.incentive_numbers = ()
        old_price = bst.PowerUtility.price
        bst.PowerUtility.price = 0.0571675
        MFSP = 2.98668849 * tea.solve_price(tea.ethanol_product)
        for i, j in dct_old.items(): setattr(tea, i, j)
        bst.PowerUtility.price = old_price
        return MFSP

    get_inc_value = lambda: tea.exemptions.sum() + tea.deductions.sum() + tea.credits.sum()+ tea.refunds.sum()

    for state in all_states:
        model.metric(MFSP_getter(state), 'MFSP', 'USD/gal', state)
        model.metric(GWP_getter(state), 'Ethanol Product GWP', 'kg CO2e/kg', state)

    # for state in states_w_inc:
    #     model.metric(MFSP_w_inc_getter(state), 'Inc MFSP', 'USD/gal', state)
    #     model.metric(get_inc_value, 'Inc value', 'USD', state)

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

    @model.parameter(element=feedstock, kind='isolated', units='USD/ton',
                        distribution=shape.Triangle(0.8*0.15, 0.15, 1.2*0.15))
    def set_corn_price(price):
            feedstock.price = price

    @param(name='Plant capacity', element=feedstock, kind='coupled', units='dry US MT/yr',
               baseline=(feedstock.F_mass - feedstock.imass['H2O']) * tea.operating_hours / 1000,
               description="annual feestock processing capacity")
    def set_plant_size(flow_rate):
            dry_content = 1 - feedstock.imass['H2O'] / feedstock.F_mass
            feedstock.F_mass = flow_rate / tea.operating_hours / dry_content * 1000

    @model.parameter(element=tea.V405, kind='coupled', units='%',
                         distribution=shape.Triangle(0.85, 0.90, 0.95))
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
            
    return model

def evaluate_SS(N=10):
    model = create_gs_model()
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model.sample(N, rule)
    model.load_samples(samples)
    model.evaluate()
    # model.table.to_excel(get_file_name('SS.xlsx'))
    return model.table